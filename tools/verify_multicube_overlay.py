"""Verify two public P03 Cube layers and their self-contained cold reopen.

Creation: --output DIR --source-root REPOSITORY --module INSTALLED_PACKAGE
Cold open: open the saved or relocated blend, then pass --output DIR and
--reopen saved|moved. DIR must contain overlay-expected.json. The tool performs
native data/API checks; it does not claim GUI or independent scientific review.
"""
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


SOURCES = (
    ('color.cube', '18a33c308c868c9f7747128f1a23c04fc69df37fd5b9681aa5dd35ef20997958',
     'sign_lambda2_rho', 'electron/bohr^3', .03, .02),
    ('igmh/dg_inter.cub', 'daf5a7e79c7dcc67b244f3dc1d2d314795c9f318c931e4f25d36e72ea168a28e',
     'delta_g_inter', 'electron/bohr^4', .005, .008),
)
CONTROLS = ('Isovalue', 'Negative Isovalue', 'Link Thresholds', 'Positive Phase', 'Negative Phase')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_job(job):
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return result
        time.sleep(.1)
    cancellation = job.cancel()
    raise TimeoutError(f'{job.directory}; cancellation={cancellation}')


def controls(obj):
    modifier = next(modifier for modifier in obj.modifiers if modifier.type == 'NODES')
    return modifier, {socket.name: socket.identifier for socket in modifier.node_group.interface.items_tree
                      if socket.item_type == 'SOCKET' and socket.in_out == 'INPUT'}


def state(obj):
    modifier, names = controls(obj)
    return dict(parameters={name: modifier[names[name]] for name in CONTROLS},
                hide_viewport=obj.hide_viewport, hide_render=obj.hide_render,
                matrix_world=[list(row) for row in obj.matrix_world])


def mesh_count(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        count = [len(mesh.vertices), len(mesh.polygons)]
        assert all(value > 0 for value in count), (obj.name, count)
        return count
    finally:
        evaluated.to_mesh_clear()


def array_identity(data):
    return {name: dict(sha256=hashlib.sha256(value.tobytes()).hexdigest(),
                       dtype=str(value.dtype), shape=list(value.shape))
            for name, value in sorted(data.arrays.items())}


def bundle_identity(blend):
    root = blend.with_suffix('.qcdata')
    return dict(blend_sha256=digest(blend),
                data_files={path.relative_to(root).as_posix(): digest(path)
                            for path in sorted(root.rglob('*')) if path.is_file()})


def dataset_snapshot(obj, storage):
    directory = Path(bpy.path.abspath(obj['qc_dataset'])).resolve(strict=True)
    assert digest(directory / 'manifest.json') == obj['qc_dataset_sha256']
    data = storage.load_dataset(directory)
    return dict(manifest_sha256=obj['qc_dataset_sha256'], source_sha256=obj['qc_source_sha256'],
                arrays=array_identity(data), field=json.loads(obj['qc_field']))


def local_paths():
    root = Path(bpy.data.filepath).resolve(strict=True).with_suffix('.qcdata')
    assert root.is_dir(), root
    result = {}
    for obj in bpy.data.objects:
        if obj.get('qc_dataset'):
            stored = obj['qc_dataset']
            path = Path(bpy.path.abspath(stored)).resolve(strict=True)
            assert stored.startswith('//') and path.is_relative_to(root), (obj.name, stored, root)
            result['dataset:' + obj.name] = path.relative_to(root).as_posix()
    for volume in bpy.data.volumes:
        path = Path(bpy.path.abspath(volume.filepath)).resolve(strict=True)
        assert volume.filepath.startswith('//') and path.is_relative_to(root), (volume.name, path, root)
        assert volume.grids.load(), volume.filepath
        result['volume:' + volume.name] = path.relative_to(root).as_posix()
    return result


def create(out, source_root, module):
    storage = importlib.import_module(module + '.data')
    jobs = importlib.import_module(module + '.blender.jobs')
    views = importlib.import_module(module + '.blender.views')
    project = importlib.import_module(module + '.blender.project')
    blend = out / 'overlay.blend'
    moved = out / 'moved 中文 path'
    for path in (blend, blend.with_suffix('.qcdata'), moved, out / 'overlay-expected.json'):
        if path.exists():
            raise FileExistsError(f'Choose a new output directory; existing artifact: {path}')
    assert not any(obj.get('qc_dataset') for obj in bpy.data.objects), 'Use a fresh isolated scene'
    surfaces, inputs, source_arrays = [], [], []
    reference = None
    for index, (relative, sha, quantity, unit, threshold, _) in enumerate(SOURCES):
        path = (source_root / 'validation/shared/data/public/P03' / relative).resolve(strict=True)
        assert digest(path) == sha, ('Public fixture identity mismatch', path)
        importer = jobs.Job('import', source=str(path), source_sha256=sha)
        run_job(importer)
        imported = storage.load_dataset(importer.directory / 'dataset')
        before = array_identity(imported)
        assert imported.metadata['source']['sha256'] == sha
        assert len(imported.arrays['atomic_numbers']) == 6
        field = imported.metadata['fields'][0]
        assert field['shape'] == [91, 38, 156], field['shape']
        declaration = jobs.Job('declare_field', dataset=str(importer.directory / 'dataset'),
                               dataset_sha256=digest(importer.directory / 'dataset/manifest.json'),
                               field_array=field['array'], quantity='custom',
                               custom_quantity=quantity, custom_unit=unit)
        run_job(declaration)
        directory = declaration.directory / 'dataset'
        data = storage.load_dataset(directory)
        assert array_identity(data) == before, 'Declaration changed numeric arrays'
        assert (data.metadata['fields'][0]['quantity'], data.metadata['fields'][0]['unit']) == (quantity, unit)
        if reference is None:
            reference = data
            atoms = views.atom_view(directory)
            atoms.name = 'QC P03 shared atoms'
        else:
            np.testing.assert_array_equal(data.arrays['atomic_numbers'], reference.arrays['atomic_numbers'])
            np.testing.assert_allclose(data.arrays['positions'], reference.arrays['positions'], atol=1e-8, rtol=0)
        surface = views.field_view(directory, atoms)
        surface.name = 'QC P03 ' + quantity
        modifier, names = controls(surface)
        for name, value in {'Isovalue': threshold, 'Negative Isovalue': .01,
                            'Link Thresholds': False, 'Positive Phase': True,
                            'Negative Phase': index == 0}.items():
            modifier[names[name]] = value
        surface.hide_viewport = surface.hide_render = False
        surfaces.append(surface)
        source_arrays.append(before)
        inputs.append(dict(path=str(path), sha256=sha, quantity=quantity, unit=unit,
                           import_job=str(importer.directory), declaration_job=str(declaration.directory)))
    assert surfaces[0].qc_settings.volume != surfaces[1].qc_settings.volume
    assert controls(surfaces[0])[0].node_group != controls(surfaces[1])[0].node_group
    np.testing.assert_allclose(np.array(surfaces[0].matrix_world), np.array(surfaces[1].matrix_world), atol=1e-8)
    baseline = {obj.name: dict(state=state(obj), counts=mesh_count(obj), dataset=dataset_snapshot(obj, storage))
                for obj in surfaces}
    changes = []
    for index, obj in enumerate(surfaces):
        other = surfaces[1 - index]
        modifier, names = controls(obj)
        modifier[names['Isovalue']] = SOURCES[index][5]
        changed = mesh_count(obj)
        assert changed != baseline[obj.name]['counts'], ('Threshold did not change geometry', obj.name)
        assert state(other) == baseline[other.name]['state']
        assert mesh_count(other) == baseline[other.name]['counts']
        changes.append(dict(view=obj.name, threshold=SOURCES[index][5], counts=changed))
        modifier[names['Isovalue']] = SOURCES[index][4]
        for flag in ('hide_viewport', 'hide_render'):
            setattr(obj, flag, True)
            bpy.context.view_layer.update()
            assert getattr(obj, flag) is True
            assert state(other) == baseline[other.name]['state']
            assert mesh_count(other) == baseline[other.name]['counts']
            setattr(obj, flag, False)
        assert state(obj) == baseline[obj.name]['state']
        assert mesh_count(obj) == baseline[obj.name]['counts']
    for index, obj in enumerate(surfaces):
        assert dataset_snapshot(obj, storage) == baseline[obj.name]['dataset']
        assert dataset_snapshot(obj, storage)['arrays'] == source_arrays[index]
    project.save_project(blend)
    paths = local_paths()
    for obj in surfaces:
        assert dataset_snapshot(obj, storage) == baseline[obj.name]['dataset']
        assert state(obj) == baseline[obj.name]['state']
        assert mesh_count(obj) == baseline[obj.name]['counts']
    report = dict(status='Passed', blender=bpy.app.version_string, module=module,
                  module_file=str(Path(views.__file__).resolve()), inputs=inputs,
                  checks=['actual import and declaration jobs', 'same atom identities and coordinates',
                          'independent thresholds and nonempty geometry', 'independent visibility flags',
                          'scientific arrays unchanged', 'self-contained local paths'],
                  surfaces=baseline, threshold_changes=changes, local_paths=paths,
                  blend='overlay.blend', relocated_blend='moved 中文 path/overlay.blend',
                  saved_path=str(blend.resolve()), moved_path=str((moved / blend.name).resolve()),
                  bundle=bundle_identity(blend),
                  saved_cold_reopen='Not Run', moved_cold_reopen='Not Run',
                  GUI='Not Run', independent_scientific_acceptance='Not Run')
    (out / 'overlay-expected.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    moved.mkdir()
    shutil.copy2(blend, moved / blend.name)
    shutil.copytree(blend.with_suffix('.qcdata'), moved / blend.with_suffix('.qcdata').name)
    shutil.copy2(out / 'overlay-expected.json', moved / 'overlay-expected.json')
    assert bundle_identity(moved / blend.name) == report['bundle']
    return report


def reopen(out, module, mode):
    report = json.loads((out / 'overlay-expected.json').read_text(encoding='utf-8'))
    storage = importlib.import_module(module + '.data')
    assert report['module'] == module
    assert Path(bpy.data.filepath).name == report['blend']
    assert Path(bpy.data.filepath).resolve() == Path(report[mode + '_path']).resolve()
    assert bundle_identity(Path(bpy.data.filepath).resolve()) == report['bundle']
    assert local_paths() == report['local_paths']
    for name, expected in report['surfaces'].items():
        obj = bpy.data.objects[name]
        assert state(obj) == expected['state'], name
        assert dataset_snapshot(obj, storage) == expected['dataset'], name
        assert mesh_count(obj) == expected['counts'], name
    return dict(status='Passed', check=mode + '_cold_reopen', blend=str(Path(bpy.data.filepath).resolve()),
                blender=bpy.app.version_string, module=module, local_paths=report['local_paths'],
                surfaces=report['surfaces'], GUI='Not Run', independent_scientific_acceptance='Not Run')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--module', default='bl_ext.user_default.qcblender')
    parser.add_argument('--reopen', choices=('saved', 'moved'))
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    result_path = args.output / ('overlay-reopen-' + args.reopen + '.json' if args.reopen else 'overlay.json')
    try:
        bpy.ops.preferences.addon_enable(module=args.module)
        result = (reopen(args.output, args.module, args.reopen) if args.reopen else
                  create(args.output, args.source_root.resolve(strict=True), args.module))
    except Exception as error:
        result_path.write_text(json.dumps(dict(status='Failed', error_type=type(error).__name__,
                                               error=str(error)), indent=2), encoding='utf-8')
        raise
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('MULTICUBE_OVERLAY_PASSED: ' + (args.reopen or 'create'))
