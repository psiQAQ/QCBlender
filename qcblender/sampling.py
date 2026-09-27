"""Scalar grid sampling without Blender."""
import itertools

import numpy as np


def sample_point(values, valid, field, position):
    """Trilinear float64 sampling; invalid contributing corners do not become zero."""
    point = (np.asarray(position, dtype=float) - field['origin']) @ np.linalg.inv(np.asarray(field['steps']))
    if not np.isfinite(point).all():
        raise ValueError('Sampling coordinates must be finite')
    shape = np.asarray(values.shape)
    if np.any(point < -1e-7) or np.any(point > shape - 1 + 1e-7):
        raise ValueError('Cursor is outside the field domain')
    point = np.clip(point, 0, shape - 1)
    lower = np.floor(point).astype(int)
    upper = np.minimum(lower + 1, shape - 1)
    fraction = point - lower
    result = 0.
    for corner in itertools.product((0, 1), repeat=3):
        weight = float(np.prod(np.where(corner, fraction, 1 - fraction)))
        if weight <= 1e-14:
            continue
        index = tuple(np.where(corner, upper, lower))
        if not valid[index]:
            raise ValueError('Cursor interpolation intersects an invalid field region')
        result += weight * float(values[index])
    return result
