"""Pure checks for affine source grid and associated atom plane geometry."""
import itertools
import unittest

import numpy as np

from qcblender.planes import plane_frame


class PlaneFrames(unittest.TestCase):
    def setUp(self):
        self.field = {'shape': [5, 4, 3], 'origin': [1, -2, .5],
                      'steps': [[.8, .2, .1], [.1, .7, .15], [.05, .2, .6]]}
        self.transform = np.array([[2, .1, 0, 3], [0, .7, .2, -1], [0, 0, 1.5, 2], [0, 0, 0, 1.]])

    def test_grid_planes_contain_affine_sections(self):
        for mode, fixed in (('ij', 2), ('jk', 0), ('ki', 1)):
            with self.subTest(mode=mode):
                center, axes, width, height = plane_frame(self.field, mode, self.transform)
                self.assertAlmostEqual(np.linalg.det(axes), 1.)
                np.testing.assert_allclose(axes.T @ axes, np.eye(3), atol=1e-12)
                indices = np.array(list(itertools.product(*[(0, n-1) for n in self.field['shape']])), dtype=float)
                indices[:, fixed] = .5 * (self.field['shape'][fixed]-1)
                source = indices @ self.field['steps'] + self.field['origin']
                points = source @ self.transform[:3, :3].T + self.transform[:3, 3]
                local = (points-center) @ axes
                np.testing.assert_allclose(local[:, 2], 0, atol=1e-12)
                self.assertLessEqual(np.abs(local[:, 0]).max(), width/2 + 1e-12)
                self.assertLessEqual(np.abs(local[:, 1]).max(), height/2 + 1e-12)

    def test_atom_plane_intersection_and_invalid_definitions(self):
        atoms = np.array([[1.8, -1, 1], [2.8, -1, 1], [1.8, 0, 1],
                          [1.8, -1, 2], [3.8, -1, 1]])
        center, axes, width, height = plane_frame(self.field, 'atoms', np.eye(4), atoms=atoms,
                                                    source_numbers=(1, 2, 3))
        self.assertGreater(width * height, 0)
        self.assertAlmostEqual(float((atoms[0]-center) @ axes[:, 2]), 0)
        moved = np.eye(4)
        moved[2, 3] = .25
        moved_center, moved_axes, _, _ = plane_frame(self.field, 'atoms', np.eye(4),
            atoms=atoms, source_numbers=(1, 2, 3), atom_to_view=moved)
        self.assertAlmostEqual(float((atoms[0] + [0, 0, .25] - moved_center) @ moved_axes[:, 2]), 0)
        for numbers in ((1, 1, 2), (1, 2, 9), (1, 2, 5)):
            with self.assertRaises(ValueError):
                plane_frame(self.field, 'atoms', np.eye(4), atoms=atoms, source_numbers=numbers)
        with self.assertRaises(ValueError):
            plane_frame(self.field, 'ij', self.transform, position=1.1)
        broken = self.transform.copy()
        broken[0, 0] = 0
        broken[1, 1] = 0
        broken[2, 2] = 0
        with self.assertRaises(ValueError):
            plane_frame(self.field, 'ij', broken)


if __name__ == '__main__':
    unittest.main()
