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
            path = module('data').filesystem_path(bpy.path.abspath(obj['qc_dataset']))
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


def render(path, transparent=True, resolution=(480, 360)):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = transparent
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
    filesystem_path = module('data').filesystem_path
    shutil.copytree(filesystem_path(out / 'evidence.qcdata'), filesystem_path(moved / 'evidence.qcdata'), dirs_exist_ok=True)
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
    sys.path.insert(0, str(ROOT))
    from tools.prepare_sop_fixture import real_fields as rebuild
    views = rebuild()
    for obj in views.values():
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


def check_copy(out):
    copied_report = check_binding(out)
    source = bpy.data.objects['VMD density surface']
    esp = bpy.data.objects['VMD ESP source']
    layers, copying = module('blender.layers'), module('blender.copy_display')
    first, second = [layers.copy_layer(source, bpy.context.collection) for _ in range(2)]
    first.name, second.name = 'VMD copy target A', 'VMD copy target B'
    first.location.x, second.location.x = 4, -4
    first.hide_render = second.hide_render = True
    sm, names = controls(source)
    sm[names['Isovalue']] = .008
    sm[names['Style (0 solid, 1 wire, 2 points)']] = 1
    sm[names['Wire Radius']] = .025
    module('blender.color_ranges').apply_range(source, (-.08, 0, .08))
    fm, fn = controls(first)
    fm.node_group.name = 'User renamed standard QC graph'
    fm[fn['Legend Position']] = (8., 9., 10.)
    fm[fn['Plane Origin']] = (.2, .3, .4)
    # Both target maps share the source material before the copy.
    source_mat = copying._state(source)['materials']['scalar_map'][0]
    for target in (first, second):
        for ref_kind, owner, key in copying._state(target)['materials']['scalar_map'][1]:
            assert ref_kind == 'node'
            owner.default_value = source_mat
    bpy.context.view_layer.update()
    before = {obj.name: (obj['qc_field'], obj['qc_color_source'], [list(row) for row in obj.matrix_world])
              for obj in (first, second)}
    activate(source)
    first.select_set(True)
    second.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    clones = [copying._state(obj)['materials']['scalar_map'][0] for obj in (first, second)]
    assert len({source_mat.as_pointer(), *(mat.as_pointer() for mat in clones)}) == 3
    for obj in (first, second):
        modifier, keys = controls(obj)
        assert modifier[keys['Isovalue']] == sm[names['Isovalue']]
        assert modifier[keys['Style (0 solid, 1 wire, 2 points)']] == 1
        assert (obj['qc_field'], obj['qc_color_source'], [list(row) for row in obj.matrix_world]) == before[obj.name]
    np.testing.assert_allclose(fm[fn['Legend Position']], (8, 9, 10))
    np.testing.assert_allclose(fm[fn['Plane Origin']], (.2, .3, .4))
    ramps = [next(n.color_ramp for n in mat.node_tree.nodes if n.get('qc_role') == 'color_ramp')
             for mat in (source_mat, *clones)]
    original_colors = [list(ramp.elements[0].color) for ramp in ramps]
    ramps[1].elements[0].color = (.2, .8, .1, 1)
    assert list(ramps[0].elements[0].color) == original_colors[0]
    assert list(ramps[2].elements[0].color) == original_colors[2]
    # A later incompatible target must prevent writes to an earlier compatible one.
    module('blender.scalars').add_mapping(esp, esp, -.05, .05)
    first_before = display_state(first)
    activate(source)
    first.select_set(True)
    esp.select_set(True)
    expect_error(lambda: bpy.ops.qcblender.copy_display_parameters(), 'quantity or unit')
    assert display_state(first) == first_before
    esp_before = json.loads(esp['qc_field'])
    assert bpy.ops.qcblender.copy_display_parameters(geometry=False, numerical=False) == {'FINISHED'}
    assert json.loads(esp['qc_field']) == esp_before
    assert bpy.ops.qcblender.copy_display_parameters(appearance=False, numerical=False) == {'FINISHED'}
    # A changed public interface is rejected before updating any target.
    extra = module('blender.views').socket(fm.node_group, 'Custom control', 'NodeSocketFloat', default=1)
    module('blender.graph').tag_view(fm.node_group)
    activate(source)
    second.select_set(True)
    first.select_set(True)
    second_before = display_state(second)
    expect_error(lambda: bpy.ops.qcblender.copy_display_parameters(), 'Unsupported QC graph input')
    assert display_state(second) == second_before
    fm.node_group.interface.remove(extra)
    module('blender.graph').tag_view(fm.node_group)
    # Fog transfers preserve target clipping, even though controls live in a material.
    fog = module('blender.fog').fog_view(source)
    fog.hide_render = True
    fog_target = layers.copy_layer(fog, bpy.context.collection)
    source_mat = copying._state(fog)['materials']['Material'][0]
    target_mat = copying._state(fog_target)['materials']['Material'][0]
    assert fog.material_slots[0].material == source_mat
    assert fog_target.material_slots[0].material == target_mat and target_mat != source_mat
    unrelated = bpy.data.materials.new('Fog unrelated slot')
    fog_target.data.materials.append(unrelated)
    source_nodes = copying._material_nodes(source_mat)
    target_nodes = copying._material_nodes(target_mat)
    source_nodes['Opacity Scale'].outputs[0].default_value = 31
    target_nodes['Plane Enabled'].outputs[0].default_value = 1
    target_nodes['Plane Origin'].inputs[0].default_value = 2
    activate(fog)
    fog_target.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    copied_mat = copying._state(fog_target)['materials']['Material'][0]
    assert fog_target.material_slots[0].material == copied_mat
    assert fog_target.material_slots[1].material == unrelated
    assert copied_mat != target_mat and copied_mat != source_mat
    target_nodes = copying._material_nodes(copied_mat)
    assert target_nodes['Opacity Scale'].outputs[0].default_value == 31
    assert target_nodes['Plane Enabled'].outputs[0].default_value == 1
    assert target_nodes['Plane Origin'].inputs[0].default_value == 2
    fog_target.data.materials.clear()
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    assert len(fog_target.material_slots) == 0
    assert copying._state(fog_target)['materials']['Material'][0] != source_mat
    # Atomic selection is local to the target, including legacy saved charge views.
    atoms = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'atoms')
    activate(atoms)
    module('blender.atomic_properties').charge_items(None, bpy.context)
    assert bpy.ops.qcblender.color_charge(method='mulliken', minimum=-.4, maximum=.4) == {'FINISHED'}
    am, an = controls(atoms)
    assert json.loads(am.node_group['qc_sockets']) == an
    atom_target = layers.copy_layer(atoms, bpy.context.collection)
    atom_target.hide_render = True
    tm, tn = controls(atom_target)
    tm[tn['First Atom (1-based)']] = 2
    tm[tn['Last Atom (0 = all)']] = 4
    tm[tn['Legend Position']] = (5., 6., 7.)
    legacy_keys = {name: key for name, key in tn.items()
                   if name not in (*copying.CHARGE_RANGE, 'Show Legend', 'Legend Position')}
    tm.node_group['qc_sockets'] = json.dumps(legacy_keys)
    am[an['Atom Radius']] = .32
    activate(atoms)
    atom_target.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    assert tm[tn['Atom Radius']] == am[an['Atom Radius']]
    assert tm[tn['First Atom (1-based)']] == 2 and tm[tn['Last Atom (0 = all)']] == 4
    np.testing.assert_allclose(tm[tn['Legend Position']], (5, 6, 7))
    assert copying._state(atoms)['materials']['charge_map'][0] != copying._state(atom_target)['materials']['charge_map'][0]
    atom_before = display_state(atoms)
    expect_error(lambda: module('blender.scalars').add_mapping(atoms, esp, -.05, .05), 'atomic charge')
    assert display_state(atoms) == atom_before
    # Slice dimensions transfer without moving the target plane.
    sliced = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'slice')
    slice_target = layers.copy_layer(sliced, bpy.context.collection)
    slice_target.hide_render = True
    slm, sln = controls(sliced)
    stm, stn = controls(slice_target)
    slm[sln['Width']], slm[sln['Height']], slm[sln['Resolution']] = 7., 8., 31
    stm[stn['Center']] = (1., 2., 3.)
    activate(sliced)
    slice_target.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    assert stm[stn['Width']] == 7 and stm[stn['Height']] == 8 and stm[stn['Resolution']] == 31
    np.testing.assert_allclose(stm[stn['Center']], (1, 2, 3))
    assert hashes() == copied_report['arrays']
    activate(source)
    source.hide_render = False
    report = {key: value for key, value in copied_report.items() if key not in ('objects', 'arrays')}
    report.update(copy_groups='Passed', independent_materials='Passed', target_identity_and_layout='Passed',
                  all_target_preflight='Passed', appearance_geometry_cross_quantity='Passed',
                  renamed_graph='Passed', custom_graph_rejection='Passed', fog_clip_preserved='Passed',
                  charge_and_legacy_copy='Passed', atom_selection_preserved='Passed', slice_plane_preserved='Passed')
    report['render_pixels'] = render(out / 'evidence.png')
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
    scene = bpy.context.scene
    report[key + '_pixels'] = render(out / (key + '.png'), transparent=scene.render.film_transparent,
                                    resolution=(scene.render.resolution_x, scene.render.resolution_y))
    report[key] = 'Passed'
    report['status'] = ('Passed' if report['cold_open'] == report['moved_cold_open'] == 'Passed' else 'Not Run')
    (out / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return {key: 'Passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', choices=['panel', 'binding', 'copy', 'reopen'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.preferences.addon_enable(module=MODULE)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    result = {'panel': check_panel, 'binding': check_binding, 'copy': check_copy, 'reopen': check_reopen}[args.check](args.out)
    print(json.dumps(result, ensure_ascii=False))
