"""Preference and data-preservation behavior at the Blender UI boundary."""
import gc
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from qcblender import i18n


class DeferredProperty:
    def __init__(self, **keywords):
        self.keywords = keywords


class RecordingLayout:
    """Record native layout calls without starting Blender."""

    def __init__(self):
        self.calls = []
        self.enabled = True

    def label(self, **kwargs):
        self.calls.append(('label', (), kwargs))

    def prop(self, *args, **kwargs):
        self.calls.append(('prop', args, kwargs))

    def operator(self, *args, **kwargs):
        self.calls.append(('operator', args, kwargs))
        return SimpleNamespace()

    def row(self, **kwargs):
        child = RecordingLayout()
        self.calls.append(('row', (), kwargs, child))
        return child

    def box(self):
        child = RecordingLayout()
        self.calls.append(('box', (), {}, child))
        return child

    def panel(self, *args, **kwargs):
        header = RecordingLayout()
        body = None if kwargs.get('default_closed') else RecordingLayout()
        self.calls.append(('panel', args, kwargs, header, body))
        return header, body


class I18nCoreTests(unittest.TestCase):
    def setUp(self):
        self.view = SimpleNamespace(language='zh_HANS', use_translate_interface=True,
                                    use_translate_tooltips=True)
        self.bpy = SimpleNamespace(
            context=SimpleNamespace(preferences=SimpleNamespace(view=self.view)),
            app=SimpleNamespace(translations=SimpleNamespace(locale='zh_HANS')),
            props=SimpleNamespace(_PropertyDeferred=DeferredProperty),
        )
        self.catalog = {
            'Source': '来源', 'Source help': '来源用途',
            'Read field {name} at {value:.3f}': '在 {value:.3f} 读取场 {name}',
            'Missing scientific field: {name}': '缺少科学场：{name}',
            'Cannot read source {path}: {detail}': '无法读取来源 {path}：{detail}',
            '{name}': '通用的 {name}',
        }
        for patcher in (patch.dict('sys.modules', {'bpy': self.bpy}),
                        patch.object(i18n, '_messages', self.catalog),
                        patch.object(i18n, '_enum_cache', {})):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_interface_and_tooltips_have_independent_switches(self):
        for interface, tooltips in ((True, False), (False, True), (True, True), (False, False)):
            with self.subTest(interface=interface, tooltips=tooltips):
                self.view.use_translate_interface = interface
                self.view.use_translate_tooltips = tooltips
                self.assertEqual(i18n.iface('Source'), '来源' if interface else 'Source')
                self.assertEqual(i18n.tip('Source help'), '来源用途' if tooltips else 'Source help')

    def test_default_language_uses_resolved_blender_locale(self):
        self.view.language = 'DEFAULT'
        for locale, expected in (('zh_HANS', '来源'), ('zh_CN', '来源'),
                                 ('en_US', 'Source'), ('ja_JP', 'Source')):
            with self.subTest(locale=locale):
                self.bpy.app.translations.locale = locale
                self.assertEqual(i18n.iface('Source'), expected)
                self.assertEqual(i18n.interface_language(), 'zh_HANS' if expected == '来源' else 'en_US')

    def test_explicit_language_ignores_system_locale(self):
        self.bpy.app.translations.locale = 'ja_JP'
        for language, expected in (('zh_HANS', '来源'), ('zh_CN', '来源'),
                                   ('en_US', 'Source'), ('fr_FR', 'Source')):
            with self.subTest(language=language):
                self.view.language = language
                self.assertEqual(i18n.iface('Source'), expected)

    def test_missing_blender_or_preferences_keeps_canonical_messages(self):
        with patch.dict('sys.modules', {'bpy': None}):
            self.assertEqual(i18n.iface('Source'), 'Source')
            self.assertEqual(i18n.tip('Source help'), 'Source help')
        self.bpy.context = SimpleNamespace()
        self.assertEqual(i18n.iface('Source'), 'Source')
        self.assertEqual(i18n.tip('Source help'), 'Source help')

    def test_known_message_formats_values_after_translation(self):
        values = {'name': 'qc_scalar_value [electron/bohr^3]', 'value': 1.125}
        self.assertEqual(i18n.iface('Read field {name} at {value:.3f}', **values),
                         '在 1.125 读取场 qc_scalar_value [electron/bohr^3]')
        self.view.use_translate_interface = False
        self.assertEqual(i18n.iface('Read field {name} at {value:.3f}', **values),
                         'Read field qc_scalar_value [electron/bohr^3] at 1.125')

    def test_unknown_messages_and_values_remain_verbatim(self):
        data = 'qc_atom_id [angstrom] user/Source {unknown} -0.004'
        self.assertEqual(i18n.iface(data), data)
        self.assertEqual(i18n.tip(data), data)
        self.assertEqual(i18n.iface('User object: {name}', name='Source'), 'User object: Source')

    def test_error_translation_preserves_scientific_and_user_data(self):
        detail = 'qc_scalar_value [electron/bohr^3] = -0.004; Source {literal}'
        path = '用户数据/Source/水分子.fchk'
        error = ValueError(f'Cannot read source {path}: {detail}')
        self.assertEqual(i18n.error_text(error), f'无法读取来源 {path}：{detail}')
        self.assertEqual(i18n.error_text('Missing scientific field: qc_atom_id'),
                         '缺少科学场：qc_atom_id')

    def test_unknown_errors_are_not_translated_by_a_broad_placeholder(self):
        unknown = 'Source qc_atom_id [angstrom] -0.004 {literal}'
        self.assertEqual(i18n.error_text(RuntimeError(unknown)), unknown)
        self.view.use_translate_interface = False
        self.assertEqual(i18n.error_text('Missing scientific field: qc_atom_id'),
                         'Missing scientific field: qc_atom_id')

    def test_exact_error_uses_catalog_and_interface_switch(self):
        self.assertEqual(i18n.error_text('Source'), '来源')
        self.view.use_translate_tooltips = False
        self.assertEqual(i18n.error_text('Source'), '来源')
        self.view.use_translate_interface = False
        self.assertEqual(i18n.error_text('Source'), 'Source')

    def test_enum_items_preserve_ids_values_icons_separators_and_inputs(self):
        original = [('qc_atom_id', 'Source', 'Source help', 'ATOM', 23), None,
                    ('profile', 'User-defined label', 'User-defined tooltip', 7)]
        result = i18n.enum_items(original)
        self.assertEqual(result, [('qc_atom_id', '来源', '来源用途', 'ATOM', 23), None,
                                  ('profile', 'User-defined label', 'User-defined tooltip', 7)])
        self.assertEqual(original[0], ('qc_atom_id', 'Source', 'Source help', 'ATOM', 23))
        self.assertIsNot(result, original)

    def test_dynamic_enum_items_remain_reusable_after_callback_inputs_are_gone(self):
        def callback():
            return i18n.enum_items([(''.join(('source', '_id')), ''.join(('Sou', 'rce')),
                                     ''.join(('Source', ' help')))])

        first = callback()
        first_identity = id(first)
        del first
        gc.collect()
        second = callback()
        self.assertEqual(id(second), first_identity)
        self.assertEqual(second, [('source_id', '来源', '来源用途')])
        self.assertIs(callback(), second)

    def test_enum_cache_separates_tooltip_and_interface_preferences(self):
        items = [('id', 'Source', 'Source help')]
        both = i18n.enum_items(items)
        self.view.use_translate_tooltips = False
        only_interface = i18n.enum_items(items)
        self.assertEqual(only_interface, [('id', '来源', 'Source help')])
        self.assertIsNot(only_interface, both)
        self.view.use_translate_interface = False
        canonical = i18n.enum_items(items)
        self.assertEqual(canonical, [('id', 'Source', 'Source help')])
        self.view.use_translate_tooltips = True
        only_tooltip = i18n.enum_items(items)
        self.assertEqual(only_tooltip, [('id', 'Source', '来源用途')])

    def test_enum_language_switch_preserves_previous_callback_results(self):
        items = [('id', 'Source', 'Source help')]
        chinese = i18n.enum_items(items)
        self.view.language = 'en_US'
        english = i18n.enum_items(items)
        self.assertEqual(english, [('id', 'Source', 'Source help')])
        self.assertEqual(chinese, [('id', '来源', '来源用途')])
        self.assertIsNot(chinese, english)
        self.view.language = 'zh_HANS'
        self.assertIs(i18n.enum_items(items), chinese)

    def test_layout_translates_ui_text_once_and_retains_operator_identifier(self):
        raw = RecordingLayout()
        wrapped = i18n.ui_layout(raw)
        operator = wrapped.operator('qcblender.source_details', text='Source', icon='INFO')
        operator.field = 'qc_scalar_value'
        self.assertEqual(raw.calls, [('operator', ('qcblender.source_details',),
                                      {'text': '来源', 'icon': 'INFO', 'translate': False})])
        self.assertEqual(operator.field, 'qc_scalar_value')
        self.assertIs(i18n.ui_layout(wrapped), wrapped)

    def test_layout_translate_false_preserves_user_text_even_if_it_matches_catalog(self):
        raw = RecordingLayout()
        wrapped = i18n.ui_layout(raw)
        wrapped.label(text='Source', translate=False)
        wrapped.prop(SimpleNamespace(Source=1), 'Source', text='Source', translate=False)
        self.assertEqual(raw.calls[0][2], {'text': 'Source', 'translate': False})
        self.assertEqual(raw.calls[1][1][1], 'Source')
        self.assertEqual(raw.calls[1][2], {'text': 'Source', 'translate': False})

    def test_nested_layouts_keep_translation_and_forward_native_state(self):
        raw = RecordingLayout()
        row = i18n.ui_layout(raw).row(align=True)
        row.enabled = False
        box = row.box()
        box.label(text='Source')
        native_row = raw.calls[0][3]
        native_box = native_row.calls[0][3]
        self.assertEqual(raw.calls[0][2], {'align': True})
        self.assertFalse(native_row.enabled)
        self.assertFalse(row.enabled)
        self.assertEqual(native_box.calls[0][2], {'text': '来源', 'translate': False})

    def test_panel_layouts_wrap_header_and_body_and_preserve_closed_body(self):
        raw = RecordingLayout()
        wrapped = i18n.ui_layout(raw)
        header, body = wrapped.panel('qc_panel')
        header.label(text='Source')
        body.label(text='Source', translate=False)
        self.assertEqual(raw.calls[0][3].calls[0][2]['text'], '来源')
        self.assertEqual(raw.calls[0][4].calls[0][2]['text'], 'Source')
        closed_header, closed_body = wrapped.panel('closed', default_closed=True)
        self.assertIsNone(closed_body)
        closed_header.label(text='Source')
        self.assertEqual(raw.calls[1][3].calls[0][2]['text'], '来源')

    def test_prepare_class_adds_context_without_changing_identifiers_or_metadata(self):
        ordinary = DeferredProperty(name='Source', description='Source help', default='qc_atom_id')
        specialized = DeferredProperty(name='Source', translation_context='Specialized Context')

        class Operator:
            bl_idname = 'qcblender.source_details'
            bl_label = 'Source'
            bl_description = 'Source help'
            __annotations__ = {'source': ordinary, 'specialized': specialized, 'unrelated': str}

        i18n.prepare_class(Operator)
        self.assertEqual(Operator.bl_translation_context, i18n.CONTEXT)
        self.assertEqual(ordinary.keywords, {'name': 'Source', 'description': 'Source help',
                                            'default': 'qc_atom_id', 'translation_context': i18n.CONTEXT})
        self.assertEqual(specialized.keywords['translation_context'], 'Specialized Context')
        self.assertEqual(Operator.bl_idname, 'qcblender.source_details')
        self.assertEqual(Operator.bl_label, 'Source')
        self.assertEqual(Operator.bl_description, 'Source help')
        self.assertIs(Operator.__annotations__['unrelated'], str)


if __name__ == '__main__':
    unittest.main()
