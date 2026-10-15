"""Check installed operator tooltips in Blender without executing QC operations.

Run with Blender --background --python-exit-code 1 --python this_file.py --
--output report.json [--module bl_ext.user_default.qcblender]. Native keymap
items provide independent, real OperatorProperties with their RNA defaults.
This checks registered metadata, callbacks and native translation lookup;
visual hover and independent human review remain Not Run.
"""
import argparse
import ast
import hashlib
import importlib
import inspect
import itertools
import json
import os
from pathlib import Path
import sys
import textwrap
import traceback

import bpy


LANGUAGES = ('en_US', 'zh_HANS')
CONTEXT_VARIANTS = {
    'qcblender.apply_result_filter': (
        ('esp_area', {'qc_analysis_role': 'esp_area'}),
        ('nbo', {'qc_analysis_role': 'nbo'}),
        ('ets_nocv', {'qc_analysis_role': 'ets_nocv'}),
        ('esp_points', {'qc_analysis_role': 'esp_maximum'}),
        ('aim_points', {'qc_analysis_role': 'aim_N'}),
    ),
    'qcblender.toggle_contours': (
        ('disabled', {'qc_view_kind': 'slice', 'qc_contour_enabled': False}),
        ('enabled', {'qc_view_kind': 'slice', 'qc_contour_enabled': True}),
    ),
    'qcblender.set_view_style': (
        ('atoms', {'qc_view_kind': 'atoms'}),
        ('field', {'qc_view_kind': 'field'}),
    ),
}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def description_callback(cls, package):
    """Find inherited plugin callbacks, excluding the native Operator API stub."""
    for base in cls.__mro__:
        if 'description' in vars(base):
            if base.__module__.startswith(package + '.'):
                return getattr(cls, 'description')
            return None
    return None


def selector_names(callback):
    """Read callback parameter selectors without inventing default values."""
    if callback is None:
        return []
    tree = ast.parse(textwrap.dedent(inspect.getsource(callback)))
    names = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == 'properties'):
            names.add(node.attr)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == 'getattr' and len(node.args) >= 2
              and isinstance(node.args[0], ast.Name) and node.args[0].id == 'properties'
              and isinstance(node.args[1], ast.Constant)):
            names.add(node.args[1].value)
    return sorted(names)


def selector_variants(identifier, name, prop, property_labels):
    if identifier == 'qcblender.property_help' and name == 'property_key':
        return sorted(property_labels)
    if prop.type == 'ENUM':
        values = [item.identifier for item in prop.enum_items if item.identifier]
        check(values, f'{identifier}.{name}: no native enum items available')
        return values
    if prop.type == 'BOOLEAN':
        return [False, True]
    if prop.type == 'INT':
        check(prop.hard_max - prop.hard_min <= 16,
              f'{identifier}.{name}: selector range is too large; add explicit cases')
        return list(range(prop.hard_min, prop.hard_max + 1))
    if prop.type == 'STRING':
        # Nonempty IDs test the single-annotation branch; no annotation is edited.
        return ['', '__qc_tooltip_validation__']
    raise ValueError(f'{identifier}.{name}: unsupported selector type {prop.type}')


def scenarios(identifier, selectors, rna, property_labels):
    cases = [('defaults', {}, None)]
    values = [selector_variants(identifier, name, rna.properties[name], property_labels)
              for name in selectors]
    contexts = CONTEXT_VARIANTS.get(identifier, (('current', None),))
    combinations = list(itertools.product(*values)) if values else [()]
    for context_name, context_values in contexts:
        for combination in combinations:
            properties = dict(zip(selectors, combination))
            if not properties and context_values is None:
                continue
            name = context_name + ':' + ','.join(f'{key}={value!r}' for key, value in properties.items())
            cases.append((name, properties, context_values))
    return cases


def expected_chinese(identifier, english, properties, catalog, property_labels):
    if identifier == 'qcblender.property_help' and properties.property_key in property_labels:
        key = properties.property_key
        canonical = property_labels[key][1]
        check(english == key + '\n' + canonical,
              f'{identifier}: property key or canonical help changed')
        check(canonical in catalog, f'{identifier}: untranslated help for {key}')
        return key + '\n' + catalog[canonical]
    check(english in catalog, f'{identifier}: description has no Chinese catalog entry: {english!r}')
    return catalog[english]


def validate_text(identifier, text, labels):
    check(isinstance(text, str) and text.strip(), f'{identifier}: empty description')
    check(text.strip() not in labels, f'{identifier}: description only repeats its label')


def operator_inventory(package):
    auto_load = importlib.import_module(package + '.auto_load')
    classes = {cls.bl_idname: cls for cls in auto_load._registered
               if issubclass(cls, bpy.types.Operator) and cls.bl_idname.startswith('qcblender.')}
    native = {}
    for name in dir(bpy.ops.qcblender):
        if name.startswith('_'):
            continue
        operator = getattr(bpy.ops.qcblender, name)
        native['qcblender.' + name] = operator.get_rna_type()
    check(classes.keys() == native.keys(),
          f'Registered class/native operator mismatch: {sorted(classes.keys() ^ native.keys())}')
    check(classes, 'No installed QCBlender operators were discovered')
    required = {'qcblender.add_annotation', 'qcblender.edit_annotation',
                'qcblender.face_annotations', 'qcblender.remove_annotation',
                'qcblender.unify_annotation_materials', 'qcblender.open_properties',
                'qcblender.rebuild_cache', 'qcblender.relocate_dataset',
                'qcblender.save_project', 'qcblender.archive_project'}
    check(required <= classes.keys(), f'Required candidate operators are missing: {sorted(required - classes.keys())}')
    return classes, native


def workspace_tools(package):
    tools = {}
    for name, module in list(sys.modules.items()):
        if not name.startswith(package + '.blender.') or module is None:
            continue
        for cls in vars(module).values():
            if (inspect.isclass(cls) and cls.__module__ == name
                    and issubclass(cls, bpy.types.WorkSpaceTool)
                    and getattr(cls, 'bl_idname', '').startswith('qcblender.')):
                tools[cls.bl_idname] = cls
    return tools


def set_preferences(view, language, interface, tooltips):
    view.language = language
    view.use_translate_interface = interface
    view.use_translate_tooltips = tooltips


def verify_case(identifier, cls, rna, callback, properties, catalog, labels, view,
                property_labels, report_case):
    set_preferences(view, 'en_US', False, False)
    english = callback(bpy.context, properties) if callback else rna.description
    validate_text(identifier, english, labels)
    chinese = expected_chinese(identifier, english, properties, catalog, property_labels)
    validate_text(identifier, chinese, labels)
    check(chinese != english and any('\u4e00' <= char <= '\u9fff' for char in chinese),
          f'{identifier}: Chinese description has no translated explanatory text')
    context = getattr(cls, 'bl_translation_context', '*')
    report_case['english'] = english
    report_case['chinese'] = chinese
    report_case['language_checks'] = []
    for language, interface, tooltips in itertools.product(LANGUAGES, (False, True), (False, True)):
        set_preferences(view, language, interface, tooltips)
        expected = chinese if language == 'zh_HANS' and tooltips else english
        raw = callback(bpy.context, properties) if callback else rna.description
        shown = bpy.app.translations.pgettext_tip(raw, context)
        if callback:
            check(raw == expected,
                  f'{identifier}: callback ignores independent tooltip preferences: '
                  f'{language}/{interface}/{tooltips}: {raw!r}')
        check(shown == expected,
              f'{identifier}: native tooltip lookup mismatch: {language}/{interface}/{tooltips}: {shown!r}')
        report_case['language_checks'].append({
            'language': language, 'translate_interface': interface,
            'translate_tooltips': tooltips, 'text': shown, 'status': 'Passed',
        })
    report_case['status'] = 'Passed'


def run(args, report):
    if args.module not in bpy.context.preferences.addons:
        result = bpy.ops.preferences.addon_enable(module=args.module)
        check(result == {'FINISHED'}, f'Could not enable installed candidate: {args.module}')
    addon = importlib.import_module(args.module)
    i18n = importlib.import_module(args.module + '.i18n')
    property_labels = importlib.import_module(args.module + '.property_labels').LABELS
    catalog = i18n.messages()
    classes, native = operator_inventory(args.module)
    tools = workspace_tools(args.module)
    check({'qcblender.probe_tool', 'qcblender.slice_tool'} <= tools.keys(),
          'Installed probe/slice WorkSpaceTool declarations were not discovered')
    report.update(module_file=addon.__file__, operator_count=len(classes), tool_count=len(tools))
    paths = {Path(inspect.getfile(cls)).resolve() for cls in [*classes.values(), *tools.values()]}
    paths.add(Path(i18n.__file__).resolve())
    report['source_files_sha256'] = {str(path): sha256(path) for path in sorted(paths, key=str)}
    view = bpy.context.preferences.view
    saved_preferences = (view.language, view.use_translate_interface, view.use_translate_tooltips)
    keyconfig = None
    context_object = None
    keyconfig_name = None
    context_object_name = None
    try:
        keyconfig = bpy.context.window_manager.keyconfigs.new('__QC_tooltip_validation_' + str(os.getpid()))
        keyconfig_name = keyconfig.name
        keymap = keyconfig.keymaps.new('QC Tooltip Validation', space_type='EMPTY', region_type='WINDOW')
        context_object = bpy.data.objects.new('__QC_tooltip_context_' + str(os.getpid()), None)
        context_object_name = context_object.name
        for identifier, cls in sorted(classes.items()):
            record = {'operator': identifier, 'status': 'Failed', 'cases': []}
            report['operators'].append(record)
            item = None
            try:
                rna = native[identifier]
                callback = description_callback(cls, args.module)
                selectors = selector_names(callback)
                check(all(name in rna.properties for name in selectors),
                      f'{identifier}: callback selector missing from registered RNA')
                item = keymap.keymap_items.new(identifier, 'F3', 'PRESS')
                properties = item.properties
                check(isinstance(properties, bpy.types.OperatorProperties),
                      f'{identifier}: expected real native OperatorProperties')
                check(properties.bl_rna.identifier == rna.identifier,
                      f'{identifier}: keymap properties use a different RNA type')
                record.update(rna_identifier=rna.identifier, rna_description=rna.description,
                              callback=bool(callback), selectors=selectors,
                              property_instance='KeyMapItem.properties (native OperatorProperties)')
                labels = {cls.bl_label, catalog.get(cls.bl_label, cls.bl_label)}
                for name, values, context_values in scenarios(identifier, selectors, rna, property_labels):
                    case = {'name': name, 'properties': values, 'context': context_values, 'status': 'Failed'}
                    record['cases'].append(case)
                    try:
                        for selector in selectors:
                            properties.property_unset(selector)
                            check(not properties.is_property_set(selector, ghost=False),
                                  f'{identifier}.{selector}: default selector remains explicitly set')
                        defaults = {selector: getattr(properties, selector) for selector in selectors}
                        for selector, value in defaults.items():
                            check(value == rna.properties[selector].default,
                                  f'{identifier}.{selector}: unset native value differs from RNA default')
                        if name == 'defaults':
                            case['rna_defaults'] = defaults
                        for key, value in values.items():
                            setattr(properties, key, value)
                            check(getattr(properties, key) == value, f'{identifier}.{key}: RNA setter changed selector')
                        if context_values is None:
                            verify_case(identifier, cls, rna, callback, properties, catalog,
                                        labels, view, property_labels, case)
                        else:
                            for key in list(context_object.keys()):
                                del context_object[key]
                            for key, value in context_values.items():
                                context_object[key] = value
                            with bpy.context.temp_override(object=context_object, active_object=context_object):
                                verify_case(identifier, cls, rna, callback, properties, catalog,
                                            labels, view, property_labels, case)
                    except Exception as error:
                        case['error'] = f'{type(error).__name__}: {error}'
                record['status'] = 'Passed' if all(case['status'] == 'Passed' for case in record['cases']) else 'Failed'
            except Exception as error:
                record['error'] = f'{type(error).__name__}: {error}'
            finally:
                if item is not None:
                    keymap.keymap_items.remove(item)
        # WorkSpaceTools are intentionally not registered in background mode.
        for identifier, cls in sorted(tools.items()):
            record = {'tool': identifier, 'status': 'Failed', 'checks': []}
            report['workspace_tools'].append(record)
            try:
                english = cls.bl_description
                labels = {cls.bl_label, catalog.get(cls.bl_label, cls.bl_label)}
                validate_text(identifier, english, labels)
                check(english in catalog, f'{identifier}: untranslated tool description')
                chinese = catalog[english]
                validate_text(identifier, chinese, labels)
                check(chinese != english and any('\u4e00' <= c <= '\u9fff' for c in chinese),
                      f'{identifier}: tool description has no Chinese explanation')
                for language, interface, tooltips in itertools.product(LANGUAGES, (False, True), (False, True)):
                    set_preferences(view, language, interface, tooltips)
                    shown = bpy.app.translations.pgettext_tip(english, getattr(cls, 'bl_translation_context', '*'))
                    expected = chinese if language == 'zh_HANS' and tooltips else english
                    check(shown == expected, f'{identifier}: native tool-description lookup mismatch')
                    record['checks'].append({'language': language, 'translate_interface': interface,
                                             'translate_tooltips': tooltips, 'text': shown, 'status': 'Passed'})
                record['status'] = 'Passed'
            except Exception as error:
                record['error'] = f'{type(error).__name__}: {error}'
    finally:
        cleanup_errors = []
        for label, cleanup in (
                ('context_object', lambda: bpy.data.objects.remove(context_object, do_unlink=True)
                 if context_object is not None else None),
                ('keyconfig', lambda: bpy.context.window_manager.keyconfigs.remove(keyconfig)
                 if keyconfig is not None else None),
                ('preferences', lambda: set_preferences(view, *saved_preferences))):
            try:
                cleanup()
            except Exception as error:
                cleanup_errors.append(f'{label}: {type(error).__name__}: {error}')
        report['temporary_data_removed'] = (
            (context_object_name is None or context_object_name not in bpy.data.objects) and
            (keyconfig_name is None or keyconfig_name not in bpy.context.window_manager.keyconfigs))
        report['preferences_restored'] = saved_preferences == (
            view.language, view.use_translate_interface, view.use_translate_tooltips)
        report['cleanup_errors'] = cleanup_errors
        check(not cleanup_errors and report['temporary_data_removed'] and report['preferences_restored'],
              'Temporary validation resources or preferences could not be restored')
    failures = [row for row in [*report['operators'], *report['workspace_tools']] if row['status'] != 'Passed']
    check(not failures, f'{len(failures)} operators or tools failed; see per-case JSON evidence')
    report['status'] = 'Passed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--module', default='bl_ext.user_default.qcblender')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    args = parser.parse_args(argv)
    report = {
        'status': 'Failed', 'module': args.module, 'blender': bpy.app.version_string,
        'pid': os.getpid(), 'script_sha256': sha256(__file__), 'operators': [], 'workspace_tools': [],
        'method': 'Installed RNA metadata, registered callbacks with native OperatorProperties, '
                  'and bpy.app.translations.pgettext_tip; no QC operator execution',
        'gui_hover': 'Not Run', 'independent_human_review': 'Not Run',
    }
    try:
        run(args, report)
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        report['traceback'] = traceback.format_exc()
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if report['status'] != 'Passed':
        raise RuntimeError('Operator tooltip verification failed; see ' + str(args.output))
    print('QCBLENDER_OPERATOR_TOOLTIPS_PASSED ' + str(args.output))


if __name__ == '__main__':
    main()
