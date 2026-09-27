import unittest
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qcblender.framing import fit_orthographic


class Framing(unittest.TestCase):
    def check_frame(self, points, basis, aspect, margin):
        location, scale, clip_end = fit_orthographic(points, basis, aspect, margin)
        projected = (np.asarray(points) - location) @ np.asarray(basis).T
        width = scale * min(1, aspect)
        height = scale * min(1, 1 / aspect)
        self.assertLessEqual(np.max(np.abs(projected[:, 0])), width * (0.5 - margin) + 1e-9)
        self.assertLessEqual(np.max(np.abs(projected[:, 1])), height * (0.5 - margin) + 1e-9)
        self.assertLess(np.max(projected[:, 2]), 0)
        self.assertGreater(clip_end, -np.min(projected[:, 2]))
        return scale

    def test_landscape_portrait_and_pixel_aspect(self):
        points = [[-2, -1, -1], [2, 1, 1]]
        identity = np.eye(3)
        self.assertAlmostEqual(self.check_frame(points, identity, 2, .05), 4 / .9)
        self.assertAlmostEqual(self.check_frame(points, identity, .5, .05), 8 / .9)
        self.assertAlmostEqual(self.check_frame(points, identity, 1, 0), 4)

    def test_rotation_and_multiple_views(self):
        basis = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
        points = [[-2, 0, 0], [3, 0, 1], [0, 2, 0]]
        self.assertAlmostEqual(self.check_frame(points, basis, 2, .05), 10 / .9)

    def test_single_point_and_zero_span(self):
        self.assertGreater(self.check_frame([[1, 2, 3]], np.eye(3), 1, .05), 0)
        self.assertAlmostEqual(self.check_frame([[0, -1, 0], [0, 1, 0]], np.eye(3), 2, 0), 4)

    def test_invalid_inputs(self):
        for points in ([], [[float('nan'), 0, 0]], [[1, 2]], [[float('inf'), 0, 0]]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                fit_orthographic(points, np.eye(3), 1)
        for aspect, margin, basis in ((0, .05, np.eye(3)), (1, .5, np.eye(3)),
                                      (1, -.01, np.eye(3)), (1, .05, np.zeros((3, 3)))):
            with self.subTest(aspect=aspect, margin=margin), self.assertRaises(ValueError):
                fit_orthographic([[0, 0, 0]], basis, aspect, margin)


if __name__ == '__main__':
    unittest.main()
