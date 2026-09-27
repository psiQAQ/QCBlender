import json
import hashlib
import textwrap
from functools import lru_cache
from pathlib import Path

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

ADDON_ID = __package__.rsplit('.', 1)[0]
_operations = {}


def draw_material_controls(layout, mat):
    if not mat or not mat.use_nodes:
        return
    nodes = mat.node_tree.nodes
    from .views import node_by_type

    shader = node_by_type(nodes, 'ShaderNodeBsdfPrincipled')
    if shader:
        for name in ('Base Color', 'Alpha', 'Roughness'):
            if not shader.inputs[name].is_linked:
                layout.prop(shader.inputs[name], 'default_value', text=name)
    for node in nodes:
        if node.get('qc_role') in ('color_ramp', 'opacity_ramp'):
            layout.label(text='Opacity multiplier' if node['qc_role'] == 'opacity_ramp' else 'Color map')
            layout.template_color_ramp(node, 'color_ramp', expand=True)
        elif node.get('qc_role') == 'color_invert':
            layout.prop(node.outputs[0], 'default_value', text='Reverse (0 or 1)')
        elif node.get('qc_control'):
            if node.bl_idname == 'ShaderNodeCombineXYZ':
                layout.label(text=node['qc_control'])
                row = layout.row(align=True)
                for item in node.inputs:
                    row.prop(item, 'default_value', text=item.name)
            else:
                layout.prop(node.outputs[0], 'default_value', text=node['qc_control'])
    if mat.get('qc_fog'):
        layout.label(text='Optical display; source values unchanged')


def cancel_operations():
    for operator, manager in list(_operations.values()):
        manager.event_timer_remove(operator._timer)
        operator._job.cancel()
    _operations.clear()


class AsyncOperation:
    def execute(self, context):
        try:
            self._job = self.begin(context)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self._timer = context.window_manager.event_timer_add(0.25, window=context.window)
        _operations[id(self)] = (self, context.window_manager)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if id(self) not in _operations:
            return {'CANCELLED'}
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}
        try:
            report = self._job.poll()
            if report is None:
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if report['status'] != 'succeeded':
                raise RuntimeError(report.get('error', 'Scientific worker failed; inspect runtime report'))
            self.accept(context, report)
        except (RuntimeError, ValueError, OSError, KeyError, ReferenceError) as error:
            self.cancel(context)
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        context.window_manager.event_timer_remove(self._timer)
        _operations.pop(id(self), None)
        return {'FINISHED'}

    def cancel(self, context):
        if _operations.pop(id(self), None) is not None:
            context.window_manager.event_timer_remove(self._timer)
        self._job.cancel()


class QCBlenderPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID
    runtime_report: StringProperty(name='Runtime report', default='')

    def draw(self, context):
        self.layout.operator('qcblender.check_runtime', icon='CHECKMARK')
        if self.runtime_report:
            report = json.loads(self.runtime_report)
            for entry in report.get('modules', []):
                self.layout.label(text=f"{entry['module']}: {entry['status']}")
            if report.get('error'):
                self.layout.label(text=report['error'], icon='ERROR')


class QCBLENDER_OT_check_runtime(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.check_runtime'
    bl_label = 'Check Scientific Runtime'

    def begin(self, context):
        from .jobs import Job
        return Job('diagnose')

    def accept(self, context, report):
        context.preferences.addons[ADDON_ID].preferences.runtime_report = json.dumps(report)
        self.report({'INFO'}, 'Scientific runtime checks passed')


class QCBLENDER_OT_import(AsyncOperation, bpy.types.Operator, ImportHelper):
    bl_idname = 'qcblender.import_calculation'
    bl_label = 'Import Gaussian Result'
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = '.fchk'
    filter_glob: StringProperty(default='*.fchk;*.fch;*.cube;*.cub;*.log;*.out', options={'HIDDEN'})
    job_number: IntProperty(name='Gaussian Log job number', default=1, min=1)
    source_sha256: StringProperty(options={'HIDDEN'})

    def invoke(self, context, event):
        self._preview_gui = True
        return ImportHelper.invoke(self, context, event)

    def begin(self, context):
        from .jobs import Job
        self._inspecting = getattr(self, '_preview_gui', False) and Path(self.filepath).suffix.lower() in ('.log', '.out')
        return Job('inspect_source' if self._inspecting else 'import',
                   source=str(Path(self.filepath).resolve(strict=True)), job_index=self.job_number - 1,
                   source_sha256=self.source_sha256)

    def accept(self, context, report):
        from .views import atom_view, field_view
        from ..data import load_dataset
        if self._inspecting:
            bpy.ops.qcblender.choose_log_job('INVOKE_DEFAULT', filepath=self.filepath,
                                           summary=json.dumps(report))
            return
        directory = self._job.directory / 'dataset'
        obj = atom_view(directory)
        data = load_dataset(directory)
        for index in range(len(data.metadata.get('fields', []))):
            field_view(directory, obj, index)
        self.report({'INFO'}, 'Imported Gaussian data; 1 Blender unit = 1 angstrom')


@lru_cache(maxsize=16)
def cached_job_choices(summary):
    # Blender retains references to dynamic enum strings beyond the callback.
    jobs = json.loads(summary)['jobs'] if summary else []
    return [(str(i), f"{i+1}: {job['status']} | {job['route'] or '未记录'}",
             f"Lines {job['line_start']}–{job['line_end']}") for i, job in enumerate(jobs)]


def job_choices(self, context):
    return cached_job_choices(self.summary)


class QCBLENDER_OT_choose_log_job(bpy.types.Operator):
    bl_idname = 'qcblender.choose_log_job'
    bl_label = 'Choose Gaussian Calculation'
    filepath: StringProperty(options={'HIDDEN'})
    summary: StringProperty(options={'HIDDEN'})
    job: EnumProperty(name='Calculation', items=job_choices)

    def invoke(self, context, event):
        self.job = '0'
        return context.window_manager.invoke_props_dialog(self, width=640)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'job')
        record = json.loads(self.summary)['jobs'][int(self.job)]
        layout.label(text=f"Lines {record['line_start']}–{record['line_end']} | {record['status']}")
        for line in textwrap.wrap(record['route'] or '未记录', width=85):
            layout.label(text=line)
        layout.label(text='Explicit geometry: ' + ('detected; validated on import' if record['explicit_geometry'] else 'not detected'))
        selection = record['energy_selection']
        energy = next((e for e in record['energies'] if e['id'] == selection.get('record_id')), None)
        layout.label(text=f"Energy: {energy['value_hartree']} Hartree" if energy else 'Energy: ' + selection['status'])
        if not energy and record['energies']:
            layout.label(text=f"Last records ({len(record['energies'])} total; not a selected final energy):")
            for item in record['energies'][-3:]:
                layout.label(text=f"L{item['line_start']} {item['method']} / {item['kind']}: {item['value_hartree']} Hartree")
        layout.label(text='Import keeps this calculation status; no geometry inheritance')

    def execute(self, context):
        report = json.loads(self.summary)
        return bpy.ops.qcblender.import_calculation('EXEC_DEFAULT', filepath=self.filepath,
            job_number=int(self.job)+1, source_sha256=report['source']['sha256'])


class QCBLENDER_OT_generate(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.generate_field'
    bl_label = 'Generate Quantum Field'
    bl_options = {'REGISTER', 'UNDO'}

    quantity: EnumProperty(name='Quantity', items=[
        ('orbital_amplitude', 'Molecular orbital', 'Signed orbital amplitude'),
        ('electron_number_density', 'Electron density', 'Alpha plus beta, SCF occupations'),
        ('alpha_density', 'Alpha density', 'Alpha spin electrons'),
        ('beta_density', 'Beta density', 'Beta spin electrons'),
        ('spin_density', 'Spin density', 'Alpha minus beta, SCF occupations'),
        ('electrostatic_potential', 'Electrostatic potential', 'Nuclear minus electronic potential')])
    spin: EnumProperty(name='Spin', items=[('alpha', 'Alpha', ''), ('beta', 'Beta', '')])
    orbital: IntProperty(name='Orbital number (1-based)', default=1, min=1)
    orbital_choice: EnumProperty(name='Orbital', items=[('HOMO', 'HOMO', 'Highest-energy occupied orbital in this spin channel'),
        ('LUMO', 'LUMO', 'Lowest-energy unoccupied orbital in this spin channel'),
        ('EXPLICIT', 'Source number', 'Choose the original orbital number')], default='HOMO')
    spacing: FloatProperty(name='Grid spacing (angstrom)', default=0.2, min=0.02, max=2)
    padding: FloatProperty(name='Grid margin (angstrom)', default=3, min=0.5, max=30)
    memory_mb: IntProperty(name='Memory budget (MiB)', default=512, min=32, max=16384)

    @classmethod
    def poll(cls, context):
        return context.object is not None and 'qc_dataset' in context.object

    def invoke(self, context, event):
        from ..data import load_dataset
        try:
            data = load_dataset(bpy.path.abspath(context.object['qc_dataset']))
            if 'orbitals' not in data.metadata:
                raise ValueError('This source has no orbital coefficients')
            self._preview = data
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'quantity')
        if self.quantity == 'orbital_amplitude':
            layout.prop(self, 'spin')
            layout.prop(self, 'orbital_choice')
            if self.orbital_choice == 'EXPLICIT':
                layout.prop(self, 'orbital')
            if hasattr(self, '_preview'):
                from ..data import orbital_selection
                try:
                    selected = orbital_selection(self._preview, self.spin, self.orbital_choice, self.orbital)
                    layout.label(text=f"Source MO {selected['source_number']} | occupation {selected['occupation']:.6g}")
                    layout.label(text=f"Energy: {selected['energy_hartree']} Hartree")
                except ValueError as error:
                    layout.label(text=str(error), icon='ERROR')
        layout.prop(self, 'spacing')
        layout.prop(self, 'padding')
        layout.prop(self, 'memory_mb')
        layout.label(text='Grid limits require convergence checks for quantitative use')

    def begin(self, context):
        import numpy as np
        from ..data import load_dataset, orbital_selection
        from .jobs import Job
        self._source = context.object
        self._dataset = bpy.path.abspath(self._source['qc_dataset'])
        self._input_digest = hashlib.sha256((Path(self._dataset) / 'manifest.json').read_bytes()).hexdigest()
        data = load_dataset(self._dataset)
        if self.quantity == 'orbital_amplitude':
            self.orbital = orbital_selection(data, self.spin, self.orbital_choice, self.orbital)['source_number']
        positions = data.arrays['positions']
        origin = positions.min(axis=0) - self.padding
        upper = positions.max(axis=0) + self.padding
        shape = (np.ceil((upper - origin) / self.spacing).astype(int) + 1).tolist()
        return Job('evaluate', dataset=self._dataset, dataset_sha256=self._input_digest,
                   grid={'origin': origin.tolist(), 'steps': (np.eye(3) * self.spacing).tolist(), 'shape': shape},
                   parameters={'quantity': self.quantity, 'spin': self.spin, 'orbital': self.orbital,
                               'memory_mb': self.memory_mb})

    def accept(self, context, report):
        from .views import field_view
        if self._source.name not in bpy.data.objects or bpy.path.abspath(self._source['qc_dataset']) != self._dataset:
            raise ValueError('Source view changed during calculation; result was retained but not attached')
        if hashlib.sha256((Path(self._dataset) / 'manifest.json').read_bytes()).hexdigest() != self._input_digest:
            raise ValueError('Source dataset changed during calculation; stale result was not attached')
        field_view(self._job.directory / 'dataset', self._source)
        self.report({'INFO'}, 'Quantum field ready; adjust isovalue in the geometry node modifier')


class QCBLENDER_OT_declare_field(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.declare_field'
    bl_label = 'Identify Cube Quantity and Unit'
    quantity: EnumProperty(name='Values already use this quantity/unit', items=[
        ('electron_number_density', 'Electron density [electron/bohr^3]', ''),
        ('spin_density', 'Alpha-minus-beta spin density [electron/bohr^3]', ''),
        ('electrostatic_potential', 'ESP [hartree/e]', ''),
        ('orbital_amplitude', 'Orbital amplitude [bohr^-3/2]', ''),
        ('custom', 'Other externally computed scalar field', '')])
    custom_quantity: StringProperty(name='Physical quantity', default='External scalar', maxlen=120)
    custom_unit: StringProperty(name='Unit (use unknown if unavailable)', default='unknown', maxlen=80)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 'qc_field' in context.object
                and json.loads(context.object['qc_field'])['quantity'] == 'unknown_scalar')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'quantity')
        if self.quantity == 'custom':
            self.layout.prop(self, 'custom_quantity')
            self.layout.prop(self, 'custom_unit')
        self.layout.label(text='Confirm against the generating calculation; values are not converted.')

    def begin(self, context):
        from .jobs import Job
        self._source = context.object
        self._directory = bpy.path.abspath(self._source['qc_dataset'])
        self._digest = hashlib.sha256((Path(self._directory) / 'manifest.json').read_bytes()).hexdigest()
        return Job('declare_field', dataset=self._directory, dataset_sha256=self._digest,
                   field_array=json.loads(self._source['qc_field'])['array'], quantity=self.quantity,
                   custom_quantity=self.custom_quantity, custom_unit=self.custom_unit)

    def accept(self, context, report):
        from .project import rebind_dataset
        if hashlib.sha256((Path(self._directory) / 'manifest.json').read_bytes()).hexdigest() != self._digest:
            raise ValueError('Dataset changed during interpretation')
        rebind_dataset(self._directory, self._job.directory / 'dataset')
        self.report({'INFO'}, 'Saved explicit user-assigned quantity and units; array values unchanged')


class QCBLENDER_PT_main(bpy.types.Panel):
    bl_label = 'QCBlender'
    bl_idname = 'QCBLENDER_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator('qcblender.import_calculation', text='Import', icon='IMPORT')
        row.operator('qcblender.associate_sources', text='Associate', icon='CON_TRACKTO')
        layout.operator('qcblender.import_paired_field', text='Import IGMH / IRI', icon='VOLUME_DATA')
        layout.operator('qcblender.import_nbo', text='Import NBO Records', icon='TEXT')
        row = layout.row(align=True)
        row.operator('qcblender.import_esp_analysis', text='ESP Surface')
        row.operator('qcblender.import_aim_analysis', text='AIM')
        layout.operator('qcblender.import_ets_nocv', text='ETS-NOCV Table')
        layout.operator('qcblender.import_nocv_field', text='NOCV Pair Cube')
        layout.operator('qcblender.import_irc_path', text='IRC FCHK Path')
        row = layout.row(align=True)
        row.operator('qcblender.generate_field', text='Generate Field', icon='VOLUME_DATA')
        row.operator('qcblender.declare_field', text='Identify Cube', icon='INFO')
        row = layout.row(align=True)
        row.operator('qcblender.map_scalar', text='Map Colors', icon='COLOR')
        row.operator('qcblender.create_slice', text='Slice', icon='MESH_PLANE')
        row.operator('qcblender.create_fog', text='Fog', icon='VOLUME_DATA')
        row = layout.row(align=True)
        row.operator('qcblender.add_clipping', text='Clip', icon='MOD_BOOLEAN')
        row.operator('qcblender.probe_field', text='Read at Cursor', icon='PIVOT_CURSOR')
        if context.object and context.object.get('qc_view_kind') in ('field', 'slice'):
            row = layout.row(align=True)
            row.operator('qcblender.mark_profile_start', text='Mark Profile Start')
            create = row.row(align=True)
            create.enabled = 'qc_profile_start' in context.object
            create.operator('qcblender.create_line_profile', text='Create Line Profile')
        if context.object and context.object.get('qc_view_kind') == 'profile':
            layout.operator('qcblender.export_line_profile', icon='EXPORT')
            chart = json.loads(context.object['qc_chart'])
            layout.label(text=f"Distance: 0–{chart['x_max']:.6g} Å | {chart['y_unit']}")
            layout.label(text=f"{chart['valid_count']}/{chart['sample_count']} valid samples")
        row = layout.row(align=True)
        row.operator('qcblender.color_charge', text='Charge', icon='MATERIAL')
        row.operator('qcblender.show_dipole', text='Dipole', icon='EMPTY_ARROWS')
        row.operator('qcblender.measure_distance', text='Distance')
        layout.operator('qcblender.create_framed_camera', text='Create Framed QC Camera', icon='CAMERA_DATA')
        layout.operator('qcblender.save_project', icon='FILE_TICK')
        layout.operator('qcblender.archive_project', icon='PACKAGE')
        layout.operator('qcblender.rebuild_cache', icon='FILE_REFRESH')
        layout.operator('qcblender.relocate_dataset', icon='FILE_FOLDER')
        if _operations:
            for operation, manager in _operations.values():
                progress = operation._job.progress()
                layout.label(text=f"{progress['phase']}: {progress['fraction']:.0%} (Esc cancels)", icon='TIME')
        obj = context.object
        if obj and 'qc_dataset' in obj:
            layout.label(text='Coordinates: angstrom')
            for diagnostic in json.loads(obj.get('qc_diagnostics', '[]')):
                box = layout.box()
                for line in textwrap.wrap(diagnostic, width=max(24, int(context.region.width / 8))):
                    box.label(text=line)
            if 'qc_calculation_status' in obj:
                layout.label(text='Calculation: ' + obj['qc_calculation_status'])
            settings = obj.qc_settings
            if settings.modes:
                layout.label(text='Vibration / IR (source values)')
                layout.template_list('QCBLENDER_UL_modes', '', settings, 'modes', settings, 'active_mode', rows=5)
                if 'qc_mode_frequency_cm-1' in obj:
                    layout.label(text=f"Frequency: {obj['qc_mode_frequency_cm-1']:.4f} cm^-1")
                if 'qc_mode_ir_km_mol' in obj:
                    layout.label(text=f"IR: {obj['qc_mode_ir_km_mol']:.4f} km/mol")
            if settings.energies:
                layout.label(text='Energy records (Hartree)')
                if 'qc_energy_selection' in obj:
                    choice = json.loads(obj['qc_energy_selection'])
                    layout.label(text='Target: ' + choice['status'])
                layout.template_list('QCBLENDER_UL_energies', '', settings, 'energies', settings, 'active_energy', rows=4)
                if 0 <= settings.active_energy < len(settings.energies):
                    record = json.loads(settings.energies[settings.active_energy].record)
                    layout.label(text=f"Value: {record['value_hartree']:.10f} Eh")
                    layout.label(text='Kind: ' + record['kind'])
                    method = record['method'] or 'unknown'
                    layout.label(text='Method: ' + (method if not method.startswith('#') else 'see source route'))
                    if record.get('state'):
                        layout.label(text='State: ' + str(record['state']['source_number']))
                    layout.label(text='Source: ' + str(record.get('line_start', record.get('source_field', 'unknown'))))
                    layout.label(text=str(record.get('raw_label', record['kind'])))
            if 'qc_charge_method' in obj:
                layout.label(text='Charges: ' + obj['qc_charge_method'])
            if obj.get('qc_vdw_missing', '[]') != '[]':
                layout.label(text='Missing VDW radii: ' + obj['qc_vdw_missing'], icon='ERROR')
            if 'qc_probe' in obj:
                probe = json.loads(obj['qc_probe'])
                layout.label(text=f"Last sample: {probe['value']:.8g} {probe['unit']}")
                layout.label(text='Source angstrom: ' + ', '.join(f'{v:.4g}' for v in probe['source_position_angstrom']))
                layout.label(text='Trilinear grid interpolation; click to refresh')
            if 'qc_field' in obj:
                field = json.loads(obj['qc_field'])
                layout.label(text=field['quantity'])
                layout.label(text='Unit: ' + field['unit'])
                layout.label(text='Grid: ' + ' x '.join(map(str, field['shape'])))
                if field.get('method'):
                    layout.label(text='Method: ' + field['method'])
                if field.get('interpretation') == 'user_assigned':
                    layout.label(text='Quantity/unit explicitly assigned by user')
                if field.get('orbital'):
                    mo = field['orbital']
                    layout.label(text=f"{mo['spin']} MO {mo['source_number']} | occupation {mo['occupation']:.6g}")
                    layout.label(text=f"Energy: {mo['energy_hartree']} Hartree")
                if 'qc_color_source' in obj:
                    color_source = json.loads(obj['qc_color_source'])
                    layout.label(text='Colors: ' + color_source['quantity'] + ' [' + color_source['unit'] + ']')
                    layout.label(text='Magenta: outside valid field domain')
        if obj and obj.get('qc_view_kind') and obj.get('qc_view_kind') != 'profile':
            from .graph import view_modifier
            try:
                modifier = view_modifier(obj)
            except ValueError as error:
                layout.label(text=str(error), icon='INFO')
                modifier = None
            if modifier:
                values = {item.name: modifier.get(item.identifier) for item in modifier.node_group.interface.items_tree
                          if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.identifier in modifier}
                for prefix in ('Color', 'Charge'):
                    if prefix + ' Center' in values and not values[prefix + ' Minimum'] < values[prefix + ' Center'] < values[prefix + ' Maximum']:
                        layout.label(text=prefix + ': require minimum < center < maximum', icon='ERROR')
                for item in modifier.node_group.interface.items_tree:
                    if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.identifier in modifier:
                        layout.prop(modifier, '["' + item.identifier + '"]', text=item.name)
                        if item.socket_type == 'NodeSocketMaterial':
                            mat = modifier.get(item.identifier)
                            draw_material_controls(layout, mat)
                shown = {modifier.get(item.identifier) for item in modifier.node_group.interface.items_tree
                         if item.item_type == 'SOCKET' and item.socket_type == 'NodeSocketMaterial'}
                for node in modifier.node_group.nodes:
                    for control in node.inputs:
                        if control.type == 'MATERIAL' and not control.is_linked and control.default_value and control.default_value not in shown:
                            shown.add(control.default_value)
                            draw_material_controls(layout, control.default_value)
