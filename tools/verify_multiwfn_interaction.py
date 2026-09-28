"""Installed interaction checks; run prepare, then reopen each saved blend in fresh Blender processes.

blender --background --factory-startup --python tools/verify_multiwfn_interaction.py -- \
  --mode prepare --fixture outputs/multiwfn-parameters/01-foundation-r5/final-sop/cases/C07/C07.blend \
  --out outputs/multiwfn-parameters/02-interaction
blender --background --factory-startup --python tools/verify_multiwfn_interaction.py -- \
  --mode reopen --fixture outputs/multiwfn-parameters/02-interaction/evidence.blend \
  --out outputs/multiwfn-parameters/02-interaction
Repeat reopen with --fixture "<out>/moved 中文 path/evidence.blend".
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import sys

import bpy
from mathutils import Matrix, Vector
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qc_evidence', ROOT / 'tools/verify_vmd_parameters.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
module = evidence.module
SOURCE_CUBE = ROOT / 'outputs/v1-acceptance/sources/c07-c09-research/phenol-2026-09-27/igmh/dg_inter.cub'


def status(report, name, action):
    try:
        detail = action()
    except Exception as error:
        report[name] = {'status': 'Failed', 'error': repr(error)}
        raise
    report[name] = {'status': 'Passed', 'detail': detail}


def slice_state(obj):
    modifier, sockets = module('blender.interaction').slice_controls(obj)
    return {'definition': json.loads(obj.get('qc_plane_definition', '{}')),
            'controls': {name: list(modifier[sockets[name]]) if name in ('Center', 'Rotation')
                         else float(modifier[sockets[name]])
                         for name in ('Center', 'Rotation', 'Width', 'Height', 'Resolution')},
            'transform': [list(row) for row in obj.matrix_world],
            'volume_transform': [list(row) for row in obj.qc_settings.volume.matrix_world],
            'dataset': obj.get('qc_dataset_sha256'), 'source': obj.get('qc_source_sha256'),
            'field': json.loads(obj['qc_field'])}


def activate(obj):
    evidence.activate(obj)


def make_cube(out):
    """Six source atoms: one valid plane and one collinear triple, on a sheared Å grid."""
    path = out / 'affine-six-atoms.cube'
    steps = np.array(((1., .25, 0.), (.2, 1., .15), (.1, .3, 1.1)))
    indices = np.array(((1, 1, 1), (2, 1, 1), (1, 2, 1),
                        (0, 0, 0), (1, 0, 0), (2, 0, 0)), dtype=float)
    atoms = indices @ steps
    lines = ['QC affine interaction fixture', 'Values = i + 2j + 3k', '6 0 0 0']
    lines += [f'-4 {step[0]:.12g} {step[1]:.12g} {step[2]:.12g}' for step in steps]
    lines += [f'1 1 {x:.12g} {y:.12g} {z:.12g}' for x, y, z in atoms]
    values = [i + 2*j + 3*k for i, j, k in itertools.product(range(4), repeat=3)]
    lines += [' '.join(map(str, values[i:i+8])) for i in range(0, len(values), 8)]
    path.write_text('\n'.join(lines) + '\n', encoding='ascii')
    data = module('cube').read_cube(path)
    field = data.metadata['fields'][0]
    field.update(quantity='electron_number_density', unit='electron/bohr^3',
                 interpretation='user_assigned', vdb='field.vdb')
    directory = out / 'affine-source'
    directory.mkdir(exist_ok=True)
    cache = directory / 'field.vdb'
    module('worker').write_volume(data, cache)
    field['vdb_sha256'] = hashlib.sha256(cache.read_bytes()).hexdigest()
    module('data').save_dataset(data, directory)
    return directory, data


def check_real_c07():
    surface = next(obj for obj in bpy.context.scene.objects
                   if obj.get('qc_view_kind') == 'field'
                   and json.loads(obj['qc_field'])['quantity'] == 'delta_g')
    volume, field, metadata, source = module('blender.source_browser').bound_field(surface)
    assert source['sha256'] == hashlib.sha256(SOURCE_CUBE.read_bytes()).hexdigest()
    saved = module('data').load_dataset(bpy.path.abspath(volume['qc_dataset']))
    original = module('cube').read_cube(SOURCE_CUBE)
    values = saved.arrays[field['array']]
    np.testing.assert_array_equal(values, original.arrays['cube_0'])
    index = np.array((5.25, 6.5, 7.75))
    point = np.asarray(field['origin']) + index @ np.asarray(field['steps'])
    sampled = module('sampling').sample_point(values, saved.arrays[field['valid_mask']], field, point)
    direct = sum(np.prod([t if bit else 1-t for t, bit in zip(index % 1, bits)])
                 * values[tuple(np.floor(index).astype(int) + bits)]
                 for bits in itertools.product((0, 1), repeat=3))
    np.testing.assert_allclose(sampled, direct, rtol=0, atol=1e-12)
    world = volume.matrix_world @ Vector(point)
    np.testing.assert_allclose(module('profile').source_positions(world, world, volume.matrix_world)[0],
                               point, rtol=0, atol=2e-6)
    return {'source_sha256': source['sha256'], 'sample': sampled, 'unit': field['unit']}


def check_planes(out):
    directory, data = make_cube(out)
    field = data.metadata['fields'][0]
    source = module('blender.views').field_view(directory)
    source.name = 'Interaction affine field'
    atoms = module('blender.views').atom_view(directory)
    atoms.name = 'Interaction affine atoms'
    baseline = evidence.hashes()
    activate(source)
    assert bpy.ops.qcblender.create_slice() == {'FINISHED'}
    section = bpy.context.object
    section.name = 'Interaction affine slice'
    initial = slice_state(section)
    assert initial['definition']['mode'] == 'ij' and initial['definition']['position'] == .5
    assert initial['controls']['Resolution'] == 101

    volume = source.qc_settings.volume
    volume.matrix_world = (Matrix.Translation((2., -1., 3.)) @ Matrix.Rotation(.4, 4, 'Z')
                           @ Matrix.Diagonal((1.2, .8, 1.1, 1.)))
    atoms.matrix_world = volume.matrix_world.copy()
    section.matrix_world = Matrix.Translation((-1., 2., -.5)) @ Matrix.Rotation(.2, 4, 'X')
    source_to_view = np.asarray(section.matrix_world.inverted() @ volume.matrix_world)
    plane = module('planes')
    frames = {}
    for mode in ('ij', 'jk', 'ki'):
        activate(section)
        assert bpy.ops.qcblender.define_slice_plane(mode=mode, position=.5) == {'FINISHED'}, mode
        state = slice_state(section)
        assert state['definition']['mode'] == mode and state['definition']['position'] == .5
        center, axes, width, height = plane.plane_frame(field, mode, source_to_view, .5)
        np.testing.assert_allclose(state['controls']['Center'], center, atol=2e-5)
        np.testing.assert_allclose(state['controls']['Width'], width, atol=2e-5)
        np.testing.assert_allclose(state['controls']['Height'], height, atol=2e-5)
        np.testing.assert_allclose(axes.T @ axes, np.eye(3), atol=1e-9)
        fixed = {'ij': 2, 'jk': 0, 'ki': 1}[mode]
        grid_center = (np.asarray(center) - source_to_view[:3, 3]) @ np.linalg.inv(source_to_view[:3, :3]).T
        grid_index = (grid_center - field['origin']) @ np.linalg.inv(np.asarray(field['steps']))
        np.testing.assert_allclose(grid_index[fixed], 1.5, atol=2e-5)
        free = [axis for axis in range(3) if axis != fixed]
        for a, b in itertools.product((0., 3.), repeat=2):
            index = np.full(3, 1.5)
            index[free] = (a, b)
            source_corner = index @ np.asarray(field['steps']) + field['origin']
            corner = source_corner @ source_to_view[:3, :3].T + source_to_view[:3, 3]
            projection = (corner - center) @ axes
            assert abs(projection[0]) <= width/2 + 2e-5
            assert abs(projection[1]) <= height/2 + 2e-5
            assert abs(projection[2]) <= 2e-5
        frames[mode] = {'center': list(map(float, center)), 'width': width, 'height': height}

    activate(section)
    assert bpy.ops.qcblender.define_slice_plane(mode='atoms', configuration=atoms.name,
                                                atom_1=1, atom_2=2, atom_3=3) == {'FINISHED'}
    assert slice_state(section)['definition']['source_numbers'] == [1, 2, 3]
    before = slice_state(section)
    assert evidence.expect_error(lambda: bpy.ops.qcblender.define_slice_plane(
        mode='atoms', configuration=atoms.name, atom_1=4, atom_2=5, atom_3=6), '')
    assert slice_state(section) == before, 'Collinear rejection changed the slice'
    original_sha = atoms['qc_source_sha256']
    try:
        atoms['qc_source_sha256'] = '0' * 64
        assert evidence.expect_error(lambda: bpy.ops.qcblender.define_slice_plane(
            mode='atoms', configuration=atoms.name, atom_1=1, atom_2=2, atom_3=3), '')
        assert slice_state(section) == before, 'Source identity rejection changed the slice'
    finally:
        atoms['qc_source_sha256'] = original_sha

    assert bpy.ops.qcblender.layer_action(target=section.name, action='DUPLICATE') == {'FINISHED'}
    duplicated = bpy.context.object
    duplicated.name = 'Interaction duplicated slice'
    assert slice_state(duplicated) == before, 'Display-layer duplication lost plane definition or binding'
    activate(source)
    assert bpy.ops.qcblender.create_slice() == {'FINISHED'}
    target = bpy.context.object
    target.name = 'Interaction parameter target'
    assert bpy.ops.qcblender.define_slice_plane(mode='jk', position=.5) == {'FINISHED'}
    activate(section)
    target.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    module('blender.interaction')._sync_plane_labels_timer()
    assert slice_state(target)['definition']['mode'] == 'FREE', 'Parameter copy kept a stale plane identity'
    assert slice_state(target)['source'] == before['source']
    modifier, sockets = module('blender.interaction').slice_controls(section)
    modifier[sockets['Center']] = (0.25, .5, .75)
    module('blender.interaction')._sync_plane_labels_timer()
    assert slice_state(section)['definition']['mode'] == 'FREE'

    sample_point = np.array((1.2, 1.3, 1.4)) @ np.asarray(field['steps'])
    world = volume.matrix_world @ Vector(sample_point)
    source_point = module('profile').source_positions(world, world, volume.matrix_world)[0]
    # Blender Matrix/Vector are float32; retain tight double precision checks above for raw arrays.
    np.testing.assert_allclose(source_point, sample_point, atol=2e-6)
    value = module('sampling').sample_point(data.arrays[field['array']],
                                             data.arrays[field['valid_mask']], field, source_point)
    np.testing.assert_allclose(value, 1.2 + 2*1.3 + 3*1.4, atol=1e-5)
    assert evidence.hashes() == baseline, 'Plane controls changed scientific arrays'
    return {'frames': frames, 'synthetic_sample': value,
            'objects': [section.name, duplicated.name, target.name, atoms.name, source.name]}


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    report = {'cold_open': 'Not Run', 'moved_cold_open': 'Not Run',
              'modal_probe_and_gizmo_gui': 'Not Run: Computer Use in visible Blender',
              'status': 'Not Run'}
    try:
        status(report, 'real_c07_parsed_sampling', check_real_c07)
        status(report, 'affine_planes_and_rejections', lambda: check_planes(out))
        before = evidence.hashes()
        report['arrays'] = before
        report['slices'] = {obj.name: slice_state(obj) for obj in bpy.context.scene.objects
                            if obj.get('qc_view_kind') == 'slice' and obj.name.startswith('Interaction ')}
        report['sources'] = {obj.name: [obj.get('qc_dataset_sha256'), obj.get('qc_source_sha256')]
                             for obj in bpy.context.scene.objects if obj.get('qc_dataset')}
        module('blender.project').save_project(out / 'evidence.blend')
        assert evidence.hashes() == before, 'Portable save changed scientific arrays'
        moved = out / 'moved 中文 path'
        moved.mkdir(exist_ok=True)
        shutil.copy2(out / 'evidence.blend', moved / 'evidence.blend')
        shutil.copytree(out / 'evidence.qcdata', moved / 'evidence.qcdata', dirs_exist_ok=True)
        report['portable_save_arrays'] = 'Passed'
    except Exception as error:
        report['status'] = 'Failed'
        report['error'] = repr(error)
        raise
    finally:
        (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def reopen(out):
    report = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
    moved = 'moved 中文 path' in Path(bpy.data.filepath).parts
    key = 'moved_cold_open' if moved else 'cold_open'
    try:
        assert evidence.hashes() == report['arrays'], 'Scientific arrays changed across cold reopen'
        for name, expected in report['slices'].items():
            assert slice_state(bpy.data.objects[name]) == expected, name
        for name, expected in report['sources'].items():
            obj = bpy.data.objects[name]
            assert [obj.get('qc_dataset_sha256'), obj.get('qc_source_sha256')] == expected, name
            assert Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(Path(bpy.data.filepath).parent)
        report[key] = 'Passed'
        report['status'] = ('Passed' if report['cold_open'] == report['moved_cold_open'] == 'Passed'
                            else 'Not Run')
    except Exception as error:
        report[key] = 'Failed'
        report['status'] = 'Failed'
        report['error'] = repr(error)
        raise
    finally:
        (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return {key: report[key], 'status': report['status']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('prepare', 'reopen'), required=True)
    parser.add_argument('--fixture', type=Path, required=True, help='C07 blend, or saved evidence blend for reopen')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    out = args.out.resolve()
    assert out.is_relative_to((ROOT / 'outputs').resolve()), 'Use a task directory under outputs/'
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to((ROOT / 'outputs').resolve()), 'Use an isolated Blender profile under outputs/'
    assert bpy.ops.preferences.addon_enable(module=evidence.MODULE) == {'FINISHED'}
    installed = Path(module('blender.interaction').__file__).resolve()
    assert 'extensions' in installed.parts and installed != ROOT / 'qcblender/blender/interaction.py'
    assert bpy.ops.wm.open_mainfile(filepath=str(args.fixture.resolve(strict=True))) == {'FINISHED'}
    result = prepare(out) if args.mode == 'prepare' else reopen(out)
    print(json.dumps(result, ensure_ascii=False))
