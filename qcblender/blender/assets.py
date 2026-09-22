"""Unbound, composable geometry assets. All coordinates are in angstrom."""
import bpy

from .views import socket
from .graph import arrange


def asset(key, title, inputs, outputs=(('Geometry', 'NodeSocketGeometry'),)):
    existing = next((g for g in bpy.data.node_groups if g.get('qc_asset_id') == key), None)
    if existing:
        return existing, None, None
    tree = bpy.data.node_groups.new(title, 'GeometryNodeTree')
    tree['qc_asset_id'] = key
    for name, kind, default in inputs:
        socket(tree, name, kind, default=default)
    for name, kind in outputs:
        socket(tree, name, kind, 'OUTPUT')
    tree.asset_mark()
    tree.asset_data.description = title + '; source data remains unchanged; coordinates in angstrom'
    return tree, tree.nodes.new('NodeGroupInput'), tree.nodes.new('NodeGroupOutput')


def math(tree, operation, *values):
    node = tree.nodes.new('ShaderNodeMath')
    node.operation = operation
    for index, value in enumerate(values):
        if isinstance(value, (int, float)):
            node.inputs[index].default_value = value
        else:
            tree.links.new(value, node.inputs[index])
    return node.outputs[0]


def sample_group():
    tree, source, output = asset('qc.sample.v1', 'QC Sample Scalar Field', [
        ('Volume', 'NodeSocketGeometry', None), ('Position', 'NodeSocketVector', (0, 0, 0))],
        [('Value', 'NodeSocketFloat'), ('Valid', 'NodeSocketBool')])
    if source is None:
        return tree
    for grid_name, target in [('qc_value', 'Value'), ('qc_valid', 'Valid')]:
        grid = tree.nodes.new('GeometryNodeGetNamedGrid')
        grid.inputs['Name'].default_value = grid_name
        tree.links.new(source.outputs['Volume'], grid.inputs['Volume'])
        sample = tree.nodes.new('GeometryNodeSampleGrid')
        sample.inputs['Interpolation'].default_value = 'Trilinear'
        tree.links.new(grid.outputs['Grid'], sample.inputs['Grid'])
        tree.links.new(source.outputs['Position'], sample.inputs['Position'])
        value = sample.outputs['Value']
        if target == 'Valid':
            value = math(tree, 'GREATER_THAN', value, .999999)
        tree.links.new(value, output.inputs[target])
    return arrange(tree)


def selection_group():
    from .views import atom_selection
    tree, source, output = asset('qc.atom_selection.v1', 'QC Select Atoms', [
        ('Selection', 'NodeSocketBool', True), ('Element (0 = all)', 'NodeSocketInt', 0),
        ('First Atom (1-based)', 'NodeSocketInt', 1), ('Last Atom (0 = all)', 'NodeSocketInt', 0)],
        [('Selection', 'NodeSocketBool')])
    if source is not None:
        tree.links.new(atom_selection(tree, source), output.inputs['Selection'])
        arrange(tree)
    return tree


def surface_style_group():
    tree, source, output = asset('qc.surface_style.v1', 'QC Surface Representation', [
        ('Geometry', 'NodeSocketGeometry', None), ('Style (0 solid, 1 wire, 2 points)', 'NodeSocketInt', 0),
        ('Wire Radius', 'NodeSocketFloat', .012), ('Point Radius', 'NodeSocketFloat', .025),
        ('Quality', 'NodeSocketInt', 2)])
    if source is None:
        return tree
    nodes, links = tree.nodes, tree.links
    curves = nodes.new('GeometryNodeMeshToCurve')
    links.new(source.outputs['Geometry'], curves.inputs['Mesh'])
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle.inputs['Resolution'].default_value = 8
    links.new(source.outputs['Wire Radius'], circle.inputs['Radius'])
    tubes = nodes.new('GeometryNodeCurveToMesh')
    links.new(curves.outputs['Curve'], tubes.inputs['Curve'])
    links.new(circle.outputs['Curve'], tubes.inputs['Profile Curve'])
    sphere = nodes.new('GeometryNodeMeshIcoSphere')
    links.new(source.outputs['Point Radius'], sphere.inputs['Radius'])
    links.new(source.outputs['Quality'], sphere.inputs['Subdivisions'])
    instance = nodes.new('GeometryNodeInstanceOnPoints')
    links.new(source.outputs['Geometry'], instance.inputs['Points'])
    links.new(sphere.outputs['Mesh'], instance.inputs['Instance'])
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    geometry = source.outputs['Geometry']
    for number, alternative in [(1, tubes.outputs['Mesh']), (2, realize.outputs['Geometry'])]:
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(math(tree, 'COMPARE', source.outputs['Style (0 solid, 1 wire, 2 points)'], number), switch.inputs['Switch'])
        links.new(geometry, switch.inputs['False'])
        links.new(alternative, switch.inputs['True'])
        geometry = switch.outputs['Output']
    links.new(geometry, output.inputs['Geometry'])
    return arrange(tree)


def atom_style_group():
    tree, source, output = asset('qc.atom_style.v1', 'QC Style Atoms and Bonds', [
        ('Geometry', 'NodeSocketGeometry', None), ('Selection', 'NodeSocketBool', True),
        ('Style (0 ball-stick, 1 space-fill, 2 bonds)', 'NodeSocketInt', 0),
        ('Atom Radius', 'NodeSocketFloat', .25), ('Bond Radius', 'NodeSocketFloat', .07),
        ('VDW Scale', 'NodeSocketFloat', 1.), ('Quality', 'NodeSocketInt', 2),
        ('Material', 'NodeSocketMaterial', None)])
    if source is None:
        return tree
    nodes, links = tree.nodes, tree.links
    delete = nodes.new('GeometryNodeDeleteGeometry')
    delete.domain = 'POINT'
    links.new(source.outputs['Geometry'], delete.inputs['Geometry'])
    links.new(math(tree, 'SUBTRACT', 1, source.outputs['Selection']), delete.inputs['Selection'])
    sphere = nodes.new('GeometryNodeMeshIcoSphere')
    sphere.inputs['Radius'].default_value = 1
    links.new(source.outputs['Quality'], sphere.inputs['Subdivisions'])
    radius = nodes.new('GeometryNodeInputNamedAttribute')
    radius.data_type = 'FLOAT'
    radius.inputs['Name'].default_value = 'qc_vdw_radius'
    choose_radius = nodes.new('GeometryNodeSwitch')
    choose_radius.input_type = 'FLOAT'
    space = math(tree, 'COMPARE', source.outputs['Style (0 ball-stick, 1 space-fill, 2 bonds)'], 1)
    links.new(space, choose_radius.inputs['Switch'])
    links.new(source.outputs['Atom Radius'], choose_radius.inputs['False'])
    links.new(math(tree, 'MULTIPLY', radius.outputs['Attribute'], source.outputs['VDW Scale']), choose_radius.inputs['True'])
    instance = nodes.new('GeometryNodeInstanceOnPoints')
    links.new(delete.outputs['Geometry'], instance.inputs['Points'])
    links.new(sphere.outputs['Mesh'], instance.inputs['Instance'])
    links.new(choose_radius.outputs['Output'], instance.inputs['Scale'])
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    curves = nodes.new('GeometryNodeMeshToCurve')
    links.new(delete.outputs['Geometry'], curves.inputs['Mesh'])
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle.inputs['Resolution'].default_value = 8
    links.new(source.outputs['Bond Radius'], circle.inputs['Radius'])
    tubes = nodes.new('GeometryNodeCurveToMesh')
    links.new(curves.outputs['Curve'], tubes.inputs['Curve'])
    links.new(circle.outputs['Curve'], tubes.inputs['Profile Curve'])
    join = nodes.new('GeometryNodeJoinGeometry')
    for geometry, hidden in [(realize.outputs['Geometry'], math(tree, 'COMPARE', source.outputs['Style (0 ball-stick, 1 space-fill, 2 bonds)'], 2)),
                             (tubes.outputs['Mesh'], space)]:
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(hidden, switch.inputs['Switch'])
        links.new(geometry, switch.inputs['False'])
        links.new(switch.outputs['Output'], join.inputs['Geometry'])
    smooth = nodes.new('GeometryNodeSetShadeSmooth')
    links.new(join.outputs['Geometry'], smooth.inputs['Geometry'])
    assign = nodes.new('GeometryNodeSetMaterial')
    links.new(smooth.outputs['Geometry'], assign.inputs['Geometry'])
    links.new(source.outputs['Material'], assign.inputs['Material'])
    links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    return arrange(tree)


def slice_group():
    tree, source, output = asset('qc.slice.v1', 'QC Planar Slice', [
        ('Center', 'NodeSocketVector', (0, 0, 0)), ('Rotation', 'NodeSocketVector', (0, 0, 0)),
        ('Width', 'NodeSocketFloat', 6.), ('Height', 'NodeSocketFloat', 6.),
        ('Resolution', 'NodeSocketInt', 101)])
    if source is None:
        return tree
    grid = tree.nodes.new('GeometryNodeMeshGrid')
    for name, target in [('Width', 'Size X'), ('Height', 'Size Y'), ('Resolution', 'Vertices X'), ('Resolution', 'Vertices Y')]:
        tree.links.new(source.outputs[name], grid.inputs[target])
    transform = tree.nodes.new('GeometryNodeTransform')
    tree.links.new(grid.outputs['Mesh'], transform.inputs['Geometry'])
    tree.links.new(source.outputs['Center'], transform.inputs['Translation'])
    tree.links.new(source.outputs['Rotation'], transform.inputs['Rotation'])
    tree.links.new(transform.outputs['Geometry'], output.inputs['Geometry'])
    return arrange(tree)


def color_group():
    from .scalars import color_fraction
    tree, source, output = asset('qc.color_scalar.v2', 'QC Map Scalar Colors v2', [
        ('Geometry', 'NodeSocketGeometry', None), ('Value', 'NodeSocketFloat', 0.),
        ('Valid', 'NodeSocketBool', True), ('Color Minimum', 'NodeSocketFloat', -.05),
        ('Color Center', 'NodeSocketFloat', 0.), ('Color Maximum', 'NodeSocketFloat', .05),
        ('Material', 'NodeSocketMaterial', None)])
    if source is None:
        return tree
    fraction = color_fraction(tree, source, source.outputs['Value'], 'Color Minimum', 'Color Center', 'Color Maximum')
    opacity = tree.nodes.new('GeometryNodeInputNamedAttribute')
    opacity.data_type = 'FLOAT'
    opacity.inputs['Name'].default_value = 'qc_opacity'
    alpha = tree.nodes.new('GeometryNodeSwitch')
    alpha.input_type = 'FLOAT'
    alpha.inputs['False'].default_value = 1.
    tree.links.new(opacity.outputs['Exists'], alpha.inputs['Switch'])
    tree.links.new(opacity.outputs['Attribute'], alpha.inputs['True'])
    geometry = source.outputs['Geometry']
    for name, kind, value in [('qc_scalar_value', 'FLOAT', source.outputs['Value']),
                              ('qc_sample_valid', 'BOOLEAN', source.outputs['Valid']),
                              ('qc_color_fraction', 'FLOAT', fraction), ('qc_opacity', 'FLOAT', alpha.outputs['Output'])]:
        store = tree.nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        store.inputs['Name'].default_value = name
        tree.links.new(geometry, store.inputs['Geometry'])
        tree.links.new(value, store.inputs['Value'])
        geometry = store.outputs['Geometry']
    assign = tree.nodes.new('GeometryNodeSetMaterial')
    tree.links.new(source.outputs['Material'], assign.inputs['Material'])
    tree.links.new(geometry, assign.inputs['Geometry'])
    tree.links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    return arrange(tree)
