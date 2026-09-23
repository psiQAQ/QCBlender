"""Parser and Blender persistence checks for external text analysis roles."""
from pathlib import Path
import sys
from unittest.mock import patch

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs' / 'science')]
import qcblender
from qcblender.analysis_data import import_aim, import_esp, import_ets
from qcblender.data import load_dataset, save_dataset
from qcblender.external_results import aim_properties, esp_area, esp_extrema, ets_nocv_pairs, mayer_orders
from qcblender.gaussian_log import read_log
from qcblender.blender.external_results import area_view, path_view, point_view, store_analysis, table_view
from qcblender.blender.project import save_project
from qcblender.blender.views import atom_view

OUT = ROOT / 'outputs' / 'external-results'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()


def pdb_line(serial, name, resid, xyz, value=0):
    chars = list(' ' * 80)
    chars[:6] = list('HETATM')
    chars[6:11] = list(f'{serial:5d}')
    chars[12:16] = list(f'{name:<4s}')
    chars[22:26] = list(f'{resid:4d}')
    for start, number in zip((30, 38, 46), xyz):
        chars[start:start+8] = list(f'{number:8.3f}')
    chars[60:66] = list(f'{value:6.2f}')
    return ''.join(chars) + '\n'


if '--reopen' in sys.argv:
    objects = [obj for obj in bpy.data.objects if obj.get('qc_analysis_role')]
    assert {'esp_area', 'aim_paths', 'ets_nocv'} <= {obj['qc_analysis_role'] for obj in objects}
    for obj in objects:
        load_dataset(bpy.path.abspath(obj['qc_dataset']))
    print('ESP/AIM/ETS text result cold reopen Passed; scientific fixtures Not Run')
else:
    with patch.object(bpy.utils, 'user_resource', return_value=''):
        try:
            store_analysis(None)
        except OSError:
            pass
        else:
            raise AssertionError('Unavailable Blender data directory accepted')
    source = ROOT / 'outputs' / 'log-examples' / 'water_neutral_nbo_opt_freq.out'
    reference = read_log(source, 1)
    reference_dir = OUT / 'reference.qcdata'
    save_dataset(reference, reference_dir)
    parent = atom_view(reference_dir)
    positions = reference.arrays['positions'].tolist()
    extrema = OUT / 'synthetic-extrema.pdb'
    extrema.write_text(pdb_line(1, 'C', 1, [0.0, 1.5, 0.2], 8.2) +
                       pdb_line(2, 'O', 1, [0.0, -1.5, 0.2], -6.1), encoding='utf-8')
    area = OUT / 'synthetic-area.txt'
    area.write_text('Center Area Percentage\n-2.0 1.5 30.0\n2.0 3.5 70.0\n', encoding='utf-8')
    esp = import_esp(reference, extrema, area, 'density 0.001 e/bohr^3', 'kcal/mol', 'kcal/mol', 'angstrom^2')
    assert len(esp.metadata['analysis']['extrema']) == 2
    esp_dir = OUT / 'esp.qcdata'
    save_dataset(esp, esp_dir)
    point_view(esp_dir, esp, parent, [esp.metadata['analysis']['extrema'][0]],
               'QC ESP maximum', (.9, .5, .1, 1), 'esp_maximum')
    area_view(esp_dir, esp, parent)
    bad = OUT / 'bad-extrema.pdb'
    bad.write_text(pdb_line(1, 'C', 1, [0, 0, 0], 1)[:-20], encoding='utf-8')
    try:
        esp_extrema(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Truncated extrema accepted')
    bad_area = OUT / 'bad-area.txt'
    bad_area.write_text('Center Area Percentage\n0.0 -1.0 20.0\n', encoding='utf-8')
    try:
        esp_area(bad_area)
    except ValueError:
        pass
    else:
        raise AssertionError('Negative surface area accepted')
    cps = OUT / 'synthetic-cps.pdb'
    cps.write_text(pdb_line(1, 'C', 1, positions[0]) + pdb_line(2, 'N', 1, [0, .4, 0]), encoding='utf-8')
    paths = OUT / 'synthetic-paths.pdb'
    paths.write_text(pdb_line(1, 'X', 1, positions[0]) + pdb_line(2, 'X', 1, positions[1]), encoding='utf-8')
    props = OUT / 'synthetic-cpprop.txt'
    props.write_text('Critical point 2 :\nCP type: (3,-1)\nrho: 0.2\n', encoding='utf-8')
    aim = import_aim(reference, cps, paths, props)
    orphan = OUT / 'orphan-cpprop.txt'
    orphan.write_text('Critical point 9 :\nrho: 0.2\n', encoding='utf-8')
    try:
        aim_properties(orphan, {1, 2})
    except ValueError:
        pass
    else:
        raise AssertionError('Orphan AIM property accepted')
    aim_dir = OUT / 'aim.qcdata'
    save_dataset(aim, aim_dir)
    point_view(aim_dir, aim, parent, [aim.metadata['analysis']['critical_points'][1]],
               'QC AIM CP N', (.1, .8, .2, 1), 'aim_N')
    path_view(aim_dir, aim, parent)
    ets_file = OUT / 'synthetic-ets.txt'
    ets_file.write_text('Note: All energies are given in kcal/mol\n'
                        'Pair Energy | Orbital Eigenvalue Energy | Orbital Eigenvalue Energy\n'
                        '-----\n1 -2.50 6 0.12000 -3.10 7 -0.12000 0.60\n', encoding='utf-8')
    ets = import_ets(reference, ets_file, 'kcal/mol')
    bad_ets = OUT / 'bad-ets.txt'
    bad_ets.write_text(ets_file.read_text(encoding='utf-8') +
                       '2 -1.50 8 0.12000 -2.10 9\n', encoding='utf-8')
    try:
        ets_nocv_pairs(bad_ets, 'kcal/mol')
    except ValueError:
        pass
    else:
        raise AssertionError('Truncated ETS-NOCV row accepted')
    ets_dir = OUT / 'ets.qcdata'
    save_dataset(ets, ets_dir)
    table_view(ets_dir, ets, parent, 'QC ETS-NOCV pairs', 'ets_nocv')
    mayer_file = OUT / 'synthetic-mayer.txt'
    mayer_file.write_text('Bond orders with absolute value\n# 1: 1(O) 2(H) 0.95\n'
                          'Total valences and free valences\n', encoding='utf-8')
    assert mayer_orders(mayer_file, 3)[0]['order'] == .95
    bpy.context.view_layer.objects.active = parent
    parent.select_set(True)
    parent['qc_field'] = '{"quantity":"electrostatic_potential"}'
    assert bpy.ops.qcblender.import_esp_analysis(extrema_path=str(extrema), area_path=str(area),
                                                  surface_definition='density 0.001 e/bohr^3',
                                                  extrema_unit='kcal/mol', center_unit='kcal/mol',
                                                  area_unit='angstrom^2') == {'FINISHED'}
    assert bpy.ops.qcblender.import_aim_analysis(cps_path=str(cps), paths_path=str(paths),
                                                  properties_path=str(props)) == {'FINISHED'}
    assert bpy.ops.qcblender.import_ets_nocv(output_path=str(ets_file),
                                             energy_unit='kcal/mol') == {'FINISHED'}
    roles = {obj.get('qc_analysis_role') for obj in bpy.data.objects}
    assert {'esp_maximum', 'esp_minimum', 'esp_area', 'aim_paths', 'ets_nocv'} <= roles
    save_project(OUT / 'results.blend')
    print('Synthetic format/Blender persistence checks Passed; scientific fixtures Not Run')
