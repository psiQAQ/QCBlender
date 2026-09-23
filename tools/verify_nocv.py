"""Check explicit NOCV pair/Cube association and native signed field persistence."""
import hashlib
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs' / 'science')]
import qcblender
from qcblender.analysis_data import import_ets
from qcblender.cube import read_cube
from qcblender.data import load_dataset, save_dataset
from qcblender.nocv import import_nocv
from qcblender.worker import write_volume
from qcblender.blender.project import save_project
from qcblender.blender.views import atom_view, field_view

OUT = ROOT / 'outputs' / 'nocv-acceptance'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()

if '--reopen' in sys.argv:
    field = next(obj for obj in bpy.data.objects if obj.get('qc_analysis_role') == 'nocv_field')
    data = load_dataset(bpy.path.abspath(field['qc_dataset']))
    assert data.metadata['analysis']['pair']['pair'] == 1
    assert data.metadata['fields'][0]['quantity'] == 'nocv_deformation_density'
    assert field.qc_settings.volume is not None
    print('NOCV signed field cold reopen Passed; real NOCV fixture Not Run')
else:
    cube = ROOT / 'outputs' / 'vesta-comparison' / 'ch4-alpha-mo8.cube'
    reference = read_cube(cube)
    table_file = OUT / 'synthetic-ets.txt'
    table_file.write_text('Note: All energies are given in kcal/mol\n'
        'Pair Energy | Orbital Eigenvalue Energy | Orbital Eigenvalue Energy\n'
        '-----\n1 -2.50 6 0.12000 -3.10 7 -0.12000 0.60\n', encoding='utf-8')
    table = import_ets(reference, table_file, 'kcal/mol')
    table_dir = OUT / 'table.qcdata'
    save_dataset(table, table_dir)
    try:
        import_nocv(cube, table, 2, 'Total', 'electron/bohr^3')
    except ValueError as error:
        assert 'pair and spin' in str(error)
    else:
        raise AssertionError('Wrong ETS pair accepted')
    data = import_nocv(cube, table, 1, 'Total', 'electron/bohr^3')
    assert data.metadata['analysis']['cube_source']['sha256'] == hashlib.sha256(cube.read_bytes()).hexdigest()
    assert data.metadata['analysis']['table_source'] == table.metadata['source']['sha256']
    directory = OUT / 'field.qcdata'
    directory.mkdir(exist_ok=True)
    data.metadata['fields'][0]['vdb'] = 'field.vdb'
    write_volume(data, directory / 'field.vdb')
    data.metadata['fields'][0]['vdb_sha256'] = hashlib.sha256((directory / 'field.vdb').read_bytes()).hexdigest()
    save_dataset(data, directory)
    root = atom_view(table_dir)
    field = field_view(directory, root)
    field['qc_analysis_role'] = 'nocv_field'
    save_project(OUT / 'nocv.blend')
    print('Numeric Cube NOCV role/Blender save Passed; real NOCV fixture Not Run')
