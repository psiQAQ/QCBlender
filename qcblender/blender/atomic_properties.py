import json

from .node_identity import node_socket, socket_name, label_role

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty
import numpy as np

from ..data import load_dataset
from .scalars import scalar_material, add_legend, color_fraction
from .views import material, socket
from .graph import view_modifier, tag_view, frame_nodes
from .index_ranges import atom_bounds, atom_count, bounded_int, limit_property

_charge_items = {}


class QCBLENDER_OT_distance(bpy.types.Operator):
    bl_idname = 'qcblender.measure_distance'
    bl_label = 'Label Equilibrium Atom Distance'
    bl_description = 'Create a distance label for two source atom numbers using the dataset equilibrium geometry in angstroms; this is not a current-step measurement'
    bl_options = {'REGISTER', 'UNDO'}
    first: bounded_int('first', atom_bounds, name='First atom (1-based)', default=1, min=1)
    second: bounded_int('second', atom_bounds, name='Second atom (1-based)', default=2, min=1)

    @classmethod
    def poll(cls, context):
        return atom_count(context.object) >= 2

    def invoke(self, context, event):
        for name in ('first', 'second'):
            limit_property(self, name, atom_bounds, context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        from ..i18n import iface, ui_layout
        layout = ui_layout(self.layout)
        layout.label(text=iface('Atoms 1-{count}', count=atom_count(context.object)))
        layout.prop(self, 'first')
        layout.prop(self, 'second')

    def execute(self, context):
        from ..i18n import iface, error_text
        parent = context.object
        try:
            data = load_dataset(bpy.path.abspath(parent['qc_dataset']))
            coords = data.arrays['positions']
            if self.first == self.second or max(self.first, self.second) > len(coords):
                raise ValueError('Choose two different existing atom numbers')
            points = coords[[self.first - 1, self.second - 1]]
            distance = float(np.linalg.norm(points[1] - points[0]))
        except (ValueError, OSError, KeyError) as error:
            self.report({'ERROR'}, error_text(error))
            return {'CANCELLED'}
        text = bpy.data.curves.new('QC distance label', 'FONT')
        text.body = f'{self.first}-{self.second}: {distance:.4f} angstrom (equilibrium)'
        text.size = .13
        obj = bpy.data.objects.new('QC equilibrium distance', text)
        context.collection.objects.link(obj)
        obj.parent = parent
        obj.location = points.mean(axis=0)
        obj['qc_measurement'] = json.dumps({'quantity': 'distance', 'unit': 'angstrom', 'value': distance,
            'source_atom_numbers': [self.first, self.second], 'geometry': 'source equilibrium',
            'source_sha256': data.metadata['source']['sha256']})
        return {'FINISHED'}


def charge_items(self, context):
    from ..i18n import tip
    obj = context.object
    if obj is None or 'qc_dataset' not in obj:
        return []
    path = bpy.path.abspath(obj['qc_dataset'])
    if path not in _charge_items:
        data = load_dataset(path)
        _charge_items[path] = [(c['method'], c['method'], 'Atomic partial charge in e')
                               for c in data.metadata.get('charges', [])]
    return [(identifier, label, tip(description))
            for identifier, label, description in _charge_items[path]]


class QCBLENDER_OT_color_charge(bpy.types.Operator):
    bl_idname = 'qcblender.color_charge'
    bl_label = 'Color by Atomic Charge'
    bl_description = 'Color the active atom view with a recorded partial-charge method and an explicit range in e; use a separate atom layer if a scalar color field is already bound'
    bl_options = {'REGISTER', 'UNDO'}
    method: EnumProperty(name='Charge method', items=charge_items)
    minimum: FloatProperty(name='Minimum (e)', default=-1)
    maximum: FloatProperty(name='Maximum (e)', default=1)

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'charge')

    def invoke(self, context, event):
        from ..i18n import iface, error_text
        items = charge_items(self, context)
        if not items:
            self.report({'ERROR'}, iface('This source has no atomic partial charges'))
            return {'CANCELLED'}
        self.method = items[0][0]
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        from ..i18n import iface, error_text
        obj = context.object
        tree = view_modifier(obj).node_group
        if tree.get('qc_color_mapping'):
            self.report({'ERROR'}, iface('This view already uses a scalar field for color; use a separate atom view for charges'))
            return {'CANCELLED'}
        data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
        prop = next((c for c in data.metadata['charges'] if c['method'] == self.method), None)
        if prop is None or not np.isfinite([self.minimum, self.maximum]).all() or self.minimum >= self.maximum:
            self.report({'ERROR'}, iface('Choose an available charge method and an increasing finite color range'))
            return {'CANCELLED'}
        obj.data.attributes['qc_charge'].data.foreach_set('value', data.arrays[prop['array']])
        obj.data.update()
        obj['qc_charge_method'] = self.method
        if not tree.get('qc_charge_mapping'):
            for name, value in [('Charge Minimum', self.minimum), ('Charge Center', (self.minimum + self.maximum) / 2),
                                ('Charge Maximum', self.maximum)]:
                item = socket(tree, name, 'NodeSocketFloat', default=value)
                view_modifier(obj)[item.identifier] = value
            nodes, links = tree.nodes, tree.links
            existing_nodes = set(nodes)
            inputs = next(n for n in nodes if n.type == 'GROUP_INPUT')
            output = next(n for n in nodes if n.type == 'GROUP_OUTPUT')
            geometry = node_socket(output.inputs, 'Geometry').links[0].from_socket
            attr = nodes.new('GeometryNodeInputNamedAttribute')
            attr.data_type = 'FLOAT'
            node_socket(attr.inputs, 'Name').default_value = 'qc_charge'
            valid = nodes.new('GeometryNodeInputNamedAttribute')
            valid.data_type = 'BOOLEAN'
            node_socket(valid.inputs, 'Name').default_value = 'qc_charge_valid'
            fraction = color_fraction(tree, inputs, node_socket(attr.outputs, 'Attribute'), 'Charge Minimum', 'Charge Center', 'Charge Maximum')
            for name, value, kind in [('qc_color_fraction', fraction, 'FLOAT'),
                                       ('qc_sample_valid', node_socket(valid.outputs, 'Attribute'), 'BOOLEAN')]:
                store = nodes.new('GeometryNodeStoreNamedAttribute')
                store.data_type, store.domain = kind, 'POINT'
                node_socket(store.inputs, 'Name').default_value = name
                links.new(geometry, node_socket(store.inputs, 'Geometry'))
                links.new(value, node_socket(store.inputs, 'Value'))
                geometry = node_socket(store.outputs, 'Geometry')
            assign = nodes.new('GeometryNodeSetMaterial')
            color_material = scalar_material()
            node_socket(assign.inputs, 'Material').default_value = color_material
            links.new(geometry, node_socket(assign.inputs, 'Geometry'))
            links.new(node_socket(assign.outputs, 'Geometry'), node_socket(output.inputs, 'Geometry'))
            frame_nodes(tree, [node for node in nodes if node not in existing_nodes], 'Charge: attributes and colors')
            existing_nodes = set(nodes)
            add_legend(obj, color_material, 'Charge Minimum', 'Charge Center', 'Charge Maximum', self.method + ' atomic charge [e]')
            frame_nodes(tree, [node for node in nodes if node not in existing_nodes], 'Legend: range and labels')
            tree['qc_charge_mapping'] = True
        else:
            for node in tree.nodes:
                if label_role(node) == 'QC Legend Title':
                    node_socket(node.inputs, 'String').default_value = self.method + ' atomic charge [e]'
            for item in tree.interface.items_tree:
                if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                    if socket_name(item, tree) == 'Charge Minimum':
                        view_modifier(obj)[item.identifier] = self.minimum
                    elif socket_name(item, tree) == 'Charge Center':
                        view_modifier(obj)[item.identifier] = (self.minimum + self.maximum) / 2
                    elif socket_name(item, tree) == 'Charge Maximum':
                        view_modifier(obj)[item.identifier] = self.maximum
        tag_view(tree)
        obj.update_tag()
        return {'FINISHED'}


class QCBLENDER_OT_dipole(bpy.types.Operator):
    bl_idname = 'qcblender.show_dipole'
    bl_label = 'Show Molecular Dipole'
    bl_description = 'Create a dipole vector at the source coordinate origin from the recorded molecular dipole; show its physical direction with an adjustable angstrom-per-Debye display scale'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        from .capabilities import poll_action
        return poll_action(cls, context, 'dipole')

    def execute(self, context):
        from ..i18n import iface, error_text
        parent = context.object
        data = load_dataset(bpy.path.abspath(parent['qc_dataset']))
        if 'dipole' not in data.metadata:
            self.report({'ERROR'}, iface('This source has no molecular dipole'))
            return {'CANCELLED'}
        prop = data.metadata['dipole']
        vector = data.arrays[prop['array']].copy()
        if prop['unit'] == 'e*bohr':
            vector *= 2.541746473
        elif prop['unit'] != 'debye':
            self.report({'ERROR'}, iface('Unsupported dipole unit'))
            return {'CANCELLED'}
        mesh = bpy.data.meshes.new('QC dipole carrier')
        obj = bpy.data.objects.new('QC dipole (Debye; physical direction)', mesh)
        context.collection.objects.link(obj)
        obj.parent = parent
        obj['qc_dipole_source'] = json.dumps(prop)
        obj['qc_view_kind'] = 'dipole'
        obj['qc_dipole_debye'] = vector.tolist()
        obj['qc_display_anchor'] = 'source coordinate origin'
        tree = bpy.data.node_groups.new('QC Vector Glyph v1', 'GeometryNodeTree')
        socket(tree, 'Vector (Debye)', 'NodeSocketVector', default=tuple(vector))
        socket(tree, 'Angstrom per Debye', 'NodeSocketFloat', default=.5, minimum=0)
        socket(tree, 'Radius', 'NodeSocketFloat', default=.04, minimum=.001)
        socket(tree, 'Geometry', 'NodeSocketGeometry', 'OUTPUT')
        nodes, links = tree.nodes, tree.links
        inputs, output = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
        length = nodes.new('ShaderNodeVectorMath')
        length.operation = 'LENGTH'
        links.new(node_socket(inputs.outputs, 'Vector (Debye)'), length.inputs[0])
        scale = nodes.new('ShaderNodeMath')
        scale.operation = 'MULTIPLY'
        links.new(node_socket(length.outputs, 'Value'), scale.inputs[0])
        links.new(node_socket(inputs.outputs, 'Angstrom per Debye'), scale.inputs[1])
        join = nodes.new('GeometryNodeJoinGeometry')
        # Cylinder is centered; the native cone extends from its base at z=0 to z=Depth.
        for node_type, fraction, center in [('GeometryNodeMeshCylinder', .8, .4), ('GeometryNodeMeshCone', .2, .8)]:
            primitive = nodes.new(node_type)
            node_socket(primitive.inputs, 'Vertices').default_value = 24
            height = nodes.new('ShaderNodeMath')
            height.operation = 'MULTIPLY'
            height.inputs[1].default_value = fraction
            links.new(scale.outputs[0], height.inputs[0])
            links.new(height.outputs[0], node_socket(primitive.inputs, 'Depth'))
            if node_type.endswith('Cylinder'):
                links.new(node_socket(inputs.outputs, 'Radius'), node_socket(primitive.inputs, 'Radius'))
            else:
                node_socket(primitive.inputs, 'Radius Top').default_value = 0
                radius = nodes.new('ShaderNodeMath')
                radius.operation = 'MULTIPLY'
                radius.inputs[1].default_value = 2.5
                links.new(node_socket(inputs.outputs, 'Radius'), radius.inputs[0])
                links.new(radius.outputs[0], node_socket(primitive.inputs, 'Radius Bottom'))
            shift = nodes.new('ShaderNodeMath')
            shift.operation = 'MULTIPLY'
            shift.inputs[1].default_value = center
            links.new(scale.outputs[0], shift.inputs[0])
            xyz = nodes.new('ShaderNodeCombineXYZ')
            links.new(shift.outputs[0], node_socket(xyz.inputs, 'Z'))
            transform = nodes.new('GeometryNodeTransform')
            links.new(node_socket(primitive.outputs, 'Mesh'), node_socket(transform.inputs, 'Geometry'))
            links.new(node_socket(xyz.outputs, 'Vector'), node_socket(transform.inputs, 'Translation'))
            links.new(node_socket(transform.outputs, 'Geometry'), node_socket(join.inputs, 'Geometry'))
        align = nodes.new('FunctionNodeAlignEulerToVector')
        align.axis = 'Z'
        links.new(node_socket(inputs.outputs, 'Vector (Debye)'), node_socket(align.inputs, 'Vector'))
        orient = nodes.new('GeometryNodeTransform')
        links.new(node_socket(join.outputs, 'Geometry'), node_socket(orient.inputs, 'Geometry'))
        links.new(node_socket(align.outputs, 'Rotation'), node_socket(orient.inputs, 'Rotation'))
        assign = nodes.new('GeometryNodeSetMaterial')
        node_socket(assign.inputs, 'Material').default_value = material('QC dipole gold', (1., .55, .06, 1))
        links.new(node_socket(orient.outputs, 'Geometry'), node_socket(assign.inputs, 'Geometry'))
        nonzero = nodes.new('ShaderNodeMath')
        nonzero.operation = 'GREATER_THAN'
        nonzero.inputs[1].default_value = 1e-12
        links.new(node_socket(length.outputs, 'Value'), nonzero.inputs[0])
        switch = nodes.new('GeometryNodeSwitch')
        switch.input_type = 'GEOMETRY'
        links.new(nonzero.outputs[0], node_socket(switch.inputs, 'Switch'))
        links.new(node_socket(assign.outputs, 'Geometry'), node_socket(switch.inputs, 'True'))
        links.new(node_socket(switch.outputs, 'Output'), node_socket(output.inputs, 'Geometry'))
        obj.modifiers.new('QC Dipole', 'NODES').node_group = tree
        for index, node in enumerate(nodes):
            node.location = (index % 5 * 220, -(index // 5) * 240)
        tag_view(tree)
        return {'FINISHED'}
