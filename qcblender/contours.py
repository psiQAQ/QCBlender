"""Sample planar QC fields and trace contours without Blender."""

import hashlib
from pathlib import Path
import re

import numpy as np

from .sampling import sample_point


def levels_from_samples(values, valid, explicit=''):
    samples = np.asarray(values, dtype=np.float64)[np.asarray(valid, dtype=bool)]
    if not len(samples) or not np.isfinite(samples).all():
        raise ValueError('The contour plane has no finite valid samples')
    if isinstance(explicit, str):
        tokens = [part for part in re.split(r'[,;\s]+', explicit.strip()) if part]
        levels = [float(token) for token in tokens]
    else:
        levels = [float(value) for value in explicit]
    if len(levels) > 64 or not all(np.isfinite(level) for level in levels):
        raise ValueError('Use at most 64 finite contour levels')
    if levels:
        if len(set(levels)) != len(levels):
            raise ValueError('Contour levels must be distinct')
        return sorted(levels)
    low, high = float(samples.min()), float(samples.max())
    if low == high:
        return []
    return np.linspace(low, high, 11, dtype=np.float64)[1:-1].tolist()


def plane_positions(origin, axis_u, axis_v, resolution):
    if type(resolution) is not int or not 2 <= resolution <= 1001:
        raise ValueError('Contour plane resolution must be between 2 and 1001')
    vectors = np.asarray((origin, axis_u, axis_v), dtype=np.float64)
    if vectors.shape != (3, 3) or not np.isfinite(vectors).all():
        raise ValueError('Contour plane vectors must be finite 3D coordinates')
    if np.linalg.norm(np.cross(vectors[1], vectors[2])) <= 1e-12:
        raise ValueError('Contour plane axes must span an area')
    fraction = np.linspace(0., 1., resolution)
    return (vectors[0] + fraction[:, None, None] * vectors[2]
            + fraction[None, :, None] * vectors[1])


def sample_plane(data, field, positions, cancelled=lambda: False):
    count = len(positions)
    values = np.zeros((count, count), dtype=np.float64)
    valid = np.zeros((count, count), dtype=bool)
    source = data.arrays[field['array']]
    mask = data.arrays[field['valid_mask']]
    for row in range(count):
        if cancelled():
            raise InterruptedError('Contour sampling cancelled')
        for column in range(count):
            try:
                values[row, column] = sample_point(source, mask, field, positions[row, column])
                valid[row, column] = True
            except ValueError:
                pass
    return values, valid


def trace_contours(values, valid, positions, level, cancelled=lambda: False):
    """Return polylines; a cell contributes only when all four corners are valid."""
    values = np.asarray(values, dtype=np.float64)
    valid = np.asarray(valid, dtype=bool)
    positions = np.asarray(positions, dtype=np.float64)
    if (values.ndim != 2 or values.shape != valid.shape
            or positions.shape != (*values.shape, 3) or not np.isfinite(level)):
        raise ValueError('Contour grid, validity and positions must agree')
    if not np.isfinite(values[valid]).all() or not np.isfinite(positions).all():
        raise ValueError('Contour inputs must be finite')
    points, neighbors = {}, {}

    def connect(first, second):
        if np.linalg.norm(points[first] - points[second]) <= 1e-12:
            return
        neighbors.setdefault(first, set()).add(second)
        neighbors.setdefault(second, set()).add(first)

    for row in range(values.shape[0] - 1):
        if cancelled():
            raise InterruptedError('Contour tracing cancelled')
        for column in range(values.shape[1] - 1):
            corners = ((row, column), (row, column + 1),
                       (row + 1, column + 1), (row + 1, column))
            if not all(valid[index] for index in corners):
                continue
            scalar = [float(values[index]) for index in corners]
            above = [value >= level for value in scalar]
            edges = ((0, 1, ('h', row, column)),
                     (1, 2, ('v', row, column + 1)),
                     (2, 3, ('h', row + 1, column)),
                     (3, 0, ('v', row, column)))
            crossed = []
            for number, (start, stop, key) in enumerate(edges):
                if above[start] == above[stop]:
                    continue
                fraction = (level - scalar[start]) / (scalar[stop] - scalar[start])
                points[key] = (positions[corners[start]] * (1 - fraction)
                               + positions[corners[stop]] * fraction)
                crossed.append(number)
            if len(crossed) == 2:
                connect(edges[crossed[0]][2], edges[crossed[1]][2])
            elif len(crossed) == 4:
                delta = [value - level for value in scalar]
                determinant = delta[0] * delta[2] - delta[1] * delta[3]
                scale = max(abs(value) for value in delta) ** 2
                if abs(determinant) <= 1e-14 * scale:
                    diagonal = scalar[0] - scalar[1] + scalar[2] - scalar[3]
                    u = (scalar[0] - scalar[3]) / diagonal
                    v = (scalar[0] - scalar[1]) / diagonal
                    center = ('c', row, column)
                    points[center] = ((1-u) * (1-v) * positions[corners[0]]
                                      + u * (1-v) * positions[corners[1]]
                                      + u * v * positions[corners[2]]
                                      + (1-u) * v * positions[corners[3]])
                    for _, _, key in edges:
                        connect(key, center)
                else:
                    pairs = ((0, 1), (2, 3)) if determinant > 0 else ((0, 3), (1, 2))
                    for first, second in pairs:
                        connect(edges[first][2], edges[second][2])

    unused = {frozenset((first, second)) for first, linked in neighbors.items()
              for second in linked}
    lines = []

    def walk(start, next_key):
        path = [start]
        previous, current = start, next_key
        while True:
            unused.remove(frozenset((previous, current)))
            path.append(current)
            options = [key for key in neighbors[current]
                       if frozenset((current, key)) in unused]
            if len(neighbors[current]) != 2 or not options:
                break
            previous, current = current, options[0]
        lines.append([points[key].tolist() for key in path])

    for start in sorted(neighbors):
        if len(neighbors[start]) != 2:
            for next_key in sorted(neighbors[start]):
                if frozenset((start, next_key)) in unused:
                    walk(start, next_key)
    while unused:
        first, second = sorted(next(iter(unused)))
        walk(first, second)
    return lines


def contour_report(request, load_dataset, cancelled=lambda: False):
    dataset = Path(request['dataset'])
    digest = hashlib.sha256((dataset / 'manifest.json').read_bytes()).hexdigest()
    if digest != request['dataset_sha256']:
        raise ValueError('Contour dataset changed after the request was created')
    data = load_dataset(dataset)
    field = request['field']
    if field not in data.metadata['fields']:
        raise ValueError('Contour field differs from the saved dataset')
    plane = request['plane']
    positions = plane_positions(plane['origin'], plane['axis_u'], plane['axis_v'], plane['resolution'])
    values, valid = sample_plane(data, field, positions, cancelled)
    levels = levels_from_samples(values, valid, request.get('levels', ''))
    paths = [{'level': level, 'lines': trace_contours(values, valid, positions, level, cancelled)}
             for level in levels]
    return {'status': 'succeeded', 'identity': request['identity'], 'levels': levels,
            'paths': paths, 'valid_count': int(valid.sum()), 'sample_count': int(valid.size)}
