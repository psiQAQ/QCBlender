"""Structural measurements from real, source-ordered coordinates in angstrom."""

import math

import numpy as np


ATOM_COUNTS = {'DISTANCE': 2, 'ANGLE': 3, 'DIHEDRAL': 4}


def measure(kind, positions, source_atom_numbers):
    """Return angstrom or degrees; dihedral sign follows B→C and BA/CD projections."""
    count = ATOM_COUNTS.get(kind)
    numbers = list(source_atom_numbers)
    coords = np.asarray(positions, dtype=np.float64)
    if (count is None or len(numbers) != count or any(type(n) is not int for n in numbers)
            or len(set(numbers)) != count or coords.ndim != 2 or coords.shape[1] != 3
            or any(n < 1 or n > len(coords) for n in numbers)):
        raise ValueError('Choose distinct, existing source atom numbers in measurement order')
    points = coords[np.array(numbers) - 1]
    if not np.isfinite(points).all():
        raise ValueError('Measurement coordinates must be finite')
    if kind == 'DISTANCE':
        distance = float(np.linalg.norm(points[1] - points[0]))
        if distance <= 1e-12:
            raise ValueError('Distance is undefined: coincident atoms')
        return distance
    first, second = points[0] - points[1], points[2] - points[1]
    if kind == 'ANGLE':
        if min(np.linalg.norm(first), np.linalg.norm(second)) <= 1e-12:
            raise ValueError('Angle is undefined: zero-length arm')
        return math.degrees(math.atan2(float(np.linalg.norm(np.cross(first, second))),
                                       float(np.dot(first, second))))
    axis = points[2] - points[1]
    axis_length = float(np.linalg.norm(axis))
    if axis_length <= 1e-12:
        raise ValueError('Dihedral is undefined: zero-length central bond')
    axis /= axis_length
    last = points[3] - points[2]
    v = first - np.dot(first, axis) * axis
    w = last - np.dot(last, axis) * axis
    if min(np.linalg.norm(v), np.linalg.norm(w)) <= 1e-12:
        raise ValueError('Dihedral is undefined: terminal arm lies on central axis')
    angle = math.degrees(math.atan2(float(np.dot(np.cross(v, w), axis)), float(np.dot(v, w))))
    return 180.0 if angle <= -180.0 else angle
