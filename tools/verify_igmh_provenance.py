"""Installed-extension native import and portable P03 declaration verification.

Run in an isolated Blender profile under <sample>/outputs:
  blender --background --python this_file -- --root ROOT --sample SAMPLES
          --out OUT --zip CANDIDATE.zip
Cold read (both original and moved directory): use --factory-startup, then add
--reopen --blend PROJECT.blend. The script installs/enables the candidate before
opening the project through open_mainfile and the real load_post handlers.
Each run needs a new or empty --out directory. The script uses real Job workers
and registered operators.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--sample', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--zip', type=Path, required=True)
parser.add_argument('--reopen', action='store_true')
parser.add_argument('--blend', type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
reopen_target = None
if args.reopen:
    target = args.blend or (Path(bpy.data.filepath) if bpy.data.filepath else None)
    if target is None:
        parser.error('--reopen requires --blend PROJECT.blend or an already loaded project')
    reopen_target = target.resolve(strict=True)
    if not reopen_target.is_file() or reopen_target.suffix.lower() != '.blend':
        parser.error('--blend must identify an existing .blend file')
elif args.blend is not None:
    parser.error('--blend is available only with --reopen')
if args.out.exists() and any(args.out.iterdir()):
    raise FileExistsError(f'Validation output directory must be new or empty: {args.out}')
args.out.mkdir(parents=True, exist_ok=True)
sys.path[:0] = [str(args.root), str(args.sample / 'outputs/science')]
from tools.local_inputs import input_path
import numpy as np

assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.sample / 'outputs'), 'Use an isolated validation profile'
assert bpy.ops.extensions.package_install_files(filepath=str(args.zip), repo='user_default',
                                                 enable_on_install=True, overwrite=True) == {'FINISHED'}
MODULE = 'bl_ext.user_default.qcblender'
package = importlib.import_module(MODULE)
installed = Path(package.__file__).parent
for relative in ('external_fields.py', 'static_reference.py', 'blender/external_fields.py'):
    assert (installed / relative).read_bytes() == (args.root / 'qcblender' / relative).read_bytes(), relative


def module(name):
    return importlib.import_module(MODULE + '.' + name)


storage = module('data')
external = module('external_fields')
views = module('blender.views')
ui = module('blender.ui')
browser = module('blender.source_browser')
exports = module('data_export')
checks = []


def passed(name, **details):
    checks.append(dict(check=name, status='Passed', **details))
    print('Passed:', name, flush=True)


def activate(obj):
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def run_pair(parent, geometry, color, **declaration):
    activate(parent)
    before = set(ui._operations)
    result = bpy.ops.qcblender.import_paired_field(
        'EXEC_DEFAULT', method='IGMH', geometry_source=str(geometry), color_source=str(color),
        geometry_unit='electron/bohr^4', color_unit='electron/bohr^3', **declaration)
    assert result == {'RUNNING_MODAL'}, result
    keys = set(ui._operations) - before
    assert len(keys) == 1, keys
    operator = ui._operations[keys.pop()][0]
    until = time.monotonic() + 240
    while time.monotonic() < until:
        verdict = operator.modal(bpy.context, SimpleNamespace(type='TIMER'))
        if verdict != {'RUNNING_MODAL'}:
            assert verdict == {'FINISHED'}, (verdict, operator._job.directory)
            return operator
        time.sleep(.05)
    operator.cancel(bpy.context)
    raise TimeoutError('Paired field worker did not complete')


def cached_dataset(data, name):
    directory = args.out / 'datasets' / name
    directory.mkdir(parents=True, exist_ok=True)
    for index, field in enumerate(data.metadata.get('fields', [])):
        field['vdb'] = f'field-{index}.vdb'
        module('worker').write_volume(data, directory / field['vdb'], index)
        field['vdb_sha256'] = hashlib.sha256((directory / field['vdb']).read_bytes()).hexdigest()
    storage.save_dataset(data, directory)
    return directory


def paired_table(parent):
    return next(obj for obj in bpy.data.objects if obj.parent == parent and obj.get('qc_analysis_role') == 'paired')


def verify_p03(record, expected):
    directory = Path(bpy.path.abspath(record['qc_dataset']))
    data = storage.load_dataset(directory)
    declaration = data.metadata['analysis']['igmh_declaration']
    assert declaration['component'] == 'inter'
    assert declaration['fragments'] == [[1, 2, 3], [4, 5, 6]]
    assert declaration['interpretation'] == 'user_assigned'
    assert declaration['status'] == 'declared'
    assert declaration['source'] == 'P03 Multiwfn fragment setup'
    for key, values in expected.arrays.items():
        np.testing.assert_array_equal(data.arrays[key], values)
    assert browser.cached_metadata(record).get('analysis', {}).get('igmh_declaration') == declaration
    assert module('blender.external_fields').QCBLENDER_PT_igmh_declaration.poll(SimpleNamespace(object=record))
    metadata = browser.refresh_source(record)
    assert metadata['analysis']['igmh_declaration'] == declaration
    report = exports.export_dataset(directory, args.out / 'csv', 'paired')
    sidecar = json.loads(Path(report['directory'], 'metadata.json').read_text(encoding='utf-8'))
    assert sidecar['scientific_metadata']['analysis']['igmh_declaration'] == declaration
    first, second = data.metadata['fields']
    valid = data.arrays[first['valid_mask']] & data.arrays[second['valid_mask']]
    assert report['files'][0]['row_count'] == int(valid.sum())
    passed('P03 imported arrays, declaration, panel eligibility and CSV metadata',
           declaration=declaration, csv=report['directory'])


folder = input_path('public-tutorial/P03/igmh', args.sample)
geometry, color = folder / 'dg_inter.cub', folder / 'sl2r.cub'
expected = external.pair_cubes(geometry, color, 'IGMH', 'electron/bohr^4', 'electron/bohr^3')
if args.reopen:
    assert bpy.ops.wm.open_mainfile(filepath=str(reopen_target), load_ui=False) == {'FINISHED'}
    assert Path(bpy.data.filepath).resolve() == reopen_target
    record = next(obj for obj in bpy.data.objects if obj.get('qc_qualification') == 'P03-IGMH')
    assert record['qc_dataset'].startswith('//')
    verify_p03(record, expected)
    for obj in bpy.data.objects:
        if obj.get('qc_dataset'):
            storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
    passed('portable original or moved cold read after candidate enable and load_post',
           blend=bpy.data.filepath)
else:
    # All views below are real atom_view meshes with their source Dataset.
    gaussian = module('gaussian_log')
    source = input_path('log-examples/water_neutral_nbo_opt_freq.out', args.sample)
    static_log = gaussian.read_log(source, 1)
    static_fchk = module('readers').read_source(
        input_path('sop/c10-c13/peroxide-irc-pyscf/step-001.fchk', args.sample))
    static_cube = module('cube').read_cube(geometry)
    static_references = []
    for name, data in [('log', static_log), ('fchk', static_fchk), ('cube', static_cube)]:
        directory = cached_dataset(data, 'static-' + name)
        reference = views.atom_view(directory)
        reference['qc_qualification'] = 'static-' + name
        static_references.append((name, reference, data))
        module('blender.static_reference').capture_reference(reference)
        passed('static ' + name + ' atom_view eligibility')

    def small_pair(data, name):
        # Construct two explicit synthetic grids with the real reference nuclei.
        paths = []
        for role, values in [('geometry', '.1 .2 .3 .4 .5 .6 .7 .8'),
                             ('color', '-.04 -.03 -.02 -.01 .01 .02 .03 .04')]:
            path = args.out / (name + '-' + role + '.cube')
            rows = ['Synthetic native eligibility grid', 'Nuclei from real reference source',
                    f'{len(data.arrays["atomic_numbers"])} 0 0 0',
                    '-2 1 0 0', '-2 0 1 0', '-2 0 0 1']
            rows.extend(f'{int(number)} {int(number)} ' + ' '.join(f'{value:.12g}' for value in xyz)
                        for number, xyz in zip(data.arrays['atomic_numbers'], data.arrays['positions']))
            path.write_text('\n'.join(rows + [values]) + '\n', encoding='ascii')
            paths.append(path)
        return paths

    for name, reference, data in static_references[:2]:
        paths = small_pair(data, name)
        operator = run_pair(reference, *paths, igmh_component='total')
        imported = storage.load_dataset(operator._job.directory / 'dataset')
        assert imported.metadata['analysis']['igmh_declaration']['component'] == 'total'
        assert paired_table(reference) is not None
        passed('static ' + name + ' actual paired operator and worker',
               worker=str(operator._job.directory), grids='synthetic with real reference nuclei')

    cube_reference = static_references[2][1]
    operator = run_pair(cube_reference, geometry, color, igmh_component='inter',
                        igmh_fragments='[[1,2,3],[4,5,6]]',
                        igmh_declaration_source='P03 Multiwfn fragment setup')
    record = paired_table(cube_reference)
    record['qc_qualification'] = 'P03-IGMH'
    verify_p03(record, expected)
    passed('static Cube actual P03 paired operator and worker', worker=str(operator._job.directory))

    def refuse(obj, name):
        activate(obj)
        for operator_name in ('import_paired_field', 'import_nbo', 'import_aim_analysis', 'import_ets_nocv'):
            operation = getattr(bpy.ops.qcblender, operator_name)
            assert not operation.poll(), (name, operator_name)
            count = len(bpy.data.objects)
            try:
                operation('EXEC_DEFAULT')
            except RuntimeError as error:
                assert '独立' in str(error), str(error)
            else:
                raise AssertionError('Dynamic reference was accepted: ' + name)
            assert len(bpy.data.objects) == count
        # A real static mesh parented to the dynamic mesh tests ancestor guards.
        child = views.atom_view(Path(bpy.path.abspath(cube_reference['qc_dataset'])))
        child.parent = obj
        activate(child)
        assert not bpy.ops.qcblender.import_paired_field.poll()
        passed(name + ' actual atom_view reference and ancestor rejection')

    optimization = gaussian.read_log(source, 0)
    optimization_root = views.atom_view(cached_dataset(optimization, 'dynamic-optimization'))
    refuse(optimization_root, 'optimization source without selected step')
    activate(optimization_root)
    assert bpy.ops.qcblender.optimization_view() == {'FINISHED'}
    optimization_view = bpy.context.object
    refuse(optimization_view, 'optimization initial step 1')
    activate(optimization_view)
    assert bpy.ops.qcblender.optimization_step(direction='GOTO', step=2) == {'FINISHED'}
    refuse(optimization_view, 'optimization step 2')

    manifest = input_path('sop/c10-c13/peroxide-irc-pyscf', args.sample) / 'steps.csv'
    previous = {obj.as_pointer() for obj in bpy.data.objects}
    assert bpy.ops.qcblender.import_irc_path(manifest_path=str(manifest)) == {'FINISHED'}
    irc = next(obj for obj in bpy.data.objects if obj.as_pointer() not in previous and obj.get('qc_irc'))
    refuse(irc, 'IRC initial step 1')
    activate(irc)
    assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
    refuse(irc, 'IRC step 2')

    xyz = args.out / 'frames.xyz'
    xyz.write_text('1\nFrame one\nH 0 0 0\n1\nFrame two\nH 0 0 1\n', encoding='utf-8')
    trajectory = module('readers').read_source(xyz)
    xyz_view = views.atom_view(cached_dataset(trajectory, 'dynamic-xyz'))
    # Match the scientific import operator's atom_view -> initialize_trajectory
    # sequence before asking current_geometry or a step operator to inspect it.
    module('blender.trajectory').initialize_trajectory(xyz_view, trajectory)
    positions, identity = module('blender.geometry').current_geometry(xyz_view, trajectory)
    assert identity['kind'] == 'trajectory' and identity['step'] == 1
    np.testing.assert_array_equal(positions, trajectory.arrays['positions'])
    refuse(xyz_view, 'XYZ initial frame 1')
    activate(xyz_view)
    assert bpy.ops.qcblender.trajectory_frame(direction='GOTO', frame=2) == {'FINISHED'}
    positions, identity = module('blender.geometry').current_geometry(xyz_view, trajectory)
    assert identity['kind'] == 'trajectory' and identity['step'] == 2
    np.testing.assert_array_equal(positions, trajectory.arrays[trajectory.metadata['trajectory']['array']][1])
    refuse(xyz_view, 'XYZ frame 2')

    # Finish with the user-facing P03 view selected, then save using the operator.
    display = next(obj for obj in bpy.data.objects if obj.get('qc_analysis')
                   and obj.parent == cube_reference)
    display['qc_qualification'] = 'P03-IGMH-display'
    activate(display)
    target = args.out / 'P03-IGMH-portable.blend'
    assert bpy.ops.qcblender.save_project(filepath=str(target)) == {'FINISHED'}
    passed('Save Portable QC Project operator', blend=str(target))

report = {'status': 'Passed', 'checks': checks,
          'source_commit': subprocess.check_output(['git', '-C', str(args.root), 'rev-parse', 'HEAD'], text=True).strip(),
          'product_tree': subprocess.check_output(['git', '-C', str(args.root), 'rev-parse', 'HEAD:qcblender'], text=True).strip(),
          'candidate_zip_sha256': hashlib.sha256(args.zip.read_bytes()).hexdigest()}
(args.out / ('reopen-report.json' if args.reopen else 'report.json')).write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('IGMH_PROVENANCE_NATIVE_PASSED:', len(checks))
