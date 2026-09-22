"""Normalize Gaussian data while retaining method and source identities."""
import hashlib
from importlib.metadata import version
from pathlib import Path
import warnings
import re

import numpy as np

from .data import BOHR_ANGSTROM, Dataset


def source_record(path, format_name, parser):
    return {'filename': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'format': format_name, 'parser': parser}


def read_fchk(path):
    from iodata import load_one
    path = Path(path)
    declared = 0
    size = path.stat().st_size
    with path.open(encoding='ascii', errors='strict') as stream:
        for line in stream:
            match = re.search(r'\bN=\s*(\d+)\s*$', line)
            if match:
                count = int(match[1])
                declared += count
                if count > size or declared * 8 > 512 * 1024**2:
                    raise MemoryError('FCHK declared arrays exceed file bounds or import budget')
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        mol = load_one(str(path), fmt='fchk')
    arrays = {'atomic_numbers': np.asarray(mol.atnums, dtype=np.int32),
              'positions': np.asarray(mol.atcoords, dtype=np.float64) * BOHR_ANGSTROM,
              'core_charges': np.asarray(mol.atcorenums, dtype=np.float64)}
    metadata = {'source': source_record(path, 'gaussian-fchk', 'qc-iodata ' + version('qc-iodata')),
                'coordinate_unit': 'angstrom', 'source_coordinate_unit': 'bohr',
                'title': mol.title, 'method': mol.lot, 'basis_name': mol.obasis_name,
                'calculation_status': 'unknown', 'charge': float(mol.charge),
                'spin_polarization': float(mol.spinpol), 'electron_count': float(mol.nelec),
                'diagnostics': [str(w.message) for w in captured],
                'energies': [], 'charges': [], 'fields': []}
    if mol.energy is not None:
        metadata['energies'].append({'kind': 'electronic_total', 'value_hartree': float(mol.energy),
                                     'method': mol.lot, 'role': 'source_total',
                                     'source_field': 'Total Energy', 'validity': 'unknown'})
    for method, values in mol.atcharges.items():
        key = 'charge_' + method
        arrays[key] = np.asarray(values, dtype=np.float64)
        metadata['charges'].append({'method': method, 'array': key, 'unit': 'e'})
    dipole = mol.moments.get((1, 'c'))
    if dipole is not None:
        arrays['dipole'] = np.asarray(dipole, dtype=np.float64)
        metadata['dipole'] = {'array': 'dipole', 'unit': 'e*bohr', 'origin': 'source coordinate origin'}
    if mol.mo is not None and mol.obasis is not None:
        metadata['orbitals'] = {'kind': mol.mo.kind, 'norba': mol.mo.norba, 'norbb': mol.mo.norbb,
                                'energy_unit': 'hartree', 'source_number_base': 1}
        for name in ('coeffs', 'occs', 'energies', 'occs_aminusb'):
            value = getattr(mol.mo, name)
            if value is not None:
                arrays['mo_' + name] = np.asarray(value, dtype=np.float64)
        metadata['basis'] = {'primitive_normalization': mol.obasis.primitive_normalization,
                             'conventions': [[am, kind, names] for (am, kind), names in mol.obasis.conventions.items()],
                             'shells': []}
        for index, shell in enumerate(mol.obasis.shells):
            exps, coeffs = f'shell_{index}_exponents', f'shell_{index}_coeffs'
            arrays[exps] = np.asarray(shell.exponents, dtype=np.float64)
            arrays[coeffs] = np.asarray(shell.coeffs, dtype=np.float64)
            metadata['basis']['shells'].append({'center': int(shell.icenter),
                                               'angular_momenta': list(map(int, shell.angmoms)),
                                               'kinds': list(shell.kinds), 'exponents': exps, 'coeffs': coeffs})
    metadata['density_matrices'] = []
    for kind, matrix in mol.one_rdms.items():
        key = 'dm_' + kind
        arrays[key] = np.asarray(matrix, dtype=np.float64)
        metadata['density_matrices'].append({'kind': kind, 'array': key})
    result = Dataset(metadata, arrays)
    infer_bonds(result)
    result.validate()
    return result


def infer_bonds(data):
    import periodictable
    from scipy.spatial import cKDTree
    positions = data.arrays['positions']
    radii = np.array([getattr(periodictable.elements[int(z)], 'covalent_radius', None) or 0
                      for z in data.arrays['atomic_numbers']], dtype=float)
    if len(positions) == 0 or not radii.any():
        pairs = np.empty((0, 2), dtype=np.int32)
    else:
        pairs = cKDTree(positions).query_pairs(2 * radii.max() * 1.2, output_type='ndarray')
        if len(pairs):
            distance = np.linalg.norm(positions[pairs[:, 0]] - positions[pairs[:, 1]], axis=1)
            summed = radii[pairs[:, 0]] + radii[pairs[:, 1]]
            keep = ((distance > 0.1) & (distance <= 1.2 * summed)
                    & (radii[pairs[:, 0]] > 0) & (radii[pairs[:, 1]] > 0))
            pairs = pairs[keep]
    data.arrays['bonds'] = np.asarray(pairs, dtype=np.int32).reshape(-1, 2)
    data.metadata['bonds'] = {'source': 'distance_inferred', 'factor': 1.2,
                              'radii': 'periodictable ' + version('periodictable'), 'unit': 'angstrom'}


def wavefunction(data):
    """Reconstruct the backend adapter from normalized records, without a source file."""
    from iodata import IOData
    from iodata.basis import MolecularBasis, Shell
    from iodata.orbitals import MolecularOrbitals
    info = data.metadata['orbitals']
    basis = data.metadata['basis']
    arrays = data.arrays
    shells = [Shell(s['center'], s['angular_momenta'], s['kinds'],
                    arrays[s['exponents']], arrays[s['coeffs']]) for s in basis['shells']]
    return IOData(atnums=arrays['atomic_numbers'], atcoords=arrays['positions'] / BOHR_ANGSTROM,
                  atcorenums=arrays['core_charges'],
                  obasis=MolecularBasis(shells, {(am, kind): names for am, kind, names in basis['conventions']},
                                        basis['primitive_normalization']),
                  mo=MolecularOrbitals(info['kind'], info['norba'], info['norbb'],
                                       arrays.get('mo_occs'), arrays.get('mo_coeffs'), arrays.get('mo_energies'),
                                       occs_aminusb=arrays.get('mo_occs_aminusb')))


def read_source(path, job_index=0):
    path = Path(path)
    if path.stat().st_size > 512 * 1024**2:
        raise MemoryError('Source exceeds the current 512 MiB import limit')
    if path.suffix.lower() in ('.fchk', '.fch'):
        return read_fchk(path)
    if path.suffix.lower() in ('.cube', '.cub'):
        from .cube import read_cube
        return read_cube(path)
    if path.suffix.lower() in ('.log', '.out'):
        from .gaussian_log import read_log
        return read_log(path, job_index)
    raise ValueError(f'Unsupported input format: {path.suffix}')
