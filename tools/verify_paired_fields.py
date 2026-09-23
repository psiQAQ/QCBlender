"""Check paired Cube parsing, Blender views, and portable reopen with a numeric Cube fixture."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs' / 'science')]
import qcblender
from qcblender.data import load_dataset, save_dataset
from qcblender.external_fields import pair_cubes, scatter_points
from qcblender.worker import write_volume
from qcblender.blender.views import atom_view, field_view
from qcblender.blender.scalars import add_mapping
from qcblender.blender.external_fields import scatter_view
from qcblender.blender.project import save_project

OUT = ROOT / 'outputs' / 'paired-fields'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()

if '--reopen' in sys.argv:
    geometry = next(o for o in bpy.data.objects if o.get('qc_analysis'))
    data = load_dataset(bpy.path.abspath(geometry['qc_dataset']))
    assert len(data.metadata['fields']) == 2
    assert data.metadata['analysis']['kind'] == 'IGMH'
    assert any(o.get('qc_view_kind') == 'scatter' for o in bpy.data.objects)
    assert geometry.qc_settings.volume is not None
    print('paired fields cold reopen Passed')
else:
    source = ROOT / 'outputs' / 'vesta-comparison' / 'ch4-alpha-mo8.cube'
    color = OUT / 'numeric-color.cube'
    shutil.copy2(source, color)
    lines = color.read_text(encoding='ascii').splitlines(keepends=True)
    first_value = lines[12].split()
    first_value[0] = str(-float(first_value[0]))
    lines[12] = ' '.join(first_value) + '\n'
    color.write_text(''.join(lines), encoding='ascii')
    data = pair_cubes(source, color, 'IGMH', 'dimensionless', 'electron/bohr^3')
    assert pair_cubes(source, color, 'IRI', 'dimensionless', 'electron/bohr^3').metadata['analysis']['kind'] == 'IRI'
    assert len(scatter_points(data)) > 100
    assert data.metadata['analysis']['color_source']['sha256'] == hashlib.sha256(color.read_bytes()).hexdigest()
    try:
        pair_cubes(source, ROOT / 'outputs' / 'visual-acceptance-v2' / 'unknown.cube',
                   'IGMH', 'dimensionless', 'electron/bohr^3')
    except ValueError as error:
        assert 'Atom identities/order' in str(error)
    else:
        raise AssertionError('Mismatched atom identities accepted')
    try:
        pair_cubes(source, color, 'IGMH', 'unknown', 'electron/bohr^3')
    except ValueError as error:
        assert 'unit' in str(error)
    else:
        raise AssertionError('Unknown field unit accepted')
    bad_grid = OUT / 'bad-grid.cube'
    lines = color.read_text(encoding='ascii').splitlines(keepends=True)
    header = lines[2].split()
    header[1] = str(float(header[1]) + .1)
    lines[2] = ' '.join(header) + '\n'
    bad_grid.write_text(''.join(lines), encoding='ascii')
    try:
        pair_cubes(source, bad_grid, 'IGMH', 'dimensionless', 'electron/bohr^3')
    except ValueError as error:
        assert 'grids differ' in str(error)
    else:
        raise AssertionError('Mismatched Cube grids accepted')
    directory = OUT / 'numeric-pair.qcdata'
    directory.mkdir(exist_ok=True)
    for index, field in enumerate(data.metadata['fields']):
        field['vdb'] = f'field-{index}.vdb'
        write_volume(data, directory / field['vdb'], index)
        field['vdb_sha256'] = hashlib.sha256((directory / field['vdb']).read_bytes()).hexdigest()
    save_dataset(data, directory)
    parent = atom_view(directory)
    geometry = field_view(directory, parent, 0)
    color = field_view(directory, parent, 1)
    geometry['qc_analysis'] = json.dumps(data.metadata['analysis'])
    add_mapping(geometry, color, -.05, .05)
    scatter = scatter_view(directory, data, parent)
    assert len(scatter.data.vertices) > 100
    assert geometry.get('qc_color_source')
    save_project(OUT / 'paired.blend')
    print('paired fields parsing and Blender save Passed; scientific semantics Not Run')
