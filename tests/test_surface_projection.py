"""Real Multiwfn reference, grid semantics, persistence and lossless CSV export."""
import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from qcblender.contours import trace_contours
from qcblender.data import load_dataset, save_dataset
from qcblender.data_export import export_dataset
from qcblender.surface_projection import (DEPTH_TOLERANCE, MISSED, UNKNOWN, VALID,
    check_generation_log, color_range, grid_positions, import_projection, parse_grid,
    parse_mask, scan_settings)
from qcblender.xyz import read_xyz
from tools.local_inputs import input_path

ROOT = Path(__file__).resolve().parents[1]


class SurfaceProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = input_path('scientific-displays/ru-vdw-20261023')
        cls.reference = read_xyz(cls.source / 'reference.xyz')
        cls.scan = scan_settings(json.loads((cls.source / 'scan.json').read_text()))
        cls.data = import_projection(cls.reference, cls.source / 'distmap.txt', cls.source / 'scan.json',
                                     cls.source / 'mwfn_log.txt', cls.source / 'validity.csv')

    def small_scan(self, **changes):
        scan = {**self.scan, 'nx': 2, 'ny': 3, 'x_range_angstrom': [-2., 1.],
                'y_range_angstrom': [3., 5.], 'xy_offset_angstrom': [-2., 3.],
                'z_start_angstrom': 2., 'z_end_angstrom': -2.}
        return scan_settings({**scan, **changes})

    def test_real_points_against_independent_analytic_reference(self):
        data = self.data
        self.assertEqual(data.arrays['projection_depth'].shape, (61, 41))
        self.assertEqual(data.metadata['fields'], [])
        self.assertEqual(data.metadata['analysis']['counts'], {'missed': 1095, 'valid': 1406, 'unknown': 0})
        with (self.source / 'independent-reference.csv').open() as stream:
            for row in csv.DictReader(stream):
                ix, iy = int(row['ix']), int(row['iy'])
                self.assertLessEqual(abs(data.arrays['projection_depth'][ix, iy] - float(row['expected_depth_angstrom'])), DEPTH_TOLERANCE)
                self.assertEqual(data.arrays['projection_state'][ix, iy], int(row['sample_hits']))
                self.assertAlmostEqual(data.arrays['projection_x'][ix], float(row['x_angstrom']), places=6)
                self.assertAlmostEqual(data.arrays['projection_y'][iy], float(row['y_angstrom']), places=6)
        np.testing.assert_array_equal(data.arrays['positions'], self.reference.arrays['positions'])
        self.assertEqual(data.metadata['analysis']['reference_source'], self.reference.metadata['source']['sha256'])

    def test_unordered_non_square_grid_and_single_offset(self):
        text = '3 2 -1\n0 1 -2\n3 0 -3\n0 0 0\n3 1 -2.5\n0 2 -4\n'
        arrays = parse_grid(text, self.small_scan())
        np.testing.assert_array_equal(arrays['projection_x'], [-2, 1])
        np.testing.assert_array_equal(arrays['projection_y'], [3, 4, 5])
        np.testing.assert_array_equal(arrays['projection_depth'], [[0, -2, -4], [-3, -2.5, -1]])
        self.assertEqual(arrays['projection_state'][0, 0], VALID)
        self.assertEqual(arrays['projection_state'][0, 2], UNKNOWN)
        absolute = '\n'.join(f'{float(a)-2} {float(b)+3} {c}' for a, b, c in (line.split() for line in text.splitlines()))
        second = parse_grid(absolute, self.small_scan(xy_mode='absolute', xy_offset_angstrom=[0., 0.]))
        np.testing.assert_array_equal(second['projection_x'], arrays['projection_x'])
        with self.assertRaisesRegex(ValueError, 'offset'):
            parse_grid(absolute, self.small_scan())

    def test_reject_missing_duplicate_nonfinite_and_nonregular_grid(self):
        valid = '0 0 0\n0 1 -1\n0 2 -2\n3 0 -3\n3 1 -4\n3 2 -1\n'
        for text in (valid.rsplit('\n', 2)[0], valid.replace('3 2 -1', '3 1 -1'),
                     valid.replace('3 2 -1', '3 2 nan'), valid.replace('3 2 -1', '3 1.5 -1'),
                     valid.replace('3 2 -1', '3 2 -1 7'), valid.replace('3 2 -1', '3 2 0.01'),
                     valid.replace('3 2 -1', '3 2 -4.01')):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_grid(text, self.small_scan())

    def test_bottom_unknown_without_mask_and_explicit_endpoint_hit(self):
        data = import_projection(self.reference, self.source / 'distmap.txt', self.source / 'scan.json', self.source / 'mwfn_log.txt')
        self.assertEqual(data.metadata['analysis']['counts'], {'missed': 0, 'valid': 1406, 'unknown': 1095})
        values = np.array([[-4., -4.], [-1., 0.]])
        mask = parse_mask('ix,iy,state\n0,0,1\n0,1,0\n1,0,2\n1,1,1\n', (2, 2), values, -4.)
        np.testing.assert_array_equal(mask, [[VALID, MISSED], [UNKNOWN, VALID]])
        for text in ('ix,iy,state\n0,0,0\n', 'ix,iy,state\n0,0,0\n0,0,1\n',
                     'ix,iy,state\n1,0,0\n', 'ix,iy,state\n4,0,1\n', 'ix,iy,state\n0,0,3\n'):
            with self.assertRaises(ValueError):
                parse_mask(text, (2, 2), values, -4.)

    def test_scan_units_scaling_offsets_and_log_identity(self):
        for changes in ({'coordinate_unit': 'bohr'}, {'depth_definition': 'z_start-z_hit'},
                        {'data_scale_factor': -1.}, {'xy_mode': 'guess'}, {'xy_offset_angstrom': [0., 0.]},
                        {'nx': True}, {'nx': 1000000}, {'z_step_angstrom': 0}, {'z_start_angstrom': -8},
                        {'radius_scale': float('nan')}):
            with self.subTest(changes=changes), self.assertRaises((ValueError, MemoryError)):
                scan_settings({**self.scan, **changes})
        log = (self.source / 'mwfn_log.txt').read_text()
        for changes in ({'nx': 62}, {'z_step_angstrom': .01}, {'radius_scale': .8}, {'producer_version': 'wrong'}):
            with self.assertRaises(ValueError):
                check_generation_log(log, {**self.scan, **changes})

    def test_dynamic_reference_rejected_before_file_reads(self):
        for marker in ({'trajectory': {'kind': 'xyz'}}, {'analysis': {'kind': 'IRC'}},
                       {'optimization': {'status': 'available'}}):
            ref = copy.deepcopy(self.reference)
            ref.metadata.update(marker)
            with self.assertRaisesRegex(ValueError, 'static scientific reference'):
                import_projection(ref, 'missing', 'missing', 'missing')

    def test_cold_dataset_and_csv_preserve_every_state_and_raw_value(self):
        base = ROOT / '.tmp/tests/runs/surface-projection'
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            directory = Path(temporary) / 'dataset'
            save_dataset(self.data, directory)
            loaded = load_dataset(directory)
            self.assertEqual(loaded.metadata, self.data.metadata)
            for name, value in self.data.arrays.items():
                np.testing.assert_array_equal(loaded.arrays[name], value)
            exported = export_dataset(directory, Path(temporary) / 'exports', 'PROJECTION')
            with (Path(exported['directory']) / 'surface_projection.csv').open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 2501)
            for row in rows:
                ix, iy = int(row['ix']), int(row['iy'])
                self.assertEqual(float(row['depth_angstrom']), self.data.arrays['projection_depth'][ix, iy])
                self.assertEqual(int(row['state']), self.data.arrays['projection_state'][ix, iy])

    def test_saved_contract_rejects_shifted_axes_and_invalid_states(self):
        for name, value in (('projection_x', self.data.arrays['projection_x'] - 7),
                            ('projection_state', np.full((61, 41), 3)),
                            ('projection_depth', np.zeros((41, 61)))):
            data = copy.deepcopy(self.data)
            data.arrays[name] = value
            with self.assertRaises(ValueError):
                data.validate()

    def test_contours_use_valid_cells_only_and_do_not_change_arrays(self):
        values = np.array([[-1., -2., -3.], [-2., -3., -4.]])
        positions = np.array([[[i, j, 0.] for j in range(3)] for i in range(2)])
        self.assertTrue(trace_contours(values, np.ones((2, 3), bool), positions, -2.5))
        states = np.full((2, 3), VALID)
        states[0, 1] = UNKNOWN
        self.assertFalse(trace_contours(values, states == VALID, positions, -2.5))
        before = {key: value.copy() for key, value in self.data.arrays.items()}
        lines = trace_contours(self.data.arrays['projection_depth'], self.data.arrays['projection_state'] == VALID,
                               grid_positions(self.data), -3.)
        self.assertTrue(lines)
        for name, value in before.items():
            np.testing.assert_array_equal(self.data.arrays[name], value)
        low, high = color_range(self.data)
        self.assertGreater(low, -12)
        self.assertLessEqual(high, 0)
        self.assertEqual(color_range(self.data, (-10., 0.)), (-10., 0.))
        with self.assertRaises(ValueError):
            color_range(self.data, (0., 0.))


if __name__ == '__main__':
    unittest.main()
