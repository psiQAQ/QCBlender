import unittest
from types import SimpleNamespace

import numpy as np

from qcblender.measurements import (annotation_prefix, geometry_label, measure, measurement_text, parse_source_atom_numbers,
                                     validate_annotation_style)
from qcblender.geometry import scientific_geometry


class MeasurementTests(unittest.TestCase):
    def test_default_and_exact_custom_prefixes_keep_value_and_unit(self):
        record = {'kind': 'irc', 'step': 2}
        self.assertEqual(annotation_prefix('ATOM', [3]), '')
        self.assertEqual(measurement_text('DISTANCE', [1, 2], 1.23456, record, 4,
                         prefix_mode='DEFAULT'), 'Distance(1,2) = 1.2346 Å')
        self.assertEqual(measurement_text('ANGLE', [1, 2, 3], 90., record, 2,
                         prefix_mode='DEFAULT'), 'Angle(1,2,3) = 90.00 °')
        for prefix in ('', '   ', '测量：', 'Custom = '):
            self.assertEqual(measurement_text('DISTANCE', [1, 2], 1.2, record, 2,
                             prefix_mode='CUSTOM', prefix=prefix), prefix + '1.20 Å')
        self.assertEqual(measurement_text('DIHEDRAL', [1, 2, 3, 4], None, record, 2,
                         'zero-length central bond', prefix_mode='DEFAULT'),
                         'Dihedral(1,2,3,4) = undefined (zero-length central bond) °')

    def test_update_style_does_not_consult_saved_color(self):
        style = {'size': .16, 'line_width': .01, 'offset': [0., 0., 0.], 'decimals': 4}
        validate_annotation_style(style, validate_color=False)
        validate_annotation_style({**style, 'color': 'user owns material'}, validate_color=False)
        for key in ('measurement_width', 'arc_radius'):
            with self.assertRaises(ValueError):
                validate_annotation_style({**style, key: float('nan')}, validate_color=False)

    def test_source_numbers_and_visible_geometry_context(self):
        self.assertEqual(parse_source_atom_numbers('1, 3 2', 3), [1, 3, 2])
        for expression in ('1,1', '0,2', '1,4', '1-2', '', '1,,2', '1,', ',1'):
            with self.assertRaises(ValueError):
                parse_source_atom_numbers(expression, 3)
        self.assertEqual(geometry_label({'kind': 'source', 'step': None}), 'Source geometry')
        self.assertEqual(geometry_label({'kind': 'optimization', 'step': 3}), 'Optimization Step 3')
        self.assertEqual(geometry_label({'kind': 'irc', 'step': 2}), 'IRC Step 2')
        self.assertEqual(measurement_text('DISTANCE', [1, 2], 1.23456,
                         {'kind': 'source', 'step': None}, 4), '1-2 · Source geometry: 1.2346 Å')
        self.assertIn('Optimization Step 3: undefined', measurement_text('DIHEDRAL', [1, 2, 3, 4],
                      None, {'kind': 'optimization', 'step': 3}, 2, 'terminal arm lies on central axis'))
        with self.assertRaises(ValueError):
            geometry_label({'kind': 'irc', 'step': None})

    def test_nonfinite_style_rejected_before_annotation_mutation(self):
        style = {'size': .16, 'line_width': .01, 'color': [1., .8, .2],
                 'offset': [.2, .2, .2], 'decimals': 4}
        validate_annotation_style(style)
        for name, invalid in [('size', float('nan')), ('line_width', float('inf')),
                              ('color', [1., float('nan'), 0.]),
                              ('offset', [0., float('inf'), 0.])]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_annotation_style({**style, name: invalid})

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
        self.assertEqual(measure('DISTANCE', points, [1, 2]), 0.)
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
