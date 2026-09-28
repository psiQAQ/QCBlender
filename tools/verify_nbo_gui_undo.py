"""Foreground NBO import and undo/redo check with a real Gaussian Log."""
import importlib
import json
from pathlib import Path
import time
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
OUT = ROOT / 'outputs' / 'nbo-acceptance'
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
views = importlib.import_module(MODULE + '.blender.views')
started = time.monotonic()


def finish(error=None):
    if error:
        (OUT / 'gui-undo-error.txt').write_text(error, encoding='utf-8')
    else:
        (OUT / 'gui-undo.json').write_text(json.dumps({'import': 'Passed', 'undo': 'Passed',
                                                       'redo': 'Passed'}), encoding='utf-8')
        (OUT / 'gui-undo-error.txt').unlink(missing_ok=True)
    bpy.ops.wm.quit_blender()
    return None


def begin():
    try:
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            obj = views.atom_view(OUT / 'reference.qcdata')
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.context.preferences.edit.use_global_undo = True
            bpy.ops.ed.undo_push(message='QC NBO baseline')
            result = bpy.ops.qcblender.import_nbo(
                'EXEC_DEFAULT', True,
                filepath=str(input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)),
                job_number=2, block_number=1)
            assert result == {'RUNNING_MODAL'}, result
        bpy.app.timers.register(check, first_interval=.5)
    except Exception:
        return finish(traceback.format_exc())
    return None


def check():
    try:
        if not any(obj.get('qc_view_kind') == 'nbo' for obj in bpy.data.objects):
            if time.monotonic() - started > 25:
                raise TimeoutError('NBO modal import did not finish')
            return .5
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            assert bpy.ops.ed.undo() == {'FINISHED'}
            assert not any(obj.get('qc_view_kind') == 'nbo' for obj in bpy.data.objects)
            assert bpy.ops.ed.redo() == {'FINISHED'}
            assert any(obj.get('qc_view_kind') == 'nbo' for obj in bpy.data.objects)
        return finish()
    except Exception:
        return finish(traceback.format_exc())


bpy.app.timers.register(begin, first_interval=2.0)
