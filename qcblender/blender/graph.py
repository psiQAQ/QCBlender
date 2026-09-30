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


def arrange(tree):
    """Lay out a newly built graph by dependency depth; never rearrange saved user graphs."""
    pending = list(tree.nodes)
    depths, counts = {}, {}
    while pending:
        ready = [n for n in pending if all(l.from_node in depths for s in n.inputs for l in s.links)]
        if not ready:
            ready = [pending[0]]
        for node in ready:
            depth = max((depths.get(l.from_node, -1) + 1 for s in node.inputs for l in s.links), default=0)
            row = counts.get(depth, 0)
            node.location = (depth * 240, -row * 240)
            node.width = 190
            depths[node], counts[depth] = depth, row + 1
            pending.remove(node)
    return tree


def frame_nodes(tree, nodes, title, origin=None):
    """Arrange only the supplied outer-view nodes inside one explanatory frame."""
    nodes = list(nodes)
    if not nodes:
        return
    if tree.get('qc_asset_id') or any(node.type == 'FRAME' or node.parent for node in nodes):
        raise ValueError('Layout requires unparented outer-view nodes')
    if origin is None:
        right = 0
        for node in tree.nodes:
            if node in nodes:
                continue
            x = node.location.x
            parent = node.parent
            while parent:
                x += parent.location.x
                parent = parent.parent
            right = max(right, x + node.width)
        origin = (right + 320, 0)
    frame = tree.nodes.new('NodeFrame')
    frame.label = title
    frame.location = origin
    depths, rows = {}, {}
    pending = list(nodes)
    while pending:
        ready = [node for node in pending if all(link.from_node not in nodes or link.from_node in depths
                 for socket in node.inputs for link in socket.links)] or [pending[0]]
        for node in ready:
            depth = max((depths[link.from_node] + 1 for socket in node.inputs for link in socket.links
                         if link.from_node in depths), default=0)
            row = rows.get(depth, 0)
            node.parent = frame
            node.location = (depth * 300, -row * 300)
            node.width = 220
            depths[node], rows[depth] = depth, row + 1
            pending.remove(node)
    return frame
