"""Unbound, composable geometry assets. All coordinates are in angstrom."""

from .node_identity import node_socket, socket_name
import bpy

from .views import group_sockets, socket
from .graph import arrange


PANELS = {
    'qc.sample.v1': (('Source', ('Volume',)), ('Sampling', ('Position',))),
    'qc.atom_selection.v1': (('Selection', ('Selection', 'Element (0 = all)',
                                          'First Atom (1-based)', 'Last Atom (0 = all)')),),
    'qc.surface_style.v1': (('Source', ('Geometry',)),
                            ('Representation', ('Style (0 solid, 1 wire, 2 points)',
                                                'Wire Radius', 'Point Radius', 'Quality'))),
    'qc.atom_style.v1': (('Source', ('Geometry', 'Selection')),
                         ('Representation', ('Style (0 ball-stick, 1 space-fill, 2 bonds)',
                                             'Atom Radius', 'Bond Radius', 'VDW Scale', 'Quality')),
                         ('Material', ('Material',))),
    'qc.slice.v1': (('Placement', ('Center', 'Rotation')),
                   ('Grid', ('Width', 'Height', 'Resolution'))),
    'qc.color_scalar.v2': (('Source', ('Geometry', 'Value', 'Valid')),
                           ('Range', ('Color Minimum', 'Color Center', 'Color Maximum')),
                           ('Material', ('Material',))),
    'qc.clip.v1': (('Source', ('Geometry',)),
                   ('Plane', ('Plane Enabled', 'Plane Origin', 'Plane Normal')),
                   ('Box', ('Box Enabled', 'Box Minimum', 'Box Maximum'))),
}


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
    group_sockets(tree, PANELS[key])
    return tree, tree.nodes.new('NodeGroupInput'), tree.nodes.new('NodeGroupOutput')


def math(tree, operation, *values):
    node = tree.nodes.new('ShaderNodeMath')
    node.operation = operation
    for index, value in enumerate(values):
        if isinstance(value, (int, float)):
            node_socket(node.inputs, index).default_value = value
        else:
            tree.links.new(value, node_socket(node.inputs, index))
    return node.outputs[0]


def sample_group():
    tree, source, output = asset('qc.sample.v1', 'QC Sample Scalar Field', [
        ('Volume', 'NodeSocketGeometry', None), ('Position', 'NodeSocketVector', (0, 0, 0))],
        [('Value', 'NodeSocketFloat'), ('Valid', 'NodeSocketBool')])
    if source is None:
        return tree
    for grid_name, target in [('qc_value', 'Value'), ('qc_valid', 'Valid')]:
        grid = tree.nodes.new('GeometryNodeGetNamedGrid')
        node_socket(grid.inputs, 'Name').default_value = grid_name
        tree.links.new(node_socket(source.outputs, 'Volume'), node_socket(grid.inputs, 'Volume'))
        sample = tree.nodes.new('GeometryNodeSampleGrid')
        node_socket(sample.inputs, 'Interpolation').default_value = 'Trilinear'
        tree.links.new(node_socket(grid.outputs, 'Grid'), node_socket(sample.inputs, 'Grid'))
        tree.links.new(node_socket(source.outputs, 'Position'), node_socket(sample.inputs, 'Position'))
        value = node_socket(sample.outputs, 'Value')
        if target == 'Valid':
            value = math(tree, 'GREATER_THAN', value, .999999)
        tree.links.new(value, node_socket(output.inputs, target))
    return arrange(tree)


def selection_group():
    from .views import atom_selection
    tree, source, output = asset('qc.atom_selection.v1', 'QC Select Atoms', [
        ('Selection', 'NodeSocketBool', True), ('Element (0 = all)', 'NodeSocketInt', 0),
        ('First Atom (1-based)', 'NodeSocketInt', 1), ('Last Atom (0 = all)', 'NodeSocketInt', 0)],
        [('Selection', 'NodeSocketBool')])
    if source is not None:
        tree.links.new(atom_selection(tree, source), node_socket(output.inputs, 'Selection'))
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
    links.new(node_socket(source.outputs, 'Geometry'), node_socket(curves.inputs, 'Mesh'))
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    node_socket(circle.inputs, 'Resolution').default_value = 8
    links.new(node_socket(source.outputs, 'Wire Radius'), node_socket(circle.inputs, 'Radius'))
    tubes = nodes.new('GeometryNodeCurveToMesh')
    links.new(node_socket(curves.outputs, 'Curve'), node_socket(tubes.inputs, 'Curve'))
    links.new(node_socket(circle.outputs, 'Curve'), node_socket(tubes.inputs, 'Profile Curve'))
    sphere = nodes.new('GeometryNodeMeshIcoSphere')
    links.new(node_socket(source.outputs, 'Point Radius'), node_socket(sphere.inputs, 'Radius'))
    links.new(node_socket(source.outputs, 'Quality'), node_socket(sphere.inputs, 'Subdivisions'))
    instance = nodes.new('GeometryNodeInstanceOnPoints')
    links.new(node_socket(source.outputs, 'Geometry'), node_socket(instance.inputs, 'Points'))
    links.new(node_socket(sphere.outputs, 'Mesh'), node_socket(instance.inputs, 'Instance'))
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(node_socket(instance.outputs, 'Instances'), node_socket(realize.inputs, 'Geometry'))
    geometry = node_socket(source.outputs, 'Geometry')
    for number, alternative in [(1, node_socket(tubes.outputs, 'Mesh')), (2, node_socket(realize.outputs, 'Geometry'))]:
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(math(tree, 'COMPARE', node_socket(source.outputs, 'Style (0 solid, 1 wire, 2 points)'), number), node_socket(switch.inputs, 'Switch'))
        links.new(geometry, node_socket(switch.inputs, 'False'))
        links.new(alternative, node_socket(switch.inputs, 'True'))
        geometry = node_socket(switch.outputs, 'Output')
    links.new(geometry, node_socket(output.inputs, 'Geometry'))
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
    links.new(node_socket(source.outputs, 'Geometry'), node_socket(delete.inputs, 'Geometry'))
    links.new(math(tree, 'SUBTRACT', 1, node_socket(source.outputs, 'Selection')), node_socket(delete.inputs, 'Selection'))
    sphere = nodes.new('GeometryNodeMeshIcoSphere')
    node_socket(sphere.inputs, 'Radius').default_value = 1
    links.new(node_socket(source.outputs, 'Quality'), node_socket(sphere.inputs, 'Subdivisions'))
    radius = nodes.new('GeometryNodeInputNamedAttribute')
    radius.data_type = 'FLOAT'
    node_socket(radius.inputs, 'Name').default_value = 'qc_vdw_radius'
    choose_radius = nodes.new('GeometryNodeSwitch')
    choose_radius.input_type = 'FLOAT'
    space = math(tree, 'COMPARE', node_socket(source.outputs, 'Style (0 ball-stick, 1 space-fill, 2 bonds)'), 1)
    links.new(space, node_socket(choose_radius.inputs, 'Switch'))
    links.new(node_socket(source.outputs, 'Atom Radius'), node_socket(choose_radius.inputs, 'False'))
    links.new(math(tree, 'MULTIPLY', node_socket(radius.outputs, 'Attribute'), node_socket(source.outputs, 'VDW Scale')), node_socket(choose_radius.inputs, 'True'))
    instance = nodes.new('GeometryNodeInstanceOnPoints')
    links.new(node_socket(delete.outputs, 'Geometry'), node_socket(instance.inputs, 'Points'))
    links.new(node_socket(sphere.outputs, 'Mesh'), node_socket(instance.inputs, 'Instance'))
    links.new(node_socket(choose_radius.outputs, 'Output'), node_socket(instance.inputs, 'Scale'))
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(node_socket(instance.outputs, 'Instances'), node_socket(realize.inputs, 'Geometry'))
    curves = nodes.new('GeometryNodeMeshToCurve')
    links.new(node_socket(delete.outputs, 'Geometry'), node_socket(curves.inputs, 'Mesh'))
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    node_socket(circle.inputs, 'Resolution').default_value = 8
    links.new(node_socket(source.outputs, 'Bond Radius'), node_socket(circle.inputs, 'Radius'))
    tubes = nodes.new('GeometryNodeCurveToMesh')
    links.new(node_socket(curves.outputs, 'Curve'), node_socket(tubes.inputs, 'Curve'))
    links.new(node_socket(circle.outputs, 'Curve'), node_socket(tubes.inputs, 'Profile Curve'))
    join = nodes.new('GeometryNodeJoinGeometry')
    for geometry, hidden in [(node_socket(realize.outputs, 'Geometry'), math(tree, 'COMPARE', node_socket(source.outputs, 'Style (0 ball-stick, 1 space-fill, 2 bonds)'), 2)),
                             (node_socket(tubes.outputs, 'Mesh'), space)]:
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(hidden, node_socket(switch.inputs, 'Switch'))
        links.new(geometry, node_socket(switch.inputs, 'False'))
        links.new(node_socket(switch.outputs, 'Output'), node_socket(join.inputs, 'Geometry'))
    smooth = nodes.new('GeometryNodeSetShadeSmooth')
    links.new(node_socket(join.outputs, 'Geometry'), node_socket(smooth.inputs, 'Geometry'))
    assign = nodes.new('GeometryNodeSetMaterial')
    links.new(node_socket(smooth.outputs, 'Geometry'), node_socket(assign.inputs, 'Geometry'))
    links.new(node_socket(source.outputs, 'Material'), node_socket(assign.inputs, 'Material'))
    links.new(node_socket(assign.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
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
        tree.links.new(node_socket(source.outputs, name), node_socket(grid.inputs, target))
    transform = tree.nodes.new('GeometryNodeTransform')
    tree.links.new(node_socket(grid.outputs, 'Mesh'), node_socket(transform.inputs, 'Geometry'))
    tree.links.new(node_socket(source.outputs, 'Center'), node_socket(transform.inputs, 'Translation'))
    tree.links.new(node_socket(source.outputs, 'Rotation'), node_socket(transform.inputs, 'Rotation'))
    tree.links.new(node_socket(transform.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
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
    fraction = color_fraction(tree, source, node_socket(source.outputs, 'Value'), 'Color Minimum', 'Color Center', 'Color Maximum')
    opacity = tree.nodes.new('GeometryNodeInputNamedAttribute')
    opacity.data_type = 'FLOAT'
    node_socket(opacity.inputs, 'Name').default_value = 'qc_opacity'
    alpha = tree.nodes.new('GeometryNodeSwitch')
    alpha.input_type = 'FLOAT'
    node_socket(alpha.inputs, 'False').default_value = 1.
    tree.links.new(node_socket(opacity.outputs, 'Exists'), node_socket(alpha.inputs, 'Switch'))
    tree.links.new(node_socket(opacity.outputs, 'Attribute'), node_socket(alpha.inputs, 'True'))
    geometry = node_socket(source.outputs, 'Geometry')
    for name, kind, value in [('qc_scalar_value', 'FLOAT', node_socket(source.outputs, 'Value')),
                              ('qc_sample_valid', 'BOOLEAN', node_socket(source.outputs, 'Valid')),
                              ('qc_color_fraction', 'FLOAT', fraction), ('qc_opacity', 'FLOAT', node_socket(alpha.outputs, 'Output'))]:
        store = tree.nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        node_socket(store.inputs, 'Name').default_value = name
        tree.links.new(geometry, node_socket(store.inputs, 'Geometry'))
        tree.links.new(value, node_socket(store.inputs, 'Value'))
        geometry = node_socket(store.outputs, 'Geometry')
    assign = tree.nodes.new('GeometryNodeSetMaterial')
    tree.links.new(node_socket(source.outputs, 'Material'), node_socket(assign.inputs, 'Material'))
    tree.links.new(geometry, node_socket(assign.inputs, 'Geometry'))
    tree.links.new(node_socket(assign.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
    return arrange(tree)
