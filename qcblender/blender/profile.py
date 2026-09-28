"""Cursor-driven scalar line profiles with independent Blender curve views."""
import json

import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ExportHelper
import numpy as np

from ..data import load_dataset
from ..profile import export_profile_csv, sample_profile, source_positions
from ..plot_layout import DEFAULT_LAYOUT, profile_layout
from .source_browser import color_volume, read_metadata
from .views import bind, material


def profile_source(obj, role):
    if role == 'GEOMETRY':
        volume = obj.qc_settings.volume
        if volume is None or json.loads(volume['qc_field']) != json.loads(obj['qc_field']):
            raise ValueError('Geometry field volume differs from the active view')
        if volume['qc_source_sha256'] != obj['qc_source_sha256']:
            raise ValueError('Geometry field source differs from the active view')
    elif role == 'COLOR':
        if not obj.get('qc_color_source'):
            raise ValueError('Active view has no color field binding')
        volume = color_volume(obj)
        recorded = json.loads(obj['qc_color_source'])
        field = json.loads(volume['qc_field'])
        if (volume['qc_source_sha256'] != recorded['source'] or
                any(field[key] != recorded[key] for key in ('quantity', 'unit'))):
            raise ValueError('Linked color field differs from the recorded binding')
    else:
        raise ValueError('Choose the geometry or color field')
    read_metadata(volume)
    return volume, json.loads(volume['qc_field'])


def profile_curve(directory, data, location):
    arrays = data.arrays
    valid = arrays['profile_valid']
    length = float(arrays['profile_distance'][-1])
    curve = bpy.data.curves.new('QC line profile', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_resolution = 2
    curve.materials.append(material('QC line profile', (.12, .34, .78, 1)))
    obj = bpy.data.objects.new('QC line profile', curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'profile'
    for key, value in DEFAULT_LAYOUT.items():
        obj['qc_profile_' + key] = value
    obj['qc_chart'] = json.dumps({'x': 'distance along profile', 'x_unit': 'angstrom',
                                  'x_min': 0., 'x_max': length, 'y_unit': data.metadata['profile']['field']['unit'],
                                  'y_min': 0., 'y_max': 1., 'sample_count': len(valid),
                                  'valid_count': int(valid.sum())})
    layout = apply_profile_layout(obj, data)
    for axis in 'xy':
        obj['qc_profile_' + axis + '_min'], obj['qc_profile_' + axis + '_max'] = layout[axis + '_range']
    return obj


def cleanup_profile_ticks(owner):
    """Remove the generated labels before replacing or deleting a profile view."""
    for child in tuple(owner.children):
        if not child.get('qc_profile_tick'):
            continue
        text = child.data
        bpy.data.objects.remove(child, do_unlink=True)
        if text.users == 0:
            bpy.data.curves.remove(text)


def copy_profile_ticks(source, target, collection):
    """Copy saved chart labels without reopening its scientific Dataset."""
    for child in tuple(source.children):
        if not child.get('qc_profile_tick'):
            continue
        copied = child.copy()
        copied.data = child.data.copy()
        collection.objects.link(copied)
        copied.parent = target


def apply_profile_layout(obj, data):
    """Rebuild only chart geometry and tick text from the saved profile samples."""
    arrays = data.arrays
    layout = profile_layout(arrays['profile_distance'], arrays['profile_values'],
                            arrays['profile_valid'],
                            {key: obj.get('qc_profile_' + key, value)
                             for key, value in DEFAULT_LAYOUT.items()})
    curve = obj.data
    curve.splines.clear()
    curve.bevel_depth = layout['line_width']

    def add_path(points):
        spline = curve.splines.new('POLY')
        spline.points.add(len(points) - 1)
        for vertex, position in zip(spline.points, points):
            vertex.co = (*position, 1.)

    for path in layout['paths']:
        add_path(path)
    add_path(((0., 0., 0.), (layout['width'], 0., 0.)))
    add_path(((0., 0., 0.), (0., 0., layout['height'])))
    for _, x, _ in layout['x_ticks']:
        add_path(((x, 0., 0.), (x, 0., -.08)))
    for _, y, _ in layout['y_ticks']:
        add_path(((0., 0., y), (-.08, 0., y)))

    cleanup_profile_ticks(obj)

    def label(body, position, size=.14):
        text = bpy.data.curves.new('QC profile label', 'FONT')
        text.body, text.size = body, size
        text.materials.append(curve.materials[0])
        child = bpy.data.objects.new('QC profile label', text)
        bpy.context.collection.objects.link(child)
        child.parent = obj
        child.location = position
        child.rotation_euler.x = 1.5707963267948966
        child['qc_profile_tick'] = True

    for _, x, caption in layout['x_ticks']:
        label(caption, (x-.1, 0., -.28))
    for _, y, caption in layout['y_ticks']:
        label(caption, (-.62, 0., y-.06))
    label('Distance (Å)', (layout['width']/2-.5, 0., -.55))
    label(data.metadata['profile']['field']['unit'], (-.62, 0., layout['height']+.18))
    chart = json.loads(obj['qc_chart'])
    chart.update(x_min=layout['x_range'][0], x_max=layout['x_range'][1],
                 y_min=layout['y_range'][0], y_max=layout['y_range'][1])
    obj['qc_chart'] = json.dumps(chart)
    return layout


class QCBLENDER_OT_mark_profile_start(bpy.types.Operator):
    bl_idname = 'qcblender.mark_profile_start'
    bl_label = 'Mark Profile Start at 3D Cursor'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') in ('field', 'slice')

    def execute(self, context):
        obj = context.object
        try:
            read_metadata(obj)
            world = list(context.scene.cursor.location)
            if not np.isfinite(world).all():
                raise ValueError('Profile start must be finite')
            obj['qc_profile_start'] = json.dumps({'world': world,
                'dataset_sha256': obj['qc_dataset_sha256'], 'field': obj['qc_field'],
                'color_source': obj.get('qc_color_source', '')})
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_create_line_profile(bpy.types.Operator):
    bl_idname = 'qcblender.create_line_profile'
    bl_label = 'Create Line Profile to 3D Cursor'
    bl_options = {'REGISTER', 'UNDO'}

    field_role: EnumProperty(name='Sample field', items=[('GEOMETRY', 'Geometry', ''), ('COLOR', 'Color', '')], default='GEOMETRY')
    samples: IntProperty(name='Samples', default=101, min=2, max=1001)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') in ('field', 'slice')

    def invoke(self, context, event):
        try:
            profile_source(context.object, 'COLOR')
        except (ValueError, OSError, KeyError, TypeError):
            self.field_role = 'GEOMETRY'
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        try:
            profile_source(context.object, 'COLOR')
        except (ValueError, OSError, KeyError, TypeError):
            self.layout.label(text='Sample field: Geometry')
        else:
            self.layout.prop(self, 'field_role')
        self.layout.prop(self, 'samples')

    def execute(self, context):
        obj = context.object
        try:
            if 'qc_profile_start' not in obj:
                raise ValueError('Mark a profile start on this view first')
            marked = json.loads(obj['qc_profile_start'])
            if (marked['dataset_sha256'] != obj['qc_dataset_sha256'] or marked['field'] != obj['qc_field'] or
                    marked['color_source'] != obj.get('qc_color_source', '')):
                raise ValueError('Active field binding changed after marking the profile start')
            read_metadata(obj)
            volume, field = profile_source(obj, self.field_role)
            world_end = list(context.scene.cursor.location)
            local = source_positions(marked['world'], world_end, volume.matrix_world)
            directory = bpy.path.abspath(volume['qc_dataset'])
            source = load_dataset(directory)
            data = sample_profile(source, field, local[0], local[1], marked['world'], world_end,
                                  volume['qc_dataset_sha256'], self.field_role, self.samples)
            from .external_results import store_analysis
            output = store_analysis(data)
            location = obj.matrix_world.translation.copy()
            location.x += 3
            chart = profile_curve(output, data, location)
            for selected in context.selected_objects:
                selected.select_set(False)
            chart.select_set(True)
            context.view_layer.objects.active = chart
        except (ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_export_line_profile(bpy.types.Operator, ExportHelper):
    bl_idname = 'qcblender.export_line_profile'
    bl_label = 'Export Line Profile CSV'
    filename_ext = '.csv'
    filter_glob: StringProperty(default='*.csv', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'profile'

    def execute(self, context):
        try:
            read_metadata(context.object)
            data = load_dataset(bpy.path.abspath(context.object['qc_dataset']))
            export_profile_csv(data, self.filepath)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}
