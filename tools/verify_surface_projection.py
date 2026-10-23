"""Real Multiwfn import, native display, CSV and portable cold-read verification."""
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
parser.add_argument('--package-root', type=Path)
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
    assert args.science_site is None and args.package_root is None
    bpy.ops.preferences.addon_enable(module=args.module)


def api(name):
    return importlib.import_module(args.module + '.' + name)


def activate(obj):
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def dataset(obj):
    return api('data').load_dataset(bpy.path.abspath(obj['qc_dataset']))


def science(obj):
    return {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in dataset(obj).arrays.items()}


def displayed(obj):
    attrs = obj.data.attributes
    return {'faces': len(obj.data.polygons), 'vertices': len(obj.data.vertices),
            'attributes': {key: [entry.value for entry in attrs[key].data]
                for key in ('qc_projection_ix', 'qc_projection_iy', 'qc_projection_depth', 'qc_projection_state')},
            'contours': sorted(float(child['qc_projection_level']) for child in obj.children
                               if child.get('qc_projection_part') == 'contours')}


def check_mesh(obj, expected_faces):
    data = dataset(obj)
    record = displayed(obj)
    assert record['faces'] == expected_faces and record['vertices'] == expected_faces * 4
    attributes = record['attributes']
    for vertex, ix, iy, depth, state in zip(obj.data.vertices,
            attributes['qc_projection_ix'], attributes['qc_projection_iy'],
            attributes['qc_projection_depth'], attributes['qc_projection_state']):
        assert abs(depth - data.arrays['projection_depth'][ix, iy]) < 1e-6
        assert state == data.arrays['projection_state'][ix, iy]
        assert vertex.co.z == 0.
    for start in range(0, len(obj.data.vertices), 4):
        ix, iy = attributes['qc_projection_ix'][start], attributes['qc_projection_iy'][start]
        center = np.mean([vertex.co[:] for vertex in obj.data.vertices[start:start+4]], axis=0)
        np.testing.assert_allclose(center[:2], [data.arrays['projection_x'][ix], data.arrays['projection_y'][iy]], atol=1e-6, rtol=0)
    atoms = next(child for child in obj.children if child.get('qc_projection_part') == 'atoms')
    assert set(item.value for item in atoms.data.attributes['qc_atom_id'].data) == set(range(61))
    for i, face in enumerate(atoms.data.polygons):
        center = np.mean([atoms.data.vertices[index].co[:] for index in face.vertices], axis=0)
        np.testing.assert_allclose(center[:2], data.arrays['positions'][i, :2], atol=1e-6, rtol=0)
    return record


def expect_cancel(operation):
    try:
        result = operation()
    except RuntimeError as error:
        assert 'Projection' in str(error), str(error)
    else:
        assert result == {'CANCELLED'}, result


def main():
    if args.reopen:
        previous = json.loads((OUT / 'native.json').read_text(encoding='utf-8'))
        objects = {obj.name: obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'projection'}
        assert set(objects) == set(previous['maps'])
        for name, obj in objects.items():
            record = previous['maps'][name]
            assert science(obj) == record['science']
            assert json.loads(obj['qc_projection_settings']) == record['settings']
            assert displayed(obj) == record['displayed']
            assert json.loads(obj['qc_projection_point']) == record['point']
            directory = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
            assert directory.is_relative_to(OUT / 'projection.qcdata')
            check_mesh(obj, record['displayed']['faces'])
        obj = objects['QC Projection verified mask']
        activate(obj)
        assert bpy.ops.qcblender.projection_point(ix=0, iy=0) == {'FINISHED'}
        assert json.loads(obj['qc_projection_point'])['state'] == 'missed'
        return {'cold_reopen': 'Passed', 'maps': len(objects), 'scientific_arrays_and_display': 'Passed',
                'post_reopen_point_read': 'Passed'}
    assert not bpy.data.filepath, 'Start a fresh owned process without a user project'
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    source = ROOT / 'validation/shared/data/local/scientific-displays/ru-vdw-20261023'
    reference = api('xyz').read_xyz(source / 'reference.xyz')
    refdir = OUT / 'reference-dataset'
    api('data').save_dataset(reference, refdir)
    parent = api('blender.views').atom_view(refdir)
    activate(parent)
    before = science(parent)
    operator_args = dict(data_path=str(source / 'distmap.txt'), settings_path=str(source / 'scan.json'),
                         log_path=str(source / 'mwfn_log.txt'))
    assert bpy.ops.qcblender.import_surface_projection(**operator_args, mask_path=str(source / 'validity.csv')) == {'FINISHED'}
    obj = bpy.context.object
    obj.name = 'QC Projection verified mask'
    check_mesh(obj, 1406)
    original = science(obj)
    assert bpy.ops.qcblender.projection_settings(manual_range=True, minimum=-8., maximum=0.,
        show_contours=True, contour_levels='-4,-3,-2') == {'FINISHED'}
    assert displayed(obj)['contours'] == [-4., -3., -2.]
    snapshot, old_settings = displayed(obj), obj['qc_projection_settings']
    expect_cancel(lambda: bpy.ops.qcblender.projection_settings(manual_range=True, minimum=0., maximum=0.))
    assert snapshot == displayed(obj) and old_settings == obj['qc_projection_settings']
    assert bpy.ops.qcblender.projection_point(ix=30, iy=20) == {'FINISHED'}
    assert json.loads(obj['qc_projection_point'])['state'] == 'valid'
    point = obj['qc_projection_point']
    expect_cancel(lambda: bpy.ops.qcblender.projection_point(ix=61, iy=0))
    assert obj['qc_projection_point'] == point
    assert science(obj) == original and science(parent) == before
    export = api('data_export').export_dataset(bpy.path.abspath(obj['qc_dataset']), OUT / 'csv', 'PROJECTION')
    with (Path(export['directory']) / 'surface_projection.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2501
    values = dataset(obj)
    for row in rows:
        ix, iy = int(row['ix']), int(row['iy'])
        assert float(row['depth_angstrom']) == values.arrays['projection_depth'][ix, iy]
        assert int(row['state']) == values.arrays['projection_state'][ix, iy]
    activate(parent)
    assert bpy.ops.qcblender.import_surface_projection(**operator_args) == {'FINISHED'}
    unknown = bpy.context.object
    unknown.name = 'QC Projection unknown bottom'
    unknown.location.x += 25
    check_mesh(unknown, 2501)
    assert sum(face.material_index == 1 for face in unknown.data.polygons) == 1095
    assert bpy.ops.qcblender.projection_settings(show_unknown=False) == {'FINISHED'}
    check_mesh(unknown, 1406)
    assert bpy.ops.qcblender.projection_settings(show_unknown=True) == {'FINISHED'}
    check_mesh(unknown, 2501)
    activate(parent)
    bad_scan = {**json.loads((source / 'scan.json').read_text()), 'xy_offset_angstrom': [0, 0]}
    bad_path = OUT / 'invalid-offset.json'
    bad_path.write_text(json.dumps(bad_scan), encoding='utf-8')
    count = len(bpy.data.objects)
    expect_cancel(lambda: bpy.ops.qcblender.import_surface_projection(**{**operator_args, 'settings_path': str(bad_path)}))
    assert len(bpy.data.objects) == count
    activate(obj)
    rendered = None
    if args.render:
        camera = bpy.data.objects.new('Projection camera', bpy.data.cameras.new('Projection camera'))
        bpy.context.collection.objects.link(camera)
        camera.location = obj.location + __import__('mathutils').Vector((0., -.3, 30.))
        camera.data.type, camera.data.ortho_scale = 'ORTHO', 23.5
        scene = bpy.context.scene
        scene.camera = camera
        lamp = bpy.data.objects.new('Projection area light', bpy.data.lights.new('Projection area light', 'AREA'))
        bpy.context.collection.objects.link(lamp)
        lamp.location = obj.location + __import__('mathutils').Vector((0., 0., 15.))
        lamp.data.energy, lamp.data.size = 1500, 12
        scene.world.use_nodes = True
        scene.world.node_tree.nodes.get('Background').inputs[0].default_value = (1, 1, 1, 1)
        scene.world.node_tree.nodes.get('Background').inputs[1].default_value = 1.
        parent.hide_render = True
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 16
        scene.view_settings.view_transform = 'Standard'
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1280, 960, 100
        scene.render.image_settings.file_format = 'PNG'
        rendered = OUT / 'projection.png'
        scene.render.filepath = str(rendered)
        assert bpy.ops.render.render(write_still=True) == {'FINISHED'}
    project = api('blender.project').save_project(OUT / 'projection.blend')
    return {'project': str(project), 'render': str(rendered) if rendered else None, 'csv_rows': len(rows),
            'invalid_offset_cancelled_without_scene_change': True, 'invalid_settings_preserved_display': True,
            'reference_science_unchanged': science(parent) == before,
            'maps': {view.name: {'science': science(view), 'settings': json.loads(view['qc_projection_settings']),
                       'displayed': displayed(view), 'point': json.loads(view['qc_projection_point'])} for view in (obj, unknown)}}


try:
    record = dict(main(), status='Passed', blender=bpy.app.version_string,
                  module=args.module, module_path=importlib.import_module(args.module).__file__)
except Exception:
    record = {'status': 'Failed', 'error': traceback.format_exc(), 'module': args.module}
    REPORT.write_text(json.dumps(record, indent=2), encoding='utf-8')
    raise
REPORT.write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps({'status': record['status'], 'report': str(REPORT)}))
