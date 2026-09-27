import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qcblender.external_results import ets_nocv_pairs


REFERENCE_ROOT = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
REAL_TABLE = REFERENCE_ROOT / 'outputs/v1-acceptance/sources/c10-c13/multiwfn-cobh3-20260927/COBH3-ETS-NOCV.txt'
REAL_STDOUT = REAL_TABLE.with_name('stdout.txt')
HEADER = 'Pair Energy | Orbital Eigenvalue Energy | Orbital Eigenvalue Energy'
ROW = '1 -2.50 6 0.12000 -3.10 7 -0.12000 0.60'
PLACEHOLDER = 'Note: Energies of NOCV orbitals have not been evaluated, so they are all zero'


class NocvEnergyStatus(unittest.TestCase):
    def setUp(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=ROOT / 'outputs')
        self.addCleanup(self.directory.cleanup)

    def parse(self, lines, unit='kcal/mol'):
        path = Path(self.directory.name) / 'pairs.txt'
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return ets_nocv_pairs(path, unit)

    def test_real_calculated_table(self):
        rows = ets_nocv_pairs(REAL_TABLE, 'kcal/mol')
        self.assertEqual(len(rows), 9)
        self.assertEqual((rows[0]['pair'], rows[0]['pair_energy'], rows[0]['spin'],
                          rows[0]['source_line'], rows[0]['energy_unit']),
                         (1, -77.88, 'Total', 7, 'kcal/mol'))

    def test_placeholder_is_skipped_and_later_calculated_table_is_read(self):
        with self.assertRaisesRegex(ValueError, 'have not been evaluated'):
            self.parse([PLACEHOLDER, HEADER, ROW])
        rows = self.parse([PLACEHOLDER, HEADER, ROW, '',
                           'Note: All energies are given in kcal/mol', HEADER, ROW])
        self.assertEqual([(row['pair'], row['source_line']) for row in rows], [(1, 7)])
        self.assertEqual(len(self.parse([PLACEHOLDER,
                                         'Note: All energies are given in kcal/mol', HEADER, ROW])), 1)

    def test_real_stdout_earlier_uncalculated_notice(self):
        lines = REAL_STDOUT.read_text(encoding='utf-8').splitlines()
        start = next(i for i, line in enumerate(lines) if 'NOCV orbital energies are not calculated' in line)
        end = next(i for i in range(start, len(lines)) if 'Sum of NOCV eigenvalues:' in lines[i])
        section = [line for line in lines[start:end]
                   if 'Energies of NOCV orbitals have not been evaluated' not in line]
        with self.assertRaisesRegex(ValueError, 'have not been evaluated'):
            self.parse(section)
        self.assertEqual(len(self.parse([*section, *REAL_TABLE.read_text(encoding='utf-8').splitlines()])), 9)

    def test_zero_values_need_an_explicit_placeholder_statement_to_be_skipped(self):
        zero = '1 0.00 6 0.12000 0.00 7 -0.12000 0.00'
        self.assertEqual(self.parse(['Note: All energies are given in kcal/mol', HEADER, zero])[0]['pair_energy'], 0)
        for unit in ('kcal/mol', 'hartree'):
            with self.subTest(unit=unit):
                self.assertEqual(self.parse([HEADER, zero], unit)[0]['energy_unit'], unit)

    def test_explicit_units_are_validated(self):
        for note, unit, error in (
            ('Note: All energies are given in eV', 'kcal/mol', 'unsupported energy unit ev'),
            ('Note: All energies are given in kcal/mol', 'hartree', 'declares kcal/mol, not hartree'),
            ('Note: All energies are given in Hartree', 'kcal/mol', 'declares hartree, not kcal/mol'),
        ):
            with self.subTest(note=note, unit=unit):
                with self.assertRaisesRegex(ValueError, error):
                    self.parse([note, HEADER, ROW], unit)
        real_lines = REAL_TABLE.read_text(encoding='utf-8').splitlines()
        for note, error in (('Note: All energies are given in hartree', 'declares hartree, not kcal/mol'),
                            ('Note: All energies are given in eV', 'unsupported energy unit ev')):
            with self.subTest(earlier_note=note):
                with self.assertRaisesRegex(ValueError, error):
                    self.parse([note, *real_lines])
        self.assertEqual(len(self.parse(['Note: All energies are given in kcal/mol', *real_lines])), 9)

    def test_spin_pair_identity_and_conflicting_duplicates(self):
        rows = self.parse(['Alpha NOCV orbitals', HEADER, ROW,
                           'Beta NOCV orbitals', HEADER, ROW])
        self.assertEqual([(row['spin'], row['pair'], row['source_line']) for row in rows],
                         [('Alpha', 1, 3), ('Beta', 1, 6)])
        with self.assertRaisesRegex(ValueError, 'Conflicting ETS-NOCV pair'):
            self.parse([HEADER, ROW, HEADER, ROW.replace('-2.50', '-2.60')])


if __name__ == '__main__':
    unittest.main()
