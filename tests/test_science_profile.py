"""Pure Python checks for field profile coordinates, gaps, and saved CSV."""
import csv
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.data import Dataset, load_dataset, save_dataset
from qcblender.profile import export_profile_csv, sample_profile, source_positions, valid_runs
from qcblender.sampling import sample_point


ROOT = Path(__file__).resolve().parents[1]


class LineProfile(unittest.TestCase):
    def setUp(self):
        steps = np.array([[.5, .1, 0], [0, .5, .1], [.1, 0, .5]])
        origin = np.array([-1., 2., -.5])
        positions = np.moveaxis(np.indices((5, 3, 3)), 0, -1) @ steps + origin
        self.field = {'array': 'scalar', 'valid_mask': 'scalar_valid', 'shape': [5, 3, 3],
                      'origin': origin.tolist(), 'steps': steps.tolist(),
                      'quantity': 'analytic', 'unit': 'hartree'}
        self.positions = positions
        self.reference = Dataset({'source': {'filename': 'analytic.cube', 'sha256': 'a' * 64},
                                  'coordinate_unit': 'angstrom', 'fields': [self.field]},
                                 {'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3)),
                                  'scalar': positions @ [2., -3., .5] + 1.,
                                  'scalar_valid': np.ones((5, 3, 3), dtype=bool)})
        self.reference.validate()

    def profile(self, start, end, count=5, role='GEOMETRY'):
        return sample_profile(self.reference, self.field, start, end, start, end, 'b' * 64, role, count)

    def test_sheared_grid_endpoints_distance_and_single_point(self):
        start, end = self.positions[0, 1, 1], self.positions[4, 1, 1]
        data = self.profile(start, end)
        arrays = data.arrays
        np.testing.assert_allclose(arrays['profile_positions'][[0, -1]], [start, end])
        np.testing.assert_allclose(arrays['profile_distance'], np.linspace(0, np.linalg.norm(end - start), 5))
        np.testing.assert_allclose(arrays['profile_values'], arrays['profile_positions'] @ [2., -3., .5] + 1.)
        self.assertTrue(arrays['profile_valid'].all())
        self.assertAlmostEqual(sample_point(self.reference.arrays['scalar'], self.reference.arrays['scalar_valid'],
                                            self.field, start), arrays['profile_values'][0])
        self.assertEqual(data.metadata['source']['kind'], 'derived')
        self.assertEqual(data.metadata['profile']['source_manifest_sha256'], 'b' * 64)

    def test_invalid_domain_mask_gaps_and_csv_reopen(self):
        self.reference.arrays['scalar_valid'][2, :, :] = False
        start, end = self.positions[0, 1, 1], self.positions[4, 1, 1]
        data = self.profile(start, end)
        self.assertEqual(valid_runs(data.arrays['profile_valid']), [(0, 2), (3, 5)])
        self.assertEqual(data.arrays['profile_values'][2], 0.)
        output = ROOT / 'outputs/science-profile'
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as temporary:
            directory = Path(temporary)
            save_dataset(data, directory / 'dataset')
            reopened = load_dataset(directory / 'dataset')
            export_profile_csv(reopened, directory / 'profile.csv')
            with (directory / 'profile.csv').open(encoding='utf-8', newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 5)
            self.assertEqual((rows[2]['value'], rows[2]['valid'], rows[2]['unit']), ('', '0', 'hartree'))
            self.assertEqual(float(rows[-1]['distance_angstrom']), np.linalg.norm(end - start))
        outside = self.profile(start - (end - start), end, 11)
        self.assertFalse(outside.arrays['profile_valid'][0])
        self.assertEqual(float(outside.arrays['profile_values'][0]), 0.)

    def test_rejected_lines_and_source_transform(self):
        start, end = self.positions[0, 1, 1], self.positions[4, 1, 1]
        for count in (1, 1002):
            with self.assertRaisesRegex(ValueError, 'between 2 and 1001'):
                self.profile(start, end, count)
        with self.assertRaisesRegex(ValueError, 'must differ'):
            self.profile(start, start)
        with self.assertRaisesRegex(ValueError, 'no adjacent valid'):
            self.profile(start - (end - start), start, 2)
        geometry = np.eye(4)
        geometry[:3, 3] = [3, 0, 0]
        color = np.eye(4)
        color[:3, 3] = [-4, 0, 0]
        world = [np.array([0., 0., 0.]), np.array([1., 0., 0.])]
        np.testing.assert_allclose(source_positions(*world, geometry)[:, 0], [-3., -2.])
        np.testing.assert_allclose(source_positions(*world, color)[:, 0], [4., 5.])
        rotated = np.array([[0., -2., 0., 3.], [1., 0., 0., 4.],
                            [0., 0., .5, 5.], [0., 0., 0., 1.]])
        local = np.array([start, end])
        transformed = local @ rotated[:3, :3].T + rotated[:3, 3]
        np.testing.assert_allclose(source_positions(*transformed, rotated), local)
        color_field = dict(self.field, array='color', quantity='color_analytic')
        self.reference.arrays['color'] = 2 * self.reference.arrays['scalar']
        self.reference.metadata['fields'].append(color_field)
        color_data = sample_profile(self.reference, color_field, start, end, start, end,
                                    'c' * 64, 'COLOR', 5)
        self.assertEqual(color_data.metadata['profile']['field_role'], 'COLOR')
        np.testing.assert_allclose(color_data.arrays['profile_values'],
                                   2 * self.profile(start, end).arrays['profile_values'])


if __name__ == '__main__':
    unittest.main()
