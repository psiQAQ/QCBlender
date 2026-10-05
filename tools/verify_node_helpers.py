"""Check atom-selection nodes and shared math inputs in native Blender."""
from pathlib import Path
import argparse
import json
import subprocess
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qcblender.blender import assets
parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, default=ROOT / 'outputs/node-helpers.json')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])

group = assets.selection_group()
assert assets.selection_group() == group
assert group['qc_asset_id'] == 'qc.atom_selection.v1'
# Public v1 contract, fixed from the 47fd82c compatibility snapshot.
expected_interface = [
    ('Selection', 'Socket_0', 'INPUT', 'NodeSocketBool', True),
    ('Element (0 = all)', 'Socket_1', 'INPUT', 'NodeSocketInt', 0),
    ('First Atom (1-based)', 'Socket_2', 'INPUT', 'NodeSocketInt', 1),
    ('Last Atom (0 = all)', 'Socket_3', 'INPUT', 'NodeSocketInt', 0),
    ('Selection', 'Socket_4', 'OUTPUT', 'NodeSocketBool', False)]
actual_interface = sorted(
    [(s.name, s.identifier, s.in_out, s.socket_type, s.default_value)
     for s in group.interface.items_tree if s.item_type == 'SOCKET'],
    key=lambda item: item[1])
assert actual_interface == expected_interface, actual_interface
identifiers = [(s.name, s.identifier) for s in group.interface.items_tree
               if s.item_type == 'SOCKET']
mesh = bpy.data.meshes.new('Selection check')
mesh.from_pydata([(0, 0, 0), (1, 0, 0), (2, 0, 0)], [], [])
for name, values in [('qc_atom_id', [0, 1, 2]), ('qc_atomic_number', [6, 1, 8])]:
    mesh.attributes.new(name, 'INT', 'POINT').data.foreach_set('value', values)
obj = bpy.data.objects.new('Selection check', mesh)
bpy.context.collection.objects.link(obj)
tree = bpy.data.node_groups.new('Selection check', 'GeometryNodeTree')
tree.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
source, output = tree.nodes.new('NodeGroupInput'), tree.nodes.new('NodeGroupOutput')
selection = tree.nodes.new('GeometryNodeGroup')
selection.node_tree = group
separate = tree.nodes.new('GeometryNodeSeparateGeometry')
tree.links.new(source.outputs['Geometry'], separate.inputs['Geometry'])
tree.links.new(selection.outputs['Selection'], separate.inputs['Selection'])
tree.links.new(separate.outputs['Selection'], output.inputs['Geometry'])
obj.modifiers.new('Selection check', 'NODES').node_group = tree
for element, first, last, enabled, expected_ids in [
        (0, 1, 0, True, [0, 1, 2]), (6, 1, 0, True, [0]),
        (8, 1, 0, True, [2]), (0, 2, 2, True, [1]),
        (8, 1, 2, True, []), (0, 3, 2, True, []), (0, 1, 0, False, [])]:
    for name, value in zip(('Element (0 = all)', 'First Atom (1-based)',
                            'Last Atom (0 = all)', 'Selection'), (element, first, last, enabled)):
        selection.inputs[name].default_value = value
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    assert len(evaluated.data.vertices) == len(expected_ids)
    actual_ids = []
    if expected_ids:
        attribute = evaluated.data.attributes.get('qc_atom_id')
        assert attribute is not None, 'Source atom IDs missing from selection'
        assert (attribute.data_type, attribute.domain) == ('INT', 'POINT')
        actual_ids = sorted(item.value for item in attribute.data)
    assert actual_ids == expected_ids, (element, first, last, enabled, actual_ids, expected_ids)
assert identifiers == [(s.name, s.identifier) for s in group.interface.items_tree
                       if s.item_type == 'SOCKET']
number = assets.math(tree, 'ADD', True, 2.5)
assert tuple(s.default_value for s in number.node.inputs[:2]) == (1., 2.5)
linked = assets.math(tree, 'MULTIPLY', number, 3)
assert linked.node.inputs[0].links[0].from_socket == number
assert linked.node.inputs[1].default_value == 3
try:
    assets.math(tree, 'ADD', 'invalid', 1)
except TypeError:
    pass
else:
    raise AssertionError('Non-socket input accepted')
print('NODE_HELPERS_PASSED: atom IDs, v1 interface, identifiers, reuse, numeric/socket inputs, invalid input')
report = dict(status='Passed', blender=bpy.app.version_string,
              source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              checks=['source atom IDs', 'v1 interface', 'stable identifiers', 'math input boundaries'])
destination = args.report
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
