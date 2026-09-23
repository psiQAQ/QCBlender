"""Attach precomputed external analysis records to an explicit QC geometry."""
from pathlib import Path

import numpy as np

from .data import Dataset
from .external_results import (aim_paths, aim_points, aim_properties, esp_area,
                               esp_extrema, ets_nocv_pairs)
from .readers import source_record


def analysis_dataset(reference, kind, paths, result):
    sources = [source_record(Path(path), Path(path).suffix.lower().lstrip('.'),
                             'qcblender.external_results 0.1') for path in paths]
    metadata = {'source': sources[0], 'coordinate_unit': 'angstrom', 'fields': [],
                'charges': [], 'energies': [], 'title': kind + ' external result',
                'calculation_status': 'external_analysis', 'diagnostics': [],
                'analysis': dict(result, kind=kind, sources=sources,
                                 reference_source=reference.metadata['source']['sha256'],
                                 association='user_assigned')}
    arrays = {'atomic_numbers': np.array(reference.arrays['atomic_numbers'], copy=True),
              'positions': np.array(reference.arrays['positions'], copy=True)}
    data = Dataset(metadata, arrays)
    data.validate()
    return data


def check_text_sources(paths):
    for path in paths:
        if Path(path).stat().st_size > 64 * 1024**2:
            raise MemoryError('External text result exceeds the 64 MiB import limit')


def spatial_check(points, reference, margin_angstrom=10):
    coordinates = np.asarray(points, dtype=float)
    atoms = reference.arrays['positions']
    if not len(atoms) or coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise ValueError('External coordinates and reference atoms are required')
    if np.any(coordinates < atoms.min(axis=0) - margin_angstrom) or np.any(coordinates > atoms.max(axis=0) + margin_angstrom):
        raise ValueError('External point coordinates lie outside the selected geometry vicinity')
    return {'kind': 'bounding_box', 'margin_angstrom': margin_angstrom,
            'meaning': 'coarse spatial check; exact calculation identity supplied by user'}


def import_esp(reference, extrema_path, area_path, surface_definition, value_unit, center_unit, area_unit):
    check_text_sources((extrema_path, area_path))
    if not all(str(value).strip() and str(value).strip().lower() != 'unknown'
               for value in (surface_definition, value_unit, center_unit, area_unit)):
        raise ValueError('ESP surface definition and all value/area units are required')
    extrema = esp_extrema(extrema_path)
    bins = esp_area(area_path)
    check = spatial_check([point['position_angstrom'] for point in extrema], reference)
    result = {'surface_definition': surface_definition.strip(), 'extrema_unit': value_unit.strip(),
              'distribution_center_unit': center_unit.strip(), 'area_unit': area_unit.strip(),
              'extrema': extrema, 'area_bins': bins, 'spatial_check': check,
              'area_sum': sum(row['area'] for row in bins)}
    return analysis_dataset(reference, 'ESP', [extrema_path, area_path], result)


def import_aim(reference, cps_path, paths_path, properties_path=None):
    check_text_sources([cps_path, paths_path] + ([properties_path] if properties_path else []))
    cps = aim_points(cps_path)
    paths = aim_paths(paths_path)
    properties = aim_properties(properties_path, {point['serial'] for point in cps}) if properties_path else {}
    check = spatial_check([point['position_angstrom'] for point in cps] +
                          [position for path in paths for position in path['points_angstrom']], reference)
    files = [cps_path, paths_path] + ([properties_path] if properties_path else [])
    return analysis_dataset(reference, 'AIM', files,
                            {'critical_points': cps, 'paths': paths, 'properties': properties,
                             'spatial_check': check, 'coordinate_unit': 'angstrom'})


def import_ets(reference, output_path, energy_unit):
    check_text_sources((output_path,))
    pairs = ets_nocv_pairs(output_path, energy_unit)
    return analysis_dataset(reference, 'ETS-NOCV', [output_path],
                            {'pairs': pairs, 'energy_unit': energy_unit})
