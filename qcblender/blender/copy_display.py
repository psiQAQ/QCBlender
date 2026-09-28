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
LEGEND_LAYOUT = ('Legend Length', 'Legend Width', 'Legend Text Size', 'Legend Decimals',
                 'Legend Vertical', 'Legend Rotation')
EXTRA = ('Geometry', 'Selection', 'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)',
         'Center', 'Rotation', 'Width', 'Height', 'Legend Position', 'Amplitude (angstrom)', 'Phase',
         'Cycles per second', 'Animate', 'Show Displacement Vectors', 'Vector Radius') + CLIP + LEGEND_LAYOUT
SOCKET_TYPES = {
    **{name: 'NodeSocketFloat' for name in (
        'Atom Radius', 'Bond Radius', 'VDW Scale', 'Wire Radius', 'Point Radius', 'Adaptivity',
        'Positive Opacity', 'Negative Opacity', 'Isovalue', 'Negative Isovalue',
        'Width', 'Height', 'Amplitude (angstrom)', 'Phase', 'Cycles per second', 'Vector Radius',
        'Legend Length', 'Legend Width', 'Legend Text Size', *COLOR_RANGE, *CHARGE_RANGE)},
    **{name: 'NodeSocketInt' for name in (
        STYLE_SOCKETS['atoms'], STYLE_SOCKETS['field'], 'Quality', 'Resolution',
        'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)', 'Legend Decimals')},
    **{name: 'NodeSocketBool' for name in (
        'Selection', 'Smooth Normals', 'Positive Phase', 'Negative Phase', 'Link Thresholds',
        'Show Legend', 'Legend Vertical', 'Animate', 'Show Displacement Vectors', 'Plane Enabled', 'Box Enabled')},
    **{name: 'NodeSocketVector' for name in (
        'Center', 'Rotation', 'Legend Position', 'Legend Rotation', 'Plane Origin', 'Plane Normal', 'Box Minimum', 'Box Maximum')},
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
    recorded = json.loads(tree.get('qc_sockets', '{}'))
    identities = {name: item.identifier for name, item in sockets.items()}
    # Existing charge views may predate registration of the added charge controls.
    legacy_charge = (kind == 'atoms' and tree.get('qc_charge_mapping')
                     and set(identities) - set(recorded) <= set(CHARGE_RANGE + ('Show Legend', 'Legend Position') + LEGEND_LAYOUT)
                     and all(identities.get(name) == identifier for name, identifier in recorded.items()))
    if (len(sockets) != sum(item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                            for item in tree.interface.items_tree)
            or recorded != identities and not legacy_charge):
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


def _display_path(obj, modifier, kind, sockets, mapping):
    """Require copied inputs to feed the standard displayed geometry branch."""
    from .graph import geometry_output

    tree = modifier.node_group

    def linked(input_socket):
        if len(input_socket.links) != 1:
            raise ValueError('QC display geometry has an unsupported connection')
        return input_socket.links[0].from_socket

    def group(asset_id):
        matches = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
                   and node.node_tree and node.node_tree.get('qc_asset_id') == asset_id]
        if len(matches) != 1:
            raise ValueError('QC display asset is missing or ambiguous')
        return matches[0]

    inputs = [node for node in tree.nodes if node.type == 'GROUP_INPUT']
    if len(inputs) != 1:
        raise ValueError('QC display input is ambiguous')
    inputs = inputs[0]
    asset = 'qc.atom_style.v1' if kind == 'atoms' else next(iter(CORE_ASSETS[kind]))
    style = group(asset)
    clip_nodes = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeGroup'
                  and node.node_tree and node.node_tree.get('qc_asset_id') == 'qc.clip.v1']
    if len(clip_nodes) != int(bool(tree.get('qc_clipping'))):
        raise ValueError('QC clipping graph is missing or ambiguous')
    clip = clip_nodes[0] if clip_nodes else None
    used_clip = False

    def unclipped(socket):
        nonlocal used_clip
        if clip and socket == clip.outputs['Geometry']:
            if used_clip or any(linked(clip.inputs[name]) != inputs.outputs[name] for name in CLIP):
                raise ValueError('QC clipping controls have changed')
            used_clip = True
            return linked(clip.inputs['Geometry'])
        return socket

    if mapping[0]:
        # color_volume() already validates the scalar group, legend and final output.
        displayed = linked(group('qc.color_scalar.v2').inputs['Geometry'])
    else:
        displayed = linked(geometry_output(tree))
    displayed = unclipped(displayed)

    if mapping[1]:
        join = displayed.node
        if join.bl_idname != 'GeometryNodeJoinGeometry' or displayed != join.outputs['Geometry']:
            raise ValueError('QC charge display is disconnected')
        branches = [link.from_socket for link in join.inputs['Geometry'].links]
        legends = [socket for socket in branches if socket.node.bl_idname == 'GeometryNodeSwitch'
                   and socket == socket.node.outputs['Output']]
        assignments = [socket.node for socket in branches if socket.node.bl_idname == 'GeometryNodeSetMaterial'
                       and socket == socket.node.outputs['Geometry']
                       and not socket.node.inputs['Material'].is_linked
                       and _has_role(socket.node.inputs['Material'].default_value, 'color_ramp')]
        if len(branches) != 2 or len(legends) != 1 or len(assignments) != 1:
            raise ValueError('QC charge legend has an unsupported branch')
        assign = assignments[0]
        if linked(legends[0].node.inputs['Switch']) != inputs.outputs['Show Legend']:
            raise ValueError('QC charge legend control is disconnected')
        displayed = linked(assign.inputs['Geometry'])
        for attribute in ('qc_sample_valid', 'qc_color_fraction'):
            node = displayed.node
            if (node.bl_idname != 'GeometryNodeStoreNamedAttribute'
                    or displayed != node.outputs['Geometry']
                    or node.inputs['Name'].default_value != attribute):
                raise ValueError('QC charge color branch has changed')
            displayed = linked(node.inputs['Geometry'])
        displayed = unclipped(displayed)

    if kind == 'atoms' and 'Show Displacement Vectors' in sockets:
        join = displayed.node
        if join.bl_idname != 'GeometryNodeJoinGeometry' or displayed != join.outputs['Geometry']:
            raise ValueError('QC displacement branch is disconnected')
        branches = [link.from_socket for link in join.inputs['Geometry'].links]
        vectors = [socket for socket in branches if socket.node.bl_idname == 'GeometryNodeSwitch'
                   and socket == socket.node.outputs['Output']]
        if len(branches) != 2 or len(vectors) != 1 or style.outputs['Geometry'] not in branches:
            raise ValueError('QC displacement branch has changed')
        if linked(vectors[0].node.inputs['Switch']) != inputs.outputs['Show Displacement Vectors']:
            raise ValueError('QC displacement control is disconnected')
        displayed = style.outputs['Geometry']

    if displayed != style.outputs['Geometry'] or (clip is not None and not used_clip and not mapping[0]):
        raise ValueError('QC style is not connected to the displayed geometry')

    controls = GEOMETRY[kind]
    if kind == 'atoms':
        controls += ('Material',)
    elif kind == 'field':
        controls += ('Isovalue', 'Negative Isovalue', 'Link Thresholds', 'Positive Phase', 'Negative Phase',
                     'Positive Opacity', 'Negative Opacity', 'Positive Material', 'Negative Material')
    elif kind == 'fog':
        controls += ('Material',)
    if any(linked(style.inputs[name]) != inputs.outputs[name] for name in controls):
        raise ValueError('QC display controls are disconnected from the style')
    if kind == 'atoms':
        geometry = linked(style.inputs['Geometry'])
        if 'Show Displacement Vectors' in sockets:
            position = geometry.node
            if (position.bl_idname != 'GeometryNodeSetPosition' or geometry != position.outputs['Geometry']
                    or linked(position.inputs['Geometry']) != inputs.outputs['Geometry']):
                raise ValueError('QC atom geometry input has changed')
        elif geometry != inputs.outputs['Geometry']:
            raise ValueError('QC atom geometry input has changed')
        if not style.inputs['Selection'].links:
            raise ValueError('QC atom selection is disconnected')
    if kind in ('field', 'fog'):
        volume = linked(style.inputs['Volume']).node
        if (volume.bl_idname != 'GeometryNodeObjectInfo'
                or volume.outputs['Geometry'] != linked(style.inputs['Volume'])
                or volume.transform_space != 'RELATIVE'
                or volume.inputs['Object'].default_value != obj.qc_settings.volume):
            raise ValueError('QC displayed volume differs from its bound source')


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
    _display_path(obj, modifier, kind, sockets, mapping)
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
