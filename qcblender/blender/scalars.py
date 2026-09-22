"""Native grid sampling, signed color maps and planar scalar slices."""
import json

import bpy
from bpy.props import FloatProperty, IntProperty
import numpy as np

from ..association import compare_sources
from ..data import load_dataset
from .views import bind, material, socket


def scalar_material():
    mat = material('QC scalar color map', (.5, .5, .5, 1))
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    value = nodes.new('ShaderNodeAttribute')
    value.attribute_name = 'qc_color_fraction'
    valid = nodes.new('ShaderNodeAttribute')
    valid.attribute_name = 'qc_sample_valid'
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (.8, .03, .02, 1)
    ramp.color_ramp.elements[1].color = (.03, .18, .8, 1)
    ramp.color_ramp.elements.new(.5).color = (.95, .95, .95, 1)
    links.new(value.outputs['Fac'], ramp.inputs['Fac'])
    missing = nodes.new('ShaderNodeMixRGB')
    missing.inputs[1].default_value = (1, 0, 1, 1)
    links.new(valid.outputs['Fac'], missing.inputs[0])
    links.new(ramp.outputs['Color'], missing.inputs[2])
    links.new(missing.outputs[0], nodes.get('Principled BSDF').inputs['Base Color'])
    legend = nodes.new('ShaderNodeAttribute')
    legend.attribute_name = 'qc_legend'
    emission = nodes.new('ShaderNodeEmission')
    links.new(missing.outputs[0], emission.inputs['Color'])
    mix = nodes.new('ShaderNodeMixShader')
    links.new(legend.outputs['Fac'], mix.inputs[0])
    links.new(nodes.get('Principled BSDF').outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs[0], nodes.get('Material Output').inputs['Surface'])
    return mat


def color_fraction(tree, inputs, value, minimum, center, maximum):
    nodes, links = tree.nodes, tree.links
    lower, upper = nodes.new('ShaderNodeMapRange'), nodes.new('ShaderNodeMapRange')
    for mapping, start, end, low, high in [(lower, minimum, center, 0, .5), (upper, center, maximum, .5, 1)]:
        mapping.clamp = True
        links.new(value, mapping.inputs['Value'])
        links.new(inputs.outputs[start], mapping.inputs['From Min'])
        links.new(inputs.outputs[end], mapping.inputs['From Max'])
        mapping.inputs['To Min'].default_value, mapping.inputs['To Max'].default_value = low, high
    below = nodes.new('ShaderNodeMath')
    below.operation = 'LESS_THAN'
    links.new(value, below.inputs[0])
    links.new(inputs.outputs[center], below.inputs[1])
    choose = nodes.new('GeometryNodeSwitch')
    choose.input_type = 'FLOAT'
    links.new(below.outputs[0], choose.inputs['Switch'])
    links.new(lower.outputs['Result'], choose.inputs['True'])
    links.new(upper.outputs['Result'], choose.inputs['False'])
    return choose.outputs['Output']


def add_legend(obj, color_material, minimum, center, maximum, title):
    """Legend geometry reads the same range sockets and material as the colored view."""
    modifier = obj.modifiers[0]
    tree = modifier.node_group
    nodes, links = tree.nodes, tree.links
    for name, kind, value in [('Show Legend', 'NodeSocketBool', False),
                              ('Legend Position', 'NodeSocketVector', (3., 0., 0.))]:
        item = socket(tree, name, kind, default=value)
        modifier[item.identifier] = value
    inputs = next(n for n in nodes if n.type == 'GROUP_INPUT')
    output = next(n for n in nodes if n.type == 'GROUP_OUTPUT')
    original = output.inputs['Geometry'].links[0].from_socket
    grid = nodes.new('GeometryNodeMeshGrid')
    grid.inputs['Size X'].default_value = 2
    grid.inputs['Size Y'].default_value = .18
    grid.inputs['Vertices X'].default_value = 65
    grid.inputs['Vertices Y'].default_value = 2
    position = nodes.new('GeometryNodeInputPosition')
    xyz = nodes.new('ShaderNodeSeparateXYZ')
    links.new(position.outputs['Position'], xyz.inputs['Vector'])
    fraction = nodes.new('ShaderNodeMapRange')
    fraction.inputs['From Min'].default_value = -1
    fraction.inputs['From Max'].default_value = 1
    links.new(xyz.outputs['X'], fraction.inputs['Value'])
    geometry = grid.outputs['Mesh']
    for name, kind, value in [('qc_color_fraction', 'FLOAT', fraction.outputs['Result']),
                               ('qc_sample_valid', 'BOOLEAN', True), ('qc_legend', 'BOOLEAN', True)]:
        store = nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        store.inputs['Name'].default_value = name
        links.new(geometry, store.inputs['Geometry'])
        if value is True:
            store.inputs['Value'].default_value = True
        else:
            links.new(value, store.inputs['Value'])
        geometry = store.outputs['Geometry']
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = color_material
    links.new(geometry, assign.inputs['Geometry'])
    legend = nodes.new('GeometryNodeJoinGeometry')
    links.new(assign.outputs['Geometry'], legend.inputs['Geometry'])
    text_material = material('QC legend text', (.015, .015, .015, 1))
    emission = text_material.node_tree.nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (.015, .015, .015, 1)
    text_material.node_tree.links.new(emission.outputs[0], text_material.node_tree.nodes['Material Output'].inputs['Surface'])
    for label, offset in [(minimum, (-1, -.28, 0)), (center, (-.2, -.28, 0)),
                           (maximum, (.65, -.28, 0)), (None, (-1, .2, 0))]:
        text = nodes.new('GeometryNodeStringToCurves')
        text.inputs['Size'].default_value = .16
        if label:
            number = nodes.new('FunctionNodeValueToString')
            number.label = label
            number.inputs['Decimals'].default_value = 5
            links.new(inputs.outputs[label], number.inputs['Value'])
            links.new(number.outputs['String'], text.inputs['String'])
        else:
            text.label = 'QC Legend Title'
            text.inputs['String'].default_value = title
        realize = nodes.new('GeometryNodeRealizeInstances')
        links.new(text.outputs['Curve Instances'], realize.inputs['Geometry'])
        fill = nodes.new('GeometryNodeFillCurve')
        links.new(realize.outputs['Geometry'], fill.inputs['Curve'])
        transform = nodes.new('GeometryNodeTransform')
        transform.inputs['Translation'].default_value = offset
        links.new(fill.outputs['Mesh'], transform.inputs['Geometry'])
        text_assign = nodes.new('GeometryNodeSetMaterial')
        text_assign.inputs['Material'].default_value = text_material
        links.new(transform.outputs['Geometry'], text_assign.inputs['Geometry'])
        links.new(text_assign.outputs['Geometry'], legend.inputs['Geometry'])
    transform = nodes.new('GeometryNodeTransform')
    links.new(legend.outputs['Geometry'], transform.inputs['Geometry'])
    links.new(inputs.outputs['Legend Position'], transform.inputs['Translation'])
    show = nodes.new('GeometryNodeSwitch')
    show.input_type = 'GEOMETRY'
    links.new(inputs.outputs['Show Legend'], show.inputs['Switch'])
    links.new(transform.outputs['Geometry'], show.inputs['True'])
    join = nodes.new('GeometryNodeJoinGeometry')
    links.new(original, join.inputs['Geometry'])
    links.new(show.outputs['Output'], join.inputs['Geometry'])
    links.new(join.outputs['Geometry'], output.inputs['Geometry'])


def add_mapping(target, source, low, high):
    if not np.isfinite([low, high]).all() or low >= high:
        raise ValueError('Color minimum must be finite and below color maximum')
    volume = source.qc_settings.volume
    if volume is None:
        raise ValueError('Source field has no bound volume')
    modifier = target.modifiers[0]
    tree = modifier.node_group
    if tree.get('qc_color_mapping'):
        raise ValueError('This view already has a scalar mapping; edit its node inputs')
    for name, value in [('Color Minimum', low), ('Color Center', (low + high) / 2), ('Color Maximum', high)]:
        item = socket(tree, name, 'NodeSocketFloat', default=value)
        modifier[item.identifier] = value
    nodes, links = tree.nodes, tree.links
    inputs = next(n for n in nodes if n.type == 'GROUP_INPUT')
    output = next(n for n in nodes if n.type == 'GROUP_OUTPUT')
    geometry = output.inputs['Geometry'].links[0].from_socket
    info = nodes.new('GeometryNodeObjectInfo')
    info.transform_space = 'RELATIVE'
    info.inputs['Object'].default_value = volume
    position = nodes.new('GeometryNodeInputPosition')
    samples = []
    for name in ('qc_value', 'qc_valid'):
        grid = nodes.new('GeometryNodeGetNamedGrid')
        grid.inputs['Name'].default_value = name
        links.new(info.outputs['Geometry'], grid.inputs['Volume'])
        sample = nodes.new('GeometryNodeSampleGrid')
        sample.inputs['Interpolation'].default_value = 'Trilinear'
        links.new(grid.outputs['Grid'], sample.inputs['Grid'])
        links.new(position.outputs['Position'], sample.inputs['Position'])
        samples.append(sample.outputs['Value'])
    valid = nodes.new('ShaderNodeMath')
    valid.operation = 'GREATER_THAN'
    valid.inputs[1].default_value = .999999
    links.new(samples[1], valid.inputs[0])
    fraction = color_fraction(tree, inputs, samples[0], 'Color Minimum', 'Color Center', 'Color Maximum')
    for name, value, kind in [('qc_scalar_value', samples[0], 'FLOAT'),
                               ('qc_sample_valid', valid.outputs[0], 'BOOLEAN'),
                               ('qc_color_fraction', fraction, 'FLOAT')]:
        store = nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        store.inputs['Name'].default_value = name
        links.new(geometry, store.inputs['Geometry'])
        links.new(value, store.inputs['Value'])
        geometry = store.outputs['Geometry']
    assign = nodes.new('GeometryNodeSetMaterial')
    color_material = scalar_material()
    assign.inputs['Material'].default_value = color_material
    links.new(geometry, assign.inputs['Geometry'])
    links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    field = json.loads(source['qc_field'])
    title = {'electrostatic_potential': 'ESP', 'orbital_amplitude': 'MO amplitude',
             'electron_number_density': 'Electron density', 'spin_density': 'Spin density'}.get(field['quantity'], field['quantity'])
    add_legend(target, color_material, 'Color Minimum', 'Color Center', 'Color Maximum', title + ' [' + field['unit'] + ']')
    tree['qc_color_mapping'] = True
    target['qc_color_source'] = json.dumps({'source': source['qc_source_sha256'],
                                           'quantity': field['quantity'], 'unit': field['unit'],
                                           'interpolation': 'trilinear', 'missing_color': 'magenta'})
    for index, node in enumerate(nodes):
        node.location = (index % 6 * 220, -(index // 6) * 240)
    target.update_tag()


class QCBLENDER_OT_map_scalar(bpy.types.Operator):
    bl_idname = 'qcblender.map_scalar'
    bl_label = 'Map Selected Field to Active Surface'
    bl_options = {'REGISTER', 'UNDO'}
    minimum: FloatProperty(name='Color minimum (field unit)', default=-.05)
    maximum: FloatProperty(name='Color maximum (field unit)', default=.05)

    @classmethod
    def poll(cls, context):
        return context.object and 'qc_field' in context.object and len(context.selected_objects) == 2

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        target = context.object
        source = next(o for o in context.selected_objects if o != target)
        try:
            if 'qc_field' not in source:
                raise ValueError('Select two scalar field views, with the receiving surface active')
            associated = json.loads(source.parent.get('qc_association', '{}')) if source.parent else {}
            explicit_alignment = (associated.get('reference_source') == target['qc_source_sha256']
                                  and associated.get('moving_source') == source['qc_source_sha256'])
            compare_sources(load_dataset(bpy.path.abspath(target['qc_dataset'])),
                            load_dataset(bpy.path.abspath(source['qc_dataset'])), allow_rigid=explicit_alignment)
            add_mapping(target, source, self.minimum, self.maximum)
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class QCBLENDER_OT_slice(bpy.types.Operator):
    bl_idname = 'qcblender.create_slice'
    bl_label = 'Create Scalar Slice'
    bl_options = {'REGISTER', 'UNDO'}
    resolution: IntProperty(name='Samples per axis', default=101, min=2, max=1001)
    minimum: FloatProperty(name='Color minimum (field unit)', default=-.05)
    maximum: FloatProperty(name='Color maximum (field unit)', default=.05)

    @classmethod
    def poll(cls, context):
        return context.object is not None and 'qc_field' in context.object

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        source = context.object
        data = load_dataset(bpy.path.abspath(source['qc_dataset']))
        field = json.loads(source['qc_field'])
        shape, steps, origin = np.array(field['shape']), np.array(field['steps']), np.array(field['origin'])
        corners = np.array([[i, j, k] for i in (0, shape[0]-1) for j in (0, shape[1]-1) for k in (0, shape[2]-1)]) @ steps + origin
        mesh = bpy.data.meshes.new('QC slice carrier')
        obj = bpy.data.objects.new('QC scalar slice', mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = source.parent
        bind(obj, bpy.path.abspath(source['qc_dataset']), data)
        obj['qc_field'] = source['qc_field']
        obj['qc_view_kind'] = 'slice'
        tree = bpy.data.node_groups.new('QC Slice v1', 'GeometryNodeTree')
        socket(tree, 'Center', 'NodeSocketVector', default=tuple(corners.mean(axis=0)))
        socket(tree, 'Rotation', 'NodeSocketVector', default=(0, 0, 0))
        socket(tree, 'Width', 'NodeSocketFloat', default=float(np.ptp(corners[:, 0])), minimum=.001)
        socket(tree, 'Height', 'NodeSocketFloat', default=float(np.ptp(corners[:, 1])), minimum=.001)
        socket(tree, 'Resolution', 'NodeSocketInt', default=self.resolution, minimum=2)
        socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
        nodes, links = tree.nodes, tree.links
        inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
        grid = nodes.new('GeometryNodeMeshGrid')
        links.new(inputs.outputs['Width'], grid.inputs['Size X'])
        links.new(inputs.outputs['Height'], grid.inputs['Size Y'])
        links.new(inputs.outputs['Resolution'], grid.inputs['Vertices X'])
        links.new(inputs.outputs['Resolution'], grid.inputs['Vertices Y'])
        transform = nodes.new('GeometryNodeTransform')
        links.new(grid.outputs['Mesh'], transform.inputs['Geometry'])
        links.new(inputs.outputs['Center'], transform.inputs['Translation'])
        links.new(inputs.outputs['Rotation'], transform.inputs['Rotation'])
        links.new(transform.outputs['Geometry'], output.inputs['Geometry'])
        obj.modifiers.new('QC Slice', 'NODES').node_group = tree
        try:
            add_mapping(obj, source, self.minimum, self.maximum)
        except (ValueError, OSError, KeyError) as error:
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
            bpy.data.node_groups.remove(tree)
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        return {'FINISHED'}
