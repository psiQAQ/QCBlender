"""Render all surface representations from the installed extension and a real Gaussian MO."""
import importlib
import json
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/composable'
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
graph = importlib.import_module(MODULE + '.blender.graph')
scene = bpy.context.scene
surface = next(o for o in scene.objects if o.get('qc_view_kind') == 'field')
modifier = graph.view_modifier(surface)
controls = {s.name: s.identifier for s in modifier.node_group.interface.items_tree if s.item_type == 'SOCKET'}
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.render.resolution_x = scene.render.resolution_y = 256
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.color_mode = 'RGBA'
for obj in scene.objects:
    if obj.type not in ('LIGHT', 'CAMERA') and obj != surface:
        obj.hide_render = True
counts = {}
for style, label in enumerate(('solid', 'wire', 'points')):
    modifier[controls['Style (0 solid, 1 wire, 2 points)']] = style
    surface.update_tag()
    scene.render.filepath = str(OUT / (label + '.png'))
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(scene.render.filepath, check_existing=False)
    pixels = np.array(image.pixels[:]).reshape(-1, 4)
    bpy.data.images.remove(image)
    assert (pixels[:, 3] > .01).sum() > 100, label
    assert (pixels[:, 0] > pixels[:, 2] + .02).sum() > 20, label
    assert (pixels[:, 2] > pixels[:, 0] + .02).sum() > 20, label
    counts[label] = int((pixels[:, 3] > .01).sum())
assert len(set(counts.values())) == 3
report = json.loads((OUT / 'report.json').read_text(encoding='utf-8'))
report['surface_style_render'] = 'Passed'
report['render_visible_pixels'] = counts
(OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
