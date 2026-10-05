"""Qualification and lightweight generation preview without allocating a field grid."""
import hashlib
import math
from pathlib import Path

from .data import Dataset, load_dataset, orbital_selection
from .resources import array_descriptor, field_resources
from .science_identity import scientific_identity


def qualify_dataset(directory, expected_digest, cancelled=lambda: False):
    from .evaluate import prepare
    manifest = Path(directory) / 'manifest.json'

    def check():
        if cancelled():
            raise InterruptedError('Scientific qualification cancelled')
        if hashlib.sha256(manifest.read_bytes()).hexdigest() != expected_digest:
            raise ValueError('Dataset changed during scientific qualification')

    check()
    data = load_dataset(directory)
    identity = scientific_identity()
    try:
        prepare(data)
    except ValueError as error:
        # Storage/layout failures occur outside this boundary. Unsupported science is explicit.
        check()
        return {'eligible': False, 'reason': str(error), 'dataset_sha256': expected_digest,
                'science_sha256': identity['sha256']}
    check()
    preview = {'arrays': {name: array_descriptor(array) for name, array in data.arrays.items()},
               'nbasis': data.arrays['mo_coeffs'].shape[0],
               'bounds': [data.arrays['positions'].min(axis=0).tolist(),
                          data.arrays['positions'].max(axis=0).tolist()],
               'orbitals': data.metadata['orbitals'],
               'orbital_arrays': {name: data.arrays[name].tolist() for name in
                                  ('mo_occs', 'mo_occs_aminusb', 'mo_energies') if name in data.arrays}}
    return {'eligible': True, 'reason': None, 'dataset_sha256': expected_digest,
            'science_sha256': identity['sha256'], 'preview': preview}


def preview_orbital(preview, spin, choice, number):
    import numpy as np
    data = Dataset({'orbitals': preview['orbitals']},
                   {name: np.asarray(value) for name, value in preview['orbital_arrays'].items()})
    return orbital_selection(data, spin, choice, number)


def preview_grid(preview, spacing, padding):
    if not math.isfinite(spacing) or spacing <= 0 or not math.isfinite(padding) or padding < 0:
        raise ValueError('Grid spacing and margin must be finite and positive')
    lower, upper = preview['bounds']
    origin = [value - padding for value in lower]
    shape = [math.ceil((hi - lo + 2 * padding) / spacing) + 1 for lo, hi in zip(lower, upper)]
    return {'origin': origin, 'steps': [[spacing if i == j else 0 for j in range(3)] for i in range(3)],
            'shape': shape}


def preview_resources(preview, grid, quantity, memory_mb, validate=True):
    return field_resources(preview['arrays'], grid['shape'], preview['nbasis'], quantity, memory_mb,
                           validate=validate)
