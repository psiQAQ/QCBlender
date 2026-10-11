"""Audit native operator polls and visible panel/menu draw paths in a fresh Blender.

Run with --factory-startup: this script replaces the scene with empty/Cube cases.
The layout recorder checks Python draw paths; real GUI rendering remains separate.
"""
import argparse
import importlib
import json
from pathlib import Path
import sys
import traceback
from types import SimpleNamespace

import bpy


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--module', default='qcblender')
parser.add_argument('--source-root', type=Path, default=ROOT)
parser.add_argument('--quit', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
sys.path.insert(0, str(args.source_root))
report = {'status': 'Failed', 'blender': bpy.app.version_string,
          'checks': [], 'buttons': [], 'limitations': ['Layout recording is not GUI rendering']}


class Layout:
    def __init__(self, owner, parent=None):
        self.owner, self.parent = owner, parent
        self.enabled = True

    def row(self, **kwargs):
        return Layout(self.owner, self)

    column = box = split = grid_flow = row

    def operator(self, name, **kwargs):
        node, enabled = self, True
        while node is not None:
            enabled = enabled and node.enabled
            node = node.parent
        group, action = name.split('.')
        available = getattr(getattr(bpy.ops, group), action).poll()
        report['buttons'].append(dict(owner=self.owner, operator=name,
                                      text=kwargs.get('text', ''), enabled=bool(enabled and available)))
        return SimpleNamespace()

    def label(self, **kwargs):
        pass

    def separator(self, **kwargs):
        pass

    def prop(self, *args, **kwargs):
        pass

    def template_list(self, *args, **kwargs):
        pass


def check(name, function):
    try:
        details = function()
    except Exception:
        report['checks'].append(dict(name=name, status='Failed', error=traceback.format_exc()))
    else:
        report['checks'].append(dict(name=name, status='Passed', result=details))


def native_poll(cls):
    group, name = cls.bl_idname.split('.')
    return getattr(getattr(bpy.ops, group), name).poll()


def run_checks(classes):
    by_id = {getattr(cls, 'bl_idname', cls.__name__): cls for cls in classes}

    def panel_available(cls):
        parent = by_id.get(getattr(cls, 'bl_parent_id', None))
        if parent is not None and not panel_available(parent):
            return False
        poll = getattr(cls, 'poll', None)
        return bool(poll(bpy.context)) if poll is not None else True

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for scenario in ('empty', 'default_cube'):
        if scenario == 'default_cube':
            bpy.ops.mesh.primitive_cube_add()
            assert bpy.context.object is not None and not bpy.context.object.get('qc_dataset')
        for cls in classes:
            if issubclass(cls, bpy.types.Operator):
                check(f'{scenario}: native poll {cls.bl_idname}', lambda cls=cls: native_poll(cls))
        for cls in classes:
            if issubclass(cls, bpy.types.Menu):
                owner = f'{scenario}: direct menu {cls.__name__}'
                check(owner, lambda cls=cls, owner=owner: cls.draw(
                    SimpleNamespace(layout=Layout(owner)), bpy.context))
            elif issubclass(cls, bpy.types.Panel):
                def draw_panel(cls=cls):
                    if not panel_available(cls):
                        return 'Not applicable (panel or parent poll)'
                    owner = f'{scenario}: panel {cls.__name__}'
                    cls.draw(SimpleNamespace(layout=Layout(owner)), bpy.context)
                    return 'Draw path completed'
                check(f'{scenario}: panel {cls.__name__}', draw_panel)


def run():
    try:
        package = importlib.import_module(args.module)
        if not hasattr(bpy.types.Object, 'qc_settings'):
            package.register()
        report['module_path'] = package.__file__
        classes = importlib.import_module(args.module + '.auto_load').discover()
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            run_checks(classes)
        report['status'] = 'Failed' if any(row['status'] == 'Failed' for row in report['checks']) else 'Passed'
    except Exception:
        report['error'] = traceback.format_exc()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    failures = [row for row in report['checks'] if row['status'] == 'Failed']
    print(json.dumps(dict(status=report['status'], checks=len(report['checks']),
                          buttons=len(report['buttons']), failures=failures,
                          error=report.get('error')), ensure_ascii=False))
    if args.quit:
        bpy.ops.wm.quit_blender()
    if report['status'] != 'Passed' and bpy.app.background:
        raise AssertionError('Empty button audit failed; see ' + str(args.report))


if bpy.app.background:
    run()
else:
    bpy.app.timers.register(run, first_interval=1.0)
