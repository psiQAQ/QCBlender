"""Checks of the installed VMD interaction candidate in an isolated Blender process."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys

import bpy
import numpy as np

MODULE = 'bl_ext.user_default.qcblender'


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def controls(obj):
    modifier = module('blender.graph').view_modifier(obj)
    return modifier, {s.name: s.identifier for s in modifier.node_group.interface.items_tree
                      if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}


def activate(obj):
    module('blender.layers').activate(bpy.context, obj)


def mesh_count(obj):
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return [len(mesh.vertices), len(mesh.polygons)]
    finally:
        evaluated.to_mesh_clear()


def hashes():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.get('qc_dataset'):
            path = Path(bpy.path.abspath(obj['qc_dataset']))
            raw = (path / 'manifest.json').read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            assert digest == obj['qc_dataset_sha256']
            module('data').load_dataset(path)
            result[digest] = {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(path.rglob('*')) if p.is_file()}
    return result


def render(path):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.render.resolution_x = 480
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    pixels = np.array(image.pixels[:]).reshape(-1, 4)
    bpy.data.images.remove(image)
    visible = int((pixels[:, 3] > .01).sum())
    assert visible > 100, path
    return visible


def save_evidence(out, report):
    report['arrays'] = hashes()
    report['objects'] = {obj.name: {'kind': obj.get('qc_view_kind'),
        'source': obj.get('qc_source_sha256'), 'field': obj.get('qc_field'),
        'color': obj.get('qc_color_source'), 'counts': mesh_count(obj)}
        for obj in bpy.context.scene.objects if obj.get('qc_view_kind') in ('atoms', 'field', 'slice')}
    module('blender.project').save_project(out / 'evidence.blend')
    moved = out / 'moved 中文 path'
    moved.mkdir(exist_ok=True)
    shutil.copy2(out / 'evidence.blend', moved / 'evidence.blend')
    shutil.copytree(out / 'evidence.qcdata', moved / 'evidence.qcdata', dirs_exist_ok=True)
    report['cold_open'] = 'Not Run'
    report['moved_cold_open'] = 'Not Run'
    report['status'] = 'Passed'
    (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


def check_panel(out):
    out.mkdir(parents=True, exist_ok=True)
    before = hashes()
    report = {'styles': {}}
    surface = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'field')
    for obj in [surface, next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'atoms')]:
        activate(obj)
        modifier, names = controls(obj)
        name = next(name for name in names if name.startswith('Style ('))
        initial = modifier[names[name]]
        counts = []
        for style in range(3):
            assert bpy.ops.qcblender.set_view_style(socket_id=names[name], style=style) == {'FINISHED'}
            counts.append(mesh_count(obj))
            if obj == surface:
                report['styles'][str(style)] = render(out / f'style-{style}.png')
        assert len({tuple(count) for count in counts}) == 3, counts
        modifier[names[name]] = initial
        obj.update_tag()
        report[obj['qc_view_kind'] + '_counts'] = counts
    assert hashes() == before
    activate(surface)
    report['final_render'] = render(out / 'evidence.png')
    save_evidence(out, report)
    return report


def check_reopen(out):
    report = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
    assert hashes() == report['arrays']
    for name, expected in report['objects'].items():
        obj = bpy.context.scene.objects[name]
        assert obj.get('qc_source_sha256') == expected['source']
        assert obj.get('qc_field') == expected['field']
        assert obj.get('qc_color_source') == expected['color']
        assert mesh_count(obj) == expected['counts']
        assert Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(Path(bpy.data.filepath).parent)
    moved = 'moved 中文 path' in bpy.data.filepath
    key = 'moved_cold_open' if moved else 'cold_open'
    report[key + '_pixels'] = render(out / (key + '.png'))
    report[key] = 'Passed'
    (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return {key: 'Passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', choices=['panel', 'reopen'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.preferences.addon_enable(module=MODULE)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    result = check_panel(args.out) if args.check == 'panel' else check_reopen(args.out)
    print(json.dumps(result, ensure_ascii=False))
