import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from qcblender.atom_selection import combine_numbers, evaluate_steps, parse_numbers, select_numbers


class AtomSelectionTests(unittest.TestCase):
    def setUp(self):
        self.positions = np.array([[0., 0., 0.], [1., 0., 0.], [3., 0., 0.],
                                   [0., 4., 0.], [9., 0., 0.]])

    def test_source_numbers_and_distance_boundary(self):
        self.assertEqual(parse_numbers('1, 3,3-4', 5), (1, 3, 4))
        self.assertEqual(select_numbers(self.positions, (1, 3), 2.), (1, 2, 3))
        self.assertEqual(select_numbers(self.positions, (1,), 0., False), ())
        for text in ('', '0', '6', '3-2', '1,,2', '1-a'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_numbers(text, 5)
        for radius in (-1., float('nan'), float('inf')):
            with self.subTest(radius=radius), self.assertRaises(ValueError):
                select_numbers(self.positions, (1,), radius)

    def test_set_operations_and_empty_result(self):
        current = (1, 2, 3)
        self.assertEqual(combine_numbers(current, (3, 4), 'REPLACE', 5), (3, 4))
        self.assertEqual(combine_numbers(current, (3, 4), 'UNION', 5), (1, 2, 3, 4))
        self.assertEqual(combine_numbers(current, (3, 4), 'INTERSECT', 5), (3,))
        self.assertEqual(combine_numbers(current, (3, 4), 'DIFFERENCE', 5), (1, 2))
        self.assertEqual(combine_numbers(current, (), 'INVERT', 5), (4, 5))
        with self.assertRaisesRegex(ValueError, 'empty'):
            combine_numbers(current, (1, 2, 3), 'DIFFERENCE', 5)

    def test_recompute_uses_current_scientific_geometry_only_on_request(self):
        steps = [{'mode': 'REPLACE', 'seeds': [1], 'radius': 1., 'include_seeds': True},
                 {'mode': 'UNION', 'seeds': [4], 'radius': None, 'include_seeds': True},
                 {'mode': 'DIFFERENCE', 'seeds': [2], 'radius': None, 'include_seeds': True}]
        fixed = evaluate_steps(self.positions, steps)
        moved = self.positions.copy()
        moved[2] = (.5, 0., 0.)
        self.assertEqual(fixed, (1, 4))
        self.assertEqual(evaluate_steps(moved, steps), (1, 3, 4))
        self.assertEqual(fixed, (1, 4))


class CopySelectionTests(unittest.TestCase):
    def test_custom_source_graph_can_transfer_verified_mask(self):
        bpy = types.ModuleType('bpy')
        bpy.types = types.SimpleNamespace(Operator=type('Operator', (), {}))
        props = types.ModuleType('bpy.props')
        for name in ('BoolProperty', 'EnumProperty', 'FloatProperty', 'StringProperty'):
            setattr(props, name, lambda **kwargs: None)
        geometry = types.ModuleType('qcblender.blender.geometry')
        geometry.current_geometry = lambda obj: None
        graph = types.ModuleType('qcblender.blender.graph')
        graph.view_modifier = lambda obj: None
        spec = importlib.util.spec_from_file_location(
            'qcblender.blender._atom_selection_test',
            Path(__file__).resolve().parents[1] / 'qcblender/blender/atom_selection.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': props,
                                      'qcblender.blender.geometry': geometry,
                                      'qcblender.blender.graph': graph}):
            spec.loader.exec_module(module)

        class View(dict):
            def __init__(self, attr=None, **values):
                super().__init__(values)
                self.data = types.SimpleNamespace(attributes={module.ATTRIBUTE: attr} if attr else {})

        record = {'dataset_sha256': 'dataset', 'source_sha256': 'source', 'selected_job': 1}
        positions = np.zeros((3, 3))
        target = View()
        source = View()
        with (patch.object(module, 'current_geometry', side_effect=[(positions, record)] * 2),
              patch.object(module, '_preflight', return_value='target state') as preflight,
              patch.object(module, '_write') as write):
            module.copy_selection(source, target)
            preflight.assert_called_once_with(target)
            write.assert_not_called()

        attr = types.SimpleNamespace(domain='POINT', data_type='BOOLEAN',
                                     data=[types.SimpleNamespace(value=value) for value in (True, False, True)])
        saved = {'steps': [{'mode': 'REPLACE', 'seeds': [1, 3], 'radius': None}],
                 'fixed_numbers': [1, 3], 'source': record}
        source = View(attr, **{module.RECORD: json.dumps(saved)})
        with (patch.object(module, 'current_geometry', side_effect=[(positions, record)] * 2),
              patch.object(module, '_preflight', return_value='target state') as preflight,
              patch.object(module, '_write') as write):
            module.copy_selection(source, target)
            preflight.assert_called_once_with(target)
            write.assert_called_once_with(target, (1, 3), saved, 'target state')
        attr.data[1].value = True
        with (patch.object(module, 'current_geometry', side_effect=[(positions, record)] * 2),
              patch.object(module, '_preflight', return_value='target state'),
              patch.object(module, '_write') as write):
            with self.assertRaisesRegex(ValueError, 'differs'):
                module.copy_selection(source, target)
            write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
