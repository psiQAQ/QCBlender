"""Localization contracts without loading Blender or modifying scientific data."""
import ast
import importlib.util
from pathlib import Path
import string
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
BLENDER = ROOT / 'qcblender' / 'blender'
OWNED = (
    'annotations', 'association', 'atom_selection', 'camera', 'capabilities', 'charts',
    'color_presets', 'color_ranges', 'data_export', 'editor_ui', 'external_fields',
    'external_results', 'interaction', 'irc', 'layers', 'nbo', 'nocv', 'optimization',
    'profile', 'project', 'result_browser', 'scalars', 'source_browser', 'trajectory', 'ui',
)


def source(name):
    return ast.parse((BLENDER / (name + '.py')).read_text(encoding='utf-8'))


def messages():
    spec = importlib.util.spec_from_file_location('ui_messages', ROOT / 'qcblender/translations_ui.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.MESSAGES


class UILocalization(unittest.TestCase):
    def test_translated_templates_preserve_fields_conversions_and_format_specs(self):
        def fields(text):
            return sorted((field, spec, conversion) for _, field, spec, conversion
                          in string.Formatter().parse(text) if field is not None)
        for english, chinese in messages().items():
            with self.subTest(english=english):
                self.assertEqual(fields(english), fields(chinese))
                self.assertFalse(any('\u4e00' <= char <= '\u9fff' for char in english))

    def test_static_ui_and_dynamic_templates_have_registered_translations(self):
        available = messages()
        branded = {'QCBlender', 'QC Slice Gizmo'}
        for name in OWNED:
            for node in ast.walk(source(name)):
                values = []
                if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                        and target.id in ('bl_label', 'bl_description') for target in node.targets):
                    values.append(node.value)
                if isinstance(node, ast.Call):
                    values.extend(keyword.value for keyword in node.keywords
                                  if keyword.arg in ('text', 'name', 'description', 'title'))
                    if isinstance(node.func, ast.Name) and node.func.id == 'iface' and node.args:
                        values.append(node.args[0])
                for value in values:
                    if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value:
                        with self.subTest(file=name, line=node.lineno, text=value.value):
                            self.assertIn(value.value, available.keys() | branded)

    def test_local_selection_identifiers_and_approved_labels(self):
        operator = next(node for node in source('atom_selection').body
                        if isinstance(node, ast.ClassDef) and node.name == 'QCBLENDER_OT_local_selection')
        mode = next(node for node in operator.body if isinstance(node, ast.AnnAssign)
                    and node.target.id == 'mode')
        items = ast.literal_eval(next(keyword.value for keyword in mode.annotation.keywords
                                      if keyword.arg == 'items'))
        self.assertEqual([row[0] for row in items],
                         ['REPLACE', 'UNION', 'INTERSECT', 'DIFFERENCE', 'INVERT', 'CLEAR', 'RECOMPUTE'])
        self.assertEqual([messages()[row[1]] for row in items],
                         ['替换', '并集', '交集', '差集', '反选', '清除限制', '重新计算'])
        self.assertTrue(all(row[2] for row in items))

    def test_section_visibility_uses_stable_key_when_panel_label_changes(self):
        tree = source('editor_ui')
        section = next(node for node in tree.body
                       if isinstance(node, ast.ClassDef) and node.name == '_ObjectSection')
        calls = []
        ui = types.ModuleType('qcblender.blender.ui')
        ui.parameter_section_available = lambda obj, key: calls.append(key) or True
        namespace = {'__package__': 'qcblender.blender', 'is_qc': lambda context: True}
        exec(compile(ast.Module(body=[section], type_ignores=[]), str(BLENDER / 'editor_ui.py'), 'exec'), namespace)
        panel = type('Panel', (namespace['_ObjectSection'],), {'section_key': 'geometry'})
        context = types.SimpleNamespace(object=object())
        with patch.dict(sys.modules, {'qcblender.blender.ui': ui}):
            for label in ('Geometry Representation', '几何表示'):
                panel.bl_label = label
                self.assertTrue(panel.poll(context))
        self.assertEqual(calls, ['geometry', 'geometry'])


if __name__ == '__main__':
    unittest.main()
