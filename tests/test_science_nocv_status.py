import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
from qcblender.external_results import ets_nocv_pairs


REFERENCE_ROOT = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
REAL_TABLE = input_path('sop/c10-c13/multiwfn-cobh3-20260927/COBH3-ETS-NOCV.txt', REFERENCE_ROOT)
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
        with self.assertRaisesRegex(ValueError, 'have not been evaluated'):
            self.parse([PLACEHOLDER, 'Note: All energies are given in kcal/mol', HEADER, ROW])

    def test_real_stdout_earlier_uncalculated_notice(self):
        lines = REAL_STDOUT.read_text(encoding='utf-8').splitlines()
        start = next(i for i, line in enumerate(lines) if 'NOCV orbital energies are not calculated' in line)
        end = next(i for i in range(start, len(lines)) if 'Sum of NOCV eigenvalues:' in lines[i])
        section = [line for line in lines[start:end]
                   if 'Energies of NOCV orbitals have not been evaluated' not in line]
        with self.assertRaisesRegex(ValueError, 'have not been evaluated'):
            self.parse(section)
        header = next(i for i, line in enumerate(section) if 'Pair  Energy |' in line)
        section.insert(header, 'Note: All energies are given in kcal/mol')
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

    def test_duplicate_scientific_field_conflicts(self):
        for field, column, replacement in (
            ('pair_energy', 1, '-2.60'),
            ('positive_orbital', 2, '8'),
            ('positive_eigenvalue', 3, '0.12001'),
            ('negative_eigenvalue', 6, '-0.12001'),
            ('positive_energy', 4, '-3.11'),
            ('negative_orbital', 5, '9'),
            ('negative_energy', 7, '0.61'),
            ('positive_eigenvalue', 3, '0.120000000001'),
        ):
            with self.subTest(field=field):
                columns = ROW.split()
                columns[column] = replacement
                with self.assertRaisesRegex(ValueError, 'Conflicting ETS-NOCV pair') as raised:
                    self.parse([HEADER, ROW, HEADER, ' '.join(columns)])
                self.assertIn(field, str(raised.exception))
                self.assertIn('lines 2 and 4', str(raised.exception))

    def test_duplicate_reports_all_conflicting_fields(self):
        with self.assertRaisesRegex(ValueError, 'Conflicting ETS-NOCV pair') as raised:
            self.parse([HEADER, ROW, HEADER,
                        ROW.replace('0.12000', '0.12001').replace('-3.10', '-3.11')])
        for field in ('positive_eigenvalue', 'negative_eigenvalue', 'positive_energy'):
            self.assertIn(field, str(raised.exception))
        self.assertIn('lines 2 and 4', str(raised.exception))

    def test_identical_normalized_duplicates_keep_first_provenance(self):
        normalized = '1 -2.5000 6 0.120000 -3.100 7 -0.120000 0.600'
        for unit in ('kcal/mol', 'hartree'):
            with self.subTest(unit=unit):
                first = self.parse([HEADER, ROW], unit)
                self.assertEqual(self.parse([HEADER, ROW, HEADER, normalized], unit), first)

    def test_real_table_identical_duplicates_keep_first_provenance(self):
        lines = REAL_TABLE.read_text(encoding='utf-8').splitlines()
        self.assertEqual(self.parse([*lines, *lines]), ets_nocv_pairs(REAL_TABLE, 'kcal/mol'))

    def test_real_table_duplicate_scientific_conflicts(self):
        lines = REAL_TABLE.read_text(encoding='utf-8').splitlines()
        first = ets_nocv_pairs(REAL_TABLE, 'kcal/mol')[0]
        index = first['source_line'] - 1
        for field, column in (('positive_eigenvalue', 3), ('negative_eigenvalue', 6),
                              ('positive_energy', 4), ('negative_energy', 7)):
            with self.subTest(field=field):
                changed = list(lines)
                columns = changed[index].split()
                columns[column] = f'{float(columns[column]) + 0.01:.5f}'
                changed[index] = ' '.join(columns)
                with self.assertRaisesRegex(ValueError, 'Conflicting ETS-NOCV pair') as raised:
                    self.parse([*lines, *changed])
                self.assertIn(field, str(raised.exception))
                self.assertIn(f'lines {index + 1} and {len(lines) + index + 1}',
                              str(raised.exception))


if __name__ == '__main__':
    unittest.main()
