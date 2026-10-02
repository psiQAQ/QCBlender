"""Export real normal-mode frames with source labels using Blender's native renderer."""
import hashlib
import importlib
import json
from pathlib import Path
import time

import bpy
from mathutils import Vector
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
OUT = ROOT / 'outputs/animation-acceptance-v2'
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
jobs = importlib.import_module(MODULE + '.blender.jobs')
views = importlib.import_module(MODULE + '.blender.views')
project = importlib.import_module(MODULE + '.blender.project')
storage = importlib.import_module(MODULE + '.data')
job = jobs.Job('import', source=str(input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)), job_index=1)
deadline = time.monotonic() + 120
while (result := job.poll()) is None:
    if time.monotonic() > deadline:
        job.cancel()
        raise TimeoutError(str(job.directory))
    time.sleep(.1)
assert result['status'] == 'succeeded', result
for obj in bpy.data.objects:
    obj.hide_render = True
atoms = views.atom_view(job.directory / 'dataset')
# This Gaussian orientation puts water in YZ; face its molecular plane toward the camera.
atoms.rotation_euler[2] = np.pi / 2
atoms.qc_settings.active_mode = 1
modifier = atoms.modifiers[0]
inputs = {s.name: s.identifier for s in modifier.node_group.interface.items_tree
          if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
modifier[inputs['Animate']] = True
modifier[inputs['Show Displacement Vectors']] = True
modifier[inputs['Amplitude (angstrom)']] = .35
scene = bpy.context.scene
scene.render.fps, scene.render.fps_base = 24, 1
scene.frame_start, scene.frame_end, scene.frame_step = 0, 18, 6
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1100, 450, 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(OUT / 'mode-')
scene.world.color = (.25, .25, .25)
camera = bpy.data.objects.new('QC vibration camera', bpy.data.cameras.new('QC vibration camera'))
scene.collection.objects.link(camera)
camera.location = (3.8, -18, 1)
camera.rotation_euler = (Vector((3.8, 0, .6)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type, camera.data.ortho_scale = 'ORTHO', 12
scene.camera = camera
for location in ((-2, -5, 6), (7, -3, 7)):
    light = bpy.data.objects.new('QC vibration light', bpy.data.lights.new('QC vibration light', 'AREA'))
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector((3, 0, 0)) - light.location).to_track_quat('-Z', 'Y').to_euler()
    light.data.energy, light.data.size = 1000, 5
text = bpy.data.curves.new('QC mode source caption', 'FONT')
text.body = (f"Water | mode 2 | {atoms['qc_mode_frequency_cm-1']:.4f} cm^-1\n"
             'Display amplitude 0.35 angstrom | playback 1 Hz (not physical time)')
text.size = .17
label = bpy.data.objects.new('QC mode source caption', text)
scene.collection.objects.link(label)
label.location, label.rotation_euler = (-1, 0, -1.5), (np.pi / 2, 0, 0)
data = storage.load_dataset(job.directory / 'dataset')
before = {name: array.copy() for name, array in data.arrays.items()}
project.save_project(OUT / 'water-mode.blend')
bpy.ops.render.render(animation=True)
frames = sorted(OUT.glob('mode-*.png'))
assert len(frames) == 4
assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in frames}) >= 3
after = storage.load_dataset(bpy.path.abspath(atoms['qc_dataset']))
for name in before:
    np.testing.assert_array_equal(before[name], after.arrays[name])
report = {'status': 'Passed', 'native_animation_export': 'Passed', 'scientific_arrays_unchanged': 'Passed',
          'frames': [p.name for p in frames], 'mode': 2, 'frequency_cm-1': atoms['qc_mode_frequency_cm-1'],
          'source_sha256': atoms['qc_source_sha256'], 'display_amplitude_angstrom': .35,
          'playback_hz': 1, 'physical_time': False}
(OUT / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
