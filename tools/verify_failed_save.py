"""A real Blender save failure must retain the previous portable-project index."""
import importlib
import json
from pathlib import Path
import tempfile

import bpy

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
project = importlib.import_module(MODULE + '.blender.project')
original = {obj.name: obj['qc_dataset'] for obj in bpy.data.objects if 'qc_dataset' in obj}
original_volumes = {v.name: v.filepath for v in bpy.data.volumes}
with tempfile.TemporaryDirectory(prefix='failed-save-', dir=ROOT / 'outputs') as temporary:
    target = Path(temporary) / 'previous.blend'
    # An existing directory at the file path forces Blender's real save operator to fail.
    target.mkdir()
    sidecar = target.with_suffix('.qcdata')
    sidecar.mkdir()
    manifest = sidecar / 'manifest.json'
    previous = b'{"format":"qcblender.scene","schema":"0.1","datasets":[],"sentinel":"previous"}\n'
    manifest.write_bytes(previous)
    try:
        project.save_project(target)
    except (OSError, RuntimeError):
        pass
    else:
        raise AssertionError('Expected the real Blender save to fail')
    assert manifest.read_bytes() == previous, 'Failed save replaced the previous scene index'
    assert {o.name: o['qc_dataset'] for o in bpy.data.objects if 'qc_dataset' in o} == original
    assert {v.name: v.filepath for v in bpy.data.volumes} == original_volumes
    fresh = Path(temporary) / 'first-save.blend'
    fresh.mkdir()
    try:
        project.save_project(fresh)
    except (OSError, RuntimeError):
        pass
    else:
        raise AssertionError('Expected the first save to fail')
    assert not (fresh.with_suffix('.qcdata') / 'manifest.json').exists()
    assert {o.name: o['qc_dataset'] for o in bpy.data.objects if 'qc_dataset' in o} == original
    assert {v.name: v.filepath for v in bpy.data.volumes} == original_volumes
report = {'status': 'Passed', 'real_save_failure': 'Observed', 'previous_scene_index': 'Preserved',
          'live_dataset_and_volume_paths': 'Preserved', 'failed_first_save_index': 'Absent'}
(ROOT / 'outputs/acceptance/failed-save.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
