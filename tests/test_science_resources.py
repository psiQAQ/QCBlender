"""Dataset byte boundaries, allocation rejection and scientific identity regressions."""
from copy import deepcopy
from io import BytesIO
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qcblender.data import Dataset, load_dataset, save_dataset
from qcblender.evaluate import Grid, evaluate_field
from qcblender.readers import read_source
from qcblender.resources import array_descriptor, dataset_bytes, field_resources, npy_bytes
from qcblender.science_identity import DEPENDENCIES, SOURCE_MEMBERS, field_cache_key, scientific_identity
from qcblender.science_preflight import qualify_dataset, preview_grid, preview_orbital, preview_resources

ROOT = Path(__file__).resolve().parents[1]


class ResourceContract(unittest.TestCase):
    def setUp(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'outputs')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.data = Dataset({'coordinate_unit': 'angstrom'}, {
            'atomic_numbers': np.array([1], dtype=np.int32), 'positions': np.zeros((1, 3))})

    def test_estimator_matches_numpy_serialization(self):
        arrays = [np.array(True), np.empty((0, 3)), np.ones((3, 4), dtype=np.float32),
                  np.asfortranarray(np.ones((3, 4))), np.arange(4, dtype=np.int32)]
        for array in arrays:
            with self.subTest(dtype=str(array.dtype), shape=array.shape):
                stream = BytesIO()
                np.save(stream, array, allow_pickle=False)
                self.assertEqual(npy_bytes(array_descriptor(array)), stream.tell())

    def test_save_and_load_at_exact_limit_and_one_byte_over(self):
        size = dataset_bytes(self.data.arrays)
        save_dataset(self.data, self.directory / 'dataset', max_bytes=size)
        load_dataset(self.directory / 'dataset', max_bytes=size)
        with patch('qcblender.data.np.load', side_effect=AssertionError('Array read before budget check')):
            with self.assertRaises(MemoryError):
                load_dataset(self.directory / 'dataset', max_bytes=size - 1)
        with self.assertRaises(MemoryError):
            save_dataset(self.data, self.directory / 'rejected', max_bytes=size - 1)
        self.assertFalse((self.directory / 'rejected').exists())

    def test_all_paths_are_checked_before_any_array_is_read(self):
        manifest = save_dataset(self.data, self.directory / 'dataset')
        value = json.loads(manifest.read_text(encoding='utf-8'))
        value['arrays']['positions']['path'] = '../outside.npy'
        manifest.write_text(json.dumps(value), encoding='utf-8')
        with patch('qcblender.data.np.load', side_effect=AssertionError('Array read before paths checked')):
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                load_dataset(manifest.parent)

    def test_duplicate_manifest_records_count_independently(self):
        self.data.arrays['same_positions'] = self.data.arrays['positions']
        manifest = save_dataset(self.data, self.directory / 'dataset')
        with self.assertRaises(MemoryError):
            load_dataset(manifest.parent, max_bytes=dataset_bytes(self.data.arrays) - 1)

    def test_result_replaces_old_fields_but_budget_retains_resident_inputs(self):
        self.data.arrays.update(field_values=np.zeros((3, 3, 3)), field_valid=np.ones((3, 3, 3), dtype=bool))
        records = {name: array_descriptor(array) for name, array in self.data.arrays.items()}
        estimate = field_resources(records, [2, 2, 2], 1, 'orbital_amplitude')
        result = {name: array for name, array in self.data.arrays.items() if not name.startswith('field_')}
        result.update(field_values=np.zeros((2, 2, 2)), field_valid=np.ones((2, 2, 2), dtype=bool))
        self.assertEqual(estimate['dataset_bytes'], dataset_bytes(result))
        self.assertEqual(estimate['input_bytes'], sum(array.nbytes for array in self.data.arrays.values()))
        field_resources(records, [2, 2, 2], 1, 'orbital_amplitude', max_bytes=estimate['dataset_bytes'])
        with self.assertRaises(MemoryError):
            field_resources(records, [2, 2, 2], 1, 'orbital_amplitude', max_bytes=estimate['dataset_bytes'] - 1)

    def test_512_cubed_is_rejected_before_prepare_or_large_allocation(self):
        self.data.arrays['mo_coeffs'] = np.zeros((1, 1))
        grid = Grid([0, 0, 0], np.eye(3), [512, 512, 512])
        with patch('qcblender.evaluate.prepare', side_effect=AssertionError('prepare must not run')):
            with patch('qcblender.evaluate.np.empty', side_effect=AssertionError('No allocation allowed')):
                with self.assertRaisesRegex(MemoryError, 'dataset arrays'):
                    evaluate_field(self.data, grid, 'orbital_amplitude', memory_mb=4096)

    def test_qualification_rejects_large_ao_matrix_before_loading_arrays(self):
        self.data.arrays['mo_coeffs'] = np.zeros((20000, 1))
        manifest = save_dataset(self.data, self.directory / 'dataset')
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        with patch('qcblender.data.np.load', side_effect=AssertionError('No array reads')):
            with patch('qcblender.evaluate.prepare', side_effect=AssertionError('No density matrices')):
                report = qualify_dataset(manifest.parent, digest, memory_mb=16384)
        self.assertFalse(report['eligible'])
        self.assertEqual(report['refusal_kind'], 'resource')
        self.assertGreater(report['minimum_working_bytes'], 16384 * 1024**2)

    def test_each_scientific_member_changes_identity_display_docs_do_not(self):
        for member in SOURCE_MEMBERS:
            shutil.copy2(ROOT / 'qcblender' / member, self.directory / member)
        versions = {name: 'test-version' for name in DEPENDENCIES}
        original = scientific_identity(self.directory, versions.__getitem__)
        for member in SOURCE_MEMBERS:
            path = self.directory / member
            contents = path.read_bytes()
            path.write_bytes(contents + b'\n# scientific change\n')
            self.assertNotEqual(original['sha256'], scientific_identity(self.directory, versions.__getitem__)['sha256'])
            path.write_bytes(contents)
        for dependency in DEPENDENCIES:
            changed = dict(versions, **{dependency: 'changed'})
            self.assertNotEqual(original['sha256'], scientific_identity(self.directory, changed.__getitem__)['sha256'])
        (self.directory / 'USER_GUIDE.md').write_text('changed documentation', encoding='utf-8')
        (self.directory / 'views.py').write_text('changed display', encoding='utf-8')
        self.assertEqual(original, scientific_identity(self.directory, versions.__getitem__))
        key = field_cache_key('input', {}, {'memory_mb': 512, 'quantity': 'orbital_amplitude'}, '5.1.1', original)
        self.assertEqual(key, field_cache_key('input', {}, {'memory_mb': 1024, 'quantity': 'orbital_amplitude'}, '5.1.1', original))
        self.assertNotEqual(key, field_cache_key('input', {}, {'memory_mb': 512, 'quantity': 'orbital_amplitude'}, '5.1.1', dict(original, sha256='changed')))


class ScientificQualification(unittest.TestCase):
    def setUp(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'outputs')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.data = read_source(ROOT / 'tests/data/iodata/o2_cc_pvtz_pure.fchk')

    def qualify(self, data=None, cancelled=lambda: False):
        manifest = save_dataset(self.data if data is None else data, self.directory)
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        return qualify_dataset(self.directory, digest, cancelled)

    def test_real_qualification_lightweight_preview_and_orbital_selection(self):
        with patch('qcblender.evaluate.evaluate_field', side_effect=AssertionError('No field calculation')):
            report = self.qualify()
        self.assertTrue(report['eligible'])
        preview = report['preview']
        self.assertNotIn('mo_coeffs', preview['orbital_arrays'])
        self.assertEqual(preview_orbital(preview, 'alpha', 'EXPLICIT', 9)['source_number'], 9)
        grid = preview_grid(preview, .2, 3)
        estimate = preview_resources(preview, grid, 'orbital_amplitude', 512)
        self.assertIsNone(estimate['refusal_reason'])

    def test_unsupported_method_ecp_occupations_density_are_rejected(self):
        for defect in ('method', 'ecp', 'density', 'fractional'):
            data = deepcopy(self.data)
            if defect == 'method':
                data.metadata['method'] = 'unqualified'
            elif defect == 'ecp':
                data.arrays['core_charges'][0] -= 1
            elif defect == 'density':
                data.arrays['dm_scf'] = np.zeros((data.arrays['mo_coeffs'].shape[0],) * 2)
            else:
                data = read_source(ROOT / 'tests/data/iodata/water_sto3g_hf_g03.fchk')
                data.arrays['mo_occs'][0] = 1.5
            with self.subTest(defect=defect):
                result = self.qualify(data)
                self.assertFalse(result['eligible'])
                self.assertTrue(result['reason'])

    def test_cancel_and_manifest_change_fail_without_field_evaluation(self):
        with self.assertRaises(InterruptedError):
            self.qualify(cancelled=lambda: True)
        self.qualify()
        with self.assertRaisesRegex(ValueError, 'changed'):
            qualify_dataset(self.directory, '0' * 64)


if __name__ == '__main__':
    unittest.main()
