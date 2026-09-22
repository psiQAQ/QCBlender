"""Mode and energy selection backed by saved scientific records."""
import json
import math

import bpy
from bpy.props import CollectionProperty, IntProperty, PointerProperty, StringProperty
import numpy as np

from ..data import load_dataset
from .graph import view_modifier


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
    if settings.spectrum:
        colors = np.tile([0.35, 0.45, 0.55, 1.], (2 * len(settings.modes), 1))
        colors[index*2:index*2+2] = [1., 0.3, 0.04, 1.]
        settings.spectrum.data.color_attributes['qc_ir_color'].data.foreach_set('color', colors.ravel())
        settings.spectrum.data.update()


class QCModeItem(bpy.types.PropertyGroup):
    label: StringProperty()


class QCEnergyItem(bpy.types.PropertyGroup):
    label: StringProperty()
    record: StringProperty()


class QCViewSettings(bpy.types.PropertyGroup):
    modes: CollectionProperty(type=QCModeItem)
    active_mode: IntProperty(default=0, min=0, update=select_mode)
    energies: CollectionProperty(type=QCEnergyItem)
    active_energy: IntProperty(default=0, min=0)
    spectrum: PointerProperty(type=bpy.types.Object)
    volume: PointerProperty(type=bpy.types.Object)


class QCBLENDER_UL_modes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.label)


class QCBLENDER_UL_energies(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.label)


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
    if ir is not None:
        settings.spectrum = ir_spectrum(obj, frequencies, ir)
    select_mode(settings, bpy.context)


def add_animation_nodes(obj):
    from .views import socket
    tree = view_modifier(obj).node_group
    for name, kind, default in [('Amplitude (angstrom)', 'NodeSocketFloat', .2),
                                 ('Phase', 'NodeSocketFloat', 0.),
                                 ('Cycles per second', 'NodeSocketFloat', 1.),
                                 ('Animate', 'NodeSocketBool', False)]:
        item = socket(tree, name, kind, default=default)
        # Existing modifiers receive zero when a socket is first created, before its default changes.
        view_modifier(obj)[item.identifier] = default
    nodes, links = tree.nodes, tree.links
    inputs = next(node for node in nodes if node.type == 'GROUP_INPUT')
    consumers = [link.to_socket for link in list(inputs.outputs['Geometry'].links)]
    for link in list(inputs.outputs['Geometry'].links):
        links.remove(link)
    equilibrium = nodes.new('GeometryNodeInputNamedAttribute')
    equilibrium.data_type = 'FLOAT_VECTOR'
    equilibrium.inputs['Name'].default_value = 'qc_equilibrium_position'
    displacement = nodes.new('GeometryNodeInputNamedAttribute')
    displacement.data_type = 'FLOAT_VECTOR'
    displacement.inputs['Name'].default_value = 'qc_mode_displacement'
    time = nodes.new('GeometryNodeInputSceneTime')
    cycles = nodes.new('ShaderNodeMath')
    cycles.operation = 'MULTIPLY'
    links.new(time.outputs['Seconds'], cycles.inputs[0])
    links.new(inputs.outputs['Cycles per second'], cycles.inputs[1])
    radians = nodes.new('ShaderNodeMath')
    radians.operation = 'MULTIPLY'
    radians.inputs[1].default_value = math.tau
    links.new(cycles.outputs[0], radians.inputs[0])
    animate = nodes.new('GeometryNodeSwitch')
    animate.input_type = 'FLOAT'
    links.new(inputs.outputs['Animate'], animate.inputs['Switch'])
    links.new(radians.outputs[0], animate.inputs['True'])
    phase = nodes.new('ShaderNodeMath')
    phase.operation = 'ADD'
    links.new(animate.outputs['Output'], phase.inputs[0])
    links.new(inputs.outputs['Phase'], phase.inputs[1])
    sine = nodes.new('ShaderNodeMath')
    sine.operation = 'SINE'
    links.new(phase.outputs[0], sine.inputs[0])
    amplitude = nodes.new('ShaderNodeMath')
    amplitude.operation = 'MULTIPLY'
    links.new(inputs.outputs['Amplitude (angstrom)'], amplitude.inputs[0])
    links.new(sine.outputs[0], amplitude.inputs[1])
    offset = nodes.new('ShaderNodeVectorMath')
    offset.operation = 'SCALE'
    links.new(displacement.outputs['Attribute'], offset.inputs[0])
    links.new(amplitude.outputs[0], offset.inputs['Scale'])
    position = nodes.new('GeometryNodeSetPosition')
    links.new(inputs.outputs['Geometry'], position.inputs['Geometry'])
    links.new(equilibrium.outputs['Attribute'], position.inputs['Position'])
    links.new(offset.outputs['Vector'], position.inputs['Offset'])
    for consumer in consumers:
        links.new(position.outputs['Geometry'], consumer)
    add_mode_vectors(obj, displacement.outputs['Attribute'], inputs)
    for index, node in enumerate(nodes):
        node.location = (index % 5 * 220, -(index // 5) * 240)


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
        primitive.inputs['Vertices'].default_value = 12
        primitive.inputs['Depth'].default_value = depth
        if kind.endswith('Cylinder'):
            primitive.inputs['Radius'].default_value = 1
        else:
            primitive.inputs['Radius Top'].default_value = 0
            primitive.inputs['Radius Bottom'].default_value = 2.5
        transform = nodes.new('GeometryNodeTransform')
        transform.inputs['Translation'].default_value = (0, 0, offset)
        links.new(primitive.outputs['Mesh'], transform.inputs['Geometry'])
        links.new(transform.outputs['Geometry'], arrow.inputs['Geometry'])
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = material('QC mode vectors', (.95, .6, .05, 1))
    links.new(arrow.outputs['Geometry'], assign.inputs['Geometry'])
    vector = nodes.new('ShaderNodeVectorMath')
    vector.operation = 'SCALE'
    links.new(displacement, vector.inputs[0])
    links.new(inputs.outputs['Amplitude (angstrom)'], vector.inputs['Scale'])
    length = nodes.new('ShaderNodeVectorMath')
    length.operation = 'LENGTH'
    links.new(vector.outputs['Vector'], length.inputs[0])
    scale = nodes.new('ShaderNodeCombineXYZ')
    links.new(inputs.outputs['Vector Radius'], scale.inputs['X'])
    links.new(inputs.outputs['Vector Radius'], scale.inputs['Y'])
    links.new(length.outputs['Value'], scale.inputs['Z'])
    align = nodes.new('FunctionNodeAlignEulerToVector')
    align.axis = 'Z'
    links.new(vector.outputs['Vector'], align.inputs['Vector'])
    instances = nodes.new('GeometryNodeInstanceOnPoints')
    style = next(n for n in nodes if n.type == 'GROUP' and n.node_tree.get('qc_asset_id') == 'qc.atom_style.v1')
    links.new(style.inputs['Geometry'].links[0].from_socket, instances.inputs['Points'])
    links.new(assign.outputs['Geometry'], instances.inputs['Instance'])
    links.new(scale.outputs['Vector'], instances.inputs['Scale'])
    links.new(align.outputs['Rotation'], instances.inputs['Rotation'])
    positive = nodes.new('ShaderNodeMath')
    positive.operation = 'GREATER_THAN'
    positive.inputs[1].default_value = 1e-10
    links.new(length.outputs['Value'], positive.inputs[0])
    selected = nodes.new('FunctionNodeBooleanMath')
    selected.operation = 'AND'
    links.new(positive.outputs[0], selected.inputs[0])
    links.new(style.inputs['Selection'].links[0].from_socket, selected.inputs[1])
    links.new(selected.outputs[0], instances.inputs['Selection'])
    realize = nodes.new('GeometryNodeRealizeInstances')
    links.new(instances.outputs['Instances'], realize.inputs['Geometry'])
    switch = nodes.new('GeometryNodeSwitch')
    switch.input_type = 'GEOMETRY'
    links.new(inputs.outputs['Show Displacement Vectors'], switch.inputs['Switch'])
    links.new(realize.outputs['Geometry'], switch.inputs['True'])
    output = next(n for n in nodes if n.type == 'GROUP_OUTPUT')
    original = output.inputs['Geometry'].links[0].from_socket
    joined = nodes.new('GeometryNodeJoinGeometry')
    links.new(original, joined.inputs['Geometry'])
    links.new(switch.outputs['Output'], joined.inputs['Geometry'])
    links.new(joined.outputs['Geometry'], output.inputs['Geometry'])


def ir_spectrum(parent, frequencies, intensities):
    from .views import material
    height_scale = 2 / max(float(intensities.max()), 1e-12)
    vertices = [(float(f) / 1000, 0, z) for f, intensity in zip(frequencies, intensities)
                for z in (0, float(intensity) * height_scale)]
    mesh = bpy.data.meshes.new('QC IR sticks')
    mesh.from_pydata(vertices, [(2*i, 2*i+1) for i in range(len(frequencies))], [])
    colors = mesh.color_attributes.new('qc_ir_color', 'FLOAT_COLOR', 'POINT')
    colors.data.foreach_set('color', np.tile([0.35, 0.45, 0.55, 1.], (len(vertices), 1)).ravel())
    obj = bpy.data.objects.new('QC IR stick spectrum', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = (4, 0, 0)
    obj['qc_frequency_scale'] = '1000 cm^-1 per Blender unit'
    obj['qc_view_kind'] = 'spectrum'
    obj['qc_intensity_scale'] = height_scale
    obj['qc_intensity_unit'] = 'km/mol'
    tree = bpy.data.node_groups.new('QC IR Sticks v1', 'GeometryNodeTree')
    tree.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, links = tree.nodes, tree.links
    inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    curve = nodes.new('GeometryNodeMeshToCurve')
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle.inputs['Resolution'].default_value = 8
    circle.inputs['Radius'].default_value = 0.012
    tubes = nodes.new('GeometryNodeCurveToMesh')
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = material('QC IR spectrum colors', (.4,.4,.4,1), 'qc_ir_color')
    links.new(inputs.outputs['Geometry'], curve.inputs['Mesh'])
    links.new(curve.outputs['Curve'], tubes.inputs['Curve'])
    links.new(circle.outputs['Curve'], tubes.inputs['Profile Curve'])
    links.new(tubes.outputs['Mesh'], assign.inputs['Geometry'])
    links.new(assign.outputs['Geometry'], output.inputs['Geometry'])
    obj.modifiers.new('QC IR sticks', 'NODES').node_group = tree
    text = bpy.data.curves.new('QC IR axis labels', 'FONT')
    text.body = 'IR sticks: x = frequency / 1000 cm^-1\nHeight scaled from km/mol; selected mode is orange'
    text.size = .16
    label = bpy.data.objects.new('QC IR labels', text)
    bpy.context.collection.objects.link(label)
    label.parent = obj
    label.location = (0, 0, -.35)
    label.rotation_euler = (math.pi/2, 0, 0)
    return obj
