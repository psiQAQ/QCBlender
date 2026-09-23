"""Foreground undo/redo checks for ESP, AIM, and ETS imports."""
import importlib
import json
from pathlib import Path
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'external-results'
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
views = importlib.import_module(MODULE + '.blender.views')


def check():
    try:
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            parent = views.atom_view(OUT / 'reference.qcdata')
            parent_name = parent.name
            parent['qc_field'] = '{"quantity":"electrostatic_potential"}'
            bpy.context.preferences.edit.use_global_undo = True
            for role, call in (
                ('esp_area', lambda: bpy.ops.qcblender.import_esp_analysis(
                    'EXEC_DEFAULT', True, extrema_path=str(OUT / 'synthetic-extrema.pdb'),
                    area_path=str(OUT / 'synthetic-area.txt'))),
                ('aim_paths', lambda: bpy.ops.qcblender.import_aim_analysis(
                    'EXEC_DEFAULT', True, cps_path=str(OUT / 'synthetic-cps.pdb'),
                    paths_path=str(OUT / 'synthetic-paths.pdb'),
                    properties_path=str(OUT / 'synthetic-cpprop.txt'))),
                ('ets_nocv', lambda: bpy.ops.qcblender.import_ets_nocv(
                    'EXEC_DEFAULT', True, output_path=str(OUT / 'synthetic-ets.txt'),
                    energy_unit='kcal/mol')),
            ):
                for selected in bpy.context.selected_objects:
                    selected.select_set(False)
                parent = bpy.data.objects[parent_name]
                parent.select_set(True)
                bpy.context.view_layer.objects.active = parent
                bpy.ops.ed.undo_push(message='QC analysis import baseline')
                assert call() == {'FINISHED'}
                assert any(obj.get('qc_analysis_role') == role for obj in bpy.data.objects)
                assert bpy.ops.ed.undo() == {'FINISHED'}
                assert not any(obj.get('qc_analysis_role') == role for obj in bpy.data.objects)
                assert bpy.ops.ed.redo() == {'FINISHED'}
                assert any(obj.get('qc_analysis_role') == role for obj in bpy.data.objects)
        (OUT / 'gui.json').write_text(json.dumps({'esp': 'Passed', 'aim': 'Passed',
                                                  'ets': 'Passed'}), encoding='utf-8')
        (OUT / 'gui-error.txt').unlink(missing_ok=True)
    except Exception:
        (OUT / 'gui-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(check, first_interval=2.0)
