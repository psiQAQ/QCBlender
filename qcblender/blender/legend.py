"""Explicit upgrade of the original QC geometry-node legend."""
import math

import bpy

from .graph import tag_view


def _link(input_socket):
    if len(input_socket.links) != 1:
        raise ValueError('Legacy legend connection is missing or customized')
    return input_socket.links[0].from_socket


def _legacy_legend(obj):
    """Return the old legend nodes only after checking its complete display branch."""
    from .copy_display import _state

    state = _state(obj)
    tree, modifier = state['modifier'].node_group, state['modifier']
    if tree.get('qc_legend_layout') or bool(tree.get('qc_color_mapping')) == bool(tree.get('qc_charge_mapping')):
        raise ValueError('Selected view has no legacy QC legend to upgrade')
    if any(name in state['sockets'] for name in ('Legend Length', 'Legend Width', 'Legend Text Size',
                                                'Legend Decimals', 'Legend Vertical', 'Legend Rotation')):
        raise ValueError('Legend layout inputs already exist')
    inputs = [node for node in tree.nodes if node.type == 'GROUP_INPUT']
    if len(inputs) != 1 or not {'Show Legend', 'Legend Position'} <= state['sockets'].keys():
        raise ValueError('Legacy legend controls are missing or ambiguous')
    inputs = inputs[0]
    switches = [node for node in tree.nodes if node.bl_idname == 'GeometryNodeSwitch'
                and node.input_type == 'GEOMETRY' and node.inputs['Switch'].links
                and _link(node.inputs['Switch']) == inputs.outputs['Show Legend']]
    if len(switches) != 1:
        raise ValueError('Legacy legend visibility branch is customized')
    show = switches[0]
    outer = _link(show.inputs['True']).node
    if (outer.bl_idname != 'GeometryNodeTransform'
            or _link(outer.inputs['Translation']) != inputs.outputs['Legend Position']
            or outer.inputs['Rotation'].links or tuple(outer.inputs['Rotation'].default_value) != (0, 0, 0)
            or show.inputs['False'].links):
        raise ValueError('Legacy legend transform is customized')
    legend = _link(outer.inputs['Geometry']).node
    if legend.bl_idname != 'GeometryNodeJoinGeometry':
        raise ValueError('Legacy legend geometry is customized')
    final_links = show.outputs['Output'].links
    if len(final_links) != 1 or final_links[0].to_node.bl_idname != 'GeometryNodeJoinGeometry':
        raise ValueError('Legacy legend output is customized')
    final = final_links[0].to_node
    branches = [link.from_socket for link in final.inputs['Geometry'].links]
    if len(branches) != 2 or show.outputs['Output'] not in branches or len(final.outputs['Geometry'].links) != 1:
        raise ValueError('Legacy legend display branch is customized')

    nodes = {show, outer, legend, final}
    bars, text_materials, titles = [], set(), []
    prefix = 'Charge' if tree.get('qc_charge_mapping') else 'Color'
    ranges = [prefix + ' ' + suffix for suffix in ('Minimum', 'Center', 'Maximum')]
    expected = dict(zip(ranges + [None], [(-1, -.28, 0), (-.2, -.28, 0),
                                          (.65, -.28, 0), (-1, .2, 0)]))
    legend_branches = [link.from_socket for link in legend.inputs['Geometry'].links]
    if len(legend_branches) != 5:
        raise ValueError('Legacy legend has an unsupported geometry branch')
    for branch in legend_branches:
        assign = branch.node
        if assign.bl_idname != 'GeometryNodeSetMaterial' or branch != assign.outputs['Geometry']:
            raise ValueError('Legacy legend material branch is customized')
        nodes.add(assign)
        previous = _link(assign.inputs['Geometry']).node
        if previous.bl_idname == 'GeometryNodeStoreNamedAttribute':
            bars.append((assign, previous))
            continue
        if previous.bl_idname != 'GeometryNodeTransform' or previous.inputs['Translation'].links:
            raise ValueError('Legacy legend text transform is customized')
        if assign.inputs['Material'].is_linked or assign.inputs['Material'].default_value is None:
            raise ValueError('Legacy legend text material is customized')
        offset = tuple(previous.inputs['Translation'].default_value)
        fill = _link(previous.inputs['Geometry']).node
        realize = _link(fill.inputs['Curve']).node if fill.bl_idname == 'GeometryNodeFillCurve' else None
        text = _link(realize.inputs['Geometry']).node if realize and realize.bl_idname == 'GeometryNodeRealizeInstances' else None
        if text is None or text.bl_idname != 'GeometryNodeStringToCurves' or text.inputs['Size'].links \
                or not math.isclose(text.inputs['Size'].default_value, .16, abs_tol=1e-6):
            raise ValueError('Legacy legend text geometry is customized')
        number = _link(text.inputs['String']).node if text.inputs['String'].links else None
        label = number.label if number and number.bl_idname == 'FunctionNodeValueToString' else None
        if label not in expected or any(math.fabs(a - b) > 1e-6 for a, b in zip(offset, expected[label])):
            raise ValueError('Legacy legend text layout is customized')
        if label:
            if number.inputs['Decimals'].links or number.inputs['Decimals'].default_value != 5 \
                    or _link(number.inputs['Value']) != inputs.outputs[label]:
                raise ValueError('Legacy legend number source is customized')
            nodes.add(number)
        elif text.label != 'QC Legend Title':
            raise ValueError('Legacy legend title is customized')
        if label is None:
            titles.append(text)
        else:
            ranges.remove(label)
        text_materials.add(assign.inputs['Material'].default_value)
        nodes.update((previous, fill, realize, text))
    if len(bars) != 1 or len(titles) != 1 or ranges or len(text_materials) != 1:
        raise ValueError('Legacy legend branches are missing or ambiguous')
    bar_assign, store = bars[0]
    role = 'charge_map' if prefix == 'Charge' else 'scalar_map'
    if bar_assign.inputs['Material'].is_linked or \
            bar_assign.inputs['Material'].default_value != state['materials'][role][0]:
        raise ValueError('Legacy legend no longer uses its QC color material')
    for name, kind in (('qc_legend', 'BOOLEAN'), ('qc_sample_valid', 'BOOLEAN'),
                       ('qc_color_fraction', 'FLOAT')):
        if store.bl_idname != 'GeometryNodeStoreNamedAttribute' or store.data_type != kind \
                or store.inputs['Name'].default_value != name or store.domain != 'POINT':
            raise ValueError('Legacy legend color attributes are customized')
        nodes.add(store)
        if name != 'qc_color_fraction' and (store.inputs['Value'].links or
                                            not store.inputs['Value'].default_value):
            raise ValueError('Legacy legend validity attributes are customized')
        if name == 'qc_color_fraction':
            fraction = _link(store.inputs['Value']).node
            if fraction.bl_idname != 'ShaderNodeMapRange' or \
                    fraction.inputs['From Min'].links or fraction.inputs['From Max'].links or \
                    fraction.inputs['From Min'].default_value != -1 or \
                    fraction.inputs['From Max'].default_value != 1:
                raise ValueError('Legacy legend color range is customized')
            xyz_output = _link(fraction.inputs['Value'])
            xyz = xyz_output.node
            position_output = _link(xyz.inputs['Vector']) if xyz.bl_idname == 'ShaderNodeSeparateXYZ' else None
            position = position_output.node if position_output else None
            if position is None or position.bl_idname != 'GeometryNodeInputPosition':
                raise ValueError('Legacy legend color coordinates are customized')
            if xyz_output != xyz.outputs['X'] or position_output != position.outputs['Position']:
                raise ValueError('Legacy legend color axis is customized')
            nodes.update((fraction, xyz, position))
        store = _link(store.inputs['Geometry']).node
    if store.bl_idname != 'GeometryNodeMeshGrid' or \
            any(store.inputs[name].links or not math.isclose(store.inputs[name].default_value, value,
                                                            abs_tol=1e-6)
                for name, value in (('Size X', 2), ('Size Y', .18),
                                    ('Vertices X', 65), ('Vertices Y', 2))):
        raise ValueError('Legacy legend grid is customized')
    nodes.add(store)
    if any(link.to_node not in nodes for node in nodes - {final} for output in node.outputs for link in output.links):
        raise ValueError('Legacy legend nodes have custom external connections')
    return modifier, nodes, final, show, bar_assign.inputs['Material'].default_value, \
        next(iter(text_materials)), titles[0].inputs['String'].default_value, prefix


def upgrade_legend(obj):
    """Replace a checked legacy legend in one view, preserving its other graph and values."""
    from .scalars import add_legend

    modifier, old_nodes, final, show, color_mat, text_mat, title, prefix = _legacy_legend(obj)
    old_tree = modifier.node_group
    values = {item.name: modifier.get(item.identifier, item.default_value)
              for item in old_tree.interface.items_tree
              if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
    old_properties = {key: modifier[key] for key in modifier.keys()}
    clone = old_tree.copy()
    try:
        final_copy, show_copy = clone.nodes[final.name], clone.nodes[show.name]
        destination = final_copy.outputs['Geometry'].links[0].to_socket
        original = next(link.from_socket for link in final_copy.inputs['Geometry'].links
                        if link.from_node != show_copy)
        for node in old_nodes:
            clone.nodes.remove(clone.nodes[node.name])
        clone.links.new(original, destination)
        add_legend(obj, color_mat, *(prefix + ' ' + part for part in
                   ('Minimum', 'Center', 'Maximum')), title,
                   tree=clone, text_material=text_mat, destination=destination)
        clone['qc_legend_layout'] = 1
        tag_view(clone)
        modifier.node_group = clone
        for item in clone.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                modifier[item.identifier] = values.get(item.name, item.default_value)
        obj.update_tag()
    except Exception:
        modifier.node_group = old_tree
        for key in set(modifier.keys()) - old_properties.keys():
            del modifier[key]
        for key, value in old_properties.items():
            modifier[key] = value
        if clone.users == 0:
            bpy.data.node_groups.remove(clone)
        raise


class QCBLENDER_OT_upgrade_legend(bpy.types.Operator):
    bl_idname = 'qcblender.upgrade_legend'
    bl_label = 'Upgrade QC Legend'
    bl_description = 'Upgrade a known QC legend to editable layout controls'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        try:
            upgrade_legend(context.object)
        except (ValueError, KeyError, TypeError, AttributeError, ReferenceError, RuntimeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}
