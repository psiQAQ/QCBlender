"""The layout shared by horizontal and vertical GN legends."""
import unittest

from qcblender.blender.legend_layout import LAYOUT, coordinate


class LegendLayout(unittest.TestCase):
    def test_default_horizontal_positions_match_saved_legend(self):
        actual = {name: tuple(coordinate(axis, 2, .18, .16) for axis in axes)
                  for name, axes in LAYOUT['horizontal'].items()}
        for name, expected in {'minimum': (-1, -.28), 'center': (-.2, -.28),
                               'maximum': (.65, -.28), 'title': (-1, .2)}.items():
            self.assertAlmostEqual(actual[name][0], expected[0])
            self.assertAlmostEqual(actual[name][1], expected[1])

    def test_vertical_labels_stay_beside_bar_at_variable_size(self):
        length, width, size = 3, .3, .2
        actual = {name: tuple(coordinate(axis, length, width, size) for axis in axes)
                  for name, axes in LAYOUT['vertical'].items()}
        self.assertEqual(actual['minimum'][0], actual['center'][0])
        self.assertEqual(actual['center'][0], actual['maximum'][0])
        self.assertGreater(actual['minimum'][0], width / 2)
        self.assertLess(actual['minimum'][1], actual['center'][1])
        self.assertLess(actual['center'][1], actual['maximum'][1])
        self.assertGreater(actual['title'][1], length / 2)


if __name__ == '__main__':
    unittest.main()
