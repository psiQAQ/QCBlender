"""Exercise Properties navigation with Blender's real dynamic RNA contexts."""
import argparse
import importlib
import json
from pathlib import Path
import sys
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--quit', action='store_true')
parser.add_argument('--module', default='qcblender')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
report = {'blender': bpy.app.version_string, 'checks': [], 'status': 'Failed'}


def check(name, editor, expected):
    if not bpy.app.background:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    before = (space.context, space.pin_id, space.use_pin_id)
    result = bpy.ops.qcblender.open_properties(editor=editor)
    assert result == {expected}, (name, result)
    if expected == 'CANCELLED':
        assert (space.context, space.pin_id, space.use_pin_id) == before, name
    else:
        assert space.context == editor, (name, space.context)
    report['checks'].append({'name': name, 'status': 'Passed'})


def run():
    global area, space
    if args.module != 'qcblender':
        bpy.ops.preferences.addon_enable(module=args.module)
    operator = importlib.import_module(args.module + '.blender.editor_ui').QCBLENDER_OT_open_properties
    registered = not operator.is_registered
    if registered:
        bpy.utils.register_class(operator)
    report['module_path'] = importlib.import_module(args.module).__file__
    area = next(a for a in bpy.context.screen.areas if a.type == 'PROPERTIES')
    space = area.spaces.active
    try:
        run_checks()
        report['status'] = 'Passed'
    except Exception:
        report['error'] = traceback.format_exc()
        print(report['error'])
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if registered:
            bpy.utils.unregister_class(operator)
    print(json.dumps(report, ensure_ascii=False))
    if args.quit:
        bpy.ops.wm.quit_blender()
    if report['status'] != 'Passed' and bpy.app.background:
        raise AssertionError(report['error'])


def run_checks():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    assert bpy.context.object is None
    check('empty scene object properties', 'OBJECT', 'CANCELLED')
    check('empty scene material properties', 'MATERIAL', 'CANCELLED')
    check('empty scene render properties', 'RENDER', 'FINISHED')
    check('empty scene output properties', 'OUTPUT', 'FINISHED')

    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.object
    check('active mesh object properties', 'OBJECT', 'FINISHED')
    assert space.pin_id == obj and space.use_pin_id
    check('mesh without material', 'MATERIAL', 'FINISHED')
    bpy.context.view_layer.objects.active = None
    check('no active object with pinned mesh', 'OBJECT', 'CANCELLED')
    check('no active object with pinned mesh material', 'MATERIAL', 'CANCELLED')
    bpy.context.view_layer.objects.active = obj

    other = bpy.data.objects.new('Other object', None)
    bpy.context.collection.objects.link(other)
    space.pin_id = other
    check('replace existing pin with active mesh', 'OBJECT', 'FINISHED')
    assert space.pin_id == obj
    area.type = 'TEXT_EDITOR'
    try:
        check('missing Properties editor', 'OBJECT', 'CANCELLED')
    except RuntimeError as exc:
        # Blender promotes ERROR reports to RuntimeError at the operator boundary.
        assert '请先将一个编辑器切换为属性编辑器' in str(exc), str(exc)
        report['checks'].append({'name': 'missing Properties editor', 'status': 'Passed'})


if bpy.app.background:
    run()
else:
    bpy.app.timers.register(run, first_interval=1.0)
