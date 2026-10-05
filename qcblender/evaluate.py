"""Chunked real HF/DFT fields; input/output positions use angstrom."""
from dataclasses import dataclass
from importlib.metadata import version

import numpy as np

from .data import BOHR_ANGSTROM, Dataset, orbital_selection
from .readers import wavefunction
from .resources import array_descriptor, field_resources


@dataclass
class Grid:
    origin: np.ndarray
    steps: np.ndarray
    shape: tuple

    def __post_init__(self):
        self.origin = np.asarray(self.origin, dtype=np.float64)
        self.steps = np.asarray(self.steps, dtype=np.float64)
        self.shape = tuple(self.shape)
        if (self.origin.shape != (3,) or self.steps.shape != (3, 3)
                or not np.isfinite(self.origin).all() or not np.isfinite(self.steps).all()):
            raise ValueError('Grid requires finite origin (3,) and step vectors (3,3)')
        if len(self.shape) != 3 or any(type(n) is not int or n < 2 for n in self.shape):
            raise ValueError('Grid shape requires three integers >= 2')
        if abs(np.linalg.det(self.steps)) < 1e-15:
            raise ValueError('Grid step vectors must be linearly independent')

    def points(self, start, stop):
        indices = np.array(np.unravel_index(np.arange(start, stop), self.shape)).T
        return self.origin + indices @ self.steps


def prepare(data):
    from gbasis.wrappers import from_iodata
    data.validate()
    method = (data.metadata.get('method') or '').lower()
    for prefix in ('ro', 'u', 'r'):
        if method.startswith(prefix):
            method = method[len(prefix):]
            break
    # New methods require explicit verification of the canonical SCF orbital identity.
    if method not in {'hf', 'b3lyp', 'pbe', 'pbepbe', 'pbe1pbe', 'blyp', 'bp86',
                      'm06', 'm062x', 'm052x', 'wb97xd', 'cam-b3lyp', 'lsda'}:
        raise ValueError(f'Wavefunction evaluation is not qualified for method {data.metadata.get("method")}')
    mol = wavefunction(data)
    if mol.mo.kind not in ('restricted', 'unrestricted'):
        raise ValueError('Only real restricted/unrestricted orbitals are supported')
    if np.any(mol.atnums <= 0) or not np.array_equal(mol.atcorenums, mol.atnums):
        raise ValueError('ECP and ghost centers are not yet qualified for field evaluation')
    if any(max(s.angmoms) > 4 for s in mol.obasis.shells):
        raise ValueError('Angular momentum above g is not yet qualified')
    if any(np.any(s.exponents <= 0) for s in mol.obasis.shells):
        raise ValueError('Gaussian exponents must be positive')
    if mol.mo.occs is None or mol.mo.coeffs is None:
        raise ValueError('Orbital coefficients and occupations are required')
    if mol.mo.kind == 'restricted' and not np.all(mol.mo.occs == np.round(mol.mo.occs)):
        raise ValueError('Restricted fractional occupations require explicit spin populations')
    basis = from_iodata(mol)
    ca, cb = mol.mo.coeffsa, mol.mo.coeffsb
    pa = (ca * mol.mo.occsa) @ ca.T
    pb = (cb * mol.mo.occsb) @ cb.T
    total, spin = pa + pb, pa - pb
    for key, expected in [('dm_scf', total), ('dm_scf_spin', spin)]:
        if key in data.arrays:
            printed = data.arrays[key]
            if printed.shape != expected.shape or not np.allclose(printed, expected, atol=2e-6, rtol=2e-6):
                raise ValueError(f'{key} disagrees with the SCF orbital occupations')
            if key == 'dm_scf':
                total = printed
            else:
                spin = printed
    pa, pb = (total + spin) / 2, (total - spin) / 2
    return mol, basis, pa, pb


def evaluate_points(data, points_angstrom, quantity, spin='alpha', orbital=1, nuclear_radius_bohr=0.02):
    points = np.asarray(points_angstrom, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError('Field points must be a finite (N,3) array in angstrom')
    mol, basis, pa, pb = prepare(data)
    return _points(mol, basis, pa, pb, points / BOHR_ANGSTROM, quantity, spin, orbital, nuclear_radius_bohr)


def _points(mol, basis, pa, pb, points, quantity, spin, orbital, radius):
    from gbasis.evals.eval import evaluate_basis
    from gbasis.evals.electrostatic_potential import electrostatic_potential
    valid = np.ones(len(points), dtype=bool)
    if quantity == 'electrostatic_potential':
        if not np.isfinite(radius) or radius <= 0:
            raise ValueError('ESP exclusion radius must be positive and finite')
        for center in mol.atcoords:
            valid &= np.linalg.norm(points - center, axis=1) >= radius
        values = np.zeros(len(points))
        if valid.any():
            values[valid] = electrostatic_potential(basis, pa + pb, points[valid],
                                                    mol.atcoords, mol.atnums.astype(float))
    else:
        ao = evaluate_basis(basis, points, screen_basis=False)
        if quantity == 'orbital_amplitude':
            if spin not in ('alpha', 'beta'):
                raise ValueError('Orbital spin must be alpha or beta')
            coefficients = mol.mo.coeffsa if spin == 'alpha' else mol.mo.coeffsb
            if type(orbital) is not int or not 1 <= orbital <= coefficients.shape[1]:
                raise ValueError('Orbital source number is outside the available range')
            values = coefficients[:, orbital - 1] @ ao
        elif quantity in ('electron_number_density', 'spin_density', 'alpha_density', 'beta_density'):
            matrix = {'electron_number_density': pa + pb, 'spin_density': pa - pb,
                      'alpha_density': pa, 'beta_density': pb}[quantity]
            values = np.einsum('mi,mn,ni->i', ao, matrix, ao, optimize=True)
        else:
            raise ValueError('Unsupported field quantity: ' + str(quantity))
    if not np.isfinite(values).all():
        raise ArithmeticError('Non-finite field values returned by the scientific backend')
    return values, valid


def evaluate_field(data, grid, quantity, spin='alpha', orbital=1, memory_mb=512,
                   nuclear_radius_bohr=0.02, cancelled=None, progress=None):
    resources = field_resources({name: array_descriptor(array) for name, array in data.arrays.items()},
                                grid.shape, data.arrays['mo_coeffs'].shape[0], quantity, memory_mb)
    count, chunk = resources['voxel_count'], resources['chunk']
    mol, basis, pa, pb = prepare(data)
    values, valid = np.empty(count), np.empty(count, dtype=bool)
    for start in range(0, count, chunk):
        if cancelled is not None and cancelled():
            raise InterruptedError('Field evaluation cancelled')
        stop = min(start + chunk, count)
        points = grid.points(start, stop) / BOHR_ANGSTROM
        values[start:stop], valid[start:stop] = _points(mol, basis, pa, pb, points, quantity, spin, orbital,
                                                       nuclear_radius_bohr)
        if progress is not None:
            progress(stop / count)
    units = {'orbital_amplitude': 'bohr^-3/2', 'electron_number_density': 'electron/bohr^3',
             'spin_density': 'electron/bohr^3', 'alpha_density': 'electron/bohr^3',
             'beta_density': 'electron/bohr^3', 'electrostatic_potential': 'hartree/e'}
    field = {'quantity': quantity, 'unit': units[quantity], 'array': 'field_values',
             'valid_mask': 'field_valid', 'origin': grid.origin.tolist(), 'steps': grid.steps.tolist(),
             'shape': list(grid.shape), 'coordinate_unit': 'angstrom',
             'method': data.metadata['method'], 'density_level': 'scf',
             'density_source': {key: 'printed' if key in data.arrays else 'orbital_occupations'
                                for key in ('dm_scf', 'dm_scf_spin')},
             'backend': 'qc-gbasis ' + version('qc-gbasis'),
             'source_sha256': data.metadata['source']['sha256'],
             'spin': {'orbital_amplitude': spin, 'spin_density': 'alpha-minus-beta',
                      'alpha_density': 'alpha', 'beta_density': 'beta'}.get(quantity, 'total'),
             'orbital_source_number': orbital if quantity == 'orbital_amplitude' else None,
             'nuclear_exclusion_radius_bohr': nuclear_radius_bohr if quantity == 'electrostatic_potential' else None,
             'memory_budget_mb': memory_mb}
    metadata = dict(data.metadata, fields=[field])
    if quantity == 'orbital_amplitude':
        field['orbital'] = orbital_selection(data, spin, number=orbital)
    arrays = dict(data.arrays, field_values=values.reshape(grid.shape), field_valid=valid.reshape(grid.shape))
    return Dataset(metadata, arrays)
