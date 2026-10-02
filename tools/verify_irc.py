"""Check real P04 ordered configurations, Mayer records and exported CSV in Blender."""
import csv
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs/science')]
import qcblender
from qcblender.data import load_dataset
from qcblender.data_export import export_dataset
from qcblender.irc import import_irc, import_irc_mayer
from qcblender.blender.project import save_project

OUT = ROOT / 'outputs/irc-acceptance'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()
SOURCE = ROOT / 'tests/data/tutorial/P04'


def activate(obj):
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def check_mayer_view(root, expected, step):
    tables = [child for child in root.children if child.get('qc_analysis_role') == 'irc_mayer']
    assert len(tables) == 1
    assert not any(child.get('qc_analysis_role') in ('irc_energy', 'irc_cursor', 'irc_mayer_curve', 'irc_mayer_cursor') for child in root.children)
    table = tables[0]
    assert table.get('qc_data_record') and table.type == 'MESH' and len(table.data.vertices) == 0
    data = load_dataset(bpy.path.abspath(table['qc_dataset']))
    for name in data.arrays:
        np.testing.assert_array_equal(data.arrays[name], expected.arrays[name])
    assert root['qc_irc_step'] == step and json.loads(root['qc_irc_record'])['step'] == step
    activate(table)
    assert bpy.ops.qcblender.select_irc_mayer_pair() == {'FINISHED'}
    assert table['qc_mayer_pair_index'] == 0
    np.testing.assert_array_equal(list(table['qc_mayer_display_values']), expected.arrays['mayer_orders'][:, 0])
    report = export_dataset(bpy.path.abspath(table['qc_dataset']), OUT / 'csv', 'Mayer')
    path = Path(report['directory']) / 'mayer.csv'
    with path.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == expected.arrays['mayer_orders'].size
    assert report['files'][0]['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    pairs = expected.arrays['mayer_pairs'].tolist()
    for row in rows:
        pair = [int(row['atom_a_1based']), int(row['atom_b_1based'])]
        assert float(row['mayer_order']) == expected.arrays['mayer_orders'][int(row['step']) - 1, pairs.index(pair)]
    return table


expected = import_irc(SOURCE / 'steps.csv')
expected_mayer = import_irc_mayer(expected, SOURCE / 'mayer-pyscf.csv')
if '--reopen' in sys.argv:
    root = next(obj for obj in bpy.data.objects if obj.get('qc_irc'))
else:
    assert bpy.ops.qcblender.import_irc_path(manifest_path=str(SOURCE / 'steps.csv')) == {'FINISHED'}
    root = next(obj for obj in bpy.data.objects if obj.get('qc_irc'))
    activate(root)
    assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
    with bpy.context.temp_override(object=root, active_object=root):
        assert bpy.ops.qcblender.import_irc_mayer(manifest_path=str(SOURCE / 'mayer-pyscf.csv')) == {'FINISHED'}
    table = bpy.context.view_layer.objects.active
    assert table.select_get() and not root.select_get()

data = load_dataset(bpy.path.abspath(root['qc_dataset']))
assert root['qc_irc_step'] == 2
for name in expected.arrays:
    np.testing.assert_array_equal(data.arrays[name], expected.arrays[name])
np.testing.assert_allclose([v.co[:] for v in root.data.vertices], expected.arrays['irc_positions'][1], atol=1e-6)
check_mayer_view(root, expected_mayer, 2)
exported = export_dataset(bpy.path.abspath(root['qc_dataset']), OUT / 'csv', 'IRC')
with (Path(exported['directory']) / 'irc_steps.csv').open(encoding='utf-8', newline='') as stream:
    rows = list(csv.DictReader(stream))
np.testing.assert_array_equal([float(row['energy_hartree']) for row in rows], expected.arrays['irc_energies'])
if '--reopen' not in sys.argv:
    save_project(OUT / 'irc.blend')
print('Real P04 IRC configurations, Mayer records and CSV Passed')
