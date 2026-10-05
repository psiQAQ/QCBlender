"""Native accept-boundary regression using real VDB bytes and scene datablocks.

Run in fresh Blender with --background --factory-startup --python-exit-code 1
--python this.py -- --dataset DIR --output NEW_DIR --case paired-second
[--root PRODUCT_CHECKOUT] [--science-root DIR].
Cases: paired-second, import-second, import-first. The same unchanged-scene
assertion fails on pre-fix products and passes after the accept guard is fixed.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--root', type=Path, default=ROOT)
parser.add_argument('--science-root', type=Path)
parser.add_argument('--case', choices=('paired-second', 'import-second', 'import-first'), required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
ROOT = args.root.resolve(strict=True)
sys.path[:0] = [str(ROOT), str(args.science_root or ROOT / 'outputs/science')]
import qcblender
assert Path(qcblender.__file__).resolve().parent == ROOT / 'qcblender', 'Product checkout does not match --root'
from qcblender.data import filesystem_path, load_dataset, save_dataset, volume_cache
from qcblender.static_reference import dynamic_reference
from qcblender.blender.external_fields import QCBLENDER_OT_import_paired_field
from qcblender.blender.static_reference import capture_reference
from qcblender.blender.ui import QCBLENDER_OT_import
from qcblender.blender.views import atom_view

qcblender.register()
out = args.output.resolve()
assert not out.exists(), 'Use a fresh task evidence directory'
out.mkdir(parents=True)
source = load_dataset(args.dataset)
assert not dynamic_reference(source.metadata), 'Use a static source fixture'
assert source.metadata.get('fields'), 'Source must provide a real VDB field'
original_field = source.metadata['fields'][0]
original_cache = volume_cache(args.dataset, original_field)

# A controlled two-field Dataset uses the exact same valid scientific samples.
# The second display cache is damaged after save while arrays and manifest stay intact.
result = deepcopy(source)
result.metadata['fields'] = [dict(original_field, vdb='field-0.vdb'),
                             dict(original_field, vdb='field-1.vdb')]
result.metadata['analysis'] = {'kind': 'IGMH', 'status': 'user_assigned'}
job = out / 'job'
directory = job / 'dataset'
directory.mkdir(parents=True)
for field in result.metadata['fields']:
    shutil.copy2(filesystem_path(original_cache), directory / field['vdb'])
save_dataset(result, directory)
bad_index = 0 if args.case == 'import-first' else 1
bad_cache = directory / result.metadata['fields'][bad_index]['vdb']
bad_cache.write_bytes(b'not an OpenVDB file')
probe = bpy.data.volumes.new('accept regression native probe')
try:
    probe.filepath = str(bad_cache)
    loaded = probe.grids.load()
    reason = probe.grids.error_message
    assert not loaded and reason, 'Fixture must fail actual Blender VDB load'
finally:
    bpy.data.volumes.remove(probe)

reference = out / 'reference'
reference_data = deepcopy(source)
reference_data.metadata['fields'] = []
save_dataset(reference_data, reference)
parent = atom_view(reference)
if args.case == 'paired-second':
    operator_type = QCBLENDER_OT_import_paired_field
    operation = SimpleNamespace(_job=SimpleNamespace(directory=job), _reference=parent,
                                _reference_path=reference, _reference_snapshot=capture_reference(parent),
                                color_minimum=-.05, color_maximum=.05, report=lambda *args: None)
else:
    operator_type = QCBLENDER_OT_import
    operation = SimpleNamespace(_job=SimpleNamespace(directory=job), _inspecting=False,
                                report=lambda *args: None)


def state():
    from qcblender.blender.source_browser import _metadata
    return {'datablocks': {name: set(getattr(bpy.data, name).keys())
                           for name in ('objects', 'meshes', 'volumes', 'materials', 'node_groups')},
            'bindings': {obj.name: {key: obj[key] for key in ('qc_dataset', 'qc_dataset_sha256', 'qc_field') if key in obj}
                         for obj in bpy.data.objects},
            'volume_paths': {volume.name: volume.filepath for volume in bpy.data.volumes},
            'active': bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
            'selected': tuple(sorted(obj.name for obj in bpy.context.selected_objects)),
            'metadata_cache_keys': set(_metadata)}


before = state()
try:
    # Actual registered operator accept implementation; only the completed worker
    # handoff is supplied, so no replacement stands in for native loading or views.
    operator_type.accept(operation, bpy.context, {'status': 'succeeded'})
except (OSError, ValueError, RuntimeError) as error:
    message = str(error)
else:
    raise AssertionError('Native-unreadable completed Dataset was accepted')
after = state()
added = {name: sorted(after['datablocks'][name] - before['datablocks'][name])
         for name in before['datablocks']}
report = {'case': args.case, 'native_error': reason, 'error': message, 'new_datablocks': added,
          'scene_unchanged': before == after,
          'diagnostic_matches': str(bad_cache) in message and reason in message,
          'module_root': str(ROOT), 'source_dataset': str(args.dataset)}
report['status'] = 'Passed' if report['scene_unchanged'] and report['diagnostic_matches'] else 'Failed'
(out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
assert report['diagnostic_matches'], message
assert before == after, 'Accept failure changed scene, bindings, metadata cache or datablocks'
