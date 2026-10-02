"""Attach precomputed external analysis records to an explicit QC geometry."""
import math
from pathlib import Path
import re

import numpy as np

from .data import Dataset
from .association import require_static_geometry
from .external_results import (aim_paths, aim_points, aim_properties, esp_area,
                               esp_extrema, esp_extrema_unit, ets_nocv_pairs)
from .readers import source_record


def analysis_dataset(reference, kind, paths, result):
    require_static_geometry(reference)
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
    require_static_geometry(reference)
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
    if str(surface_definition).strip().lower() in ('', 'unknown') or not str(center_unit).strip():
        raise ValueError('ESP surface definition and distribution center unit are required')
    energy_units = {'kcal/mol': 'kcal/mol', 'ev': 'eV', 'a.u.': 'a.u.'}
    def energy_unit(value, label):
        unit = energy_units.get(str(value).strip().lower())
        if unit is None:
            raise ValueError(f'ESP {label} must be a.u., eV or kcal/mol')
        return unit

    declaration = esp_extrema_unit(extrema_path)
    if value_unit and str(value_unit).strip():
        value_unit = energy_unit(value_unit, 'extrema unit')
        if declaration and value_unit != declaration['unit']:
            raise ValueError(f'ESP extrema unit {value_unit} conflicts with PDB line {declaration["source_line"]}: {declaration["unit"]}')
    elif declaration:
        value_unit = declaration['unit']
    else:
        raise ValueError('ESP extrema PDB has no B-factor unit declaration; specify the extrema unit')
    center_unit = energy_unit(center_unit, 'distribution center unit')
    area_declaration = None
    for number, line in enumerate(Path(area_path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if 'area unit' not in line.lower():
            continue
        match = re.fullmatch(r'\s*Note:\s*Area unit is in\s+(.+?)\s*', line, re.I)
        if not match or match[1].lower() != 'angstrom^2':
            raise ValueError(f'ESP area line {number} has an unsupported area unit declaration')
        area_declaration = {'unit': 'angstrom^2', 'source_line': number, 'raw': line}
    if area_unit and str(area_unit).strip():
        if str(area_unit).strip().lower() not in ('angstrom^2', 'bohr^2'):
            raise ValueError('ESP area unit must be angstrom^2 or bohr^2')
        area_unit = str(area_unit).strip().lower()
        if area_declaration and area_unit != area_declaration['unit']:
            raise ValueError(f'ESP area unit {area_unit} conflicts with table line {area_declaration["source_line"]}')
    elif area_declaration:
        area_unit = area_declaration['unit']
    else:
        raise ValueError('ESP area table has no area unit declaration; specify the area unit')
    extrema = esp_extrema(extrema_path)
    bins = esp_area(area_path)
    check = spatial_check([point['position_angstrom'] for point in extrema], reference)
    result = {'surface_definition': surface_definition.strip(), 'extrema_unit': value_unit,
              'extrema_unit_declaration': declaration,
              'distribution_center_unit': center_unit, 'area_unit': area_unit,
              'area_unit_declaration': area_declaration,
              'extrema': extrema, 'area_bins': bins, 'spatial_check': check,
              'area_sum': sum(row['area'] for row in bins)}
    return analysis_dataset(reference, 'ESP', [extrema_path, area_path], result)


def import_aim(reference, cps_path, paths_path, properties_path=None):
    check_text_sources([cps_path, paths_path] + ([properties_path] if properties_path else []))
    cps = aim_points(cps_path)
    paths = aim_paths(paths_path)
    if properties_path:
        lines = Path(properties_path).read_text(encoding='utf-8', errors='replace').splitlines()
        current, seen_fields = None, set()
        for number, line in enumerate(lines, 1):
            stripped = line.strip()
            legacy = re.match(r'-+\s*CP\s+(\d+)', stripped)
            modern = re.match(r'Critical point\s+(\d+)', stripped)
            if legacy:
                if not re.search(r'CP\s+\d+,\s*Type\s*\([^)]+\)', stripped):
                    raise ValueError(f'AIM property line {number} has a malformed CP header')
                current = int(legacy[1])
                seen_fields.add((current, 'type'))
            if modern:
                if not re.match(r'Critical point\s+\d+\s*:', stripped):
                    raise ValueError(f'AIM property line {number} has a malformed CP header')
                current = int(modern[1])
            field = re.match(r'(CP_type|CP type|Position \(Angstrom\))(?=\s|:|$)', stripped)
            if field:
                kind = 'position' if field[1].startswith('Position') else 'type'
                if current is None or (current, kind) in seen_fields:
                    raise ValueError(f'AIM property line {number} has an unassigned or repeated {kind} field')
                seen_fields.add((current, kind))
                value = stripped.partition(':')[2].strip()
                if not value or value == 'unknown':
                    raise ValueError(f'AIM property line {number} has a malformed field')
    properties = aim_properties(properties_path, {point['serial'] for point in cps}) if properties_path else {}
    cp_types = {'C': '(3,-3)', 'N': '(3,-1)', 'O': '(3,+1)', 'F': '(3,+3)'}
    unverified_type = unverified_position = 0
    for point in cps:
        record = properties.get(point['serial'], {})
        labels = [record[key] for key in ('CP_type', 'CP type') if key in record and record[key] != 'unknown']
        if not labels:
            unverified_type += 1
        elif any(label != cp_types[point['type']] for label in labels):
            raise ValueError(f"AIM CP {point['serial']} property type conflicts with CPs.pdb or is malformed")
        position = record.get('Position (Angstrom)')
        if position is None:
            unverified_position += 1
        else:
            try:
                values = [float(value) for value in str(position).split()]
            except ValueError as error:
                raise ValueError(f"AIM CP {point['serial']} property position is malformed") from error
            if len(values) != 3 or not all(math.isfinite(value) for value in values):
                raise ValueError(f"AIM CP {point['serial']} property position is malformed or nonfinite")
            if any(abs(a - b) > 0.0005001 for a, b in zip(values, point['position_angstrom'])):
                raise ValueError(f"AIM CP {point['serial']} property position conflicts with CPs.pdb")
    check = spatial_check([point['position_angstrom'] for point in cps] +
                          [position for path in paths for position in path['points_angstrom']], reference)
    files = [cps_path, paths_path] + ([properties_path] if properties_path else [])
    data = analysis_dataset(reference, 'AIM', files,
                            {'critical_points': cps, 'paths': paths, 'properties': properties,
                             'spatial_check': check, 'coordinate_unit': 'angstrom'})
    for field, count in (('type', unverified_type), ('position', unverified_position)):
        if count:
            data.metadata['diagnostics'].append(f'AIM CP property {field} unverified for {count} CP(s): field absent')
    return data


def import_ets(reference, output_path, energy_unit):
    check_text_sources((output_path,))
    pairs = ets_nocv_pairs(output_path, energy_unit)
    return analysis_dataset(reference, 'ETS-NOCV', [output_path],
                            {'pairs': pairs, 'energy_unit': energy_unit})
