"""Check AIM property association against actual Multiwfn C09 records."""
import os
from pathlib import Path
import re
import tempfile
import unittest

from qcblender.analysis_data import import_aim
from qcblender.readers import read_source


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
C09 = REFERENCE_ROOT / 'outputs/v1-acceptance/sources/multiwfn-local/C09'
FCHK = REFERENCE_ROOT / 'outputs/complex-examples/sources/Trp_polar.fchk'


class AimAssociation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all(path.is_file() for path in (FCHK, C09 / 'CPs.pdb', C09 / 'paths.pdb', C09 / 'CPprop.txt')):
            raise unittest.SkipTest('Real C09 and reference FCHK files are required; set QCBLENDER_REFERENCE_ROOT')
        cls.reference = read_source(FCHK)
        cls.source = (C09 / 'CPprop.txt').read_text(encoding='utf-8')

    def import_properties(self, text):
        output = ROOT / 'outputs/science-aim-association'
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as temporary:
            path = Path(temporary) / 'CPprop.txt'
            path.write_text(text, encoding='utf-8')
            return import_aim(self.reference, C09 / 'CPs.pdb', C09 / 'paths.pdb', path)

    def test_real_c09_and_alternate_type_key(self):
        data = import_aim(self.reference, C09 / 'CPs.pdb', C09 / 'paths.pdb', C09 / 'CPprop.txt')
        analysis = data.metadata['analysis']
        self.assertEqual((len(analysis['critical_points']), len(analysis['paths']), len(analysis['properties'])),
                         (59, 58, 59))
        self.assertEqual(data.metadata['diagnostics'], [])
        modern = re.sub(r'^.*CP\s+1,\s+Type \(3,-3\).*$\n',
                        ' Critical point 1:\n CP type: (3,-3)\n', self.source, count=1, flags=re.M)
        self.assertEqual(self.import_properties(modern).metadata['diagnostics'], [])

    def test_conflicts_and_printed_coordinate_tolerance(self):
        wrong_type = self.source.replace('Type (3,-3)', 'Type (3,-1)', 1)
        with self.assertRaisesRegex(ValueError, 'CP 1.*type conflicts'):
            self.import_properties(wrong_type)
        for x, accepted in (('3.1385000', True), ('3.1385010', False)):
            with self.subTest(x=x):
                changed = re.sub(r'^ Position \(Angstrom\):.*$',
                                 f' Position (Angstrom): {x} -0.656344441861 1.538010181370',
                                 self.source, count=1, flags=re.M)
                if accepted:
                    self.assertEqual(self.import_properties(changed).metadata['diagnostics'], [])
                else:
                    with self.assertRaisesRegex(ValueError, 'CP 1.*position conflicts'):
                        self.import_properties(changed)

    def test_missing_fields_are_diagnosed(self):
        missing = re.sub(r'^.*CP\s+1,\s+Type \(3,-3\).*$\n',
                         ' Critical point 1:\n', self.source, count=1, flags=re.M)
        missing = re.sub(r'^ Position \(Angstrom\):.*$\n', '', missing, count=1, flags=re.M)
        diagnostics = self.import_properties(missing).metadata['diagnostics']
        self.assertEqual(len(diagnostics), 2)
        self.assertTrue(all('unverified for 1 CP(s)' in message for message in diagnostics))
        absent = import_aim(self.reference, C09 / 'CPs.pdb', C09 / 'paths.pdb')
        self.assertTrue(all('unverified for 59 CP(s)' in message for message in absent.metadata['diagnostics']))

    def test_malformed_and_nonfinite_fields_fail(self):
        for changed in (self.source.replace('Type (3,-3)', 'Type (bad)', 1),
                        self.source.replace('Type (3,-3)', 'Type 3,-3', 1),
                        re.sub(r'^ Position \(Angstrom\):.*$', ' Position (Angstrom): broken',
                               self.source, count=1, flags=re.M),
                        re.sub(r'^ Position \(Angstrom\):', ' Position (Angstrom)',
                               self.source, count=1, flags=re.M),
                        re.sub(r'^ Position \(Angstrom\):.*$', 'Position (Angstrom)',
                               self.source, count=1, flags=re.M),
                        re.sub(r'^ Position \(Angstrom\):.*$', ' Position (Angstrom): nan 0 0',
                               self.source, count=1, flags=re.M)):
            with self.subTest(changed=changed[:100]):
                with self.assertRaisesRegex(ValueError, '(CP 1.*(malformed|nonfinite)|malformed (CP header|field))'):
                    self.import_properties(changed)

    def test_repeated_fields_cannot_hide_conflicts(self):
        wrong_type_then_correct = self.source.replace(
            ' Corresponding nucleus:', ' CP_type: (3,-1)\n CP_type: (3,-3)\n Corresponding nucleus:', 1)
        wrong_position_then_correct = self.source.replace(
            ' Position (Angstrom):',
            ' Position (Angstrom): 999 999 999\n Position (Angstrom):', 1)
        for changed in (wrong_type_then_correct, wrong_position_then_correct):
            with self.subTest(changed=changed[:150]):
                with self.assertRaisesRegex(ValueError, 'repeated|conflicts'):
                    self.import_properties(changed)


if __name__ == '__main__':
    unittest.main()
