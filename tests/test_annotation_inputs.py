"""Source-number entry boundaries, independent of Blender's numeric widgets."""
import unittest

from qcblender.annotation_inputs import edit_numbers, resize_numbers


class AnnotationNumberInputs(unittest.TestCase):
    def test_steps_and_typed_values_clamp_to_range(self):
        self.assertEqual(edit_numbers([3, 6], [0, 99], 8), [1, 8])
        self.assertEqual(edit_numbers([3, 6], [4, 6], 8), [4, 6])
        self.assertEqual(edit_numbers([3, 6], [2, 6], 8), [2, 6])

    def test_duplicate_keeps_previous_number_without_skip(self):
        self.assertEqual(edit_numbers([1, 2, 3, 4], [2, 2, 3, 4], 8), [1, 2, 3, 4])
        self.assertEqual(edit_numbers([1, 3], [3, 3], 8), [1, 3])
        self.assertEqual(edit_numbers([1, 3], [1, 1], 8), [1, 3])

    def test_clamp_to_occupied_boundary_is_rejected(self):
        self.assertEqual(edit_numbers([1, 3], [1, -100], 8), [1, 3])
        self.assertEqual(edit_numbers([3, 8], [100, 8], 8), [3, 8])

    def test_same_value_and_single_atom_are_stable(self):
        self.assertEqual(edit_numbers([1], [99], 1), [1])
        self.assertEqual(edit_numbers([1, 2, 3, 4], [1, 2, 3, 4], 4), [1, 2, 3, 4])

    def test_batch_growth_uses_unused_numbers_and_retains_order(self):
        self.assertEqual(resize_numbers([4, 2], 5, 5), [4, 2, 1, 3, 5])
        self.assertEqual(resize_numbers([4, 2], 99, 4), [4, 2, 1, 3])
        self.assertEqual(resize_numbers([4, 2, 3], 0, 4), [4])

    def test_invalid_starting_state_is_not_silently_repaired(self):
        for previous, proposed, count in [([1, 1], [1, 2], 4), ([5], [1], 4), ([1], [2], 0), ([1], [], 4)]:
            with self.subTest(previous=previous, count=count), self.assertRaises(ValueError):
                edit_numbers(previous, proposed, count)


if __name__ == '__main__':
    unittest.main()
