"""Orthographic framing math, independent of Blender."""

import numpy as np


def fit_orthographic(points, basis, aspect, margin=0.05):
    """Return camera location, ortho scale, and far clip for world-space points.

    ``basis`` has camera right, up, and back unit vectors as its rows.
    Blender's orthographic scale spans the longer render dimension.
    """
    points = np.asarray(points, dtype=float)
    basis = np.asarray(basis, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or not len(points) or not np.isfinite(points).all():
        raise ValueError('Camera framing requires finite world-space points with shape (N, 3)')
    if (basis.shape != (3, 3) or not np.isfinite(basis).all()
            or not np.allclose(basis @ basis.T, np.eye(3), atol=1e-6)):
        raise ValueError('Camera orientation must have three orthonormal axes')
    if not np.isfinite(aspect) or aspect <= 0:
        raise ValueError('Render aspect must be positive and finite')
    if not np.isfinite(margin) or not 0 <= margin < 0.5:
        raise ValueError('Camera margin must be between 0 and 0.5')

    projected = points @ basis.T
    low, high = projected.min(axis=0), projected.max(axis=0)
    span = high - low
    if not np.isfinite(span).all():
        raise ValueError('Camera bounds exceed finite coordinate range')
    usable = 1 - 2 * margin
    scale = max(span[0] / min(1, aspect), span[1] / min(1, 1 / aspect)) / usable
    scale = max(float(scale), 0.001)
    distance = max(float(max(span)), 1.0)
    camera_coordinates = [(low[0] + high[0]) / 2, (low[1] + high[1]) / 2, high[2] + distance]
    location = np.asarray(camera_coordinates) @ basis
    clip_end = max(1000.0, float(span[2] + distance) * 1.05)
    if not np.isfinite(scale) or not np.isfinite(clip_end) or not np.isfinite(location).all():
        raise ValueError('Camera framing exceeds finite coordinate range')
    return location, scale, clip_end
