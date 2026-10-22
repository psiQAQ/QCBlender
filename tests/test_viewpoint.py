"""Camera orientation contracts on real point geometry, independent of Blender."""
import unittest
from unittest.mock import patch

import numpy as np

from qcblender import viewpoint
from qcblender.viewpoint import choose_orientation


def rotation():
    matrix, _ = np.linalg.qr(np.random.default_rng(13).normal(size=(3, 3)))
    matrix[:, 0] *= np.linalg.det(matrix)
    return matrix


class ViewpointTests(unittest.TestCase):
    def assert_proper(self, basis):
        np.testing.assert_allclose(basis @ basis.T, np.eye(3), atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(basis), 1)

    def test_planar_rectangle_and_frame_aspect(self):
        points = np.array([[-4., -1, 0], [-4, 1, 0], [4, -1, 0], [4, 1, 0]])
        for aspect, long_axis in ((1, 0), (2, 0), (.5, 1)):
            result = choose_orientation(points, aspect=aspect)
            self.assert_proper(result.basis)
            self.assertAlmostEqual(abs(result.basis[2, 2]), 1)
            self.assertAlmostEqual(abs(result.basis[long_axis, 0]), 1)
            self.assertEqual(result.method, 'PCA')
            self.assertEqual(result.message, '')

    def test_rotated_planar_line_and_point_follow_reference(self):
        transform = rotation()
        cases = (
            np.array([[-4., -1, 0], [-4, 1, 0], [4, -1, 0], [4, 1, 0]]),
            np.array([[-3., 0, 0], [0, 0, 0], [3, 0, 0]]),
            np.zeros((1, 3)),
        )
        for points in cases:
            with self.subTest(points=points.tolist()):
                result = choose_orientation(points @ transform.T, reference_basis=transform.T)
                np.testing.assert_allclose(result.basis, transform.T, atol=1e-12)
                self.assert_proper(result.basis)

    def test_actual_span_overrides_variance_for_long_frame_axis(self):
        # Most points spread along X, but two Y endpoints define the longer span.
        x = np.linspace(-3, 3, 200)
        points = np.concatenate((np.column_stack((x, np.zeros_like(x), np.zeros_like(x))),
                                 [[0, -5, 0], [0, 5, 0]]))
        for mode in ('PCA', 'UNOBSTRUCTED'):
            for aspect, long_axis in ((2, 0), (.5, 1)):
                result = choose_orientation(points, mode, aspect=aspect)
                spans = np.ptp(points @ result.basis[:2].T, axis=0)
                self.assertGreaterEqual(spans[long_axis], spans[1 - long_axis])
                self.assert_proper(result.basis)

    def test_symmetric_and_nearly_symmetric_preserve_reference(self):
        transform = rotation()
        reference = transform.T
        cube = np.array([[x, y, z] for x in (-1., 1.) for y in (-1., 1.) for z in (-1., 1.)])
        for stretch in (1., 1 + 1e-7):
            points = cube * [stretch, 1., 1.]
            result = choose_orientation(points, reference_basis=reference, aspect=.6)
            np.testing.assert_allclose(result.basis, reference, atol=1e-12)
        # Circular plane has an ambiguous in-plane orientation, but a unique normal.
        angle = np.linspace(0, 2 * np.pi, 80, endpoint=False)
        ring = np.column_stack((np.cos(angle), np.sin(angle), np.zeros(80)))
        result = choose_orientation(ring @ transform.T, reference_basis=reference)
        np.testing.assert_allclose(result.basis, reference, atol=1e-12)

    def test_transform_invariance_for_both_modes(self):
        points = np.random.default_rng(3).normal(size=(300, 3)) * [5, 2, .4]
        transform = rotation()
        for mode in ('PCA', 'UNOBSTRUCTED'):
            expected = choose_orientation(points, mode)
            moved = choose_orientation(points * 1e-8 + [3e-7, -4e-7, 8e-7], mode)
            np.testing.assert_allclose(moved.basis, expected.basis, atol=1e-11)
            self.assertAlmostEqual(moved.score, expected.score)
            turned = choose_orientation(points @ transform.T, mode, reference_basis=transform.T)
            np.testing.assert_allclose(turned.basis, expected.basis @ transform.T, atol=1e-11)
            self.assertAlmostEqual(turned.score, expected.score)

    def test_single_point_and_extreme_finite_scales(self):
        for mode in ('PCA', 'UNOBSTRUCTED'):
            point = choose_orientation([[1e300, -1e300, 3]], mode)
            np.testing.assert_array_equal(point.basis, np.eye(3))
            result = choose_orientation([[-1e308, 0, 0], [1e308, 0, 0]], mode)
            self.assert_proper(result.basis)
        for scale in (1e-250, 1e250):
            result = choose_orientation(np.array([[-2., -1, 0], [-2, 1, 0], [2, -1, 0], [2, 1, 0]]) * scale)
            np.testing.assert_array_equal(result.basis, np.eye(3))

    def test_invalid_geometry_aspect_reference_and_mode(self):
        for points in ([], [1, 2, 3], [[1, 2]], [[0, 0, np.nan]], [[0, np.inf, 0]]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                choose_orientation(points)
        for aspect in (0, -1, np.nan, np.inf, 'invalid', None):
            with self.subTest(aspect=aspect), self.assertRaises(ValueError):
                choose_orientation([[0, 0, 0]], aspect=aspect)
        for basis in (np.diag([1, 1, -1]), np.eye(3) * 2, np.zeros((2, 3)),
                      [[np.nan, 0, 0], [0, 1, 0], [0, 0, 1]]):
            with self.subTest(basis=basis), self.assertRaises(ValueError):
                choose_orientation([[0, 0, 0]], reference_basis=basis)
        with self.assertRaises(ValueError):
            choose_orientation([[0, 0, 0]], 'CURRENT')

    def test_deterministic_immutable_input_and_proper_results(self):
        points = np.random.default_rng(12).normal(size=(700, 3)) * [3, 1, .3]
        reference = rotation()
        original, original_reference = points.copy(), reference.copy()
        points.flags.writeable = False
        reference.flags.writeable = False
        for mode in ('PCA', 'UNOBSTRUCTED'):
            first = choose_orientation(points, mode, reference, aspect=.75)
            second = choose_orientation(points, mode, reference, aspect=.75)
            np.testing.assert_array_equal(first.basis, second.basis)
            self.assertEqual(first.score, second.score)
            self.assert_proper(first.basis)
        np.testing.assert_array_equal(points, original)
        np.testing.assert_array_equal(reference, original_reference)

    def test_layered_structure_visibility_improves_over_pca(self):
        x, y = np.meshgrid(np.linspace(-4, 4, 25), np.linspace(-2, 2, 17))
        plane = np.column_stack((x.ravel(), y.ravel(), np.zeros(x.size)))
        points = np.concatenate([plane + [0, 0, z] for z in (-.5, 0, .5)])
        pca = choose_orientation(points)
        result = choose_orientation(points, 'UNOBSTRUCTED')
        self.assertGreater(result.score, pca.score + .15)
        self.assertGreater(np.linalg.norm(result.basis[2, :2]), .1)
        self.assert_proper(result.basis)

    def test_large_geometry_has_bounded_scoring_and_candidate_count(self):
        points = np.random.default_rng(20).normal(size=(100003, 3))
        sizes = []
        score = viewpoint._visibility_score

        def observed(sample, basis):
            sizes.append(len(sample))
            return score(sample, basis)

        with patch.object(viewpoint, '_visibility_score', side_effect=observed):
            result = choose_orientation(points, 'UNOBSTRUCTED')
        self.assertTrue(sizes)
        self.assertLessEqual(max(sizes), 4096)
        self.assertLessEqual(len(sizes), 147)
        self.assert_proper(result.basis)


if __name__ == '__main__':
    unittest.main()
