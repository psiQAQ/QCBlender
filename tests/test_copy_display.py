"""Pure Python checks for copy policy and all-target preflight."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def load_module():
    bpy = types.ModuleType('bpy')
    bpy.types = types.SimpleNamespace(Operator=type('Operator', (), {}))
    bpy.data = types.SimpleNamespace(materials=types.SimpleNamespace(remove=lambda *args, **kwargs: None))
    props = types.ModuleType('bpy.props')
    props.BoolProperty = lambda **kwargs: None
    graph = types.ModuleType('qcblender.blender.graph')
    graph.view_modifier = lambda obj: None
    browser = types.ModuleType('qcblender.blender.source_browser')
    browser.color_volume = lambda obj: None
    spec = importlib.util.spec_from_file_location(
        'qcblender.blender._copy_display_test',
        Path(__file__).resolve().parents[1] / 'qcblender/blender/copy_display.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'bpy': bpy, 'bpy.props': props,
                                  'qcblender.blender.graph': graph,
                                  'qcblender.blender.source_browser': browser}):
        spec.loader.exec_module(module)
    return module


copy = load_module()


class View(dict):
    def __init__(self, name, quantity='orbital_amplitude', unit='bohr^-3/2'):
        super().__init__(qc_field='{"quantity": "' + quantity + '", "unit": "' + unit + '"}')
        self.name = name

    def update_tag(self):
        pass


def state(view, kind='slice', mapping=(False, False), modifier=None):
    sockets = {'Width': types.SimpleNamespace(identifier='width', socket_type='NodeSocketFloat'),
               'Height': types.SimpleNamespace(identifier='height', socket_type='NodeSocketFloat'),
               'Resolution': types.SimpleNamespace(identifier='resolution', socket_type='NodeSocketInt')}
    values = {'Width': 6., 'Height': 6., 'Resolution': 25}
    return {'obj': view, 'kind': kind, 'mapping': mapping,
            'modifier': modifier or {'width': 6., 'height': 6., 'resolution': 25},
            'sockets': sockets, 'values': values, 'materials': {}}


class CopyPolicy(unittest.TestCase):
    def test_shared_target_material_gets_independent_copies(self):
        class Material:
            use_nodes = True

            def __init__(self):
                self.node_tree = types.SimpleNamespace(nodes=[])

            def get(self, key):
                return None

            def copy(self):
                return Material()

        original, source_material = Material(), Material()
        source, first, second = View('source'), View('first'), View('second')
        states = {}
        for obj, mat in ((source, source_material), (first, original), (second, original)):
            modifier = {'material': mat}
            item = types.SimpleNamespace(identifier='material', socket_type='NodeSocketMaterial')
            states[id(obj)] = {'obj': obj, 'kind': 'field', 'mapping': (False, False),
                               'modifier': modifier, 'sockets': {'Positive Material': item},
                               'values': {'Positive Material': mat},
                               'materials': {'Positive Material': (mat, [('socket', modifier, 'material')])}}
        views = types.ModuleType('qcblender.blender.views')
        views.node_by_type = lambda nodes, kind: None
        with (patch.object(copy, '_state', side_effect=lambda obj: states[id(obj)]),
              patch.dict(sys.modules, {'qcblender.blender.views': views})):
            copy.copy_parameters(source, [first, second], False, True, False)
        first_material = states[id(first)]['modifier']['material']
        second_material = states[id(second)]['modifier']['material']
        self.assertIsNot(first_material, second_material)
        self.assertIsNot(first_material, original)
        self.assertIs(states[id(source)]['modifier']['material'], source_material)

    def test_standard_socket_default_need_not_be_explicit_modifier_property(self):
        items = [types.SimpleNamespace(name=name, identifier='input_' + str(i),
                                       socket_type=kind, item_type='SOCKET', in_out='INPUT', default_value=value)
                 for i, (name, kind, value) in enumerate((('Width', 'NodeSocketFloat', 6.),
                                                           ('Height', 'NodeSocketFloat', 6.),
                                                           ('Resolution', 'NodeSocketInt', 101)), 1)]
        tree = {'qc_view_graph': 2,
                'qc_sockets': '{"Width": "input_1", "Height": "input_2", "Resolution": "input_3"}'}
        asset = types.SimpleNamespace(get=lambda key: 'qc.slice.v1')
        node = types.SimpleNamespace(bl_idname='GeometryNodeGroup', node_tree=asset)
        tree = types.SimpleNamespace(name='User Renamed Slice', get=tree.get,
                                     interface=types.SimpleNamespace(items_tree=items), nodes=[node])

        class Modifier(dict):
            node_group = tree

        self.assertIn('Resolution', copy._inputs(Modifier(), 'slice'))

    def test_unknown_quantity_and_color_unit_are_not_numeric_compatibility(self):
        self.assertRaises(ValueError, copy._known_signature, {'quantity': 'unknown_scalar', 'unit': 'hartree'})
        self.assertRaises(ValueError, copy._known_signature, {'quantity': 'spin_density', 'unit': 'unknown'})
        source = state(View('source', 'unknown_scalar', 'unknown'))
        target = state(View('target', 'spin_density', 'electron/bohr^3'))
        self.assertIn('Width', copy.GEOMETRY['slice'])
        self.assertIn('Height', copy.GEOMETRY['slice'])
        self.assertEqual(copy._plan(source, target, True, False, False)['names'], list(copy.GEOMETRY['slice']))

    def test_appearance_can_cross_quantity_without_copying_numbers(self):
        source = state(View('source'), kind='field')
        target = state(View('target', 'spin_density', 'electron/bohr^3'), kind='field')
        socket = types.SimpleNamespace(identifier='opacity', socket_type='NodeSocketFloat')
        source['sockets'] = target['sockets'] = {'Positive Opacity': socket}
        source['values'] = {'Positive Opacity': .4}
        target['values'] = {'Positive Opacity': 1.}
        plan = copy._plan(source, target, False, True, False)
        self.assertEqual(plan['names'], ['Positive Opacity'])
        with patch.object(copy, '_science_field', side_effect=lambda obj, kind: __import__('json').loads(obj['qc_field'])):
            self.assertRaises(ValueError, copy._plan, source, target, False, True, True)

    def test_atoms_numeric_color_range_uses_color_quantity(self):
        source, target = state(View('source'), kind='atoms', mapping=(True, False)), state(View('target'), kind='atoms', mapping=(True, False))
        source['sockets'] = target['sockets'] = {
            name: types.SimpleNamespace(identifier=name, socket_type='NodeSocketFloat') for name in copy.COLOR_RANGE}
        source['values'] = {'Color Minimum': -1., 'Color Center': 0., 'Color Maximum': 1.}
        target['values'] = {'Color Minimum': -2., 'Color Center': 0., 'Color Maximum': 2.}
        with patch.object(copy, '_color_signature', side_effect=[('electrostatic_potential', 'hartree/e')] * 2):
            self.assertEqual(copy._plan(source, target, False, False, True)['names'], list(copy.COLOR_RANGE))

    def test_one_incompatible_target_prevents_all_writes(self):
        source, good, bad = View('source'), View('good'), View('bad', 'spin_density')
        states = {id(obj): state(obj, kind='field') for obj in (source, good, bad)}
        for view in states.values():
            view['sockets'] = {name: types.SimpleNamespace(identifier=name, socket_type='NodeSocketFloat')
                               for name in ('Isovalue', 'Negative Isovalue')}
            view['modifier'] = {'Isovalue': .02, 'Negative Isovalue': .02}
            view['values'] = {'Isovalue': .02, 'Negative Isovalue': .02}
        states[id(source)]['values'] = {'Isovalue': .05, 'Negative Isovalue': .05}
        with (patch.object(copy, '_state', side_effect=lambda obj: states[id(obj)]),
              patch.object(copy, '_science_field', side_effect=lambda obj, kind: __import__('json').loads(obj['qc_field']))):
            self.assertRaises(ValueError, copy.copy_parameters, source, [good, bad], False, False, True)
        self.assertEqual(states[id(good)]['modifier']['Isovalue'], .02)

    def test_runtime_write_failure_rolls_back_previous_target(self):
        class RejectingModifier(dict):
            def __setitem__(self, key, value):
                if value == 101:
                    raise RuntimeError('write failed')
                super().__setitem__(key, value)

        source, first, second = View('source'), View('first'), View('second')
        states = {id(obj): state(obj) for obj in (source, first, second)}
        states[id(source)]['values']['Resolution'] = 101
        states[id(second)]['modifier'] = RejectingModifier(resolution=25)
        with patch.object(copy, '_state', side_effect=lambda obj: states[id(obj)]):
            self.assertRaises(RuntimeError, copy.copy_parameters, source, [first, second], True, False, False)
        self.assertEqual(states[id(first)]['modifier']['resolution'], 25)
        self.assertEqual(states[id(second)]['modifier']['resolution'], 25)


if __name__ == '__main__':
    unittest.main()
