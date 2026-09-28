"""Verify installed ETS-NOCV parsing, pair fields and portable source identity."""
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
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--reopen', choices=('saved', 'moved'))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
storage = importlib.import_module(MODULE + '.data')
project = importlib.import_module(MODULE + '.blender.project')
browser = importlib.import_module(MODULE + '.blender.source_browser')
views = importlib.import_module(MODULE + '.blender.views')
activate = importlib.import_module(MODULE + '.blender.layers').activate
Job = importlib.import_module(MODULE + '.blender.jobs').Job
REPORT = OUT / 'nocv.json'


def run_job(action, expected='succeeded', **kwargs):
    job = Job(action, **kwargs)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        receipt = job.poll()
        if receipt is not None:
            assert receipt['status'] == expected, receipt
            return job, receipt
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


def snapshot():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.get('qc_dataset'):
            data = storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
            result[obj.name] = {'manifest': obj['qc_dataset_sha256'],
                'arrays': {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in data.arrays.items()},
                'source_group': list(browser.source_group(obj)[0]), 'analysis': data.metadata.get('analysis')}
    return result


if args.reopen:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert snapshot() == report['snapshot']
    for obj in bpy.context.scene.objects:
        if obj.get('qc_dataset'):
            assert Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(Path(bpy.data.filepath).with_suffix('.qcdata'))
    bpy.context.scene.render.filepath = str(OUT / (args.reopen + '.png'))
    bpy.ops.render.render(write_still=True)
    report[args.reopen + '_cold_reopen'] = 'Passed'
else:
    source = input_path('sop/c10-c13', ROOT)
    real = source / 'multiwfn-cobh3-20260927'
    fchk = source / 'multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/COBH3.fch'
    job, _ = run_job('import', source=str(fchk))
    for obj in bpy.context.scene.objects:
        obj.hide_render = True
    atoms = views.atom_view(job.directory / 'dataset')
    activate(bpy.context, atoms)
    assert bpy.ops.qcblender.import_ets_nocv(output_path=str(real / 'COBH3-ETS-NOCV.txt'), energy_unit='kcal/mol') == {'FINISHED'}
    table = next(obj for obj in bpy.context.scene.objects if obj.get('qc_analysis_role') == 'ets_nocv')
    data = storage.load_dataset(bpy.path.abspath(table['qc_dataset']))
    pairs = data.metadata['analysis']['pairs']
    assert len(pairs) == 9 and pairs[0]['pair_energy'] == -77.88 and pairs[0]['energy_unit'] == 'kcal/mol'
    raw = (real / 'COBH3-ETS-NOCV.txt').read_text(encoding='utf-8')
    placeholder = 'Note: Energies of NOCV orbitals have not been evaluated, so they are all zero\n' + raw
    errors = {}
    for name, text, unit, expected in (
        ('placeholder', placeholder, 'kcal/mol', 'have not been evaluated'),
        ('unsupported', raw.replace('kcal/mol', 'eV'), 'kcal/mol', 'unsupported energy unit'),
        ('conflicting', raw, 'hartree', 'declares kcal/mol, not hartree')):
        path = OUT / (name + '.txt')
        path.write_text(text, encoding='utf-8')
        before = (set(bpy.data.objects.keys()), set(bpy.data.meshes.keys()))
        try:
            bpy.ops.qcblender.import_ets_nocv(output_path=str(path), energy_unit=unit)
        except RuntimeError as error:
            assert expected in str(error), error
            errors[name] = str(error)
        else:
            raise AssertionError(name)
        assert before == (set(bpy.data.objects.keys()), set(bpy.data.meshes.keys()))
    cases = {}
    header = 'Pair Energy | Orbital Eigenvalue Energy | Orbital Eigenvalue Energy\n'
    zero = header + '1 0.00 1 0.56514 0.00 51 -0.56514 0.00\n'
    for name, text, unit, count, energy in (
        ('placeholder-then-computed', placeholder + '\n' + raw, 'kcal/mol', 9, -77.88),
        ('legitimate-zero', 'All energies are given in kcal/mol\n' + zero, 'kcal/mol', 1, 0),
        ('missing-unit', zero, 'hartree', 1, 0)):
        path = OUT / (name + '.txt')
        path.write_text(text, encoding='utf-8')
        before = set(bpy.data.objects.keys())
        assert bpy.ops.qcblender.import_ets_nocv(output_path=str(path), energy_unit=unit) == {'FINISHED'}
        added = bpy.data.objects[(set(bpy.data.objects.keys()) - before).pop()]
        analysis = storage.load_dataset(bpy.path.abspath(added['qc_dataset'])).metadata['analysis']
        assert len(analysis['pairs']) == count and analysis['pairs'][0]['pair_energy'] == energy
        assert analysis['energy_unit'] == unit
        cases[name] = 'Passed'
    table_directory = Path(bpy.path.abspath(table['qc_dataset']))
    arguments = dict(source=str(real / 'COBH3-NOCV-pair1.cub'), table_dataset=str(table_directory),
                     table_sha256=table['qc_dataset_sha256'], unit='electron/bohr^3')
    before = set(bpy.data.objects.keys())
    for pair, spin in ((999, 'Total'), (1, 'Alpha')):
        _, error = run_job('import_nocv', expected='failed', pair_number=pair, spin=spin, **arguments)
        assert 'pair and spin' in error['error'], error
        assert before == set(bpy.data.objects.keys())
    job, _ = run_job('import_nocv', pair_number=1, spin='Total', **arguments)
    field = views.field_view(job.directory / 'dataset', atoms)
    field['qc_analysis_role'] = 'nocv_field'
    field['qc_ets_table_source'] = table['qc_source_sha256']
    data = storage.load_dataset(job.directory / 'dataset')
    descriptor = data.metadata['fields'][0]
    cube = importlib.import_module(MODULE + '.cube').read_cube(real / 'COBH3-NOCV-pair1.cub')
    np.testing.assert_array_equal(data.arrays[descriptor['array']], cube.arrays['cube_0'])
    assert data.metadata['analysis']['pair'] == pairs[0]
    modifier = field.modifiers[0]
    inputs = {s.name: s.identifier for s in modifier.node_group.interface.items_tree if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new('NOCV acceptance camera')
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = (6, -9, 6)
    camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type, camera_data.ortho_scale = 'ORTHO', 8
    scene.camera = camera
    light_data = bpy.data.lights.new('NOCV acceptance light', 'AREA')
    light_data.energy, light_data.size = 1500, 6
    light = bpy.data.objects.new(light_data.name, light_data)
    scene.collection.objects.link(light)
    light.location = (4, -6, 8)
    light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world.color = (.2, .2, .2)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x, scene.render.resolution_y = 800, 600
    scene.render.resolution_percentage = 100
    renders = []
    baseline = snapshot()
    for name, positive, negative, threshold in (('positive', True, False, .003), ('negative', False, True, .003), ('both', True, True, .006)):
        for key, value in {'Positive Phase': positive, 'Negative Phase': negative, 'Link Thresholds': False,
                           'Isovalue': threshold, 'Negative Isovalue': .002}.items():
            modifier[inputs[key]] = value
        field.update_tag()
        bpy.context.view_layer.update()
        scene.render.filepath = str(OUT / ('C13-' + name + '.png'))
        bpy.ops.render.render(write_still=True)
        renders.append(hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest())
    assert len(set(renders)) == 3 and snapshot() == baseline
    activate(bpy.context, field)
    project.save_project(OUT / 'C12-C13.blend')
    moved = OUT / 'moved'
    moved.mkdir(exist_ok=True)
    shutil.copy2(OUT / 'C12-C13.blend', moved / 'C12-C13.blend')
    shutil.copytree(OUT / 'C12-C13.qcdata', moved / 'C12-C13.qcdata', dirs_exist_ok=True)
    report = {'status': 'Passed', 'blender': bpy.app.version_string, 'pairs': pairs,
              'valid_count': 9, 'errors_preserve_scene': errors, 'cases': cases,
              'pair_spin_rejection': 'Passed', 'cube_arrays_match': 'Passed',
              'phase_threshold_renders': renders, 'source_arrays_unchanged': 'Passed',
              'saved_cold_reopen': 'Not Run', 'moved_cold_reopen': 'Not Run', 'snapshot': snapshot()}
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({key: value for key, value in report.items() if key != 'snapshot'}))
