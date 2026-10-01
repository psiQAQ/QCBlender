"""Pure filesystem-path identity checks; Blender resolves // before this boundary."""
import os
from pathlib import Path
import unittest

from qcblender.data import dataset_path_key


class DatasetBindingPaths(unittest.TestCase):
    def test_empty_and_distinct_dataset_paths(self):
        self.assertEqual(dataset_path_key(''), '')
        first = str(Path('datasets') / 'first')
        self.assertEqual(dataset_path_key(first), dataset_path_key(str(Path('datasets') / '.' / 'first')))
        self.assertNotEqual(dataset_path_key(first), dataset_path_key(str(Path('datasets') / 'second')))

    @unittest.skipUnless(os.name == 'nt', 'Windows path identity rules')
    def test_mixed_separators_case_and_dot_segments(self):
        expected = dataset_path_key(r'D:\project\case.qcdata\datasets\abc')
        for path in (r'd:/PROJECT/case.qcdata/datasets/abc',
                     r'D:\project/case.qcdata\datasets/./abc',
                     r'D:\project\case.qcdata\datasets\other\..\abc'):
            with self.subTest(path=path):
                self.assertEqual(dataset_path_key(path), expected)

    @unittest.skipUnless(os.name == 'nt', 'Windows extended-length path rules')
    def test_extended_long_local_paths(self):
        ordinary = 'D:/' + 'long-directory/' * 30 + 'datasets/abc'
        extended = '\\\\?\\' + ordinary.replace('/', '\\')
        self.assertGreater(len(ordinary), 260)
        self.assertEqual(dataset_path_key(ordinary), dataset_path_key(extended))
        self.assertEqual(dataset_path_key(ordinary), dataset_path_key(extended.replace('\\', '/')))

    @unittest.skipUnless(os.name == 'nt', 'Windows UNC path rules')
    def test_unc_and_extended_unc_paths(self):
        ordinary = r'\\server\share\project\datasets\abc'
        self.assertEqual(dataset_path_key(ordinary), dataset_path_key(r'\\?\UNC\server\share\project\datasets\abc'))
        self.assertEqual(dataset_path_key(ordinary), dataset_path_key('//SERVER/share/project/datasets/abc'))
        self.assertNotEqual(dataset_path_key(ordinary), dataset_path_key(r'\\server\other-share\project\datasets\abc'))

    @unittest.skipIf(os.name == 'nt', 'POSIX case-sensitive path rules')
    def test_posix_case_remains_distinct(self):
        self.assertNotEqual(dataset_path_key('/project/ABC'), dataset_path_key('/project/abc'))
