"""Display clipping and point inspection without modifying source arrays."""
import itertools
import json

import bpy
import numpy as np

from ..data import load_dataset
from .assets import asset, math
from .graph import arrange, insert_geometry, tag_view, view_modifier
from .views import socket

CLIP_INPUTS = [
    ('Plane Enabled', 'NodeSocketBool', False),
    ('Plane Origin', 'NodeSocketVector', (0., 0., 0.)),
    ('Plane Normal', 'NodeSocketVector', (1., 0., 0.)),
    ('Box Enabled', 'NodeSocketBool', False),
    ('Box Minimum', 'NodeSocketVector', (-3., -3., -3.)),
    ('Box Maximum', 'NodeSocketVector', (3., 3., 3.))]


def clip_mask(tree, position, controls):
    nodes, links = tree.nodes, tree.links
    offset = nodes.new('ShaderNodeVectorMath')
    offset.operation = 'SUBTRACT'
    links.new(position, offset.inputs[0])
    links.new(controls['Plane Origin'], offset.inputs[1])
    dot = nodes.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    links.new(offset.outputs['Vector'], dot.inputs[0])
    links.new(controls['Plane Normal'], dot.inputs[1])
    outside = math(tree, 'MULTIPLY', controls['Plane Enabled'], math(tree, 'LESS_THAN', dot.outputs['Value'], 0))
    xyz = []
    for vector in (position, controls['Box Minimum'], controls['Box Maximum']):
        split = nodes.new('ShaderNodeSeparateXYZ')
        links.new(vector, split.inputs[0])
        xyz.append(split)
    box_outside = 0
    for axis in 'XYZ':
        below = math(tree, 'LESS_THAN', xyz[0].outputs[axis], xyz[1].outputs[axis])
        above = math(tree, 'GREATER_THAN', xyz[0].outputs[axis], xyz[2].outputs[axis])
        box_outside = math(tree, 'MAXIMUM', box_outside, math(tree, 'MAXIMUM', below, above))
    outside = math(tree, 'MAXIMUM', outside, math(tree, 'MULTIPLY', controls['Box Enabled'], box_outside))
    return math(tree, 'SUBTRACT', 1, outside)


def clip_group():
    tree, source, output = asset('qc.clip.v1', 'QC Clip Geometry',
        [('Geometry', 'NodeSocketGeometry', None)] + CLIP_INPUTS)
    if source is None:
        return tree
    position = tree.nodes.new('GeometryNodeInputPosition')
    keep = clip_mask(tree, position.outputs['Position'], {name: source.outputs[name] for name, _, _ in CLIP_INPUTS})
    delete = tree.nodes.new('GeometryNodeDeleteGeometry')
    delete.domain = 'POINT'
    tree.links.new(source.outputs['Geometry'], delete.inputs['Geometry'])
    tree.links.new(math(tree, 'SUBTRACT', 1, keep), delete.inputs['Selection'])
    tree.links.new(delete.outputs['Geometry'], output.inputs['Geometry'])
    return arrange(tree)


def add_clip(obj):
    modifier = view_modifier(obj)
    tree = modifier.node_group
    if tree.get('qc_clipping'):
        raise ValueError('This view already has clipping controls; edit its existing nodes')
    if obj.get('qc_view_kind') == 'fog':
        raise ValueError('Volume clipping is controlled by the fog material')
    node = insert_geometry(tree, clip_group())
    inputs = next(n for n in tree.nodes if n.type == 'GROUP_INPUT')
    for name, kind, default in CLIP_INPUTS:
        item = socket(tree, name, kind, default=default)
        modifier[item.identifier] = default
        tree.links.new(inputs.outputs[item.identifier], node.inputs[name])
    tree['qc_clipping'] = True
    tag_view(tree)
    obj.update_tag()


def sample_point(values, valid, field, position):
    """Trilinear float64 sampling; invalid contributing corners do not become zero."""
    point = (np.asarray(position, dtype=float) - field['origin']) @ np.linalg.inv(np.asarray(field['steps']))
    if not np.isfinite(point).all():
        raise ValueError('Sampling coordinates must be finite')
    shape = np.asarray(values.shape)
    if np.any(point < -1e-7) or np.any(point > shape - 1 + 1e-7):
        raise ValueError('Cursor is outside the field domain')
    point = np.clip(point, 0, shape - 1)
    lower = np.floor(point).astype(int)
    upper = np.minimum(lower + 1, shape - 1)
    fraction = point - lower
    result = 0.
    for corner in itertools.product((0, 1), repeat=3):
        weight = float(np.prod(np.where(corner, fraction, 1 - fraction)))
        if weight <= 1e-14:
            continue
        index = tuple(np.where(corner, upper, lower))
        if not valid[index]:
            raise ValueError('Cursor interpolation intersects an invalid field region')
        result += weight * float(values[index])
    return result


class QCBLENDER_OT_clip(bpy.types.Operator):
    bl_idname = 'qcblender.add_clipping'
    bl_label = 'Add Plane / Box Clipping'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') in ('field', 'slice', 'atoms')

    def execute(self, context):
        try:
            add_clip(context.object)
        except ValueError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_probe(bpy.types.Operator):
    bl_idname = 'qcblender.probe_field'
    bl_label = 'Read Field at 3D Cursor'

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.qc_settings.volume is not None

    def execute(self, context):
        obj = context.object
        try:
            source = obj.qc_settings.volume
            field = json.loads(source['qc_field'])
            data = load_dataset(bpy.path.abspath(source['qc_dataset']))
            position = source.matrix_world.inverted() @ context.scene.cursor.location
            value = sample_point(data.arrays[field['array']], data.arrays[field['valid_mask']], field, position)
            obj['qc_probe'] = json.dumps({'value': value, 'unit': field['unit'], 'quantity': field['quantity'],
                'source_position_angstrom': list(position), 'world_position': list(context.scene.cursor.location),
                'interpolation': 'trilinear', 'source_sha256': source['qc_source_sha256']})
        except (ValueError, OSError, KeyError) as error:
            if 'qc_probe' in obj:
                del obj['qc_probe']
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self.report({'INFO'}, f"{field['quantity']}: {value:.8g} {field['unit']} (trilinear)")
        return {'FINISHED'}
