"""Installed extension: real optimization import, view isolation and portable reopen."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/optimization-trajectory/verification')
parser.add_argument('--reopen', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
storage = importlib.import_module(MODULE + '.data')
views = importlib.import_module(MODULE + '.blender.views')
browser = importlib.import_module(MODULE + '.blender.source_browser')
project = importlib.import_module(MODULE + '.blender.project')
layers = importlib.import_module(MODULE + '.blender.layers')
Job = importlib.import_module(MODULE + '.blender.jobs').Job


def import_source():
    job = Job('import', source=str(input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)), job_index=0)
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return job.directory / 'dataset'
        time.sleep(.1)
    job.cancel()
    raise TimeoutError('Optimization import')


def coordinates(obj):
    return np.array([v.co[:] for v in obj.data.vertices])


def digest_arrays(obj):
    return {key: hashlib.sha256(value.tobytes()).hexdigest()
            for key, value in storage.load_dataset(bpy.path.abspath(obj['qc_dataset'])).arrays.items()}


report = {'status': 'Passed', 'blender': bpy.app.version_string}
if args.reopen:
    before = json.loads((OUT / 'before-save.json').read_text())
    for name, record in before.items():
        obj = bpy.data.objects[name]
        assert digest_arrays(obj) == record['arrays']
        np.testing.assert_allclose(coordinates(obj), record['positions'], atol=1e-7)
        assert obj.get('qc_optimization_step') == record['step']
        assert browser.source_details(obj) == [tuple(entry) for entry in record['details']]
        path = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
        assert path.is_relative_to(Path(bpy.data.filepath).with_suffix('.qcdata'))
    report['moved_cold_reopen'] = 'Passed'
else:
    source = views.atom_view(import_source())
    layers.activate(bpy.context, source)
    data = storage.load_dataset(bpy.path.abspath(source['qc_dataset']))
    assert data.arrays['optimization_positions'].shape == (4, 3, 3)
    original = coordinates(source).copy()
    assert bpy.ops.qcblender.optimization_view() == {'FINISHED'}
    obj = bpy.context.object
    obj.name = 'Optimization'
    assert obj != source and obj['qc_optimization_count'] == 4
    before = digest_arrays(obj)
    for step in range(1, 5):
        assert bpy.ops.qcblender.optimization_step(step=step) == {'FINISHED'}
        np.testing.assert_allclose(coordinates(obj), data.arrays['optimization_positions'][step-1], atol=1e-7)
        np.testing.assert_array_equal(coordinates(source), original)
        record = dict(browser.source_details(obj))['Optimization step']
        assert record['step'] == step
        assert record['energy']['value_hartree'] == data.metadata['optimization']['steps'][step-1]['energy']['value_hartree']
        assert digest_arrays(obj) == before
    assert len(obj.qc_settings.modes) == 0 and len(obj.qc_settings.energies) == 0
    assert obj.data.attributes.get('qc_charge') is None
    # RNA rejects the invalid step without changing any coordinates or record.
    state = coordinates(obj).copy()
    try:
        outcome = bpy.ops.qcblender.optimization_step(step=5)
    except RuntimeError as error:
        assert 'outside' in str(error)
    else:
        assert outcome == {'CANCELLED'}
    np.testing.assert_array_equal(coordinates(obj), state)
    assert obj['qc_optimization_step'] == 4
    def reject_without_change(message):
        positions, record = coordinates(obj).copy(), obj['qc_optimization_record']
        try:
            outcome = bpy.ops.qcblender.optimization_step(step=1)
        except RuntimeError as error:
            assert message in str(error), str(error)
        else:
            assert outcome == {'CANCELLED'}
        np.testing.assert_array_equal(coordinates(obj), positions)
        assert obj['qc_optimization_record'] == record and obj['qc_optimization_step'] == 4

    equilibrium = coordinates(obj).copy()
    obj.data.attributes.remove(obj.data.attributes['qc_equilibrium_position'])
    reject_without_change('attribute')
    attr = obj.data.attributes.new('qc_equilibrium_position', 'FLOAT_VECTOR', 'POINT')
    attr.data.foreach_set('vector', equilibrium.ravel())
    obj.data.attributes['qc_atom_id'].data[0].value = 1
    reject_without_change('identities')
    obj.data.attributes['qc_atom_id'].data[0].value = 0
    manifest = Path(bpy.path.abspath(obj['qc_dataset'])) / 'manifest.json'
    original_manifest = manifest.read_bytes()
    try:
        manifest.write_bytes(original_manifest + b'\n')
        reject_without_change('manifest differs')
    finally:
        manifest.write_bytes(original_manifest)
    report['broken_attributes_identity_and_binding_reject_without_mutation'] = 'Passed'
    assert bpy.ops.qcblender.layer_action(target=obj.name, action='DUPLICATE') == {'FINISHED'}
    duplicate = bpy.context.object
    duplicate.name = 'Independent optimization'
    assert bpy.ops.qcblender.optimization_step(step=2) == {'FINISHED'}
    assert obj['qc_optimization_step'] == 4
    assert duplicate.data != obj.data
    assert duplicate.modifiers[0].node_group != obj.modifiers[0].node_group
    assert digest_arrays(duplicate) == before
    report['real_worker_steps_energy_source_and_independent_copy'] = 'Passed'
    report['out_of_range_atomic_rejection'] = 'Passed'
    expected = {item.name: {'arrays': digest_arrays(item), 'positions': coordinates(item).tolist(),
                           'step': item.get('qc_optimization_step'), 'details': browser.source_details(item)}
                for item in (source, obj, duplicate)}
    (OUT / 'before-save.json').write_text(json.dumps(expected, indent=2), encoding='utf-8')
    project.save_project(OUT / 'optimization.blend')
    moved = OUT / 'moved'
    moved.mkdir(exist_ok=True)
    shutil.copy2(OUT / 'optimization.blend', moved / 'optimization.blend')
    shutil.copytree(OUT / 'optimization.qcdata', moved / 'optimization.qcdata', dirs_exist_ok=True)
    report['portable_save'] = 'Passed'

(OUT / ('cold-reopen.json' if args.reopen else 'checks.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
