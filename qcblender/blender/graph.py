"""Locate QC controls without depending on modifier order or editable labels."""
import json


def view_modifier(obj):
    candidates = [m for m in obj.modifiers if m.type == 'NODES' and m.node_group]
    tagged = [m for m in candidates if m.node_group.get('qc_view_graph')]
    if len(tagged) == 1:
        return tagged[0]
    # Saved v1 graphs have no tag. Only accept an unambiguous QC graph.
    legacy = [m for m in candidates if m.name.startswith('QC ') and m.node_group.name.startswith('QC ')]
    if not tagged and len(legacy) == 1:
        return legacy[0]
    raise ValueError('Cannot identify a unique QC display modifier; select or restore its QC graph')


def tag_view(tree):
    tree['qc_view_graph'] = 2
    tree['qc_sockets'] = json.dumps({s.name: s.identifier for s in tree.interface.items_tree
                                    if s.item_type == 'SOCKET' and s.in_out == 'INPUT'})


def geometry_output(tree):
    outputs = [n for n in tree.nodes if n.type == 'GROUP_OUTPUT' and n.is_active_output]
    if len(outputs) != 1:
        raise ValueError('Expected one active geometry output')
    return next(s for s in outputs[0].inputs if s.type == 'GEOMETRY')


def append_branch(tree, geometry):
    output = geometry_output(tree)
    previous = output.links[0].from_socket if output.links else None
    if previous and previous.node.bl_idname == 'GeometryNodeJoinGeometry':
        join = previous.node
    else:
        join = tree.nodes.new('GeometryNodeJoinGeometry')
        if previous:
            tree.links.new(previous, join.inputs['Geometry'])
        tree.links.new(join.outputs['Geometry'], output)
    tree.links.new(geometry, join.inputs['Geometry'])


def insert_geometry(tree, group, input_name='Geometry', output_name='Geometry'):
    output = geometry_output(tree)
    if not output.links:
        raise ValueError('Display graph has no connected geometry output')
    previous = output.links[0].from_socket
    node = tree.nodes.new('GeometryNodeGroup')
    node.node_tree = group
    tree.links.new(previous, node.inputs[input_name])
    tree.links.new(node.outputs[output_name], output)
    return node
