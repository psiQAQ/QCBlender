"""Explicit, undoable output setup using native scene settings as the authority."""
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty

from ..framing import fit_orthographic
from ..i18n import error_text, ui_layout
from .camera import (QCBLENDER_OT_create_framed_camera, configure_camera,
                     framing_inputs, selected_views, subject_points)
from .output_settings import apply_output, restore_output, validate_output


class QCBLENDER_OT_apply_output(bpy.types.Operator):
    bl_idname = 'qcblender.apply_output'
    bl_label = 'Apply QC Output'
    bl_description = 'Frame the selected QC views and apply reversible scene lighting, color management and PNG output settings'
    bl_options = {'REGISTER', 'UNDO'}

    direction: EnumProperty(name='Viewing direction', default='PCA', items=[
        ('CURRENT', 'Current View', 'Keep the current 3D viewing direction'),
        ('PCA', 'Principal Axes', 'Show the widest principal plane of the displayed geometry'),
        ('UNOBSTRUCTED', 'Reduce Overlap', 'Search a bounded set of directions to reduce projected overlap; transparency and fog are not modeled'),
    ])
    margin: FloatProperty(name='Margin per side', default=.05, min=0., max=.49, subtype='FACTOR')
    quality: EnumProperty(name='Output quality', default='STANDARD', items=[
        ('PREVIEW', 'Preview (EEVEE, 64 samples)', 'Fast output using EEVEE'),
        ('STANDARD', 'Standard (Cycles, 128 samples)', 'Cycles with adaptive threshold 0.02'),
        ('HIGH', 'High (Cycles, 512 samples)', 'Cycles with adaptive threshold 0.005'),
    ])
    background: EnumProperty(name='Background', default='WHITE', items=[
        ('WHITE', 'White', 'White image background'),
        ('BLACK', 'Black', 'Black image background'),
        ('TRANSPARENT', 'Transparent PNG', 'RGBA PNG with transparent film'),
        ('CUSTOM', 'Custom Color', 'Choose the visible background color'),
    ])
    background_color: FloatVectorProperty(name='Background color', subtype='COLOR', size=3,
                                          default=(1., 1., 1.), min=0., max=1.)
    resolution_x: IntProperty(name='Width', default=1920, min=4, max=65536)
    resolution_y: IntProperty(name='Height', default=1080, min=4, max=65536)
    resolution_percentage: IntProperty(name='Resolution percentage', default=100, min=1, max=100,
                                       subtype='PERCENTAGE')
    denoise: BoolProperty(name='Denoise', default=True,
                          description='Use OpenImageDenoise for Cycles; disable it to inspect fine details')

    @classmethod
    def poll(cls, context):
        return QCBLENDER_OT_create_framed_camera.poll(context)

    def invoke(self, context, event):
        render = context.scene.render
        self.resolution_x = render.resolution_x
        self.resolution_y = render.resolution_y
        self.resolution_percentage = render.resolution_percentage
        return context.window_manager.invoke_props_dialog(self, width=440)

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.prop(self, 'direction')
        if self.direction == 'UNOBSTRUCTED':
            layout.label(text='Overlap is approximate; transparent surfaces and fog are excluded', icon='INFO')
        layout.prop(self, 'margin')
        layout.prop(self, 'quality')
        if self.quality != 'PREVIEW':
            layout.prop(self, 'denoise')
        row = layout.row(align=True)
        row.prop(self, 'resolution_x')
        row.prop(self, 'resolution_y')
        layout.prop(self, 'resolution_percentage')
        layout.prop(self, 'background')
        if self.background == 'CUSTOM':
            layout.prop(self, 'background_color')
        layout.label(text='Original scene settings are saved until Restore Original Output', icon='INFO')

    def execute(self, context):
        scene = context.scene
        options = {name: getattr(self, name) for name in ('quality', 'background', 'background_color',
                   'resolution_x', 'resolution_y', 'resolution_percentage', 'denoise')}
        camera = scene.qc_output.camera
        previous_camera = scene.camera
        previous = None
        created = False
        try:
            validate_output(scene, **options)
            if camera is not None:
                if camera.type != 'CAMERA' or camera.name not in scene.objects:
                    raise ValueError('The QC output camera is missing from this scene; restore the original output first')
                if camera.data.users > 1 or any(camera.name in other.objects for other in bpy.data.scenes if other != scene):
                    raise ValueError('The QC output camera is shared; make it single-user before applying output')
                previous = (camera.matrix_world.copy(), camera.rotation_mode, camera.data.type,
                            camera.data.ortho_scale, camera.data.clip_end)
            aspect = self.resolution_x * scene.render.pixel_aspect_x / (self.resolution_y * scene.render.pixel_aspect_y)
            points, subject, basis, rotation, message = framing_inputs(context, self.direction, aspect)
            if not len(subject):
                subject = subject_points(context, selected_views(context))
            if not len(subject):
                subject = points
            location, scale, clip_end = fit_orthographic(points, basis, aspect, self.margin)
            created = camera is None
            camera = configure_camera(scene, location, scale, clip_end, rotation, camera)
            context.view_layer.update()
            result = apply_output(scene, camera, subject, original_camera=previous_camera, **options)
            scene.qc_output.camera = camera
            context.view_layer.update()
        except (ValueError, TypeError, RuntimeError, ReferenceError, AttributeError) as error:
            if camera is not None and created:
                data = camera.data
                bpy.data.objects.remove(camera, do_unlink=True)
                if data.users == 0:
                    bpy.data.cameras.remove(data)
            elif camera is not None and previous is not None:
                camera.rotation_mode = previous[1]
                camera.matrix_world = previous[0]
                camera.data.type, camera.data.ortho_scale, camera.data.clip_end = previous[2:]
            scene.camera = previous_camera
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        if message:
            self.report({'INFO'}, error_text(message))
        for warning in result.get('warnings', []):
            self.report({'WARNING'}, error_text(warning))
        self.report({'INFO'}, error_text('QC output settings applied'))
        return {'FINISHED'}


class QCBLENDER_OT_restore_output(bpy.types.Operator):
    bl_idname = 'qcblender.restore_output'
    bl_label = 'Restore Original Output'
    bl_description = 'Restore the camera, world, light visibility and output settings saved before the first QC output application'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.qc_output.active

    def execute(self, context):
        try:
            restore_output(context.scene)
        except (ValueError, TypeError, RuntimeError, ReferenceError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        self.report({'INFO'}, error_text('Original output settings restored'))
        return {'FINISHED'}


class QCBLENDER_PT_output(bpy.types.Panel):
    bl_label = 'QC Output'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        layout = ui_layout(self.layout)
        layout.operator('qcblender.apply_output', icon='RENDER_STILL')
        layout.operator('qcblender.restore_output', icon='LOOP_BACK')
        if context.scene.qc_output.active:
            layout.label(text='QC output is active; native scene settings remain editable', icon='INFO')
