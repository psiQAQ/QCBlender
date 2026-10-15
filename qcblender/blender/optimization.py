"""Discrete optimization views keep final-geometry properties on their source view."""
from .node_identity import socket_name
from ..i18n import error_text, iface, ui_layout
import copy
import json
import textwrap

import bpy
from bpy.props import EnumProperty
from .index_ranges import bounded_int, step_bounds


def load_bound_dataset(obj):
    from ..data import load_dataset
    from .source_browser import read_metadata
    read_metadata(obj)
    return load_dataset(bpy.path.abspath(obj['qc_dataset']))


def set_step(obj, data, step):
    from ..geometry import scientific_geometry
    from .geometry import current_geometry
    from .annotations import prepare_annotations, apply_annotations
    from .association import prepare_association_invalidation, apply_association_invalidation
    current_geometry(obj, data)
    if obj.data.users > 1:
        raise ValueError('Optimization step changes require an independent atom mesh; make Object Data single-user first')
    trajectory = data.metadata['optimization']
    if not 1 <= step <= len(trajectory['steps']):
        raise ValueError('Optimization step is outside the imported trajectory')
    positions, record = scientific_geometry(data, 'optimization', step)
    record['dataset_sha256'] = obj['qc_dataset_sha256']
    if obj.type != 'MESH' or obj.mode != 'OBJECT' or len(obj.data.vertices) != len(positions):
        raise ValueError('Atom mesh no longer matches the optimization trajectory')
    for name, kind in (('qc_equilibrium_position', 'FLOAT_VECTOR'), ('qc_atom_id', 'INT'), ('qc_atomic_number', 'INT')):
        attr = obj.data.attributes.get(name)
        if attr is None or attr.domain != 'POINT' or attr.data_type != kind or len(attr.data) != len(positions):
            raise ValueError('Optimization atom attribute is missing or invalid: ' + name)
    if ([v.value for v in obj.data.attributes['qc_atom_id'].data] != list(range(len(positions))) or
            [v.value for v in obj.data.attributes['qc_atomic_number'].data] != data.arrays['atomic_numbers'].tolist()):
        raise ValueError('Optimization atom identities or ordering changed')
    serialized = json.dumps(trajectory['steps'][step - 1])
    prepared = prepare_annotations(obj, positions, record)
    associations = prepare_association_invalidation(obj, record)
    obj.data.vertices.foreach_set('co', positions.ravel())
    obj.data.attributes['qc_equilibrium_position'].data.foreach_set('vector', positions.ravel())
    obj.data.update()
    obj['qc_optimization_step'] = step
    obj['qc_optimization_count'] = len(trajectory['steps'])
    obj['qc_optimization_record'] = serialized
    apply_annotations(prepared)
    apply_association_invalidation(associations)
    obj.update_tag()


class QCBLENDER_OT_optimization_view(bpy.types.Operator):
    bl_idname = 'qcblender.optimization_view'
    bl_label = 'Create Optimization View'
    bl_description = 'Create a separate switchable atom view from the recorded optimization trajectory; bonds are inferred from step 1 and scientific properties remain on the source view'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.get('qc_optimization_available', False) and not obj.get('qc_optimization_step')

    def execute(self, context):
        from ..data import Dataset
        from ..readers import infer_bonds
        from .external_results import store_analysis
        from .graph import view_modifier
        from .layers import activate
        from .views import atom_view
        try:
            source = context.object
            data = load_bound_dataset(source)
            trajectory = data.metadata['optimization']
            metadata = {key: copy.deepcopy(data.metadata[key]) for key in
                        ('source', 'coordinate_unit', 'selected_job', 'jobs', 'method', 'calculation_status', 'optimization')}
            metadata.update(title=iface('{value0} / Optimization', value0=data.metadata['title']), fields=[], charges=[], energies=[],
                            diagnostics=['Discrete optimization steps; bonds inferred from step 1; no per-step charges, modes or fields'])
            arrays = {'atomic_numbers': data.arrays['atomic_numbers'],
                      'positions': data.arrays[trajectory['array']][0],
                      trajectory['array']: data.arrays[trajectory['array']]}
            view_data = Dataset(metadata, arrays)
            infer_bonds(view_data)
            directory = store_analysis(view_data)
            obj = atom_view(directory)
            obj.matrix_world = source.matrix_world.copy()
            obj.location.x += float(data.arrays[trajectory['array']][:, :, 0].max() -
                                    data.arrays[trajectory['array']][:, :, 0].min()) + 3
            modifier = view_modifier(obj)
            style = next(item for item in modifier.node_group.interface.items_tree
                         if item.item_type == 'SOCKET' and socket_name(item) == 'Style (0 ball-stick, 1 space-fill, 2 bonds)')
            modifier[style.identifier] = 1
            set_step(obj, view_data, 1)
            activate(context, obj)
        except (ValueError, OSError, KeyError, TypeError, MemoryError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_optimization_step(bpy.types.Operator):
    bl_idname = 'qcblender.optimization_step'
    bl_label = 'Choose Optimization Step'
    bl_description = 'Choose or advance the active optimization view step and refresh its geometry and annotations; these discrete steps are not physical time'
    bl_options = {'REGISTER', 'UNDO'}
    direction: EnumProperty(items=[('GOTO', 'Choose', ''), ('PREV', 'Previous', ''), ('NEXT', 'Next', '')])
    step: bounded_int('step', step_bounds, name='Step', default=1, min=1)

    @classmethod
    def description(cls, context, properties):
        from ..i18n import tip
        messages = {
            'GOTO': 'Choose a recorded optimization step by its 1-based order and update the active trajectory view geometry, energy and annotations',
            'PREV': 'Move the active optimization view to the preceding recorded step and refresh geometry, energy and annotations',
            'NEXT': 'Move the active optimization view to the following recorded step and refresh geometry, energy and annotations',
        }
        return tip(messages.get(getattr(properties, 'direction', None), cls.bl_description))

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_optimization_step'))

    def invoke(self, context, event):
        if self.direction != 'GOTO':
            return self.execute(context)
        self.step = context.object['qc_optimization_step']
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        ui_layout(self.layout).label(text=iface('Steps 1-{value0}', value0=context.object["qc_optimization_count"]))
        ui_layout(self.layout).prop(self, 'step')

    def execute(self, context):
        obj = context.object
        try:
            data = load_bound_dataset(obj)
            step = self.step if self.direction == 'GOTO' else obj['qc_optimization_step'] + (1 if self.direction == 'NEXT' else -1)
            set_step(obj, data, step)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_optimization(bpy.types.Panel):
    bl_label = 'Optimization Trajectory'
    bl_idname = 'QCBLENDER_PT_optimization'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and bool(obj.get('qc_optimization_status'))

    def draw(self, context):
        obj, layout = context.object, ui_layout(self.layout)

        def label(text):
            for line in textwrap.wrap(error_text(text), width=max(20, int(context.region.width / 8))):
                layout.label(text=line)

        if not obj.get('qc_optimization_available'):
            label(obj.get('qc_optimization_reason', 'Trajectory unavailable'))
        elif not obj.get('qc_optimization_step'):
            layout.operator('qcblender.optimization_view')
            layout.label(text='Creates a separate view beside the source')
        else:
            record = json.loads(obj['qc_optimization_record'])
            step, count = obj['qc_optimization_step'], obj['qc_optimization_count']
            layout.label(text=iface('Step {value0} / {value1} | {value2}', value0=step, value1=count, value2=record["status"]))
            layout.label(text=iface('Calculation: {value0}', value0=record['calculation_status']))
            energy = record['energy']
            layout.label(text=f'{energy["method"]}: {energy["value_hartree"]:.10f} Hartree' if energy else iface('Energy: {status}', status=iface(record['energy_status'])), translate=False)
            layout.label(text=iface('Geometry lines {value0}-{value1}', value0=record["geometry_line_start"], value1=record["geometry_line_end"]))
            row = layout.row(align=True)
            previous, following = row.row(), row.row()
            previous.enabled, following.enabled = step > 1, step < count
            previous.operator('qcblender.optimization_step', text='Previous').direction = 'PREV'
            following.operator('qcblender.optimization_step', text='Next').direction = 'NEXT'
            layout.operator('qcblender.optimization_step', text='Choose Step').direction = 'GOTO'
            for criterion in record['convergence']:
                layout.label(text=criterion['quantity'])
                layout.label(text=f'{criterion["value"]:g} / {criterion["threshold"]:g} | ' + iface('YES' if criterion['converged'] else 'NO'), translate=False)
            units = record['convergence_unit_system']
            label(units['text'] if units else 'Convergence units: not recorded')
            if not record['convergence']:
                layout.label(text='Convergence criteria: not recorded')
            layout.label(text='Discrete steps, not physical time')
            label('Bonds inferred from step 1; properties remain on source')
