"""Mode and energy selection backed by saved scientific records."""

from .node_identity import node_socket, socket_name
import json
import math

import bpy
from bpy.props import CollectionProperty, IntProperty, PointerProperty, StringProperty

from ..data import load_dataset
from .graph import view_modifier, frame_nodes
from .index_ranges import collection_index


def select_mode(settings, context):
    obj = settings.id_data
    if not obj.get('qc_dataset') or len(settings.modes) == 0:
        return
    data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
    index = settings.active_mode
    if not 0 <= index < len(data.arrays['mode_frequencies']):
        return
    displacement = data.arrays['mode_display_displacements'][index]
    attr = obj.data.attributes.get('qc_mode_displacement')
    if attr is None:
        attr = obj.data.attributes.new('qc_mode_displacement', 'FLOAT_VECTOR', 'POINT')
    attr.data.foreach_set('vector', displacement.ravel())
    obj['qc_mode_source_number'] = index + 1
    obj['qc_mode_frequency_cm-1'] = float(data.arrays['mode_frequencies'][index])
    if 'mode_ir_intensities' in data.arrays:
        obj['qc_mode_ir_km_mol'] = float(data.arrays['mode_ir_intensities'][index])
    elif 'qc_mode_ir_km_mol' in obj:
        del obj['qc_mode_ir_km_mol']
    obj.data.update()


class QCModeItem(bpy.types.PropertyGroup):
    label: StringProperty()


class QCEnergyItem(bpy.types.PropertyGroup):
    label: StringProperty()
    record: StringProperty()


class QCViewSettings(bpy.types.PropertyGroup):
    modes: CollectionProperty(type=QCModeItem)
    active_mode: collection_index('active_mode', 'modes', update=select_mode)
    energies: CollectionProperty(type=QCEnergyItem)
    active_energy: collection_index('active_energy', 'energies')
    spectrum: PointerProperty(type=bpy.types.Object)
    volume: PointerProperty(type=bpy.types.Object)
    association_reference: PointerProperty(type=bpy.types.Object)


class QCBLENDER_UL_modes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        from ..i18n import iface
        layout.label(text=item.label.replace('(imaginary)', iface('(imaginary)')))


class QCBLENDER_UL_energies(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        from ..i18n import iface
        record = json.loads(item.record)
        layout.label(text=f"{record['method']} | {iface(record['kind'])} | "
                          f"{record['value_hartree']:.10f} Eh | {iface(record['role'])}")


def setup_properties(obj, data):
    settings = obj.qc_settings
    obj['qc_calculation_status'] = data.metadata['calculation_status']
    for record in data.metadata.get('energies', []):
        item = settings.energies.add()
        item.label = f"{record['method']} | {record['kind']} | {record['value_hartree']:.10f} Eh | {record['role']}"
        item.record = json.dumps(record)
    selection = data.metadata.get('energy_selection')
    if selection:
        obj['qc_energy_selection'] = json.dumps(selection)
        for index, record in enumerate(data.metadata.get('energies', [])):
            if record.get('id') == selection['record_id']:
                settings.active_energy = index
    if 'modes' not in data.metadata:
        return
    frequencies = data.arrays['mode_frequencies']
    ir = data.arrays.get('mode_ir_intensities')
    for index, frequency in enumerate(frequencies):
        item = settings.modes.add()
        item.label = f'{index+1}: {frequency:.4f} cm^-1'
        if ir is not None:
            item.label += f' | IR {ir[index]:.4f} km/mol'
        if frequency < 0:
            item.label += ' (imaginary)'
    add_animation_nodes(obj)
    select_mode(settings, bpy.context)


def add_animation_nodes(obj):
    from .views import socket
    tree = view_modifier(obj).node_group
    existing_nodes = set(tree.nodes)
    for name, kind, default in [('Amplitude (angstrom)', 'NodeSocketFloat', .2),
                                 ('Phase', 'NodeSocketFloat', 0.),
                                 ('Cycles per second', 'NodeSocketFloat', 1.),
                                 ('Animate', 'NodeSocketBool', False)]:
        item = socket(tree, name, kind, default=default)
        # Existing modifiers receive zero when a socket is first created, before its default changes.
        view_modifier(obj)[item.identifier] = default
    nodes, links = tree.nodes, tree.links
    inputs = next(node for node in nodes if node.type == 'GROUP_INPUT')
    consumers = [link.to_socket for link in list(node_socket(inputs.outputs, 'Geometry').links)]
    for link in list(node_socket(inputs.outputs, 'Geometry').links):
        links.remove(link)
    equilibrium = nodes.new('GeometryNodeInputNamedAttribute')
    equilibrium.data_type = 'FLOAT_VECTOR'
    node_socket(equilibrium.inputs, 'Name').default_value = 'qc_equilibrium_position'
    displacement = nodes.new('GeometryNodeInputNamedAttribute')
    displacement.data_type = 'FLOAT_VECTOR'
    node_socket(displacement.inputs, 'Name').default_value = 'qc_mode_displacement'
    time = nodes.new('GeometryNodeInputSceneTime')
    cycles = nodes.new('ShaderNodeMath')
    cycles.operation = 'MULTIPLY'
    links.new(node_socket(time.outputs, 'Seconds'), cycles.inputs[0])
    links.new(node_socket(inputs.outputs, 'Cycles per second'), cycles.inputs[1])
    radians = nodes.new('ShaderNodeMath')
    radians.operation = 'MULTIPLY'
    radians.inputs[1].default_value = math.tau
    links.new(cycles.outputs[0], radians.inputs[0])
    animate = nodes.new('GeometryNodeSwitch')
    animate.input_type = 'FLOAT'
    links.new(node_socket(inputs.outputs, 'Animate'), node_socket(animate.inputs, 'Switch'))
    links.new(radians.outputs[0], node_socket(animate.inputs, 'True'))
    phase = nodes.new('ShaderNodeMath')
    phase.operation = 'ADD'
    links.new(node_socket(animate.outputs, 'Output'), phase.inputs[0])
    links.new(node_socket(inputs.outputs, 'Phase'), phase.inputs[1])
    sine = nodes.new('ShaderNodeMath')
    sine.operation = 'SINE'
    links.new(phase.outputs[0], sine.inputs[0])
    amplitude = nodes.new('ShaderNodeMath')
    amplitude.operation = 'MULTIPLY'
    links.new(node_socket(inputs.outputs, 'Amplitude (angstrom)'), amplitude.inputs[0])
    links.new(sine.outputs[0], amplitude.inputs[1])
    offset = nodes.new('ShaderNodeVectorMath')
    offset.operation = 'SCALE'
    links.new(node_socket(displacement.outputs, 'Attribute'), offset.inputs[0])
    links.new(amplitude.outputs[0], node_socket(offset.inputs, 'Scale'))
    position = nodes.new('GeometryNodeSetPosition')
    links.new(node_socket(inputs.outputs, 'Geometry'), node_socket(position.inputs, 'Geometry'))
    links.new(node_socket(equilibrium.outputs, 'Attribute'), node_socket(position.inputs, 'Position'))
    links.new(node_socket(offset.outputs, 'Vector'), node_socket(position.inputs, 'Offset'))
    for consumer in consumers:
        links.new(node_socket(position.outputs, 'Geometry'), consumer)
    add_mode_vectors(obj, node_socket(displacement.outputs, 'Attribute'), inputs)
    frame_nodes(tree, [node for node in nodes if node not in existing_nodes],
                'Modes: displacement and animation')


def add_mode_vectors(obj, displacement, inputs):
    from .views import material, socket
    modifier = view_modifier(obj)
    tree = modifier.node_group
    for name, kind, value in [('Show Displacement Vectors', 'NodeSocketBool', False),
                              ('Vector Radius', 'NodeSocketFloat', .03)]:
        item = socket(tree, name, kind, default=value)
        modifier[item.identifier] = value
    nodes, links = tree.nodes, tree.links
    arrow = nodes.new('GeometryNodeJoinGeometry')
    for kind, depth, offset in [('GeometryNodeMeshCylinder', .8, .4), ('GeometryNodeMeshCone', .2, .8)]:
        primitive = nodes.new(kind)
        node_socket(primitive.inputs, 'Vertices').default_value = 12
        node_socket(primitive.inputs, 'Depth').default_value = depth
        if kind.endswith('Cylinder'):
            node_socket(primitive.inputs, 'Radius').default_value = 1
        else:
            node_socket(primitive.inputs, 'Radius Top').default_value = 0
            node_socket(primitive.inputs, 'Radius Bottom').default_value = 2.5
        transform = nodes.new('GeometryNodeTransform')
        node_socket(transform.inputs, 'Translation').default_value = (0, 0, offset)
        links.new(node_socket(primitive.outputs, 'Mesh'), node_socket(transform.inputs, 'Geometry'))
        links.new(node_socket(transform.outputs, 'Geometry'), node_socket(arrow.inputs, 'Geometry'))
    assign = nodes.new('GeometryNodeSetMaterial')
    node_socket(assign.inputs, 'Material').default_value = material('QC mode vectors', (.95, .6, .05, 1))
    links.new(node_socket(arrow.outputs, 'Geometry'), node_socket(assign.inputs, 'Geometry'))
    vector = nodes.new('ShaderNodeVectorMath')
    vector.operation = 'SCALE'
    links.new(displacement, vector.inputs[0])
    links.new(node_socket(inputs.outputs, 'Amplitude (angstrom)'), node_socket(vector.inputs, 'Scale'))
    length = nodes.new('ShaderNodeVectorMath')
    length.operation = 'LENGTH'
    links.new(node_socket(vector.outputs, 'Vector'), length.inputs[0])
    scale = nodes.new('ShaderNodeCombineXYZ')
    links.new(node_socket(inputs.outputs, 'Vector Radius'), node_socket(scale.inputs, 'X'))
    links.new(node_socket(inputs.outputs, 'Vector Radius'), node_socket(scale.inputs, 'Y'))
    links.new(node_socket(length.outputs, 'Value'), node_socket(scale.inputs, 'Z'))
    align = nodes.new('FunctionNodeAlignEulerToVector')
    align.axis = 'Z'
    links.new(node_socket(vector.outputs, 'Vector'), node_socket(align.inputs, 'Vector'))
    instances = nodes.new('GeometryNodeInstanceOnPoints')
    style = next(n for n in nodes if n.type == 'GROUP' and n.node_tree.get('qc_asset_id') == 'qc.atom_style.v1')
    links.new(node_socket(style.inputs, 'Geometry').links[0].from_socket, node_socket(instances.inputs, 'Points'))
    links.new(node_socket(assign.outputs, 'Geometry'), node_socket(instances.inputs, 'Instance'))
    links.new(node_socket(scale.outputs, 'Vector'), node_socket(instances.inputs, 'Scale'))
    links.new(node_socket(align.outputs, 'Rotation'), node_socket(instances.inputs, 'Rotation'))
    positive = nodes.new('ShaderNodeMath')
    positive.operation = 'GREATER_THAN'
    positive.inputs[1].default_value = 1e-10
    links.new(node_socket(length.outputs, 'Value'), positive.inputs[0])
    selected = nodes.new('FunctionNodeBooleanMath')
    selected.operation = 'AND'
    links.new(positive.outputs[0], selected.inputs[0])
    links.new(node_socket(style.inputs, 'Selection').links[0].from_socket, selected.inputs[1])
    links.new(selected.outputs[0], node_socket(instances.inputs, 'Selection'))
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(node_socket(instances.outputs, 'Instances'), node_socket(realize.inputs, 'Geometry'))
    switch = nodes.new('GeometryNodeSwitch')
    switch.input_type = 'GEOMETRY'
    links.new(node_socket(inputs.outputs, 'Show Displacement Vectors'), node_socket(switch.inputs, 'Switch'))
    links.new(node_socket(realize.outputs, 'Geometry'), node_socket(switch.inputs, 'True'))
    output = next(n for n in nodes if n.type == 'GROUP_OUTPUT')
    original = node_socket(output.inputs, 'Geometry').links[0].from_socket
    joined = nodes.new('GeometryNodeJoinGeometry')
    links.new(original, node_socket(joined.inputs, 'Geometry'))
    links.new(node_socket(switch.outputs, 'Output'), node_socket(joined.inputs, 'Geometry'))
    links.new(node_socket(joined.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
