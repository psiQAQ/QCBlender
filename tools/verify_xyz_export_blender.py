"""Installed-candidate checks for discrete XYZ frames and explicit data exports."""
import argparse
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import uuid

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if ROOT.name == 'b48c':
    ROOT = Path('D:/workspace/QCBlender')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--reference-root', type=Path, required=True)
parser.add_argument('--reopen', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT, REF = args.output_dir.resolve(), args.reference_root.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
module = lambda name: importlib.import_module(MODULE + '.' + name)
storage, jobs, views, layers, trajectory, browser = map(module,
    ('data', 'blender.jobs', 'blender.views', 'blender.layers', 'blender.trajectory', 'blender.source_browser'))
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
report = {'status': 'Failed', 'blender': bpy.app.version_string,
          'gui': 'Not Run', 'independent_human_acceptance': 'Not Run', 'checks': {}}

def run(job, timeout=180):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return result
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))

def import_atoms(path, job_index=0):
    job = jobs.Job('import', source=str(path), job_index=job_index)
    run(job)
    directory = job.directory / 'dataset'
    data = storage.load_dataset(directory)
    obj = views.atom_view(directory)
    trajectory.initialize_trajectory(obj, data)
    return obj, data

def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if not obj.get('qc_dataset'):
            continue
        data = storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
        result[obj.name] = {'manifest': obj['qc_dataset_sha256'], 'source': obj['qc_source_sha256'],
            'arrays': {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in data.arrays.items()},
            'frame': obj.get('qc_trajectory_frame'), 'step': obj.get('qc_irc_step'),
            'kind': obj.get('qc_view_kind'), 'role': obj.get('qc_analysis_role'),
            'vertices': len(obj.data.vertices) if obj.type == 'MESH' else None}
    return result

def export(obj, kind, scope='ALL', filters=None):
    token = uuid.uuid4().hex
    result = run(jobs.Job('export_data', dataset=str(Path(bpy.path.abspath(obj['qc_dataset'])).resolve()),
        dataset_sha256=obj['qc_dataset_sha256'], output_directory=str(OUT / 'exports'),
        kind=kind, scope=scope, filters=filters or {}, export_token=token))
    directory = Path(result['directory'])
    meta = json.loads((directory / 'metadata.json').read_text(encoding='utf-8'))
    assert meta['dataset_manifest_sha256'] == obj['qc_dataset_sha256']
    assert meta['kind'] == kind and meta['scope'] == scope
    for item in result['files']:
        assert sha(directory / item['filename']) == item['sha256']
        with (directory / item['filename']).open(encoding='utf-8', newline='') as stream:
            reader = csv.reader(stream)
            assert next(reader) == item['columns']
            assert sum(1 for row in reader) == item['row_count']
    report.setdefault('exports', []).append(dict(kind=kind, scope=scope, filters=filters or {},
        directory=str(directory), metadata_sha256=sha(directory / 'metadata.json'), files=result['files']))
    return result, meta

try:
    if args.reopen:
        original = json.loads(args.report.read_text(encoding='utf-8'))
        assert snapshot() == original['snapshot']
        for item in original['exports']:
            directory = Path(item['directory'])
            assert sha(directory / 'metadata.json') == item['metadata_sha256']
            for file in item['files']:
                assert sha(directory / file['filename']) == file['sha256']
        report = dict(original, cold_open='Passed', cold_path=bpy.data.filepath)
    else:
        single, _ = import_atoms(REF / 'tests/data/xyz/water-dimer.xyz')
        assert 'qc_trajectory_frame' not in single
        multi, data = import_atoms(REF / 'tests/data/xyz/p04-three-frames.xyz')
        assert multi['qc_trajectory_count'] == 3
        layers.activate(bpy.context, multi)
        assert bpy.ops.qcblender.add_annotation(kind='DISTANCE', atoms='1,2', decimals=9) == {'FINISHED'}
        attrs = {name: [v.value for v in multi.data.attributes[name].data]
                 for name in ('qc_atom_id', 'qc_atomic_number', 'qc_atom_visible')}
        frame_values = []
        for frame in (1, 2, 3, 1, 2):
            assert bpy.ops.qcblender.trajectory_frame(direction='GOTO', frame=frame) == {'FINISHED'}
            positions, identity = module('blender.geometry').current_geometry(multi)
            np.testing.assert_allclose(positions, data.arrays['trajectory_positions'][frame - 1], atol=1e-7)
            for name, expected in attrs.items():
                assert [v.value for v in multi.data.attributes[name].data] == expected
            label = next(child for child in multi.children if 'qc_annotation' in child and child.type == 'FONT')
            annotation = json.loads(label['qc_annotation'])
            assert annotation['geometry']['step'] == frame and 'XYZ Frame' in label.data.body
            np.testing.assert_allclose(annotation['value'], np.linalg.norm(positions[0] - positions[1]), atol=1e-12)
            frame_values.append(dict(frame=frame, distance_angstrom=annotation['value'], identity=identity))
        assert any(title == 'XYZ frame' for title, value in browser.source_details(multi))
        copied = layers.copy_layer(multi, bpy.context.collection)
        trajectory.set_frame(copied, data, 3)
        assert multi['qc_trajectory_frame'] == 2 and copied['qc_trajectory_frame'] == 3
        layers.activate(bpy.context, multi)
        assert bpy.ops.qcblender.new_current_view() == {'FINISHED'}
        fresh = bpy.context.object
        assert fresh['qc_trajectory_frame'] == 2 and fresh.data != multi.data
        report['checks']['xyz_frames_identity_measurement_copy'] = 'Passed'
        report['xyz'] = frame_values
        h2 = OUT / 'format-bond-boundary.xyz'
        h2.write_text('2\nnear\nH 0 0 0\nH 0.7 0 0\n2\nfar\nH 0 0 0\nH 5 0 0\n', encoding='utf-8')
        bond_obj, bonds = import_atoms(h2)
        assert len(bond_obj.data.edges) == 1
        trajectory.set_frame(bond_obj, bonds, 2)
        assert len(bond_obj.data.edges) == 0
        trajectory.set_frame(bond_obj, bonds, 1)
        assert len(bond_obj.data.edges) == 1
        report['checks']['xyz_per_frame_inferred_bonds'] = 'Passed'
        ir, ir_data = import_atoms(REF / 'tests/data/local/log-examples/water_neutral_nbo_opt_freq.out', 1)
        opt, opt_data = import_atoms(REF / 'tests/data/local/log-examples/water_neutral_nbo_opt_freq.out', 0)
        assert len(ir.qc_settings.modes) == 3 and ir.qc_settings.spectrum is None
        for index in range(3):
            ir.qc_settings.active_mode = index
        export(ir, 'IR')
        export(opt, 'optimization')
        layers.activate(bpy.context, multi)
        assert bpy.ops.qcblender.import_irc_path(manifest_path=str(REF / 'tests/data/tutorial/P04/steps.csv')) == {'FINISHED'}
        irc = bpy.context.object
        export(irc, 'IRC')
        assert bpy.ops.qcblender.import_irc_mayer(manifest_path=str(REF / 'tests/data/tutorial/P04/mayer-pyscf.csv')) == {'FINISHED'}
        mayer = bpy.context.object
        assert bpy.ops.qcblender.select_irc_mayer_pair() == {'FINISHED'}
        export(mayer, 'Mayer')
        assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
        reference, ref_data = import_atoms(REF / 'tests/data/tutorial/P03/water-dimer.fchk')
        base = REF / 'tests/data/local/public-tutorial/P03'
        pair_job = jobs.Job('import_pair', geometry_source=str(base / 'igmh/dg_inter.cub'),
            color_source=str(base / 'igmh/sl2r.cub'), method='IGMH', geometry_unit='electron/bohr^4',
            color_unit='electron/bohr^3', iri_exponent=None,
            reference_dataset=str(Path(bpy.path.abspath(reference['qc_dataset']))),
            reference_sha256=reference['qc_dataset_sha256'])
        run(pair_job)
        pair_data = storage.load_dataset(pair_job.directory / 'dataset')
        record = module('blender.external_fields').paired_record(pair_job.directory / 'dataset', pair_data, reference)
        result, _ = export(record, 'paired')
        assert result['files'][0]['row_count'] == 539448
        selected = {'x_field': 1, 'y_field': 0, 'x_min': -.04, 'x_max': .04, 'y_min': .001, 'y_max': .02}
        result, _ = export(record, 'paired', 'FILTERED', selected)
        assert result['files'][0]['row_count'] == 36391
        esp = module('analysis_data').import_esp(ref_data, REF / 'tests/data/tutorial/P03/esp/surfanalysis.pdb',
            REF / 'tests/data/tutorial/P03/esp/stdout.log', 'rho=0.001 electron/bohr^3', '', 'kcal/mol', '')
        location = module('blender.external_results').store_analysis(esp)
        area = module('blender.external_results').area_view(location, esp, reference)
        export(area, 'ESP_AREA')
        result, _ = export(area, 'ESP_AREA', 'FILTERED', dict(center_min=0, center_max=20, mode='center'))
        assert result['files'][0]['row_count'] == 4
        field = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'field')
        value = json.loads(field['qc_field'])
        origin, axes = np.array(value['origin']), np.array(value['steps'])
        layers.activate(bpy.context, field)
        bpy.context.scene.cursor.location = origin + np.array([-1, 15, 15]) @ axes
        assert bpy.ops.qcblender.mark_profile_start() == {'FINISHED'}
        bpy.context.scene.cursor.location = origin + np.array([30, 15, 15]) @ axes
        assert bpy.ops.qcblender.create_line_profile(samples=101) == {'FINISHED'}
        profile = bpy.context.object
        result, _ = export(profile, 'profile')
        with (Path(result['directory']) / 'profile.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 101 and any(row['valid'] == '0' and row['value'] == '' for row in rows)
        assert not any(obj.get('qc_view_kind') in ('spectrum', 'scatter', 'profile') for obj in bpy.context.scene.objects)
        for obj in bpy.context.scene.objects:
            if obj.get('qc_data_record'):
                assert obj.type == 'MESH' and not obj.data.vertices and not obj.modifiers
        report['checks']['explicit_worker_exports_all_kinds_and_no_2d_geometry'] = 'Passed'
        cancel_root = OUT / 'cancelled-export'
        token = uuid.uuid4().hex
        cancelled = jobs.Job('export_data', dataset=str(pair_job.directory / 'dataset'),
            dataset_sha256=record['qc_dataset_sha256'], output_directory=str(cancel_root),
            kind='paired', scope='ALL', filters={}, export_token=token)
        deadline = time.monotonic() + 60
        staging = cancel_root / ('.qc-export-' + token)
        while not staging.exists() and cancelled.process.poll() is None and time.monotonic() < deadline:
            time.sleep(.05)
        assert staging.exists(), 'Export finished before its cancellation boundary could be verified'
        cancelled.cancel()
        module('data_export').cleanup_staging(cancel_root, token)
        assert not list(cancel_root.iterdir())
        report['checks']['cancelled_worker_has_no_final_or_staging'] = 'Passed'
        module('blender.project').save_project(OUT / 'integration.blend')
        report['snapshot'] = snapshot()
        report['project'] = str(OUT / 'integration.blend')
        report['cold_open'] = 'Not Run'
    report['status'] = 'Passed'
except Exception as error:
    report['error'] = repr(error)
    raise
finally:
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key not in ('snapshot', 'xyz', 'exports')}, ensure_ascii=False))
