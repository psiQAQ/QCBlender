"""Check paired Cube parsing, Blender views, and portable reopen with real C07 paired Cube sources."""
import hashlib
import csv
import os
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs' / 'science')]
import qcblender
from qcblender.data import load_dataset, save_dataset
from qcblender.external_fields import pair_cubes
from qcblender.data_export import export_dataset
from tools.local_inputs import input_path
import numpy as np
from qcblender.worker import write_volume
from qcblender.blender.views import atom_view, field_view
from qcblender.blender.scalars import add_mapping
from qcblender.blender.external_fields import paired_record
from qcblender.blender.project import save_project

OUT = ROOT / 'outputs' / 'paired-fields'
OUT.mkdir(parents=True, exist_ok=True)
qcblender.register()

if '--reopen' in sys.argv:
    geometry = next(o for o in bpy.data.objects if o.get('qc_analysis'))
    data = load_dataset(bpy.path.abspath(geometry['qc_dataset']))
    assert len(data.metadata['fields']) == 2
    assert data.metadata['analysis']['kind'] == 'IGMH'
    record = next(o for o in bpy.data.objects if o.get('qc_analysis_role') == 'paired')
    assert record.get('qc_data_record') and len(record.data.vertices) == 0
    exported = export_dataset(bpy.path.abspath(record['qc_dataset']), OUT / 'csv', 'paired')
    fields = data.metadata['fields']
    valid = data.arrays[fields[0]['valid_mask']] & data.arrays[fields[1]['valid_mask']]
    assert exported['files'][0]['row_count'] == int(valid.sum())
    assert geometry.qc_settings.volume is not None
    print('paired fields cold reopen Passed')
else:
    reference_root = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
    folder = input_path('sop/c07-c09-research/phenol-2026-09-27/igmh', reference_root)
    source, color = folder / 'dg_inter.cub', folder / 'sl2r.cub'
    data = pair_cubes(source, color, 'IGMH', 'electron/bohr^4', 'electron/bohr^3')
    assert data.metadata['analysis']['color_source']['sha256'] == hashlib.sha256(color.read_bytes()).hexdigest()
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
        pair_cubes(source, bad_grid, 'IGMH', 'electron/bohr^4', 'electron/bohr^3')
    except ValueError as error:
        assert 'grids differ' in str(error)
    else:
        raise AssertionError('Mismatched Cube grids accepted')
    directory = OUT / 'c07-pair.qcdata'
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
    record = paired_record(directory, data, parent)
    assert record.get('qc_data_record') and record.get('qc_analysis_role') == 'paired'
    assert len(record.data.vertices) == 0 and not record.modifiers
    fields = data.metadata['fields']
    valid = data.arrays[fields[0]['valid_mask']].ravel() & data.arrays[fields[1]['valid_mask']].ravel()
    expected = np.flatnonzero(valid)
    exported = export_dataset(directory, OUT / 'csv', 'paired')
    assert exported['files'][0]['row_count'] == len(expected)
    with (Path(exported['directory']) / 'paired_voxels.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        for index in expected:
            row = next(reader)
            assert int(row['flat_index_0based']) == index
            assert float(row['x_value']) == data.arrays[fields[1]['array']].ravel()[index]
            assert float(row['y_value']) == data.arrays[fields[0]['array']].ravel()[index]
        assert next(reader, None) is None
    assert geometry.get('qc_color_source')
    save_project(OUT / 'paired.blend')
    print('paired fields parsing and Blender save Passed; scientific semantics Not Run')
