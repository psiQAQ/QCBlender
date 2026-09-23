"""Check hydrogen visibility through the installed Blender operator and saved scene."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import qcblender
from qcblender.blender.graph import view_modifier
from qcblender.blender.layers import copy_layer
from qcblender.blender.views import atom_view
from qcblender.data import Dataset, save_dataset, load_dataset

OUT = ROOT / 'outputs' / 'atom-visibility'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()


def vertex_count(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return len(mesh.vertices)
    finally:
        evaluated.to_mesh_clear()


if '--reopen' in sys.argv:
    source = next(o for o in bpy.data.objects if o.get('qc_hydrogen_visibility') == 'KEEP')
    assert source['qc_hydrogen_keep'] == '2'
    assert vertex_count(source) > 0
    assert load_dataset(Path(source['qc_dataset'])).arrays['atomic_numbers'].tolist() == [6, 1, 1, 8]
    (OUT / 'reopened.json').write_text(json.dumps({'status': 'Passed'}), encoding='utf-8')
else:
    atoms = [6, 1, 1, 8]
    data = Dataset({'source': {'filename': 'analytic', 'sha256': hashlib.sha256(b'analytic').hexdigest()},
                    'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': []},
                   {'atomic_numbers': np.asarray(atoms, dtype=np.int32),
                    'positions': np.asarray([[0, 0, 0], [1, 0, 0], [-1, 0, 0], [0, 1.5, 0]], dtype=float),
                    'bonds': np.asarray([[0, 1], [0, 2], [0, 3]], dtype=np.int32)})
    directory = OUT / 'atoms.qcdata'
    save_dataset(data, directory)
    original_manifest = hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest()
    obj = atom_view(directory)
    original = vertex_count(obj)
    assert bpy.ops.qcblender.hydrogen_visibility(mode='HIDE') == {'FINISHED'}
    hidden = vertex_count(obj)
    assert 0 < hidden < original
    assert bpy.ops.qcblender.hydrogen_visibility(mode='KEEP', keep='2') == {'FINISHED'}
    kept = vertex_count(obj)
    assert hidden < kept < original
    try:
        bpy.ops.qcblender.hydrogen_visibility(mode='KEEP', keep='1')
    except RuntimeError as error:
        assert 'not hydrogen' in str(error)
    else:
        raise AssertionError('Non-hydrogen atom number was accepted')
    assert vertex_count(obj) == kept
    duplicate = copy_layer(obj, bpy.context.collection)
    assert vertex_count(duplicate) == kept
    bpy.context.view_layer.objects.active = duplicate
    assert bpy.ops.qcblender.hydrogen_visibility(mode='RESTORE') == {'FINISHED'}
    assert vertex_count(duplicate) == original
    assert vertex_count(obj) == kept
    assert load_dataset(directory).arrays['atomic_numbers'].tolist() == atoms
    assert hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest() == original_manifest
    assert view_modifier(obj).node_group != view_modifier(duplicate).node_group
    oxygen = Dataset({'source': {'filename': 'analytic-o2', 'sha256': hashlib.sha256(b'analytic-o2').hexdigest()},
                      'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': []},
                     {'atomic_numbers': np.array([8, 8], dtype=np.int32),
                      'positions': np.array([[0, 0, 0], [1.2, 0, 0]], dtype=float),
                      'bonds': np.array([[0, 1]], dtype=np.int32)})
    oxygen_dir = OUT / 'oxygen.qcdata'
    save_dataset(oxygen, oxygen_dir)
    oxygen_view = atom_view(oxygen_dir)
    oxygen_count = vertex_count(oxygen_view)
    assert bpy.ops.qcblender.hydrogen_visibility(mode='HIDE') == {'FINISHED'}
    assert vertex_count(oxygen_view) == oxygen_count
    assert bpy.ops.qcblender.hydrogen_visibility(mode='RESTORE') == {'FINISHED'}
    assert vertex_count(oxygen_view) == oxygen_count
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'visibility.blend'))
    (OUT / 'report.json').write_text(json.dumps({'status': 'Passed', 'original': original,
                                                  'hidden': hidden, 'kept': kept}), encoding='utf-8')
