"""Editable contour overlays, material palettes and profile axes."""

import hashlib
import json
import math
from pathlib import Path

import bpy
from bpy.app.handlers import persistent
from bpy.props import EnumProperty
from mathutils import Euler, Matrix, Vector

from ..plot_layout import DEFAULT_LAYOUT
from .graph import view_modifier
from .ui import AsyncOperation


PALETTES = {
    'RWB': ((.8, .03, .02, 1), (.95, .95, .95, 1), (.03, .18, .8, 1)),
    'BWR': ((.03, .18, .8, 1), (.95, .95, .95, 1), (.8, .03, .02, 1)),
    'BCY': ((.03, .18, .8, 1), (0., .85, .85, 1), (1., .85, .04, 1)),
    'GRAY': ((.04, .04, .04, 1), (.5, .5, .5, 1), (.96, .96, .96, 1)),
}
_pending = {}
_blocked = {}


def _mapped_material(obj):
    tree = view_modifier(obj).node_group
    nodes = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
             and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2']
    if len(nodes) != 1 or not tree.get('qc_color_mapping'):
        raise ValueError('View has no unique QC scalar color mapping')
    mat = nodes[0].inputs['Material'].default_value
    if mat is None or not mat.use_nodes:
        raise ValueError('QC scalar material is missing')
    ramps = [node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeValToRGB'
             and node.get('qc_role') == 'color_ramp']
    if len(ramps) != 1:
        raise ValueError('QC scalar material has no unique color ramp')
    return mat, ramps[0]


class QCBLENDER_OT_color_palette(bpy.types.Operator):
    bl_idname = 'qcblender.color_palette'
    bl_label = 'Set QC Scalar Palette'
    bl_options = {'REGISTER', 'UNDO'}

    palette: EnumProperty(items=[(key, key, '') for key in PALETTES])

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_color_source'))

    def execute(self, context):
        try:
            mat, ramp = _mapped_material(context.object)
            elements = sorted(ramp.color_ramp.elements, key=lambda element: element.position)
            if len(elements) != 3:
                raise ValueError('The color ramp was customized; keep editing it directly')
            for element, position, color in zip(elements, (0., .5, 1.), PALETTES[self.palette]):
                element.position, element.color = position, color
            mat['qc_palette'] = self.palette
        except (ValueError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_palette(bpy.types.Panel):
    bl_label = 'QCBlender · 色谱预设'
    bl_idname = 'QCBLENDER_PT_palette'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object is None or not context.object.get('qc_color_source'):
            return False
        try:
            _mapped_material(context.object)
            return True
        except ValueError:
            return False

    def draw(self, context):
        mat, ramp = _mapped_material(context.object)
        self.layout.label(text=mat.name)
        grid = self.layout.grid_flow(columns=2, align=True)
        for key, title in (('RWB', '红白蓝'), ('BWR', '蓝白红'),
                           ('BCY', '蓝青黄'), ('GRAY', '灰度')):
            grid.operator('qcblender.color_palette', text=title,
                         depress=mat.get('qc_palette', 'RWB') == key).palette = key
        self.layout.label(text='色带细节在节点材质中编辑')


def _contour_defaults(obj):
    defaults = {'qc_contour_enabled': False, 'qc_contour_source': 'COLOR' if obj.get('qc_color_source') else 'GEOMETRY',
                'qc_contour_levels': '', 'qc_contour_width': .02,
                'qc_contour_color': (.02, .02, .02, 1.), 'qc_contour_labels': False}
    for key, value in defaults.items():
        if key not in obj:
            obj[key] = value
    obj.id_properties_ui('qc_contour_width').update(min=.001, soft_max=.2)
    obj.id_properties_ui('qc_contour_color').update(subtype='COLOR', min=0., max=1.)


def _carrier(obj):
    name = obj.get('qc_contour_child')
    child = bpy.data.objects.get(name) if name else None
    if child is not None and child.parent == obj and 'qc_contour_owner' in child:
        return child
    return next((item for item in obj.children if 'qc_contour_owner' in item), None)


def _hide_contours(obj):
    child = _carrier(obj)
    if child:
        child.hide_set(True)
        child.hide_render = True


def cleanup_contours(obj):
    """Lifecycle hook for deleting a view or replacing its contour overlay."""
    for child in tuple(item for item in obj.children if 'qc_contour_owner' in item):
        for label in tuple(child.children):
            if not label.get('qc_contour_label'):
                world = label.matrix_world.copy()
                label.parent = obj
                label.matrix_world = world
                continue
            data = label.data
            bpy.data.objects.remove(label, do_unlink=True)
            if data.users == 0:
                bpy.data.curves.remove(data)
        curve = child.data
        materials = list(curve.materials)
        bpy.data.objects.remove(child, do_unlink=True)
        if curve.users == 0:
            bpy.data.curves.remove(curve)
        for mat in materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
    if 'qc_contour_child' in obj:
        del obj['qc_contour_child']


def copy_contour_settings(source, target):
    """Lifecycle hook: copied views build their own overlay from their bound field."""
    cleanup_contours(target)
    for key in ('qc_contour_enabled', 'qc_contour_source', 'qc_contour_levels',
                'qc_contour_width', 'qc_contour_color', 'qc_contour_labels'):
        if key in source:
            target[key] = source[key]
    for key in ('qc_contour_child', 'qc_contour_identity'):
        if key in target:
            del target[key]


def _state(obj):
    """Read only saved Blender properties and graph sockets; never load arrays."""
    if obj.get('qc_view_kind') != 'slice' or not obj.get('qc_contour_enabled'):
        raise ValueError('Enable contours on a QC slice')
    role = obj.get('qc_contour_source', 'COLOR')
    if role == 'COLOR':
        from .source_browser import color_mapping
        if not obj.get('qc_color_source'):
            raise ValueError('This slice has no bound color field')
        source = color_mapping(obj)[0].inputs['Object'].default_value
        recorded = json.loads(obj['qc_color_source'])
        field = json.loads(source.get('qc_field') or '{}') if source is not None else {}
        if not isinstance(recorded, dict) or not isinstance(field, dict):
            raise ValueError('Bound color field record is invalid')
        field_identity = {key: field.get(key) for key in
                          ('array', 'quantity', 'unit', 'orbital', 'spin', 'source_number')}
        if (source is None or source.get('qc_source_sha256') != recorded.get('source')
                or recorded.get('field_dataset_sha256', source.get('qc_dataset_sha256'))
                != source.get('qc_dataset_sha256')
                or recorded.get('field') and recorded['field'] != field_identity
                or any(field.get(key) != recorded.get(key) for key in ('quantity', 'unit'))):
            raise ValueError('Bound color field changed')
    elif role == 'GEOMETRY':
        source = obj.qc_settings.volume
        if (source is None or source.get('qc_field') != obj.get('qc_field')
                or source.get('qc_source_sha256') != obj.get('qc_source_sha256')):
            raise ValueError('Bound geometry field changed')
    else:
        raise ValueError('Choose the geometry or color field')
    if source is None or not source.get('qc_field') or not source.get('qc_dataset_sha256'):
        raise ValueError('Contour field binding is missing')
    modifier = view_modifier(obj)
    items = {item.name: item.identifier for item in modifier.node_group.interface.items_tree
             if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    controls = {name: modifier[items[name]] for name in ('Center', 'Rotation', 'Width', 'Height', 'Resolution')}
    center = Vector(controls['Center'])
    rotation = Euler(controls['Rotation'], 'XYZ').to_matrix()
    width, height, resolution = float(controls['Width']), float(controls['Height']), int(controls['Resolution'])
    if (not math.isfinite(width) or not math.isfinite(height)
            or width <= 0 or height <= 0 or not 2 <= resolution <= 1001):
        raise ValueError('Slice size and resolution must be positive')
    local_origin = center + rotation @ Vector((-width/2, -height/2, 0.))
    local_u, local_v = rotation @ Vector((width, 0., 0.)), rotation @ Vector((0., height, 0.))
    inverse = source.matrix_world.inverted()
    linear = inverse.to_3x3() @ obj.matrix_world.to_3x3()
    plane = {'origin': list(inverse @ (obj.matrix_world @ local_origin)),
             'axis_u': list(linear @ local_u), 'axis_v': list(linear @ local_v),
             'resolution': resolution}
    settings = {key: obj.get(key) for key in ('qc_contour_source', 'qc_contour_levels',
                'qc_contour_width', 'qc_contour_color', 'qc_contour_labels')}
    settings['qc_contour_color'] = list(settings['qc_contour_color'])
    if (not math.isfinite(float(settings['qc_contour_width'])) or float(settings['qc_contour_width']) <= 0
            or len(settings['qc_contour_color']) != 4
            or any(not math.isfinite(float(value)) or not 0 <= float(value) <= 1
                   for value in settings['qc_contour_color'])):
        raise ValueError('Contour width and RGBA color must be valid')
    binding = {'target_name': obj.name, 'target_dataset': obj.get('qc_dataset_sha256'),
               'source_name': source.name, 'source_dataset': source['qc_dataset_sha256'],
               'field': source['qc_field'], 'plane': plane, 'settings': settings,
               'target_matrix': [list(row) for row in obj.matrix_world],
               'source_matrix': [list(row) for row in source.matrix_world]}
    identity = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    return source, plane, identity


def _draw_contours(target, source, plane, report):
    from .views import material

    curve = bpy.data.curves.new('QC slice contours', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = float(target['qc_contour_width'])
    curve.bevel_resolution = 2
    color = tuple(target['qc_contour_color'])
    curve.materials.append(material('QC slice contour', color))
    longest = []
    for record in report['paths']:
        lines = record['lines']
        for line in lines:
            if len(line) < 2:
                continue
            spline = curve.splines.new('POLY')
            spline.points.add(len(line)-1)
            for point, xyz in zip(spline.points, line):
                point.co = (*xyz, 1.)
        if lines:
            longest.append((record['level'], max(lines, key=len)))
    carrier = bpy.data.objects.new('QC slice contours', curve)
    bpy.context.collection.objects.link(carrier)
    carrier.parent = target
    carrier.matrix_world = source.matrix_world.copy()
    carrier['qc_contour_owner'] = target.name
    carrier['qc_contour_identity'] = report['identity']
    if target.get('qc_contour_labels'):
        u = Vector(plane['axis_u']).normalized()
        v = Vector(plane['axis_v'])
        v = (v - u * u.dot(v)).normalized()
        normal = u.cross(v)
        orientation = Matrix((u, v, normal)).transposed().to_euler()
        unit = json.loads(source['qc_field'])['unit']
        for level, line in longest:
            font = bpy.data.curves.new('QC contour label', 'FONT')
            font.body, font.size = f'{level:.4g} {unit}', .16
            font.materials.append(curve.materials[0])
            label = bpy.data.objects.new('QC contour label', font)
            bpy.context.collection.objects.link(label)
            label.parent = carrier
            label.location = line[len(line)//2]
            label.rotation_euler = orientation
            label['qc_contour_label'] = True
    return carrier


class QCBLENDER_OT_toggle_contours(bpy.types.Operator):
    bl_idname = 'qcblender.toggle_contours'
    bl_label = 'Enable or Disable QC Contours'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'slice'

    def execute(self, context):
        obj = context.object
        _contour_defaults(obj)
        obj['qc_contour_enabled'] = not obj['qc_contour_enabled']
        if not obj['qc_contour_enabled']:
            _hide_contours(obj)
        else:
            child = _carrier(obj)
            if child is not None:
                try:
                    _, _, identity = _state(obj)
                except (ValueError, KeyError, TypeError):
                    pass
                else:
                    if identity == child.get('qc_contour_identity'):
                        child.hide_set(False)
                        child.hide_render = False
        return {'FINISHED'}


class QCBLENDER_OT_update_contours(AsyncOperation, bpy.types.Operator):
    bl_idname = 'qcblender.update_contours'
    bl_label = 'Update QC Slice Contours'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'slice'

    def begin(self, context):
        from .jobs import Job
        from .source_browser import mapped_field, read_metadata

        self._target = context.object
        source, self._plane, self._identity = _state(self._target)
        if self._target.as_pointer() in _pending:
            raise ValueError('Contour update is already running for this slice')
        if self._target.get('qc_contour_source') == 'COLOR':
            if mapped_field(self._target)[0] != source:
                raise ValueError('Bound color field changed')
        else:
            read_metadata(source)
        self._source = source
        self._target_pointer = self._target.as_pointer()
        self._target_name = self._target.name
        self._source_pointer = source.as_pointer()
        _hide_contours(self._target)
        self._target['qc_contour_status'] = 'Updating contours'
        job = Job('contours', dataset=bpy.path.abspath(source['qc_dataset']),
                  dataset_sha256=source['qc_dataset_sha256'], field=json.loads(source['qc_field']),
                  plane=self._plane, levels=self._target.get('qc_contour_levels', ''),
                  identity=self._identity)
        _pending[self._target.as_pointer()] = self._identity
        _blocked.pop(self._target.as_pointer(), None)
        return job

    def accept(self, context, report):
        pointer = self._target_pointer
        _pending.pop(pointer, None)
        if bpy.data.objects.get(self._target_name) != self._target:
            return
        source, plane, current = _state(self._target)
        if (pointer != self._target_pointer or source.as_pointer() != self._source_pointer
                or current != self._identity or report['identity'] != self._identity):
            _hide_contours(self._target)
            return
        path = Path(bpy.path.abspath(self._source['qc_dataset'])) / 'manifest.json'
        if hashlib.sha256(path.read_bytes()).hexdigest() != self._source['qc_dataset_sha256']:
            raise ValueError('Contour dataset changed before attachment')
        cleanup_contours(self._target)
        carrier = _draw_contours(self._target, self._source, plane, report)
        self._target['qc_contour_child'] = carrier.name
        self._target['qc_contour_identity'] = self._identity
        self._target['qc_contour_status'] = (
            f"{len(report['levels'])} levels; {report['valid_count']}/{report['sample_count']} valid samples")
        self.report({'INFO'}, f"Updated {len(report['levels'])} contour levels")

    def cancel(self, context):
        if hasattr(self, '_target_pointer'):
            pointer = self._target_pointer
            _pending.pop(pointer, None)
            _blocked[pointer] = getattr(self, '_identity', '')
            if bpy.data.objects.get(self._target_name) == self._target:
                self._target['qc_contour_status'] = 'Contour update cancelled or failed'
        super().cancel(context)


class QCBLENDER_PT_contours(bpy.types.Panel):
    bl_label = '切片等值线'
    bl_idname = 'QCBLENDER_PT_contours'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'slice'

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.operator('qcblender.toggle_contours',
                        text='关闭等值线' if obj.get('qc_contour_enabled') else '开启等值线')
        if not obj.get('qc_contour_enabled'):
            return
        for key, label in (('qc_contour_levels', '阈值列表（空白：自动 9 条）'),
                           ('qc_contour_width', '线宽 [布局单位]'), ('qc_contour_color', '线颜色'),
                           ('qc_contour_labels', '数值标签')):
            layout.prop(obj, f'["{key}"]', text=label)
        row = layout.row(align=True)
        for role, title in (('COLOR', '绑定色场'), ('GEOMETRY', '几何场')):
            sub = row.row(align=True)
            sub.enabled = role != 'COLOR' or bool(obj.get('qc_color_source'))
            button = sub.operator('qcblender.contour_source', text=title,
                                  depress=obj.get('qc_contour_source') == role)
            button.role = role
        layout.operator('qcblender.update_contours', text='更新等值线')
        if obj.get('qc_contour_status'):
            layout.label(text=obj['qc_contour_status'])


class QCBLENDER_OT_contour_source(bpy.types.Operator):
    bl_idname = 'qcblender.contour_source'
    bl_label = 'Choose QC Contour Field'
    bl_options = {'REGISTER', 'UNDO'}

    role: EnumProperty(items=[('COLOR', 'Color field', ''), ('GEOMETRY', 'Geometry field', '')])

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'slice'

    def execute(self, context):
        if self.role == 'COLOR' and not context.object.get('qc_color_source'):
            self.report({'ERROR'}, 'No bound color field is available')
            return {'CANCELLED'}
        context.object['qc_contour_source'] = self.role
        _hide_contours(context.object)
        return {'FINISHED'}


class QCBLENDER_OT_apply_profile_axes(bpy.types.Operator):
    bl_idname = 'qcblender.apply_profile_axes'
    bl_label = 'Apply Profile Axes'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'profile'

    def execute(self, context):
        from ..data import load_dataset
        from .profile import apply_profile_layout
        from .source_browser import read_metadata

        obj = context.object
        try:
            chart = json.loads(obj['qc_chart'])
            legacy = 'qc_profile_width' not in obj
            for key, value in DEFAULT_LAYOUT.items():
                if 'qc_profile_' + key not in obj:
                    obj['qc_profile_' + key] = chart.get(key, value)
            if legacy:
                for axis in 'xy':
                    if obj['qc_profile_' + axis + '_min'] >= obj['qc_profile_' + axis + '_max']:
                        obj['qc_profile_' + axis + '_max'] = obj['qc_profile_' + axis + '_min'] + 1.
            read_metadata(obj)
            data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
            apply_profile_layout(obj, data)
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_PT_profile_axes(bpy.types.Panel):
    bl_label = '剖面坐标轴与排版'
    bl_idname = 'QCBLENDER_PT_profile_axes'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'profile'

    def draw(self, context):
        obj = context.object
        layout = self.layout
        if 'qc_profile_width' not in obj:
            layout.operator('qcblender.apply_profile_axes', text='添加坐标轴控件')
            return
        layout.label(text='图幅与线宽使用本地布局单位')
        for key, title in (('width', '图幅宽度'), ('height', '图幅高度'), ('line_width', '线宽')):
            layout.prop(obj, f'["qc_profile_{key}"]', text=title)
        for axis in 'xy':
            layout.prop(obj, f'["qc_profile_{axis}_auto"]', text=axis.upper() + ' 自动范围')
            if not obj.get(f'qc_profile_{axis}_auto', True):
                row = layout.row(align=True)
                row.prop(obj, f'["qc_profile_{axis}_min"]', text='最小值')
                row.prop(obj, f'["qc_profile_{axis}_max"]', text='最大值')
            layout.prop(obj, f'["qc_profile_{axis}_ticks"]', text=axis.upper() + ' 刻度数')
        layout.prop(obj, '["qc_profile_precision"]', text='小数位数')
        layout.operator('qcblender.apply_profile_axes', text='应用排版')


def _watch_contours():
    for obj in bpy.data.objects:
        if obj.get('qc_view_kind') != 'slice' or not obj.get('qc_contour_enabled'):
            continue
        pointer = obj.as_pointer()
        try:
            _, _, identity = _state(obj)
        except (ValueError, KeyError, TypeError, ReferenceError):
            _hide_contours(obj)
            continue
        if identity == obj.get('qc_contour_identity') and _carrier(obj) is not None:
            continue
        _hide_contours(obj)
        if pointer in _pending or _blocked.get(pointer) == identity:
            continue
        attempted = False
        for window in bpy.context.window_manager.windows:
            area = next((area for area in window.screen.areas if area.type == 'VIEW_3D'), None)
            if area is None:
                continue
            region = next((region for region in area.regions if region.type == 'WINDOW'), None)
            if region is None:
                continue
            attempted = True
            try:
                with bpy.context.temp_override(window=window, area=area, region=region,
                                               object=obj, active_object=obj):
                    result = bpy.ops.qcblender.update_contours('EXEC_DEFAULT')
            except (RuntimeError, ValueError):
                continue
            if 'RUNNING_MODAL' in result:
                break
        else:
            if attempted:
                _blocked[pointer] = identity
    return .5


@persistent
def _on_load(_):
    _pending.clear()
    _blocked.clear()


def register():
    if not bpy.app.timers.is_registered(_watch_contours):
        bpy.app.timers.register(_watch_contours, first_interval=.5, persistent=True)
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)


def unregister():
    if bpy.app.timers.is_registered(_watch_contours):
        bpy.app.timers.unregister(_watch_contours)
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
    _pending.clear()
    _blocked.clear()
