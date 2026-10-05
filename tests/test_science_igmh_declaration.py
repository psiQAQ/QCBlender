"""IGMH import declarations preserve the source grids and numerical exports."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
sys.path[:0] = [str(ROOT), str(SAMPLES / 'outputs/science')]
import numpy as np
from qcblender.data import load_dataset, save_dataset
from qcblender.data_export import export_dataset
from qcblender.external_fields import pair_cubes
from tools.local_inputs import input_path


class IGMHDeclaration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = input_path('public-tutorial/P03/igmh', SAMPLES)
        cls.geometry, cls.color = folder / 'dg_inter.cub', folder / 'sl2r.cub'
        cls.baseline = pair_cubes(cls.geometry, cls.color, 'IGMH', 'electron/bohr^4', 'electron/bohr^3')
        ROOT.joinpath('outputs').mkdir(exist_ok=True)

    def pair(self, **declaration):
        return pair_cubes(self.geometry, self.color, 'IGMH', 'electron/bohr^4', 'electron/bohr^3',
                          **declaration)

    def test_each_component_changes_only_declarations(self):
        for component in ('inter', 'intra', 'total', 'unknown'):
            with self.subTest(component=component):
                data = self.pair(igmh_component=component, igmh_fragments=[[1, 2, 3], [4, 5, 6]],
                                 igmh_declaration_source='P03 Multiwfn fragment setup')
                declaration = data.metadata['analysis']['igmh_declaration']
                self.assertEqual(declaration['component'], component)
                self.assertEqual(declaration['fragments'], [[1, 2, 3], [4, 5, 6]])
                self.assertEqual(declaration['interpretation'], 'user_assigned')
                self.assertEqual(declaration['source'], 'P03 Multiwfn fragment setup')
                self.assertEqual(declaration['status'], 'unverified' if component == 'unknown' else 'declared')
                self.assertEqual(data.metadata['fields'], self.baseline.metadata['fields'])
                for key, values in self.baseline.arrays.items():
                    np.testing.assert_array_equal(data.arrays[key], values)

    def test_fragment_validation_and_overlap(self):
        for fragments in ([[0]], [[7]], [[1.0]], [[True]], [['1']], [[1, 1]], [1, 2], {'1': [1]}):
            with self.subTest(fragments=fragments), self.assertRaises(ValueError):
                self.pair(igmh_component='inter', igmh_fragments=fragments)
        data = self.pair(igmh_component='intra', igmh_fragments=[[1, 2], [2, 3]])
        declaration = data.metadata['analysis']['igmh_declaration']
        self.assertEqual(declaration['fragments'], [[1, 2], [2, 3]])
        self.assertEqual(declaration['overlapping_atoms'], [2])
        self.assertTrue(declaration['warnings'])
        self.pair(igmh_component='total', igmh_fragments=[[1]])

    def test_invalid_component_source_and_iri_declarations_are_rejected(self):
        from qcblender.external_fields import igmh_declaration
        for component in ('INTER', '', 'delta_g'):
            with self.subTest(component=component), self.assertRaises(ValueError):
                igmh_declaration(component, None, '', 6)
        for source in (None, 1, 'x' * 501):
            with self.subTest(source=source), self.assertRaises(ValueError):
                igmh_declaration('inter', None, source, 6)
        with self.assertRaisesRegex(ValueError, 'only to IGMH'):
            pair_cubes(self.geometry, self.color, 'IRI', 'a.u.', 'electron/bohr^3', 1.1,
                       igmh_component='inter')

    def test_manifest_and_csv_metadata_keep_declaration(self):
        data = self.pair(igmh_component='inter', igmh_fragments=[[1, 2, 3], [4, 5, 6]],
                         igmh_declaration_source='P03 fragment assignment')
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as tmp:
            directory = Path(tmp) / 'dataset'
            save_dataset(data, directory)
            reopened = load_dataset(directory)
            self.assertEqual(reopened.metadata['analysis'], data.metadata['analysis'])
            exported = export_dataset(directory, Path(tmp) / 'export', 'paired')
            metadata = json.loads(Path(exported['directory'], 'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(metadata['scientific_metadata']['analysis']['igmh_declaration'],
                             data.metadata['analysis']['igmh_declaration'])

    def test_missing_and_legacy_declarations_are_unverified(self):
        from qcblender.external_fields import igmh_declaration_record
        self.assertEqual(igmh_declaration_record(self.baseline.metadata['analysis'])['status'], 'unverified')
        legacy = copy.deepcopy(self.baseline.metadata['analysis'])
        legacy.pop('igmh_declaration', None)
        self.assertEqual(igmh_declaration_record(legacy)['component'], 'unknown')
        self.assertEqual(igmh_declaration_record(legacy)['status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
