from ..i18n import enum_items, error_text, iface, tip, ui_layout
from .node_identity import node_socket, socket_name
import json
import hashlib
import textwrap
from functools import lru_cache
from pathlib import Path

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ImportHelper
from .index_ranges import bounded_int, orbital_bounds, limit_orbital

ADDON_ID = __package__.rsplit('.', 1)[0]
_operations = {}
_qualifications = {}
_qualification_handoffs = {}


def clear_qualification_handoffs(*args):
    callbacks = [entry['callback'] for entry in _qualification_handoffs.values()]
    _qualification_handoffs.clear()
    for callback in callbacks:
        try:
            if bpy.app.timers.is_registered(callback):
                bpy.app.timers.unregister(callback)
        except (RuntimeError, ReferenceError) as error:
            print('QCBlender qualification timer cleanup: ' + str(error))


def _handoff_diagnostic(error):
    message = iface('Scientific qualification handoff: {error}', error=error_text(error))
    print('QCBlender ' + message)

    def draw(menu, context):
        for line in textwrap.wrap(message, width=75):
            ui_layout(menu.layout).label(text=line)

    try:
        bpy.context.window_manager.popup_menu(draw, title=iface('Scientific qualification'), icon='ERROR')
    except (RuntimeError, ReferenceError, AttributeError) as popup_error:
        print('QCBlender qualification diagnostic popup: ' + str(popup_error))


def qualification_context_available(override):
    window, area, region = (override[name] for name in ('window', 'area', 'region'))
    # RNA collection membership accepts names, so compare its actual members.
    return (window in tuple(bpy.context.window_manager.windows)
            and area in tuple(window.screen.areas) and region in tuple(area.regions))


def defer_qualification_handoff(parent_id, binding, ui_context, action, parameters, preview=None):
    token = object()
    entry = {'parent_id': parent_id, 'binding': binding, 'ui_context': dict(ui_context),
             'action': action, 'parameters': dict(parameters), 'preview': preview}

    def dispatch():
        pending = _qualification_handoffs.get(token)
        if pending is None:
            return None
        if pending['parent_id'] in _operations:
            return .05
        _qualification_handoffs.pop(token)
        try:
            override = pending['ui_context']
            if not qualification_context_available(override):
                raise ValueError('The qualification window or editor changed; invoke Generate again')
            with bpy.context.temp_override(**override):
                same_science_source(bpy.context, *pending['binding'])
                key = pending['binding'][2:]
                cached = _qualifications.get(key)
                if pending['action'] == 'generate':
                    if cached is None or cached is not pending['preview']:
                        raise ValueError('Scientific qualification was cleared or replaced; invoke Generate again')
                    result = bpy.ops.qcblender.generate_field('INVOKE_DEFAULT', True, **pending['parameters'])
                else:
                    if cached is not None:
                        raise ValueError('Scientific qualification changed before its budget retry')
                    result = bpy.ops.qcblender.qualify_science('INVOKE_DEFAULT', **pending['parameters'])
                if 'CANCELLED' in result:
                    raise RuntimeError('The qualification dialog handoff was cancelled')
        except (RuntimeError, ValueError, OSError, KeyError, ReferenceError, MemoryError, AttributeError, TypeError) as error:
            _handoff_diagnostic(error)
        return None

    entry['callback'] = dispatch
    _qualification_handoffs[token] = entry
    try:
        bpy.app.timers.register(dispatch, first_interval=0)
    except (RuntimeError, ValueError) as error:
        _qualification_handoffs.pop(token)
        raise RuntimeError('Cannot defer scientific qualification dialog: ' + str(error)) from error


def clear_qualifications(*args):
    clear_qualification_handoffs()
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
        return 'material'
    if role == 'opacity_ramp':
        return 'material'
    control = node.get('qc_control', '')
    if control.startswith(('Plane ', 'Box ')):
        return 'spatial'
    if control.startswith('Color '):
        return 'color'
    if control == 'Display Threshold':
        return 'geometry'
    return 'material' if control else None


def draw_material_controls(layout, mat, section='material', unit='', preset_role=''):
    layout = ui_layout(layout)
    if not mat or not mat.use_nodes:
        return
    nodes = mat.node_tree.nodes
    from .views import node_by_type

    shader = node_by_type(nodes, 'ShaderNodeBsdfPrincipled')
    if shader and section == 'material':
        for name in ('Base Color', 'Alpha', 'Roughness'):
            if not node_socket(shader.inputs, name).is_linked:
                layout.prop(node_socket(shader.inputs, name), 'default_value', text=name)
    for node in nodes:
        if node.get('qc_role') in ('color_ramp', 'opacity_ramp') and section == _material_section(node):
            layout.label(text='Opacity multiplier' if node['qc_role'] == 'opacity_ramp' else 'Color map')
            layout.template_color_ramp(node, 'color_ramp', expand=True)
            if node['qc_role'] == 'color_ramp' and preset_role:
                row = layout.row()
                row.operator_context = 'INVOKE_DEFAULT'
                operator = row.operator('qcblender.apply_color_preset', text='Apply Color Ramp Preset…')
                operator.material_role = preset_role
        elif node.get('qc_role') == 'color_invert' and section == 'material':
            layout.prop(node_socket(node.outputs, 0), 'default_value', text='Reverse (0 or 1)')
        elif node.get('qc_control') and section == _material_section(node):
            if node['qc_control'] in ('Plane Origin', 'Plane Normal') and not next(
                    (node_socket(other.outputs, 0).default_value for other in nodes if other.get('qc_control') == 'Plane Enabled'), False):
                continue
            if node['qc_control'] in ('Box Minimum', 'Box Maximum') and not next(
                    (node_socket(other.outputs, 0).default_value for other in nodes if other.get('qc_control') == 'Box Enabled'), False):
                continue
            if node.bl_idname == 'ShaderNodeCombineXYZ':
                label = (iface('{control} [view-local direction, dimensionless]', control=iface(node['qc_control']))
                         if node['qc_control'] == 'Plane Normal' else
                         iface('{control} [view-local Å]', control=iface(node['qc_control'])))
                layout.label(text=label, translate=False)
                row = layout.row(align=True)
                for item in node.inputs:
                    row.prop(item, 'default_value', text=socket_name(item))
            else:
                label = node['qc_control']
                if label in ('Color Minimum', 'Color Maximum', 'Display Threshold', 'Opacity Range'):
                    label = iface('{control} [{unit}]', control=iface(label), unit=unit or iface('Unit unknown'))
                layout.prop(node_socket(node.outputs, 0), 'default_value', text=label)
    if mat.get('qc_fog') and section == 'material':
        layout.label(text='Optical display; source values unchanged')


def cancel_operations():
    clear_qualification_handoffs()
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
            self.report({'ERROR'}, error_text(error))
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
            self.report({'ERROR'}, error_text(error))
            self.cancel(context)
            return {'CANCELLED'}
        for error in finish_operation(self):
            self.report({'ERROR'}, error_text(error))
        return {'FINISHED'}

    def cancel(self, context):
        timer_errors = finish_operation(self)
        job = getattr(self, '_job', None)
        if job is None:
            for error in timer_errors:
                self.report({'ERROR'}, error_text(error))
            return None
        report = job.cancel()
        messages = timer_errors + report['errors']
        if messages or report['status'] != 'exited':
            details = '; '.join(messages) or 'Worker exit has not been confirmed'
            self.report({'ERROR'}, iface('Cancellation {value0}; PID {value1}; {value2}: {value3}', value0=report["status"], value1=report["pid"], value2=report["directory"], value3=details))
        # Blender's Operator.cancel callback must return None.


class QCBlenderPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID
    runtime_report: StringProperty(name='Runtime report', default='')
    data_output_directory: StringProperty(name='Data Export Directory', subtype='DIR_PATH', default='')

    def draw(self, context):
        ui_layout(self.layout).prop(self, 'data_output_directory')
        ui_layout(self.layout).label(text='Empty: saved project directory; unsaved projects use the system Documents directory')
        ui_layout(self.layout).operator('qcblender.check_runtime', icon='CHECKMARK')
        if self.runtime_report:
            report = json.loads(self.runtime_report)
            for entry in report.get('modules', []):
                ui_layout(self.layout).label(text=f"{entry['module']}: {entry['status']}")
            if report.get('error'):
                ui_layout(self.layout).label(text=error_text(report['error']), icon='ERROR')


class QCBLENDER_OT_check_runtime(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.check_runtime'
    bl_label = 'Check Scientific Runtime'

    def begin(self, context):
        from .jobs import Job
        return Job('diagnose')

    def accept(self, context, report):
        context.preferences.addons[ADDON_ID].preferences.runtime_report = json.dumps(report)
        self.report({'INFO'}, error_text('Scientific runtime checks passed'))


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
        self.report({'INFO'}, error_text('Imported scientific data; 1 Blender unit = 1 angstrom'))


@lru_cache(maxsize=16)
def cached_job_choices(summary):
    # Blender retains references to dynamic enum strings beyond the callback.
    jobs = json.loads(summary)['jobs'] if summary else []
    return [(str(i), f"{i+1}: {job['status']} | {job['route'] or 'Not recorded'}",
             f"Lines {job['line_start']}–{job['line_end']}") for i, job in enumerate(jobs)]


def job_choices(self, context):
    jobs = json.loads(self.summary).get('jobs', []) if self.summary else []
    return enum_items([(identifier,
        iface('{number}: {status} | {route}', number=index + 1,
              status=iface(jobs[index]['status']), route=jobs[index]['route'] or iface('Not recorded')),
        tip('Lines {start}–{end}', start=jobs[index]['line_start'], end=jobs[index]['line_end']))
        for index, (identifier, label, description) in enumerate(cached_job_choices(self.summary))])


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
        layout = ui_layout(self.layout)
        layout.prop(self, 'job')
        record = json.loads(self.summary)['jobs'][int(self.job)]
        layout.label(text=iface('Lines {value0}–{value1} | {value2}', value0=record['line_start'], value1=record['line_end'], value2=record['status']))
        for line in textwrap.wrap(record['route'] or 'Not recorded', width=85):
            layout.label(text=line)
        layout.label(text=iface('Explicit geometry: {value0}', value0='detected; validated on import' if record['explicit_geometry'] else 'not detected'))
        selection = record['energy_selection']
        energy = next((e for e in record['energies'] if e['id'] == selection.get('record_id')), None)
        layout.label(text=iface('Energy: {value0} Hartree', value0=energy['value_hartree']) if energy else iface('Energy: {status}', status=iface(selection['status'])))
        if not energy and record['energies']:
            layout.label(text=iface('Last records ({value0} total; not a selected final energy):', value0=len(record['energies'])))
            for item in record['energies'][-3:]:
                layout.label(text=iface('L{value0} {value1} / {value2}: {value3} Hartree', value0=item['line_start'], value1=item['method'], value2=item['kind'], value3=item['value_hartree']))
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

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'generate')

    def invoke(self, context, event):
        try:
            self._retry_binding = science_binding(context)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        for line in textwrap.wrap(error_text(self.reason), width=85):
            ui_layout(self.layout).label(text=line)
        ui_layout(self.layout).prop(self, 'memory_mb')
        ui_layout(self.layout).label(text='Retry source qualification before opening field parameters')

    def begin(self, context):
        from .jobs import Job
        self._source, self._dataset, self._digest, self._fingerprint = science_binding(context)
        self._handoff_context = {name: getattr(context, name) for name in ('window', 'area', 'region')}
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
                defer_qualification_handoff(id(self),
                    (self._source, self._dataset, self._digest, self._fingerprint), self._handoff_context,
                    'retry', {'reason': report['reason'],
                              'memory_mb': max(32, math.ceil(report['minimum_working_bytes'] / 1024**2))})
                return
            raise ValueError(report['reason'])
        _qualifications[(self._digest, self._fingerprint)] = report['preview']
        defer_qualification_handoff(id(self),
            (self._source, self._dataset, self._digest, self._fingerprint), self._handoff_context,
            'generate', {'memory_mb': report.get('memory_mb', 512)}, report['preview'])


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
    spin: EnumProperty(name='Spin', items=[('alpha', 'Alpha', ''), ('beta', 'Beta', '')], update=limit_orbital)
    orbital: bounded_int('orbital', orbital_bounds, name='Orbital number (1-based)', default=1, min=1)
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
                result = bpy.ops.qcblender.qualify_science('EXEC_DEFAULT', memory_mb=self.memory_mb)
                if 'CANCELLED' in result:
                    return {'CANCELLED'}
                # This dispatcher changes no data. The independent qualification job
                # owns its modal handler and schedules the generation dialog later.
                return {'CANCELLED'}
        except (RuntimeError, ValueError, OSError, KeyError, MemoryError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        limit_orbital(self, context)
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.prop(self, 'quantity')
        if self.quantity == 'orbital_amplitude':
            layout.prop(self, 'spin')
            layout.prop(self, 'orbital_choice')
            if self.orbital_choice == 'EXPLICIT':
                row = layout.row()
                count = orbital_bounds(self, context)[1]
                row.enabled = bool(count)
                row.prop(self, 'orbital')
                if count:
                    layout.label(text=iface('Orbitals 1-{value0}', value0=count))
            if hasattr(self, '_preview'):
                from ..science_preflight import preview_orbital
                try:
                    selected = preview_orbital(self._preview, self.spin, self.orbital_choice, self.orbital)
                    layout.label(text=iface('Source MO {value0} | occupation {value1:.6g}', value0=selected['source_number'], value1=selected['occupation']))
                    layout.label(text=iface('Energy: {value0} Hartree', value0=selected['energy_hartree']))
                except ValueError as error:
                    layout.label(text=error_text(error), icon='ERROR')
        layout.prop(self, 'spacing')
        layout.prop(self, 'padding')
        layout.prop(self, 'memory_mb')
        if hasattr(self, '_preview'):
            from ..science_preflight import preview_grid, preview_resources
            import math
            try:
                grid = preview_grid(self._preview, self.spacing, self.padding)
                layout.label(text=iface('Grid: {value0} | {value1:,} voxels', value0=' × '.join(map(str, grid['shape'])), value1=math.prod(grid['shape'])))
                resources = preview_resources(self._preview, grid, self.quantity, self.memory_mb, validate=False)
                layout.label(text=iface('Dataset: {value0:.2f} MiB / 1024 MiB', value0=resources['dataset_bytes'] / 1024**2))
                layout.label(text=iface('Evaluation estimate: {value0:.2f} MiB / {value1} MiB', value0=resources['minimum_working_bytes'] / 1024**2, value1=self.memory_mb))
                if resources['refusal_reason']:
                    for line in textwrap.wrap(error_text(resources['refusal_reason']), width=75):
                        layout.label(text=line, icon='ERROR')
            except (ValueError, MemoryError) as error:
                layout.label(text=error_text(error), icon='ERROR')
        for line in textwrap.wrap(iface('Grid limits require convergence checks for quantitative use'), width=75):
            layout.label(text=line)

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
        self.report({'INFO'}, error_text('Quantum field ready; adjust isovalue in the geometry node modifier'))


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
        ui_layout(self.layout).prop(self, 'quantity')
        if self.quantity == 'custom':
            ui_layout(self.layout).prop(self, 'custom_quantity')
            ui_layout(self.layout).prop(self, 'custom_unit')
        ui_layout(self.layout).label(text='Confirm against the generating calculation; values are not converted.')

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
        self.report({'INFO'}, error_text('Saved explicit user-assigned quantity and units; array values unchanged'))


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
                        and socket_name(item) == STYLE_SOCKETS[context.object['qc_view_kind']]
                        and item.identifier == self.socket_id
                        for item in modifier.node_group.interface.items_tree)
            if not valid or self.socket_id not in modifier:
                raise ValueError('Selected QC style input is unavailable')
            modifier[self.socket_id] = self.style
            context.object.update_tag()
            context.object.data.update()
        except ValueError as error:
            self.report({'ERROR'}, error_text(error))
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
    values = {socket_name(item): modifier.get(item.identifier) for item in items}
    quantity = field.get('quantity', '')
    color_unit = record(obj, 'qc_color_source').get('unit', field.get('unit', ''))
    materials = [modifier.get(item.identifier) for item in items
                 if item.socket_type == 'NodeSocketMaterial'
                 and socket_group(socket_name(item), item.socket_type, values, quantity)]
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
    return (any(socket_group(socket_name(item), item.socket_type, values, quantity) == group for item in items)
            or (group == 'material' and any(materials))
            or any(_material_section(node) == group for mat in materials if mat and mat.use_nodes
                   for node in mat.node_tree.nodes)
            or (group == 'color' and obj.get('qc_view_kind') in ('atoms', 'field', 'slice')))


def draw_view_parameters(layout, obj, section=None):
    """Edit the existing node controls in their native Properties sections."""
    layout = ui_layout(layout)
    from .parameters import GROUPS, GROUP_LABELS, STYLES, STYLE_SOCKETS, socket_group, socket_item_label
    from .capabilities import record
    field = record(obj, 'qc_field')
    try:
        modifier, items, values, quantity, color_unit, materials = view_parameter_state(obj)
    except ValueError as error:
        layout.label(text=error_text(error), icon='INFO')
        return

    preset_materials = {}
    if section in (None, 'material'):
        from .copy_display import _state
        try:
            preset_materials = {role: mat for role, (mat, _) in _state(obj)['materials'].items()
                                if role in ('scalar_map', 'charge_map')}
        except (ValueError, KeyError, TypeError, ReferenceError):
            # Custom graphs keep their native controls without preset actions.
            pass

    for group in GROUPS:
        if section is not None and group != section:
            continue
        grouped = [item for item in items if socket_group(socket_name(item), item.socket_type, values, quantity) == group]
        material_controls = (group == 'material' and any(materials)) or any(
            _material_section(node) == group
            for mat in materials if mat and mat.use_nodes for node in mat.node_tree.nodes)
        color_binding = group == 'color' and obj.get('qc_view_kind') in ('atoms', 'field', 'slice')
        if not grouped and not material_controls and not color_binding:
            continue
        box = layout if section else layout.box()
        if section is None:
            box.label(text=GROUP_LABELS[group])
        if group == 'legend':
            box.label(text='Dimensions use view-local layout units')
            if not modifier.node_group.get('qc_legend_layout'):
                box.operator('qcblender.upgrade_legend', text='Upgrade to Adjustable Legend')
        if group == 'spatial' and (any(socket_name(item).startswith(('Plane ', 'Box ')) for item in grouped)
                                  or any(mat and mat.get('qc_fog') for mat in materials)):
            box.label(text='Clipping uses view-local coordinates; positions and bounds are in Å')
        if group == 'color':
            if color_binding:
                box.operator('qcblender.select_color_field', text='Select / Replace Color Field')
            if obj.get('qc_color_source'):
                row = box.row(align=True)
                row.operator('qcblender.symmetric_color_range', text='Zero-Centered Symmetry')
                row.operator('qcblender.read_color_range', text='Read Valid Range')
                box.label(text='Out of range: endpoint colors; invalid samples: magenta')
            for prefix in ('Color', 'Charge'):
                if prefix + ' Center' in values and not values[prefix + ' Minimum'] < values[prefix + ' Center'] < values[prefix + ' Maximum']:
                    box.label(text=iface('{value0}: minimum < center < maximum', value0=prefix), icon='ERROR')
        for item in grouped:
            if socket_name(item) == STYLE_SOCKETS.get(obj.get('qc_view_kind')):
                row = box.row(align=True)
                row.label(text='Style')
                for value, label in enumerate(STYLES[obj['qc_view_kind']]):
                    button = row.operator('qcblender.set_view_style', text=label,
                                          depress=modifier.get(item.identifier) == value)
                    button.socket_id, button.style = item.identifier, value
            else:
                box.prop(modifier, '["' + item.identifier + '"]',
                         text=socket_item_label(item, quantity, color_unit if socket_name(item).startswith('Color ') else field.get('unit', '')), translate=False)
        for mat in materials:
            if mat:
                role = next((name for name, target in preset_materials.items() if target == mat), '')
                draw_material_controls(box, mat, group, color_unit, role)
