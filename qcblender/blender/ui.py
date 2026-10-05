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
_qualifications = {}


def clear_qualifications(*args):
    _qualifications.clear()


def science_binding(context):
    from ..science_identity import scientific_identity
    source = context.object
    if source is None:
        raise ValueError('Select the wavefunction source')
    directory = bpy.path.abspath(source['qc_dataset'])
    digest = hashlib.sha256((Path(directory) / 'manifest.json').read_bytes()).hexdigest()
    if source.get('qc_dataset_sha256') != digest:
        raise ValueError('Dataset manifest differs from the saved source binding; rebind the verified source')
    fingerprint = scientific_identity()['sha256']
    return source, directory, digest, fingerprint


def same_science_source(context, source, directory, digest, fingerprint):
    if context.object != source or source.name not in bpy.data.objects:
        raise ValueError('Selected source changed during scientific qualification')
    current = science_binding(context)
    if current[1:] != (directory, digest, fingerprint):
        raise ValueError('Source binding or scientific implementation changed; qualify it again')


def _material_section(node):
    role = node.get('qc_role')
    if role in ('color_ramp', 'color_invert'):
        return '材质'
    if role == 'opacity_ramp':
        return '材质'
    control = node.get('qc_control', '')
    if control.startswith(('Plane ', 'Box ')):
        return '空间观察'
    if control.startswith('Color '):
        return '颜色映射'
    if control == 'Display Threshold':
        return '几何表示'
    return '材质' if control else None


def draw_material_controls(layout, mat, section='材质', unit=''):
    if not mat or not mat.use_nodes:
        return
    nodes = mat.node_tree.nodes
    from .views import node_by_type

    shader = node_by_type(nodes, 'ShaderNodeBsdfPrincipled')
    if shader and section == '材质':
        for name in ('Base Color', 'Alpha', 'Roughness'):
            if not shader.inputs[name].is_linked:
                layout.prop(shader.inputs[name], 'default_value', text=name)
    for node in nodes:
        if node.get('qc_role') in ('color_ramp', 'opacity_ramp') and section == _material_section(node):
            layout.label(text='Opacity multiplier' if node['qc_role'] == 'opacity_ramp' else 'Color map')
            layout.template_color_ramp(node, 'color_ramp', expand=True)
        elif node.get('qc_role') == 'color_invert' and section == '材质':
            layout.prop(node.outputs[0], 'default_value', text='Reverse (0 or 1)')
        elif node.get('qc_control') and section == _material_section(node):
            if node['qc_control'] in ('Plane Origin', 'Plane Normal') and not next(
                    (other.outputs[0].default_value for other in nodes if other.get('qc_control') == 'Plane Enabled'), False):
                continue
            if node['qc_control'] in ('Box Minimum', 'Box Maximum') and not next(
                    (other.outputs[0].default_value for other in nodes if other.get('qc_control') == 'Box Enabled'), False):
                continue
            if node.bl_idname == 'ShaderNodeCombineXYZ':
                label = (' [视图局部方向，无量纲]' if node['qc_control'] == 'Plane Normal'
                         else ' [视图局部 Å]')
                layout.label(text=node['qc_control'] + label)
                row = layout.row(align=True)
                for item in node.inputs:
                    row.prop(item, 'default_value', text=item.name)
            else:
                label = node['qc_control']
                if label in ('Color Minimum', 'Color Maximum', 'Display Threshold', 'Opacity Range'):
                    label += f' [{unit or "单位未知"}]'
                layout.prop(node.outputs[0], 'default_value', text=label)
    if mat.get('qc_fog') and section == '材质':
        layout.label(text='Optical display; source values unchanged')


def cancel_operations():
    reports = []
    for operator, _ in list(_operations.values()):
        timer_errors = finish_operation(operator)
        try:
            operator.cancel(None)
            report = operator._job.cancellation
        except Exception as error:
            # A failing operator must not leave other tasks' native timers and children running.
            report = {'status': 'exit_unconfirmed', 'pid': operator._job.process.pid,
                      'directory': str(operator._job.directory),
                      'errors': [f'Operation cancellation: {type(error).__name__}: {error}']}
            print('QCBlender cancellation: ' + json.dumps(report))
        if timer_errors:
            print('QCBlender timer cleanup: ' + '; '.join(timer_errors))
        reports.append(report)
    return reports


def finish_operation(operator):
    operation = _operations.pop(id(operator), None)
    if operation is None:
        return []
    try:
        operation[1].event_timer_remove(operator._timer)
    except (RuntimeError, ReferenceError) as error:
        return [f'Operation timer cleanup: {type(error).__name__}: {error}']
    return []


class AsyncOperation:
    def execute(self, context):
        try:
            self._job = self.begin(context)
        except (ValueError, OSError, KeyError, MemoryError) as error:
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
        except (RuntimeError, ValueError, OSError, KeyError, ReferenceError, MemoryError) as error:
            self.report({'ERROR'}, str(error))
            self.cancel(context)
            return {'CANCELLED'}
        for error in finish_operation(self):
            self.report({'ERROR'}, error)
        return {'FINISHED'}

    def cancel(self, context):
        timer_errors = finish_operation(self)
        report = self._job.cancel()
        messages = timer_errors + report['errors']
        if messages or report['status'] != 'exited':
            details = '; '.join(messages) or 'Worker exit has not been confirmed'
            self.report({'ERROR'}, f'Cancellation {report["status"]}; PID {report["pid"]}; '
                        f'{report["directory"]}: {details}')
        # Blender's Operator.cancel callback must return None.


class QCBlenderPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID
    runtime_report: StringProperty(name='Runtime report', default='')
    data_output_directory: StringProperty(name='数据导出目录', subtype='DIR_PATH', default='')

    def draw(self, context):
        self.layout.prop(self, 'data_output_directory')
        self.layout.label(text='留空：已保存工程的目录；未保存工程使用系统文档目录')
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
    bl_label = 'Import Gaussian / Cube / XYZ'
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = '.fchk'
    filter_glob: StringProperty(default='*.fchk;*.fch;*.cube;*.cub;*.log;*.out;*.xyz', options={'HIDDEN'})
    job_number: IntProperty(name='Gaussian Log job number', default=1, min=1)
    source_sha256: StringProperty(options={'HIDDEN'})

    def invoke(self, context, event):
        self._preview_gui = True
        self.source_sha256 = ''
        self.job_number = 1
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
        from .native_volume import check_field_cache
        if self._inspecting:
            bpy.ops.qcblender.choose_log_job('INVOKE_DEFAULT', filepath=self.filepath,
                                           summary=json.dumps(report))
            return
        directory = self._job.directory / 'dataset'
        data = load_dataset(directory)
        for field in data.metadata.get('fields', []):
            check_field_cache(directory, field)
        obj = atom_view(directory)
        from .trajectory import initialize_trajectory
        initialize_trajectory(obj, data)
        for index in range(len(data.metadata.get('fields', []))):
            field_view(directory, obj, index)
        self.report({'INFO'}, 'Imported scientific data; 1 Blender unit = 1 angstrom')


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


class QCBLENDER_OT_qualify_science(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.qualify_science'
    bl_label = 'Check Scientific Source'
    memory_mb: IntProperty(name='Qualification memory budget (MiB)', default=512, min=32, max=16384)
    reason: StringProperty(options={'HIDDEN'})

    def invoke(self, context, event):
        self._retry_binding = science_binding(context)
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        for line in textwrap.wrap(self.reason, width=85):
            self.layout.label(text=line)
        self.layout.prop(self, 'memory_mb')
        self.layout.label(text='Retry source qualification before opening field parameters')

    def begin(self, context):
        from .jobs import Job
        self._source, self._dataset, self._digest, self._fingerprint = science_binding(context)
        if hasattr(self, '_retry_binding'):
            same_science_source(context, *self._retry_binding)
        return Job('qualify_science', dataset=self._dataset, dataset_sha256=self._digest, memory_mb=self.memory_mb)

    def accept(self, context, report):
        same_science_source(context, self._source, self._dataset, self._digest, self._fingerprint)
        if report['dataset_sha256'] != self._digest or report['science_sha256'] != self._fingerprint:
            raise ValueError('Scientific qualification identity does not match this request')
        if not report['eligible']:
            if report.get('refusal_kind') == 'resource' and report['minimum_working_bytes'] <= 16384 * 1024**2:
                import math
                bpy.ops.qcblender.qualify_science('INVOKE_DEFAULT', reason=report['reason'],
                    memory_mb=max(32, math.ceil(report['minimum_working_bytes'] / 1024**2)))
                return
            raise ValueError(report['reason'])
        _qualifications[(self._digest, self._fingerprint)] = report['preview']
        bpy.ops.qcblender.generate_field('INVOKE_DEFAULT', memory_mb=report.get('memory_mb', 512))


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
        from .capabilities import poll_action
        return poll_action(cls, context, 'generate')

    def invoke(self, context, event):
        try:
            self._source, self._dataset, self._input_digest, self._fingerprint = science_binding(context)
            self._preview = _qualifications.get((self._input_digest, self._fingerprint))
            if self._preview is None:
                bpy.ops.qcblender.qualify_science('EXEC_DEFAULT', memory_mb=self.memory_mb)
                # The qualification owns its modal handler. Finish this dispatcher so
                # the later generation operator can record its own native undo step.
                return {'FINISHED'}
        except (ValueError, OSError, KeyError, MemoryError) as error:
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
                from ..science_preflight import preview_orbital
                try:
                    selected = preview_orbital(self._preview, self.spin, self.orbital_choice, self.orbital)
                    layout.label(text=f"Source MO {selected['source_number']} | occupation {selected['occupation']:.6g}")
                    layout.label(text=f"Energy: {selected['energy_hartree']} Hartree")
                except ValueError as error:
                    layout.label(text=str(error), icon='ERROR')
        layout.prop(self, 'spacing')
        layout.prop(self, 'padding')
        layout.prop(self, 'memory_mb')
        if hasattr(self, '_preview'):
            from ..science_preflight import preview_grid, preview_resources
            import math
            try:
                grid = preview_grid(self._preview, self.spacing, self.padding)
                layout.label(text='Grid: ' + ' × '.join(map(str, grid['shape'])) + f" | {math.prod(grid['shape']):,} voxels")
                resources = preview_resources(self._preview, grid, self.quantity, self.memory_mb, validate=False)
                layout.label(text=f"Dataset: {resources['dataset_bytes'] / 1024**2:.2f} MiB / 1024 MiB")
                layout.label(text=f"Evaluation estimate: {resources['minimum_working_bytes'] / 1024**2:.2f} MiB / {self.memory_mb} MiB")
                if resources['refusal_reason']:
                    layout.label(text=resources['refusal_reason'], icon='ERROR')
            except (ValueError, MemoryError) as error:
                layout.label(text=str(error), icon='ERROR')
        layout.label(text='Grid limits require convergence checks for quantitative use')

    def begin(self, context):
        from ..science_preflight import preview_grid, preview_resources, preview_orbital
        from .jobs import Job
        if not getattr(self, '_preview', None):
            raise ValueError('Invoke Generate Quantum Field to qualify the source first')
        same_science_source(context, self._source, self._dataset, self._input_digest, self._fingerprint)
        if self.quantity == 'orbital_amplitude':
            self.orbital = preview_orbital(self._preview, self.spin, self.orbital_choice, self.orbital)['source_number']
        grid = preview_grid(self._preview, self.spacing, self.padding)
        preview_resources(self._preview, grid, self.quantity, self.memory_mb)
        return Job('evaluate', dataset=self._dataset, dataset_sha256=self._input_digest,
                   science_sha256=self._fingerprint, grid=grid,
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
        from .capabilities import poll_action
        return poll_action(cls, context, 'declare')

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


class QCBLENDER_OT_set_view_style(bpy.types.Operator):
    bl_idname = 'qcblender.set_view_style'
    bl_label = 'Set QC View Style'
    bl_options = {'REGISTER', 'UNDO'}

    socket_id: StringProperty(options={'HIDDEN'})
    style: IntProperty(min=0, max=2, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') in ('atoms', 'field')

    def execute(self, context):
        from .graph import view_modifier
        from .parameters import STYLE_SOCKETS

        try:
            modifier = view_modifier(context.object)
            valid = any(item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                        and item.name == STYLE_SOCKETS[context.object['qc_view_kind']]
                        and item.identifier == self.socket_id
                        for item in modifier.node_group.interface.items_tree)
            if not valid or self.socket_id not in modifier:
                raise ValueError('Selected QC style input is unavailable')
            modifier[self.socket_id] = self.style
            context.object.update_tag()
            context.object.data.update()
        except ValueError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def view_parameter_state(obj):
    """Read node controls only; shared by section visibility and drawing."""
    from .graph import view_modifier
    from .parameters import socket_group
    from .capabilities import record
    field = record(obj, 'qc_field')
    modifier = view_modifier(obj)
    items = [item for item in modifier.node_group.interface.items_tree
             if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.identifier in modifier]
    values = {item.name: modifier.get(item.identifier) for item in items}
    quantity = field.get('quantity', '')
    color_unit = record(obj, 'qc_color_source').get('unit', field.get('unit', ''))
    materials = [modifier.get(item.identifier) for item in items
                 if item.socket_type == 'NodeSocketMaterial'
                 and socket_group(item.name, item.socket_type, values, quantity)]
    for node in modifier.node_group.nodes:
        for control in node.inputs:
            if control.type == 'MATERIAL' and not control.is_linked and control.default_value and control.default_value not in materials:
                materials.append(control.default_value)
    return modifier, items, values, quantity, color_unit, materials


def parameter_section_available(obj, group):
    from .parameters import socket_group
    try:
        modifier, items, values, quantity, unit, materials = view_parameter_state(obj)
    except ValueError:
        return False
    return (any(socket_group(item.name, item.socket_type, values, quantity) == group for item in items)
            or (group == '材质' and any(materials))
            or any(_material_section(node) == group for mat in materials if mat and mat.use_nodes
                   for node in mat.node_tree.nodes)
            or (group == '颜色映射' and obj.get('qc_view_kind') in ('atoms', 'field', 'slice')))


def draw_view_parameters(layout, obj, section=None):
    """Edit the existing node controls in their native Properties sections."""
    from .parameters import GROUPS, STYLES, STYLE_SOCKETS, socket_group, socket_label
    from .capabilities import record
    field = record(obj, 'qc_field')
    try:
        modifier, items, values, quantity, color_unit, materials = view_parameter_state(obj)
    except ValueError as error:
        layout.label(text=str(error), icon='INFO')
        return

    for group in GROUPS:
        if section is not None and group != section:
            continue
        grouped = [item for item in items if socket_group(item.name, item.socket_type, values, quantity) == group]
        material_controls = (group == '材质' and any(materials)) or any(
            _material_section(node) == group
            for mat in materials if mat and mat.use_nodes for node in mat.node_tree.nodes)
        color_binding = group == '颜色映射' and obj.get('qc_view_kind') in ('atoms', 'field', 'slice')
        if not grouped and not material_controls and not color_binding:
            continue
        box = layout if section else layout.box()
        if section is None:
            box.label(text=group)
        if group == '图例排版':
            box.label(text='尺寸属于视图本地布局单位')
            if not modifier.node_group.get('qc_legend_layout'):
                box.operator('qcblender.upgrade_legend', text='升级为可调图例')
        if group == '空间观察' and (any(item.name.startswith(('Plane ', 'Box ')) for item in grouped)
                                  or any(mat and mat.get('qc_fog') for mat in materials)):
            box.label(text='裁剪坐标：视图局部坐标；位置与范围单位为 Å')
        if group == '颜色映射':
            if color_binding:
                box.operator('qcblender.select_color_field', text='选择／替换着色场')
            if obj.get('qc_color_source'):
                row = box.row(align=True)
                row.operator('qcblender.symmetric_color_range', text='零中心对称')
                row.operator('qcblender.read_color_range', text='读取有效范围')
                box.label(text='超范围：端点颜色；无效采样：洋红色')
            for prefix in ('Color', 'Charge'):
                if prefix + ' Center' in values and not values[prefix + ' Minimum'] < values[prefix + ' Center'] < values[prefix + ' Maximum']:
                    box.label(text=prefix + ': 最小值 < 中心值 < 最大值', icon='ERROR')
        for item in grouped:
            if item.name == STYLE_SOCKETS.get(obj.get('qc_view_kind')):
                row = box.row(align=True)
                row.label(text='样式')
                for value, label in enumerate(STYLES[obj['qc_view_kind']]):
                    button = row.operator('qcblender.set_view_style', text=label,
                                          depress=modifier.get(item.identifier) == value)
                    button.socket_id, button.style = item.identifier, value
            else:
                box.prop(modifier, '["' + item.identifier + '"]',
                         text=socket_label(item.name, quantity, color_unit if item.name.startswith('Color ') else field.get('unit', '')))
        for mat in materials:
            if mat:
                draw_material_controls(box, mat, group, color_unit)
