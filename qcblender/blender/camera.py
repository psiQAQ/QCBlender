"""Create a new orthographic camera around selected QC display views."""
from ..i18n import error_text
from .viewport_context import target_object, viewport_context

import bpy
from bpy.props import EnumProperty, FloatProperty
from mathutils import Matrix, Vector
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


def selected_views(context):
    if context.area.type == 'PROPERTIES':
        target = target_object(context)
        selected = [target] if (target is not None and target.get('qc_view_kind') in _DISPLAY_KINDS
                                and _renderable(target, context)) else []
    else:
        selected = [obj for obj in context.selected_objects
                    if obj.get('qc_view_kind') in _DISPLAY_KINDS and _renderable(obj, context)]
    if context.area.type == 'VIEW_3D' and not selected and context.view_layer.objects.active is not None:
        active = context.view_layer.objects.active
        if active.get('qc_view_kind') in _DISPLAY_KINDS and _renderable(active, context):
            selected = [active]
    if not selected:
        raise ValueError('Select a renderable QC display view')
    for obj in selected:
        for modifier in obj.modifiers:
            if modifier.show_viewport != modifier.show_render:
                raise ValueError(f'{obj.name}: modifier {modifier.name} has different viewport/render visibility; match both before framing')
    return selected


def _mesh_points(evaluated, matrix, limit=65536):
    mesh = evaluated.to_mesh()
    if mesh is None:
        return np.empty((0, 3))
    try:
        values = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
        mesh.vertices.foreach_get('co', values)
        values = values.reshape((-1, 3))
        if len(values) > limit:
            values = values[np.linspace(0, len(values) - 1, limit, dtype=int)]
        transform = np.asarray(matrix, dtype=np.float64)
        return values @ transform[:3, :3].T + transform[:3, 3]
    finally:
        evaluated.to_mesh_clear()


def subject_points(context, objects):
    """Sample evaluated world geometry with the complete scalar legend disabled on copies."""
    from .node_identity import socket_name
    arrays = []
    for obj in objects:
        if obj.get('qc_view_kind') in {'fog', 'spectrum', 'scatter', 'profile'}:
            continue
        duplicate = obj.copy()
        temporary_groups = []
        try:
            duplicate.hide_render = True
            duplicate.hide_viewport = False
            for modifier in duplicate.modifiers:
                if modifier.type == 'NODES' and modifier.node_group:
                    if any(node.get('qc_mayer_part') == 'bonds' for node in modifier.node_group.nodes):
                        modifier.node_group = modifier.node_group.copy()
                        temporary_groups.append(modifier.node_group)
                        for node in modifier.node_group.nodes:
                            if node.get('qc_mayer_part') == 'bonds':
                                from .node_identity import node_socket
                                node_socket(node.inputs, 'Show Legend').default_value = False
                    for item in modifier.node_group.interface.items_tree:
                        if (item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                                and socket_name(item, modifier.node_group) == 'Show Legend'):
                            modifier[item.identifier] = False
            context.scene.collection.objects.link(duplicate)
            duplicate.hide_set(False)
            duplicate.update_tag()
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            arrays.append(_mesh_points(duplicate.evaluated_get(depsgraph), duplicate.matrix_world))
            for instance in depsgraph.object_instances:
                if instance.is_instance and instance.parent and instance.parent.original == duplicate:
                    if instance.object.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
                        arrays.append(_mesh_points(instance.object, instance.matrix_world))
        finally:
            bpy.data.objects.remove(duplicate, do_unlink=True)
            for tree in temporary_groups:
                bpy.data.node_groups.remove(tree)
    context.view_layer.update()
    arrays = [array for array in arrays if len(array)]
    return np.concatenate(arrays) if arrays else np.empty((0, 3))


def framing_inputs(context, direction, aspect):
    view = viewport_context(context).view
    selected = selected_views(context)
    rotation = view.view_rotation.copy()
    axes = rotation.to_matrix()
    basis = np.array([tuple(axes.col[index]) for index in range(3)])
    depsgraph = context.evaluated_depsgraph_get()
    points = [point for obj in selected for point in _view_points(obj, depsgraph)]
    for obj in selected:
        for child in obj.children_recursive:
            if child.get('qc_annotation') and _renderable(child, context):
                points.extend(_view_points(child, depsgraph))
    subject = subject_points(context, selected) if direction != 'CURRENT' else np.empty((0, 3))
    message = ''
    if direction != 'CURRENT':
        if any(obj.get('qc_view_kind') in {'spectrum', 'scatter', 'profile'} for obj in selected) or not len(subject):
            message = 'Automatic direction is unavailable for this display; the current viewing direction was used'
        else:
            from ..viewpoint import choose_orientation
            result = choose_orientation(subject, mode=direction, reference_basis=basis, aspect=aspect)
            basis = result.basis
            rotation = Matrix(basis.T.tolist()).to_quaternion()
            message = result.message
    return points, subject, basis, rotation, message


def configure_camera(scene, location, scale, clip_end, rotation, camera=None):
    if camera is None:
        camera_data = bpy.data.cameras.new('QC Framed Camera')
        camera = bpy.data.objects.new('QC Framed Camera', camera_data)
        camera['qc_camera'] = True
        scene.collection.objects.link(camera)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    camera.data.clip_end = clip_end
    camera.location = location.tolist()
    camera.rotation_mode = 'QUATERNION'
    camera.rotation_quaternion = rotation
    scene.camera = camera
    return camera


class QCBLENDER_OT_create_framed_camera(bpy.types.Operator):
    bl_idname = 'qcblender.create_framed_camera'
    bl_label = 'Create Framed QC Camera'
    bl_description = 'Create an orthographic scene camera framing the selected renderable QC views from the current 3D viewing direction, with the chosen margin; the active view is used when no selected view qualifies'
    bl_options = {'REGISTER', 'UNDO'}

    margin: FloatProperty(name='Margin per side', default=0.05, min=0.0, max=0.49,
                          subtype='FACTOR')
    direction: EnumProperty(name='Viewing direction', default='CURRENT', items=[
        ('CURRENT', 'Current View', 'Keep the current 3D viewing direction'),
        ('PCA', 'Principal Axes', 'Show the widest principal plane of the displayed geometry'),
        ('UNOBSTRUCTED', 'Reduce Overlap', 'Search a bounded set of directions to reduce projected overlap; transparency and fog are not modeled'),
    ])

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        from ..i18n import ui_layout
        layout = ui_layout(self.layout)
        layout.prop(self, 'direction')
        layout.prop(self, 'margin')

    @classmethod
    def description(cls, context, properties):
        from ..i18n import tip
        if getattr(getattr(context, 'area', None), 'type', None) == 'PROPERTIES':
            return tip('Frame the Properties object with an orthographic camera using the largest 3D View in the same window; other selected objects are excluded')
        return tip(cls.bl_description)

    @classmethod
    def poll(cls, context):
        try:
            viewport_context(context)
        except (ValueError, ReferenceError) as error:
            cls.poll_message_set(error_text(error))
            return False
        if context.area.type == 'PROPERTIES' and target_object(context) is None:
            cls.poll_message_set(error_text('Select or pin an Object in Object Properties'))
            return False
        return True

    def execute(self, context):
        try:
            view = viewport_context(context).view
            if context.area.type == 'PROPERTIES':
                target = target_object(context)
                selected = [target] if (target is not None and target.get('qc_view_kind') in _DISPLAY_KINDS
                                        and _renderable(target, context)) else []
            else:
                selected = [obj for obj in context.selected_objects
                            if obj.get('qc_view_kind') in _DISPLAY_KINDS and _renderable(obj, context)]
            if context.area.type == 'VIEW_3D' and not selected and context.view_layer.objects.active is not None:
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
            message = ''
            if getattr(self, 'direction', 'CURRENT') != 'CURRENT':
                points, _, basis, rotation, message = framing_inputs(context, self.direction, aspect)
            location, scale, clip_end = fit_orthographic(points, basis, aspect, self.margin)
        except (ValueError, ZeroDivisionError, TypeError, ReferenceError) as error:
            self.report({'ERROR'}, error_text(error))
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
        if message:
            self.report({'INFO'}, error_text(message))
        return {'FINISHED'}
