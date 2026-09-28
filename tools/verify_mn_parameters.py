"""Installed-candidate checks for fixed selections and scene annotations."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qc_evidence', ROOT / 'tools/verify_vmd_parameters.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
module = evidence.module


def import_source(path, job_index=0):
    job = module('blender.jobs').Job('import', source=str(path), job_index=job_index)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return job.directory / 'dataset'
        time.sleep(.1)
    job.cancel()
    raise TimeoutError('Scientific import')


def members(obj):
    attr = obj.data.attributes.get('qc_local_selection')
    return [i for i, value in enumerate(attr.data, 1) if value.value] if attr else list(range(1, len(obj.data.vertices) + 1))


def selection_snapshot(obj):
    return {'members': members(obj), 'record': obj.get('qc_local_selection_record'),
            'hydrogen': [item.value for item in obj.data.attributes['qc_atom_visible'].data],
            'step': obj.get('qc_optimization_step', obj.get('qc_irc_step'))}


def assert_rejected(action, obj):
    before = selection_snapshot(obj)
    objects = set(bpy.context.scene.objects)
    error = evidence.expect_error(action, '')
    assert selection_snapshot(obj) == before
    assert set(bpy.context.scene.objects) == objects
    return error


def check_selection(out):
    out.mkdir(parents=True, exist_ok=True)
    atoms = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'atoms')
    atoms.name = 'MN local selection source'
    evidence.activate(atoms)
    before = evidence.hashes()
    initial_counts = evidence.mesh_count(atoms)
    assert bpy.ops.qcblender.local_selection(numbers='1,3-4') == {'FINISHED'}
    assert members(atoms) == [1, 3, 4]
    assert evidence.mesh_count(atoms)[0] < initial_counts[0]
    for mode, numbers, expected in [('UNION', '2', [1, 2, 3, 4]),
                                    ('INTERSECT', '1-2', [1, 2]),
                                    ('DIFFERENCE', '2', [1]), ('INVERT', '', [2, 3, 4, 5])]:
        assert bpy.ops.qcblender.local_selection(mode=mode, numbers=numbers) == {'FINISHED'}
        assert members(atoms) == expected
    errors = {text: assert_rejected(lambda text=text: bpy.ops.qcblender.local_selection(numbers=text), atoms)
              for text in ('0', '6', '3-1', '1,,2')}
    errors['empty'] = assert_rejected(lambda: bpy.ops.qcblender.local_selection(mode='INTERSECT', numbers='1'), atoms)
    assert bpy.ops.qcblender.local_selection(mode='CLEAR') == {'FINISHED'}
    positions, provenance = module('blender.geometry').current_geometry(atoms)
    radius = float(np.linalg.norm(positions[1] - positions[0]))
    # The pure Python check covers exact boundary precision; RNA uses float32.
    assert bpy.ops.qcblender.local_selection(numbers='1', use_radius=True, radius=radius + 1e-5) == {'FINISHED'}
    actual_radius = json.loads(atoms['qc_local_selection_record'])['steps'][0]['radius']
    expected = (np.linalg.norm(positions - positions[0], axis=1) <= actual_radius).nonzero()[0] + 1
    assert members(atoms) == expected.tolist()
    assert bpy.ops.qcblender.local_selection(numbers='1,3-4') == {'FINISHED'}
    assert bpy.ops.qcblender.hydrogen_visibility(mode='HIDE') == {'FINISHED'}
    fixed = members(atoms)
    hidden = evidence.mesh_count(atoms)
    assert bpy.ops.qcblender.local_selection(numbers='1-5') == {'FINISHED'}
    assert evidence.mesh_count(atoms) == hidden
    assert bpy.ops.qcblender.hydrogen_visibility(mode='RESTORE') == {'FINISHED'}
    assert members(atoms) == [1, 2, 3, 4, 5]
    assert bpy.ops.qcblender.local_selection_layer(numbers='1,3') == {'FINISHED'}
    local = bpy.context.object
    local.name = 'MN local layer'
    assert local.data != atoms.data and members(local) == [1, 3]
    lm, ln = evidence.controls(local)
    am, an = evidence.controls(atoms)
    lm[ln['Atom Radius']] = .6
    assert am[an['Atom Radius']] != lm[ln['Atom Radius']]
    assert bpy.ops.qcblender.local_selection(numbers='2,4') == {'FINISHED'}
    assert members(atoms) == [1, 2, 3, 4, 5]
    target_state = selection_snapshot(local)
    module('blender.copy_display').copy_parameters(atoms, [local])
    assert selection_snapshot(local) == target_state
    assert evidence.hashes() == before

    source = module('blender.views').atom_view(import_source(ROOT / 'outputs/log-examples/water_neutral_nbo_opt_freq.out'))
    evidence.activate(source)
    assert bpy.ops.qcblender.optimization_view() == {'FINISHED'}
    trajectory = bpy.context.object
    trajectory.name = 'MN fixed optimization neighborhood'
    assert bpy.ops.qcblender.local_selection(numbers='1', use_radius=True, radius=1.) == {'FINISHED'}
    fixed = selection_snapshot(trajectory)
    assert bpy.ops.qcblender.optimization_step(step=4) == {'FINISHED'}
    assert members(trajectory) == fixed['members']
    assert trajectory['qc_local_selection_record'] == fixed['record']
    assert bpy.ops.qcblender.new_current_view() == {'FINISHED'}
    upgraded = bpy.context.object
    assert upgraded['qc_optimization_step'] == 4 and members(upgraded) == fixed['members']
    np.testing.assert_array_equal(module('blender.geometry').current_geometry(upgraded)[0],
                                  module('blender.geometry').current_geometry(trajectory)[0])
    evidence.activate(trajectory)
    assert bpy.ops.qcblender.local_selection(mode='RECOMPUTE') == {'FINISHED'}
    assert json.loads(trajectory['qc_local_selection_record'])['source']['step'] == 4

    manifest = ROOT / 'outputs/v1-acceptance/sources/c10-c13/peroxide-irc-pyscf/steps.csv'
    assert bpy.ops.qcblender.import_irc_path(manifest_path=str(manifest)) == {'FINISHED'}
    irc = next(obj for obj in bpy.context.scene.objects if obj.get('qc_irc'))
    evidence.activate(irc)
    assert bpy.ops.qcblender.local_selection(numbers='1,3') == {'FINISHED'}
    irc_fixed = selection_snapshot(irc)
    assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
    assert members(irc) == irc_fixed['members'] and irc['qc_local_selection_record'] == irc_fixed['record']
    errors['irc_duplicate'] = assert_rejected(lambda: bpy.ops.qcblender.local_selection_layer(numbers='1'), irc)
    errors['irc_upgrade'] = assert_rejected(lambda: bpy.ops.qcblender.new_current_view(), irc)
    # Rendering isolates the two independently editable local layers.
    for obj in bpy.context.scene.objects:
        if obj.type not in ('LIGHT', 'CAMERA'):
            obj.hide_render = obj not in (atoms, local)
    local.location.x += 3
    evidence.activate(local)
    report = {'selection_operations': 'Passed', 'fixed_real_steps': 'Passed',
              'independent_layers': 'Passed', 'hydrogen_intersection': 'Passed',
              'errors': errors, 'radius': actual_radius,
              'selections': {obj.name: selection_snapshot(obj) for obj in bpy.context.scene.objects
                             if obj.get('qc_view_kind') == 'atoms'},
              'render_pixels': evidence.render(out / 'evidence.png')}
    evidence.save_evidence(out, report)
    return report


def check_reopen(out):
    report = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
    for name, expected in report.get('selections', {}).items():
        assert selection_snapshot(bpy.data.objects[name]) == expected, name
    return evidence.check_reopen(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', choices=['selection', 'reopen'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.preferences.addon_enable(module=evidence.MODULE)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    result = {'selection': check_selection, 'reopen': check_reopen}[args.check](args.out)
    print(json.dumps(result, ensure_ascii=False))
