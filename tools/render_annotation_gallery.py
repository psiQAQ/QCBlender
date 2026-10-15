"""Render the installed annotation primitives and packed Chinese text on real input."""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

MODULE = 'bl_ext.user_default.qcblender'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reopen', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.output.mkdir(parents=True, exist_ok=True)
    bpy.ops.preferences.addon_enable(module=MODULE)
    scene = bpy.context.scene
    if not args.reopen:
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        views = importlib.import_module(MODULE + '.blender.views')
        layers = importlib.import_module(MODULE + '.blender.layers')
        camera_data = bpy.data.cameras.new('Annotation gallery camera')
        camera = bpy.data.objects.new('Annotation gallery camera', camera_data)
        scene.collection.objects.link(camera)
        camera.location = (0, 0, 20)
        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = 14
        scene.camera = camera
        cases = [('ATOM', '1', (-3.4, 2.6)), ('DISTANCE', '1,4', (3.4, 2.6)),
                 ('ANGLE', '3,1,2', (-3.4, -2.1)), ('DIHEDRAL', '3,1,2,4', (3.4, -2.1))]
        for kind, atoms, (x, y) in cases:
            owner = views.atom_view(args.dataset)
            data = importlib.import_module(MODULE + '.data').load_dataset(args.dataset)
            importlib.import_module(MODULE + '.blender.trajectory').initialize_trajectory(owner, data)
            owner.name = 'Gallery ' + kind
            owner.location = (x, y, 0)
            owner.rotation_euler.x = math.radians(65)
            bpy.context.view_layer.update()
            layers.activate(bpy.context, owner)
            options = dict(kind=kind, atoms=atoms, size=.65, measurement_width=.025,
                           line_width=.012, arc_radius=.65)
            if kind == 'DIHEDRAL':
                options.update(prefix_mode='CUSTOM', prefix='二面角：')
            assert bpy.ops.qcblender.add_annotation(**options) == {'FINISHED'}
            label = next(obj for obj in owner.children if obj.type == 'FONT')
            entry = json.loads(label['qc_annotation'])
            anchor = label.location - Vector(entry['offset'])
            offset = owner.matrix_world.inverted() @ Vector((x - 2.4, y - 1.75, .8)) - anchor
            edit = dict(annotation_id=entry['id'], **{key: entry[key] for key in
                ('size', 'decimals', 'show_leader', 'line_width', 'visible', 'prefix_mode', 'prefix',
                 'show_measurement', 'measurement_width', 'arc_radius', 'show_planes')})
            edit['offset'] = offset
            assert bpy.ops.qcblender.edit_annotation(**edit) == {'FINISHED'}
            assert bpy.ops.qcblender.face_annotations(annotation_id='') == {'FINISHED'}
        light_data = bpy.data.lights.new('Gallery softbox', 'AREA')
        light = bpy.data.objects.new('Gallery softbox', light_data)
        scene.collection.objects.link(light)
        light.location = (0, 0, 7)
        light_data.energy = 1400
        light_data.shape = 'DISK'
        light_data.size = 8
        scene.world.use_nodes = True
        background = next(node for node in scene.world.node_tree.nodes if node.type == 'BACKGROUND')
        background.inputs['Color'].default_value = (.8, .8, .8, 1)
        background.inputs['Strength'].default_value = .5
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 32
        scene.render.resolution_x = 1400
        scene.render.resolution_y = 1000
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.view_settings.view_transform = 'Standard'
        scene.render.filepath = str(args.output / 'annotation-gallery.png')
        assert bpy.ops.qcblender.save_project(filepath=str(args.output / '标注与中文.blend')) == {'FINISHED'}
    labels = [obj for obj in bpy.data.objects if obj.type == 'FONT' and obj.get('qc_annotation')]
    assert len(labels) == 4
    assert all(obj.data.font.packed_file is not None for obj in labels)
    assert any(obj.data.body.startswith('二面角：') for obj in labels)
    if args.reopen:
        scene.render.filepath = str(args.output / 'annotation-gallery-reopened.png')
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(scene.render.filepath, check_existing=False)
    assert tuple(image.size) == (1400, 1000)
    report = {'status': 'Passed', 'labels': [obj.data.body for obj in labels],
              'packed_fonts': [obj.data.font.name for obj in labels], 'render': scene.render.filepath,
              'project': bpy.data.filepath, 'reopen': args.reopen, 'visual_review': 'Not Run'}
    (args.output / ('render-reopen.json' if args.reopen else 'render.json')).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
