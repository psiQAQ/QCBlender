"""Foreground Blender undo/redo check for hydrogen visibility."""
import importlib
import json
from pathlib import Path
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'atom-visibility'
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
layers = importlib.import_module(MODULE + '.blender.layers')


def check():
    try:
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            source = next(obj for obj in layers.display_layers(bpy.context.scene)
                          if obj.get('qc_hydrogen_visibility') == 'KEEP')
            layers.activate(bpy.context, source)
            name = source.name
            before = source['qc_hydrogen_visibility']
            bpy.context.preferences.edit.use_global_undo = True
            bpy.ops.ed.undo_push(message='QC H visibility baseline')
            assert bpy.ops.qcblender.hydrogen_visibility('EXEC_DEFAULT', True, mode='HIDE') == {'FINISHED'}
            assert bpy.data.objects[name]['qc_hydrogen_visibility'] == 'HIDE'
            assert bpy.ops.ed.undo() == {'FINISHED'}
            assert bpy.data.objects[name]['qc_hydrogen_visibility'] == before
            assert bpy.ops.ed.redo() == {'FINISHED'}
            assert bpy.data.objects[name]['qc_hydrogen_visibility'] == 'HIDE'
            area.spaces.active.show_region_ui = True
            bpy.ops.wm.call_panel(name='QCBLENDER_PT_layers', keep_open=True)
            bpy.ops.screen.screenshot(filepath=str(OUT / 'visibility-gui.png'))
        (OUT / 'gui.json').write_text(json.dumps({'undo': 'Passed', 'redo': 'Passed',
                                                 'panel': 'Passed'}), encoding='utf-8')
        (OUT / 'gui-error.txt').unlink(missing_ok=True)
    except Exception:
        (OUT / 'gui-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(check, first_interval=2.0)
