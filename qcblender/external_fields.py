"""Explicitly associated external scalar fields."""
import math
from pathlib import Path

import numpy as np

from .association import compare_sources
from .cube import read_cube
from .data import Dataset


def pair_cubes(geometry_path, color_path, method, geometry_unit, color_unit, iri_exponent=None):
    if method not in ('IGMH', 'IRI'):
        raise ValueError('Choose IGMH or IRI')
    for label, unit in [('Geometry', geometry_unit), ('Color', color_unit)]:
        if not unit.strip() or unit.strip().lower() in ('unknown', 'dimensionless') or len(unit) > 80:
            raise ValueError(f'{label} field unit must be explicitly specified')
    if method == 'IRI' and iri_exponent is not None:
        try:
            iri_exponent = float(iri_exponent)
        except (TypeError, ValueError) as error:
            raise ValueError('IRI density exponent must be a finite positive number') from error
        if not math.isfinite(iri_exponent) or iri_exponent <= 0:
            raise ValueError('IRI density exponent must be a finite positive number')
    elif method == 'IGMH' and iri_exponent is not None:
        raise ValueError('IRI density exponent applies only to IRI')
    geometry, color = read_cube(geometry_path), read_cube(color_path)
    if geometry.metadata['source']['sha256'] == color.metadata['source']['sha256']:
        raise ValueError('Geometry and color Cube files have identical content')
    if len(geometry.metadata['fields']) != 1 or len(color.metadata['fields']) != 1:
        raise ValueError('Each analysis role requires exactly one Cube scalar field')
    association = compare_sources(geometry, color)
    first, second = geometry.metadata['fields'][0], color.metadata['fields'][0]
    if first['shape'] != second['shape'] or not np.allclose(first['origin'], second['origin'], rtol=0, atol=1e-6) or not np.allclose(first['steps'], second['steps'], rtol=0, atol=1e-6):
        raise ValueError('Geometry and color Cube grids differ; no resampling is inferred')
    arrays = dict(geometry.arrays)
    arrays['analysis_color'] = color.arrays[second['array']]
    arrays['analysis_color_valid'] = color.arrays[second['valid_mask']]
    first.update(quantity='delta_g' if method == 'IGMH' else 'iri_function', unit=geometry_unit.strip(),
                 interpretation='user_assigned', role='geometry')
    second = dict(second, array='analysis_color', valid_mask='analysis_color_valid',
                  quantity='sign_lambda2_rho', unit=color_unit.strip(),
                  interpretation='user_assigned', role='color')
    metadata = dict(geometry.metadata)
    metadata['fields'] = [first, second]
    metadata['analysis'] = {'kind': method, 'association': association,
                            'geometry_source': geometry.metadata['source'],
                            'color_source': color.metadata['source'],
                            'importer': 'qcblender.external_fields 0.1'}
    if method == 'IRI':
        metadata['analysis']['iri_density_exponent'] = iri_exponent
        if iri_exponent is None:
            metadata['diagnostics'].append('IRI density exponent not supplied at import; interpretation unverified')
    metadata['title'] = f'{method} {Path(geometry_path).name}'
    result = Dataset(metadata, arrays)
    result.validate()
    return result
