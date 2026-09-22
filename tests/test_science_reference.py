"""Independent Gaussian cubegen / Fortran results distributed by ChemTools."""
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np
from iodata import load_one
from gbasis.wrappers import from_iodata
from gbasis.integrals.overlap import overlap_integral
from gbasis.evals.eval import evaluate_basis
from gbasis.evals.density import evaluate_density
from gbasis.evals.electrostatic_potential import electrostatic_potential

DATA = Path(__file__).parent / 'data/chemtools'
METRICS = {}


class GaussianReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in json.loads((DATA / 'sources.json').read_text(encoding='utf-8')):
            assert hashlib.sha256((DATA / item['file']).read_bytes()).hexdigest() == item['sha256']
        cls.mol = load_one(str(DATA / 'ch4_uhf_ccpvdz.fchk'))
        cls.basis = from_iodata(cls.mol)
        cls.dm = sum((c * o) @ c.T for c, o in (
            (cls.mol.mo.coeffsa, cls.mol.mo.occsa), (cls.mol.mo.coeffsb, cls.mol.mo.occsb)))

    def test_cubegen_density_and_esp(self):
        with np.load(DATA / 'data_cubegen_g09_C01_ch4_uhf_ccpvdz.npz', allow_pickle=False) as ref:
            points = ref['points']
            rho = evaluate_density(self.dm, self.basis, points)
            esp = electrostatic_potential(self.basis, self.dm, points,
                                          self.mol.atcoords, self.mol.atnums.astype(float))
            for key, actual, expected in [('density', rho, ref['dens']), ('esp', esp, ref['esp'])]:
                METRICS[key + '_max_abs_error'] = float(np.max(np.abs(actual - expected)))
                np.testing.assert_allclose(actual, expected, rtol=0, atol=1.5e-5)
            printed_dm = self.mol.one_rdms['scf']
            rho_printed = evaluate_density(printed_dm, self.basis, points)
            np.testing.assert_allclose(rho_printed, ref['dens'], rtol=0, atol=1.5e-5)

    def test_fortran_signed_molecular_orbitals(self):
        with np.load(DATA / 'data_fortran_ch4_uhf_ccpvdz.npz', allow_pickle=False) as ref:
            np.testing.assert_array_equal(self.mol.atcoords, ref['coords'])
            ao = evaluate_basis(self.basis, ref['points'])
            for spin, coefficients in [('alpha', self.mol.mo.coeffsa), ('beta', self.mol.mo.coeffsb)]:
                for source_number in (8, 9):
                    actual = coefficients[:, source_number - 1] @ ao
                    expected = ref[f'orb_{source_number:02d}'].reshape(-1)
                    METRICS[f'{spin}_mo{source_number}_max_abs_error'] = float(np.max(np.abs(actual - expected)))
                    np.testing.assert_allclose(actual, expected, rtol=0, atol=1.5e-6)

    def test_electron_count_and_orbital_normalization(self):
        overlap = overlap_integral(self.basis)
        for c in (self.mol.mo.coeffsa, self.mol.mo.coeffsb):
            np.testing.assert_allclose(c.T @ overlap @ c, np.eye(c.shape[1]), rtol=0, atol=2e-7)
        np.testing.assert_allclose(np.trace(self.dm @ overlap), self.mol.nelec, atol=2e-6)
        METRICS['electron_count'] = float(np.trace(self.dm @ overlap))


if __name__ == '__main__':
    unittest.main()
