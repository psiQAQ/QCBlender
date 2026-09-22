"""Render installed volume nodes and verify their optical transfer and cold open."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/fog-acceptance'
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
fog = importlib.import_module(MODULE + '.blender.fog')
project = importlib.import_module(MODULE + '.blender.project')
scene = bpy.context.scene


def render(name):
    scene.render.filepath = str(OUT / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(scene.render.filepath, check_existing=False)
    try:
        return np.array(image.pixels[:]).reshape(-1, 4)
    finally:
        bpy.data.images.remove(image)


if '--reopen-fog' in sys.argv:
    report = json.loads((OUT / 'report.json').read_text(encoding='utf-8'))
    obj = bpy.data.objects[report['object']]
    assert obj.qc_settings.volume is not None
    actual = render('fog-reopened')
    previous = bpy.data.images.load(str(OUT / 'fog.png'), check_existing=False)
    try:
        expected = np.array(previous.pixels[:]).reshape(-1, 4)
    finally:
        bpy.data.images.remove(previous)
    np.testing.assert_allclose(actual, expected, atol=1/255)
    report['cold_open_render'] = 'Passed'
else:
    source = next(o for o in scene.objects if o.get('qc_view_kind') == 'field')
    cache = Path(bpy.path.abspath(source.qc_settings.volume.data.filepath))
    digest = hashlib.sha256(cache.read_bytes()).hexdigest()
    for obj in scene.objects:
        if obj.type not in ('LIGHT', 'CAMERA'):
            obj.hide_render = True
    bpy.context.view_layer.objects.active = source
    assert bpy.ops.qcblender.create_fog() == {'FINISHED'}
    obj = bpy.context.object
    assert obj.get('qc_view_kind') == 'fog'
    modifier = obj.modifiers[0]
    item = next(s for s in modifier.node_group.interface.items_tree if s.name == 'Material')
    mat = modifier[item.identifier]
    assert mat['qc_transfer'].startswith('scale * abs(value)')
    assert fog.fog_material('electron_number_density')['qc_transfer'].startswith('scale * max(value, 0)')
    opacity = mat.node_tree.nodes['Optical Scale'].outputs[0]
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = False
    scene.cycles.seed = 17
    scene.render.resolution_x = scene.render.resolution_y = 192
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    opacity.default_value = 0
    empty = render('fog-zero')
    assert empty[:, 3].max() == 0, empty[:, 3].max()
    opacity.default_value = 20
    visible = render('fog')
    assert (visible[:, 3] > .05).sum() > 100
    assert ((visible[:, 3] > .05) & (visible[:, 3] < .95)).sum() > 100
    assert (visible[:, 0] > visible[:, 2] + .02).sum() > 20, 'Missing negative red lobe'
    assert (visible[:, 2] > visible[:, 0] + .02).sum() > 20, 'Missing positive blue lobe'
    controls = {n.get('qc_control'): n for n in mat.node_tree.nodes if n.get('qc_control')}
    controls['Plane Enabled'].outputs[0].default_value = 1
    clipped = render('fog-plane')
    assert clipped[:, 3].sum() < visible[:, 3].sum() * .9
    controls['Plane Enabled'].outputs[0].default_value = 0
    controls['Box Enabled'].outputs[0].default_value = 1
    for value in controls['Box Minimum'].inputs:
        value.default_value = 20
    for value in controls['Box Maximum'].inputs:
        value.default_value = 21
    boxed = render('fog-box-outside')
    assert boxed[:, 3].max() == 0
    controls['Box Enabled'].outputs[0].default_value = 0
    curve = next(n for n in mat.node_tree.nodes if n.get('qc_role') == 'opacity_ramp')
    curve.color_ramp.elements.new(.5).color = (0, 0, 0, 1)
    for element in curve.color_ramp.elements:
        element.color = (0, 0, 0, 1)
    curve_zero = render('fog-curve-zero')
    assert curve_zero[:, 3].max() == 0
    for element in curve.color_ramp.elements:
        element.color = (1, 1, 1, 1)
    assert hashlib.sha256(cache.read_bytes()).hexdigest() == digest
    project.save_project(OUT / 'fog.blend')
    report = {'status': 'Passed', 'blender': bpy.app.version_string,
              'operator': 'Passed', 'zero_opacity': 'Passed', 'signed_color_render': 'Passed',
              'source_cache_unchanged': 'Passed', 'cold_open_render': 'Not Run',
              'plane_box_clip_render': 'Passed', 'opacity_curve_render': 'Passed',
              'visible_pixels': int((visible[:, 3] > .05).sum()), 'object': obj.name}
(OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
