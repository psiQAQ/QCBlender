import unittest

import numpy as np

from tools.visual_regression import check_identity, compare_pixels


class VisualRegression(unittest.TestCase):
    def test_localized_label_change_cannot_hide_in_background(self):
        expected = np.zeros((100, 100, 3))
        actual = expected.copy()
        actual[10:12, 10:12] = 1
        result = compare_pixels(actual, expected, {'label': [10, 10, 20, 20]})
        self.assertEqual(result['regions']['full']['status'], 'Passed')
        self.assertEqual(result['regions']['label']['status'], 'Failed')
        self.assertEqual(result['status'], 'Failed')

    def test_single_channel_difference_counts_as_changed_pixel(self):
        expected = np.zeros((10, 10, 3))
        actual = expected.copy()
        actual[:2, :, 0] = 9 / 255
        result = compare_pixels(actual, expected, {})
        self.assertEqual(result['regions']['full']['changed_pixel_fraction'], .2)
        self.assertEqual(result['status'], 'Failed')

    def test_unchanged_image_and_subthreshold_noise_pass(self):
        expected = np.full((10, 10, 3), .5)
        for actual in (expected.copy(), expected + .001):
            self.assertEqual(compare_pixels(actual, expected, {})['status'], 'Passed')

    def test_bad_images_and_regions_fail_instead_of_skipping(self):
        expected = np.zeros((10, 10, 3))
        for actual, regions in ((np.zeros((9, 10, 3)), {}),
                                (np.full_like(expected, np.nan), {}),
                                (np.full_like(expected, 2), {}),
                                (expected, {'outside': [0, 0, 11, 10]})):
            with self.subTest(regions=regions, shape=actual.shape), self.assertRaises(ValueError):
                compare_pixels(actual, expected, regions)

    def test_environment_and_scientific_identity_are_required(self):
        expected = dict(environment='Blender 5.1.1', scene='MO8', input_sha256='a', scientific_arrays='b')
        check_identity(expected, expected.copy())
        for key in expected:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                check_identity({**expected, key: 'changed'}, expected)


if __name__ == '__main__':
    unittest.main()
