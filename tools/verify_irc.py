"""Check ordered FCHK and Mayer overlays in Blender with derived format fixtures."""
from pathlib import Path
import re
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs' / 'science')]
import qcblender
from qcblender.data import load_dataset
from qcblender.irc import import_irc, import_irc_mayer
from qcblender.blender.project import save_project

OUT = ROOT / 'outputs' / 'irc-acceptance'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()

if '--reopen' in sys.argv:
    root = next(obj for obj in bpy.data.objects if obj.get('qc_irc'))
    data = load_dataset(bpy.path.abspath(root['qc_dataset']))
    assert root['qc_irc_step'] == 2
    assert len(data.arrays['irc_energies']) == 2
    assert any(child.get('qc_analysis_role') == 'irc_mayer_curve' for child in root.children)
    print('IRC path and Mayer cold reopen Passed; real IRC fixture Not Run')
else:
    original = (ROOT / 'tests' / 'data' / 'iodata' / 'water_sto3g_hf_g03.fchk').read_text(encoding='ascii')
    first = OUT / 'step1.fchk'
    second = OUT / 'step2.fchk'
    first.write_text(original, encoding='ascii')
    changed = original.replace('-7.495929232844363E+01', '-7.495829232844363E+01')
    lines = changed.splitlines(keepends=True)
    index = next(i for i, line in enumerate(lines) if line.startswith('Current cartesian coordinates'))
    lines[index + 1] = re.sub(r'[-+]?\d+\.\d+E[+-]\d+', '1.00000000E-01', lines[index + 1], count=1)
    second.write_text(''.join(lines), encoding='ascii')
    manifest = OUT / 'steps.csv'
    manifest.write_text('step,fchk\n1,step1.fchk\n2,step2.fchk\n', encoding='utf-8')
    data = import_irc(manifest)
    assert data.arrays['irc_positions'].shape == (2, 3, 3)
    assert data.arrays['irc_energies'][0] != data.arrays['irc_energies'][1]
    bad = OUT / 'bad-order.csv'
    bad.write_text('step,fchk\n1,step1.fchk\n3,step2.fchk\n', encoding='utf-8')
    try:
        import_irc(bad)
    except ValueError as error:
        assert 'contiguous' in str(error)
    else:
        raise AssertionError('Gapped IRC path accepted')
    for step, value in [(1, .95), (2, .85)]:
        (OUT / f'mayer{step}.txt').write_text('Bond orders with absolute value\n'
            f'# 1: 1(O) 2(H) {value:.2f}\n# 2: 1(O) 3(H) 0.90\n'
            'Total valences and free valences\n', encoding='utf-8')
    mayer_manifest = OUT / 'mayer.csv'
    mayer_manifest.write_text('step,mayer_output\n1,mayer1.txt\n2,mayer2.txt\n', encoding='utf-8')
    assert import_irc_mayer(data, mayer_manifest).arrays['mayer_orders'].shape == (2, 2)
    assert bpy.ops.qcblender.import_irc_path(manifest_path=str(manifest)) == {'FINISHED'}
    root = next(obj for obj in bpy.data.objects if obj.get('qc_irc'))
    bpy.context.view_layer.objects.active = root
    assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
    assert root['qc_irc_step'] == 2
    assert bpy.ops.qcblender.import_irc_mayer(manifest_path=str(mayer_manifest)) == {'FINISHED'}
    save_project(OUT / 'irc.blend')
    print('IRC parser, Blender step and Mayer save Passed; real IRC fixture Not Run')
