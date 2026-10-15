"""Local-coordinate annotation geometry, independent of Blender and materials."""
import math

import numpy as np

from .measurements import measure

_EPSILON = 1e-12


def distance_dashes(first, second, dash_length=.1):
    """Equal dash/gap lengths, a dash at each end, mirror symmetry about midpoint."""
    first, second = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
    if first.shape != (3,) or second.shape != (3,) or not np.isfinite([first, second]).all():
        raise ValueError('Distance dash endpoints must be finite three-dimensional coordinates')
    if not math.isfinite(dash_length) or dash_length <= 0:
        raise ValueError('Dash length must be finite and positive')
    delta = second - first
    length = float(np.linalg.norm(delta))
    if length <= _EPSILON:
        return np.empty((0, 2, 3), dtype=float)
    count = max(1, int(math.floor((length / dash_length + 1) / 2 + .5)))
    intervals = 2 * count - 1
    fractions = np.arange(intervals + 1, dtype=float) / intervals
    return np.array([[first + delta * fractions[index], first + delta * fractions[index + 1]]
                     for index in range(0, intervals, 2)])


def _perpendicular(vector):
    axis = np.eye(3)[int(np.argmin(np.abs(vector)))]
    normal = np.cross(vector, axis)
    return normal / np.linalg.norm(normal)


def _arc(center, first, normal, angle, radius, resolution):
    if not math.isfinite(radius) or radius <= 0 or type(resolution) is not int or resolution < 2:
        raise ValueError('Arc radius and resolution must be finite and positive')
    if abs(angle) <= _EPSILON:
        return np.empty((0, 3), dtype=float)
    # A rigid transform may move an exact step boundary by floating-point noise.
    count = max(2, int(math.ceil(abs(angle) / math.pi * resolution - 1e-12)) + 1)
    steps = np.linspace(0., angle, count)
    tangent = np.cross(normal, first)
    return (np.asarray(center)[None, :] + radius *
            (np.cos(steps)[:, None] * first + np.sin(steps)[:, None] * tangent))


def angle_arc(points, radius=.5, resolution=64):
    """ABC angle centred on B; straight angles use a deterministic display plane."""
    coords = np.asarray(points, dtype=float)
    if coords.shape != (3, 3):
        raise ValueError('Angle arc needs three ordered points')
    angle = math.radians(measure('ANGLE', coords, [1, 2, 3]))
    first, second = coords[0] - coords[1], coords[2] - coords[1]
    first /= np.linalg.norm(first)
    second /= np.linalg.norm(second)
    normal = np.cross(first, second)
    length = float(np.linalg.norm(normal))
    normal = normal / length if length > _EPSILON else _perpendicular(first)
    return _arc(coords[1], first, normal, angle, radius, resolution)


def dihedral_arc(points, radius=.5, resolution=64):
    """Signed BA/CD projection arc around B→C, centred at the B/C midpoint."""
    coords = np.asarray(points, dtype=float)
    if coords.shape != (4, 3):
        raise ValueError('Dihedral arc needs four ordered points')
    angle = math.radians(measure('DIHEDRAL', coords, [1, 2, 3, 4]))
    axis = coords[2] - coords[1]
    axis /= np.linalg.norm(axis)
    first = coords[0] - coords[1]
    first -= np.dot(first, axis) * axis
    first /= np.linalg.norm(first)
    return _arc((coords[1] + coords[2]) / 2, first, axis, angle, radius, resolution)


def dihedral_planes(points):
    """The actual ABC and BCD atom triangles, not extrapolated display planes."""
    coords = np.asarray(points, dtype=float)
    if coords.shape != (4, 3):
        raise ValueError('Dihedral planes need four ordered points')
    measure('DIHEDRAL', coords, [1, 2, 3, 4])
    return np.array([coords[[0, 1, 2]], coords[[1, 2, 3]]])


def measurement_geometry(kind, positions, numbers, arc_radius=.5, dash_length=.1):
    """Return display primitives; undefined angular steps have no measurement parts."""
    empty = {'dashes': np.empty((0, 2, 3)), 'arc': np.empty((0, 3)),
             'planes': np.empty((0, 3, 3))}
    if kind == 'ATOM':
        return empty
    try:
        measure(kind, positions, numbers)
    except ValueError as error:
        if 'undefined:' not in str(error):
            raise
        return empty
    points = np.asarray(positions, dtype=float)[np.asarray(numbers) - 1]
    if kind == 'DISTANCE':
        return {**empty, 'dashes': distance_dashes(*points, dash_length)}
    if kind == 'ANGLE':
        return {**empty, 'arc': angle_arc(points, arc_radius)}
    if kind == 'DIHEDRAL':
        return {**empty, 'arc': dihedral_arc(points, arc_radius), 'planes': dihedral_planes(points)}
    raise ValueError('Unknown annotation measurement kind')
