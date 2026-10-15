"""Editable geometry node views of normalized scientific data."""

from .node_identity import node_socket, socket_name
import json
import hashlib
from pathlib import Path

import bpy
import numpy as np

from ..data import filesystem_path, load_dataset
from .graph import tag_view, frame_nodes
from .native_volume import check_field_cache


def socket(tree, name, kind, direction='INPUT', default=None, minimum=None, maximum=None):
    result = tree.interface.new_socket(name=name, in_out=direction, socket_type=kind)
    if default is not None:
        result.default_value = default
    if minimum is not None:
        result.min_value = minimum
    if maximum is not None:
        result.max_value = maximum
    from .node_identity import remember_sockets
    remember_sockets(tree)
    return result


def group_sockets(tree, panels):
    """Move existing inputs into panels without replacing their identifiers."""
    items = {(socket_name(item, tree), item.in_out): item for item in tree.interface.items_tree
             if item.item_type == 'SOCKET'}
    for title, names in panels:
        panel = tree.interface.new_panel(title)
        for index, name in enumerate(names):
            tree.interface.move_to_parent(items[name, 'INPUT'], panel, index)


def node_by_type(nodes, kind):
    return next((node for node in nodes if node.bl_idname == kind), None)


def material(name, color, attribute=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = node_by_type(mat.node_tree.nodes, 'ShaderNodeBsdfPrincipled')
    if shader is None:
        shader = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        output = node_by_type(mat.node_tree.nodes, 'ShaderNodeOutputMaterial')
        if output is None:
            output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(node_socket(shader.outputs, 'BSDF'), node_socket(output.inputs, 'Surface'))
    node_socket(shader.inputs, 'Base Color').default_value = color
    node_socket(shader.inputs, 'Alpha').default_value = color[3]
    node_socket(shader.inputs, 'Roughness').default_value = 0.35
    if attribute:
        node = mat.node_tree.nodes.new('ShaderNodeAttribute')
        node.attribute_name = attribute
        mat.node_tree.links.new(node_socket(node.outputs, 'Color'), node_socket(shader.inputs, 'Base Color'))
    return mat


def bind(obj, directory, data):
    obj['qc_dataset'] = str(Path(directory).resolve())
    obj['qc_dataset_sha256'] = hashlib.sha256(filesystem_path(Path(directory) / 'manifest.json').read_bytes()).hexdigest()
    obj['qc_source_sha256'] = data.metadata['source']['sha256']
    obj['qc_source_filename'] = data.metadata['source'].get('filename', '未记录')
    obj['qc_source_job'] = data.metadata.get('selected_job', -1)
    obj['qc_schema'] = '0.1'
    obj['qc_coordinate_unit'] = 'angstrom'
    obj['qc_diagnostics'] = json.dumps(data.metadata.get('diagnostics', []))
    from .source_browser import cache_dataset
    cache_dataset(obj, data)


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
    visible = mesh.attributes.new('qc_atom_visible', 'BOOLEAN', 'POINT')
    visible.data.foreach_set('value', [True] * len(positions))
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
    tree = bpy.data.node_groups.new('QC Atoms View v2', 'GeometryNodeTree')
    tree.is_modifier = True
    socket(tree, 'Geometry', 'NodeSocketGeometry')
    socket(tree, 'Atom Radius', 'NodeSocketFloat', default=0.25, minimum=0.001)
    socket(tree, 'Bond Radius', 'NodeSocketFloat', default=0.07, minimum=0.001)
    socket(tree, 'Selection', 'NodeSocketBool', default=True)
    socket(tree, 'Element (0 = all)', 'NodeSocketInt', default=0, minimum=0)
    socket(tree, 'First Atom (1-based)', 'NodeSocketInt', default=1, minimum=1, maximum=max(1, len(positions)))
    socket(tree, 'Last Atom (0 = all)', 'NodeSocketInt', default=0, minimum=0, maximum=len(positions))
    socket(tree, 'Style (0 ball-stick, 1 space-fill, 2 bonds)', 'NodeSocketInt', default=0, minimum=0, maximum=2)
    socket(tree, 'VDW Scale', 'NodeSocketFloat', default=1., minimum=.01)
    socket(tree, 'Quality', 'NodeSocketInt', default=3, minimum=1)
    socket(tree, 'Material', 'NodeSocketMaterial', default=material('QC Elements', (.35, .35, .35, 1), 'qc_element_color'))
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    nodes, links = tree.nodes, tree.links
    inputs = nodes.new('NodeGroupInput')
    output = nodes.new('NodeGroupOutput')
    from .assets import selection_group, atom_style_group
    from ..radii import VDW_RADII
    radii = mesh.attributes.new('qc_vdw_radius', 'FLOAT', 'POINT')
    radii.data.foreach_set('value', [VDW_RADII.get(int(z), 0.) for z in data.arrays['atomic_numbers']])
    obj['qc_vdw_missing'] = json.dumps(sorted({int(z) for z in data.arrays['atomic_numbers'] if int(z) not in VDW_RADII}))
    selected = nodes.new('GeometryNodeGroup')
    selected.node_tree = selection_group()
    for name in ('Selection', 'Element (0 = all)', 'First Atom (1-based)', 'Last Atom (0 = all)'):
        links.new(node_socket(inputs.outputs, name), node_socket(selected.inputs, name))
    style = nodes.new('GeometryNodeGroup')
    style.node_tree = atom_style_group()
    for name in ('Geometry', 'Atom Radius', 'Bond Radius', 'VDW Scale', 'Quality', 'Material', 'Style (0 ball-stick, 1 space-fill, 2 bonds)'):
        links.new(node_socket(inputs.outputs, name), node_socket(style.inputs, name))
    links.new(node_socket(selected.outputs, 'Selection'), node_socket(style.inputs, 'Selection'))
    links.new(node_socket(style.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
    obj.modifiers.new('QC Atoms and Bonds', 'NODES').node_group = tree
    from .properties import setup_properties
    setup_properties(obj, data)
    tag_view(tree)
    obj['qc_view_kind'] = 'atoms'
    trajectory = data.metadata.get('optimization')
    if trajectory:
        obj['qc_optimization_status'] = trajectory['status']
        obj['qc_optimization_available'] = trajectory['status'] == 'available'
        obj['qc_optimization_reason'] = trajectory.get('reason', '')
    ensure_atom_visibility(obj)
    frame_nodes(tree, [node for node in nodes if node.type not in ('FRAME', 'GROUP_INPUT', 'GROUP_OUTPUT')
                      and node.parent is None], 'Atoms: selection and representation', (300, 0))
    for node in nodes:
        from .node_identity import frame_role
        if node.type == 'FRAME' and frame_role(node) == 'Modes: displacement and animation':
            node.location = (300, -1400)
    inputs.location = (-100, 0)
    output.location = (1800, 0)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def ensure_atom_visibility(obj):
    """Add a per-view visibility gate while preserving the original atom selection."""
    from .graph import view_modifier

    mesh = obj.data
    if mesh.attributes.get('qc_atom_visible') is None:
        attr = mesh.attributes.new('qc_atom_visible', 'BOOLEAN', 'POINT')
        attr.data.foreach_set('value', [True] * len(mesh.vertices))
    tree = view_modifier(obj).node_group
    if tree.get('qc_atom_visibility'):
        return mesh.attributes['qc_atom_visible']
    styles = [node for node in tree.nodes if node.type == 'GROUP' and node.node_tree
              and node.node_tree.get('qc_asset_id') == 'qc.atom_style.v1']
    if len(styles) != 1:
        raise ValueError('Expected one QC atom style group in the selected view')
    socket = node_socket(styles[0].inputs, 'Selection')
    previous = socket.links[0].from_socket if socket.links else None
    attr = tree.nodes.new('GeometryNodeInputNamedAttribute')
    attr.data_type = 'BOOLEAN'
    node_socket(attr.inputs, 'Name').default_value = 'qc_atom_visible'
    gate = tree.nodes.new('ShaderNodeMath')
    gate.operation = 'MULTIPLY'
    if previous:
        tree.links.new(previous, gate.inputs[0])
    else:
        gate.inputs[0].default_value = float(socket.default_value)
    tree.links.new(node_socket(attr.outputs, 'Attribute'), gate.inputs[1])
    tree.links.new(gate.outputs[0], socket)
    tree['qc_atom_visibility'] = 1
    return mesh.attributes['qc_atom_visible']


def atom_selection(tree, inputs):
    from .assets import math
    nodes = tree.nodes

    atomic_number = nodes.new('GeometryNodeInputNamedAttribute')
    atomic_number.data_type = 'INT'
    node_socket(atomic_number.inputs, 'Name').default_value = 'qc_atomic_number'
    atom_id = nodes.new('GeometryNodeInputNamedAttribute')
    atom_id.data_type = 'INT'
    node_socket(atom_id.inputs, 'Name').default_value = 'qc_atom_id'
    source_number = math(tree, 'ADD', node_socket(atom_id.outputs, 'Attribute'), 1)
    element = node_socket(inputs.outputs, 'Element (0 = all)')
    last = node_socket(inputs.outputs, 'Last Atom (0 = all)')
    matches_element = math(tree, 'MAXIMUM', math(tree, 'COMPARE', element, 0),
                           math(tree, 'COMPARE', node_socket(atomic_number.outputs, 'Attribute'), element))
    after_first = math(tree, 'SUBTRACT', 1, math(tree, 'LESS_THAN', source_number, node_socket(inputs.outputs, 'First Atom (1-based)')))
    before_last = math(tree, 'MAXIMUM', math(tree, 'COMPARE', last, 0),
                       math(tree, 'SUBTRACT', 1, math(tree, 'GREATER_THAN', source_number, last)))
    return math(tree, 'MULTIPLY', node_socket(inputs.outputs, 'Selection'),
                math(tree, 'MULTIPLY', matches_element, math(tree, 'MULTIPLY', after_first, before_last)))


def field_view(directory, parent=None, index=0):
    data = load_dataset(directory)
    field = data.metadata['fields'][index]
    cache = check_field_cache(directory, field)
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
    tree = bpy.data.node_groups.new('QC Isosurface View v3', 'GeometryNodeTree')
    tree.is_modifier = True
    threshold = 0.05 if field['quantity'] in ('orbital_amplitude', 'spin_density') else 0.02
    socket(tree, 'Isovalue', 'NodeSocketFloat', default=threshold, minimum=1e-7)
    socket(tree, 'Link Thresholds', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Isovalue', 'NodeSocketFloat', default=threshold, minimum=1e-7)
    socket(tree, 'Style (0 solid, 1 wire, 2 points)', 'NodeSocketInt', default=0, minimum=0, maximum=2)
    socket(tree, 'Wire Radius', 'NodeSocketFloat', default=.012, minimum=.0001)
    socket(tree, 'Point Radius', 'NodeSocketFloat', default=.025, minimum=.0001)
    socket(tree, 'Quality', 'NodeSocketInt', default=2, minimum=1)
    signed = field['quantity'] not in ('electron_number_density', 'alpha_density', 'beta_density')
    socket(tree, 'Positive Phase', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Phase', 'NodeSocketBool', default=signed)
    socket(tree, 'Positive Opacity', 'NodeSocketFloat', default=1., minimum=0.)
    socket(tree, 'Negative Opacity', 'NodeSocketFloat', default=1., minimum=0.)
    socket(tree, 'Adaptivity', 'NodeSocketFloat', default=0, minimum=0)
    socket(tree, 'Smooth Normals', 'NodeSocketBool', default=True)
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    info = nodes.new('GeometryNodeObjectInfo')
    info.transform_space = 'RELATIVE'
    node_socket(info.inputs, 'Object').default_value = source
    style = nodes.new('GeometryNodeGroup')
    style.node_tree = isosurface_group()
    links.new(node_socket(info.outputs, 'Geometry'), node_socket(style.inputs, 'Volume'))
    for name in ('Isovalue', 'Link Thresholds', 'Negative Isovalue', 'Positive Phase', 'Negative Phase', 'Positive Opacity', 'Negative Opacity', 'Adaptivity', 'Smooth Normals',
                 'Style (0 solid, 1 wire, 2 points)', 'Wire Radius', 'Point Radius', 'Quality'):
        links.new(node_socket(inputs.outputs, name), node_socket(style.inputs, name))
    for label, color in [('Positive', (0.1, 0.3, 0.8, 1)), ('Negative', (0.85, 0.12, 0.08, 1))]:
        name = label + ' Material'
        mat = material('QC ' + label + ' Phase', color)
        opacity = mat.node_tree.nodes.new('ShaderNodeAttribute')
        opacity.attribute_name = 'qc_opacity'
        shader = node_by_type(mat.node_tree.nodes, 'ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(node_socket(opacity.outputs, 'Fac'), node_socket(shader.inputs, 'Alpha'))
        socket(tree, name, 'NodeSocketMaterial', default=mat)
        links.new(node_socket(inputs.outputs, name), node_socket(style.inputs, name))
    links.new(node_socket(style.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
    frame_nodes(tree, [info, style], 'Field: source and isosurface', (300, 0))
    inputs.location, output.location = (-100, 0), (1200, 0)
    obj.modifiers.new('QC Isosurface', 'NODES').node_group = tree
    tag_view(tree)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def isosurface_group():
    """Reusable signed isosurfaces of QC grids; bindings belong to the caller."""
    asset_id = 'qc.isosurface.v3'
    existing = next((group for group in bpy.data.node_groups
                     if group.bl_idname == 'GeometryNodeTree' and group.get('qc_asset_id') == asset_id), None)
    if existing is not None:
        return existing
    tree = bpy.data.node_groups.new('QC Style Isosurface v3', 'GeometryNodeTree')
    tree['qc_asset_id'] = asset_id
    socket(tree, 'Volume', 'NodeSocketGeometry')
    socket(tree, 'Isovalue', 'NodeSocketFloat', default=.05, minimum=1e-7)
    socket(tree, 'Link Thresholds', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Isovalue', 'NodeSocketFloat', default=.05, minimum=1e-7)
    socket(tree, 'Style (0 solid, 1 wire, 2 points)', 'NodeSocketInt', default=0, minimum=0)
    socket(tree, 'Wire Radius', 'NodeSocketFloat', default=.012, minimum=.0001)
    socket(tree, 'Point Radius', 'NodeSocketFloat', default=.025, minimum=.0001)
    socket(tree, 'Quality', 'NodeSocketInt', default=2, minimum=1)
    socket(tree, 'Positive Phase', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Phase', 'NodeSocketBool', default=True)
    socket(tree, 'Positive Opacity', 'NodeSocketFloat', default=1., minimum=0.)
    socket(tree, 'Negative Opacity', 'NodeSocketFloat', default=1., minimum=0.)
    socket(tree, 'Adaptivity', 'NodeSocketFloat', default=0, minimum=0)
    socket(tree, 'Smooth Normals', 'NodeSocketBool', default=True)
    socket(tree, 'Positive Material', 'NodeSocketMaterial')
    socket(tree, 'Negative Material', 'NodeSocketMaterial')
    socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
    socket(tree, 'Positive', 'NodeSocketGeometry', 'OUTPUT')
    socket(tree, 'Negative', 'NodeSocketGeometry', 'OUTPUT')
    group_sockets(tree, (
        ('Source', ('Volume',)),
        ('Thresholds', ('Isovalue', 'Link Thresholds', 'Negative Isovalue', 'Adaptivity')),
        ('Representation', ('Style (0 solid, 1 wire, 2 points)', 'Wire Radius', 'Point Radius', 'Quality', 'Smooth Normals')),
        ('Phases', ('Positive Phase', 'Negative Phase', 'Positive Opacity', 'Negative Opacity')),
        ('Materials', ('Positive Material', 'Negative Material')),
    ))
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    join = nodes.new('GeometryNodeJoinGeometry')
    smooth = nodes.new('GeometryNodeSetShadeSmooth')
    links.new(node_socket(join.outputs, 'Geometry'), node_socket(smooth.inputs, 'Geometry'))
    links.new(node_socket(inputs.outputs, 'Smooth Normals'), node_socket(smooth.inputs, 'Shade Smooth'))
    links.new(node_socket(smooth.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
    valid_grid = nodes.new('GeometryNodeGetNamedGrid')
    node_socket(valid_grid.inputs, 'Name').default_value = 'qc_valid'
    links.new(node_socket(inputs.outputs, 'Volume'), node_socket(valid_grid.inputs, 'Volume'))
    sample = nodes.new('GeometryNodeSampleGrid')
    node_socket(sample.inputs, 'Interpolation').default_value = 'Trilinear'
    links.new(node_socket(valid_grid.outputs, 'Grid'), node_socket(sample.inputs, 'Grid'))
    position = nodes.new('GeometryNodeInputPosition')
    links.new(node_socket(position.outputs, 'Position'), node_socket(sample.inputs, 'Position'))
    invalid = nodes.new('ShaderNodeMath')
    invalid.operation = 'LESS_THAN'
    invalid.inputs[1].default_value = 0.999999
    links.new(node_socket(sample.outputs, 'Value'), invalid.inputs[0])
    for label, name in [('Positive Phase', 'qc_value'), ('Negative Phase', 'qc_negative')]:
        grid = nodes.new('GeometryNodeGetNamedGrid')
        node_socket(grid.inputs, 'Name').default_value = name
        links.new(node_socket(inputs.outputs, 'Volume'), node_socket(grid.inputs, 'Volume'))
        surface = nodes.new('GeometryNodeGridToMesh')
        links.new(node_socket(grid.outputs, 'Grid'), node_socket(surface.inputs, 'Grid'))
        threshold = node_socket(inputs.outputs, 'Isovalue')
        if name == 'qc_negative':
            choose = nodes.new('GeometryNodeSwitch')
            choose.input_type = 'FLOAT'
            links.new(node_socket(inputs.outputs, 'Link Thresholds'), node_socket(choose.inputs, 'Switch'))
            links.new(node_socket(inputs.outputs, 'Isovalue'), node_socket(choose.inputs, 'True'))
            links.new(node_socket(inputs.outputs, 'Negative Isovalue'), node_socket(choose.inputs, 'False'))
            threshold = node_socket(choose.outputs, 'Output')
        links.new(threshold, node_socket(surface.inputs, 'Threshold'))
        links.new(node_socket(inputs.outputs, 'Adaptivity'), node_socket(surface.inputs, 'Adaptivity'))
        delete = nodes.new('GeometryNodeDeleteGeometry')
        delete.domain = 'POINT'
        links.new(node_socket(surface.outputs, 'Mesh'), node_socket(delete.inputs, 'Geometry'))
        links.new(invalid.outputs[0], node_socket(delete.inputs, 'Selection'))
        assign = nodes.new('GeometryNodeSetMaterial')
        links.new(node_socket(inputs.outputs, label.replace('Phase', 'Material')), node_socket(assign.inputs, 'Material'))
        from .assets import surface_style_group
        representation = nodes.new('GeometryNodeGroup')
        representation.node_tree = surface_style_group()
        links.new(node_socket(delete.outputs, 'Geometry'), node_socket(representation.inputs, 'Geometry'))
        for control in ('Style (0 solid, 1 wire, 2 points)', 'Wire Radius', 'Point Radius', 'Quality'):
            links.new(node_socket(inputs.outputs, control), node_socket(representation.inputs, control))
        opacity = nodes.new('GeometryNodeStoreNamedAttribute')
        opacity.data_type, opacity.domain = 'FLOAT', 'POINT'
        node_socket(opacity.inputs, 'Name').default_value = 'qc_opacity'
        links.new(node_socket(inputs.outputs, label.replace('Phase', 'Opacity')), node_socket(opacity.inputs, 'Value'))
        links.new(node_socket(representation.outputs, 'Geometry'), node_socket(opacity.inputs, 'Geometry'))
        links.new(node_socket(opacity.outputs, 'Geometry'), node_socket(assign.inputs, 'Geometry'))
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(node_socket(inputs.outputs, label), node_socket(switch.inputs, 'Switch'))
        links.new(node_socket(assign.outputs, 'Geometry'), node_socket(switch.inputs, 'True'))
        links.new(node_socket(switch.outputs, 'Output'), node_socket(join.inputs, 'Geometry'))
        links.new(node_socket(switch.outputs, 'Output'), node_socket(output.inputs, label.split()[0]))
    for index, node in enumerate(nodes):
        node.location = (index % 5 * 220, -(index // 5) * 240)
    from .node_identity import localize_tree
    localize_tree(tree)
    return tree
