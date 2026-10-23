"""Operator description coverage and preference-aware callbacks without Blender."""
import ast
import copy
from pathlib import Path
import sys
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest.mock import patch

from qcblender import i18n


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'annotations.py', 'editor_ui.py', 'project.py', 'localization.py',
            'custom_properties.py', 'node_identity.py', '__init__.py'}


def operator_sources():
    operators = {}
    for path in (ROOT / 'qcblender/blender').glob('*.py'):
        if path.name in EXCLUDED:
            continue
        for cls in ast.parse(path.read_text(encoding='utf-8')).body:
            if not isinstance(cls, ast.ClassDef):
                continue
            attrs = {target.id: node.value for node in cls.body if isinstance(node, ast.Assign)
                     for target in node.targets if isinstance(target, ast.Name)}
            identifier = attrs.get('bl_idname')
            if isinstance(identifier, ast.Constant) and identifier.value.startswith('qcblender.'):
                operators[identifier.value] = (path, cls, attrs)
    return operators


def description_class(identifier):
    """Compile the actual callback only; scientific methods and RNA are not stubbed."""
    path, source, attrs = operator_sources()[identifier]
    body = [node for node in source.body
            if isinstance(node, ast.FunctionDef) and node.name == 'description']
    body.insert(0, ast.Assign(targets=[ast.Name(id='bl_description', ctx=ast.Store())],
                              value=copy.deepcopy(attrs['bl_description'])))
    cls = ast.ClassDef(name='Description', bases=[], keywords=[], body=body, decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[]))
    namespace = {'__package__': 'qcblender.blender'}
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace['Description']


PROPERTY_VARIANTS = {
    'local_selection': ('mode', ('REPLACE', 'UNION', 'INTERSECT', 'DIFFERENCE', 'INVERT', 'CLEAR', 'RECOMPUTE')),
    'hydrogen_visibility': ('mode', ('HIDE', 'KEEP', 'RESTORE')),
    'layer_action': ('action', ('SELECT', 'DUPLICATE', 'REMOVE', 'UP', 'DOWN', 'VISIBILITY', 'RENDER')),
    'trajectory_frame': ('direction', ('GOTO', 'PREV', 'NEXT')),
    'optimization_step': ('direction', ('GOTO', 'PREV', 'NEXT')),
    'irc_step': ('direction', ('PREV', 'NEXT')),
    'click_probe': ('role', ('GEOMETRY', 'COLOR')),
    'contour_source': ('role', ('GEOMETRY', 'COLOR')),
    'apply_color_preset': ('material_role', ('scalar_map', 'charge_map')),
}


class OperatorTooltips(unittest.TestCase):
    def setUp(self):
        self.view = SimpleNamespace(language='zh_HANS', use_translate_interface=False,
                                    use_translate_tooltips=True)
        self.bpy = SimpleNamespace(context=SimpleNamespace(preferences=SimpleNamespace(view=self.view)))
        self.prefs_patch = patch.dict(sys.modules, {'bpy': self.bpy})
        self.prefs_patch.start()
        self.addCleanup(self.prefs_patch.stop)
        self.messages = i18n.messages()

    def test_every_owned_operator_and_workspace_tool_has_meaningful_bilingual_description(self):
        for identifier, (path, cls, attrs) in operator_sources().items():
            with self.subTest(operator=identifier):
                description = ast.literal_eval(attrs['bl_description'])
                self.assertGreater(len(description), 50)
                self.assertNotEqual(description, ast.literal_eval(attrs['bl_label']))
                self.assertIn(description, self.messages)
                self.assertTrue(any('\u4e00' <= char <= '\u9fff' for char in self.messages[description]))

    def test_all_action_variants_have_distinct_tooltips_and_obey_tooltip_switch(self):
        context = SimpleNamespace(object=MappingProxyType({}))
        for operator, (property_name, variants) in PROPERTY_VARIANTS.items():
            cls = description_class('qcblender.' + operator)
            english_descriptions = []
            for variant in variants:
                properties = SimpleNamespace(**{property_name: variant})
                for interface in (False, True):
                    self.view.use_translate_interface = interface
                    self.view.use_translate_tooltips = False
                    english = cls.description(context, properties)
                    self.assertIn(english, self.messages)
                    self.assertNotEqual(english, cls.bl_description)
                    self.view.use_translate_tooltips = True
                    chinese = cls.description(context, properties)
                    self.assertEqual(chinese, self.messages[english])
                english_descriptions.append(english)
            with self.subTest(operator=operator):
                self.assertEqual(len(set(english_descriptions)), len(variants))

    def test_context_variants_distinguish_results_styles_and_contour_state(self):
        cases = {
            'apply_result_filter': [(dict(qc_analysis_role=role), {})
                                    for role in ('esp_area', 'nbo', 'ets_nocv', 'esp_maximum')],
            'toggle_contours': [(dict(qc_contour_enabled=enabled), {}) for enabled in (False, True)],
            'set_view_style': [(dict(qc_view_kind=kind), dict(style=style))
                               for kind in ('atoms', 'field') for style in range(3)],
        }
        for operator, variants in cases.items():
            cls = description_class('qcblender.' + operator)
            shown = []
            for values, props in variants:
                context = SimpleNamespace(object=MappingProxyType(values))
                self.view.use_translate_tooltips = False
                english = cls.description(context, SimpleNamespace(**props))
                self.assertIn(english, self.messages)
                self.assertNotEqual(english, cls.bl_description)
                self.view.use_translate_tooltips = True
                self.assertEqual(cls.description(context, SimpleNamespace(**props)), self.messages[english])
                shown.append(english)
            with self.subTest(operator=operator):
                self.assertEqual(len(shown), len(set(shown)))

    def test_callbacks_accept_unset_properties_and_missing_object_without_source_access(self):
        for identifier, (_, source, _) in operator_sources().items():
            if any(isinstance(node, ast.FunctionDef) and node.name == 'description' for node in source.body):
                cls = description_class(identifier)
                with self.subTest(operator=identifier):
                    result = cls.description(None, SimpleNamespace())
                    self.assertIn(result, self.messages.values())

    def test_charge_method_cache_keeps_identifiers_and_source_labels_when_tooltip_language_changes(self):
        path = ROOT / 'qcblender/blender/atomic_properties.py'
        function = next(node for node in ast.parse(path.read_text(encoding='utf-8')).body
                        if isinstance(node, ast.FunctionDef) and node.name == 'charge_items')
        cached = [('Mulliken', 'Mulliken', 'Atomic partial charge in e'),
                  ('Workflow', 'Workflow', 'Atomic partial charge in e')]
        namespace = {'__package__': 'qcblender.blender', '_charge_items': {'dataset': cached},
                     'bpy': SimpleNamespace(path=SimpleNamespace(abspath=lambda value: value))}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
        context = SimpleNamespace(object={'qc_dataset': 'dataset'})
        for translate in (True, False, True):
            self.view.use_translate_tooltips = translate
            actual = namespace['charge_items'](None, context)
            self.assertEqual([row[:2] for row in actual], [row[:2] for row in cached])
            self.assertEqual([row[2] for row in actual],
                             [self.messages[row[2]] if translate else row[2] for row in cached])
        self.assertEqual(namespace['_charge_items']['dataset'], cached)


if __name__ == '__main__':
    unittest.main()
