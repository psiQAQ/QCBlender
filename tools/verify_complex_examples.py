"""Cold-open relocated showcases, verify portable assets, and render actual contents."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/complex-examples'
parser = argparse.ArgumentParser()
parser.add_argument('case', choices=('orbitals', 'vibration', 'polar', 'interaction'))
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source = OUT / args.case
target = OUT / 'portable' / args.case
target.mkdir(parents=True, exist_ok=True)
shutil.copy2(source / (args.case + '.blend'), target)
shutil.copytree(source / (args.case + '.qcdata'), target / (args.case + '.qcdata'), dirs_exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
bpy.ops.wm.open_mainfile(filepath=str(target / (args.case + '.blend')))
storage = importlib.import_module(MODULE + '.data')
report = json.loads((source / 'report.json').read_text(encoding='utf-8'))
verified, hashes = set(), {}
for obj in bpy.context.scene.objects:
    if 'qc_dataset' in obj:
        directory = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
        assert directory.is_relative_to(target.resolve()), directory
        data = storage.load_dataset(directory)
        actual = hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest()
        assert actual == obj['qc_dataset_sha256']
        verified.add(str(directory.relative_to(target)))
        for path in directory.rglob('*'):
            if path.is_file():
                hashes[str(path.relative_to(target))] = hashlib.sha256(path.read_bytes()).hexdigest()
for volume in bpy.data.volumes:
    if volume.filepath:
        assert Path(bpy.path.abspath(volume.filepath)).resolve().is_relative_to(target.resolve())
        assert volume.grids.load()
for entry in report['layers']:
    obj = bpy.data.objects[entry['name']]
    if 'vertices' in entry:
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            assert len(mesh.vertices) == entry['vertices'], (obj.name, len(mesh.vertices), entry['vertices'])
        finally:
            evaluated.to_mesh_clear()
if args.case == 'vibration':
    atoms = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'atoms')
    assert len(atoms.qc_settings.modes) == 54
    assert atoms.qc_settings.active_mode == report['mode']-1
    data = storage.load_dataset(bpy.path.abspath(atoms['qc_dataset']))
    np.testing.assert_allclose([v.vector[:] for v in atoms.data.attributes['qc_mode_displacement'].data],
                               data.arrays['mode_display_displacements'][report['mode']-1], atol=1e-7)
    movie = source / 'vibration-ir.mp4'
    assert movie.exists() and movie.stat().st_size > 10000
    editor = bpy.context.scene.sequence_editor_create()
    strip = editor.strips.new_movie('Verify encoded video', str(movie), channel=1, frame_start=0)
    assert strip.frame_duration == 48, strip.frame_duration
    bpy.context.scene.sequence_editor_clear()
bpy.context.scene.render.filepath = str(target / 'reopened.png')
bpy.ops.render.render(write_still=True)
for relative, digest in hashes.items():
    assert hashlib.sha256((target / relative).read_bytes()).hexdigest() == digest
result = {'status': 'Passed', 'case': args.case, 'relocated_cold_open': 'Passed',
          'geometry_counts': 'Passed', 'scientific_and_cache_files_unchanged': 'Passed',
          'render': str((target / 'reopened.png').relative_to(OUT)), 'datasets': sorted(verified),
          'human_acceptance': 'Not Run'}
if args.case == 'vibration':
    result['video_48_frames_decoded'] = 'Passed'
(source / 'reopen.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
