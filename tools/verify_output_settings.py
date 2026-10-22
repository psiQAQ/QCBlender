"""Verify actual output operators, rendering and persistence in an installed candidate.

Run inside Blender with a preserved tutorial project; all outputs go to a new
directory. Existing scientific arrays and source transforms are compared exactly.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--case', choices=('mo', 'esp', 'fog'), required=True)
parser.add_argument('--reopen', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
camera_api = importlib.import_module(MODULE + '.blender.camera')
output_api = importlib.import_module(MODULE + '.blender.output_settings')
load_dataset = importlib.import_module(MODULE + '.data').load_dataset
scene = bpy.context.scene
REPORT = OUT / (args.case + '.json')


def snapshot():
    return {obj.name: {'matrix': [list(row) for row in obj.matrix_world],
            'manifest': obj.get('qc_dataset_sha256'),
            'arrays': {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in
                       load_dataset(bpy.path.abspath(obj['qc_dataset'])).arrays.items()}}
            for obj in scene.objects if obj.get('qc_dataset')}


def camera_state():
    return {'matrix': [list(row) for row in scene.camera.matrix_world],
            'scale': scene.camera.data.ortho_scale, 'name': scene.camera.name}


def select(objects):
    for obj in scene.objects:
        obj.select_set(False)
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def render(name, transparent=False):
    path = OUT / (name + '.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        pixels = np.asarray(image.pixels[:]).reshape((-1, 4))
        actual = tuple(image.size)
        expected = tuple(max(1, value * scene.render.resolution_percentage // 100)
                         for value in (scene.render.resolution_x, scene.render.resolution_y))
        assert actual == expected, (actual, expected)
        assert np.isfinite(pixels).all()
        if transparent:
            assert pixels[:, 3].min() == 0 and pixels[:, 3].max() > .9
            assert path.read_bytes()[25] == 6, 'PNG must carry alpha'
        else:
            assert path.read_bytes()[25] == 2, 'Opaque PNG must use RGB'
        assert pixels[:, :3].max() - pixels[:, :3].min() > .1, 'Empty render'
        return {'path': str(path), 'size': actual, 'alpha_range': [float(pixels[:, 3].min()),
                float(pixels[:, 3].max())], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    finally:
        bpy.data.images.remove(image)


def main():
    if args.reopen:
        record = json.loads(REPORT.read_text(encoding='utf-8'))
        assert scene.qc_output.active and snapshot() == record['snapshot']
        assert camera_state() == record['camera']
        assert output_api._settings(scene) == record['settings']
        assert len(scene.qc_output.rig_collection.objects) == 3
        record['cold_reopen'] = 'Passed'
        return record
    original_arrays = snapshot()
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    region = next(region for region in area.regions if region.type == 'WINDOW')
    if args.case == 'mo':
        target = next(obj for obj in scene.objects if obj.get('qc_view_kind') == 'field')
    elif args.case == 'esp':
        target = next(obj for obj in scene.objects if obj.get('qc_color_source') and
                      obj.get('qc_view_kind') == 'field')
    else:
        target = next(obj for obj in scene.objects if obj.get('qc_view_kind') == 'fog')
    select([target])
    baseline = output_api._settings(scene)
    original_camera, original_world = scene.camera, scene.world
    light_state = {obj: obj.hide_render for obj in scene.objects if obj.type == 'LIGHT'}
    owned_names = None
    records = []

    def apply(direction='PCA', quality='PREVIEW', background='WHITE', width=640, height=480):
        with bpy.context.temp_override(area=area, region=region):
            result = bpy.ops.qcblender.apply_output(direction=direction, quality=quality,
                background=background, resolution_x=width, resolution_y=height,
                resolution_percentage=100, margin=.05)
        assert result == {'FINISHED'}
        bpy.context.view_layer.update()
        assert scene.qc_output.active and scene.camera == scene.qc_output.camera
        assert scene.qc_output.original_camera == original_camera
        assert scene.qc_output.original_world == original_world
        assert json.loads(scene.qc_output.baseline_json) == baseline
        assert all(obj.hide_render for obj in light_state)
        rig = scene.qc_output.rig_collection
        assert len(rig.objects) == 3
        assert all(obj.data.type == 'AREA' and obj.data.normalize for obj in rig.objects)
        assert scene.view_settings.view_transform == 'Standard'
        points = camera_api._view_points(target, bpy.context.evaluated_depsgraph_get())
        projected = np.array([world_to_camera_view(scene, scene.camera, Vector(point))[:] for point in points])
        assert np.all(projected[:, :2] >= .0499) and np.all(projected[:, :2] <= .9501)
        assert np.all(projected[:, 2] > 0)
        return sorted(obj.name for obj in rig.objects) + [scene.camera.name]

    for direction in ('CURRENT', 'PCA', 'UNOBSTRUCTED'):
        names = apply(direction)
        if owned_names is None:
            owned_names = names
        assert names == owned_names, 'Repeated apply duplicated the rig or camera'
        assert snapshot() == original_arrays
        records.append({'direction': direction, 'camera': camera_state()})
    renders = [render(args.case + '-preview')]
    apply('PCA', 'STANDARD', 'TRANSPARENT')
    renders.append(render(args.case + '-standard-transparent', transparent=True))
    if args.case == 'mo':
        apply('PCA', 'HIGH', 'WHITE', 320, 240)
        renders.append(render('mo-high'))
    if args.case == 'esp':
        from_socket = importlib.import_module(MODULE + '.blender.node_identity').interface_socket
        modifier = importlib.import_module(MODULE + '.blender.graph').view_modifier(target)
        legend = from_socket(modifier.node_group, 'Show Legend')
        saved = bool(modifier[legend.identifier])
        with bpy.context.temp_override(area=area, region=region):
            before = camera_api.subject_points(bpy.context, [target])
        modifier[legend.identifier] = not saved
        target.update_tag()
        bpy.context.view_layer.update()
        with bpy.context.temp_override(area=area, region=region):
            after = camera_api.subject_points(bpy.context, [target])
        assert np.array_equal(before, after), 'Legend changes altered orientation samples'
        modifier[legend.identifier] = saved
        target.update_tag()
        bpy.context.view_layer.update()
    assert bpy.ops.qcblender.restore_output() == {'FINISHED'}
    assert not scene.qc_output.active and output_api._settings(scene) == baseline
    assert scene.camera == original_camera and scene.world == original_world
    assert {obj: obj.hide_render for obj in light_state} == light_state
    assert scene.qc_output.rig_collection.hide_render
    assert snapshot() == original_arrays
    if args.case == 'mo':
        shared_scene = bpy.data.scenes.new('QC shared-light verification')
        original_shared_world = scene.world
        shared_scene.world = original_shared_world
        data = bpy.data.lights.new('Shared-light verification', 'POINT')
        light = bpy.data.objects.new('Shared-light verification', data)
        scene.collection.objects.link(light)
        shared_scene.collection.objects.link(light)
        try:
            apply()
            assert not light.hide_render and light.name in shared_scene.objects
            assert light.name not in scene.objects and shared_scene.world == original_shared_world
            bpy.ops.qcblender.restore_output()
            assert light.name in scene.objects and not light.hide_render
        finally:
            bpy.data.scenes.remove(shared_scene)
            bpy.data.objects.remove(light, do_unlink=True)
            bpy.data.lights.remove(data)
        shared_scene = bpy.data.scenes.new('QC shared-collection verification')
        collection = bpy.data.collections.new('Shared-light collection verification')
        scene.collection.children.link(collection)
        shared_scene.collection.children.link(collection)
        data = bpy.data.lights.new('Shared-collection light', 'POINT')
        light = bpy.data.objects.new('Shared-collection light', data)
        collection.objects.link(light)
        try:
            try:
                output_api.validate_output(scene)
            except ValueError as error:
                assert 'shared or instanced collection' in str(error)
            else:
                raise AssertionError('Shared collection must be rejected before mutation')
            assert output_api._settings(scene) == baseline and not scene.qc_output.active
        finally:
            bpy.data.scenes.remove(shared_scene)
            bpy.data.objects.remove(light, do_unlink=True)
            bpy.data.lights.remove(data)
            bpy.data.collections.remove(collection)
    apply('PCA', 'STANDARD', 'TRANSPARENT')
    assert snapshot() == original_arrays
    importlib.import_module(MODULE + '.blender.project').save_project(OUT / (args.case + '.blend'))
    return {'status': 'Passed', 'blender': bpy.app.version_string, 'case': args.case,
            'source': str(Path(bpy.data.filepath)), 'directions': records, 'renders': renders,
            'arrays_and_transforms': 'Passed', 'restore': 'Passed', 'repeat_apply': 'Passed',
            'shared_scenes': 'Passed' if args.case == 'mo' else 'Not Run',
            'legend_excluded': 'Passed' if args.case == 'esp' else 'Not Run',
            'snapshot': snapshot(), 'camera': camera_state(), 'settings': output_api._settings(scene),
            'cold_reopen': 'Not Run'}


try:
    report = main()
except Exception:
    report = {'status': 'Failed', 'case': args.case, 'traceback': traceback.format_exc()}
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    raise
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'status': report['status'], 'report': str(REPORT)}))
