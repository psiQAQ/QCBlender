"""Capture live QC configuration inputs without evaluating display geometry."""
from datetime import datetime, timezone
import math

from .copy_display import _state, _material_role
from .source_browser import (binding_key, bound_field, field_source, mapped_field,
                             object_record, read_metadata, source_object)
from .parameters import socket_label


def _value(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Non-finite configuration value')
        return value
    if hasattr(value, 'bl_rna'):
        return {'name': value.name, 'type': value.bl_rna.identifier}
    return [_value(part) for part in value]


def _material_snapshot(mat, role):
    controls = _material_role(mat, role)
    result = {'name': mat.name, 'role': role, 'controls': [], 'reasons': []}
    shaders = [node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled']
    if not shaders and not mat.get('qc_fog'):
        result['reasons'].append('Surface shader is not a supported Principled graph; color and shader inputs are unverified')
    expected_type = 'ShaderNodeVolumePrincipled' if mat.get('qc_fog') else 'ShaderNodeBsdfPrincipled'
    terminals = [node for node in mat.node_tree.nodes if node.bl_idname == expected_type]
    outputs = [node for node in mat.node_tree.nodes if node.bl_idname == 'ShaderNodeOutputMaterial'
               and node.is_active_output]
    if len(terminals) != 1 or len(outputs) != 1:
        result['reasons'].append('Material output or shader is missing/ambiguous; custom graph is unverified')
    else:
        item = outputs[0].inputs['Volume' if mat.get('qc_fog') else 'Surface']
        if len(item.links) != 1 or item.links[0].from_node != terminals[0]:
            result['reasons'].append('Material output uses a custom shader connection; graph is unverified')
    if len(shaders) > 1:
        result['reasons'].append('Several Principled shaders; surface material controls are ambiguous')
    elif shaders:
        shader = shaders[0]
        for name in ('Base Color', 'Alpha', 'Roughness'):
            item = shader.inputs[name]
            if item.is_linked:
                result['reasons'].append(name + ': incoming node link is not evaluated')
            else:
                result['controls'].append({'name': name, 'value': _value(item.default_value),
                                          'location': mat.name + ' / ' + shader.name + ' / ' + name})
    for name, node in controls.items():
        location = mat.name + ' / ' + node.name
        if name in ('color_ramp', 'opacity_ramp'):
            ramp = node.color_ramp
            value = {'color_mode': ramp.color_mode, 'interpolation': ramp.interpolation,
                     'hue_interpolation': ramp.hue_interpolation,
                     'elements': [{'position': item.position, 'color': _value(item.color)}
                                  for item in ramp.elements]}
        elif node.bl_idname == 'ShaderNodeCombineXYZ':
            if any(item.is_linked for item in node.inputs):
                raise ValueError(location + ': control uses a custom incoming link')
            value = [_value(item.default_value) for item in node.inputs]
        else:
            value = _value(node.outputs[0].default_value)
        result['controls'].append({'name': name, 'value': value, 'location': location})
    return result


def capture_view_summary(obj, frame):
    owner = source_object(obj)
    meta = read_metadata(owner)
    snapshot = {'schema': 1, 'dataset_manifest_sha256': binding_key(owner)[1],
                'captured_at_utc': datetime.now(timezone.utc).isoformat(),
                'view': {'name': obj.name, 'kind': obj.get('qc_view_kind'), 'scene_frame': frame,
                         'matrix_world': [_value(row) for row in obj.matrix_world]},
                'fields': {}, 'display': {'status': 'unverified', 'parameters': [],
                                         'materials': [], 'reasons': []}}
    if not snapshot['dataset_manifest_sha256']:
        raise ValueError('View summary requires the saved Dataset manifest SHA-256')
    if owner.get('qc_source_sha256') != meta['source']['sha256']:
        raise ValueError('View summary source differs from its saved Dataset')
    reasons = snapshot['display']['reasons']
    if owner.get('qc_view_kind') == 'atoms':
        choices = [(kind, owner.get(key)) for kind, key in
                   (('trajectory', 'qc_trajectory_frame'), ('optimization', 'qc_optimization_step'), ('irc', 'qc_irc_step'))
                   if owner.get(key) is not None]
        if len(choices) > 1:
            raise ValueError('View summary has conflicting configuration identities')
        if meta.get('trajectory') and not any(kind == 'trajectory' for kind, _ in choices):
            raise ValueError('View summary XYZ view is missing its current frame identity')
        kind, step = choices[0] if choices else ('source', None)
        snapshot['geometry_selection'] = {'kind': kind, 'step': step}
    if obj.get('qc_field'):
        if obj.get('qc_view_kind') in ('field', 'slice'):
            volume, field, field_meta, source = bound_field(obj)
        else:
            field = object_record(obj, 'qc_field')
            if field not in meta.get('fields', []):
                raise ValueError('View summary geometry field differs from its Dataset')
            volume, field_meta, source = owner, meta, field_source(meta, field)
        snapshot['fields']['geometry'] = {'field': field, 'source': source,
                                         'dataset_manifest_sha256': binding_key(volume)[1]}
    if obj.get('qc_color_source'):
        try:
            volume, field, color_meta = mapped_field(obj)
            snapshot['fields']['color'] = {'field': field, 'source': field_source(color_meta, field),
                                          'dataset_manifest_sha256': binding_key(volume)[1]}
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            reasons.append('Color binding: ' + str(error))
    try:
        state = _state(obj)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        reasons.append('Display graph: ' + str(error))
        return snapshot
    modifier = state['modifier']
    for name, item in state['sockets'].items():
        if item.socket_type == 'NodeSocketGeometry':
            continue
        if item.identifier not in modifier:
            reasons.append(name + ': modifier input is not stored; no default is substituted')
            continue
        try:
            value = _value(modifier[item.identifier])
        except (ValueError, TypeError) as error:
            reasons.append(name + ': ' + str(error))
            continue
        field = snapshot['fields'].get('geometry', {}).get('field', {})
        color = snapshot['fields'].get('color', {}).get('field', {})
        unit = color.get('unit') if name.startswith('Color ') else field.get('unit')
        snapshot['display']['parameters'].append({'name': name,
            'label': socket_label(name, field.get('quantity', ''), unit or ''), 'socket_type': item.socket_type,
            'value': value, 'location': modifier.name + ' / ' + item.identifier})
    for role, (mat, references) in state['materials'].items():
        if any(kind == 'socket' and identifier not in target
               for kind, target, identifier in references):
            reasons.append('Material ' + role + ': modifier input is not stored; no default is substituted')
            continue
        try:
            material = _material_snapshot(mat, role)
            snapshot['display']['materials'].append(material)
            reasons.extend('Material ' + mat.name + ': ' + reason for reason in material['reasons'])
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            reasons.append('Material ' + mat.name + ': ' + str(error))
    snapshot['display']['status'] = 'partial' if reasons else 'captured'
    snapshot['display']['coverage'] = 'QC outer connections and stored configuration inputs; internal groups and rendered output are unverified'
    return snapshot
