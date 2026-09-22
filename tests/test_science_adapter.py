import json
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.data import BOHR_ANGSTROM, load_dataset, save_dataset, orbital_selection
from qcblender.evaluate import Grid, evaluate_field, evaluate_points
from qcblender.evaluate import prepare
from qcblender.readers import read_source, wavefunction
from qcblender.association import compare_sources

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).parent / 'data/chemtools'


class ScientificAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_source(DATA / 'ch4_uhf_ccpvdz.fchk')

    def test_normalized_roundtrip_matches_independent_fields(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            save_dataset(self.data, directory)
            loaded = load_dataset(directory)
            for name, array in self.data.arrays.items():
                np.testing.assert_array_equal(array, loaded.arrays[name])
            with np.load(DATA / 'data_cubegen_g09_C01_ch4_uhf_ccpvdz.npz', allow_pickle=False) as ref:
                for quantity, name in [('electron_number_density', 'dens'), ('electrostatic_potential', 'esp')]:
                    values, valid = evaluate_points(loaded, ref['points'] * BOHR_ANGSTROM, quantity)
                    self.assertTrue(valid.all())
                    np.testing.assert_allclose(values, ref[name], rtol=0, atol=1.5e-5)
            with np.load(DATA / 'data_fortran_ch4_uhf_ccpvdz.npz', allow_pickle=False) as ref:
                grid = Grid([-3 * BOHR_ANGSTROM] * 3, np.eye(3) * 3 * BOHR_ANGSTROM, (3, 3, 3))
                field = evaluate_field(loaded, grid, 'orbital_amplitude', orbital=8)
                np.testing.assert_allclose(field.arrays['field_values'].ravel(), ref['orb_08'].ravel(), atol=1.5e-6, rtol=0)

    def test_invalid_grid_budget_and_cancellation(self):
        with self.assertRaisesRegex(ValueError, 'independent'):
            Grid([0, 0, 0], np.zeros((3, 3)), (3, 3, 3))
        grid = Grid([0, 0, 0], np.eye(3), (1000, 1000, 1000))
        with self.assertRaises(MemoryError):
            evaluate_field(self.data, grid, 'electron_number_density', memory_mb=32)
        small = Grid([0, 0, 0], np.eye(3), (3, 3, 3))
        with self.assertRaises(InterruptedError):
            evaluate_field(self.data, small, 'orbital_amplitude', cancelled=lambda: True)
        with self.assertRaisesRegex(ValueError, 'source number'):
            evaluate_points(self.data, [[0, 1, 2]], 'orbital_amplitude', orbital=0)

    def test_esp_nuclei_are_masked_not_physical_zero(self):
        values, valid = evaluate_points(self.data, self.data.arrays['positions'], 'electrostatic_potential')
        self.assertFalse(valid.any())
        self.assertTrue(np.isfinite(values).all())

    def test_open_shell_and_spherical_cartesian_basis_invariants(self):
        from gbasis.integrals.overlap import overlap_integral
        fixture_dir = Path(__file__).parent / 'data/iodata'
        for item in json.loads((fixture_dir / 'sources.json').read_text(encoding='utf-8')):
            self.assertEqual(hashlib.sha256((fixture_dir / item['file']).read_bytes()).hexdigest(), item['sha256'])
        for name in ('water_sto3g_hf_g03.fchk', 'ch3_hf_sto3g.fchk', 'ch3_rohf_sto3g_g03.fchk',
                     'o2_cc_pvtz_pure.fchk', 'o2_cc_pvtz_cart.fchk'):
            with self.subTest(source=name):
                data = read_source(Path(__file__).parent / 'data/iodata' / name)
                mol, basis, pa, pb = prepare(data)
                overlap = overlap_integral(basis)
                np.testing.assert_allclose(np.trace((pa + pb) @ overlap), data.metadata['electron_count'], atol=2e-5)
                np.testing.assert_allclose(np.trace((pa - pb) @ overlap), data.metadata['spin_polarization'], atol=2e-5)
                for coefficients in (mol.mo.coeffsa, mol.mo.coeffsb):
                    np.testing.assert_allclose(coefficients.T @ overlap @ coefficients,
                                               np.eye(coefficients.shape[1]), rtol=0, atol=2e-6)
                if name.startswith('ch3'):
                    spin, _ = evaluate_points(data, [[0.3, 0.2, 0.1]], 'spin_density')
                    alpha, _ = evaluate_points(data, [[0.3, 0.2, 0.1]], 'alpha_density')
                    beta, _ = evaluate_points(data, [[0.3, 0.2, 0.1]], 'beta_density')
                    total, _ = evaluate_points(data, [[0.3, 0.2, 0.1]], 'electron_number_density')
                    np.testing.assert_allclose(alpha + beta, total, atol=1e-12)
                    np.testing.assert_allclose(alpha - beta, spin, atol=1e-12)
                    self.assertGreater(abs(spin[0]), 1e-6)
                    self.assertEqual(data.metadata['spin_polarization'], 1)

    def test_checksum_and_path_traversal_fail(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = save_dataset(self.data, directory)
            manifest = json.loads(path.read_text(encoding='utf-8'))
            manifest['arrays']['positions']['path'] = '../outside.npy'
            path.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                load_dataset(directory)
            path = save_dataset(self.data, directory)
            manifest = json.loads(path.read_text(encoding='utf-8'))
            manifest['arrays']['positions']['sha256'] = '0' * 64
            path.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                load_dataset(directory)

    def test_real_dft_rectangular_orbitals_and_explicit_high_l_limit(self):
        from gbasis.integrals.overlap import overlap_integral
        for relative in ('gbasis/ch2o_q_0.fchk', 'iodata/li_h_3-21G_hf_g09.fchk', 'iodata/li2_g09_nbasis_indep.fchk'):
            data = read_source(ROOT / 'tests/data' / relative)
            mol, basis, pa, pb = prepare(data)
            overlap = overlap_integral(basis)
            for coefficients in (mol.mo.coeffsa, mol.mo.coeffsb):
                np.testing.assert_allclose(coefficients.T @ overlap @ coefficients,
                                           np.eye(coefficients.shape[1]), atol=2e-6, rtol=0)
            np.testing.assert_allclose(np.trace((pa + pb) @ overlap), data.metadata['electron_count'], atol=2e-5)
            values, mask = evaluate_points(data, [[1., 2., 3.]], 'electron_number_density')
            self.assertTrue(mask.all())
            self.assertGreater(values[0], 0)
            if 'li2_' in relative:
                self.assertEqual(mol.mo.coeffs.shape, (38, 37))
            if 'ch2o' in relative:
                self.assertEqual(data.metadata['method'].upper(), 'UB3LYP')
        for kind in ('sph', 'cart'):
            data = read_source(ROOT / f'tests/data/gbasis/h2o_hf_ccpv5z_{kind}.fchk')
            with self.assertRaisesRegex(ValueError, 'above g'):
                prepare(data)

    def test_different_geometry_cannot_share_fields(self):
        from copy import deepcopy
        moving = deepcopy(self.data)
        moving.arrays['positions'] = moving.arrays['positions'] + [1, 2, 3]
        with self.assertRaisesRegex(ValueError, 'Different geometries'):
            compare_sources(self.data, moving)
        result = compare_sources(self.data, moving, allow_rigid=True)
        np.testing.assert_allclose(result['translation_angstrom'], [-1, -2, -3])
        moving.arrays['positions'][1, 0] += 0.1
        with self.assertRaisesRegex(ValueError, 'Different geometries'):
            compare_sources(self.data, moving, allow_rigid=True)

    def test_orbital_selection_uses_spin_occupations_and_available_columns(self):
        from copy import deepcopy
        data = read_source(ROOT / 'tests/data/iodata/ch3_rohf_sto3g_g03.fchk')
        self.assertEqual(orbital_selection(data, 'alpha', 'HOMO')['source_number'], 5)
        self.assertEqual(orbital_selection(data, 'beta', 'HOMO')['source_number'], 4)
        self.assertEqual(orbital_selection(data, 'alpha', 'LUMO')['source_number'], 6)
        self.assertEqual(orbital_selection(data, 'beta', 'LUMO')['source_number'], 5)
        ambiguous = deepcopy(data)
        ambiguous.arrays.pop('mo_occs_aminusb', None)
        ambiguous.arrays['mo_occs'][0] = 1.5
        with self.assertRaisesRegex(ValueError, 'Fractional'):
            orbital_selection(ambiguous, 'alpha', 'HOMO')
        rectangular = read_source(ROOT / 'tests/data/iodata/li2_g09_nbasis_indep.fchk')
        self.assertEqual(orbital_selection(rectangular, 'alpha', number=37)['source_number'], 37)
        with self.assertRaisesRegex(ValueError, 'available range'):
            orbital_selection(rectangular, 'alpha', number=38)


if __name__ == '__main__':
    unittest.main()
