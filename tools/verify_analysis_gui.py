"""Foreground panel and IRC undo/redo smoke check for saved analysis projects."""
import importlib
import json
from pathlib import Path
import sys
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'analysis-gui'
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
kind = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'unknown'


def check():
    try:
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            if kind == 'nbo':
                obj = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'nbo')
                panel = 'QCBLENDER_PT_nbo'
            elif kind == 'paired':
                obj = next(o for o in bpy.data.objects if o.get('qc_view_kind') == 'scatter')
                panel = 'QCBLENDER_PT_paired_scatter'
            elif kind == 'esp':
                obj = next(o for o in bpy.data.objects if o.get('qc_analysis_role') == 'esp_area')
                panel = 'QCBLENDER_PT_external_results'
            elif kind == 'irc':
                obj = next(o for o in bpy.data.objects if o.get('qc_irc'))
                panel = 'QCBLENDER_PT_irc'
            elif kind == 'nocv':
                obj = next(o for o in bpy.data.objects if o.get('qc_analysis_role') == 'nocv_field')
                panel = 'QCBLENDER_PT_main'
            else:
                raise ValueError(kind)
            for previous in bpy.context.selected_objects:
                previous.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            if kind == 'irc':
                name = obj.name
                bpy.context.preferences.edit.use_global_undo = True
                bpy.ops.ed.undo_push(message='QC IRC baseline')
                assert obj['qc_irc_step'] == 2
                assert bpy.ops.qcblender.irc_step('EXEC_DEFAULT', True, direction='PREV') == {'FINISHED'}
                assert bpy.data.objects[name]['qc_irc_step'] == 1
                assert bpy.ops.ed.undo() == {'FINISHED'}
                assert bpy.data.objects[name]['qc_irc_step'] == 2
                assert bpy.ops.ed.redo() == {'FINISHED'}
                assert bpy.data.objects[name]['qc_irc_step'] == 1
            opened = bpy.ops.wm.call_panel(name=panel, keep_open=True)
            print('Panel invocation', kind, opened)
            bpy.ops.screen.screenshot(filepath=str(OUT / f'{kind}.png'))
        (OUT / f'{kind}.json').write_text(json.dumps({'panel': 'Passed',
                                                     'undo_redo': 'Passed' if kind == 'irc' else 'Not Run'}), encoding='utf-8')
        (OUT / f'{kind}-error.txt').unlink(missing_ok=True)
    except Exception:
        (OUT / f'{kind}-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(check, first_interval=2.0)
