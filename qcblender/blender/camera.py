"""Create a new orthographic camera around selected QC display views."""

import bpy
from bpy.props import FloatProperty
from mathutils import Vector
import numpy as np

from ..framing import fit_orthographic


_DISPLAY_KINDS = {'atoms', 'field', 'slice', 'fog', 'dipole', 'spectrum',
                  'scatter', 'nbo', 'analysis', 'profile'}


def _render_collection_enabled(obj, layer_collection):
    if layer_collection.exclude or layer_collection.collection.hide_render:
        return False
    if layer_collection.collection in obj.users_collection:
        return True
    return any(_render_collection_enabled(obj, child) for child in layer_collection.children)


def _renderable(obj, context):
    return (obj.name in context.scene.objects and not obj.get('qc_data_record') and not obj.hide_render
            and _render_collection_enabled(obj, context.view_layer.layer_collection))


def _corners(obj, matrix):
    return [tuple(matrix @ Vector(corner)) for corner in obj.bound_box]


def _has_bounds(obj):
    bounds = obj.bound_box
    return (len(bounds) == 8 and
            (len(getattr(obj.data, 'vertices', ())) > 0 or
             any(max(axis) > min(axis) for axis in zip(*bounds))))


def _view_points(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    points = []
    # Geometry Nodes can yield mesh/curve points, a volume, or instances.
    if _has_bounds(evaluated):
        points.extend(_corners(evaluated, evaluated.matrix_world))
    for instance in depsgraph.object_instances:
        if (instance.is_instance and instance.parent and instance.parent.original == obj
                and _has_bounds(instance.object)):
            points.extend(_corners(instance.object, instance.matrix_world))
    if not points and obj.get('qc_view_kind') == 'fog':
        source = obj.qc_settings.volume
        if source is not None:
            volume = source.evaluated_get(depsgraph)
            if volume.type == 'VOLUME' and _has_bounds(volume):
                points.extend(_corners(volume, volume.matrix_world))
    if not points:
        raise ValueError(f'{obj.name}: evaluated QC display has no geometry or volume bounds')
    return points


class QCBLENDER_OT_create_framed_camera(bpy.types.Operator):
    bl_idname = 'qcblender.create_framed_camera'
    bl_label = 'Create Framed QC Camera'
    bl_options = {'REGISTER', 'UNDO'}

    margin: FloatProperty(name='Margin per side', default=0.05, min=0.0, max=0.49,
                          subtype='FACTOR')

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def execute(self, context):
        try:
            space = context.space_data
            view = context.region_data or space.region_3d
            if view is None:
                raise ValueError('A VIEW_3D viewing direction is required')
            selected = [obj for obj in context.selected_objects
                        if obj.get('qc_view_kind') in _DISPLAY_KINDS and _renderable(obj, context)]
            if not selected and context.view_layer.objects.active is not None:
                active = context.view_layer.objects.active
                if active.get('qc_view_kind') in _DISPLAY_KINDS and _renderable(active, context):
                    selected = [active]
            if not selected:
                raise ValueError('Select a renderable QC display view')
            for obj in selected:
                for modifier in obj.modifiers:
                    if modifier.show_viewport != modifier.show_render:
                        raise ValueError(f'{obj.name}: modifier {modifier.name} has different viewport/render visibility; match both before framing')
            render = context.scene.render
            aspect = (render.resolution_x * render.pixel_aspect_x /
                      (render.resolution_y * render.pixel_aspect_y))
            rotation = view.view_rotation.copy()
            axes = rotation.to_matrix()
            basis = np.array([tuple(axes.col[index]) for index in range(3)])
            depsgraph = context.evaluated_depsgraph_get()
            points = [point for obj in selected for point in _view_points(obj, depsgraph)]
            location, scale, clip_end = fit_orthographic(points, basis, aspect, self.margin)
        except (ValueError, ZeroDivisionError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

        camera_data = bpy.data.cameras.new('QC Framed Camera')
        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = scale
        camera_data.clip_end = clip_end
        camera = bpy.data.objects.new('QC Framed Camera', camera_data)
        camera['qc_camera'] = True
        camera.location = location.tolist()
        camera.rotation_mode = 'QUATERNION'
        camera.rotation_quaternion = rotation
        context.scene.collection.objects.link(camera)
        context.scene.camera = camera
        return {'FINISHED'}
