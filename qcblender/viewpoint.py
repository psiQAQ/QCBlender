"""Deterministic camera orientation from displayed geometry, without Blender.

Bases contain world-space camera right, up and back vectors as rows. The camera
looks along local -Z. UNOBSTRUCTED estimates visibility of sampled opaque point
geometry; it does not model surfaces, materials, transparency or volume optics.
"""
from dataclasses import dataclass
import math

import numpy as np


_MAX_SAMPLES = 4096
_BLOCK_SIZE = 65536
_GRID_SIZE = 64
_EIGEN_TOL = 1e-5


@dataclass(frozen=True)
class OrientationResult:
    basis: np.ndarray
    method: str
    message: str = ""
    score: float = 0.0


def _reference_basis(reference_basis):
    basis = np.eye(3) if reference_basis is None else np.asarray(reference_basis, dtype=float)
    if (basis.shape != (3, 3) or not np.isfinite(basis).all()
            or not np.allclose(basis @ basis.T, np.eye(3), rtol=0, atol=1e-6)
            or not np.isclose(np.linalg.det(basis), 1.0, rtol=0, atol=1e-6)):
        raise ValueError("reference_basis must be a finite right-handed orthonormal 3x3 basis")
    return basis.copy()


def _geometry(points):
    """Full-data moments in bounded blocks, with a bounded scoring sample."""
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or not len(points):
        raise ValueError("points must be a nonempty Nx3 array")
    lower, upper = np.full(3, np.inf), np.full(3, -np.inf)
    for start in range(0, len(points), _BLOCK_SIZE):
        block = points[start:start + _BLOCK_SIZE]
        if not np.isfinite(block).all():
            raise ValueError("points must contain only finite coordinates")
        lower = np.minimum(lower, block.min(axis=0))
        upper = np.maximum(upper, block.max(axis=0))
    # Divide before subtraction: even opposite coordinates near float max are safe.
    magnitude = max(float(np.max(np.abs(lower))), float(np.max(np.abs(upper))))
    magnitude = magnitude or 1.0
    lo, hi = lower / magnitude, upper / magnitude
    center = (lo + hi) * 0.5
    span = float(np.max(hi - lo)) or 1.0
    total, moment = np.zeros(3), np.zeros((3, 3))
    for start in range(0, len(points), _BLOCK_SIZE):
        block = (points[start:start + _BLOCK_SIZE] / magnitude - center) / span
        total += block.sum(axis=0)
        moment += block.T @ block
    mean = total / len(points)
    covariance = moment / len(points) - np.outer(mean, mean)
    covariance = (covariance + covariance.T) * 0.5
    indices = np.linspace(0, len(points) - 1, min(len(points), _MAX_SAMPLES), dtype=np.int64)
    sample = (points[indices] / magnitude - center) / span - mean
    # All candidates use this same radius, never their own projected fit scale.
    radius = float(np.linalg.norm(sample, axis=1).max())
    if radius > 0:
        sample /= radius
    return covariance, sample, (magnitude, center, span)


def _project_preference(projector, preferred, alternatives):
    vector = projector @ preferred
    norm = np.linalg.norm(vector)
    if norm < 1e-8:
        projected = alternatives @ projector
        vector = projected[int(np.argmax(np.linalg.norm(projected, axis=1)))]
        norm = np.linalg.norm(vector)
    return vector / norm


def _align_signs(basis, reference, keep_back=False):
    signs = ((1, 1, 1), (-1, -1, 1)) if keep_back else (
        (1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1))
    best, best_alignment = basis, -np.inf
    for sign in signs:
        candidate = basis * np.asarray(sign)[:, None]
        alignment = float(np.sum(candidate * reference))
        if alignment > best_alignment + 1e-12:
            best, best_alignment = candidate, alignment
    return best


def _pca_basis(covariance, reference, aspect):
    values, vectors = np.linalg.eigh(covariance)
    tolerance = _EIGEN_TOL * max(float(values[-1]), np.finfo(float).tiny)
    if values[-1] - values[0] <= tolerance:
        return reference.copy()
    low = vectors[:, values - values[0] <= tolerance]
    high = vectors[:, values[-1] - values <= tolerance]
    back = _project_preference(low @ low.T, reference[2], reference)
    long_index = 0 if aspect >= 1 else 1
    long = _project_preference(high @ high.T, reference[long_index], reference)
    # Distinct eigenspaces are orthogonal; remove numerical roundoff explicitly.
    long -= np.dot(long, back) * back
    long /= np.linalg.norm(long)
    if long_index == 0:
        basis = np.array([long, np.cross(back, long), back])
    else:
        basis = np.array([np.cross(long, back), long, back])
    return _align_signs(basis, reference)


def _basis_for_back(back, covariance, reference, aspect):
    back = back / np.linalg.norm(back)
    long_index = 0 if aspect >= 1 else 1
    first = _project_preference(np.eye(3) - np.outer(back, back),
                                reference[long_index], reference)
    second = np.cross(back, first)
    plane = np.array([first, second])
    values, vectors = np.linalg.eigh(plane @ covariance @ plane.T)
    long = first
    if values[-1] - values[0] > _EIGEN_TOL * max(float(values[-1]), np.finfo(float).tiny):
        long = vectors[:, -1] @ plane
    if long_index == 0:
        basis = np.array([long, np.cross(back, long), back])
    else:
        basis = np.array([np.cross(long, back), long, back])
    return _align_signs(basis, reference, keep_back=True)


def _visibility_score(sample, basis):
    projected = sample @ basis.T
    cells = np.clip(((projected[:, :2] + 1.0) * (_GRID_SIZE / 2)).astype(np.int64),
                    0, _GRID_SIZE - 1)
    keys = cells[:, 0] + _GRID_SIZE * cells[:, 1]
    front = np.full(_GRID_SIZE ** 2, -np.inf)
    np.maximum.at(front, keys, projected[:, 2])
    # Points in a thin front layer share visibility rather than self-occluding.
    visible = np.count_nonzero(projected[:, 2] >= front[keys] - 1.0 / _GRID_SIZE)
    coverage = np.count_nonzero(np.isfinite(front))
    return float((0.7 * visible + 0.3 * coverage) / len(sample))


def _fit_frame_axes(points, basis, normalization, covariance, reference, aspect):
    """Resolve portrait/landscape using actual full-data projected spans."""
    values = np.linalg.eigvalsh(covariance)
    if values[-1] - values[0] <= _EIGEN_TOL * max(float(values[-1]), np.finfo(float).tiny):
        return basis  # Fully ambiguous geometry keeps the reference orientation.
    magnitude, center, span = normalization
    lower, upper = np.full(2, np.inf), np.full(2, -np.inf)
    for start in range(0, len(points), _BLOCK_SIZE):
        block = (points[start:start + _BLOCK_SIZE] / magnitude - center) / span
        projected = block @ basis[:2].T
        lower = np.minimum(lower, projected.min(axis=0))
        upper = np.maximum(upper, projected.max(axis=0))
    widths = upper - lower
    long_index = 0 if aspect >= 1 else 1
    if widths[1 - long_index] > widths[long_index] + 1e-8 * max(widths):
        basis = np.array([basis[1], -basis[0], basis[2]])
        basis = _align_signs(basis, reference, keep_back=True)
    return basis


def choose_orientation(points, mode="PCA", reference_basis=None, aspect=1.0):
    """Choose a proper camera basis from finite Nx3 BODY geometry coordinates.

    ``PCA`` looks down the least-variance axis, with the longer projected span
    along the longer frame dimension. Eigenvalues within 1e-5 of the largest variance are
    treated as ambiguous and resolved against ``reference_basis`` (identity by
    default). ``UNOBSTRUCTED`` searches 128 spherical directions and two small
    refinement rings, retaining PCA/current baselines on ties. Its score is a
    unitless approximation from depth-grid visibility and projected coverage.

    Moments use every point in bounded blocks; scoring uses at most 4096 evenly
    spaced input rows. Input arrays are not mutated. Raises ValueError for empty,
    malformed or nonfinite geometry, nonpositive aspect or an improper basis.
    """
    if mode not in ("PCA", "UNOBSTRUCTED"):
        raise ValueError("mode must be PCA or UNOBSTRUCTED")
    try:
        aspect = float(aspect)
    except (TypeError, ValueError) as exc:
        raise ValueError("aspect must be finite and positive") from exc
    if not math.isfinite(aspect) or aspect <= 0:
        raise ValueError("aspect must be finite and positive")
    reference = _reference_basis(reference_basis)
    points = np.asarray(points, dtype=float)
    covariance, sample, normalization = _geometry(points)
    pca = _pca_basis(covariance, reference, aspect)
    pca = _fit_frame_axes(points, pca, normalization, covariance, reference, aspect)
    best, score = pca, _visibility_score(sample, pca)
    if mode == "PCA" or not np.any(covariance):
        return OrientationResult(best, mode, score=score)

    def consider(candidate):
        nonlocal best, score
        candidate_score = _visibility_score(sample, candidate)
        # A small improvement threshold prevents arbitrary swaps on numerical ties.
        if candidate_score > score + 1e-4:
            best, score = candidate, candidate_score

    consider(reference)
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    for index in range(128):
        z = 1.0 - 2.0 * (index + 0.5) / 128
        radius = math.sqrt(max(0.0, 1.0 - z * z))
        angle = index * golden_angle
        local = np.array([radius * math.cos(angle), radius * math.sin(angle), z])
        consider(_basis_for_back(local @ pca, covariance, pca, aspect))
    for step in (0.12, 0.04):
        anchor = best.copy()
        for index in range(8):
            angle = index * math.pi / 4
            back = anchor[2] + step * (math.cos(angle) * anchor[0] + math.sin(angle) * anchor[1])
            consider(_basis_for_back(back, covariance, pca, aspect))
    best = _fit_frame_axes(points, best, normalization, covariance, reference, aspect)
    return OrientationResult(best, mode, score=_visibility_score(sample, best))
