"""Volume display transfers preserve the source scalar and its physical units."""
import json

import bpy

from .views import group_sockets, socket
from .graph import tag_view


def fog_material(quantity):
    mat = bpy.data.materials.new('QC volume fog')
    mat.use_nodes = True
    mat['qc_fog'] = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    value = nodes.new('ShaderNodeAttribute')
    value.attribute_name = 'qc_value'
    valid = nodes.new('ShaderNodeAttribute')
    valid.attribute_name = 'qc_valid'
    mask = nodes.new('ShaderNodeMath')
    mask.operation = 'GREATER_THAN'
    mask.inputs[1].default_value = .999999
    links.new(valid.outputs['Fac'], mask.inputs[0])
    signed = quantity not in ('electron_number_density', 'alpha_density', 'beta_density')
    magnitude = nodes.new('ShaderNodeMath')
    magnitude.operation = 'ABSOLUTE' if signed else 'MAXIMUM'
    magnitude.inputs[1].default_value = 0
    links.new(value.outputs['Fac'], magnitude.inputs[0])
    scale = nodes.new('ShaderNodeValue')
    scale.name = 'Optical Scale'
    scale['qc_control'] = 'Opacity Scale'
    scale.label = 'Display opacity scale (not electron density)'
    scale.outputs[0].default_value = 20
    opacity = nodes.new('ShaderNodeMath')
    opacity.operation = 'MULTIPLY'
    links.new(magnitude.outputs[0], opacity.inputs[0])
    links.new(scale.outputs[0], opacity.inputs[1])
    clip = nodes.new('ShaderNodeMath')
    clip.operation = 'MAXIMUM'
    clip.inputs[1].default_value = 0
    links.new(opacity.outputs[0], clip.inputs[0])
    density = nodes.new('ShaderNodeMath')
    density.operation = 'MULTIPLY'
    links.new(clip.outputs[0], density.inputs[0])
    links.new(mask.outputs[0], density.inputs[1])
    color = nodes.new('ShaderNodeValToRGB')
    color.name = 'Sign Colors'
    color['qc_role'] = 'color_ramp'
    color.color_ramp.elements[0].color = (.85, .12, .08, 1)
    color.color_ramp.elements[1].color = (.1, .3, .8, 1)
    from .assets import math
    controls = {}
    for name, default in [('Color Minimum', -.05 if signed else 0.), ('Color Maximum', .05),
                          ('Opacity Range', .1), ('Display Threshold', 0.)]:
        control = nodes.new('ShaderNodeValue')
        control['qc_control'] = name
        control.label = name
        control.outputs[0].default_value = default
        controls[name] = control.outputs[0]
    normalized = nodes.new('ShaderNodeMapRange')
    normalized.clamp = True
    links.new(value.outputs['Fac'], normalized.inputs['Value'])
    links.new(controls['Color Minimum'], normalized.inputs['From Min'])
    links.new(controls['Color Maximum'], normalized.inputs['From Max'])
    links.new(normalized.outputs['Result'], color.inputs['Fac'])
    opacity_map = nodes.new('ShaderNodeValToRGB')
    opacity_map['qc_role'] = 'opacity_ramp'
    opacity_map.label = 'Opacity multiplier versus field magnitude'
    for element in opacity_map.color_ramp.elements:
        element.color = (1, 1, 1, 1)
    fraction = math(mat.node_tree, 'DIVIDE', magnitude.outputs[0], math(mat.node_tree, 'MAXIMUM', controls['Opacity Range'], 1e-12))
    links.new(fraction, opacity_map.inputs['Fac'])
    passed = math(mat.node_tree, 'GREATER_THAN', magnitude.outputs[0], controls['Display Threshold'])
    opacity_factor = math(mat.node_tree, 'MULTIPLY', opacity_map.outputs['Color'], passed)
    from .inspection import CLIP_INPUTS, clip_mask
    clipping = {}
    for name, kind, default in CLIP_INPUTS:
        control = nodes.new('ShaderNodeCombineXYZ' if kind == 'NodeSocketVector' else 'ShaderNodeValue')
        control['qc_control'] = name
        control.label = name
        if kind == 'NodeSocketVector':
            for i, component in enumerate(default):
                control.inputs[i].default_value = component
        else:
            control.outputs[0].default_value = float(default)
        clipping[name] = control.outputs[0]
    coordinates = nodes.new('ShaderNodeTexCoord')
    keep = clip_mask(mat.node_tree, coordinates.outputs['Object'], clipping)
    optical_density = math(mat.node_tree, 'MULTIPLY', density.outputs[0],
                           math(mat.node_tree, 'MULTIPLY', opacity_factor, keep))
    shader = nodes.new('ShaderNodeVolumePrincipled')
    shader.inputs['Density Attribute'].default_value = ''
    shader.inputs['Color Attribute'].default_value = ''
    links.new(optical_density, shader.inputs['Density'])
    links.new(color.outputs[0], shader.inputs['Color'])
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(shader.outputs['Volume'], output.inputs['Volume'])
    for index, node in enumerate(nodes):
        node.location = (index % 5 * 220, -(index // 5) * 220)
    mat['qc_transfer'] = ('scale * abs(value)' if signed else 'scale * max(value, 0)') + ' * opacity curve * threshold/clip/valid masks'
    return mat


def fog_group():
    asset_id = 'qc.volume_fog.v1'
    existing = next((g for g in bpy.data.node_groups if g.get('qc_asset_id') == asset_id), None)
    if existing:
        return existing
    tree = bpy.data.node_groups.new('QC Style Volume Fog v1', 'GeometryNodeTree')
    tree['qc_asset_id'] = asset_id
    socket(tree, 'Volume', 'NodeSocketGeometry')
    socket(tree, 'Material', 'NodeSocketMaterial')
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    group_sockets(tree, (('Source', ('Volume',)), ('Material', ('Material',))))
    inputs = tree.nodes.new('NodeGroupInput')
    assign = tree.nodes.new('GeometryNodeSetMaterial')
    output = tree.nodes.new('NodeGroupOutput')
    tree.links.new(inputs.outputs['Volume'], assign.inputs['Geometry'])
    tree.links.new(inputs.outputs['Material'], assign.inputs['Material'])
    tree.links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    inputs.location, assign.location, output.location = (0, 0), (240, 0), (480, 0)
    return tree


def fog_view(source):
    volume = source.qc_settings.volume
    if volume is None:
        raise ValueError('Select a scalar field view with a bound volume')
    obj = bpy.data.objects.new('QC volume fog', bpy.data.meshes.new('QC fog carrier'))
    bpy.context.collection.objects.link(obj)
    for key in ('qc_dataset', 'qc_dataset_sha256', 'qc_source_sha256', 'qc_schema',
                'qc_coordinate_unit', 'qc_diagnostics', 'qc_field'):
        obj[key] = source[key]
    obj['qc_view_kind'] = 'fog'
    obj.qc_settings.volume = volume
    obj.parent = source.parent
    obj.matrix_world = source.matrix_world.copy()
    tree = bpy.data.node_groups.new('QC Fog View v1', 'GeometryNodeTree')
    tree.is_modifier = True
    mat = fog_material(json.loads(source['qc_field'])['quantity'])
    socket(tree, 'Material', 'NodeSocketMaterial', default=mat)
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    inputs, output = tree.nodes.new('NodeGroupInput'), tree.nodes.new('NodeGroupOutput')
    info = tree.nodes.new('GeometryNodeObjectInfo')
    info.transform_space = 'RELATIVE'
    info.inputs['Object'].default_value = volume
    style = tree.nodes.new('GeometryNodeGroup')
    style.node_tree = fog_group()
    tree.links.new(info.outputs['Geometry'], style.inputs['Volume'])
    tree.links.new(inputs.outputs['Material'], style.inputs['Material'])
    tree.links.new(style.outputs['Geometry'], output.inputs['Geometry'])
    for index, node in enumerate(tree.nodes):
        node.location = (index * 240, 0)
    obj.modifiers.new('QC Volume Fog', 'NODES').node_group = tree
    tag_view(tree)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


class QCBLENDER_OT_fog(bpy.types.Operator):
    bl_idname = 'qcblender.create_fog'
    bl_label = 'Create Volume Fog'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.qc_settings.volume is not None

    def execute(self, context):
        fog_view(context.object)
        return {'FINISHED'}
