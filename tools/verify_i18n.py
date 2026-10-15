"""Real installed Blender checks for bilingual RNA, data identity and lifecycle."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
PACKAGE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=PACKAGE)
i18n = importlib.import_module(PACKAGE + '.i18n')
identity = importlib.import_module(PACKAGE + '.blender.node_identity')
localization = importlib.import_module(PACKAGE + '.blender.localization')
custom = importlib.import_module(PACKAGE + '.blender.custom_properties')
selection = importlib.import_module(PACKAGE + '.blender.atom_selection')
views = importlib.import_module(PACKAGE + '.blender.views')
data_api = importlib.import_module(PACKAGE + '.data')
from bl_ui.properties_object import OBJECT_PT_custom_props

view = bpy.context.preferences.view
original_preferences = (view.language, view.use_translate_interface, view.use_translate_tooltips)
report = {'status': 'Failed', 'blender': bpy.app.version_string,
          'module_path': i18n.__file__, 'checks': {}, 'independent_human_review': 'Not Run'}


def record(name):
    report['checks'][name] = 'Passed'


def geometry(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        coordinates = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', coordinates)
        return hashlib.sha256(coordinates.tobytes()).hexdigest()
    finally:
        evaluated.to_mesh_clear()


try:
    catalog = i18n.messages()
    view.language = 'en_US'
    view.use_translate_interface = view.use_translate_tooltips = True
    assert i18n.iface('Local Atom Selection') == 'Local Atom Selection'
    assert bpy.app.translations.pgettext_iface('Workflow', i18n.CONTEXT) == 'Workflow'
    original = next(obj for obj in bpy.data.objects if obj.get('qc_view_kind') == 'atoms')
    before_data = data_api.load_dataset(bpy.path.abspath(original['qc_dataset']))
    arrays = {name: hashlib.sha256(value.tobytes()).hexdigest() for name, value in before_data.arrays.items()}
    initial_geometry = geometry(original)
    view.language = 'zh_HANS'
    localization._refresh()
    assert i18n.iface('Local Atom Selection') == catalog['Local Atom Selection']
    assert bpy.app.translations.pgettext_iface('Workflow', i18n.CONTEXT) == catalog['Workflow']
    assert initial_geometry == geometry(original)
    record('native_translation_context_and_geometry')

    prop = bpy.ops.qcblender.local_selection.get_rna_type().properties['mode']
    assert prop.translation_context == i18n.CONTEXT
    expected = {'REPLACE': '替换', 'UNION': '并集', 'INTERSECT': '交集', 'DIFFERENCE': '差集',
                'INVERT': '反选', 'CLEAR': '清除限制', 'RECOMPUTE': '重新计算'}
    for item in prop.enum_items:
        assert bpy.app.translations.pgettext_iface(item.name, prop.translation_context) == expected[item.identifier]
    record('seven_native_mode_enum_names')

    view.use_translate_interface = False
    localization._refresh()
    assert i18n.iface('Replace') == 'Replace'
    assert i18n.tip('Replace') == '替换'
    view.use_translate_tooltips = False
    assert i18n.tip('Replace') == 'Replace'
    view.use_translate_interface = True
    assert i18n.iface('Replace') == '替换'
    assert i18n.tip('Replace') == 'Replace'
    record('independent_interface_and_tooltip_switches')

    view.language = 'de_DE'
    assert i18n.iface('Replace') == 'Replace'
    assert bpy.app.translations.pgettext_iface('Workflow', i18n.CONTEXT) == 'Workflow'
    record('other_locale_english_fallback')

    view.language = 'zh_HANS'
    view.use_translate_tooltips = True
    from types import SimpleNamespace
    description = custom.QCBLENDER_OT_property_help.description(
        bpy.context, SimpleNamespace(property_key='qc_dataset'))
    assert 'qc_dataset' in description and '科学数据集' in description
    assert OBJECT_PT_custom_props.draw is custom._draw
    record('native_property_hook_and_key_tooltip')

    # Use a new view so the opened project is not altered by the selection checks.
    copied = views.atom_view(bpy.path.abspath(original['qc_dataset']))
    bpy.context.view_layer.objects.active = copied
    copied.select_set(True)
    identity.refresh_localization()
    cases = [('REPLACE', '1,2', [1, 2]), ('UNION', '3', [1, 2, 3]),
             ('INTERSECT', '2,3', [2, 3]), ('DIFFERENCE', '3', [2]),
             ('INVERT', '', [i for i in range(1, len(copied.data.vertices) + 1) if i != 2]),
             ('RECOMPUTE', '', [i for i in range(1, len(copied.data.vertices) + 1) if i != 2]),
             ('CLEAR', '', list(range(1, len(copied.data.vertices) + 1)))]
    for mode, numbers, expected_ids in cases:
        assert bpy.ops.qcblender.local_selection(mode=mode, numbers=numbers) == {'FINISHED'}
        attr = copied.data.attributes[selection.ATTRIBUTE]
        assert [i for i, value in enumerate(attr.data, 1) if value.value] == expected_ids, mode
    record('seven_selection_modes_after_chinese_node_localization')
    assert arrays == {name: hashlib.sha256(value.tobytes()).hexdigest() for name, value in
                     data_api.load_dataset(bpy.path.abspath(original['qc_dataset'])).arrays.items()}
    record('source_arrays_unchanged')

    # Link a real QC object from the current file, then refresh without writes.
    linked_fixture = args.report.with_suffix('.linked.blend')
    bpy.data.libraries.write(str(linked_fixture), {original})
    with bpy.data.libraries.load(str(linked_fixture), link=True) as (source, target):
        target.objects = [original.name]
    linked = target.objects[0]
    assert linked.library is not None and not linked.is_editable
    names = [(mod.name, getattr(mod, 'node_group', None).name) for mod in linked.modifiers if mod.type == 'NODES']
    identity.refresh_localization()
    assert names == [(mod.name, mod.node_group.name) for mod in linked.modifiers if mod.type == 'NODES']
    record('linked_object_refresh_preserves_readonly_data')

    original_draw = custom._original_draw
    bpy.ops.preferences.addon_disable(module=PACKAGE)
    assert OBJECT_PT_custom_props.draw is original_draw
    assert not bpy.app.timers.is_registered(localization._refresh)
    assert localization._loaded not in bpy.app.handlers.load_post
    assert localization._changed not in bpy.app.handlers.depsgraph_update_post
    bpy.ops.preferences.addon_enable(module=PACKAGE)
    assert OBJECT_PT_custom_props.draw is custom._draw
    assert bpy.app.handlers.load_post.count(localization._loaded) == 1
    assert bpy.app.handlers.depsgraph_update_post.count(localization._changed) == 1
    record('hook_handler_timer_unregister_and_reregister')
    view.language = 'en_US'
    localization._refresh()
    assert initial_geometry == geometry(original)
    report['status'] = 'Passed'
finally:
    view.language, view.use_translate_interface, view.use_translate_tooltips = original_preferences
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
