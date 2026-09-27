"""Sample scalar line profiles and export their saved arrays."""
import csv
import hashlib
import json

import numpy as np

from .data import Dataset
from .sampling import sample_point


def source_positions(world_start, world_end, matrix_world):
    """Return world endpoints in the chosen volume's local angstrom coordinates."""
    world = np.asarray((world_start, world_end), dtype=np.float64)
    matrix = np.asarray(matrix_world, dtype=np.float64)
    if world.shape != (2, 3) or matrix.shape != (4, 4) or not np.isfinite(world).all() or not np.isfinite(matrix).all():
        raise ValueError('Profile endpoints and source transform must be finite 3D coordinates')
    homogeneous = np.column_stack((world, np.ones(2))) @ np.linalg.inv(matrix).T
    if not np.isfinite(homogeneous).all() or np.any(np.abs(homogeneous[:, 3]) < 1e-15):
        raise ValueError('Source transform cannot locate the profile endpoints')
    return homogeneous[:, :3] / homogeneous[:, 3, None]


def valid_runs(valid):
    """Half-open runs with at least two adjacent valid samples."""
    edges = np.diff(np.r_[False, np.asarray(valid, dtype=bool), False].astype(np.int8))
    return [(int(start), int(stop)) for start, stop in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))
            if stop - start >= 2]


def sample_profile(reference, field, start, end, world_start, world_end, manifest_sha256, role='GEOMETRY', count=101):
    if type(count) is not int or not 2 <= count <= 1001:
        raise ValueError('Profile samples must be between 2 and 1001')
    endpoints = np.asarray((start, end), dtype=np.float64)
    world = np.asarray((world_start, world_end), dtype=np.float64)
    if endpoints.shape != (2, 3) or world.shape != (2, 3) or not np.isfinite(endpoints).all() or not np.isfinite(world).all():
        raise ValueError('Profile endpoints must be finite 3D coordinates')
    length = float(np.linalg.norm(endpoints[1] - endpoints[0]))
    if length <= 1e-12:
        raise ValueError('Profile endpoints must differ in source angstrom coordinates')
    if role not in ('GEOMETRY', 'COLOR'):
        raise ValueError('Unsupported profile field role')
    values = reference.arrays[field['array']]
    mask = reference.arrays[field['valid_mask']]
    positions = np.linspace(endpoints[0], endpoints[1], count)
    distance = np.linspace(0., length, count)
    sampled = np.zeros(count, dtype=np.float64)
    valid = np.zeros(count, dtype=bool)
    for index, point in enumerate(positions):
        try:
            sampled[index] = sample_point(values, mask, field, point)
            valid[index] = True
        except ValueError:
            pass
    if not valid_runs(valid):
        raise ValueError('Profile has no adjacent valid samples')
    profile = {'field_role': role, 'field': field, 'source_manifest_sha256': manifest_sha256,
               'source_record': reference.metadata['source'], 'start_source_angstrom': endpoints[0].tolist(),
               'end_source_angstrom': endpoints[1].tolist(), 'start_world': world[0].tolist(),
               'end_world': world[1].tolist(), 'interpolation': 'trilinear'}
    digest = hashlib.sha256(json.dumps(profile, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
    metadata = {'source': {'kind': 'derived', 'filename': 'line profile', 'sha256': digest,
                           'format': 'qcblender.profile', 'parser': 'qcblender.profile 0.1'},
                'coordinate_unit': 'angstrom', 'calculation_status': 'derived',
                'title': 'Line profile', 'fields': [], 'charges': [], 'energies': [],
                'diagnostics': [], 'profile': profile}
    data = Dataset(metadata, {'atomic_numbers': reference.arrays['atomic_numbers'].copy(),
                              'positions': reference.arrays['positions'].copy(),
                              'profile_distance': distance, 'profile_positions': positions,
                              'profile_values': sampled, 'profile_valid': valid})
    data.validate()
    return data


def export_profile_csv(data, path):
    field = data.metadata['profile']['field']
    arrays = data.arrays
    with open(path, 'w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('distance_angstrom', 'x_angstrom', 'y_angstrom', 'z_angstrom', 'value', 'unit', 'valid'))
        for distance, position, value, valid in zip(arrays['profile_distance'], arrays['profile_positions'],
                                                    arrays['profile_values'], arrays['profile_valid'], strict=True):
            writer.writerow((float(distance), *map(float, position), float(value) if valid else '',
                             field['unit'], int(valid)))
