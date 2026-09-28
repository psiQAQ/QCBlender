"""Viewport probe and native slice controls; scientific arrays remain source data."""
import hashlib
import json

import bpy
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector
import numpy as np

from ..data import load_dataset
from ..planes import plane_frame, validate_configuration
from ..profile import source_positions
from ..sampling import sample_point
from .graph import view_modifier
from .geometry import current_geometry
from .profile import profile_source
from .source_browser import binding_key, bound_field, field_source, mapped_field


def slice_controls(obj):
    if obj is None or obj.get('qc_view_kind') != 'slice':
        raise ValueError('Choose an active QC scalar slice')
    modifier = view_modifier(obj)
    sockets = {item.name: item.identifier for item in modifier.node_group.interface.items_tree
               if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    if any(name not in sockets or sockets[name] not in modifier for name in ('Center', 'Rotation', 'Width', 'Height')):
        raise ValueError('Slice controls are missing from the QC modifier')
    return modifier, sockets


def _control_digest(obj, configuration=None):
    modifier, sockets = slice_controls(obj)
    values = [list(modifier[sockets[name]]) if name in ('Center', 'Rotation')
              else float(modifier[sockets[name]]) for name in ('Center', 'Rotation', 'Width', 'Height')]
    volume = obj.qc_settings.volume
    if volume is None:
        raise ValueError('Slice field volume is missing')
    values.append(np.asarray(obj.matrix_world.inverted() @ volume.matrix_world).tolist())
    if configuration is not None:
        values.append(np.asarray(obj.matrix_world.inverted() @ configuration.matrix_world).tolist())
    return hashlib.sha256(json.dumps(values).encode('ascii')).hexdigest()


def save_plane_definition(obj, mode, position=.5, source_numbers=None, configuration=None):
    """Save the definition after assigning the existing slice modifier inputs."""
    if mode == 'FREE':
        record = {'mode': 'FREE'}
    elif mode in ('ij', 'jk', 'ki', 'atoms'):
        if mode == 'atoms' and (configuration is None or source_numbers is None):
            raise ValueError('Associated atom plane needs its configuration and source numbers')
        record = {'mode': mode, 'position': position, 'source_numbers': source_numbers,
                  'configuration': configuration.name if configuration is not None else '',
                  'control_digest': _control_digest(obj, configuration)}
    else:
        raise ValueError('Unknown plane definition')
    obj['qc_plane_definition'] = json.dumps(record)


def _plane_record(obj):
    try:
        record = json.loads(obj.get('qc_plane_definition', '{}'))
        if not isinstance(record, dict):
            return {}
        configuration = None
        if record.get('mode') == 'atoms':
            configuration = bpy.data.objects.get(record.get('configuration', ''))
            if configuration is None:
                return {'mode': 'FREE'}
        if record.get('mode') not in (None, 'FREE') and record.get('control_digest') != _control_digest(obj, configuration):
            return {'mode': 'FREE'}
        return record
    except (ValueError, TypeError, KeyError):
        return {}


def _control_value(obj, name):
    modifier, sockets = slice_controls(obj)
    return modifier[sockets[name]]


def _set_control(obj, name, value):
    modifier, sockets = slice_controls(obj)
    modifier[sockets[name]] = value
    if _plane_record(obj).get('mode') != 'FREE':
        obj['qc_plane_definition'] = json.dumps({'mode': 'FREE'})
    obj.data.update()
    obj.update_tag()


def _sync_plane_labels_timer():
    for obj in bpy.data.objects:
        if obj.get('qc_view_kind') != 'slice' or 'qc_plane_definition' not in obj:
            continue
        try:
            record = json.loads(obj['qc_plane_definition'])
            if isinstance(record, dict) and record.get('mode') not in (None, 'FREE') and _plane_record(obj).get('mode') == 'FREE':
                obj['qc_plane_definition'] = json.dumps({'mode': 'FREE'})
        except (ValueError, TypeError, KeyError):
            continue
    return None


@persistent
def _sync_plane_labels(_scene, depsgraph):
    if depsgraph.updates and not bpy.app.timers.is_registered(_sync_plane_labels_timer):
        bpy.app.timers.register(_sync_plane_labels_timer, first_interval=.1)


class QCBLENDER_GGT_slice(bpy.types.GizmoGroup):
    bl_idname = 'QCBLENDER_GGT_slice'
    bl_label = 'QC Slice Controls'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @classmethod
    def poll(cls, context):
        from .capabilities import capability
        if not capability(context, 'slice')[1]:
            return False
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
        move.use_undo = True
        move.color, move.alpha = (.9, .9, .9), .7
        self._move = move
        self._sizes = []
        for name, axis, color in (('Width', 0, (.9, .25, .2)), ('Height', 1, (.2, .6, 1.))):
            gizmo = self.gizmos.new('GIZMO_GT_arrow_3d')
            def get_size(name=name, axis=axis):
                from mathutils import Euler
                obj = context.object
                direction = Euler(_control_value(obj, 'Rotation')).to_matrix().col[axis]
                return float(_control_value(obj, name)) * (obj.matrix_world.to_3x3() @ direction).length / 2
            def set_size(value, name=name, axis=axis):
                from mathutils import Euler
                obj = context.object
                direction = Euler(_control_value(obj, 'Rotation')).to_matrix().col[axis]
                scale = (obj.matrix_world.to_3x3() @ direction).length
                if scale > 1e-12:
                    offset = float(value[0] if isinstance(value, (tuple, list)) else value)
                    _set_control(obj, name, max(.001, 2 * abs(offset) / scale))
            gizmo.target_set_handler('offset', get=get_size, set=set_size)
            gizmo.use_undo = True
            gizmo.color, gizmo.alpha = color, .7
            gizmo.scale_basis = .6
            self._sizes.append((gizmo, axis))
        self._rotations = []
        for axis, color in enumerate(((1., .4, .4), (.4, 1., .4), (.4, .4, 1.))):
            gizmo = self.gizmos.new('GIZMO_GT_dial_3d')
            def set_angle(value, axis=axis):
                obj = context.object
                angles = list(_control_value(obj, 'Rotation'))
                angles[axis] = float(value[0] if isinstance(value, (tuple, list)) else value)
                _set_control(obj, 'Rotation', tuple(angles))
            gizmo.target_set_handler('offset',
                get=lambda axis=axis: float(_control_value(context.object, 'Rotation')[axis]),
                set=set_angle)
            gizmo.use_undo = True
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
        from .capabilities import poll_action
        return poll_action(cls, context, 'slice')

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
                save_plane_definition(obj, 'FREE')
                return {'FINISHED'}
            volume, field, _, _ = bound_field(obj)
            source_to_view = obj.matrix_world.inverted() @ volume.matrix_world
            atoms = numbers = atom_to_view = None
            if self.mode == 'atoms':
                atom_view = self.configuration
                if atom_view is None or atom_view.get('qc_view_kind') != 'atoms':
                    raise ValueError('Choose an associated atom view')
                atom_data = load_dataset(bpy.path.abspath(atom_view['qc_dataset']))
                atoms, provenance = current_geometry(atom_view, atom_data)
                field_data = load_dataset(bpy.path.abspath(volume['qc_dataset']))
                record = json.loads(atom_view.get('qc_association', '{}'))
                atom_to_view = obj.matrix_world.inverted() @ atom_view.matrix_world
                validate_configuration(field_data.arrays['positions'], field_data.arrays['atomic_numbers'],
                                       atoms, atom_data.arrays['atomic_numbers'], np.asarray(source_to_view),
                                       np.asarray(atom_to_view), field_data.metadata['source']['sha256'],
                                       provenance['source_sha256'], field_data.metadata.get('selected_job'),
                                       provenance['selected_job'], record)
                numbers = (self.atom_1, self.atom_2, self.atom_3)
            center, axes, width, height = plane_frame(field, self.mode, np.asarray(source_to_view),
                                                       self.position, atoms, numbers,
                                                       None if atom_to_view is None else np.asarray(atom_to_view))
            rotation = Matrix(axes.tolist()).to_euler('XYZ')
            for name, value in (('Center', center), ('Rotation', rotation), ('Width', width), ('Height', height)):
                modifier[sockets[name]] = tuple(float(v) for v in value) if name in ('Center', 'Rotation') else float(value)
            save_plane_definition(obj, self.mode, self.position, numbers,
                                  self.configuration if self.mode == 'atoms' else None)
            obj.data.update()
            obj.update_tag()
        except (ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


def _probe_draw(operator):
    font = __import__('blf')
    font.size(0, 15)
    for index, line in enumerate(operator._hud.splitlines()):
        font.position(0, 28, 46 + 20 * index, 0)
        font.draw(0, line)


class QCBLENDER_OT_click_probe(bpy.types.Operator):
    bl_idname = 'qcblender.click_probe'
    bl_label = 'Probe Active QC Surface'
    bl_options = {'REGISTER', 'UNDO'}
    role: EnumProperty(name='Field', items=[('GEOMETRY', 'Geometry', ''), ('COLOR', 'Bound color', '')], default='GEOMETRY')

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and poll_action(cls, context, 'probe_click'))

    def invoke(self, context, event):
        try:
            self._target = context.object
            self._geometry, self._geometry_field, geometry_meta, self._geometry_source = bound_field(self._target)
            if self.role == 'COLOR':
                _, _, sample_meta = mapped_field(self._target)
            else:
                sample_meta = geometry_meta
            self._source, self._field = profile_source(self._target, self.role)
            self._field_source = field_source(sample_meta, self._field)
            if not self._field_source.get('sha256'):
                raise ValueError('Sampled field source identity is missing')
            self._geometry_meta = geometry_meta
            self._sample_meta = sample_meta
            self._target_binding = binding_key(self._target)
            self._geometry_binding = binding_key(self._geometry)
            self._source_binding = binding_key(self._source)
            self._target_job = self._target.get('qc_source_job', -1)
            self._geometry_job = self._geometry.get('qc_source_job', -1)
            self._source_job = self._source.get('qc_source_job', -1)
            if (self._target_job != geometry_meta.get('selected_job', -1)
                    or self._geometry_job != geometry_meta.get('selected_job', -1)
                    or self._source_job != sample_meta.get('selected_job', -1)):
                raise ValueError('Field calculation identity differs from its Dataset')
            self._data = load_dataset(bpy.path.abspath(self._source['qc_dataset']))
            if self._data.metadata != sample_meta or binding_key(self._source) != self._source_binding:
                raise ValueError('Sampled field Dataset changed while the probe started')
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self._old_probe = self._target.get('qc_probe')
        if 'qc_probe' in self._target:
            del self._target['qc_probe']
        self._pending = None
        self._pending_transforms = None
        self._area = context.area
        self._region = next((region for region in self._area.regions if region.type == 'WINDOW'), None)
        self._view = self._area.spaces.active.region_3d
        if self._region is None or self._view is None:
            if self._old_probe is not None:
                self._target['qc_probe'] = self._old_probe
            self.report({'ERROR'}, '3D viewport window is unavailable')
            return {'CANCELLED'}
        self._hud = 'QC probe: click active surface; Enter saves; Esc restores'
        self._handle = bpy.types.SpaceView3D.draw_handler_add(_probe_draw, (self,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self.modal(context, event)
        return {'RUNNING_MODAL'}

    def _close(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        self._area.tag_redraw()

    def _check_binding(self, context):
        if context.object != self._target or self._target.hide_get():
            raise ValueError('Active surface changed or is hidden')
        geometry, geometry_field, geometry_meta, geometry_source = bound_field(self._target)
        if self.role == 'COLOR':
            _, _, sample_meta = mapped_field(self._target)
        else:
            sample_meta = geometry_meta
        source, field = profile_source(self._target, self.role)
        if (geometry != self._geometry or geometry_field != self._geometry_field
                or source != self._source or field != self._field
                or binding_key(self._target) != self._target_binding
                or binding_key(geometry) != self._geometry_binding
                or binding_key(source) != self._source_binding
                or self._target.get('qc_source_job', -1) != self._target_job
                or geometry.get('qc_source_job', -1) != self._geometry_job
                or source.get('qc_source_job', -1) != self._source_job
                or geometry_meta != self._geometry_meta
                or geometry_source != self._geometry_source
                or sample_meta != self._sample_meta
                or field_source(sample_meta, field) != self._field_source):
            raise ValueError('Field binding changed during probe')

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if self._old_probe is not None:
                self._target['qc_probe'] = self._old_probe
            elif 'qc_probe' in self._target:
                del self._target['qc_probe']
            self._close(context)
            return {'CANCELLED'}
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if self._pending is None:
                self._hud = 'QC probe invalid: click a valid point before saving'
                self._area.tag_redraw()
                return {'RUNNING_MODAL'}
            try:
                self._check_binding(context)
                if any(not np.array_equal(saved, np.asarray(obj.matrix_world))
                       for saved, obj in zip(self._pending_transforms,
                                             (self._target, self._geometry, self._source))):
                    raise ValueError('Field transform changed after the sample')
            except (ValueError, OSError, KeyError, TypeError) as error:
                self._pending = None
                self._pending_transforms = None
                self._hud = 'QC probe invalid: ' + str(error)
                self._area.tag_redraw()
                return {'RUNNING_MODAL'}
            self._target['qc_probe'] = json.dumps(self._pending)
            self._target.update_tag()
            self._close(context)
            self.report({'INFO'}, f"{self._pending['quantity']}: {self._pending['value']:.8g} {self._pending['unit']}")
            return {'FINISHED'}
        if event.type != 'LEFTMOUSE' or event.value != 'PRESS':
            return {'RUNNING_MODAL'}
        self._pending = None
        self._pending_transforms = None
        try:
            self._check_binding(context)
            field = self._field
            region = self._region
            coord = (event.mouse_x - region.x, event.mouse_y - region.y)
            if not (0 <= coord[0] < region.width and 0 <= coord[1] < region.height):
                self._hud = 'QC probe: no hit in the 3D viewport window'
                self._area.tag_redraw()
                return {'RUNNING_MODAL'}
            origin = view3d_utils.region_2d_to_origin_3d(region, self._view, coord)
            direction = view3d_utils.region_2d_to_vector_3d(region, self._view, coord)
            evaluated = self._target.evaluated_get(context.evaluated_depsgraph_get())
            inverse = evaluated.matrix_world.inverted()
            hit, local, _, _ = evaluated.ray_cast(inverse @ origin, (inverse.to_3x3() @ direction).normalized())
            if not hit:
                self._hud = 'QC probe: no hit on active surface'
                self._area.tag_redraw()
                return {'RUNNING_MODAL'}
            world = evaluated.matrix_world @ local
            position = source_positions(world, world, self._source.matrix_world)[0]
            value = sample_point(self._data.arrays[field['array']], self._data.arrays[field['valid_mask']], field, position)
            record = {'value': float(value), 'unit': field['unit'], 'quantity': field['quantity'],
                      'field_role': self.role, 'source_position_angstrom': position.tolist(),
                      'world_position': [float(v) for v in world], 'interpolation': 'trilinear',
                      'source_sha256': self._field_source['sha256'],
                      'field_source': self._field_source,
                      'dataset_source_sha256': self._source['qc_source_sha256'],
                      'dataset_sha256': self._source['qc_dataset_sha256'],
                      'source_job': self._sample_meta.get('selected_job', -1),
                      'field': field}
            self._pending = record
            self._pending_transforms = tuple(np.asarray(obj.matrix_world).copy()
                                             for obj in (self._target, self._geometry, self._source))
            xyz = ', '.join(f'{float(v):.4g}' for v in position)
            world_xyz = ', '.join(f'{float(v):.4g}' for v in world)
            self._hud = (f"QC probe valid: {field['quantity']} = {value:.8g} {field['unit']}; Enter saves\n"
                         f"source ({xyz}) Å; world ({world_xyz}) BU")
        except ValueError as error:
            state = 'outside field' if 'outside the field domain' in str(error) else 'invalid'
            self._hud = 'QC probe ' + state + ': ' + str(error)
        except (OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            self._hud = 'QC probe invalid: ' + str(error)
        self._area.tag_redraw()
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


_registered_tools = []


def register_tool():
    if bpy.app.background:
        return
    if _registered_tools:
        if len(_registered_tools) == 3 and _sync_plane_labels in bpy.app.handlers.depsgraph_update_post:
            return
        raise RuntimeError('QC viewport tools are only partly registered')
    try:
        bpy.utils.register_class(QCBLENDER_GGT_slice)
        _registered_tools.append('gizmo')
        bpy.utils.register_tool(QCBLENDER_WST_probe, after={'builtin.cursor'}, separator=True)
        _registered_tools.append('probe')
        bpy.utils.register_tool(QCBLENDER_WST_slice, after={QCBLENDER_WST_probe.bl_idname})
        _registered_tools.append('slice')
        bpy.app.handlers.depsgraph_update_post.append(_sync_plane_labels)
    except Exception as error:
        try:
            unregister_tool()
        except Exception as cleanup:
            raise ExceptionGroup('QC viewport tool registration and rollback failed', [error, cleanup]) from error
        raise


def unregister_tool():
    if _sync_plane_labels in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_sync_plane_labels)
    if bpy.app.timers.is_registered(_sync_plane_labels_timer):
        bpy.app.timers.unregister(_sync_plane_labels_timer)
    errors = []
    for name, unregister in (('slice', lambda: bpy.utils.unregister_tool(QCBLENDER_WST_slice)),
                             ('probe', lambda: bpy.utils.unregister_tool(QCBLENDER_WST_probe)),
                             ('gizmo', lambda: bpy.utils.unregister_class(QCBLENDER_GGT_slice))):
        if name not in _registered_tools:
            continue
        try:
            unregister()
        except Exception as error:
            errors.append(error)
        else:
            _registered_tools.remove(name)
    if errors:
        raise ExceptionGroup('QC viewport tool unregister failed', errors)
