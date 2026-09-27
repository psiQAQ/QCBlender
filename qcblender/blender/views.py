"""Editable geometry node views of normalized scientific data."""
import json
import hashlib
from pathlib import Path

import bpy
import numpy as np

from ..data import load_dataset, volume_cache
from .graph import tag_view


def socket(tree, name, kind, direction='INPUT', default=None, minimum=None):
    result = tree.interface.new_socket(name=name, in_out=direction, socket_type=kind)
    if default is not None:
        result.default_value = default
    if minimum is not None:
        result.min_value = minimum
    return result


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
        mat.node_tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Alpha'].default_value = color[3]
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
    obj['qc_source_filename'] = data.metadata['source'].get('filename', '未记录')
    obj['qc_source_job'] = data.metadata.get('selected_job', -1)
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
    socket(tree, 'First Atom (1-based)', 'NodeSocketInt', default=1, minimum=1)
    socket(tree, 'Last Atom (0 = all)', 'NodeSocketInt', default=0, minimum=0)
    socket(tree, 'Style (0 ball-stick, 1 space-fill, 2 bonds)', 'NodeSocketInt', default=0, minimum=0)
    socket(tree, 'VDW Scale', 'NodeSocketFloat', default=1., minimum=.01)
    socket(tree, 'Quality', 'NodeSocketInt', default=2, minimum=1)
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
        links.new(inputs.outputs[name], selected.inputs[name])
    style = nodes.new('GeometryNodeGroup')
    style.node_tree = atom_style_group()
    for name in ('Geometry', 'Atom Radius', 'Bond Radius', 'VDW Scale', 'Quality', 'Material', 'Style (0 ball-stick, 1 space-fill, 2 bonds)'):
        links.new(inputs.outputs[name], style.inputs[name])
    links.new(selected.outputs['Selection'], style.inputs['Selection'])
    links.new(style.outputs['Geometry'], output.inputs['Geometry'])
    for index, node in enumerate(nodes):
        node.location = (index % 4 * 220, -(index // 4) * 240)
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
    socket = styles[0].inputs['Selection']
    previous = socket.links[0].from_socket if socket.links else None
    attr = tree.nodes.new('GeometryNodeInputNamedAttribute')
    attr.data_type = 'BOOLEAN'
    attr.inputs['Name'].default_value = 'qc_atom_visible'
    gate = tree.nodes.new('ShaderNodeMath')
    gate.operation = 'MULTIPLY'
    if previous:
        tree.links.new(previous, gate.inputs[0])
    else:
        gate.inputs[0].default_value = float(socket.default_value)
    tree.links.new(attr.outputs['Attribute'], gate.inputs[1])
    tree.links.new(gate.outputs[0], socket)
    tree['qc_atom_visibility'] = 1
    return mesh.attributes['qc_atom_visible']


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
    tree = bpy.data.node_groups.new('QC Isosurface View v3', 'GeometryNodeTree')
    tree.is_modifier = True
    threshold = 0.05 if field['quantity'] in ('orbital_amplitude', 'spin_density') else 0.02
    socket(tree, 'Isovalue', 'NodeSocketFloat', default=threshold, minimum=1e-7)
    socket(tree, 'Link Thresholds', 'NodeSocketBool', default=True)
    socket(tree, 'Negative Isovalue', 'NodeSocketFloat', default=threshold, minimum=1e-7)
    socket(tree, 'Style (0 solid, 1 wire, 2 points)', 'NodeSocketInt', default=0, minimum=0)
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
    info.inputs['Object'].default_value = source
    style = nodes.new('GeometryNodeGroup')
    style.node_tree = isosurface_group()
    links.new(info.outputs['Geometry'], style.inputs['Volume'])
    for name in ('Isovalue', 'Link Thresholds', 'Negative Isovalue', 'Positive Phase', 'Negative Phase', 'Positive Opacity', 'Negative Opacity', 'Adaptivity', 'Smooth Normals',
                 'Style (0 solid, 1 wire, 2 points)', 'Wire Radius', 'Point Radius', 'Quality'):
        links.new(inputs.outputs[name], style.inputs[name])
    for label, color in [('Positive', (0.1, 0.3, 0.8, 1)), ('Negative', (0.85, 0.12, 0.08, 1))]:
        name = label + ' Material'
        mat = material('QC ' + label + ' Phase', color)
        opacity = mat.node_tree.nodes.new('ShaderNodeAttribute')
        opacity.attribute_name = 'qc_opacity'
        shader = node_by_type(mat.node_tree.nodes, 'ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(opacity.outputs['Fac'], shader.inputs['Alpha'])
        socket(tree, name, 'NodeSocketMaterial', default=mat)
        links.new(inputs.outputs[name], style.inputs[name])
    links.new(style.outputs['Geometry'], output.inputs['Geometry'])
    for number, node in enumerate(nodes):
        node.location = (number * 240, 0)
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
        threshold = inputs.outputs['Isovalue']
        if name == 'qc_negative':
            choose = nodes.new('GeometryNodeSwitch')
            choose.input_type = 'FLOAT'
            links.new(inputs.outputs['Link Thresholds'], choose.inputs['Switch'])
            links.new(inputs.outputs['Isovalue'], choose.inputs['True'])
            links.new(inputs.outputs['Negative Isovalue'], choose.inputs['False'])
            threshold = choose.outputs['Output']
        links.new(threshold, surface.inputs['Threshold'])
        links.new(inputs.outputs['Adaptivity'], surface.inputs['Adaptivity'])
        delete = nodes.new('GeometryNodeDeleteGeometry')
        delete.domain = 'POINT'
        links.new(surface.outputs['Mesh'], delete.inputs['Geometry'])
        links.new(invalid.outputs[0], delete.inputs['Selection'])
        assign = nodes.new('GeometryNodeSetMaterial')
        links.new(inputs.outputs[label.replace('Phase', 'Material')], assign.inputs['Material'])
        from .assets import surface_style_group
        representation = nodes.new('GeometryNodeGroup')
        representation.node_tree = surface_style_group()
        links.new(delete.outputs['Geometry'], representation.inputs['Geometry'])
        for control in ('Style (0 solid, 1 wire, 2 points)', 'Wire Radius', 'Point Radius', 'Quality'):
            links.new(inputs.outputs[control], representation.inputs[control])
        opacity = nodes.new('GeometryNodeStoreNamedAttribute')
        opacity.data_type, opacity.domain = 'FLOAT', 'POINT'
        opacity.inputs['Name'].default_value = 'qc_opacity'
        links.new(inputs.outputs[label.replace('Phase', 'Opacity')], opacity.inputs['Value'])
        links.new(representation.outputs['Geometry'], opacity.inputs['Geometry'])
        links.new(opacity.outputs['Geometry'], assign.inputs['Geometry'])
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(inputs.outputs[label], switch.inputs['Switch'])
        links.new(assign.outputs['Geometry'], switch.inputs['True'])
        links.new(switch.outputs['Output'], join.inputs['Geometry'])
        links.new(switch.outputs['Output'], output.inputs[label.split()[0]])
    for index, node in enumerate(nodes):
        node.location = (index % 5 * 220, -(index // 5) * 240)
    tree.asset_mark()
    tree.asset_data.description = 'Signed QC scalar isosurfaces with validity mask; input coordinates in angstrom'
    return tree
