"""Viewport probe and native slice controls; scientific arrays remain source data."""
import json

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector
import numpy as np

from ..data import load_dataset
from ..planes import plane_frame
from ..profile import source_positions
from ..sampling import sample_point
from .graph import view_modifier
from .profile import profile_source
from .source_browser import bound_field, mapped_field, read_metadata


def slice_controls(obj):
    if obj is None or obj.get('qc_view_kind') != 'slice':
        raise ValueError('Choose an active QC scalar slice')
    modifier = view_modifier(obj)
    sockets = {item.name: item.identifier for item in modifier.node_group.interface.items_tree
               if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    if any(name not in sockets or sockets[name] not in modifier for name in ('Center', 'Rotation', 'Width', 'Height')):
        raise ValueError('Slice controls are missing from the QC modifier')
    return modifier, sockets


def _plane_record(obj):
    try:
        record = json.loads(obj.get('qc_plane_definition', '{}'))
        return record if isinstance(record, dict) else {}
    except (ValueError, TypeError):
        return {}


def _control_value(obj, name):
    modifier, sockets = slice_controls(obj)
    return modifier[sockets[name]]


def _set_control(obj, name, value):
    modifier, sockets = slice_controls(obj)
    modifier[sockets[name]] = value
    if name in ('Center', 'Rotation') and _plane_record(obj).get('mode') != 'FREE':
        obj['qc_plane_definition'] = json.dumps({'mode': 'FREE'})
    obj.update_tag()


class QCBLENDER_GGT_slice(bpy.types.GizmoGroup):
    bl_idname = 'QCBLENDER_GGT_slice'
    bl_label = 'QC Slice Controls'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @classmethod
    def poll(cls, context):
        try:
            slice_controls(context.object)
            return True
        except ValueError:
            return False

    def setup(self, context):
        move = self.gizmos.new('GIZMO_GT_move_3d')
        move.target_set_handler('offset',
            get=lambda: tuple(context.object.matrix_world @ Vector(_control_value(context.object, 'Center'))),
            set=lambda value: _set_control(context.object, 'Center',
                                           tuple(context.object.matrix_world.inverted() @ Vector(value))))
        move.scale_basis = .18
        move.color, move.alpha = (.9, .9, .9), .7
        self._move = move
        self._sizes = []
        for name, axis, color in (('Width', 0, (.9, .25, .2)), ('Height', 1, (.2, .6, 1.))):
            gizmo = self.gizmos.new('GIZMO_GT_arrow_3d')
            def get_size(name=name, axis=axis):
                obj = context.object
                from mathutils import Euler
                direction = Euler(_control_value(obj, 'Rotation')).to_matrix().col[axis]
                return float(_control_value(obj, name)) * (obj.matrix_world.to_3x3() @ direction).length / 2
            def set_size(value, name=name, axis=axis):
                from mathutils import Euler
                obj = context.object
                direction = Euler(_control_value(obj, 'Rotation')).to_matrix().col[axis]
                scale = (obj.matrix_world.to_3x3() @ direction).length
                if scale > 1e-12:
                    _set_control(obj, name, max(.001, 2 * abs(value) / scale))
            gizmo.target_set_handler('offset', get=get_size, set=set_size)
            gizmo.color, gizmo.alpha = color, .7
            gizmo.scale_basis = .6
            self._sizes.append((gizmo, axis))
        self._rotations = []
        for axis, color in enumerate(((1., .4, .4), (.4, 1., .4), (.4, .4, 1.))):
            gizmo = self.gizmos.new('GIZMO_GT_dial_3d')
            def set_angle(value, axis=axis):
                obj = context.object
                angles = list(_control_value(obj, 'Rotation'))
                angles[axis] = float(value)
                _set_control(obj, 'Rotation', tuple(angles))
            gizmo.target_set_handler('offset',
                get=lambda axis=axis: float(_control_value(context.object, 'Rotation')[axis]),
                set=set_angle)
            gizmo.color, gizmo.alpha = color, .5
            gizmo.scale_basis = .55 + axis * .12
            self._rotations.append((gizmo, axis))

    def refresh(self, context):
        self.draw_prepare(context)

    def draw_prepare(self, context):
        from mathutils import Euler
        obj = context.object
        try:
            center = obj.matrix_world @ Vector(_control_value(obj, 'Center'))
            local = Euler(_control_value(obj, 'Rotation')).to_matrix()
            world = obj.matrix_world.to_3x3() @ local
            axes = [world.col[i].normalized() for i in range(3)]
            self._move.matrix_basis = Matrix.Identity(4)
            for gizmo, axis in self._sizes:
                gizmo.matrix_basis = Matrix.Translation(center) @ axes[axis].to_track_quat('Z', 'Y').to_matrix().to_4x4()
            for gizmo, axis in self._rotations:
                gizmo.matrix_basis = Matrix.Translation(center) @ axes[axis].to_track_quat('Z', 'Y').to_matrix().to_4x4()
        except (ValueError, KeyError):
            return


class QCBLENDER_OT_define_plane(bpy.types.Operator):
    bl_idname = 'qcblender.define_slice_plane'
    bl_label = 'Define QC Slice Plane'
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(name='Plane', items=[('FREE', 'Free', ''), ('ij', 'Grid ij', ''),
                                                 ('jk', 'Grid jk', ''), ('ki', 'Grid ki', ''),
                                                 ('atoms', 'Three source atoms', '')], default='ij')
    position: FloatProperty(name='Grid position', default=.5, min=0, max=1)
    atom_1: IntProperty(name='First source atom', default=1, min=1)
    atom_2: IntProperty(name='Second source atom', default=2, min=1)
    atom_3: IntProperty(name='Third source atom', default=3, min=1)
    configuration: PointerProperty(name='Associated atom view', type=bpy.types.Object)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'slice'

    def invoke(self, context, event):
        record = _plane_record(context.object)
        self.mode = record.get('mode', 'ij')
        self.position = record.get('position', .5)
        numbers = record.get('source_numbers', [1, 2, 3])
        if len(numbers) == 3:
            self.atom_1, self.atom_2, self.atom_3 = numbers
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'mode')
        if self.mode in ('ij', 'jk', 'ki'):
            self.layout.prop(self, 'position')
        elif self.mode == 'atoms':
            self.layout.prop(self, 'configuration')
            for name in ('atom_1', 'atom_2', 'atom_3'):
                self.layout.prop(self, name)

    def execute(self, context):
        obj = context.object
        try:
            modifier, sockets = slice_controls(obj)
            if self.mode == 'FREE':
                obj['qc_plane_definition'] = json.dumps({'mode': 'FREE'})
                return {'FINISHED'}
            volume, field, _, _ = bound_field(obj)
            source_to_view = obj.matrix_world.inverted() @ volume.matrix_world
            atoms = numbers = atom_to_view = None
            if self.mode == 'atoms':
                atom_view = self.configuration
                if atom_view is None or atom_view.get('qc_view_kind') != 'atoms':
                    raise ValueError('Choose an associated atom view')
                read_metadata(atom_view)
                same_calculation = (atom_view.get('qc_source_sha256') == obj.get('qc_source_sha256')
                                    and atom_view.get('qc_source_job', -1) == obj.get('qc_source_job', -1))
                if not same_calculation:
                    try:
                        record = json.loads(atom_view.get('qc_association', '{}'))
                    except (ValueError, TypeError):
                        record = {}
                    if ({record.get('reference_source'), record.get('moving_source')}
                            != {atom_view.get('qc_source_sha256'), obj.get('qc_source_sha256')}
                            or record.get('status') != 'geometry_matched'):
                        raise ValueError('Atom view has no verified association with this field')
                data = load_dataset(bpy.path.abspath(atom_view['qc_dataset']))
                atoms = data.arrays['positions']
                if atom_view.get('qc_source_sha256') != data.metadata['source']['sha256']:
                    raise ValueError('Atom view source differs from its saved dataset')
                if not same_calculation and record.get('atom_mapping') != list(range(len(atoms))):
                    raise ValueError('Associated atom order is not identical to source numbering')
                numbers = (self.atom_1, self.atom_2, self.atom_3)
                atom_to_view = obj.matrix_world.inverted() @ atom_view.matrix_world
            center, axes, width, height = plane_frame(field, self.mode, np.asarray(source_to_view),
                                                       self.position, atoms, numbers,
                                                       None if atom_to_view is None else np.asarray(atom_to_view))
            rotation = Matrix(axes.tolist()).to_euler('XYZ')
            for name, value in (('Center', center), ('Rotation', rotation), ('Width', width), ('Height', height)):
                modifier[sockets[name]] = tuple(float(v) for v in value) if name in ('Center', 'Rotation') else float(value)
            obj['qc_plane_definition'] = json.dumps({'mode': self.mode, 'position': self.position,
                                                       'source_numbers': numbers, 'configuration': self.configuration.name if self.mode == 'atoms' else ''})
            obj.update_tag()
        except (ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def _probe_draw(operator):
    font = __import__('blf')
    font.position(0, 28, 46, 0)
    font.size(0, 15)
    font.draw(0, operator._hud)


class QCBLENDER_OT_click_probe(bpy.types.Operator):
    bl_idname = 'qcblender.click_probe'
    bl_label = 'Probe Active QC Surface'
    bl_options = {'REGISTER', 'UNDO'}
    role: EnumProperty(name='Field', items=[('GEOMETRY', 'Geometry', ''), ('COLOR', 'Bound color', '')], default='GEOMETRY')

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D' and
                context.object is not None and context.object.get('qc_view_kind') in ('field', 'slice'))

    def invoke(self, context, event):
        try:
            bound_field(context.object)
            if self.role == 'COLOR':
                mapped_field(context.object)
            self._target = context.object
            self._source, self._field = profile_source(self._target, self.role)
            self._data = load_dataset(bpy.path.abspath(self._source['qc_dataset']))
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self._hud = 'QC probe: click active surface; Esc cancels'
        self._handle = bpy.types.SpaceView3D.draw_handler_add(_probe_draw, (self,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self.modal(context, event)
        return {'RUNNING_MODAL'}

    def _close(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.area.tag_redraw()

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._close(context)
            return {'CANCELLED'}
        if event.type != 'LEFTMOUSE' or event.value != 'PRESS':
            return {'RUNNING_MODAL'}
        try:
            if context.object != self._target or self._target.hide_get():
                raise ValueError('Active surface changed or is hidden')
            bound_field(self._target)
            if self.role == 'COLOR':
                mapped_field(self._target)
            source, field = profile_source(self._target, self.role)
            if source != self._source or field != self._field:
                raise ValueError('Field binding changed during probe')
            region, view = context.region, context.region_data
            coord = (event.mouse_region_x, event.mouse_region_y)
            origin = view3d_utils.region_2d_to_origin_3d(region, view, coord)
            direction = view3d_utils.region_2d_to_vector_3d(region, view, coord)
            evaluated = self._target.evaluated_get(context.evaluated_depsgraph_get())
            inverse = evaluated.matrix_world.inverted()
            hit, local, _, _ = evaluated.ray_cast(inverse @ origin, (inverse.to_3x3() @ direction).normalized())
            if not hit:
                self._hud = 'QC probe: no hit on active surface'
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            world = evaluated.matrix_world @ local
            position = source_positions(world, world, self._source.matrix_world)[0]
            value = sample_point(self._data.arrays[field['array']], self._data.arrays[field['valid_mask']], field, position)
            record = {'value': value, 'unit': field['unit'], 'quantity': field['quantity'],
                      'field_role': self.role, 'source_position_angstrom': position.tolist(),
                      'world_position': list(world), 'interpolation': 'trilinear',
                      'source_sha256': self._source['qc_source_sha256']}
            self._target['qc_probe'] = json.dumps(record)
            self._close(context)
            self.report({'INFO'}, f"{field['quantity']}: {value:.8g} {field['unit']}")
            return {'FINISHED'}
        except ValueError as error:
            state = 'outside field' if 'outside the field domain' in str(error) else 'invalid'
            self._hud = 'QC probe ' + state + ': ' + str(error)
        except (OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self._hud = 'QC probe invalid: ' + str(error)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


class QCBLENDER_WST_probe(bpy.types.WorkSpaceTool):
    bl_idname = 'qcblender.probe_tool'
    bl_label = 'QC Surface Probe'
    bl_description = 'Click the active QC surface or slice to sample its geometry field'
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_icon = 'ops.generic.select'
    bl_keymap = (('qcblender.click_probe', {'type': 'LEFTMOUSE', 'value': 'PRESS'}, {}),)


class QCBLENDER_WST_slice(bpy.types.WorkSpaceTool):
    bl_idname = 'qcblender.slice_tool'
    bl_label = 'QC Slice Gizmo'
    bl_description = 'Move, rotate or resize the active QC slice'
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_icon = 'ops.transform.translate'
    bl_widget = QCBLENDER_GGT_slice.bl_idname


def register_tool():
    bpy.utils.register_class(QCBLENDER_GGT_slice)
    bpy.utils.register_tool(QCBLENDER_WST_probe, after={'builtin.cursor'}, separator=True)
    bpy.utils.register_tool(QCBLENDER_WST_slice, after={QCBLENDER_WST_probe.bl_idname})


def unregister_tool():
    bpy.utils.unregister_tool(QCBLENDER_WST_slice)
    bpy.utils.unregister_tool(QCBLENDER_WST_probe)
    bpy.utils.unregister_class(QCBLENDER_GGT_slice)
