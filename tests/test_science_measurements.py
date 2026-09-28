import unittest
from types import SimpleNamespace

import numpy as np

from qcblender.measurements import measure
from qcblender.geometry import scientific_geometry


class MeasurementTests(unittest.TestCase):
    def test_values_and_ordered_sign(self):
        points = np.array([[0., 1., 0.], [0., 0., 0.], [1., 0., 0.], [1., 0., 1.]])
        self.assertAlmostEqual(measure('DISTANCE', points, [1, 2]), 1)
        self.assertAlmostEqual(measure('ANGLE', points, [1, 2, 3]), 90)
        self.assertAlmostEqual(measure('DIHEDRAL', points, [1, 2, 3, 4]), 90)
        points[3, 2] = -1
        self.assertAlmostEqual(measure('DIHEDRAL', points, [1, 2, 3, 4]), -90)
        points[3] = [1., -1., 0.]
        self.assertAlmostEqual(measure('DIHEDRAL', points, [1, 2, 3, 4]), 180)

    def test_valid_straight_angle_and_degenerate_steps(self):
        points = np.array([[0., 0., 0.], [1., 0., 0.], [2., 0., 0.], [3., 0., 0.]])
        self.assertAlmostEqual(measure('ANGLE', points, [1, 2, 3]), 180)
        self.assertAlmostEqual(measure('ANGLE', points, [2, 1, 3]), 0)
        for kind, atoms in [('DISTANCE', [1, 1]), ('ANGLE', [1, 2, 5]),
                            ('DIHEDRAL', [1, 2, 3, 4])]:
            with self.assertRaises(ValueError):
                measure(kind, points, atoms)
        points[0] = points[1]
        with self.assertRaisesRegex(ValueError, 'zero-length arm'):
            measure('ANGLE', points, [1, 2, 3])

    def test_source_optimization_and_irc_use_selected_real_step(self):
        source = np.array([[0., 0., 0.], [1., 0., 0.]])
        data = SimpleNamespace(metadata={'source': {'sha256': 'example'},
            'coordinate_unit': 'angstrom', 'optimization': {'status': 'available',
            'array': 'opt', 'steps': [{}, {}]}, 'analysis': {'kind': 'IRC', 'steps': [{}, {}]}},
            arrays={'atomic_numbers': np.array([1, 1]), 'positions': source,
                    'opt': np.array([source, source * 2]), 'irc_positions': np.array([source, source * 3])})
        for kind, step, expected in [('source', None, 1.), ('optimization', 2, 2.), ('irc', 2, 3.)]:
            positions, record = scientific_geometry(data, kind, step)
            self.assertAlmostEqual(measure('DISTANCE', positions, [1, 2]), expected)
            self.assertEqual(record['step'], step)


if __name__ == '__main__':
    unittest.main()
