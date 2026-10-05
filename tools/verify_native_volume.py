"""Real Blender VDB/read/save/relocate checks using a supplied scientific dataset.

Use --background --factory-startup --python-exit-code 1 --python this.py --
--dataset DIR --output DIR [--science-root DIR]. Output belongs in outputs/.
Long paths are fixture construction, never a product readability criterion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--science-root', type=Path, default=ROOT / 'outputs/science')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
sys.path[:0] = [str(ROOT), str(args.science_root)]
import qcblender
from qcblender.data import filesystem_path, load_dataset, volume_cache
from qcblender.blender.native_volume import check_volume
from qcblender.blender.views import field_view
from qcblender.blender.project import rebind_dataset, save_project

qcblender.register()
out = args.output.resolve()
assert not out.exists(), 'Use a fresh evidence directory; existing files are preserved'
out.mkdir(parents=True)
report = {'checks': {}, 'source_dataset': str(args.dataset.resolve()), 'module_root': str(ROOT)}


def digest(path):
    return hashlib.sha256(filesystem_path(path).read_bytes()).hexdigest()


def clone(name):
    target = out / name
    shutil.copytree(filesystem_path(args.dataset), filesystem_path(target))
    return target


def snapshot():
    return {'ids': {name: tuple(getattr(bpy.data, name).keys())
                    for name in ('objects', 'volumes', 'meshes', 'materials', 'node_groups')},
            'bindings': {o.name: {key: o[key] for key in ('qc_dataset', 'qc_dataset_sha256', 'qc_field') if key in o}
                         for o in bpy.data.objects},
            'volumes': {v.name: v.filepath for v in bpy.data.volumes},
            'filepath': bpy.data.filepath}


def reject(name, operation, path=None, reason=None):
    before = snapshot()
    try:
        operation()
    except (OSError, ValueError, RuntimeError) as error:
        message = str(error)
        if path is not None:
            assert str(path) in message, message
        if reason:
            assert reason in message, message
    else:
        raise AssertionError(name + ' unexpectedly succeeded')
    assert snapshot() == before, name + ' modified live scene or leaked datablocks'
    report['checks'][name] = {'status': 'Passed', 'error': message}


def native(path):
    probe = bpy.data.volumes.new('verification native probe')
    try:
        probe.filepath = str(path)
        loaded = probe.grids.load()
        return {'loaded': loaded, 'reason': probe.grids.error_message,
                'grids': sorted(g.name for g in probe.grids), 'path': str(path)}
    finally:
        bpy.data.volumes.remove(probe)


def operator(operation):
    # Blender raises RuntimeError when an operator reports ERROR, even if execute returns CANCELLED.
    result = operation()
    assert result == {'CANCELLED'}, result
    raise ValueError('Operator returned CANCELLED')


ordinary = clone('ordinary')
chinese = clone('中文目录')
data = load_dataset(ordinary)
field = data.metadata['fields'][0]
for name, directory in [('ordinary', ordinary), ('chinese', chinese)]:
    cache = volume_cache(directory, field)
    before = snapshot()
    assert check_volume(cache) == {'qc_value', 'qc_negative', 'qc_valid'}
    assert snapshot() == before
    report['checks'][name] = {'status': 'Passed', 'native': native(cache)}

long_name = Path('long')
while len(str(out / long_name / field.get('vdb', 'field.vdb'))) < 300:
    long_name /= 'nested-volume-location-abcdefgh'
long = clone(long_name)
long_cache = volume_cache(long, field)
assert digest(long_cache) == digest(volume_cache(ordinary, field))
observation = native(long_cache)
report['long_path_native'] = observation
if not observation['loaded']:
    reject('long_field_no_scene_writes', lambda: field_view(long), long_cache, observation['reason'])
else:
    assert check_volume(long_cache) == {'qc_value', 'qc_negative', 'qc_valid'}
    report['checks']['long_field_no_scene_writes'] = {'status': 'Not Run', 'reason': 'Native runtime reads this long path'}

missing = clone('missing')
missing_cache = missing / field.get('vdb', 'field.vdb')
missing_cache.unlink()
reject('missing_native', lambda: check_volume(missing_cache), missing_cache)
reject('missing_field_no_scene_writes', lambda: field_view(missing))

corrupt = clone('corrupt')
corrupt_cache = corrupt / field.get('vdb', 'field.vdb')
corrupt_cache.write_bytes(b'not an OpenVDB file')
manifest = json.loads((corrupt / 'manifest.json').read_text(encoding='utf-8'))
manifest['metadata']['fields'][0]['vdb_sha256'] = digest(corrupt_cache)
(corrupt / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
reason = native(corrupt_cache)['reason']
reject('corrupt_field_no_scene_writes', lambda: field_view(corrupt), corrupt_cache, reason)

no_mask = clone('no-mask')
import openvdb
mask_cache = no_mask / field.get('vdb', 'field.vdb')
grids = openvdb.readAll(str(mask_cache))[0]
openvdb.write(str(mask_cache), grids=[grid for grid in grids if grid.name != 'qc_valid'])
manifest = json.loads((no_mask / 'manifest.json').read_text(encoding='utf-8'))
manifest['metadata']['fields'][0]['vdb_sha256'] = digest(mask_cache)
(no_mask / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
reject('missing_required_grid_no_scene_writes', lambda: field_view(no_mask), mask_cache, 'qc_valid')

surface = field_view(ordinary)
bpy.context.view_layer.objects.active = surface
assert bpy.ops.qcblender.save_project(filepath=str(out / 'current.blend')) == {'FINISHED'}
saved = Path(bpy.data.filepath)
saved_digest = digest(saved)
index = saved.with_suffix('.qcdata') / 'manifest.json'
saved_index = index.read_bytes()
source = Path(bpy.path.abspath(surface['qc_dataset'])).resolve()

if not observation['loaded']:
    reject('long_rebind_preserves_original', lambda: rebind_dataset(source, long), long_cache, observation['reason'])
    reject('long_relocate_operator_preserves_original', lambda: operator(
        lambda: bpy.ops.qcblender.relocate_dataset(filepath=str(long / 'manifest.json'))))
reject('corrupt_rebind_preserves_original', lambda: rebind_dataset(source, corrupt), corrupt_cache)
reject('missing_grid_rebind_preserves_original', lambda: rebind_dataset(source, no_mask), mask_cache)

# A real save failure: a directory at .blend prevents wm.save_as_mainfile writing the file.
blocked = out / 'blocked.blend'
blocked.mkdir()
blocked_index = blocked.with_suffix('.qcdata') / 'manifest.json'
blocked_index.parent.mkdir()
sentinel = b'{"sentinel":"previous scene index"}\n'
blocked_index.write_bytes(sentinel)
reject('real_save_failure_preserves_state', lambda: operator(
    lambda: bpy.ops.qcblender.save_project(filepath=str(blocked))))
assert blocked_index.read_bytes() == sentinel

long_target = out / long_name / 'portable.blend'
long_index = long_target.with_suffix('.qcdata') / 'manifest.json'
filesystem_path(long_index.parent).mkdir(parents=True, exist_ok=True)
filesystem_path(long_index).write_bytes(sentinel)
reject('unreadable_save_copy_preserves_state', lambda: save_project(long_target))
assert filesystem_path(long_index).read_bytes() == sentinel
assert digest(saved) == saved_digest and index.read_bytes() == saved_index
assert bpy.ops.qcblender.relocate_dataset(filepath=str(chinese / 'manifest.json')) == {'FINISHED'}
assert Path(surface['qc_dataset']) == chinese
report['checks']['chinese_relocate_operator'] = {'status': 'Passed'}
assert bpy.ops.qcblender.save_project(filepath=str(out / '中文工程.blend')) == {'FINISHED'}
report['checks']['chinese_save_operator'] = {'status': 'Passed'}
report['checks']['permission_denied'] = {'status': 'Not Run', 'reason': 'Requires supplied naturally denied target; no ACL changes'}
report['checks']['ui_undo_redo_cold_reopen'] = {'status': 'Not Run', 'reason': 'Separate foreground/cold-process validation'}
report['status'] = 'Passed'
(out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
