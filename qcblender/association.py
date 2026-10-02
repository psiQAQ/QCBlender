"""Explicit atom-order-preserving geometry association, without changing scientific data."""
import numpy as np


def require_static_geometry(data):
    if data.metadata.get('trajectory'):
        raise ValueError('Multi-frame XYZ requires a single-frame source for scientific association')


def compare_sources(reference, moving, allow_rigid=False, tolerance_angstrom=1e-3):
    reference.validate()
    moving.validate()
    require_static_geometry(reference)
    require_static_geometry(moving)
    if not np.isfinite(tolerance_angstrom) or tolerance_angstrom <= 0:
        raise ValueError('Association tolerance must be positive and finite')
    if not np.array_equal(reference.arrays['atomic_numbers'], moving.arrays['atomic_numbers']):
        raise ValueError('Atom identities/order differ; an explicit atom mapping is required')
    for key in ('charge', 'multiplicity'):
        first, second = reference.metadata.get(key), moving.metadata.get(key)
        if first is not None and second is not None and first != second:
            raise ValueError(f'Calculation {key} differs')
    target, source = reference.arrays['positions'], moving.arrays['positions']
    if len(source) == 0:
        raise ValueError('Geometry association requires atoms')
    rotation, translation = np.eye(3), np.zeros(3)
    rank = int(np.linalg.matrix_rank(source - source.mean(axis=0)))
    if allow_rigid:
        if rank < 2:
            raise ValueError('Linear/single-center geometry does not determine a unique orbital/vector rotation')
        u, _, vt = np.linalg.svd((source - source.mean(axis=0)).T @ (target - target.mean(axis=0)))
        correction = np.diag([1., 1., np.linalg.det(u @ vt)])
        rotation = u @ correction @ vt
        translation = target.mean(axis=0) - source.mean(axis=0) @ rotation
    errors = np.linalg.norm(source @ rotation + translation - target, axis=1)
    if errors.max() > tolerance_angstrom:
        raise ValueError(f'Different geometries: maximum atom displacement {errors.max():.6g} angstrom')
    return {'reference_source': reference.metadata['source']['sha256'],
            'moving_source': moving.metadata['source']['sha256'],
            'atom_mapping': list(range(len(source))), 'rotation_rows': rotation.tolist(),
            'translation_angstrom': translation.tolist(), 'max_error_angstrom': float(errors.max()),
            'tolerance_angstrom': tolerance_angstrom, 'status': 'geometry_matched',
            'property_compatibility': 'not_inferred', 'transform_convention': 'source @ rotation + translation'}
