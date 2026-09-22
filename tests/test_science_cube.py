from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.cube import read_cube
from qcblender.data import BOHR_ANGSTROM

ROOT = Path(__file__).resolve().parents[1]


class CubeReader(unittest.TestCase):
    def test_sheared_non_cubic_multiple_orbitals(self):
        expected = np.fromfunction(lambda i, j, k: i + 10*j + 100*k, (2, 3, 4))
        values = np.stack([expected, -expected - 0.5], axis=-1).ravel()
        text = ('Test two orbitals\nSigned anisotropic grid\n-1 1 2 3\n'
                '2 .2 0 0\n3 .1 .3 0\n4 0 0 .4\n6 6 1 2 3\n2 7 9\n'
                + ' '.join(map(str, values)))
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = Path(directory) / 'test.cube'
            path.write_text(text, encoding='ascii')
            data = read_cube(path)
        np.testing.assert_array_equal(data.arrays['cube_0'], expected)
        np.testing.assert_array_equal(data.arrays['cube_1'], -expected - .5)
        first = data.metadata['fields'][0]
        self.assertEqual(first['orbital_source_number'], 7)
        self.assertEqual(data.metadata['fields'][1]['orbital_source_number'], 9)
        np.testing.assert_allclose(first['origin'], np.array([1, 2, 3]) * BOHR_ANGSTROM)
        point = np.array(first['origin']) + np.array([1, 2, 3]) @ np.array(first['steps'])
        np.testing.assert_allclose(point, np.array([1.4, 2.6, 4.2]) * BOHR_ANGSTROM)
        self.assertEqual(data.metadata['charges'], [])

    def test_unknown_quantity_units_and_malformed_values(self):
        header = 'HOMO_density_ESP_filename_is_not_evidence\nComments\n1 1 2 3\n-2 1 0 0\n-2 0 1 0\n-2 0 0 1\n1 0.0 1 2 3\n'
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            path = Path(directory) / 'density.cube'
            path.write_text(header + '1 2 3 4 5 6 7 8', encoding='ascii')
            data = read_cube(path)
            self.assertEqual(data.metadata['fields'][0]['quantity'], 'unknown_scalar')
            self.assertEqual(data.metadata['fields'][0]['unit'], 'unknown')
            np.testing.assert_array_equal(data.arrays['positions'], [[1, 2, 3]])
            self.assertEqual(data.arrays['cube_nuclear_charges'][0], 0.0)
            for content in ('1 2 3', '1 2 3 4 5 6 7 8 9', '1 2 3 nan 5 6 7 8'):
                path.write_text(header + content, encoding='ascii')
                with self.assertRaises(ValueError):
                    read_cube(path)


if __name__ == '__main__':
    unittest.main()
