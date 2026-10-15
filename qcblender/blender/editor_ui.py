"""Workflow actions in the sidebar; persistent controls in native Properties."""
from ..i18n import error_text, iface, tip, ui_layout
import json
import textwrap

import bpy
from bpy.props import EnumProperty

from .capabilities import action_button, capability, record
from .source_browser import cached_metadata


def is_qc(context):
    obj = context.object
    return obj is not None and bool(obj.get('qc_view_kind') or obj.get('qc_dataset'))


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
            'OBJECT': 'Open Object Properties for the active object and pin that object in the existing Properties Editor',
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
            area.spaces.active.pin_id = context.object
            area.spaces.active.use_pin_id = True
        area.spaces.active.context = self.editor
        area.tag_redraw()
        return {'FINISHED'}


class QCBLENDER_PT_main(bpy.types.Panel):
    bl_label = 'Workflow'
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
        if capability(context, 'generate')[0]:
            calculation = layout.box()
            calculation.label(text='Compute')
            action_button(calculation, context, 'generate', 'qcblender.generate_field', 'Generate Quantum Field', 'VOLUME_DATA')
        if is_qc(context):
            layout.operator('qcblender.open_properties', text='Object Properties and Display Parameters', icon='PROPERTIES').editor = 'OBJECT'


class QCBLENDER_PT_dataset(bpy.types.Panel):
    bl_label = 'Dataset and Numerical Summary'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        layout = ui_layout(self.layout)
        summary(layout, context.object)
        layout.operator('qcblender.source_details', text='View Full Source', icon='INFO')
        layout.operator('qcblender.refresh_sources', text='Refresh Sources', icon='FILE_REFRESH')


class QCBLENDER_PT_create(bpy.types.Panel):
    bl_label = 'Create Views and Inspection Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        layout, obj = ui_layout(self.layout), context.object
        views = layout.box()
        views.label(text='Display Views')
        for action, operator, text in [
            ('surface', 'qcblender.add_surface_layer', 'Create Isosurface Layer'),
            ('fog', 'qcblender.create_fog', 'Create Volume Fog'),
        ]:
            action_button(views, context, action, operator, text)
        if obj.get('qc_view_kind') == 'atoms':
            views.operator('qcblender.local_selection_layer', text='Create Local Display Layer')
            if obj.get('qc_optimization_available') and not obj.get('qc_optimization_step'):
                views.operator('qcblender.optimization_view', text='Create Optimization Trajectory View')
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
        if obj.get('qc_view_kind') == 'atoms':
            measurements = layout.box()
            measurements.label(text='Atom and Geometry Annotations')
            buttons = measurements.grid_flow(columns=2, even_columns=True, align=True)
            for kind, title in [('ATOM', 'Atom numbers'), ('DISTANCE', 'Distance'),
                                ('ANGLE', 'Angle'), ('DIHEDRAL', 'Dihedral')]:
                buttons.operator('qcblender.add_annotation', text=title).kind = kind
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
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_dataset'))

    def draw(self, context):
        layout = ui_layout(self.layout)
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
    bl_label = 'Project and Diagnostics'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 5

    def draw(self, context):
        layout = ui_layout(self.layout)
        saving = layout.box()
        saving.label(text='Save and Export')
        for operator, text in [('save_project', 'Save Self-Contained Project'), ('archive_project', 'Archive Project')]:
            saving.operator('qcblender.' + operator, text=text)
        obj = context.object
        if obj is not None:
            from .source_browser import source_object
            from .data_export import export_choices
            if source_object(obj).get('qc_dataset') and export_choices(None, context):
                saving.operator('qcblender.export_data', text='Export Data and Parameter Summary', icon='EXPORT')
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
