import unittest
from types import SimpleNamespace

import numpy as np

from qcblender.geometry import scientific_geometry


class ScientificGeometryTests(unittest.TestCase):
    def test_real_step_and_immutable_result(self):
        source = np.array([[0., 0., 0.], [1., 0., 0.]])
        data = SimpleNamespace(metadata={'source': {'sha256': 'fixture'}, 'coordinate_unit': 'angstrom',
            'selected_job': 2, 'optimization': {'status': 'available', 'array': 'trajectory',
            'steps': [{'step': 1}, {'step': 2}]}, 'analysis': {'kind': 'IRC',
            'steps': [{'sha256': 'first'}, {'sha256': 'second'}]}}, arrays={
            'positions': source, 'atomic_numbers': np.array([1, 1]),
            'trajectory': np.array([source, source * 2]), 'irc_positions': np.array([source, source * 3])})
        for kind, step, distance in [('source', None, 1), ('optimization', 2, 2), ('irc', 2, 3)]:
            positions, record = scientific_geometry(data, kind, step)
            self.assertEqual(np.linalg.norm(positions[1] - positions[0]), distance)
            self.assertEqual(record['step'], step)
            self.assertEqual(record['selected_job'], 2)
            self.assertFalse(positions.flags.writeable)
        for kind, step in [('source', 1), ('irc', 0), ('optimization', 3), ('irc', True)]:
            with self.assertRaises(ValueError):
                scientific_geometry(data, kind, step)
        data.metadata['coordinate_unit'] = 'bohr'
        with self.assertRaisesRegex(ValueError, 'angstrom'):
            scientific_geometry(data)


if __name__ == '__main__':
    unittest.main()
