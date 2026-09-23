"""Real Gaussian NBO record and Blender persistence check."""
import hashlib
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs' / 'science')]
import qcblender
from qcblender.data import load_dataset, save_dataset
from qcblender.gaussian_log import read_log
from qcblender.nbo import associated_nbo, parse_nbo
from qcblender.blender.project import save_project
from qcblender.blender.views import atom_view, bind

OUT = ROOT / 'outputs' / 'nbo-acceptance'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'outputs' / 'log-examples' / 'water_neutral_nbo_opt_freq.out'
qcblender.register()

if '--reopen' in sys.argv:
    obj = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'nbo')
    data = load_dataset(bpy.path.abspath(obj['qc_dataset']))
    assert len(data.metadata['analysis']['orbitals']) == 7
    assert len(data.metadata['analysis']['interactions']) == 2
    assert data.metadata['analysis']['canonical_mo_mapping'] == 'none'
    print('NBO cold reopen Passed')
else:
    assert len(parse_nbo(SOURCE, 0, 0)['orbitals']) == 7
    assert len(parse_nbo(SOURCE, 0, 1)['orbitals']) == 7
    assert len(parse_nbo(SOURCE, 1, 0)['interactions']) == 2
    try:
        parse_nbo(SOURCE, 1, 1)
    except ValueError as error:
        assert 'NBO block' in str(error)
    else:
        raise AssertionError('Missing NBO block accepted')
    truncated = OUT / 'truncated-nbo.out'
    source_text = SOURCE.read_text(encoding='utf-8', errors='replace')
    truncated.write_text(source_text[:source_text.rfind('Total unit')], encoding='utf-8')
    try:
        parse_nbo(truncated, 1, 0)
    except ValueError as error:
        assert 'NBO summary' in str(error)
    else:
        raise AssertionError('Truncated NBO summary accepted')
    reference = read_log(SOURCE, 1)
    reference_dir = OUT / 'reference.qcdata'
    save_dataset(reference, reference_dir)
    try:
        associated_nbo(SOURCE, 0, 0, reference_dir)
    except ValueError as error:
        assert 'multiple geometries' in str(error)
    else:
        raise AssertionError('Ambiguous optimization NBO association accepted')
    data = associated_nbo(SOURCE, 1, 0, reference_dir)
    assert data.metadata['analysis']['source']['sha256'] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert data.metadata['analysis']['orbitals'][0]['occupancy'] > 1
    assert data.metadata['analysis']['interactions'][0]['e2_kcal_mol'] > 0
    directory = OUT / 'nbo.qcdata'
    save_dataset(data, directory)
    parent = atom_view(reference_dir)
    mesh = bpy.data.meshes.new('QC NBO records')
    obj = bpy.data.objects.new('QC NBO', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'nbo'
    obj['qc_nbo_index'] = 1
    obj['qc_e2_index'] = 1
    save_project(OUT / 'nbo.blend')
    print('Real Gaussian NBO parse, association and save Passed')
