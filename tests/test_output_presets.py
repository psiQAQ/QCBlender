"""Output contracts independent of Blender and render hardware."""

import math
import unittest

from qcblender.output_presets import PRESET_VERSION, QUALITY_PRESETS, lighting_layout, output_plan


class OutputPresets(unittest.TestCase):
    def test_quality_cost_and_noise_targets_are_explicit(self):
        self.assertEqual(PRESET_VERSION, 1)
        preview, standard, high = (QUALITY_PRESETS[name] for name in ('PREVIEW', 'STANDARD', 'HIGH'))
        self.assertEqual((preview.engine, preview.samples, preview.adaptive_threshold),
                         ('BLENDER_EEVEE', 64, None))
        self.assertEqual((standard.engine, standard.samples, standard.adaptive_threshold),
                         ('CYCLES', 128, .02))
        self.assertEqual((high.engine, high.samples, high.adaptive_threshold), ('CYCLES', 512, .005))

    def test_background_choices_and_no_mutation_of_input_color(self):
        color = [.2, .4, .6]
        self.assertEqual(output_plan(background='WHITE', background_color=color)['background_color'], (1., 1., 1.))
        self.assertEqual(output_plan(background='BLACK')['background_color'], (0., 0., 0.))
        custom = output_plan(background='CUSTOM', background_color=color, denoise=False)
        self.assertEqual(custom['background_color'], (.2, .4, .6))
        self.assertFalse(custom['denoise'])
        color[0] = .9
        self.assertEqual(custom['background_color'], (.2, .4, .6))
        self.assertEqual(output_plan(background='TRANSPARENT')['background'], 'TRANSPARENT')

    def test_invalid_choices_fail_before_mutation(self):
        for arguments in [{'quality': 'ULTRA'}, {'background': 'BLUE'}, {'denoise': 'yes'},
                          {'resolution_x': 0}, {'resolution_y': -1}, {'resolution_x': True},
                          {'resolution_percentage': 101}, {'resolution_percentage': 1.5},
                          {'background_color': [0, 1]}, {'background_color': [0, 1, math.nan]},
                          {'background_color': [-.1, 0, 0]}, {'background_color': [0, 0, 1.1]}]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                output_plan(**arguments)

    def test_light_size_position_and_power_follow_subject_scale(self):
        points = [(-2., -1., -.5), (2., 1., .5)]
        first = lighting_layout(points)
        second = lighting_layout([tuple(value * 3 for value in point) for point in points])
        self.assertEqual(first['scale'], 4.)
        self.assertEqual(first['center'], (0., 0., 0.))
        self.assertEqual([item['role'] for item in first['lights']], ['KEY', 'FILL', 'RIM'])
        for one, two in zip(first['lights'], second['lights']):
            self.assertEqual(two['location'], tuple(value * 3 for value in one['location']))
            self.assertAlmostEqual(two['size'], one['size'] * 3)
            self.assertAlmostEqual(two['energy'], one['energy'] * 9)
            self.assertAlmostEqual(one['energy'] / one['size'] ** 2, two['energy'] / two['size'] ** 2)

    def test_rigid_camera_and_subject_motion_preserves_relative_lighting(self):
        points = [(-2., -1., -.5), (2., 1., .5)]
        transform = lambda point: (-point[1] + 7., point[0] - 2., point[2] + 3.)
        first = lighting_layout(points)
        second = lighting_layout([transform(point) for point in points],
                                 right=(0., 1., 0.), up=(-1., 0., 0.))
        self.assertEqual(second['center'], transform(first['center']))
        for one, two in zip(first['lights'], second['lights']):
            self.assertEqual(two['location'], transform(one['location']))
            self.assertEqual((two['size'], two['energy']), (one['size'], one['energy']))

    def test_invalid_geometry_and_camera_basis_fail_explicitly(self):
        for points, kwargs in [([], {}), ([(0, 0, 0)], {}), ([(0, 0), (1, 1)], {}),
                               ([(0, 0, 0), (1, 1, math.inf)], {}),
                               ([(0, 0, 0), (1, 1, 1)], {'right': (2, 0, 0)}),
                               ([(0, 0, 0), (1, 1, 1)], {'up': (1, 0, 0)})]:
            with self.subTest(points=points, kwargs=kwargs), self.assertRaises(ValueError):
                lighting_layout(points, **kwargs)


if __name__ == '__main__':
    unittest.main()
