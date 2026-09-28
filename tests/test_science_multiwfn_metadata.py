"""Check Multiwfn declarations against real C07/C08 files and edited variants."""
import os
from pathlib import Path
import tempfile
import unittest

from qcblender.analysis_data import import_esp
from qcblender.external_fields import pair_cubes
from qcblender.external_results import esp_area, esp_extrema, esp_extrema_unit
from qcblender.readers import read_source


ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
SOURCES = input_path('sop', Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)))
C08 = SOURCES / 'multiwfn-local/C08'
C07 = SOURCES / 'c07-c09-research/phenol-2026-09-27'
FCHK = input_path('complex-examples/Trp_polar.fchk', Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT)))


class MultiwfnMetadata(unittest.TestCase):
    def setUp(self):
        output = ROOT / 'outputs/science-multiwfn-metadata'
        output.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)

    def write(self, name, content):
        path = self.work / name
        path.write_text(content, encoding='utf-8')
        return path

    def test_area_formats_and_interval_validation(self):
        five = self.write('five.txt', 'Note: Area unit is in Angstrom^2\n'
                          'Begin End Center Area %\n-5 0 -2.5 2 40\n0 5 2.5 3 60\n')
        bins = esp_area(five)
        self.assertEqual([(row['begin'], row['end']) for row in bins], [(-5, 0), (0, 5)])
        three = self.write('three.txt', 'Center Area Percentage\n-2.5 2 40\n2.5 3 60\n')
        self.assertEqual([(row['begin'], row['end']) for row in esp_area(three)],
                         [(None, None), (None, None)])
        for text in ('Begin End Center Area %\n0 1 2 3 50\n',
                     'Begin Center Area %\n0 1 2 50\n',
                     'Begin End Center Area %\n0 1 0.5 3 110\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                esp_area(self.write('invalid.txt', text))

    def test_real_esp_declaration_and_conflicts(self):
        if not all(path.is_file() for path in (C08 / 'surfanalysis.pdb', C08 / 'stdout.log', FCHK)):
            self.skipTest('Real C08 and FCHK sources are required; set QCBLENDER_REFERENCE_ROOT')
        pdb, area = C08 / 'surfanalysis.pdb', C08 / 'stdout.log'
        self.assertEqual(esp_extrema_unit(pdb)['source_line'], 1)
        self.assertEqual(esp_extrema_unit(pdb)['unit'], 'kcal/mol')
        self.assertEqual((len(esp_extrema(pdb)), len(esp_area(area))), (19, 40))
        reference = read_source(FCHK)
        def imported(path, value_unit='', area_unit=''):
            return import_esp(reference, path, area, 'rho=0.001 electron/bohr^3',
                              value_unit, 'kcal/mol', area_unit).metadata['analysis']
        analysis = imported(pdb)
        self.assertEqual((analysis['extrema_unit'], analysis['area_unit']),
                         ('kcal/mol', 'angstrom^2'))
        self.assertEqual(analysis['extrema_unit_declaration']['source_line'], 1)
        self.assertEqual(analysis['area_unit_declaration']['unit'], 'angstrom^2')
        self.assertEqual((analysis['area_bins'][0]['begin'], analysis['area_bins'][0]['end']),
                         (-100, -95))
        three = self.write('three.txt', 'Center Area %\n-2.5 2 40\n2.5 3 60\n')
        with self.assertRaisesRegex(ValueError, 'no area unit declaration'):
            import_esp(reference, pdb, three, 'rho=0.001 electron/bohr^3', '', 'kcal/mol', '')
        three_data = import_esp(reference, pdb, three, 'rho=0.001 electron/bohr^3',
                                '', 'kcal/mol', 'angstrom^2').metadata['analysis']
        self.assertIsNone(three_data['area_bins'][0]['begin'])
        self.assertIsNone(three_data['area_unit_declaration'])
        with self.assertRaisesRegex(ValueError, 'conflicts with PDB line 1'):
            imported(pdb, 'eV')
        with self.assertRaisesRegex(ValueError, 'conflicts with table line'):
            imported(pdb, area_unit='bohr^2')
        no_note = self.write('no-note.pdb', '\n'.join(pdb.read_text(encoding='utf-8').splitlines()[1:]) + '\n')
        with self.assertRaisesRegex(ValueError, 'no B-factor unit declaration'):
            imported(no_note)
        self.assertIsNone(imported(no_note, 'kcal/mol')['extrema_unit_declaration'])
        wrong = self.write('wrong.pdb', pdb.read_text(encoding='utf-8').replace('(i.e. ESP)', '(ALIE)', 1))
        with self.assertRaisesRegex(ValueError, 'non-ESP'):
            imported(wrong)

    def test_real_pair_units_and_iri_exponent(self):
        iri, color = C07 / 'iri/func2.cub', C07 / 'iri/func1.cub'
        if not iri.is_file() or not color.is_file():
            self.skipTest('Real C07 Cube pair is required; set QCBLENDER_REFERENCE_ROOT')
        with self.assertRaisesRegex(ValueError, 'unit must be explicitly specified'):
            pair_cubes(iri, color, 'IRI', 'dimensionless', 'electron/bohr^3', 1.1)
        with self.assertRaisesRegex(ValueError, 'finite positive'):
            pair_cubes(iri, color, 'IRI', 'a.u.', 'electron/bohr^3', 'nan')
        unit = 'electron^-0.1 bohr^-0.7'
        current = pair_cubes(iri, color, 'IRI', unit, 'electron/bohr^3', 1.1)
        self.assertEqual(current.metadata['analysis']['iri_density_exponent'], 1.1)
        self.assertEqual(current.metadata['fields'][0]['unit'], unit)
        old = pair_cubes(iri, color, 'IRI', unit, 'electron/bohr^3')
        self.assertIsNone(old.metadata['analysis']['iri_density_exponent'])
        self.assertTrue(any('exponent not supplied' in text for text in old.metadata['diagnostics']))
        igmh = pair_cubes(C07 / 'igmh/dg_inter.cub', C07 / 'igmh/sl2r.cub',
                          'IGMH', 'electron/bohr^4', 'electron/bohr^3')
        self.assertEqual(igmh.metadata['fields'][0]['unit'], 'electron/bohr^4')


if __name__ == '__main__':
    unittest.main()
