"""Read-only selection of external result records and paired-field samples."""
import hashlib
from io import BytesIO
import math
from pathlib import Path

import numpy as np


def _limits(value, lower, upper):
    return (lower is None or value >= lower) and (upper is None or value <= upper)


def _range(lower, upper, label):
    if any(value is not None and not math.isfinite(value) for value in (lower, upper)):
        raise ValueError(f'{label} range must be finite')
    if lower is not None and upper is not None and lower > upper:
        raise ValueError(f'{label} minimum exceeds maximum')


def scatter_selection(data, x_field=1, y_field=0, x_min=None, x_max=None,
                      y_min=None, y_max=None, maximum=50000):
    """Filter every valid voxel, then deterministically retain at most maximum."""
    if {x_field, y_field} != {0, 1} or len(data.metadata['fields']) != 2:
        raise ValueError('Choose the two distinct paired fields as scatter axes')
    _range(x_min, x_max, 'X')
    _range(y_min, y_max, 'Y')
    if not 1 <= maximum <= 50000:
        raise ValueError('Scatter display limit must be from 1 to 50000')
    fields = data.metadata['fields']
    x = data.arrays[fields[x_field]['array']].ravel()
    y = data.arrays[fields[y_field]['array']].ravel()
    valid = (data.arrays[fields[x_field]['valid_mask']].ravel() &
             data.arrays[fields[y_field]['valid_mask']].ravel() &
             np.isfinite(x) & np.isfinite(y))
    if x_min is not None:
        valid &= x >= x_min
    if x_max is not None:
        valid &= x <= x_max
    if y_min is not None:
        valid &= y >= y_min
    if y_max is not None:
        valid &= y <= y_max
    indexes = np.flatnonzero(valid)
    matching = len(indexes)
    if matching > maximum:
        indexes = indexes[np.linspace(0, matching - 1, maximum, dtype=np.int64)]
    return {'points': np.stack((x[indexes], y[indexes]), axis=1),
            'flat_indices': indexes, 'matching_count': matching,
            'displayed_count': len(indexes), 'x_field': x_field, 'y_field': y_field}


def scatter_report(request, directory, cancelled=lambda: False):
    """Worker entry: verify the bound dataset and write display points only."""
    from .data import load_dataset

    if cancelled():
        raise RuntimeError('Scatter filtering cancelled')
    source = Path(request['dataset'])
    digest = hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest()
    if digest != request['dataset_sha256']:
        raise ValueError('Scatter source changed after the request was created')
    selected = scatter_selection(load_dataset(source), request['x_field'], request['y_field'],
                                 request.get('x_min'), request.get('x_max'),
                                 request.get('y_min'), request.get('y_max'))
    if cancelled():
        raise RuntimeError('Scatter filtering cancelled')
    points_path = Path(directory) / 'scatter.npy'
    np.save(points_path, selected['points'], allow_pickle=False)
    report = {key: selected[key] for key in ('matching_count', 'displayed_count', 'x_field', 'y_field')}
    report['scatter_sha256'] = hashlib.sha256(points_path.read_bytes()).hexdigest()
    return report


def verified_scatter_points(path, report, x_field, y_field):
    """Load exactly the worker bytes named by its result report."""
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != report.get('scatter_sha256'):
        raise ValueError('Worker scatter array differs from its reported SHA-256')
    points = np.load(BytesIO(raw), allow_pickle=False)
    if (not isinstance(points, np.ndarray) or points.dtype.kind != 'f'
            or points.ndim != 2 or points.shape[1] != 2
            or type(report.get('matching_count')) is not int
            or type(report.get('displayed_count')) is not int
            or not 0 <= report['displayed_count'] <= report['matching_count']
            or len(points) != report['displayed_count'] or len(points) > 50000
            or not np.isfinite(points).all()
            or (report.get('x_field'), report.get('y_field')) != (x_field, y_field)):
        raise ValueError('Worker returned invalid scatter points')
    return points


def point_selection(analysis, serial=None, kind=None, value_min=None, value_max=None,
                    value_key=None):
    """Select ESP extrema or AIM critical points in source order."""
    if analysis['kind'] not in ('ESP', 'AIM'):
        raise ValueError('Select an ESP or AIM result')
    _range(value_min, value_max, 'Point value')
    if serial is not None and serial < 1:
        raise ValueError('Source number must be positive')
    key = 'extrema' if analysis['kind'] == 'ESP' else 'critical_points'
    if analysis['kind'] == 'AIM' and (value_min is not None or value_max is not None):
        if not value_key:
            raise ValueError('Choose a numeric AIM CP property before filtering values')
        if not any(value_key in record and isinstance(record[value_key], (int, float))
                   for record in analysis.get('properties', {}).values()):
            raise ValueError(f'AIM CP property {value_key!r} is absent or nonnumeric')
    def matches_value(row):
        if analysis['kind'] == 'ESP':
            return _limits(row['value'], value_min, value_max)
        if value_min is None and value_max is None:
            return True
        properties = analysis['properties']
        value = properties.get(str(row['serial']), properties.get(row['serial'], {})).get(value_key)
        return isinstance(value, (int, float)) and math.isfinite(value) and _limits(value, value_min, value_max)

    return [index for index, row in enumerate(analysis[key])
            if (serial is None or row['serial'] == serial)
            and (kind is None or row['kind' if key == 'extrema' else 'type'] == kind)
            and matches_value(row)]


def point_label(analysis, row, value_key=None):
    """Describe one source point without inventing an AIM property or unit."""
    if analysis['kind'] == 'ESP':
        return f"{row['kind']} {row['serial']} | {row['value']:.6g} {analysis['extrema_unit']}"
    if analysis['kind'] != 'AIM':
        raise ValueError('Select an ESP or AIM point')
    label = f"{row['type']} {row['serial']}"
    properties = analysis.get('properties', {})
    recorded = properties.get(str(row['serial']), properties.get(row['serial'], {}))
    key = value_key or ('Density of all electrons' if 'Density of all electrons' in recorded else None)
    if key:
        value = recorded.get(key)
        if isinstance(value, (int, float)) and math.isfinite(value):
            label += f' | {key}: {value:.6g}'
    return label


def area_selection(analysis, center_min=None, center_max=None, mode='center'):
    if analysis['kind'] != 'ESP':
        raise ValueError('Select an ESP area table')
    if mode not in ('center', 'source_interval'):
        raise ValueError('Choose center or recorded source interval filtering')
    _range(center_min, center_max, 'Area center' if mode == 'center' else 'Source interval')
    bins = analysis['area_bins']
    if mode == 'source_interval':
        if any(row.get('begin') is None or row.get('end') is None for row in bins):
            raise ValueError('Source interval bounds were not recorded in this ESP table')
        indexes = [index for index, row in enumerate(bins)
                   if (center_min is None or row['end'] >= center_min)
                   and (center_max is None or row['begin'] <= center_max)]
    else:
        indexes = [index for index, row in enumerate(bins)
                   if _limits(row['center'], center_min, center_max)]
    return {'indexes': indexes, 'total_area': sum(row['area'] for row in bins),
            'displayed_area': sum(bins[index]['area'] for index in indexes),
            'displayed_source_percentage': sum(bins[index]['percentage'] for index in indexes),
            'selection_mode': mode}


def nbo_selection(analysis, number=None, orbital_type=None, occupancy_min=None,
                  occupancy_max=None, donor=None, acceptor=None, e2_min=None, e2_max=None,
                  orbital_sort='source', interaction_sort='source'):
    if analysis['kind'] != 'NBO':
        raise ValueError('Select an NBO result')
    _range(occupancy_min, occupancy_max, 'Occupancy')
    _range(e2_min, e2_max, 'E(2)')
    if orbital_sort not in ('source', 'number', 'type', 'occupancy_desc'):
        raise ValueError('Unsupported NBO orbital sort field')
    if interaction_sort not in ('source', 'donor', 'acceptor', 'e2_desc'):
        raise ValueError('Unsupported NBO interaction sort field')
    if any(value is not None and value < 1 for value in (number, donor, acceptor)):
        raise ValueError('NBO source numbers must be positive')
    orbitals = [index for index, row in enumerate(analysis['orbitals'])
                if (number is None or row['number'] == number)
                and (orbital_type is None or row['type'] == orbital_type)
                and _limits(row['occupancy'], occupancy_min, occupancy_max)]
    allowed = {analysis['orbitals'][index]['number'] for index in orbitals}
    constrain_orbital = number is not None or orbital_type is not None or occupancy_min is not None or occupancy_max is not None
    interactions = [index for index, row in enumerate(analysis['interactions'])
                    if (not constrain_orbital or row['donor'] in allowed or row['acceptor'] in allowed)
                    and (donor is None or row['donor'] == donor)
                    and (acceptor is None or row['acceptor'] == acceptor)
                    and _limits(row['e2_kcal_mol'], e2_min, e2_max)]
    if orbital_sort != 'source':
        def orbital_key(index):
            row = analysis['orbitals'][index]
            return ((row['number'], index) if orbital_sort == 'number' else
                    (row['type'], row['number'], index) if orbital_sort == 'type' else
                    (-row['occupancy'], row['number'], index))
        orbitals.sort(key=orbital_key)
    if interaction_sort != 'source':
        def interaction_key(index):
            row = analysis['interactions'][index]
            return ((row['donor'], row['acceptor'], index) if interaction_sort == 'donor' else
                    (row['acceptor'], row['donor'], index) if interaction_sort == 'acceptor' else
                    (-row['e2_kcal_mol'], row['donor'], row['acceptor'], index))
        interactions.sort(key=interaction_key)
    return {'orbitals': orbitals, 'interactions': interactions}


def nocv_selection(analysis, pair=None, spin=None, eigen_min=None, eigen_max=None,
                   energy_min=None, energy_max=None, eigen_side='either', sort_by='pair'):
    if analysis['kind'] != 'ETS-NOCV':
        raise ValueError('Select an ETS-NOCV pair table')
    _range(eigen_min, eigen_max, 'Eigenvalue')
    _range(energy_min, energy_max, 'Pair energy')
    if pair is not None and pair < 1:
        raise ValueError('Pair number must be positive')
    if eigen_side not in ('either', 'positive', 'negative'):
        raise ValueError('Choose positive, negative or either NOCV eigenvalue')
    if sort_by not in ('pair', 'pair_energy', 'positive_eigenvalue', 'negative_eigenvalue'):
        raise ValueError('Unsupported NOCV sort field')
    rows = analysis['pairs']
    indexes = []
    for index, row in enumerate(rows):
        eigenvalues = ([row['positive_eigenvalue'], row['negative_eigenvalue']]
                       if eigen_side == 'either' else [row[eigen_side + '_eigenvalue']])
        if ((pair is None or row['pair'] == pair) and (spin is None or row['spin'] == spin)
                and _limits(row['pair_energy'], energy_min, energy_max)
                and any(_limits(value, eigen_min, eigen_max) for value in eigenvalues)):
            indexes.append(index)
    return sorted(indexes, key=lambda index: (rows[index][sort_by], rows[index]['spin'],
                                               rows[index]['pair'], index))
