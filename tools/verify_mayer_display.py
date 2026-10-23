"""Verify real P04 Mayer geometry, filtering, step preflight and portable cold read.

Run serially in a fresh Blender process. Use --module bl_ext.user_default.qcblender
for the installed candidate; source runs may explicitly pass --science-site.
"""
import argparse
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback

import bpy
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--module', default='qcblender')
parser.add_argument('--science-site', type=Path)
parser.add_argument('--package-root', type=Path, help='Source package with built node assets')
parser.add_argument('--output-dir', required=True, type=Path)
parser.add_argument('--reopen', action='store_true')
parser.add_argument('--render', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / ('reopen.json' if args.reopen else 'native.json')
bpy.context.preferences.view.language = 'en_US'
if args.module == 'qcblender':
    sys.path.insert(0, str(args.package_root.resolve().parent if args.package_root else ROOT))
    if args.science_site:
        sys.path.insert(1, str(args.science_site.resolve()))
    importlib.import_module(args.module).register()
else:
    assert args.science_site is None and args.package_root is None, 'Installed verification must use packaged dependencies'
    bpy.ops.preferences.addon_enable(module=args.module)


def api(name):
    return importlib.import_module(args.module + '.' + name)


load_dataset = api('data').load_dataset
view_modifier = api('blender.graph').view_modifier
node_socket = api('blender.node_identity').node_socket
interface_socket = api('blender.node_identity').interface_socket
mayer = api('blender.mayer')
SOURCE = ROOT / 'validation/shared/data/public/P04'


def activate(obj):
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def science(root, table):
    return {obj.name: {key: hashlib.sha256(value.tobytes()).hexdigest()
                      for key, value in load_dataset(bpy.path.abspath(obj['qc_dataset'])).arrays.items()}
            for obj in (root, table)}


def control(root, name, value):
    modifier = view_modifier(root)
    item = interface_socket(modifier.node_group, name)
    modifier[item.identifier] = value
    root.update_tag()
    bpy.context.view_layer.update()


def evaluated(root):
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    obj = root.evaluated_get(graph)
    mesh = obj.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
    try:
        positions = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        edges = np.empty(len(mesh.edges) * 2, dtype=np.int32)
        mesh.vertices.foreach_get('co', positions)
        mesh.edges.foreach_get('vertices', edges)
        geometry = hashlib.sha256(positions.tobytes() + edges.tobytes()).hexdigest()
        pair_attr = mesh.attributes.get('qc_mayer_pair')
        fractions = mesh.attributes.get('qc_color_fraction')
        result = {}
        if pair_attr:
            assert pair_attr.domain == 'POINT' and fractions.domain == 'POINT'
            for index, item in enumerate(pair_attr.data):
                if item.value > 0:
                    result.setdefault(item.value, []).append(fractions.data[index].value)
        return geometry, result
    finally:
        obj.to_mesh_clear()


def check_pairs(root, data, ids, bounds):
    _, values = evaluated(root)
    assert set(values) == set(ids), (set(values), set(ids))
    orders = data.arrays['mayer_orders'][int(root['qc_irc_step']) - 1]
    for pair_id, fractions in values.items():
        expected = np.clip((orders[pair_id - 1] - bounds[0]) / (bounds[1] - bounds[0]), 0, 1)
        np.testing.assert_allclose(fractions, expected, atol=2e-6, rtol=0)
    return {str(key): {'vertices': len(value), 'fraction': value[0]} for key, value in values.items()}


def expect_cancel(operation, fragment):
    try:
        result = operation()
    except RuntimeError as error:
        assert fragment in str(error), str(error)
    else:
        assert result == {'CANCELLED'}, result


def main():
    if args.reopen:
        previous = json.loads((OUT / 'native.json').read_text(encoding='utf-8'))
        root = next(obj for obj in bpy.context.scene.objects if obj.get('qc_irc'))
        table = mayer.mayer_table(root)
        assert root.get('qc_mayer_enabled') and root['qc_irc_step'] == 2
        assert json.loads(table['qc_mayer_settings']) == previous['settings']
        assert science(root, table) == previous['science']
        data = load_dataset(bpy.path.abspath(table['qc_dataset']))
        path = load_dataset(bpy.path.abspath(root['qc_dataset']))
        mayer.prepare_update(root, path, 2)
        pairs = check_pairs(root, data, (1, 2, 5), (0., 1.))
        assert pairs == previous['saved_pairs']
        activate(root)
        assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
        check_pairs(root, data, (1, 2, 5), (0., 1.))
        assert bpy.ops.qcblender.irc_step(direction='PREV') == {'FINISHED'}
        return {'cold_reopen': 'Passed', 'step_change_after_reopen': 'Passed', 'science': science(root, table)}

    assert not bpy.data.filepath, 'Fresh verification must start without a user project'
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    assert bpy.ops.qcblender.import_irc_path(manifest_path=str(SOURCE / 'steps.csv')) == {'FINISHED'}
    root = next(obj for obj in bpy.context.scene.objects if obj.get('qc_irc'))
    activate(root)
    assert bpy.ops.qcblender.import_irc_mayer(manifest_path=str(SOURCE / 'mayer-pyscf.csv')) == {'FINISHED'}
    table = mayer.mayer_table(root)
    path = load_dataset(bpy.path.abspath(root['qc_dataset']))
    data = load_dataset(bpy.path.abspath(table['qc_dataset']))
    before_science = science(root, table)
    original_edges = [list(edge.vertices) for edge in root.data.edges]
    original_positions = [list(vertex.co) for vertex in root.data.vertices]
    modifier = view_modifier(root)
    original_style = modifier[interface_socket(modifier.node_group, mayer.STYLE).identifier]
    baseline = evaluated(root)[0]
    activate(root)
    assert bpy.ops.qcblender.add_annotation(kind='DISTANCE', atoms='1,2', visible=False) == {'FINISHED'}
    activate(root)
    assert bpy.ops.qcblender.mayer_display(enabled=True) == {'FINISHED'}
    carrier = table['qc_mayer_carrier_object']
    assert len(table.data.vertices) == 0 and len(carrier.data.vertices) == 12
    assert modifier[interface_socket(modifier.node_group, mayer.STYLE).identifier] == original_style
    _, _, values, _, _, _ = api('blender.ui').view_parameter_state(root)
    assert values[mayer.STYLE] == 0, 'Properties must show the effective atom-ball controls'
    bounds = api('mayer').color_range(data)
    all_pairs = check_pairs(root, data, range(1, 7), bounds)
    inferred = {tuple(sorted(index + 1 for index in edge)) for edge in original_edges}
    assert any(tuple(pair) not in inferred for pair in data.arrays['mayer_pairs'])
    assert bpy.ops.qcblender.mayer_settings(use_threshold=True, threshold=.5) == {'FINISHED'}
    check_pairs(root, data, (1, 2, 5), bounds)
    assert bpy.ops.qcblender.mayer_settings(use_threshold=False) == {'FINISHED'}
    control(root, 'Element (0 = all)', 8)
    check_pairs(root, data, (1,), bounds)
    control(root, 'Element (0 = all)', 0)
    assert bpy.ops.qcblender.local_selection(mode='REPLACE', numbers='1,2') == {'FINISHED'}
    check_pairs(root, data, (1,), bounds)
    assert bpy.ops.qcblender.local_selection(mode='CLEAR') == {'FINISHED'}
    for direction, step in (('NEXT', 2), ('NEXT', 3), ('PREV', 2)):
        assert bpy.ops.qcblender.irc_step(direction=direction) == {'FINISHED'}
        assert root['qc_irc_step'] == step
        np.testing.assert_allclose([vertex.co[:] for vertex in root.data.vertices], path.arrays['irc_positions'][step - 1], atol=1e-6)
        expected = api('mayer').display_samples(path, data, step)
        np.testing.assert_allclose([vertex.co[:] for vertex in carrier.data.vertices], expected[0], atol=1e-6)
        np.testing.assert_allclose([item.value for item in carrier.data.attributes['qc_mayer_value'].data], expected[2], atol=1e-7)
        check_pairs(root, data, range(1, 7), bounds)
        assert api('mayer').color_range(data) == bounds
    before = ([vertex.co[:] for vertex in root.data.vertices], root['qc_irc_record'],
              {obj.name: obj['qc_annotation'] for obj in root.children if 'qc_annotation' in obj})
    attr = carrier.data.attributes['qc_mayer_atom']
    atom = attr.data[0].value
    attr.data[0].value = 99
    try:
        expect_cancel(lambda: bpy.ops.qcblender.irc_step(direction='NEXT'), 'identities')
        assert root['qc_irc_step'] == 2
        assert before == ([vertex.co[:] for vertex in root.data.vertices], root['qc_irc_record'],
                          {obj.name: obj['qc_annotation'] for obj in root.children if 'qc_annotation' in obj})
    finally:
        attr.data[0].value = atom
    assert bpy.ops.qcblender.irc_step(direction='PREV') == {'FINISHED'}
    assert bpy.ops.qcblender.mayer_display(enabled=False) == {'FINISHED'}
    assert evaluated(root)[0] == baseline
    assert original_positions == [list(vertex.co) for vertex in root.data.vertices]
    assert original_edges == [list(edge.vertices) for edge in root.data.edges]
    assert modifier[interface_socket(modifier.node_group, mayer.STYLE).identifier] == original_style
    assert bpy.ops.qcblender.mayer_display(enabled=True) == {'FINISHED'}
    assert bpy.ops.qcblender.mayer_settings(range_mode='MANUAL', minimum=0., maximum=1., use_threshold=True, threshold=.5) == {'FINISHED'}
    assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
    saved_pairs = check_pairs(root, data, (1, 2, 5), (0., 1.))
    assert science(root, table) == before_science
    export = api('data_export').export_dataset(bpy.path.abspath(table['qc_dataset']), OUT / 'csv', 'Mayer')
    with (Path(export['directory']) / 'mayer.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 18
    pairs = data.arrays['mayer_pairs'].tolist()
    for row in rows:
        index = pairs.index([int(row['atom_a_1based']), int(row['atom_b_1based'])])
        assert float(row['mayer_order']) == data.arrays['mayer_orders'][int(row['step']) - 1, index]
    rendered = None
    if args.render:
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            assert bpy.ops.qcblender.apply_output(direction='PCA', quality='PREVIEW', background='WHITE',
                resolution_x=960, resolution_y=640, margin=.08) == {'FINISHED'}
            subject = api('blender.camera').subject_points(bpy.context, [root])
            assert len(subject) and np.max(np.abs(subject)) < 2., 'Legend contaminated the molecular orientation'
        orientation = root.matrix_world.to_quaternion().inverted() @ bpy.context.scene.camera.matrix_world.to_quaternion()
        position = np.mean(path.arrays['irc_positions'][1], axis=0) + np.array(orientation.to_matrix().col[0]) * 3.
        assert bpy.ops.qcblender.mayer_settings(range_mode='MANUAL', minimum=0., maximum=1.,
            use_threshold=True, threshold=.5, legend_position=tuple(position),
            legend_rotation=tuple(orientation.to_euler())) == {'FINISHED'}
        with bpy.context.temp_override(area=area, region=region):
            assert bpy.ops.qcblender.apply_output(direction='PCA', quality='PREVIEW', background='WHITE',
                resolution_x=960, resolution_y=640, margin=.08) == {'FINISHED'}
        rendered = OUT / 'mayer.png'
        bpy.context.scene.render.filepath = str(rendered)
        assert bpy.ops.render.render(write_still=True) == {'FINISHED'}
        assert rendered.is_file() and rendered.stat().st_size > 1000
    project = api('blender.project').save_project(OUT / 'mayer.blend')
    return {'all_pairs': all_pairs, 'saved_pairs': saved_pairs, 'science': science(root, table),
            'settings': json.loads(table['qc_mayer_settings']), 'csv_rows': len(rows),
            'source_bonds_unchanged': True, 'disable_restores_geometry': True,
            'mismatched_identity_cancels_before_step': True, 'project': str(project),
            'render': str(rendered) if rendered else None}


try:
    record = dict(main(), status='Passed', blender=bpy.app.version_string,
                  module=args.module, module_path=importlib.import_module(args.module).__file__)
except Exception:
    record = {'status': 'Failed', 'error': traceback.format_exc(), 'module': args.module}
    REPORT.write_text(json.dumps(record, indent=2), encoding='utf-8')
    raise
REPORT.write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps({'status': record['status'], 'report': str(REPORT)}))
