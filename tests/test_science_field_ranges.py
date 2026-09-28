"""Pure Python checks for source field ranges and worker identity guards."""

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qcblender import data
from qcblender.field_ranges import field_range
from qcblender.worker import field_range_report


ROOT = Path(__file__).resolve().parents[1]


def dataset(values, valid=None):
    values = np.asarray(values, dtype=float)
    if valid is None:
        valid = np.ones(values.shape, dtype=bool)
    field = {'array': 'scalar', 'valid_mask': 'scalar_valid', 'shape': list(values.shape),
             'origin': [0, 0, 0], 'steps': np.eye(3).tolist(),
             'quantity': 'electrostatic_potential', 'unit': 'hartree/e'}
    return data.Dataset({'source': {'filename': 'test.cube', 'sha256': 'a' * 64},
                         'coordinate_unit': 'angstrom', 'fields': [field]},
                        {'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3)),
                         'scalar': values, 'scalar_valid': np.asarray(valid, dtype=bool)})


class FieldRanges(unittest.TestCase):
    def test_negative_positive_and_cross_zero(self):
        for values, expected in [([[-4., -2.]], (-4., -3., -2.)),
                                 ([[2., 8.]], (2., 5., 8.)),
                                 ([[-3., 9.]], (-3., 0., 9.))]:
            with self.subTest(values=values):
                result = field_range(dataset(np.array(values).reshape(1, 2, 1)), 'scalar')
                self.assertEqual(tuple(result[key] for key in ('minimum', 'center', 'maximum')), expected)
                self.assertEqual((result['valid_count'], result['quantity'], result['unit']),
                                 (2, 'electrostatic_potential', 'hartree/e'))

    def test_mask_and_invalid_ranges(self):
        source = dataset(np.array([-100., -4., 8., 100.]).reshape(2, 2, 1),
                         np.array([False, True, True, False]).reshape(2, 2, 1))
        result = field_range(source, 'scalar')
        self.assertEqual((result['minimum'], result['center'], result['maximum'], result['valid_count']),
                         (-4., 0., 8., 2))
        for values, mask, error in [([1., 1.], [True, True], 'increasing'),
                                    ([1., 2.], [False, False], 'no valid'),
                                    ([1., float('nan')], [True, True], 'finite')]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                field_range(dataset(np.array(values).reshape(1, 2, 1),
                                    np.array(mask).reshape(1, 2, 1)), 'scalar')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            field_range(source, 'missing')
        with self.assertRaisesRegex(ValueError, 'Choose'):
            field_range(source, '')

    def test_worker_checks_identity_integrity_cancel_and_no_dataset_writes(self):
        output = ROOT / 'outputs/science-field-ranges'
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as temporary:
            target = Path(temporary) / 'dataset'
            data.save_dataset(dataset(np.array([-3., 4.]).reshape(1, 2, 1)), target)
            manifest = target / 'manifest.json'
            digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            request = {'dataset': str(target), 'dataset_sha256': digest, 'field_array': 'scalar'}
            before = {path.relative_to(target): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in target.rglob('*') if path.is_file()}
            with patch.object(data, 'volume_cache', side_effect=AssertionError('range read built a cache')):
                result = field_range_report(request, data, field_range, lambda: False)
            self.assertEqual((result['status'], result['dataset_sha256'], result['valid_count']),
                             ('succeeded', digest, 2))
            self.assertEqual((result['minimum'], result['center'], result['maximum']), (-3., 0., 4.))
            after = {path.relative_to(target): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in target.rglob('*') if path.is_file()}
            self.assertEqual(before, after)
            for changed, message in [({**request, 'dataset_sha256': '0' * 64}, 'changed'),
                                     ({'dataset': str(target), 'field_array': 'scalar'}, 'required'),
                                     ({**request, 'field_array': 'absent'}, 'exactly one')]:
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    field_range_report(changed, data, field_range, lambda: False)
            with self.assertRaises(InterruptedError):
                field_range_report(request, data, field_range, lambda: True)
            checks = iter([False, True])
            with self.assertRaises(InterruptedError):
                field_range_report(request, data, field_range, lambda: next(checks))
            with patch.object(data, 'load_dataset', side_effect=MemoryError('budget exceeded')):
                with self.assertRaisesRegex(MemoryError, 'budget exceeded'):
                    field_range_report(request, data, field_range, lambda: False)

            original_load = data.load_dataset

            def change_manifest(directory):
                loaded = original_load(directory)
                manifest.write_bytes(manifest.read_bytes() + b' ')
                return loaded

            with patch.object(data, 'load_dataset', side_effect=change_manifest):
                with self.assertRaisesRegex(ValueError, 'changed'):
                    field_range_report(request, data, field_range, lambda: False)

            manifest.write_bytes(manifest.read_bytes()[:-1])
            array_file = next((target / 'arrays').glob('*.npy'))
            array_file.write_bytes(array_file.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                field_range_report(request, data, field_range, lambda: False)


if __name__ == '__main__':
    unittest.main()
