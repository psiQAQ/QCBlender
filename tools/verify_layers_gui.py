"""Run in an isolated foreground Blender process; verify undo and capture UI."""
import importlib
import json
from pathlib import Path
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/layer-acceptance'
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
layers = importlib.import_module(MODULE + '.blender.layers')
assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(ROOT / 'outputs')
phase = 0


def check():
    global phase
    try:
        area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        if phase == 0:
            with bpy.context.temp_override(area=area, region=region):
                source = next(o for o in layers.display_layers(bpy.context.scene) if o.get('qc_view_kind') == 'fog')
                layers.activate(bpy.context, source)
                name = source.name
                before = len(layers.display_layers(bpy.context.scene))
                bpy.context.preferences.edit.use_global_undo = True
                bpy.ops.ed.undo_push(message='QC layer baseline')
                assert bpy.ops.qcblender.layer_action('EXEC_DEFAULT', True, target=name, action='DUPLICATE') == {'FINISHED'}
                assert len(layers.display_layers(bpy.context.scene)) == before + 1
                assert bpy.ops.ed.undo() == {'FINISHED'}
                assert len(layers.display_layers(bpy.context.scene)) == before
                assert bpy.ops.ed.redo() == {'FINISHED'}
                assert len(layers.display_layers(bpy.context.scene)) == before + 1
                assert bpy.ops.ed.undo() == {'FINISHED'}
                assert len(layers.display_layers(bpy.context.scene)) == before
            phase = 1
            return 1.0
        if phase == 1:
            area.spaces.active.show_region_ui = True
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.tag_redraw()
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.wm.call_panel(name='QCBLENDER_PT_layers', keep_open=True)
            phase = 2
            return 2.0
        with bpy.context.temp_override(area=area):
            bpy.ops.screen.screenshot(filepath=str(OUT / ('display-layers.png' if phase == 2 else 'display-controls.png')))
        if phase == 2:
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.wm.call_panel(name='QCBLENDER_PT_main', keep_open=True)
            phase = 3
            return 2.0
        report = json.loads((OUT / 'report.json').read_text(encoding='utf-8'))
        report['undo'] = 'Passed'
        report['gui_screenshot'] = 'display-layers.png'
        (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        (OUT / 'gui-error.txt').unlink(missing_ok=True)
        bpy.ops.wm.quit_blender()
    except Exception:
        (OUT / 'gui-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
        bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(check, first_interval=2.0)
