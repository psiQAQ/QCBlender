import os
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.analysis_data import import_ets
from qcblender.cube import read_cube
from qcblender.nocv import import_nocv
from tools.comparison_fixture import prepare_comparison_cube, write_comparison_cube

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))


class ComparisonFixture(unittest.TestCase):
    def test_current_wavefunction_rebuilds_signed_cube_and_numeric_pair(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            output = Path(directory)
            cube = prepare_comparison_cube(REFERENCE, output)
            data = read_cube(cube)
            self.assertEqual(data.arrays['cube_0'].shape, (31, 31, 31))
            self.assertTrue(np.any(data.arrays['cube_0'] > 0))
            self.assertTrue(np.any(data.arrays['cube_0'] < 0))
            with self.assertRaises(FileExistsError):
                prepare_comparison_cube(REFERENCE, output)
            table_file = output / 'ets.txt'
            table_file.write_text('Note: All energies are given in kcal/mol\n'
                'Pair Energy | Orbital Eigenvalue Energy | Orbital Eigenvalue Energy\n'
                '-----\n1 -2.50 6 0.12000 -3.10 7 -0.12000 0.60\n', encoding='utf-8')
            table = import_ets(data, table_file, 'kcal/mol')
            paired = import_nocv(cube, table, 1, 'Total', 'electron/bohr^3')
            self.assertEqual(paired.metadata['analysis']['association']['status'], 'geometry_matched')
            with self.assertRaisesRegex(ValueError, 'pair and spin'):
                import_nocv(cube, table, 2, 'Total', 'electron/bohr^3')
            data.metadata['fields'][0]['unit'] = 'unknown'
            with self.assertRaisesRegex(ValueError, 'orbital amplitude'):
                write_comparison_cube(data, output / 'invalid.cube')


if __name__ == '__main__':
    unittest.main()
