"""Installed Blender checks for real and analytic profile snapshots."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import time
import uuid

import bpy
from mathutils import Matrix, Vector
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--reopen', choices=('saved', 'moved'))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
storage = importlib.import_module(MODULE + '.data')
project = importlib.import_module(MODULE + '.blender.project')
views = importlib.import_module(MODULE + '.blender.views')
layers = importlib.import_module(MODULE + '.blender.layers')
browser = importlib.import_module(MODULE + '.blender.source_browser')
scene = bpy.context.scene
REPORT = OUT / 'profile.json'
export_paths = {}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot():
    return {o.name: {'manifest': o['qc_dataset_sha256'], 'source': o['qc_source_sha256'],
            'arrays': {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in
                       storage.load_dataset(bpy.path.abspath(o['qc_dataset'])).arrays.items()}}
            for o in scene.objects if o.get('qc_dataset')}


def export(obj, name):
    layers.activate(bpy.context, obj)
    Job = importlib.import_module(MODULE + '.blender.jobs').Job
    token = uuid.uuid4().hex
    job = Job('export_data', export_token=token, dataset=bpy.path.abspath(obj['qc_dataset']),
              dataset_sha256=obj['qc_dataset_sha256'], output_directory=str(OUT / 'csv'),
              kind='profile', scope='ALL', filters={})
    deadline = time.monotonic() + 180
    while (report := job.poll()) is None:
        if time.monotonic() > deadline:
            job.cancel()
            importlib.import_module(MODULE + '.data_export').cleanup_staging(OUT / 'csv', token)
            raise TimeoutError(str(job.directory))
        time.sleep(.1)
    assert report['status'] == 'succeeded', report
    path = Path(report['directory']) / 'profile.csv'
    export_paths[name] = path
    assert report['files'][0]['sha256'] == digest(path)
    return digest(path)


if args.reopen:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert snapshot() == report['snapshot']
    for name, expected in report['csv'].items():
        assert export(bpy.data.objects[name], args.reopen + '-' + name) == expected
    scene.render.filepath = str(OUT / (args.reopen + '.png'))
    bpy.ops.render.render(write_still=True)
    report[args.reopen + '_cold_reopen_csv'] = 'Passed'
else:
    atom = next(o for o in scene.objects if o.get('qc_view_kind') == 'atoms')
    field = next(o for o in scene.objects if o.get('qc_view_kind') == 'field')
    errors, checks, csv_digests = {}, {}, {}
    before_arrays = snapshot()

    def create(view, start, end, name, role='GEOMETRY', count=31):
        layers.activate(bpy.context, view)
        scene.cursor.location = start
        assert bpy.ops.qcblender.mark_profile_start() == {'FINISHED'}
        scene.cursor.location = end
        assert bpy.ops.qcblender.create_line_profile(field_role=role, samples=count) == {'FINISHED'}
        obj = bpy.context.object
        obj.name = name
        assert obj.get('qc_analysis_role') == 'profile' and obj.get('qc_data_record')
        assert obj.type == 'MESH' and len(obj.data.vertices) == 0 and len(obj.modifiers) == 0
        assert obj in layers.display_layers(scene)
        data = storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
        assert data.metadata['source']['kind'] == 'derived'
        csv_digests[name] = export(obj, name)
        return obj, data

    def rejected(label, expected, **kwargs):
        before = (set(bpy.data.objects.keys()), set(bpy.data.curves.keys()))
        try:
            bpy.ops.qcblender.create_line_profile(**kwargs)
        except RuntimeError as error:
            assert expected in str(error), error
            errors[label] = str(error)
        else:
            raise AssertionError(label)
        assert before == (set(bpy.data.objects.keys()), set(bpy.data.curves.keys()))

    source = storage.load_dataset(bpy.path.abspath(field['qc_dataset']))
    f = json.loads(field['qc_field'])
    origin, steps = np.array(f['origin']), np.array(f['steps'])
    start, end = [origin + np.array(index) @ steps for index in ((0, 15, 15), (30, 15, 15))]
    curve, sampled = create(field, start, end, 'MO profile')
    expected = source.arrays[f['array']][:, 15, 15]
    np.testing.assert_allclose(sampled.arrays['profile_values'], expected, atol=1e-7)
    assert sampled.arrays['profile_valid'].all()
    np.testing.assert_allclose(sampled.arrays['profile_distance'], np.linspace(0, 6, 31), atol=1e-6)
    checks['real_geometry_max_error'] = float(np.max(np.abs(sampled.arrays['profile_values'] - expected)))
    assert {'Profile source', 'Profile field', 'Profile sampling'} <= {title for title, _ in browser.source_details(curve)}
    layers.activate(bpy.context, field)
    assert bpy.ops.qcblender.create_slice(resolution=31) == {'FINISHED'}
    slice_obj = bpy.context.object
    _, sliced = create(slice_obj, start, end, 'Slice profile')
    np.testing.assert_array_equal(sliced.arrays['profile_values'], sampled.arrays['profile_values'])
    Job = importlib.import_module(MODULE + '.blender.jobs').Job
    job = Job('evaluate', dataset=bpy.path.abspath(atom['qc_dataset']),
              grid={key: f[key] for key in ('origin', 'steps', 'shape')},
              parameters={'quantity': 'electron_number_density', 'spin': 'total', 'memory_mb': 512})
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        receipt = job.poll()
        if receipt is not None:
            assert receipt['status'] == 'succeeded', receipt
            break
        time.sleep(.1)
    else:
        job.cancel()
        raise TimeoutError(str(job.directory))
    color = views.field_view(job.directory / 'dataset', atom)
    importlib.import_module(MODULE + '.blender.scalars').add_mapping(field, color, 0, .5)
    volume = color.qc_settings.volume
    volume.matrix_world = Matrix(((2, 0, 0, .5), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    bpy.context.view_layer.update()
    world = [volume.matrix_world @ Vector(p) for p in (start, end)]
    _, colored = create(field, *world, 'Color profile', role='COLOR')
    color_data = storage.load_dataset(job.directory / 'dataset')
    cf = json.loads(color['qc_field'])
    np.testing.assert_allclose(colored.arrays['profile_values'], color_data.arrays[cf['array']][:, 15, 15], atol=1e-7)
    np.testing.assert_allclose(colored.arrays['profile_distance'][-1], 6, atol=1e-6)
    assert np.linalg.norm(np.asarray(world[1]) - world[0]) == 12
    assert colored.metadata['profile']['field']['quantity'] == 'electron_number_density'
    assert colored.metadata['profile']['source_manifest_sha256'] == color['qc_dataset_sha256']
    checks['color_transform_source_distance'] = 'Passed'
    # An explicitly synthetic affine field exercises invalid samples in a saved data record.
    grid_steps = np.array([[.5, .25, 0], [0, .5, .25], [.25, 0, .5]])
    coordinates = np.moveaxis(np.indices((5, 3, 3)), 0, -1) @ grid_steps
    af = {'array': 'scalar', 'valid_mask': 'valid', 'shape': [5, 3, 3], 'origin': [0, 0, 0],
          'steps': grid_steps.tolist(), 'quantity': 'analytic_validation', 'unit': 'test-unit', 'vdb': 'field.vdb'}
    fixture = storage.Dataset({'source': {'filename': 'analytic validation', 'sha256': hashlib.sha256(b'profile analytic gap').hexdigest()},
                'coordinate_unit': 'angstrom', 'calculation_status': 'synthetic', 'fields': [af], 'diagnostics': []},
              {'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3)),
               'scalar': coordinates @ [2, -3, .5] + 1, 'valid': np.ones((5, 3, 3), dtype=bool)})
    fixture.arrays['valid'][2, :, :] = False
    directory = OUT / 'analytic-field'
    storage.save_dataset(fixture, directory)
    importlib.import_module(MODULE + '.worker').write_volume(fixture, directory / 'field.vdb')
    analytic = views.field_view(directory)
    gap, data = create(analytic, coordinates[0, 1, 1], coordinates[4, 1, 1], 'Gap profile', count=5)
    np.testing.assert_array_equal(data.arrays['profile_valid'], [True, True, False, True, True])
    assert len(gap.data.vertices) == 0 and not gap.children
    valid = data.arrays['profile_valid']
    np.testing.assert_allclose(data.arrays['profile_values'][valid], data.arrays['profile_positions'][valid] @ [2, -3, .5] + 1)
    _, outside = create(analytic, coordinates[0, 1, 1] - 2 * grid_steps[0], coordinates[4, 1, 1], 'Outside profile', count=13)
    assert not outside.arrays['profile_valid'][0]
    import csv
    rows = list(csv.DictReader(export_paths['Gap profile'].open(encoding='utf-8')))
    assert rows[2]['value'] == '' and rows[2]['valid'] == '0'
    layers.activate(bpy.context, analytic)
    scene.cursor.location = coordinates[0, 1, 1]
    bpy.ops.qcblender.mark_profile_start()
    rejected('zero', 'must differ')
    scene.cursor.location = coordinates[0, 1, 1] - grid_steps[0]
    rejected('no-adjacent', 'no adjacent valid', samples=2)
    rejected('missing-color', 'no color field', field_role='COLOR')
    analytic['qc_dataset_sha256'] = 'f' * 64
    rejected('changed-binding', '显示层与体场来源摘要不同')
    analytic['qc_dataset_sha256'] = digest(directory / 'manifest.json')
    layers.activate(bpy.context, curve)
    assert bpy.ops.qcblender.layer_action(target=curve.name, action='DUPLICATE') == {'FINISHED'}
    copied = bpy.context.object
    copied.name = 'MO profile copy'
    assert copied.data != curve.data and len(copied.data.vertices) == 0
    assert copied['qc_data_record'] and copied['qc_dataset_sha256'] == curve['qc_dataset_sha256']
    copied.location += Vector((0, 5, 0))
    assert export(copied, copied.name) == csv_digests[curve.name]
    csv_digests[copied.name] = csv_digests[curve.name]
    assert copied['qc_source_sha256'] == curve['qc_source_sha256']
    for name, original in before_arrays.items():
        assert snapshot()[name] == original
    for obj in scene.objects:
        if obj.get('qc_view_kind'):
            obj.hide_render = obj not in (field, atom)
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    area.spaces.active.region_3d.view_rotation = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))).to_quaternion()
    layers.activate(bpy.context, field)
    scene.render.resolution_x, scene.render.resolution_y = 800, 600
    with bpy.context.temp_override(area=area, region=next(r for r in area.regions if r.type == 'WINDOW')):
        assert bpy.ops.qcblender.create_framed_camera() == {'FINISHED'}
    scene.render.filepath = str(OUT / 'profile-data-context.png')
    bpy.ops.render.render(write_still=True)
    project.save_project(OUT / 'profile.blend')
    moved = OUT / 'moved'
    moved.mkdir(exist_ok=True)
    shutil.copy2(OUT / 'profile.blend', moved / 'profile.blend')
    shutil.copytree(OUT / 'profile.qcdata', moved / 'profile.qcdata', dirs_exist_ok=True)
    report = {'status': 'Passed', 'blender': bpy.app.version_string, 'checks': checks, 'errors': errors,
              'affine_gap_record_csv': 'Passed', 'copy_independence': 'Passed', 'source_arrays_unchanged': 'Passed',
              'source_details': 'Passed', 'snapshot': snapshot(), 'csv': csv_digests,
              'saved_cold_reopen_csv': 'Not Run', 'moved_cold_reopen_csv': 'Not Run'}
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({key: value for key, value in report.items() if key not in ('snapshot', 'csv')}))
