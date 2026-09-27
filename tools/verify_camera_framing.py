"""Check native camera projection of evaluated QC views in an installed candidate."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Quaternion, Vector
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--reopen', choices=('saved', 'moved'))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
project = importlib.import_module(MODULE + '.blender.project')
load_dataset = importlib.import_module(MODULE + '.data').load_dataset
scene = bpy.context.scene
REPORT = OUT / 'camera.json'


def snapshot():
    return {obj.name: {'manifest': obj['qc_dataset_sha256'],
            'arrays': {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in
                       load_dataset(bpy.path.abspath(obj['qc_dataset'])).arrays.items()}}
            for obj in scene.objects if obj.get('qc_dataset')}


def camera_state():
    camera = scene.camera
    return {'name': camera.name, 'matrix': [list(row) for row in camera.matrix_world],
            'scale': camera.data.ortho_scale, 'type': camera.data.type}


if args.reopen:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert snapshot() == report['snapshot'] and camera_state() == report['camera']
    scene.render.filepath = str(OUT / (args.reopen + '.png'))
    bpy.ops.render.render(write_still=True)
    report[args.reopen + '_cold_reopen'] = 'Passed'
else:
    atom = next(o for o in scene.objects if o.get('qc_view_kind') == 'atoms')
    field = next(o for o in scene.objects if o.get('qc_view_kind') == 'field')
    fog = importlib.import_module(MODULE + '.blender.fog').fog_view(field)
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    area.spaces.active.region_3d.view_rotation = Quaternion((1, 0, 0), 1.1)
    old_camera = scene.camera
    old_state = camera_state()
    old_lights = {o.name: [list(row) for row in o.matrix_world] for o in scene.objects if o.type == 'LIGHT'}
    original_arrays = snapshot()
    records = []

    def select(objects):
        for obj in scene.objects:
            obj.select_set(False)
        for obj in objects:
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]

    def create():
        with bpy.context.temp_override(area=area, region=region):
            assert bpy.ops.qcblender.create_framed_camera(margin=.05) == {'FINISHED'}
        bpy.context.view_layer.update()
        assert scene.camera != old_camera

    def geometry_points(objects):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        points = []
        for obj in objects:
            evaluated = obj.evaluated_get(depsgraph)
            if obj.get('qc_view_kind') == 'fog':
                source = obj.qc_settings.volume.evaluated_get(depsgraph)
                points.extend(source.matrix_world @ Vector(p) for p in source.bound_box)
            else:
                mesh = evaluated.to_mesh()
                try:
                    points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
                finally:
                    evaluated.to_mesh_clear()
        assert points
        return points

    def check(label, objects, resolution=(800, 600), pixel=(1, 1)):
        select(objects)
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.pixel_aspect_x, scene.render.pixel_aspect_y = pixel
        before = {o.name: [list(row) for row in o.matrix_world] for o in scene.objects}
        create()
        for name, matrix in before.items():
            assert [list(row) for row in bpy.data.objects[name].matrix_world] == matrix
        projected = np.array([world_to_camera_view(scene, scene.camera, p)[:] for p in geometry_points(objects)])
        assert np.all(projected[:, :2] >= .0499) and np.all(projected[:, :2] <= .9501), (label, projected.min(0), projected.max(0))
        assert np.all(projected[:, 2] > 0)
        for obj in (atom, field, fog):
            obj.hide_render = obj not in objects
        scene.render.filepath = str(OUT / (label + '.png'))
        bpy.ops.render.render(write_still=True)
        records.append({'label': label, 'resolution': resolution, 'pixel_aspect': pixel,
                        'ndc_min': projected.min(0).tolist(), 'ndc_max': projected.max(0).tolist(), 'camera': camera_state()})
        for obj in (atom, field, fog):
            obj.hide_render = False

    scene.cycles.samples = 12
    check('atoms-landscape', [atom])
    check('atoms-portrait', [atom], (600, 800))
    check('isosurface', [field])
    check('fog', [fog])
    atom.location = (3, 1, 0)
    atom.rotation_euler = (.2, -.3, .7)
    atom.scale = (1.2, .8, 1.1)
    bpy.context.view_layer.update()
    check('multi-transform', [atom, field])
    check('pixel-aspect', [atom, field], (600, 800), (2, 1))
    select([atom])
    create()
    visible_state = camera_state()
    hidden = atom.copy()
    scene.collection.objects.link(hidden)
    hidden.location = (1000, 1000, 1000)
    hidden.hide_render = True
    select([atom, hidden, field.qc_settings.volume])
    create()
    assert scene.camera.data.ortho_scale == visible_state['scale']
    assert [list(row) for row in scene.camera.matrix_world] == visible_state['matrix']
    hidden.hide_set(True)
    errors = {}

    def rejected(label, expected):
        before = set(bpy.data.cameras.keys())
        try:
            create()
        except RuntimeError as error:
            assert expected in str(error), error
            errors[label] = str(error)
        else:
            raise AssertionError(label)
        assert set(bpy.data.cameras.keys()) == before

    select([atom])
    modifier = atom.modifiers[0]
    for viewport, render in ((True, False), (False, True)):
        modifier.show_viewport, modifier.show_render = viewport, render
        rejected(f'modifier-{viewport}-{render}', 'different viewport/render visibility')
    modifier.show_viewport = modifier.show_render = True
    empty = bpy.data.objects.new('Empty QC framing boundary', bpy.data.meshes.new('Empty QC boundary'))
    scene.collection.objects.link(empty)
    empty['qc_view_kind'] = 'atoms'
    select([empty])
    rejected('empty', 'no geometry or volume bounds')
    empty.hide_render = True
    rejected('hidden-only', 'Select a renderable QC display view')
    assert camera_state()['type'] == 'ORTHO'
    assert [list(row) for row in old_camera.matrix_world] == old_state['matrix']
    assert old_camera.data.ortho_scale == old_state['scale']
    assert {o.name: [list(row) for row in o.matrix_world] for o in scene.objects if o.type == 'LIGHT'} == old_lights
    for name, original in original_arrays.items():
        assert snapshot()[name] == original
    check('final', [atom, field])
    fog.hide_render = True
    project.save_project(OUT / 'camera.blend')
    moved = OUT / 'moved'
    moved.mkdir(exist_ok=True)
    shutil.copy2(OUT / 'camera.blend', moved / 'camera.blend')
    shutil.copytree(OUT / 'camera.qcdata', moved / 'camera.qcdata', dirs_exist_ok=True)
    report = {'status': 'Passed', 'blender': bpy.app.version_string, 'projection_checks': records,
              'hidden_and_internal_excluded': 'Passed', 'old_camera_lights_transforms_preserved': 'Passed',
              'errors': errors, 'arrays_unchanged': 'Passed', 'snapshot': snapshot(), 'camera': camera_state(),
              'saved_cold_reopen': 'Not Run', 'moved_cold_reopen': 'Not Run'}
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({key: value for key, value in report.items() if key not in ('snapshot', 'projection_checks')}))
