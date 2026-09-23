"""Bind an explicitly chosen signed Cube to one ETS-NOCV table pair."""
import numpy as np

from .association import compare_sources
from .cube import read_cube


def import_nocv(cube_path, table, pair_number, spin, unit):
    if table.metadata.get('analysis', {}).get('kind') != 'ETS-NOCV':
        raise ValueError('Select an ETS-NOCV pair table')
    matches = [row for row in table.metadata['analysis']['pairs']
               if row['pair'] == pair_number and row['spin'] == spin]
    if len(matches) != 1:
        raise ValueError('Selected pair and spin do not identify one ETS-NOCV table row')
    if not unit.strip() or unit.strip().lower() == 'unknown' or len(unit) > 80:
        raise ValueError('Specify the deformation density unit')
    data = read_cube(cube_path)
    if len(data.metadata['fields']) != 1:
        raise ValueError('NOCV pair requires one scalar Cube field')
    association = compare_sources(table, data)
    field = data.metadata['fields'][0]
    values = data.arrays[field['array']]
    if not np.any(values < 0) or not np.any(values > 0):
        raise ValueError('NOCV deformation density must contain both positive and negative values')
    field.update(quantity='nocv_deformation_density', unit=unit.strip(),
                 interpretation='user_assigned', pair=pair_number, spin=spin)
    data.metadata['analysis'] = {'kind': 'NOCV-field', 'pair': matches[0], 'spin': spin,
                                 'table_source': table.metadata['source']['sha256'],
                                 'association': association, 'cube_source': data.metadata['source'],
                                 'importer': 'qcblender.nocv 0.1'}
    data.metadata['title'] = f'NOCV pair {pair_number} {spin}'
    data.validate()
    return data
