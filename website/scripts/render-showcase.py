"""Render an opened tutorial COPY through the installed QCBlender operators.

Called over the existing Blender MCP after checking process identity. This file
does not start Blender, install dependencies, or alter the source tutorial.
"""
import hashlib
import importlib
import json
import os
from pathlib import Path

import bpy
import numpy as np


PACKAGE = 'bl_ext.user_default.qcblender'


def module(name):
    return importlib.import_module(PACKAGE + '.' + name)


def plain(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bpy.types.ID):
        return value.name
    return list(value)


def science():
    return {obj.name: {
        'matrix': [list(row) for row in obj.matrix_world],
        'dataset': obj.get('qc_dataset_sha256'),
        'arrays': {key: hashlib.sha256(array.tobytes()).hexdigest()
                   for key, array in module('data').load_dataset(
                       bpy.path.abspath(obj['qc_dataset'])).arrays.items()}}
        for obj in bpy.context.scene.objects if obj.get('qc_dataset')}


def camera():
    obj = bpy.context.scene.camera
    return {'matrix': [list(row) for row in obj.matrix_world],
            'scale': obj.data.ortho_scale, 'name': obj.name}


def check_identity(expected_pid, project):
    assert os.getpid() == expected_pid, 'Blender process changed'
    assert Path(bpy.data.filepath).resolve() == Path(project).resolve(), 'Project changed'


def prepare(case, expected_pid, project, output_dir):
    check_identity(expected_pid, project)
    scene = bpy.context.scene
    before = science()
    fields = [obj for obj in scene.objects if obj.get('qc_view_kind') == 'field'
              and not obj.hide_render]
    if case == 'esp':
        fields = [obj for obj in fields if obj.get('qc_color_source')]
    assert len(fields) == 1, f'Ambiguous visible fields: {[obj.name for obj in fields]}'
    target = fields[0]
    for obj in scene.objects:
        obj.select_set(False)
        if obj.get('qc_view_kind') and obj not in fields and obj.get('qc_view_kind') != 'atoms':
            obj.hide_render = True
    target.hide_set(False)
    target.select_set(True)
    if case == 'igmh':
        for obj in scene.objects:
            if obj.get('qc_view_kind') == 'atoms' and not obj.hide_render:
                obj.hide_set(False)
                obj.select_set(True)
    bpy.context.view_layer.objects.active = target
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    region = next(region for region in area.regions if region.type == 'WINDOW')
    options = dict(direction='PCA', quality='STANDARD',
                   background='TRANSPARENT' if case == 'orbital' else 'WHITE',
                   resolution_x=1600, resolution_y=1360 if case == 'orbital' else 1200,
                   resolution_percentage=100, margin=.09)

    def apply():
        with bpy.context.temp_override(area=area, region=region):
            assert bpy.ops.qcblender.apply_output(**options) == {'FINISHED'}
        bpy.context.view_layer.update()

    apply()
    if case == 'igmh':
        # A planar interaction surface is edge-on in the molecular principal plane.
        # Turn the view, then let the same operator refit all selected subjects.
        import math
        from mathutils import Quaternion
        area.spaces.active.region_3d.view_rotation = (
            scene.camera.matrix_world.to_quaternion() @ Quaternion((0, 1, 0), math.radians(35)))
        options['direction'] = 'CURRENT'
        apply()
    modifier = next(mod for mod in target.modifiers if mod.type == 'NODES')
    if case != 'orbital':
        rotation = module('blender.node_identity').interface_socket(modifier.node_group, 'Legend Rotation')
        local = target.matrix_world.to_quaternion().inverted() @ scene.camera.matrix_world.to_quaternion()
        modifier[rotation.identifier] = tuple(local.to_euler())
        target.update_tag()
        bpy.context.view_layer.update()
        apply()
    assert science() == before, 'Scientific arrays or transforms changed'
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    record = {'case': case, 'status': 'Prepared', 'pid': os.getpid(),
              'blender': bpy.app.version_string, 'project': str(Path(project)),
              'target': target.name, 'options': options, 'science': before,
              'camera': camera(), 'field': json.loads(target.get('qc_field', '{}')),
              'color_source': json.loads(target.get('qc_color_source', '{}')),
              'inputs': {socket.name: plain(modifier.get(socket.identifier, socket.default_value))
                         for socket in modifier.node_group.interface.items_tree
                         if socket.item_type == 'SOCKET' and socket.in_out == 'INPUT'
                         and hasattr(socket, 'default_value')}, 'cold_reopen': 'Not Run'}
    (out / (case + '.json')).write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return {'status': 'Prepared', 'target': target.name, 'options': options}


def render(case, expected_pid, project, output_dir):
    check_identity(expected_pid, project)
    out = Path(output_dir)
    report = out / (case + '.json')
    record = json.loads(report.read_text(encoding='utf-8'))
    scene = bpy.context.scene
    scene.render.use_compositing = False
    record['compositing'] = False
    scene.render.filepath = str(out / (case + '.png'))
    assert bpy.ops.render.render(write_still=True) == {'FINISHED'}
    image = bpy.data.images.load(scene.render.filepath, check_existing=False)
    try:
        pixels = np.asarray(image.pixels[:]).reshape((-1, 4))
        assert tuple(image.size) == (scene.render.resolution_x, scene.render.resolution_y)
        assert np.isfinite(pixels).all() and np.ptp(pixels[:, :3], axis=0).max() > .1
        if case == 'orbital':
            assert pixels[:, 3].min() == 0 and pixels[:, 3].max() > .9
        record['image'] = {'size': list(image.size), 'sha256': hashlib.sha256(
            Path(scene.render.filepath).read_bytes()).hexdigest()}
    finally:
        bpy.data.images.remove(image)
    assert science() == record['science']
    module('blender.project').save_project(Path(project))
    assert science() == record['science']
    record.update(status='Passed', arrays_and_transforms='Passed', camera=camera())
    report.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return {'status': 'Passed', 'image': record['image'], 'report': str(report)}


def reopen(case, expected_pid, project, output_dir):
    check_identity(expected_pid, project)
    report = Path(output_dir) / (case + '.json')
    record = json.loads(report.read_text(encoding='utf-8'))
    assert record['status'] == 'Passed'
    assert science() == record['science']
    assert camera() == record['camera']
    for obj in bpy.context.scene.objects:
        if obj.type == 'VOLUME' and obj.data.filepath:
            assert Path(bpy.path.abspath(obj.data.filepath)).is_file()
    record['cold_reopen'] = 'Passed'
    record['cold_reopen_pid'] = os.getpid()
    report.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return {'status': 'Passed', 'cold_reopen': 'Passed', 'datasets': len(record['science'])}


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Cold-read a saved showcase project in Blender')
    parser.add_argument('--case', required=True, choices=('orbital', 'esp', 'igmh'))
    parser.add_argument('--project', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    print(json.dumps(reopen(args.case, os.getpid(), args.project, args.output_dir)))
