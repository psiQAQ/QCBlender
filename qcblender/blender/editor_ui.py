"""File workflows and read-only summaries in the sidebar; object tools in Properties."""
from ..i18n import error_text, iface, tip, ui_layout
import json
import textwrap
import unicodedata

import bpy
from bpy.props import EnumProperty

from .capabilities import action_button, capability, record
from .source_browser import cached_metadata, source_object


def is_qc(context):
    obj = context.object
    return obj is not None and bool(obj.get('qc_view_kind') or obj.get('qc_dataset'))


def sidebar_subject(obj):
    """Resolve only the existing QC ownership rules, never a previous selection."""
    if obj is None:
        return None
    owner = source_object(obj)
    return owner if owner.get('qc_view_kind') or owner.get('qc_dataset') else None


def compact_lines(text, width, max_lines=3):
    """Bound narrow-sidebar text using display width, including CJK characters."""
    lines, current, used = [], '', 0
    for char in str(text).replace('\r', ' ').replace('\n', ' '):
        size = 2 if unicodedata.east_asian_width(char) in {'W', 'F'} else 1
        if used + size > width and current:
            lines.append(current)
            if len(lines) == max_lines:
                lines[-1] = lines[-1].rstrip() + '…'
                return lines
            current, used = '', 0
        current += char
        used += size
    if current:
        lines.append(current)
    return lines


def draw_sidebar_summary(layout, context, *, details):
    from .source_browser import cached_object_summary
    result = cached_object_summary(context.object)
    if not result['available']:
        return
    width = max(16, int(context.region.width / 7) - 6)

    def line(text):
        for part in compact_lines(text, width):
            layout.label(text=part, translate=False)

    def row(entry):
        value = entry['value']
        if value is None and entry.get('shape') is not None:
            value = ' × '.join(map(str, entry['shape']))
        elif value is None:
            value = iface('Not recorded')
        elif entry['key'] == 'view_type':
            value = iface({
                'atoms': 'Atoms', 'field': 'Scalar Field', 'slice': 'Slice', 'fog': 'Volume Fog',
                'dipole': 'Dipole', 'spectrum': 'Spectrum', 'scatter': 'Scatter', 'nbo': 'NBO',
                'analysis': 'Analysis', 'profile': 'Line Profile', 'annotation': 'Annotation',
            }.get(value, value))
        text = f"{iface(entry['label'])}: {value}"
        if entry.get('unit'):
            text += f" [{entry['unit']}]"
        if entry.get('shape') is not None and entry['value'] is not None:
            text += ' · ' + ' × '.join(map(str, entry['shape']))
        if entry.get('dtype'):
            text += ' · ' + entry['dtype']
        line(text)

    for entry in result['details' if details else 'short']:
        row(entry)
    if details:
        for category in result['categories']:
            layout.separator()
            count = category['count'] if category['count'] is not None else iface('Not recorded')
            line(f"{iface(category['label'])}: {count}")
            for entry in category['items']:
                row(entry)
            if category['omitted']:
                line(iface('Additional records: {value0}; inspect Object Properties', value0=category['omitted']))
    states = {'uncached': 'Source summary is not cached; refresh sources in Object Properties',
              'error': 'Source unavailable; inspect Object Properties',
              'unbound': 'No scientific dataset is bound to this object'}
    if result['state'] in states:
        line(iface(states[result['state']]))


def summary(layout, obj):
    layout = ui_layout(layout)
    layout.label(text=obj.name, icon='OBJECT_DATA', translate=False)
    layout.label(text=iface('Source: {value0}', value0=obj.get('qc_source_filename', iface('Not recorded'))))
    if obj.get('qc_source_job', -1) >= 0:
        layout.label(text=iface('Calculation {value0}', value0=obj['qc_source_job'] + 1))
    field = record(obj, 'qc_field')
    if field:
        layout.label(text=f"{field.get('quantity', iface('Not recorded'))} [{field.get('unit', iface('Not recorded'))}]")
        layout.label(text=iface('Grid: {value0}', value0=' × '.join(map(str, field.get('shape', [])))))
    color = record(obj, 'qc_color_source')
    if color:
        layout.label(text=iface('Color: {value0} [{value1}]', value0=color.get('quantity', iface('Not recorded')), value1=color.get('unit', iface('Not recorded'))))
    if obj.get('qc_optimization_record'):
        step = record(obj, 'qc_optimization_record')
        layout.label(text=iface('Optimization Step {value0} / {value1}', value0=obj.get('qc_optimization_step'), value1=obj.get('qc_optimization_count')))
        if step.get('energy'):
            layout.label(text=iface('{value0:.10f} Hartree', value0=step['energy']['value_hartree']))
    if obj.get('qc_irc'):
        step = record(obj, 'qc_irc_record')
        layout.label(text=iface('IRC Step {value0} / {value1}', value0=obj.get('qc_irc_step'), value1=step.get('count', iface('Not recorded'))))
    if obj.get('qc_trajectory_frame'):
        layout.label(text=iface('XYZ Frame {value0} / {value1}', value0=obj['qc_trajectory_frame'], value1=obj['qc_trajectory_count']))
    if obj.get('qc_mode_frequency_cm-1') is not None:
        layout.label(text=iface('Vibration {value0}: {value1:.4f} cm⁻¹', value0=obj.get('qc_mode_source_number'), value1=obj['qc_mode_frequency_cm-1']))
    probe = record(obj, 'qc_probe')
    if probe.get('value') is not None:
        layout.label(text=iface('Latest sample: {value0:.8g} {value1}', value0=probe['value'], value1=probe.get('unit', '')))


class QCBLENDER_OT_open_properties(bpy.types.Operator):
    bl_idname = 'qcblender.open_properties'
    bl_label = 'Open QC Properties'
    editor: EnumProperty(items=[('OBJECT', 'Object', ''), ('MATERIAL', 'Material', ''),
                               ('RENDER', 'Render', ''), ('OUTPUT', 'Output', '')])

    @classmethod
    def description(cls, context, properties):
        return tip({
            'OBJECT': 'Open and pin Object Properties for the active QC object or the owning QC object of its selected helper',
            'MATERIAL': 'Open Material Properties for the active object and pin that object in the existing Properties Editor',
            'RENDER': 'Open render settings in the existing Properties Editor',
            'OUTPUT': 'Open output settings in the existing Properties Editor',
        }.get(properties.editor, 'Open the requested settings in the existing Properties Editor'))

    def execute(self, context):
        if self.editor in ('OBJECT', 'MATERIAL') and context.object is None:
            self.report({'WARNING'}, error_text('Select an object first'))
            return {'CANCELLED'}
        areas = [a for a in context.screen.areas if a.type == 'PROPERTIES']
        if not areas:
            self.report({'ERROR'}, error_text('Switch an editor to the Properties Editor first'))
            return {'CANCELLED'}
        area = areas[0]
        if self.editor in ('OBJECT', 'MATERIAL'):
            target = sidebar_subject(context.object) if self.editor == 'OBJECT' else context.object
            area.spaces.active.pin_id = target if target is not None else context.object
            area.spaces.active.use_pin_id = True
        area.spaces.active.context = self.editor
        area.tag_redraw()
        return {'FINISHED'}


class QCBLENDER_PT_main(bpy.types.Panel):
    bl_label = 'Import and Export'
    bl_idname = 'QCBLENDER_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_order = 0

    def draw(self, context):
        layout = ui_layout(self.layout)
        imports = layout.box()
        imports.label(text='Import')
        imports.operator('qcblender.import_calculation', text='Import Gaussian / Cube / XYZ', icon='IMPORT')
        imports.operator('qcblender.import_irc_path', text='Import IRC Path')
        obj = context.object
        if obj is not None:
            from .data_export import export_choices
            if source_object(obj).get('qc_dataset') and export_choices(None, context):
                exporting = layout.box()
                exporting.label(text='Export')
                exporting.label(text=iface('Source object: {value0}', value0=source_object(obj).name), translate=False)
                exporting.operator('qcblender.export_data', text='Export Data and Parameter Summary', icon='EXPORT')


class QCBLENDER_PT_dataset(bpy.types.Panel):
    bl_label = 'Current QC Object'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return sidebar_subject(context.object) is not None

    def draw(self, context):
        layout = ui_layout(self.layout)
        draw_sidebar_summary(layout, context, details=False)
        obj = sidebar_subject(context.object)
        layout.label(text=iface('Properties target: {value0}', value0=obj.name), translate=False)
        layout.operator('qcblender.open_properties', text='Open Object Properties', icon='PROPERTIES').editor = 'OBJECT'


class QCBLENDER_PT_dataset_details(bpy.types.Panel):
    bl_label = 'Data and Source Details'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return sidebar_subject(context.object) is not None

    def draw(self, context):
        draw_sidebar_summary(ui_layout(self.layout), context, details=True)


class QCBLENDER_PT_create(bpy.types.Panel):
    bl_label = 'Create Views and Tools'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        layout, obj = ui_layout(self.layout), context.object
        _action_group(layout, context, 'Compute', [
            ('generate', 'qcblender.generate_field', 'Generate Quantum Field'),
        ])
        views = layout.box()
        views.label(text='Display Views')
        for action, operator, text in [
            ('surface', 'qcblender.add_surface_layer', 'Create Isosurface Layer'),
            ('fog', 'qcblender.create_fog', 'Create Volume Fog'),
        ]:
            action_button(views, context, action, operator, text)
        if obj.get('qc_view_kind') == 'atoms':
            views.operator('qcblender.local_selection_layer', text='Create Local Display Layer')
        views.operator('qcblender.new_current_view', text='Create Current-Version View')
        _action_group(layout, context, 'Spatial Tools', [
            ('slice', 'qcblender.create_slice', 'Create Slice'),
            ('clip', 'qcblender.add_clipping', 'Add Clipping Controls'),
            ('dipole', 'qcblender.show_dipole', 'Create Dipole Vector'),
        ])
        sampling_actions = [
            ('probe', 'qcblender.probe_field', 'Read Field Value at Cursor'),
            ('profile_start', 'qcblender.mark_profile_start', 'Mark Profile Start'),
            ('profile', 'qcblender.create_line_profile', 'Sample Line Profile Data'),
        ]
        if any(capability(context, action)[0] for action in ('probe', 'profile_start', 'profile', 'probe_click')):
            sampling = layout.box()
            sampling.label(text='Field Sampling')
            for action, operator, text in sampling_actions:
                action_button(sampling, context, action, operator, text)
            draw_probe_actions(sampling, context)
        camera = layout.box()
        camera.label(text='Camera')
        camera.operator('qcblender.create_framed_camera', text='Create Framed Camera', icon='CAMERA_DATA')


def _action_group(layout, context, title, actions):
    """Draw a titled group only when at least one action applies to this object."""
    if not any(capability(context, action)[0] for action, _, _ in actions):
        return
    group = layout.box()
    group.label(text=title)
    for action, operator, text in actions:
        action_button(group, context, action, operator, text)


class QCBLENDER_PT_external_import(bpy.types.Panel):
    bl_label = 'Import External Results'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_parent_id = 'QCBLENDER_PT_main'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_dataset'))

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.label(text=iface('Target: {value0}', value0=context.object.name), translate=False)
        _action_group(layout, context, 'Spatial Field Analysis', [
            ('paired', 'qcblender.import_paired_field', 'IGMH / IRI Paired Fields'),
            ('esp', 'qcblender.import_esp_analysis', 'ESP Surface Analysis'),
        ])
        _action_group(layout, context, 'Atom and Bond Analysis', [
            ('nbo', 'qcblender.import_nbo', 'NBO Records'),
            ('aim', 'qcblender.import_aim_analysis', 'AIM Topology'),
        ])
        _action_group(layout, context, 'Energy Decomposition', [
            ('nocv_table', 'qcblender.import_ets_nocv', 'ETS-NOCV Table'),
            ('nocv_field', 'qcblender.import_nocv_field', 'NOCV pair Cube'),
        ])


class QCBLENDER_PT_project(bpy.types.Panel):
    bl_label = 'Project and Maintenance'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    def draw(self, context):
        layout = ui_layout(self.layout)
        saving = layout.box()
        saving.label(text='Save and Archive')
        for operator, text in [('save_project', 'Save Self-Contained Project'), ('archive_project', 'Archive Project')]:
            saving.operator('qcblender.' + operator, text=text)
        obj = context.object
        recovery = layout.box()
        recovery.label(text='Recovery and Maintenance')
        for operator, text in [('rebuild_cache', 'Rebuild Display Cache'), ('relocate_dataset', 'Relocate Dataset'),
                               ('cleanup_legacy_node_assets', 'Preview and Clean Up Legacy QC Node Assets')]:
            recovery.operator('qcblender.' + operator, text=text)
        diagnostics = layout.box()
        diagnostics.label(text='Diagnostics')
        diagnostics.operator('qcblender.check_runtime', text='Check Scientific Runtime')
        if obj is not None:
            for diagnostic in json.loads(obj.get('qc_diagnostics', '[]')):
                for line in textwrap.wrap(error_text(diagnostic), width=40):
                    diagnostics.label(text=line)


class QCBLENDER_PT_object(bpy.types.Panel):
    bl_label = 'QCBlender · Object and Quantum Chemistry'
    bl_idname = 'QCBLENDER_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        summary(ui_layout(self.layout), context.object)
        ui_layout(self.layout).operator('qcblender.source_details', text='Source Details', icon='INFO')
        ui_layout(self.layout).operator('qcblender.refresh_sources', text='Refresh Sources')
        ui_layout(self.layout).operator('qcblender.associate_sources', text='Associate Selected Sources')
        action_button(ui_layout(self.layout), context, 'declare', 'qcblender.declare_field', 'Identify Cube Quantity and Unit')


class QCBLENDER_PT_scientific(bpy.types.Panel):
    bl_label = 'Scientific Records and Vibration Modes'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj, layout = context.object, ui_layout(self.layout)
        settings = obj.qc_settings
        meta = cached_metadata(obj)
        if not meta or 'error' in meta:
            layout.label(text=error_text(meta.get('error', 'Refresh source records')), icon='INFO')
            return
        layout.label(text=iface('Calculation status: {value0}', value0=meta.get('calculation_status', iface('Not recorded'))))
        field = record(obj, 'qc_field')
        if field.get('steps'):
            layout.label(text='Source grid step vectors [Å], read-only')
            for axis, step in zip('ijk', field['steps']):
                layout.label(text=axis + ': ' + ', '.join(f'{v:.6g}' for v in step))
        orbital = field.get('orbital')
        if isinstance(orbital, dict):
            for key in ('spin', 'source_number', 'occupation', 'energy_hartree'):
                layout.label(text=f"{key}: {orbital.get(key, iface('Not recorded'))}")
        if settings.energies:
            layout.template_list('QCBLENDER_UL_energies', '', settings, 'energies', settings, 'active_energy', rows=3)
            if 0 <= settings.active_energy < len(settings.energies):
                energy = json.loads(settings.energies[settings.active_energy].record)
                layout.label(text=iface('{value0:.10f} Hartree', value0=energy['value_hartree']))
                layout.label(text=f"{energy['method']} / {energy['kind']}")
        if settings.modes:
            layout.template_list('QCBLENDER_UL_modes', '', settings, 'modes', settings, 'active_mode', rows=4)
        if obj.get('qc_view_kind') == 'atoms':
            action_button(layout, context, 'charge', 'qcblender.color_charge', 'Set Atomic Charge Colors')


class _ObjectSection:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not is_qc(context):
            return False
        from .ui import parameter_section_available
        return parameter_section_available(context.object, cls.section_key)

    def draw(self, context):
        from .ui import draw_view_parameters
        draw_view_parameters(ui_layout(self.layout), context.object, self.section_key)


class QCBLENDER_PT_geometry(_ObjectSection, bpy.types.Panel):
    section_key = 'geometry'
    bl_label = 'Geometry Representation'


class QCBLENDER_PT_mapping(_ObjectSection, bpy.types.Panel):
    section_key = 'color'
    bl_label = 'Color Mapping'


class QCBLENDER_PT_legend(_ObjectSection, bpy.types.Panel):
    section_key = 'legend'
    bl_label = 'Legend Layout'


class QCBLENDER_PT_spatial(_ObjectSection, bpy.types.Panel):
    section_key = 'spatial'
    bl_label = 'Spatial View'

    def draw(self, context):
        super().draw(context)
        if context.object.get('qc_view_kind') == 'slice':
            from .interaction import _plane_record
            plane = _plane_record(context.object)
            ui_layout(self.layout).label(text=iface('Plane definition: {value0}', value0=plane.get('mode', 'FREE')))
            ui_layout(self.layout).operator('qcblender.define_slice_plane', text='Define Plane from Source Grid or Three Atoms')
            ui_layout(self.layout).label(text='3D View Toolbar: QC Slice Gizmo')
            ui_layout(self.layout).label(text='Resolution controls the slice display sample count')


class QCBLENDER_PT_advanced(_ObjectSection, bpy.types.Panel):
    section_key = 'advanced'
    bl_label = 'Advanced Parameters'


class QCBLENDER_PT_selection(bpy.types.Panel):
    bl_label = 'Local Selection and Annotations'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'atoms'

    def draw(self, context):
        layout, obj = ui_layout(self.layout), context.object
        layout.operator('qcblender.local_selection', text='Set Local Selection').mode = 'REPLACE'
        selected = record(obj, 'qc_local_selection_record')
        if selected:
            layout.label(text=iface('Fixed source numbers: {value0}', value0=','.join(map(str, selected.get('fixed_numbers', [])))))
            layout.operator('qcblender.local_selection', text='Recompute for Current Step').mode = 'RECOMPUTE'
            layout.operator('qcblender.local_selection', text='Clear Local Restriction').mode = 'CLEAR'
        row = layout.row(align=True)
        for mode, label in [('HIDE', 'Hide Hydrogen'), ('KEEP', 'Keep Specified Hydrogen'), ('RESTORE', 'Show All Hydrogen')]:
            row.operator('qcblender.hydrogen_visibility', text=label).mode = mode
        from .annotations import draw_annotations
        draw_annotations(layout, context)


class QCBLENDER_PT_material(bpy.types.Panel):
    bl_label = 'QCBlender · Node Materials'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        from .ui import parameter_section_available
        return is_qc(context) and parameter_section_available(context.object, 'material')

    def draw(self, context):
        from .ui import draw_view_parameters
        ui_layout(self.layout).label(text='Edit material nodes independently in the Shader Editor')
        draw_view_parameters(ui_layout(self.layout), context.object, 'material')


class QCBLENDER_MT_object(bpy.types.Menu):
    bl_label = 'QCBlender'

    def draw(self, context):
        if not is_qc(context):
            return
        layout = ui_layout(self.layout)
        layout.operator('qcblender.source_details', text='Source Details')
        layout.operator('qcblender.open_properties', text='Object Properties').editor = 'OBJECT'
        action_button(layout, context, 'slice', 'qcblender.create_slice', 'Create Slice')
        action_button(layout, context, 'probe', 'qcblender.probe_field', 'Read Field Value at Cursor')
        draw_probe_actions(layout, context)
        if (context.object.get('qc_view_kind') in ('field', 'slice', 'atoms')
                and len(context.selected_objects) == 2):
            layout.operator('qcblender.map_scalar', text='Map Selected Field to Active Surface')
        layout.operator('qcblender.create_framed_camera', text='Create Framed Camera')
        if context.object.get('qc_view_kind') in ('atoms', 'field', 'slice', 'fog'):
            layout.operator('qcblender.copy_display_parameters', text='Copy Display Parameters to Selected Views')


def object_context_menu(self, context):
    if is_qc(context):
        ui_layout(self.layout).menu('QCBLENDER_MT_object')


def draw_probe_actions(layout, context):
    layout = ui_layout(layout)
    relevant, enabled, reason = capability(context, 'probe_click')
    if not relevant:
        return
    row = layout.row()
    row.enabled = enabled
    row.operator('qcblender.click_probe', text='Click Probe · Geometry Field').role = 'GEOMETRY'
    row = layout.row()
    row.enabled = enabled and bool(context.object.get('qc_color_source'))
    row.operator('qcblender.click_probe', text='Click Probe · Bound Color Field').role = 'COLOR'
    if reason:
        layout.label(text=error_text(reason), icon='INFO')
