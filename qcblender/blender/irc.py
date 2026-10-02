"""Ordered IRC configurations and imported energy and Mayer records."""
import json

import bpy
from bpy.props import EnumProperty, StringProperty


def cache_step(root, data, step):
    root['qc_irc_record'] = json.dumps({'step': step, 'count': len(data.arrays['irc_energies']),
                                       'energy_hartree': float(data.arrays['irc_energies'][step - 1])})


class QCBLENDER_OT_import_irc(bpy.types.Operator):
    bl_idname = 'qcblender.import_irc_path'
    bl_label = 'Import Ordered IRC FCHK Path'
    bl_options = {'REGISTER', 'UNDO'}
    manifest_path: StringProperty(name='CSV manifest: step,fchk', subtype='FILE_PATH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        self.layout.prop(self, 'manifest_path')
        self.layout.label(text='CSV rows are the exact, 1-based step order')

    def execute(self, context):
        from ..irc import import_irc
        from .external_results import store_analysis
        from .graph import view_modifier
        from .views import atom_view
        try:
            data = import_irc(bpy.path.abspath(self.manifest_path))
            directory = store_analysis(data)
            root = atom_view(directory)
            root['qc_irc_step'] = 1
            root['qc_irc'] = True
            cache_step(root, data, 1)
            modifier = view_modifier(root)
            style = next(item for item in modifier.node_group.interface.items_tree
                         if item.item_type == 'SOCKET' and item.name == 'Style (0 ball-stick, 1 space-fill, 2 bonds)')
            modifier[style.identifier] = 1
        except (ValueError, OSError, KeyError, TypeError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_irc_step(bpy.types.Operator):
    bl_idname = 'qcblender.irc_step'
    bl_label = 'Change IRC Step'
    bl_options = {'REGISTER', 'UNDO'}
    direction: EnumProperty(items=[('PREV', 'Previous', ''), ('NEXT', 'Next', '')])

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and (obj.get('qc_irc') or (obj.parent and obj.parent.get('qc_irc')))

    def execute(self, context):
        from ..data import load_dataset
        from ..geometry import scientific_geometry
        from .geometry import current_geometry
        from .annotations import prepare_annotations, apply_annotations
        root = context.object if context.object.get('qc_irc') else context.object.parent
        try:
            data = load_dataset(bpy.path.abspath(root['qc_dataset']))
            current_geometry(root, data)
            step = int(root['qc_irc_step']) + (1 if self.direction == 'NEXT' else -1)
            if not 1 <= step <= len(data.arrays['irc_energies']):
                raise ValueError('IRC step is outside the imported path')
            positions, record = scientific_geometry(data, 'irc', step)
            record['dataset_sha256'] = root['qc_dataset_sha256']
            attr = root.data.attributes.get('qc_equilibrium_position')
            if attr is None or attr.domain != 'POINT' or attr.data_type != 'FLOAT_VECTOR' or len(attr.data) != len(positions):
                raise ValueError('IRC equilibrium positions are missing or invalid')
            prepared = prepare_annotations(root, positions, record)
            root.data.vertices.foreach_set('co', positions.ravel())
            root.data.attributes['qc_equilibrium_position'].data.foreach_set('vector', positions.ravel())
            root.data.update()
            root['qc_irc_step'] = step
            cache_step(root, data, step)
            apply_annotations(prepared)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_import_irc_mayer(bpy.types.Operator):
    bl_idname = 'qcblender.import_irc_mayer'
    bl_label = 'Import IRC Mayer Bond Orders'
    bl_options = {'REGISTER', 'UNDO'}
    manifest_path: StringProperty(name='CSV manifest: step,mayer_output', subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_irc')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        self.layout.prop(self, 'manifest_path')

    def execute(self, context):
        from ..data import load_dataset
        from ..irc import import_irc_mayer
        from .external_results import store_analysis, table_view
        try:
            root = context.object
            if any(child.get('qc_analysis_role') == 'irc_mayer' for child in root.children):
                raise ValueError('This IRC path already has a Mayer import')
            path = load_dataset(bpy.path.abspath(root['qc_dataset']))
            result = import_irc_mayer(path, bpy.path.abspath(self.manifest_path))
            directory = store_analysis(result)
            obj = table_view(directory, result, root, 'QC IRC Mayer orders', 'irc_mayer')
            obj['qc_pair_a'], obj['qc_pair_b'] = map(int, result.arrays['mayer_pairs'][0])
            context.view_layer.objects.active = obj
            root.select_set(False)
            obj.select_set(True)
        except (ValueError, OSError, KeyError, TypeError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_select_irc_mayer_pair(bpy.types.Operator):
    bl_idname = 'qcblender.select_irc_mayer_pair'
    bl_label = 'Read Selected Mayer Pair'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_analysis_role') == 'irc_mayer'

    def execute(self, context):
        from ..data import load_dataset
        from .source_browser import read_metadata
        obj = context.object
        try:
            read_metadata(obj)
            data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
            pair = sorted((int(obj['qc_pair_a']), int(obj['qc_pair_b'])))
            matches = [index for index, value in enumerate(data.arrays['mayer_pairs']) if value.tolist() == pair]
            if len(matches) != 1:
                raise ValueError('Selected atom pair is absent from Mayer results')
            obj['qc_mayer_pair_index'] = matches[0]
            obj['qc_mayer_display_pair'] = pair
            obj['qc_mayer_display_values'] = data.arrays['mayer_orders'][:, matches[0]].tolist()
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_irc(bpy.types.Panel):
    bl_label = 'IRC Path'
    bl_idname = 'QCBLENDER_PT_irc'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and (obj.get('qc_irc') or (obj.parent and obj.parent.get('qc_irc')))

    def draw(self, context):
        obj = context.object
        root = obj if obj.get('qc_irc') else obj.parent
        step = int(root['qc_irc_step'])
        layout = self.layout
        record = json.loads(root.get('qc_irc_record', '{}'))
        layout.label(text=f"Step {step} / {record.get('count', '未记录')}")
        if record.get('step') == step:
            layout.label(text=f"Energy: {record['energy_hartree']:.10f} hartree")
        else:
            layout.label(text='Energy: 未记录；切步时读取')
        row = layout.row(align=True)
        row.operator('qcblender.irc_step', text='Previous').direction = 'PREV'
        row.operator('qcblender.irc_step', text='Next').direction = 'NEXT'
        if root == obj:
            layout.operator('qcblender.import_irc_mayer', text='Import Mayer Results')
        if obj.get('qc_analysis_role') == 'irc_mayer':
            layout.prop(obj, '["qc_pair_a"]', text='Atom A (1-based)')
            layout.prop(obj, '["qc_pair_b"]', text='Atom B (1-based)')
            layout.operator('qcblender.select_irc_mayer_pair', text='Read Pair')
            values = obj.get('qc_mayer_display_values', [])
            pair = sorted((int(obj['qc_pair_a']), int(obj['qc_pair_b'])))
            if list(obj.get('qc_mayer_display_pair', [])) == pair and 1 <= step <= len(values):
                layout.label(text=f'Mayer order: {values[step - 1]:.6g}')
            layout.operator('qcblender.export_data', text='Export Mayer Data')
