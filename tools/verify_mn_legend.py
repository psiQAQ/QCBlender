"""Installed-extension acceptance for configurable and legacy QC legends."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_vmd_parameters as base


LAYOUT = ('Legend Length', 'Legend Width', 'Legend Text Size', 'Legend Decimals',
          'Legend Vertical', 'Legend Rotation')
DEFAULTS = (2., .18, .16, 5, False, (0., 0., 0.))


def values(obj, names=LAYOUT):
    modifier, sockets = base.controls(obj)
    result = []
    for name in names:
        value = modifier[sockets[name]]
        result.append(tuple(value) if hasattr(value, 'to_list') else value)
    return tuple(result)


def bar_samples(obj):
    """Read the evaluated color bar, not just the authored GN socket values."""
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        marked = mesh.attributes['qc_legend'].data
        fractions = mesh.attributes['qc_color_fraction'].data
        return [(tuple(vertex.co), fractions[i].value) for i, vertex in enumerate(mesh.vertices)
                if marked[i].value]
    finally:
        evaluated.to_mesh_clear()


def check_bar(obj, length, width, vertical=False, rotation=0):
    samples = bar_samples(obj)
    assert len(samples) == 130, len(samples)
    modifier, names = base.controls(obj)
    position = np.array(modifier[names['Legend Position']], dtype=float)
    points = np.array([point for point, _ in samples]) - position
    fractions = np.array([fraction for _, fraction in samples])
    assert np.isclose(fractions.min(), 0, atol=1e-5)
    assert np.isclose(fractions.max(), 1, atol=1e-5)
    assert np.any(np.isclose(fractions, .5, atol=1e-5))
    assert np.allclose(points.mean(axis=0), 0, atol=1e-4)
    assert np.allclose(points[:, 2], 0, atol=1e-4)
    if vertical:
        assert np.isclose(np.ptp(points[:, 0]), width, atol=1e-4)
        assert np.isclose(np.ptp(points[:, 1]), length, atol=1e-4)
    elif rotation:
        expected_x = abs(length * math.cos(rotation)) + abs(width * math.sin(rotation))
        expected_y = abs(length * math.sin(rotation)) + abs(width * math.cos(rotation))
        assert np.isclose(np.ptp(points[:, 0]), expected_x, atol=1e-4)
        assert np.isclose(np.ptp(points[:, 1]), expected_y, atol=1e-4)
    else:
        assert np.isclose(np.ptp(points[:, 0]), length, atol=1e-4)
        assert np.isclose(np.ptp(points[:, 1]), width, atol=1e-4)
    return {'vertices': len(samples), 'fraction': [float(fractions.min()), float(fractions.max())],
            'extent': [float(np.ptp(points[:, axis])) for axis in (0, 1)]}


def graph_text_controls(obj, prefix):
    tree = base.controls(obj)[0].node_group
    inputs = next(node for node in tree.nodes if node.type == 'GROUP_INPUT')
    browser = base.module('blender.source_browser')
    _, title = browser.color_mapping(obj)
    assert title.label == 'QC Legend Title'
    assert title.inputs['Size'].links[0].from_socket == inputs.outputs['Legend Text Size']
    numbers = [node for node in tree.nodes if node.bl_idname == 'FunctionNodeValueToString'
               and node.label.startswith(prefix + ' ')]
    assert {node.label for node in numbers} == {prefix + ' ' + word for word in
                                               ('Minimum', 'Center', 'Maximum')}
    for number in numbers:
        assert number.inputs['Decimals'].links[0].from_socket == inputs.outputs['Legend Decimals']
        assert number.inputs['Value'].links[0].from_socket == inputs.outputs[number.label]
    return title.inputs['String'].default_value


def legacy_fixture(obj):
    """Convert an isolated new view into the exact pre-layout legend graph."""
    modifier, names = base.controls(obj)
    tree = modifier.node_group
    inputs = next(node for node in tree.nodes if node.type == 'GROUP_INPUT')
    show = next(node for node in tree.nodes if node.bl_idname == 'GeometryNodeSwitch'
                and node.input_type == 'GEOMETRY' and node.inputs['Switch'].links
                and node.inputs['Switch'].links[0].from_socket == inputs.outputs['Show Legend'])
    final = show.outputs['Output'].links[0].to_node
    destination = final.outputs['Geometry'].links[0].to_socket
    original = next(link.from_socket for link in final.inputs['Geometry'].links if link.from_node != show)
    legend = show.inputs['True'].links[0].from_node.inputs['Geometry'].links[0].from_node
    branches = [link.from_node for link in legend.inputs['Geometry'].links]
    color = next(node.inputs['Material'].default_value for node in branches
                 if node.inputs['Geometry'].links[0].from_node.bl_idname == 'GeometryNodeSwitch')
    text_material = next(node.inputs['Material'].default_value for node in branches
                         if node.inputs['Geometry'].links[0].from_node.bl_idname == 'GeometryNodeTransform')
    title = base.module('blender.source_browser').color_mapping(obj)[1].inputs['String'].default_value
    old_nodes = {final}

    def collect(node):
        if node in old_nodes or node == inputs:
            return
        old_nodes.add(node)
        for socket in node.inputs:
            for link in socket.links:
                collect(link.from_node)

    collect(show)
    for node in old_nodes:
        tree.nodes.remove(node)
    tree.links.new(original, destination)
    for name in LAYOUT:
        tree.interface.remove(next(item for item in tree.interface.items_tree
                                   if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.name == name))
    del tree['qc_legend_layout']
    for name in LAYOUT:
        if names[name] in modifier:
            del modifier[names[name]]

    nodes, links = tree.nodes, tree.links
    grid = nodes.new('GeometryNodeMeshGrid')
    for name, value in (('Size X', 2), ('Size Y', .18), ('Vertices X', 65), ('Vertices Y', 2)):
        grid.inputs[name].default_value = value
    position = nodes.new('GeometryNodeInputPosition')
    xyz = nodes.new('ShaderNodeSeparateXYZ')
    links.new(position.outputs['Position'], xyz.inputs['Vector'])
    fraction = nodes.new('ShaderNodeMapRange')
    fraction.inputs['From Min'].default_value = -1
    fraction.inputs['From Max'].default_value = 1
    links.new(xyz.outputs['X'], fraction.inputs['Value'])
    geometry = grid.outputs['Mesh']
    for name, kind, value in (('qc_color_fraction', 'FLOAT', fraction.outputs['Result']),
                              ('qc_sample_valid', 'BOOLEAN', True), ('qc_legend', 'BOOLEAN', True)):
        store = nodes.new('GeometryNodeStoreNamedAttribute')
        store.data_type, store.domain = kind, 'POINT'
        store.inputs['Name'].default_value = name
        links.new(geometry, store.inputs['Geometry'])
        if value is True:
            store.inputs['Value'].default_value = True
        else:
            links.new(value, store.inputs['Value'])
        geometry = store.outputs['Geometry']
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.inputs['Material'].default_value = color
    links.new(geometry, assign.inputs['Geometry'])
    legend = nodes.new('GeometryNodeJoinGeometry')
    links.new(assign.outputs['Geometry'], legend.inputs['Geometry'])
    for label, offset in (('Color Minimum', (-1, -.28, 0)), ('Color Center', (-.2, -.28, 0)),
                          ('Color Maximum', (.65, -.28, 0)), (None, (-1, .2, 0))):
        text = nodes.new('GeometryNodeStringToCurves')
        text.inputs['Size'].default_value = .16
        if label:
            number = nodes.new('FunctionNodeValueToString')
            number.label = label
            number.inputs['Decimals'].default_value = 5
            links.new(inputs.outputs[label], number.inputs['Value'])
            links.new(number.outputs['String'], text.inputs['String'])
        else:
            text.label = 'QC Legend Title'
            text.inputs['String'].default_value = title
        realize = nodes.new('GeometryNodeRealizeInstances')
        links.new(text.outputs['Curve Instances'], realize.inputs['Geometry'])
        fill = nodes.new('GeometryNodeFillCurve')
        links.new(realize.outputs['Geometry'], fill.inputs['Curve'])
        transform = nodes.new('GeometryNodeTransform')
        transform.inputs['Translation'].default_value = offset
        links.new(fill.outputs['Mesh'], transform.inputs['Geometry'])
        text_assign = nodes.new('GeometryNodeSetMaterial')
        text_assign.inputs['Material'].default_value = text_material
        links.new(transform.outputs['Geometry'], text_assign.inputs['Geometry'])
        links.new(text_assign.outputs['Geometry'], legend.inputs['Geometry'])
    transform = nodes.new('GeometryNodeTransform')
    links.new(legend.outputs['Geometry'], transform.inputs['Geometry'])
    links.new(inputs.outputs['Legend Position'], transform.inputs['Translation'])
    show = nodes.new('GeometryNodeSwitch')
    show.input_type = 'GEOMETRY'
    links.new(inputs.outputs['Show Legend'], show.inputs['Switch'])
    links.new(transform.outputs['Geometry'], show.inputs['True'])
    final = nodes.new('GeometryNodeJoinGeometry')
    links.new(original, final.inputs['Geometry'])
    links.new(show.outputs['Output'], final.inputs['Geometry'])
    links.new(final.outputs['Geometry'], destination)
    base.module('blender.graph').tag_view(tree)
    obj.update_tag()


def check_legend(out):
    out.mkdir(parents=True, exist_ok=True)
    before = base.hashes()
    for obj in bpy.context.scene.objects:
        if obj.type not in ('CAMERA', 'LIGHT'):
            obj.hide_render = True
    fields = base.real_fields(out)
    view, color = fields['electron_number_density'], fields['electrostatic_potential']
    view.name, color.name = 'MN legend surface', 'MN legend ESP source'
    view.hide_render = False
    base.activate(view)
    assert bpy.ops.qcblender.select_color_field(source_name=color.name, minimum=-.05, maximum=.05) == {'FINISHED'}
    modifier, names = base.controls(view)
    assert np.allclose(values(view)[:3], DEFAULTS[:3])
    assert values(view)[3:5] == DEFAULTS[3:5]
    assert np.allclose(values(view)[5], DEFAULTS[5])
    assert graph_text_controls(view, 'Color') == 'ESP [hartree/e]'
    original_range = values(view, ('Color Minimum', 'Color Center', 'Color Maximum'))
    material = base.module('blender.copy_display')._state(view)['materials']['scalar_map'][0]
    modifier[names['Show Legend']] = True
    modifier[names['Legend Position']] = (2.5, 0, 0)
    report = {'checks': {}, 'bars': {}, 'renders': {}}
    report['bars']['default'] = check_bar(view, 2, .18)
    report['renders']['default'] = base.render(out / 'default.png')
    for name, value in {'Legend Length': 3.2, 'Legend Width': .28,
                        'Legend Text Size': .22, 'Legend Decimals': 2}.items():
        modifier[names[name]] = value
    report['bars']['horizontal'] = check_bar(view, 3.2, .28)
    report['renders']['horizontal'] = base.render(out / 'horizontal.png')
    modifier[names['Legend Vertical']] = True
    modifier[names['Legend Length']] = 2.6
    modifier[names['Legend Width']] = .2
    report['bars']['vertical'] = check_bar(view, 2.6, .2, vertical=True)
    report['renders']['vertical'] = base.render(out / 'vertical.png')
    modifier[names['Legend Vertical']] = False
    modifier[names['Legend Rotation']] = (0, 0, math.pi / 4)
    report['bars']['rotated'] = check_bar(view, 2.6, .2, rotation=math.pi / 4)
    report['renders']['rotated'] = base.render(out / 'rotated.png')
    assert graph_text_controls(view, 'Color') == 'ESP [hartree/e]'
    assert values(view, ('Color Minimum', 'Color Center', 'Color Maximum')) == original_range
    assert base.module('blender.copy_display')._state(view)['materials']['scalar_map'][0] == material
    report['checks']['default_layout_variants_range_material'] = 'Passed'

    layout = values(view)
    assert bpy.ops.qcblender.select_color_field(source_name=view.name) == {'FINISHED'}
    assert graph_text_controls(view, 'Color') == 'Electron density [electron/bohr^3]'
    assert values(view) == layout
    assert values(view, ('Color Minimum', 'Color Center', 'Color Maximum')) == original_range
    assert bpy.ops.qcblender.select_color_field(source_name=color.name) == {'FINISHED'}
    assert graph_text_controls(view, 'Color') == 'ESP [hartree/e]'
    report['checks']['color_replacement_preserves_layout'] = 'Passed'

    layers = base.module('blender.layers')
    target = layers.copy_layer(view, bpy.context.collection)
    target.name = 'MN independent legend layout'
    target.hide_render = True
    target_modifier, target_names = base.controls(target)
    target_modifier[target_names['Legend Length']] = 1.4
    target_modifier[target_names['Legend Vertical']] = True
    target_modifier[target_names['Legend Position']] = (-2, 1, 0)
    target_layout = values(target)
    modifier[names['Legend Length']] = 2.9
    base.activate(view)
    target.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    assert values(target) == target_layout
    assert target_modifier[target_names['Show Legend']]
    assert values(target, ('Color Minimum', 'Color Center', 'Color Maximum')) == original_range
    assert graph_text_controls(target, 'Color') == 'ESP [hartree/e]'
    report['checks']['copy_keeps_target_layout'] = 'Passed'

    legacy = layers.copy_layer(view, bpy.context.collection)
    legacy.name, legacy.hide_render = 'MN legacy upgrade', True
    legacy_fixture(legacy)
    assert not base.controls(legacy)[0].node_group.get('qc_legend_layout')
    base.activate(legacy)
    assert bpy.ops.qcblender.upgrade_legend() == {'FINISHED'}
    assert base.controls(legacy)[0].node_group.get('qc_legend_layout') == 1
    assert values(legacy)[3:5] == DEFAULTS[3:5]
    assert graph_text_controls(legacy, 'Color') == 'ESP [hartree/e]'
    check_bar(legacy, 2, .18)
    report['checks']['legacy_upgrade'] = 'Passed'
    custom = layers.copy_layer(view, bpy.context.collection)
    custom.name, custom.hide_render = 'MN custom legacy rejected', True
    legacy_fixture(custom)
    tree = base.controls(custom)[0].node_group
    title = base.module('blender.source_browser').color_mapping(custom)[1]
    title.inputs['Size'].default_value = .22
    before_graph = (tree.as_pointer(), len(tree.nodes), tuple(item.name for item in tree.interface.items_tree))
    base.activate(custom)
    assert bpy.ops.qcblender.upgrade_legend() == {'CANCELLED'}
    assert before_graph == (tree.as_pointer(), len(tree.nodes),
                            tuple(item.name for item in tree.interface.items_tree))
    assert title.inputs['Size'].default_value == .22
    report['checks']['custom_legacy_rejected_without_change'] = 'Passed'
    after = base.hashes()
    assert all(after.get(key) == value for key, value in before.items())

    base.activate(view)
    view.hide_render = False
    report['renders']['final'] = base.render(out / 'evidence.png')
    base.save_evidence(out, report)
    return report


def check_reopen(out):
    obj = bpy.data.objects['MN legend surface']
    assert graph_text_controls(obj, 'Color') == 'ESP [hartree/e]'
    assert base.controls(obj)[0].node_group.get('qc_legend_layout') == 1
    check_bar(obj, 2.9, .2, rotation=math.pi / 4)
    upgraded = bpy.data.objects['MN legacy upgrade']
    assert base.controls(upgraded)[0].node_group.get('qc_legend_layout') == 1
    custom = bpy.data.objects['MN custom legacy rejected']
    assert not base.controls(custom)[0].node_group.get('qc_legend_layout')
    assert base.module('blender.source_browser').color_mapping(custom)[1].inputs['Size'].default_value == .22
    return base.check_reopen(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', choices=('legend', 'reopen'), required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.preferences.addon_enable(module=base.MODULE)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    result = {'legend': check_legend, 'reopen': check_reopen}[args.check](args.out)
    print(json.dumps(result, ensure_ascii=False))
