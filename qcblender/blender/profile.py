"""Cursor-driven scalar line profiles with independent Blender curve views."""
import json

import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ExportHelper
import numpy as np

from ..data import load_dataset
from ..profile import export_profile_csv, sample_profile, source_positions, valid_runs
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
    values = arrays['profile_values'][valid]
    low, high = float(values.min()), float(values.max())
    span = high - low or 1.
    length = float(arrays['profile_distance'][-1])
    curve = bpy.data.curves.new('QC line profile', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = .02
    curve.bevel_resolution = 2
    for start, stop in valid_runs(valid):
        spline = curve.splines.new('POLY')
        spline.points.add(stop - start - 1)
        for point, distance, value in zip(spline.points, arrays['profile_distance'][start:stop],
                                          arrays['profile_values'][start:stop]):
            point.co = (4 * float(distance) / length, 0, 3 * (float(value) - low) / span, 1)
    curve.materials.append(material('QC line profile', (.12, .34, .78, 1)))
    obj = bpy.data.objects.new('QC line profile', curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'profile'
    obj['qc_chart'] = json.dumps({'x': 'distance along profile', 'x_unit': 'angstrom',
                                  'x_min': 0., 'x_max': length, 'y_unit': data.metadata['profile']['field']['unit'],
                                  'y_min': low, 'y_max': high, 'sample_count': len(valid),
                                  'valid_count': int(valid.sum())})
    return obj


class QCBLENDER_OT_mark_profile_start(bpy.types.Operator):
    bl_idname = 'qcblender.mark_profile_start'
    bl_label = 'Mark Profile Start at 3D Cursor'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'profile_start')

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
        from .capabilities import poll_action
        return poll_action(cls, context, 'profile')

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
