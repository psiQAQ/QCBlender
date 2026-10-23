"""Calculated pair identity and all-step color ranges using the real P04 records."""
import copy
from pathlib import Path
import unittest

import numpy as np

from qcblender.irc import import_irc, import_irc_mayer
from qcblender.mayer import color_range, display_samples, validate_binding


class MayerDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / 'validation/shared/data/public/P04'
        cls.path = import_irc(source / 'steps.csv')
        cls.mayer = import_irc_mayer(cls.path, source / 'mayer-pyscf.csv')

    def test_actual_pairs_include_non_geometry_bonds(self):
        geometry = {tuple(sorted(pair)) for pair in self.path.arrays['bonds'].tolist()}
        calculated = {tuple(pair - 1) for pair in self.mayer.arrays['mayer_pairs']}
        self.assertTrue(calculated - geometry)
        before = {name: array.copy() for name, array in self.mayer.arrays.items()}
        for step in (1, 2, 3):
            positions, atom_ids, values, pair_ids = display_samples(self.path, self.mayer, step)
            np.testing.assert_array_equal(positions, self.path.arrays['irc_positions'][step - 1][atom_ids])
            np.testing.assert_array_equal(atom_ids.reshape(-1, 2) + 1, self.mayer.arrays['mayer_pairs'])
            np.testing.assert_array_equal(values.reshape(-1, 2)[:, 0], self.mayer.arrays['mayer_orders'][step - 1])
            np.testing.assert_array_equal(values[::2], values[1::2])
            np.testing.assert_array_equal(pair_ids, np.repeat(np.arange(1, 7), 2))
        for name in before:
            np.testing.assert_array_equal(self.mayer.arrays[name], before[name])

    def test_full_path_range_and_manual_validation(self):
        values = self.mayer.arrays['mayer_orders']
        self.assertEqual(color_range(self.mayer), (values.min(), values.max()))
        self.assertEqual(color_range(self.mayer, (-.1, 1.2)), (-.1, 1.2))
        for bad in ((1, 1), (1, 0), (float('nan'), 2), (0, float('inf'))):
            with self.assertRaises(ValueError):
                color_range(self.mayer, bad)
        constant = copy.deepcopy(self.mayer)
        constant.arrays['mayer_orders'][:] = .5
        self.assertEqual(color_range(constant), (.5, .5))

    def test_reject_invalid_pairs_values_and_source_identity(self):
        for bad_pairs in (np.array([[1, 1]]), np.array([[0, 2]]), np.array([[1, 5]]),
                          np.array([[2, 1]]), np.array([[1., 2.]]), np.array([[1, 2], [1, 2]])):
            data = copy.deepcopy(self.mayer)
            data.arrays['mayer_pairs'] = bad_pairs
            with self.assertRaises(ValueError):
                data.validate()
        data = copy.deepcopy(self.mayer)
        data.arrays['mayer_orders'] = data.arrays['mayer_orders'][:, :-1]
        with self.assertRaises(ValueError):
            data.validate()
        data = copy.deepcopy(self.mayer)
        data.arrays['mayer_orders'][1, 0] = np.nan
        with self.assertRaises(ValueError):
            data.validate()
        for key, value in [('path_source', 'different'), ('path_steps', ['different'] * 3)]:
            data = copy.deepcopy(self.mayer)
            data.metadata['analysis'][key] = value
            with self.assertRaises(ValueError):
                validate_binding(self.path, data)
        data = copy.deepcopy(self.mayer)
        data.arrays['atomic_numbers'][0] = 1
        with self.assertRaises(ValueError):
            validate_binding(self.path, data)

    def test_degenerate_pair_and_out_of_range_step(self):
        for step in (0, 4, 1.5):
            with self.assertRaises(ValueError):
                display_samples(self.path, self.mayer, step)
        path = copy.deepcopy(self.path)
        path.arrays['irc_positions'][1, 1] = path.arrays['irc_positions'][1, 0]
        with self.assertRaisesRegex(ValueError, 'nonzero separation'):
            display_samples(path, self.mayer, 2)

    def test_legacy_mayer_record_keeps_declared_association(self):
        data = copy.deepcopy(self.mayer)
        del data.metadata['analysis']['path_steps']
        validate_binding(self.path, data)


if __name__ == '__main__':
    unittest.main()
