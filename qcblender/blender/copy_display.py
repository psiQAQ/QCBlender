"""Copy selected display controls between compatible views in the current scene."""
import json
import math

import bpy
from bpy.props import BoolProperty

from .graph import view_modifier
from .parameters import STYLE_SOCKETS
from .source_browser import color_volume


CORE_ASSETS = {
    'atoms': {'qc.atom_selection.v1', 'qc.atom_style.v1'},
    'field': {'qc.isosurface.v3'},
    'slice': {'qc.slice.v1'},
    'fog': {'qc.volume_fog.v1'},
}
GEOMETRY = {
    'atoms': (STYLE_SOCKETS['atoms'], 'Atom Radius', 'Bond Radius', 'VDW Scale', 'Quality'),
    'field': (STYLE_SOCKETS['field'], 'Wire Radius', 'Point Radius', 'Quality', 'Adaptivity', 'Smooth Normals'),
    'slice': ('Width', 'Height', 'Resolution'),
    'fog': (),
}
COLOR_RANGE = ('Color Minimum', 'Color Center', 'Color Maximum')
CHARGE_RANGE = ('Charge Minimum', 'Charge Center', 'Charge Maximum')
APPEARANCE = {
    'atoms': ('Material', 'Show Legend'),
    'field': ('Positive Material', 'Negative Material', 'Positive Opacity', 'Negative Opacity', 'Show Legend'),
    'slice': ('Show Legend',),
    'fog': ('Material',),
}
NUMERICAL = {
    'atoms': (*CHARGE_RANGE, *COLOR_RANGE),
    'field': ('Isovalue', 'Negative Isovalue', 'Link Thresholds', 'Positive Phase', 'Negative Phase',
              *COLOR_RANGE),
    'slice': COLOR_RANGE,
    'fog': (),
}
FOG_NUMERIC = ('Color Minimum', 'Color Maximum', 'Opacity Range', 'Display Threshold')
FOG_APPEARANCE = ('Opacity Scale',)
CLIP = ('Plane Enabled', 'Plane Origin', 'Plane Normal', 'Box Enabled', 'Box Minimum', 'Box Maximum')
EXTRA = ('Geometry', 'Selection', 'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)',
         'Center', 'Rotation', 'Width', 'Height', 'Legend Position', 'Amplitude (angstrom)', 'Phase',
         'Cycles per second', 'Animate', 'Show Displacement Vectors', 'Vector Radius') + CLIP
SOCKET_TYPES = {
    **{name: 'NodeSocketFloat' for name in (
        'Atom Radius', 'Bond Radius', 'VDW Scale', 'Wire Radius', 'Point Radius', 'Adaptivity',
        'Positive Opacity', 'Negative Opacity', 'Isovalue', 'Negative Isovalue',
        'Width', 'Height', 'Amplitude (angstrom)', 'Phase', 'Cycles per second', 'Vector Radius',
        *COLOR_RANGE, *CHARGE_RANGE)},
    **{name: 'NodeSocketInt' for name in (
        STYLE_SOCKETS['atoms'], STYLE_SOCKETS['field'], 'Quality', 'Resolution',
        'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)')},
    **{name: 'NodeSocketBool' for name in (
        'Selection', 'Smooth Normals', 'Positive Phase', 'Negative Phase', 'Link Thresholds',
        'Show Legend', 'Animate', 'Show Displacement Vectors', 'Plane Enabled', 'Box Enabled')},
    **{name: 'NodeSocketVector' for name in (
        'Center', 'Rotation', 'Legend Position', 'Plane Origin', 'Plane Normal', 'Box Minimum', 'Box Maximum')},
    **{name: 'NodeSocketMaterial' for name in ('Material', 'Positive Material', 'Negative Material')},
    'Geometry': 'NodeSocketGeometry',
}
MATERIAL_CONTROLS = set(FOG_NUMERIC + FOG_APPEARANCE + CLIP)
MATERIAL_ROLES = {'color_ramp', 'color_invert', 'opacity_ramp'}
_MISSING = object()


def _known_signature(record):
    quantity, unit = record.get('quantity'), record.get('unit')
    if (not isinstance(quantity, str) or not isinstance(unit, str)
            or quantity.strip().lower() in ('', 'unknown', 'unknown_scalar')
            or unit.strip().lower() in ('', 'unknown', '?')):
        raise ValueError('Numeric copying requires known physical quantity and unit')
    return quantity, unit


def _record(obj, key):
    value = json.loads(obj[key])
    if not isinstance(value, dict):
        raise ValueError(f'{key} must be a record')
    return value


def _science_field(obj, kind):
    if kind in ('field', 'slice'):
        from .source_browser import bound_field

        return bound_field(obj)[1]
    from .source_browser import binding_key, read_metadata

    volume = obj.qc_settings.volume
    if (volume is None or volume.get('qc_view_kind') != 'volume'
            or binding_key(volume) != binding_key(obj)
            or volume.get('qc_source_sha256') != obj.get('qc_source_sha256')):
        raise ValueError('Fog volume differs from the selected view')
    field, meta = _record(obj, 'qc_field'), read_metadata(obj)
    if (_record(volume, 'qc_field') != field or field not in meta.get('fields', [])
            or obj.get('qc_source_sha256') != meta['source'].get('sha256')):
        raise ValueError('Fog field differs from the saved dataset identity')
    return field


def _color_signature(obj):
    from .source_browser import mapped_field

    return _known_signature(mapped_field(obj)[1])


def _inputs(modifier, kind):
    tree = modifier.node_group
    assets = {node.node_tree.get('qc_asset_id') for node in tree.nodes
              if node.bl_idname == 'GeometryNodeGroup' and node.node_tree}
    if tree.get('qc_view_graph') != 2 or not CORE_ASSETS[kind].issubset(assets):
        raise ValueError('Only current standard QC view graphs support parameter copying')
    sockets = {item.name: item for item in tree.interface.items_tree
               if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    if (len(sockets) != sum(item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                            for item in tree.interface.items_tree)
            or json.loads(tree.get('qc_sockets', '{}')) != {name: item.identifier for name, item in sockets.items()}):
        raise ValueError('QC graph socket identities have changed')
    allowed = set(GEOMETRY[kind] + APPEARANCE[kind] + NUMERICAL[kind] + EXTRA)
    for name, item in sockets.items():
        if name not in allowed or item.socket_type != SOCKET_TYPES[name]:
            raise ValueError(f'Unsupported QC graph input: {name}')
    required = set(GEOMETRY[kind]) | ({'Material'} if kind in ('atoms', 'fog') else
                                       {'Positive Material', 'Negative Material'} if kind == 'field' else set())
    if kind == 'field':
        required.update(('Isovalue', 'Negative Isovalue', 'Link Thresholds', 'Positive Phase', 'Negative Phase'))
    if not required.issubset(sockets):
        raise ValueError('QC view is missing standard display inputs')
    return sockets


def _mapping(obj, modifier, sockets):
    tree = modifier.node_group
    scalar = bool(tree.get('qc_color_mapping'))
    charge = bool(tree.get('qc_charge_mapping'))
    if scalar != bool(obj.get('qc_color_source')) or charge and obj.get('qc_view_kind') != 'atoms':
        raise ValueError('QC color mapping metadata is inconsistent')
    groups = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
              and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2']
    if len(groups) != int(scalar):
        raise ValueError('Unsupported custom scalar mapping graph')
    if scalar:
        if not set(COLOR_RANGE + ('Show Legend',)).issubset(sockets):
            raise ValueError('QC color mapping controls are incomplete')
        color_volume(obj)
    method = obj.get('qc_charge_method')
    if charge and (not set(CHARGE_RANGE + ('Show Legend',)).issubset(sockets)
                   or not isinstance(method, str) or method.strip().lower() in ('', 'unknown')):
        raise ValueError('QC charge mapping controls or method are missing')
    if any(name in sockets for name in COLOR_RANGE) != scalar or any(name in sockets for name in CHARGE_RANGE) != charge:
        raise ValueError('Unsupported custom color mapping inputs')
    return scalar, charge


def _has_role(mat, role):
    return mat and mat.use_nodes and any(node.get('qc_role') == role for node in mat.node_tree.nodes)


def _materials(obj, modifier, sockets, mapping):
    roles = {}
    for name in ('Material', 'Positive Material', 'Negative Material'):
        if name in sockets:
            mat = modifier.get(sockets[name].identifier, sockets[name].default_value)
            if mat is None or not mat.use_nodes:
                raise ValueError(f'{name} is missing a node material')
            if (obj.get('qc_view_kind') == 'fog') != bool(mat.get('qc_fog')):
                raise ValueError(f'{name} is not the expected QC material')
            roles[name] = (mat, [('socket', modifier, sockets[name].identifier)])
    tree = modifier.node_group
    if mapping[0]:
        groups = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
                  and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2']
        if len(groups) != 1 or groups[0].inputs['Material'].is_linked:
            raise ValueError('Scalar mapping material is ambiguous')
        mat = groups[0].inputs['Material'].default_value
        if not _has_role(mat, 'color_ramp'):
            raise ValueError('Scalar color ramp is unavailable')
        refs = [('node', groups[0].inputs['Material'], None)]
        refs.extend(('node', node.inputs['Material'], None) for node in tree.nodes
                    if node.bl_idname == 'GeometryNodeSetMaterial' and not node.inputs['Material'].is_linked
                    and node.inputs['Material'].default_value == mat)
        roles['scalar_map'] = (mat, refs)
    if mapping[1]:
        other = roles.get('scalar_map', (None,))[0]
        candidates = {node.inputs['Material'].default_value for node in tree.nodes
                      if node.bl_idname == 'GeometryNodeSetMaterial' and not node.inputs['Material'].is_linked
                      and _has_role(node.inputs['Material'].default_value, 'color_ramp')
                      and node.inputs['Material'].default_value != other}
        if len(candidates) != 1:
            raise ValueError('Charge color ramp is missing or ambiguous')
        mat = candidates.pop()
        refs = [('node', node.inputs['Material'], None) for node in tree.nodes
                if node.bl_idname == 'GeometryNodeSetMaterial' and not node.inputs['Material'].is_linked
                and node.inputs['Material'].default_value == mat]
        roles['charge_map'] = (mat, refs)
    return roles


def _material_nodes(mat):
    result = {}
    for node in mat.node_tree.nodes:
        key = node.get('qc_role') or node.get('qc_control')
        if key:
            if key in result or key not in MATERIAL_ROLES | MATERIAL_CONTROLS:
                raise ValueError('Unknown or duplicate QC material control')
            expected = ('ShaderNodeValToRGB' if key in ('color_ramp', 'opacity_ramp') else
                        'ShaderNodeCombineXYZ' if key in ('Plane Origin', 'Plane Normal', 'Box Minimum', 'Box Maximum') else
                        'ShaderNodeValue')
            if node.bl_idname != expected:
                raise ValueError(f'Unsupported QC material control node: {key}')
            result[key] = node
    return result


def _material_role(mat, role):
    nodes = _material_nodes(mat)
    if role in ('scalar_map', 'charge_map'):
        expected = {'color_ramp', 'color_invert'}
    elif mat.get('qc_fog'):
        expected = {'color_ramp', 'opacity_ramp', *FOG_APPEARANCE, *FOG_NUMERIC, *CLIP}
    else:
        expected = set()
    if nodes.keys() != expected:
        raise ValueError(f'{role} has unsupported QC material controls')
    return nodes


def _ramp(source, target):
    original, copied = source.color_ramp, target.color_ramp
    copied.color_mode = original.color_mode
    copied.interpolation = original.interpolation
    copied.hue_interpolation = original.hue_interpolation
    while len(copied.elements) > 2:
        copied.elements.remove(copied.elements[-1])
    first, last = original.elements[0], original.elements[-1]
    copied.elements[0].position, copied.elements[1].position = 0, 1
    copied.elements[0].color, copied.elements[1].color = first.color[:], last.color[:]
    copied.elements[0].position, copied.elements[1].position = first.position, last.position
    for element in list(original.elements)[1:-1]:
        copied.elements.new(element.position).color = element.color[:]


def _copy_material_values(source, target, appearance, numerical, role):
    old, new = _material_role(source, role), _material_role(target, role)
    if old.keys() != new.keys() or bool(source.get('qc_fog')) != bool(target.get('qc_fog')):
        raise ValueError(f'{role} has incompatible material controls')
    if appearance:
        from .views import node_by_type

        left = node_by_type(source.node_tree.nodes, 'ShaderNodeBsdfPrincipled')
        right = node_by_type(target.node_tree.nodes, 'ShaderNodeBsdfPrincipled')
        if bool(left) != bool(right):
            raise ValueError(f'{role} has incompatible shaders')
        if left:
            for name in ('Base Color', 'Alpha', 'Roughness'):
                if left.inputs[name].is_linked != right.inputs[name].is_linked:
                    raise ValueError(f'{role} has incompatible shader inputs')
                if not left.inputs[name].is_linked:
                    right.inputs[name].default_value = left.inputs[name].default_value
        for key in ('color_ramp', 'opacity_ramp'):
            if key in old:
                _ramp(old[key], new[key])
        for key in ('color_invert', *FOG_APPEARANCE):
            if key in old:
                new[key].outputs[0].default_value = old[key].outputs[0].default_value
    if numerical and role == 'Material' and source.get('qc_fog'):
        for key in FOG_NUMERIC:
            new[key].outputs[0].default_value = old[key].outputs[0].default_value


def _check_range(values, prefix):
    low, mid, high = (values[prefix + ' ' + suffix] for suffix in ('Minimum', 'Center', 'Maximum'))
    if not all(math.isfinite(value) for value in (low, mid, high)) or not low < mid < high:
        raise ValueError(f'{prefix} range must have finite minimum < center < maximum')


def _state(obj):
    kind = obj.get('qc_view_kind')
    if kind not in CORE_ASSETS:
        raise ValueError(f'{obj.name}: unsupported QC view type {kind!r}')
    modifier = view_modifier(obj)
    sockets = _inputs(modifier, kind)
    mapping = _mapping(obj, modifier, sockets)
    values = {name: modifier.get(item.identifier, getattr(item, 'default_value', None))
              for name, item in sockets.items()}
    materials = _materials(obj, modifier, sockets, mapping)
    for role, (mat, _) in materials.items():
        _material_role(mat, role)
    return {'obj': obj, 'kind': kind, 'modifier': modifier, 'sockets': sockets,
            'mapping': mapping, 'values': values, 'materials': materials}


def _plan(source, target, geometry, appearance, numerical):
    kind = source['kind']
    if target['kind'] != kind:
        raise ValueError(f"{target['obj'].name}: select the same QC view type as the active view")
    if (appearance or numerical) and source['mapping'] != target['mapping']:
        raise ValueError(f"{target['obj'].name}: source and target color mapping capabilities differ")
    if numerical and kind in ('field', 'fog'):
        if _known_signature(_science_field(source['obj'], kind)) != _known_signature(_science_field(target['obj'], kind)):
            raise ValueError(f"{target['obj'].name}: geometry field quantity or unit differs")
    if numerical and source['mapping'][0]:
        if _color_signature(source['obj']) != _color_signature(target['obj']):
            raise ValueError(f"{target['obj'].name}: color field quantity or unit differs")
    if numerical and source['mapping'][1] and source['obj'].get('qc_charge_method') != target['obj'].get('qc_charge_method'):
        raise ValueError(f"{target['obj'].name}: atomic charge method differs")
    names = []
    if geometry:
        names.extend(GEOMETRY[kind])
    if appearance:
        names.extend(name for name in APPEARANCE[kind] if name in source['sockets'])
    if numerical:
        names.extend(name for name in NUMERICAL[kind] if name in source['sockets'])
    for name in names:
        if name not in target['sockets'] or source['sockets'][name].socket_type != target['sockets'][name].socket_type:
            raise ValueError(f"{target['obj'].name}: missing compatible {name} input")
    if numerical:
        for prefix, enabled in (('Color', source['mapping'][0]), ('Charge', source['mapping'][1])):
            if enabled:
                _check_range(source['values'], prefix)
        if kind == 'field' and any(not math.isfinite(source['values'][name]) or source['values'][name] <= 0
                                   for name in ('Isovalue', 'Negative Isovalue')):
            raise ValueError('Isosurface thresholds must be finite and positive')
    material_roles = set(source['materials']) if appearance else set()
    if numerical and kind == 'fog':
        material_roles.add('Material')
    if material_roles - target['materials'].keys() or (appearance and source['materials'].keys() != target['materials'].keys()):
        raise ValueError(f"{target['obj'].name}: material roles differ")
    if not names and not material_roles:
        raise ValueError(f"{target['obj'].name}: selected groups contain no transferable controls")
    if material_roles and any(role.endswith('_map') for role in material_roles) and target['modifier'].node_group.users > 1:
        raise ValueError(f"{target['obj'].name}: shared QC graph cannot safely rebind its mapping material")
    for role in material_roles:
        old, new = source['materials'][role][0], target['materials'][role][0]
        left, right = _material_role(old, role), _material_role(new, role)
        if left.keys() != right.keys() or bool(old.get('qc_fog')) != bool(new.get('qc_fog')):
            raise ValueError(f"{target['obj'].name}: incompatible {role} material controls")
        if numerical and role == 'Material' and kind == 'fog':
            if not set(FOG_NUMERIC).issubset(left):
                raise ValueError('Fog numeric controls are incomplete')
            low, high = (left[name].outputs[0].default_value for name in ('Color Minimum', 'Color Maximum'))
            if not all(math.isfinite(value) for value in (low, high)) or low >= high:
                raise ValueError('Fog color range must be finite and increasing')
    return {'target': target, 'names': names, 'roles': material_roles}


def copy_parameters(source_obj, targets, geometry=True, appearance=True, numerical=True):
    """Validate the full selection, then write only existing target display values."""
    if not (geometry or appearance or numerical):
        raise ValueError('Choose at least one parameter group')
    if not targets:
        raise ValueError('Select at least one other QC view')
    source = _state(source_obj)
    plans = [_plan(source, _state(obj), geometry, appearance, numerical) for obj in targets]
    created, changes = [], []
    try:
        # Build every material copy before touching a target view.
        for plan in plans:
            plan['copies'] = {}
            for role in plan['roles']:
                source_mat = source['materials'][role][0]
                target_mat = plan['target']['materials'][role][0]
                clone = target_mat.copy()
                created.append(clone)
                _copy_material_values(source_mat, clone, appearance, numerical, role)
                plan['copies'][role] = clone
        for plan in plans:
            target = plan['target']
            modifier = target['modifier']
            for name in plan['names']:
                if target['sockets'][name].socket_type == 'NodeSocketMaterial':
                    continue
                key = target['sockets'][name].identifier
                changes.append(('socket', modifier, key, modifier.get(key, _MISSING)))
                modifier[key] = source['values'][name]
            for role, clone in plan['copies'].items():
                for ref_kind, owner, key in target['materials'][role][1]:
                    old = owner.get(key, _MISSING) if ref_kind == 'socket' else owner.default_value
                    changes.append((ref_kind, owner, key, old))
                    if ref_kind == 'socket':
                        owner[key] = clone
                    else:
                        owner.default_value = clone
            target['obj'].update_tag()
    except Exception:
        for ref_kind, owner, key, old in reversed(changes):
            if ref_kind == 'socket':
                if old is _MISSING:
                    del owner[key]
                else:
                    owner[key] = old
            else:
                owner.default_value = old
        for plan in plans:
            plan['target']['obj'].update_tag()
        for clone in created:
            bpy.data.materials.remove(clone, do_unlink=True)
        raise


class QCBLENDER_OT_copy_display_parameters(bpy.types.Operator):
    bl_idname = 'qcblender.copy_display_parameters'
    bl_label = 'Copy Display Parameters'
    bl_description = 'Copy selected display groups from the active view to compatible selected QC views'
    bl_options = {'REGISTER', 'UNDO'}

    geometry: BoolProperty(name='几何表示', default=True)
    appearance: BoolProperty(name='外观', default=True)
    numerical: BoolProperty(name='数值设置', default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None and len(context.selected_objects) > 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        for name in ('geometry', 'appearance', 'numerical'):
            self.layout.prop(self, name)

    def execute(self, context):
        try:
            copy_parameters(context.object, [obj for obj in context.selected_objects if obj != context.object],
                            self.geometry, self.appearance, self.numerical)
        except (ValueError, KeyError, TypeError, AttributeError, ReferenceError, RuntimeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}
