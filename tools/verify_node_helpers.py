"""Check atom-selection nodes and shared math inputs in native Blender."""
from pathlib import Path
import argparse
import importlib
import json
import math
import subprocess
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
parser = argparse.ArgumentParser()
parser.add_argument('--report', '--output', dest='report', type=Path, default=ROOT / 'outputs/node-helpers.json')
parser.add_argument('--module', default='qcblender', help='Source or installed extension package')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
assets = importlib.import_module(args.module + '.blender.assets')

def check():
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
    # Synthetic source atoms exercise engineering identity, not scientific accuracy.
    positions = [(0., 0., 0.), (1.25, -.5, 2.), (-2., .75, 1.5),
                 (3.5, 1.25, -.25), (-.75, -2., 4.), (2.25, 3., -1.5)]
    elements = [6, 1, 8, 6, 1, 8]
    charges = [-.75, .125, .5, -.25, 0., .875]
    valid = [True, True, False, True, False, True]
    mesh.from_pydata(positions, [], [])
    for name, kind, values in [('qc_atom_id', 'INT', list(range(6))),
                               ('qc_atomic_number', 'INT', elements),
                               ('qc_charge', 'FLOAT', charges),
                               ('qc_charge_valid', 'BOOLEAN', valid)]:
        mesh.attributes.new(name, kind, 'POINT').data.foreach_set('value', values)
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
    observations = []
    for order in [list(range(6)), [4, 1, 5, 0, 3, 2], list(reversed(range(6)))]:
        mesh.vertices.foreach_set('co', [coordinate for index in order for coordinate in positions[index]])
        for name, values in [('qc_atom_id', list(range(6))), ('qc_atomic_number', elements),
                             ('qc_charge', charges), ('qc_charge_valid', valid)]:
            mesh.attributes[name].data.foreach_set('value', [values[index] for index in order])
        mesh.update()
        for element, first, last, enabled, expected_ids in [
                (0, 1, 0, True, [0, 1, 2, 3, 4, 5]), (6, 1, 0, True, [0, 3]),
                (8, 1, 0, True, [2, 5]), (0, 2, 2, True, [1]),
                (6, 2, 5, True, [3]), (8, 2, 5, True, [2]),
                (8, 1, 2, True, []), (0, 3, 2, True, []), (0, 1, 0, False, [])]:
            for name, value in zip(('Element (0 = all)', 'First Atom (1-based)',
                                    'Last Atom (0 = all)', 'Selection'), (element, first, last, enabled)):
                selection.inputs[name].default_value = value
            obj.update_tag()
            bpy.context.view_layer.update()
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            result = evaluated.to_mesh()
            try:
                assert len(result.vertices) == len(expected_ids), 'Unexpected selection count'
                rows = []
                if expected_ids:
                    for name, kind in [('qc_atom_id', 'INT'), ('qc_atomic_number', 'INT'),
                                       ('qc_charge', 'FLOAT'), ('qc_charge_valid', 'BOOLEAN')]:
                        attribute = result.attributes.get(name)
                        assert attribute is not None, 'Source attribute missing: ' + name
                        assert (attribute.data_type, attribute.domain) == (kind, 'POINT'), name
                    for index, vertex in enumerate(result.vertices):
                        atom_id = result.attributes['qc_atom_id'].data[index].value
                        assert atom_id in expected_ids, ('Unexpected source ID', atom_id)
                        coordinate = tuple(vertex.co)
                        atomic_number = result.attributes['qc_atomic_number'].data[index].value
                        charge = result.attributes['qc_charge'].data[index].value
                        charge_valid = bool(result.attributes['qc_charge_valid'].data[index].value)
                        assert math.dist(coordinate, positions[atom_id]) < 1e-6, ('Position mismatch', atom_id, coordinate)
                        assert atomic_number == elements[atom_id], ('Element mismatch', atom_id)
                        assert abs(charge - charges[atom_id]) < 1e-6, ('Charge mismatch', atom_id)
                        assert charge_valid == valid[atom_id], ('Validity mismatch', atom_id)
                        rows.append(dict(atom_id=atom_id, position=coordinate, atomic_number=atomic_number,
                                         charge=charge, charge_valid=charge_valid))
                assert sorted(row['atom_id'] for row in rows) == expected_ids
                observations.append(dict(input_order=order, selection=[element, first, last, enabled], points=rows))
            finally:
                evaluated.to_mesh_clear()

    # No charge source must remain absent through GN instead of becoming valid zero.
    for name in ('qc_charge', 'qc_charge_valid'):
        mesh.attributes.remove(mesh.attributes[name])
    selection.inputs['Selection'].default_value = True
    selection.inputs['Element (0 = all)'].default_value = 0
    selection.inputs['First Atom (1-based)'].default_value = 1
    selection.inputs['Last Atom (0 = all)'].default_value = 0
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    result = evaluated.to_mesh()
    try:
        assert len(result.vertices) == 6
        assert all(result.attributes.get(name) is None for name in ('qc_charge', 'qc_charge_valid'))
    finally:
        evaluated.to_mesh_clear()
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
                  module=args.module, module_file=str(Path(assets.__file__).resolve()),
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  fixture='Synthetic atom attributes; engineering regression only', observations=observations,
                  checks=['source atom IDs and per-point positions/elements/charges/validity',
                          'missing charge attributes stay absent', 'v1 interface', 'stable identifiers',
                          'math input boundaries'])
    return report


destination = args.report
destination.parent.mkdir(parents=True, exist_ok=True)
try:
    report = check()
except Exception as error:
    destination.write_text(json.dumps(dict(status='Failed', module=args.module,
        error_type=type(error).__name__, error=str(error)), indent=2) + '\n', encoding='utf-8')
    raise
destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
