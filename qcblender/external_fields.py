"""Explicitly associated external scalar fields."""
import math
from collections import Counter
from pathlib import Path

import numpy as np

from .association import compare_sources
from .cube import read_cube
from .data import Dataset


def igmh_declaration(component, fragments, source, atom_count):
    """Validate user statements in the source Cube atom order; never infer a component."""
    if component not in ('inter', 'intra', 'total', 'unknown'):
        raise ValueError('Choose inter, intra, total or unknown for the IGMH component')
    if not isinstance(source, str) or len(source) > 500:
        raise ValueError('IGMH declaration source must be text of at most 500 characters')
    fragments = [] if fragments is None else fragments
    if not isinstance(fragments, list) or any(not isinstance(fragment, list) for fragment in fragments):
        raise ValueError('IGMH fragments must be a list of lists of 1-based source Cube atom numbers')
    members = []
    for fragment in fragments:
        if any(type(atom) is not int or not 1 <= atom <= atom_count for atom in fragment):
            raise ValueError(f'IGMH fragment atoms must be integers in source Cube order, 1-{atom_count}')
        if len(fragment) != len(set(fragment)):
            raise ValueError('IGMH atom numbers must not repeat within one fragment')
        members.extend(fragment)
    overlap = sorted(atom for atom, count in Counter(members).items() if count > 1)
    warnings = ['片段之间包含重复原子；已保留交叠声明：' + ', '.join(map(str, overlap))] if overlap else []
    return {'component': component, 'fragments': [list(fragment) for fragment in fragments],
            'atom_indexing': 'source_cube_1based', 'source': source.strip(),
            'interpretation': 'user_assigned',
            'status': 'unverified' if component == 'unknown' else 'declared',
            'overlapping_atoms': overlap, 'warnings': warnings}


def igmh_declaration_record(analysis):
    """Read current and legacy records for display without assigning missing science."""
    record = analysis.get('igmh_declaration')
    if isinstance(record, dict):
        return record
    return {'component': 'unknown', 'fragments': [], 'source': '',
            'interpretation': 'unverified', 'status': 'unverified', 'warnings': []}


def pair_cubes(geometry_path, color_path, method, geometry_unit, color_unit, iri_exponent=None,
               *, igmh_component='unknown', igmh_fragments=None, igmh_declaration_source=''):
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
    if method == 'IRI' and (igmh_component != 'unknown' or igmh_fragments is not None
                            or igmh_declaration_source):
        raise ValueError('IGMH declarations apply only to IGMH fields')
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
    if method == 'IGMH':
        declaration = igmh_declaration(igmh_component, igmh_fragments, igmh_declaration_source,
                                      len(geometry.arrays['atomic_numbers']))
        metadata['analysis']['igmh_declaration'] = declaration
        metadata['diagnostics'].extend(declaration['warnings'])
        if declaration['status'] == 'unverified':
            metadata['diagnostics'].append('IGMH component not declared; interpretation unverified')
    if method == 'IRI':
        metadata['analysis']['iri_density_exponent'] = iri_exponent
        if iri_exponent is None:
            metadata['diagnostics'].append('IRI density exponent not supplied at import; interpretation unverified')
    metadata['title'] = f'{method} {Path(geometry_path).name}'
    result = Dataset(metadata, arrays)
    result.validate()
    return result
