"""Run against the relocated acceptance .blend in an isolated Blender process."""
import hashlib
import importlib
import json
from pathlib import Path
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
storage = importlib.import_module(MODULE + '.data')
jobs = importlib.import_module(MODULE + '.blender.jobs')
project = importlib.import_module(MODULE + '.blender.project')
copies = importlib.import_module(MODULE + '.project')
views = importlib.import_module(MODULE + '.blender.views')


def finish(job):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        report = job.poll()
        if report is not None:
            assert report['status'] == 'succeeded', report
            return job.directory / 'dataset'
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


def vertices(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return np.array([v.co[:] for v in mesh.vertices])
    finally:
        evaluated.to_mesh_clear()


surface = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'field')
expected = vertices(surface)
original = Path(bpy.path.abspath(surface['qc_dataset'])).resolve()
data = storage.load_dataset(original)
cache = storage.volume_cache(original, data.metadata['fields'][0])
backup = cache.with_suffix('.vdb.held')
assert not backup.exists()
surface.qc_settings.volume.data.grids.unload()
cache.rename(backup)
try:
    rebuilt = finish(jobs.Job('rebuild_cache', dataset=str(original), dataset_sha256=surface['qc_dataset_sha256']))
    recovered = storage.load_dataset(rebuilt)
    for key in data.arrays:
        np.testing.assert_array_equal(data.arrays[key], recovered.arrays[key])
    project.rebind_dataset(original, rebuilt)
    np.testing.assert_array_equal(vertices(surface), expected)
finally:
    backup.rename(cache)
relocated = copies.copy_dataset(rebuilt, ROOT / 'outputs/recovery/另一个目录')
bpy.context.view_layer.objects.active = surface
assert bpy.ops.qcblender.relocate_dataset(filepath=str(relocated / 'manifest.json')) == {'FINISHED'}
assert Path(surface['qc_dataset']) == relocated
np.testing.assert_array_equal(vertices(surface), expected)

water = finish(jobs.Job('import', source=str(input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)), job_index=1))
atoms = views.atom_view(water)
bpy.context.view_layer.objects.active = atoms
assert bpy.ops.qcblender.color_charge(method='mulliken', minimum=-1, maximum=1) == {'FINISHED'}
existing = set(bpy.data.objects)
assert bpy.ops.qcblender.show_dipole() == {'FINISHED'}
arrow = (set(bpy.data.objects) - existing).pop()
vector = np.array(arrow['qc_dipole_debye'])
length = np.linalg.norm(vector)
projection = vertices(arrow) @ (vector / length)
np.testing.assert_allclose([projection.min(), projection.max()], [0, length * .5], atol=1e-6)
modifier = arrow.modifiers[0]
sockets = {s.name: s.identifier for s in modifier.node_group.interface.items_tree
           if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
modifier[sockets['Angstrom per Debye']] = 1.0
np.testing.assert_allclose((vertices(arrow) @ (vector / length)).max(), length, atol=1e-6)
modifier[sockets['Vector (Debye)']] = (0., 0., 0.)
assert len(vertices(arrow)) == 0
modifier[sockets['Vector (Debye)']] = tuple(vector)
script = ROOT / 'tools/probe_vibration.py'
exec(compile(script.read_text(encoding='utf-8'), str(script), 'exec'), {'__file__': str(script)})
report = {'status': 'Passed', 'cache_rebuild_arrays_exact': 'Passed', 'cache_rebuild_geometry_exact': 'Passed',
          'relocate_by_manifest_identity': 'Passed', 'dipole_direction_length_zero': 'Passed',
          'atomic_charge_operator': 'Passed', 'vibration_ir': 'Passed'}
(ROOT / 'outputs/acceptance/recovery.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
