"""Editable geometry node views of normalized scientific data."""
import json
import hashlib
from pathlib import Path

import bpy
import numpy as np

from ..data import load_dataset, volume_cache


def socket(tree, name, kind, direction='INPUT', default=None, minimum=None):
    result = tree.interface.new_socket(name=name, in_out=direction, socket_type=kind)
    if default is not None:
        result.default_value = default
    if minimum is not None:
        result.min_value = minimum
    return result


def material(name, color, attribute=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = 0.35
    if attribute:
        node = mat.node_tree.nodes.new('ShaderNodeAttribute')
        node.attribute_name = attribute
        mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
    return mat


def bind(obj, directory, data):
    obj['qc_dataset'] = str(Path(directory).resolve())
    obj['qc_dataset_sha256'] = hashlib.sha256((Path(directory) / 'manifest.json').read_bytes()).hexdigest()
    obj['qc_source_sha256'] = data.metadata['source']['sha256']
    obj['qc_schema'] = '0.1'
    obj['qc_coordinate_unit'] = 'angstrom'
    obj['qc_diagnostics'] = json.dumps(data.metadata.get('diagnostics', []))


def atom_view(directory):
    data = load_dataset(directory)
    title = data.metadata.get('title') or data.metadata['source']['filename']
    mesh = bpy.data.meshes.new('QC atoms')
    positions = data.arrays['positions']
    edges = data.arrays.get('bonds', np.empty((0, 2), dtype=np.int32))
    mesh.from_pydata(positions.tolist(), edges.tolist(), [])
    mesh.update()
    obj = bpy.data.objects.new(title, mesh)
    bpy.context.collection.objects.link(obj)
    bind(obj, directory, data)
    for name, values in [('qc_atom_id', np.arange(len(positions))),
                         ('qc_atomic_number', data.arrays['atomic_numbers'])]:
        attr = mesh.attributes.new(name, 'INT', 'POINT')
        attr.data.foreach_set('value', values)
    positions_attr = mesh.attributes.new('qc_equilibrium_position', 'FLOAT_VECTOR', 'POINT')
    positions_attr.data.foreach_set('vector', positions.ravel())
    colors = {1: (0.85, 0.85, 0.85, 1), 6: (0.12, 0.16, 0.20, 1), 7: (0.12, 0.22, 0.8, 1),
              8: (0.85, 0.08, 0.06, 1), 9: (0.1, 0.65, 0.15, 1), 15: (1., 0.4, 0.05, 1),
              16: (0.9, 0.7, 0.05, 1), 17: (0.1, 0.65, 0.15, 1)}
    attr = mesh.color_attributes.new('qc_element_color', 'FLOAT_COLOR', 'POINT')
    attr.data.foreach_set('color', np.array([colors.get(int(z), (0.45, 0.35, 0.6, 1))
                                           for z in data.arrays['atomic_numbers']]).ravel())
    if data.metadata.get('charges'):
        prop = data.metadata['charges'][0]
        attr = mesh.attributes.new('qc_charge', 'FLOAT', 'POINT')
        attr.data.foreach_set('value', data.arrays[prop['array']])
        valid = mesh.attributes.new('qc_charge_valid', 'BOOLEAN', 'POINT')
        valid.data.foreach_set('value', [True] * len(positions))
        obj['qc_charge_method'] = prop['method']
    bond_source = mesh.attributes.new('qc_bond_source', 'INT', 'EDGE')
    bond_source.data.foreach_set('value', np.ones(len(edges), dtype=np.int32))
    tree = bpy.data.node_groups.new('QC Style Atoms and Bonds v1', 'GeometryNodeTree')
    tree.is_modifier = True
    socket(tree, 'Geometry', 'NodeSocketGeometry')
    socket(tree, 'Atom Radius', 'NodeSocketFloat', default=0.25, minimum=0.001)
    socket(tree, 'Bond Radius', 'NodeSocketFloat', default=0.07, minimum=0.001)
    socket(tree, 'Selection', 'NodeSocketBool', default=True)
    socket(tree, 'Element (0 = all)', 'NodeSocketInt', default=0, minimum=0)
    socket(tree, 'First Atom (1-based)', 'NodeSocketInt', default=1, minimum=1)
    socket(tree, 'Last Atom (0 = all)', 'NodeSocketInt', default=0, minimum=0)
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    nodes, links = tree.nodes, tree.links
    inputs = nodes.new('NodeGroupInput')
    output = nodes.new('NodeGroupOutput')
    selected = atom_selection(tree, inputs)
    invert = nodes.new('FunctionNodeBooleanMath')
    invert.operation = 'NOT'
    links.new(selected, invert.inputs[0])
    delete = nodes.new('GeometryNodeDeleteGeometry')
    delete.domain = 'POINT'
    links.new(inputs.outputs['Geometry'], delete.inputs['Geometry'])
    links.new(invert.outputs[0], delete.inputs['Selection'])
    sphere = nodes.new('GeometryNodeMeshIcoSphere')
    sphere.inputs['Subdivisions'].default_value = 2
    links.new(inputs.outputs['Atom Radius'], sphere.inputs['Radius'])
    instances = nodes.new('GeometryNodeInstanceOnPoints')
    links.new(delete.outputs['Geometry'], instances.inputs['Points'])
    links.new(sphere.outputs['Mesh'], instances.inputs['Instance'])
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(instances.outputs['Instances'], realize.inputs['Geometry'])
    curves = nodes.new('GeometryNodeMeshToCurve')
    links.new(delete.outputs['Geometry'], curves.inputs['Mesh'])
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle.inputs['Resolution'].default_value = 8
    links.new(inputs.outputs['Bond Radius'], circle.inputs['Radius'])
    tubes = nodes.new('GeometryNodeCurveToMesh')
    links.new(curves.outputs['Curve'], tubes.inputs['Curve'])
    links.new(circle.outputs['Curve'], tubes.inputs['Profile Curve'])
    join = nodes.new('GeometryNodeJoinGeometry')
    links.new(realize.outputs['Geometry'], join.inputs['Geometry'])
    links.new(tubes.outputs['Mesh'], join.inputs['Geometry'])
    mat = material('QC Elements', (0.35, 0.35, 0.35, 1), 'qc_element_color')
    smooth = nodes.new('GeometryNodeSetShadeSmooth')
    links.new(join.outputs['Geometry'], smooth.inputs['Geometry'])
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = mat
    links.new(smooth.outputs['Geometry'], assign.inputs['Geometry'])
    links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    for index, node in enumerate(nodes):
        node.location = (index % 4 * 220, -(index // 4) * 240)
    obj.modifiers.new('QC Atoms and Bonds', 'NODES').node_group = tree
    tree.asset_mark()
    from .properties import setup_properties
    setup_properties(obj, data)
    obj['qc_view_kind'] = 'atoms'
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def atom_selection(tree, inputs):
    nodes, links = tree.nodes, tree.links

    def math_node(operation, first, second):
        node = nodes.new('ShaderNodeMath')
        node.operation = operation
        for index, value in enumerate((first, second)):
            if isinstance(value, (int, float)):
                node.inputs[index].default_value = value
            else:
                links.new(value, node.inputs[index])
        return node.outputs[0]

    atomic_number = nodes.new('GeometryNodeInputNamedAttribute')
    atomic_number.data_type = 'INT'
    atomic_number.inputs['Name'].default_value = 'qc_atomic_number'
    atom_id = nodes.new('GeometryNodeInputNamedAttribute')
    atom_id.data_type = 'INT'
    atom_id.inputs['Name'].default_value = 'qc_atom_id'
    source_number = math_node('ADD', atom_id.outputs['Attribute'], 1)
    element = inputs.outputs['Element (0 = all)']
    last = inputs.outputs['Last Atom (0 = all)']
    matches_element = math_node('MAXIMUM', math_node('COMPARE', element, 0),
                                math_node('COMPARE', atomic_number.outputs['Attribute'], element))
    after_first = math_node('SUBTRACT', 1, math_node('LESS_THAN', source_number, inputs.outputs['First Atom (1-based)']))
    before_last = math_node('MAXIMUM', math_node('COMPARE', last, 0),
                            math_node('SUBTRACT', 1, math_node('GREATER_THAN', source_number, last)))
    return math_node('MULTIPLY', inputs.outputs['Selection'],
                     math_node('MULTIPLY', matches_element, math_node('MULTIPLY', after_first, before_last)))


def field_view(directory, parent=None, index=0):
    data = load_dataset(directory)
    field = data.metadata['fields'][index]
    cache = volume_cache(directory, field)
    volume = bpy.data.volumes.new('QC field data')
    volume.filepath = str(cache)
    source = bpy.data.objects.new('QC ' + field['quantity'] + ' source', volume)
    bpy.context.collection.objects.link(source)
    bind(source, directory, data)
    source['qc_view_kind'] = 'volume'
    source['qc_field'] = json.dumps(field)
    source.hide_render = True
    source.hide_set(True)
    mesh = bpy.data.meshes.new('QC surface carrier')
    obj = bpy.data.objects.new('QC ' + field['quantity'], mesh)
    bpy.context.collection.objects.link(obj)
    bind(obj, directory, data)
    obj['qc_field'] = json.dumps(field)
    obj['qc_view_kind'] = 'field'
    obj.qc_settings.volume = source
    if parent:
        obj.parent = parent
        source.parent = parent
    tree = bpy.data.node_groups.new('QC Isosurface v1', 'GeometryNodeTree')
    tree.is_modifier = True
    threshold = 0.05 if field['quantity'] in ('orbital_amplitude', 'spin_density') else 0.02
    socket(tree, 'Isovalue', 'NodeSocketFloat', default=threshold, minimum=1e-7)
    signed = field['quantity'] in ('orbital_amplitude', 'spin_density', 'unknown_scalar', 'electrostatic_potential')
    socket(tree, 'Positive Phase', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Phase', 'NodeSocketBool', default=signed)
    socket(tree, 'Adaptivity', 'NodeSocketFloat', default=0, minimum=0)
    socket(tree, 'Smooth Normals', 'NodeSocketBool', default=True)
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    info = nodes.new('GeometryNodeObjectInfo')
    info.transform_space = 'RELATIVE'
    info.inputs['Object'].default_value = source
    style = nodes.new('GeometryNodeGroup')
    style.node_tree = isosurface_group()
    links.new(info.outputs['Geometry'], style.inputs['Volume'])
    for name in ('Isovalue', 'Positive Phase', 'Negative Phase', 'Adaptivity', 'Smooth Normals'):
        links.new(inputs.outputs[name], style.inputs[name])
    for label, color in [('Positive', (0.1, 0.3, 0.8, 1)), ('Negative', (0.85, 0.12, 0.08, 1))]:
        name = label + ' Material'
        socket(tree, name, 'NodeSocketMaterial', default=material('QC ' + label + ' Phase', color))
        links.new(inputs.outputs[name], style.inputs[name])
    links.new(style.outputs['Geometry'], output.inputs['Geometry'])
    for number, node in enumerate(nodes):
        node.location = (number * 240, 0)
    obj.modifiers.new('QC Isosurface', 'NODES').node_group = tree
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def isosurface_group():
    """Reusable signed isosurfaces of QC grids; bindings belong to the caller."""
    asset_id = 'qc.isosurface.v1'
    existing = next((group for group in bpy.data.node_groups
                     if group.bl_idname == 'GeometryNodeTree' and group.get('qc_asset_id') == asset_id), None)
    if existing is not None:
        return existing
    tree = bpy.data.node_groups.new('QC Style Isosurface v1', 'GeometryNodeTree')
    tree['qc_asset_id'] = asset_id
    socket(tree, 'Volume', 'NodeSocketGeometry')
    socket(tree, 'Isovalue', 'NodeSocketFloat', default=.05, minimum=1e-7)
    socket(tree, 'Positive Phase', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Phase', 'NodeSocketBool', default=True)
    socket(tree, 'Adaptivity', 'NodeSocketFloat', default=0, minimum=0)
    socket(tree, 'Smooth Normals', 'NodeSocketBool', default=True)
    socket(tree, 'Positive Material', 'NodeSocketMaterial')
    socket(tree, 'Negative Material', 'NodeSocketMaterial')
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    join = nodes.new('GeometryNodeJoinGeometry')
    smooth = nodes.new('GeometryNodeSetShadeSmooth')
    links.new(join.outputs['Geometry'], smooth.inputs['Geometry'])
    links.new(inputs.outputs['Smooth Normals'], smooth.inputs['Shade Smooth'])
    links.new(smooth.outputs['Geometry'], output.inputs['Geometry'])
    valid_grid = nodes.new('GeometryNodeGetNamedGrid')
    valid_grid.inputs['Name'].default_value = 'qc_valid'
    links.new(inputs.outputs['Volume'], valid_grid.inputs['Volume'])
    sample = nodes.new('GeometryNodeSampleGrid')
    sample.inputs['Interpolation'].default_value = 'Trilinear'
    links.new(valid_grid.outputs['Grid'], sample.inputs['Grid'])
    position = nodes.new('GeometryNodeInputPosition')
    links.new(position.outputs['Position'], sample.inputs['Position'])
    invalid = nodes.new('ShaderNodeMath')
    invalid.operation = 'LESS_THAN'
    invalid.inputs[1].default_value = 0.999999
    links.new(sample.outputs['Value'], invalid.inputs[0])
    for label, name in [('Positive Phase', 'qc_value'), ('Negative Phase', 'qc_negative')]:
        grid = nodes.new('GeometryNodeGetNamedGrid')
        grid.inputs['Name'].default_value = name
        links.new(inputs.outputs['Volume'], grid.inputs['Volume'])
        surface = nodes.new('GeometryNodeGridToMesh')
        links.new(grid.outputs['Grid'], surface.inputs['Grid'])
        links.new(inputs.outputs['Isovalue'], surface.inputs['Threshold'])
        links.new(inputs.outputs['Adaptivity'], surface.inputs['Adaptivity'])
        delete = nodes.new('GeometryNodeDeleteGeometry')
        delete.domain = 'POINT'
        links.new(surface.outputs['Mesh'], delete.inputs['Geometry'])
        links.new(invalid.outputs[0], delete.inputs['Selection'])
        assign = nodes.new('GeometryNodeSetMaterial')
        links.new(inputs.outputs[label.replace('Phase', 'Material')], assign.inputs['Material'])
        links.new(delete.outputs['Geometry'], assign.inputs['Geometry'])
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(inputs.outputs[label], switch.inputs['Switch'])
        links.new(assign.outputs['Geometry'], switch.inputs['True'])
        links.new(switch.outputs['Output'], join.inputs['Geometry'])
    for index, node in enumerate(nodes):
        node.location = (index % 5 * 220, -(index // 5) * 240)
    tree.asset_mark()
    tree.asset_data.description = 'Signed QC scalar isosurfaces with validity mask; input coordinates in angstrom'
    return tree
