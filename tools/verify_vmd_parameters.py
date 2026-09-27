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
ROOT = Path(__file__).resolve().parents[1]


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


def display_state(obj):
    modifier, names = controls(obj)
    inputs, materials = {}, set()
    for item in modifier.node_group.interface.items_tree:
        if item.item_type != 'SOCKET' or item.in_out != 'INPUT' or not hasattr(item, 'default_value'):
            continue
        value = modifier.get(item.identifier, item.default_value)
        if isinstance(value, bpy.types.Material):
            materials.add(value)
            inputs[item.name] = {'material': value.name}
        elif isinstance(value, (str, bool, float, int)) or value is None:
            inputs[item.name] = value
        elif hasattr(value, 'to_list'):
            inputs[item.name] = value.to_list()
        elif hasattr(value, '__iter__'):
            inputs[item.name] = list(value)
    for node in modifier.node_group.nodes:
        for socket in node.inputs:
            if socket.type == 'MATERIAL' and not socket.is_linked and socket.default_value:
                materials.add(socket.default_value)
    material_states = {}
    for mat in materials:
        state = {}
        for node in mat.node_tree.nodes if mat.use_nodes else ():
            role = node.get('qc_role') or node.get('qc_control')
            if role and node.bl_idname == 'ShaderNodeValToRGB':
                ramp = node.color_ramp
                state[role] = [ramp.interpolation, ramp.color_mode, ramp.hue_interpolation,
                               [(e.position, list(e.color)) for e in ramp.elements]]
            elif role and node.bl_idname == 'ShaderNodeValue':
                state[role] = node.outputs[0].default_value
            elif role and node.bl_idname == 'ShaderNodeCombineXYZ':
                state[role] = [s.default_value for s in node.inputs]
            elif node.bl_idname == 'ShaderNodeBsdfPrincipled':
                state[node.name] = {name: list(node.inputs[name].default_value)
                    if name == 'Base Color' else node.inputs[name].default_value
                    for name in ('Base Color', 'Alpha', 'Roughness') if not node.inputs[name].is_linked}
        material_states[mat.name] = state
    return json.loads(json.dumps({'inputs': inputs, 'materials': material_states,
                                  'transform': [list(row) for row in obj.matrix_world]}))


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
        'color': obj.get('qc_color_source'), 'display': display_state(obj),
        'counts': mesh_count(obj) if obj.get('qc_view_kind') != 'fog' else None}
        for obj in bpy.context.scene.objects if obj.get('qc_view_kind') in ('atoms', 'field', 'slice', 'fog')}
    module('blender.project').save_project(out / 'evidence.blend')
    moved = out / 'moved 中文 path'
    moved.mkdir(exist_ok=True)
    shutil.copy2(out / 'evidence.blend', moved / 'evidence.blend')
    shutil.copytree(out / 'evidence.qcdata', moved / 'evidence.qcdata', dirs_exist_ok=True)
    report['cold_open'] = 'Not Run'
    report['moved_cold_open'] = 'Not Run'
    report['status'] = 'Not Run'
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


def real_fields(out):
    reference = ROOT / 'outputs/source-adoption/04-profile/final-sop/cases/C04/C04.qcdata/datasets'
    views = {}
    for path in sorted(reference.glob('*/manifest.json')):
        metadata = json.loads(path.read_text(encoding='utf-8'))['metadata']
        fields = metadata.get('fields', [])
        if not fields or fields[0]['quantity'] in views:
            continue
        directory = out / 'datasets' / path.parent.name
        shutil.copytree(path.parent, directory, dirs_exist_ok=True)
        obj = module('blender.views').field_view(directory)
        views[fields[0]['quantity']] = obj
        obj.hide_render = True
    return views


def expect_error(action, message):
    try:
        outcome = action()
    except (RuntimeError, ValueError) as error:
        assert message.lower() in str(error).lower(), str(error)
        return str(error)
    assert outcome == {'CANCELLED'}, outcome
    return 'CANCELLED'


def check_binding(out):
    out.mkdir(parents=True, exist_ok=True)
    for obj in bpy.context.scene.objects:
        if obj.type not in ('LIGHT', 'CAMERA'):
            obj.hide_render = True
    fields = real_fields(out)
    density, esp = fields['electron_number_density'], fields['electrostatic_potential']
    density.name, esp.name = 'VMD density surface', 'VMD ESP source'
    density.hide_render = False
    activate(density)
    modifier, names = controls(density)
    modifier[names['Isovalue']] = .004
    original = hashes()
    assert bpy.ops.qcblender.select_color_field(source_name=esp.name, minimum=-.05, maximum=.05) == {'FINISHED'}
    browser, scalars = module('blender.source_browser'), module('blender.scalars')
    info, title = browser.color_mapping(density)
    assert info.inputs['Object'].default_value == esp.qc_settings.volume
    assert 'ESP [hartree/e]' == title.inputs['String'].default_value
    modifier, names = controls(density)
    modifier[names['Legend Position']] = (2.7, -.4, .1)
    initial = tuple(modifier[names[name]] for name in ('Color Minimum', 'Color Center', 'Color Maximum'))
    assert bpy.ops.qcblender.select_color_field(source_name=density.name) == {'FINISHED'}
    assert browser.color_volume(density) == density.qc_settings.volume
    assert title.inputs['String'].default_value == 'Electron density [electron/bohr^3]'
    assert tuple(modifier[names[name]] for name in ('Color Minimum', 'Color Center', 'Color Maximum')) == initial
    np.testing.assert_allclose(modifier[names['Legend Position']], (2.7, -.4, .1))
    assert bpy.ops.qcblender.select_color_field(source_name=esp.name) == {'FINISHED'}
    module('blender.inspection').add_clip(density)
    assert browser.color_volume(density) == esp.qc_settings.volume
    assert bpy.ops.qcblender.select_color_field(source_name=esp.name) == {'FINISHED'}
    copied = module('blender.layers').copy_layer(density, bpy.context.collection)
    copied.hide_render = True
    assert browser.color_volume(copied) == esp.qc_settings.volume
    # Unknown extra mapping is rejected without changing the previous binding.
    record = density['qc_color_source']
    tree = modifier.node_group
    extra = tree.nodes.new('GeometryNodeGroup')
    extra.node_tree = module('blender.assets').color_group()
    count = len(tree.nodes)
    error = expect_error(lambda: bpy.ops.qcblender.select_color_field(source_name=density.name), 'ambiguous')
    assert density['qc_color_source'] == record and len(tree.nodes) == count
    assert info.inputs['Object'].default_value == esp.qc_settings.volume
    tree.nodes.remove(extra)
    # Original selection-based operator and a slice still use the same field binding.
    target = module('blender.views').field_view(Path(bpy.path.abspath(density['qc_dataset'])))
    target.hide_render = True
    activate(target)
    esp.select_set(True)
    module('blender.inspection').add_clip(target)
    assert bpy.ops.qcblender.map_scalar() == {'FINISHED'}
    assert browser.color_volume(target) == esp.qc_settings.volume
    activate(esp)
    assert bpy.ops.qcblender.create_slice(resolution=21) == {'FINISHED'}
    sliced = bpy.context.object
    sliced.hide_render = True
    assert browser.color_volume(sliced) == esp.qc_settings.volume
    assert hashes() == original
    activate(density)
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    region = next(region for region in area.regions if region.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        assert bpy.ops.qcblender.create_framed_camera() == {'FINISHED'}
    report = {'create_replace': 'Passed', 'range_and_legend_preserved': 'Passed',
              'legacy_selection_and_slice': 'Passed', 'clip_before_and_after': 'Passed',
              'custom_graph_rejected': error, 'arrays_unchanged': 'Passed',
              'render_pixels': render(out / 'evidence.png')}
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
        if expected['counts'] is not None:
            assert mesh_count(obj) == expected['counts']
        if 'display' in expected:
            assert display_state(obj) == expected['display'], name
        assert Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(Path(bpy.data.filepath).parent)
    moved = 'moved 中文 path' in bpy.data.filepath
    key = 'moved_cold_open' if moved else 'cold_open'
    report[key + '_pixels'] = render(out / (key + '.png'))
    report[key] = 'Passed'
    report['status'] = ('Passed' if report['cold_open'] == report['moved_cold_open'] == 'Passed' else 'Not Run')
    (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return {key: 'Passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', choices=['panel', 'binding', 'reopen'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.preferences.addon_enable(module=MODULE)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    result = {'panel': check_panel, 'binding': check_binding, 'reopen': check_reopen}[args.check](args.out)
    print(json.dumps(result, ensure_ascii=False))
