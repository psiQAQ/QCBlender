"""Current scientific configurations, independent of Blender display meshes."""
import unittest
import copy

import numpy as np

from qcblender.association import compare_sources
from qcblender.data import Dataset


def trajectory():
    positions = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
    moved = positions.copy()
    moved[1, 0] = 1.2
    return Dataset({'source': {'sha256': 'fixture'}, 'coordinate_unit': 'angstrom',
                    'selected_job': 0, 'analysis': {'kind': 'IRC',
                    'steps': [{'step': 1}, {'step': 2}]}},
                   {'atomic_numbers': np.array([8, 1, 1]), 'positions': positions,
                    'irc_positions': np.array([positions, moved])})


class CurrentAssociation(unittest.TestCase):
    def test_different_current_irc_steps_are_not_associated(self):
        data = trajectory()
        with self.assertRaisesRegex(ValueError, 'Different geometries'):
            compare_sources(data, data, moving_kind='irc', moving_step=2)

    def test_both_roles_and_optimization_use_selected_coordinates(self):
        data = trajectory()
        data.metadata['optimization'] = {'status': 'available', 'array': 'optimization_positions',
                                         'steps': [{'step': 1}, {'step': 2}]}
        data.arrays['optimization_positions'] = data.arrays['irc_positions'].copy()
        originals = {key: value.copy() for key, value in data.arrays.items()}
        for kind in ('irc', 'optimization'):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(ValueError, 'Different geometries'):
                    compare_sources(data, data, reference_kind=kind, reference_step=2)
                result = compare_sources(data, data, reference_kind=kind, reference_step=2,
                                         moving_kind=kind, moving_step=2)
                self.assertEqual(result['max_error_angstrom'], 0.)
                self.assertEqual(result['reference_geometry']['step'], 2)
                self.assertEqual(result['moving_geometry']['kind'], kind)
                self.assertEqual(result['reference_geometry']['selected_job'], 0)
        for key, value in originals.items():
            np.testing.assert_array_equal(data.arrays[key], value)

    def test_static_position_arguments_and_rigid_transform_remain_compatible(self):
        reference = trajectory()
        moving = copy.deepcopy(reference)
        moving.arrays['positions'] += [3., -2., 1.]
        with self.assertRaisesRegex(ValueError, 'Different geometries'):
            compare_sources(reference, moving, False, .001)
        result = compare_sources(reference, moving, True, .001)
        np.testing.assert_allclose(result['translation_angstrom'], [-3., 2., -1.], atol=1e-12)
        self.assertEqual(result['version'], 2)
        self.assertEqual(result['reference_geometry']['kind'], 'source')
        self.assertIsNone(result['moving_geometry']['step'])

    def test_current_rigid_geometry_uses_both_selected_steps(self):
        reference = trajectory()
        moving = copy.deepcopy(reference)
        moving.arrays['irc_positions'][1] += [3., -2., 1.]
        result = compare_sources(reference, moving, True, .001, reference_kind='irc', reference_step=2,
                                 moving_kind='irc', moving_step=2)
        self.assertLess(result['max_error_angstrom'], 1e-12)
        np.testing.assert_allclose(result['translation_angstrom'], [-3., 2., -1.], atol=1e-12)

    def test_bad_identity_and_nonfinite_coordinates_are_rejected(self):
        reference = trajectory()
        for field, value in (('atomic_numbers', np.array([1, 8, 1])),
                             ('positions', np.full((3, 3), np.nan))):
            moving = copy.deepcopy(reference)
            moving.arrays[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                compare_sources(reference, moving)
        for kind, step in (('irc', 0), ('irc', 3), ('irc', True), ('source', 1), ('missing', None)):
            with self.subTest(kind=kind, step=step), self.assertRaises(ValueError):
                compare_sources(reference, reference, moving_kind=kind, moving_step=step)
        for tolerance in (0, -1, np.inf, np.nan):
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                compare_sources(reference, reference, tolerance_angstrom=tolerance)

    def test_linear_rigid_alignment_still_requires_unique_rotation(self):
        data = trajectory()
        data.arrays['positions'][:, 1] = 0.
        with self.assertRaisesRegex(ValueError, 'unique.*rotation'):
            compare_sources(data, data, True)


if __name__ == '__main__':
    unittest.main()
