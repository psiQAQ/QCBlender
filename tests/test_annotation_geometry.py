"""Scientific sign conventions and symmetric display geometry contracts."""
import unittest
import numpy as np

from qcblender.annotation_geometry import (distance_dashes, angle_arc, dihedral_arc,
                                           dihedral_planes, measurement_geometry)


class AnnotationGeometry(unittest.TestCase):
    def test_dashes_have_equal_gaps_and_symmetric_endpoints(self):
        first, last = np.array([1., -2., .3]), np.array([2.3, 1., .1])
        segments = distance_dashes(first, last)
        np.testing.assert_allclose(segments[0, 0], first)
        np.testing.assert_allclose(segments[-1, 1], last)
        lengths = np.linalg.norm(segments[:, 1] - segments[:, 0], axis=1)
        gaps = np.linalg.norm(segments[1:, 0] - segments[:-1, 1], axis=1)
        np.testing.assert_allclose(lengths, lengths[0])
        np.testing.assert_allclose(gaps, lengths[0])
        np.testing.assert_allclose(segments + segments[::-1, ::-1], np.broadcast_to(first + last, segments.shape))

    def test_zero_and_short_distance_no_invalid_segments(self):
        self.assertEqual(distance_dashes([0, 0, 0], [0, 0, 0]).shape, (0, 2, 3))
        short = distance_dashes([0, 0, 0], [.001, 0, 0])
        self.assertEqual(short.shape, (1, 2, 3))
        np.testing.assert_allclose(short[0], [[0, 0, 0], [.001, 0, 0]])

    def test_angle_arc_radius_endpoints_and_straight_boundary(self):
        points = np.array([[1., 0., 0.], [0., 0., 0.], [0., 1., 0.]])
        arc = angle_arc(points)
        np.testing.assert_allclose(np.linalg.norm(arc - points[1], axis=1), .5)
        np.testing.assert_allclose(arc[[0, -1]], [[.5, 0., 0.], [0., .5, 0.]], atol=1e-12)
        points[2] = [-1., 0., 0.]
        straight = angle_arc(points)
        np.testing.assert_allclose(straight[-1], [-.5, 0., 0.], atol=1e-12)
        self.assertTrue(np.isfinite(straight).all())
        points[2] = [2., 0., 0.]
        self.assertEqual(angle_arc(points).shape, (0, 3))

    def test_dihedral_arc_uses_signed_central_axis_and_midpoint(self):
        points = np.array([[0., 1., 0.], [0., 0., 0.], [2., 0., 0.], [2., 0., 1.]])
        arc = dihedral_arc(points)
        np.testing.assert_allclose(arc[[0, -1]], [[1., .5, 0.], [1., 0., .5]], atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(arc - [1., 0., 0.], axis=1), .5)
        points[-1, -1] = -1
        np.testing.assert_allclose(dihedral_arc(points)[-1], [1., 0., -.5], atol=1e-12)
        points[-1] = [2., -1., 0.]
        np.testing.assert_allclose(dihedral_arc(points)[-1], [1., -.5, 0.], atol=1e-12)

    def test_planes_are_source_atom_triangles_and_undefined_steps_have_no_parts(self):
        points = np.array([[0., 1., 0.], [0., 0., 0.], [1., 0., 0.], [1., 0., 1.]])
        np.testing.assert_array_equal(dihedral_planes(points), points[[[0, 1, 2], [1, 2, 3]]])
        points[0] = [-1., 0., 0.]
        geometry = measurement_geometry('DIHEDRAL', points, [1, 2, 3, 4])
        self.assertTrue(all(len(part) == 0 for part in geometry.values()))

    def test_rigid_transform_preserves_arc_shape_and_ordered_sign(self):
        points = np.array([[0., 1., 0.], [0., 0., 0.], [1., 0., 0.], [1., 0., -1.]])
        rotation, _ = np.linalg.qr(np.random.default_rng(17).normal(size=(3, 3)))
        if np.linalg.det(rotation) < 0:
            rotation[:, 0] *= -1
        translation = np.array([4., -1., 3.])
        transformed = points @ rotation.T + translation
        np.testing.assert_allclose(dihedral_arc(transformed), dihedral_arc(points) @ rotation.T + translation)
        np.testing.assert_allclose(angle_arc(transformed[:3]), angle_arc(points[:3]) @ rotation.T + translation)
        np.testing.assert_allclose(dihedral_planes(transformed), dihedral_planes(points) @ rotation.T + translation)


if __name__ == '__main__':
    unittest.main()
