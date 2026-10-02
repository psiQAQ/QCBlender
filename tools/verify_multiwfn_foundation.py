"""Installed first-batch acceptance checks for Multiwfn controls and node assets.

Run in an isolated Blender 5.1.1 profile with the candidate extension installed:

  blender --background --python tools/verify_multiwfn_foundation.py -- \
    --case core \
    --output-dir outputs/multiwfn-foundation/core

Repeat with --case nbo and --case analysis using separate output directories.
Scenes rebuild from verified inputs; --fixture-blend accepts an existing scene.
The optional --case gui runs in an isolated visible Blender session with a real
View3D and Properties area. Computer Use still signs off visual placement.
"""
import argparse
import ast
import csv
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import sys
import textwrap

import bpy


MODULE = 'bl_ext.user_default.qcblender'
ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {
    'generate': 'generate_field', 'charge': 'color_charge', 'dipole': 'show_dipole',
    'declare': 'declare_field', 'slice': 'create_slice', 'fog': 'create_fog',
    'surface': 'add_surface_layer', 'probe': 'probe_field', 'clip': 'add_clipping',
    'profile_start': 'mark_profile_start', 'profile': 'create_line_profile',
    'paired': 'import_paired_field', 'nbo': 'import_nbo',
    'esp': 'import_esp_analysis', 'aim': 'import_aim_analysis',
    'nocv_table': 'import_ets_nocv', 'nocv_field': 'import_nocv_field',
}
KINDS = ('atoms', 'field', 'slice', 'fog', 'nbo', 'analysis')
N_PANELS = ('main', 'dataset', 'create', 'external_import', 'project')
N_PANEL_EDIT_ACTIONS = {'qcblender.declare_field', 'qcblender.associate_sources',
                        'qcblender.copy_display_parameters', 'qcblender.select_color_field'}
OBJECT_PANELS = ('object', 'scientific', 'geometry', 'mapping', 'legend',
                 'spatial', 'advanced', 'selection')


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def activate(obj):
    for selected in bpy.context.selected_objects:
        selected.select_set(False)
    bpy.context.view_layer.objects.active = obj
    if obj is not None:
        obj.select_set(True)


def check_panels(report):
    for name in N_PANELS:
        cls = getattr(bpy.types, 'QCBLENDER_PT_' + name)
        assert cls.bl_space_type == 'VIEW_3D' and cls.bl_region_type == 'UI', name
        source = ast.parse(textwrap.dedent(inspect.getsource(cls.draw)))
        assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                       and node.func.attr in ('prop', 'template_list') for node in ast.walk(source)), name
        assert not any(operator in inspect.getsource(cls.draw) for operator in N_PANEL_EDIT_ACTIONS), name
    for name in OBJECT_PANELS:
        cls = getattr(bpy.types, 'QCBLENDER_PT_' + name)
        assert cls.bl_space_type == 'PROPERTIES' and cls.bl_context == 'object', name
    material = bpy.types.QCBLENDER_PT_material
    assert material.bl_space_type == 'PROPERTIES' and material.bl_context == 'material'
    report['registered_panel_placement'] = 'Passed'
    report['n_panel_direct_property_controls'] = 'Passed'
    report['n_panel_visual_actions'] = 'Not Run: Computer Use must inspect visible actions'


def check_capabilities(report, objects):
    capability = module('blender.capabilities').capability
    browser = module('blender.source_browser')
    matrix = {}
    ordinary = bpy.data.objects.new('Foundation ordinary object', bpy.data.meshes.new('Foundation ordinary mesh'))
    bpy.context.collection.objects.link(ordinary)
    cases = {'none': None, 'ordinary': ordinary, **objects}
    report['capability_matrix'] = matrix
    mismatches = []
    try:
        for label, obj in cases.items():
            activate(obj)
            if obj is not None and obj.get('qc_dataset'):
                browser.refresh_source(obj)
            matrix[label] = {}
            for action, operator in ACTIONS.items():
                applicable, enabled, reason = capability(bpy.context, action)
                polled = bool(getattr(bpy.ops.qcblender, operator).poll())
                matrix[label][action] = {'applicable': applicable, 'enabled': enabled,
                                         'poll': polled, 'reason': reason}
                if polled != enabled:
                    mismatches.append((label, action, matrix[label][action]))
            if label in ('none', 'ordinary'):
                assert not any(row['applicable'] for row in matrix[label].values())
            if label == 'atoms':
                assert not matrix[label]['slice']['applicable']
            if label in ('field', 'slice'):
                assert matrix[label]['profile_start']['enabled']
            if label == 'fog':
                assert not matrix[label]['profile_start']['applicable']
            if label in ('nbo', 'analysis'):
                assert matrix[label]['nbo']['applicable']
    finally:
        mesh = ordinary.data
        bpy.data.objects.remove(ordinary, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    assert not mismatches, mismatches
    report['capability_operator_poll'] = 'Passed'


def check_broken_source(report, field):
    broken = field.copy()
    broken.data = field.data.copy()
    bpy.context.collection.objects.link(broken)
    broken['qc_dataset_sha256'] = '0' * 64
    browser = module('blender.source_browser')
    try:
        activate(broken)
        cached = browser.refresh_source(broken)
        assert 'error' in cached, cached
        count = len(bpy.context.scene.objects)
        applicable, enabled, reason = module('blender.capabilities').capability(bpy.context, 'slice')
        assert applicable and not enabled and reason
        assert not bpy.ops.qcblender.create_slice.poll()
        assert len(bpy.context.scene.objects) == count
        report['broken_source'] = {'status': 'Passed', 'reason': reason}
    finally:
        activate(None)
        mesh = broken.data
        bpy.data.objects.remove(broken, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def check_unknown_cube(report, output_dir):
    source = output_dir / 'unknown.cube'
    source.write_text('Scalar quantity unspecified\nSynthetic declaration test\n1 0 0 0\n'
                      '-2 1 0 0\n-2 0 1 0\n-2 0 0 1\n1 1 0 0 0\n1 2 3 4 5 6 7 8\n', encoding='ascii')
    data = module('cube').read_cube(source)
    assert data.metadata['fields'][0]['quantity'] == 'unknown_scalar'
    directory = output_dir / 'unknown-cube-dataset'
    directory.mkdir(parents=True, exist_ok=True)
    cache = directory / 'field.vdb'
    module('worker').write_volume(data, cache)
    data.metadata['fields'][0]['vdb_sha256'] = hashlib.sha256(cache.read_bytes()).hexdigest()
    module('data').save_dataset(data, directory)
    obj = module('blender.views').field_view(directory)
    activate(obj)
    module('blender.source_browser').refresh_source(obj)
    relevant, enabled, _ = module('blender.capabilities').capability(bpy.context, 'declare')
    assert relevant and enabled and bpy.ops.qcblender.declare_field.poll()
    count = len(bpy.context.scene.objects)
    assert not bpy.ops.qcblender.generate_field.poll()
    assert len(bpy.context.scene.objects) == count
    report['real_unknown_cube'] = {'status': 'Passed', 'source': str(source)}


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def check_data_records(report, output_dir):
    storage = module('data')
    exporter = module('data_export')
    results = []
    seen = set()
    for obj in bpy.context.scene.objects:
        if not obj.get('qc_data_record'):
            continue
        assert obj.type == 'MESH' and len(obj.data.vertices) == 0 and not obj.modifiers
        source = Path(bpy.path.abspath(obj['qc_dataset']))
        data = storage.load_dataset(source)
        digest = hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest()
        assert digest == obj['qc_dataset_sha256']
        for kind in exporter.available_exports(data):
            if (digest, kind) in seen:
                continue
            seen.add((digest, kind))
            exported = exporter.export_dataset(source, output_dir / 'data-exports', kind)
            destination = Path(exported['directory'])
            metadata = json.loads((destination / 'metadata.json').read_text(encoding='utf-8'))
            assert metadata['source'] == data.metadata['source']
            assert metadata['dataset_manifest_sha256'] == digest
            assert metadata['scientific_metadata'] == data.metadata
            for record in exported['files']:
                path = destination / record['filename']
                assert file_sha256(path) == record['sha256']
                with path.open(encoding='utf-8', newline='') as stream:
                    assert sum(1 for _ in csv.DictReader(stream)) == record['row_count']
            results.append({'object': obj.name, 'kind': kind, 'directory': str(destination)})
    report['data_record_exports'] = ({'status': 'Passed', 'exports': results} if results else
        {'status': 'Not Run', 'reason': 'This fixture contains no bound data record carriers'})


def check_materials(report, objects):
    elements = bpy.data.materials.get('QC Elements')
    assert elements and elements.use_nodes
    shader = module('blender.views').node_by_type(elements.node_tree.nodes, 'ShaderNodeBsdfPrincipled')
    output = module('blender.views').node_by_type(elements.node_tree.nodes, 'ShaderNodeOutputMaterial')
    assert shader and output and output.inputs['Surface'].is_linked
    field = objects['field']
    modifier = module('blender.graph').view_modifier(field)
    mats = [modifier.get(item.identifier) or item.default_value
            for item in modifier.node_group.interface.items_tree
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT'
            and item.socket_type == 'NodeSocketMaterial']
    mats = [mat for mat in mats if mat]
    assert mats
    assert all(mat.use_nodes and module('blender.views').node_by_type(mat.node_tree.nodes,
               'ShaderNodeOutputMaterial') for mat in mats)
    report['default_material_nodes'] = 'Passed'


def check_parameter_sections(report, objects):
    ui = module('blender.ui')
    browser = module('blender.source_browser')
    data = module('data')
    original_load, original_read = data.load_dataset, browser.read_metadata
    try:
        def forbidden(*_args, **_kwargs):
            raise AssertionError('Parameter visibility read a scientific dataset or manifest')
        data.load_dataset = forbidden
        browser.read_metadata = forbidden
        for obj in objects.values():
            if obj.get('qc_view_kind') in ('atoms', 'field', 'slice', 'fog'):
                for section in module('blender.parameters').GROUPS:
                    assert isinstance(ui.parameter_section_available(obj, section), bool)
        field = objects['field']
        assert ui.parameter_section_available(field, '几何表示')
        assert ui.parameter_section_available(field, '材质')
        activate(field)
        assert bpy.types.QCBLENDER_PT_geometry.poll(bpy.context)
        assert bpy.types.QCBLENDER_PT_material.poll(bpy.context)
        mapped = next(obj for obj in bpy.context.scene.objects if obj.get('qc_color_source'))
        _, _, _, _, _, materials = ui.view_parameter_state(mapped)
        roles = [node for mat in materials if mat and mat.use_nodes
                 for node in mat.node_tree.nodes if node.get('qc_role') in ('color_ramp', 'color_invert')]
        assert roles and all(ui._material_section(node) == '材质' for node in roles)
    finally:
        data.load_dataset, browser.read_metadata = original_load, original_read
    report['node_only_parameter_visibility'] = 'Passed'
    report['color_ramp_in_material_properties'] = 'Passed'


def check_assets(report):
    catalog = module('asset_catalog')
    library = module('blender.asset_library')
    assert len(catalog.ASSETS) == 9
    assert library.LIBRARY_FILE.is_file()
    catalog_file = library.LIBRARY_DIR / 'blender_assets.cats.txt'
    assert catalog_file.read_text(encoding='utf-8') == catalog.catalog_text()
    assert any(Path(row.path).resolve() == library.LIBRARY_DIR.resolve()
               for row in bpy.context.preferences.filepaths.asset_libraries)
    with bpy.data.libraries.load(str(library.LIBRARY_FILE), link=False) as (source, target):
        names = list(source.node_groups)
        assert len(names) == 9 and not source.objects and not source.volumes
        target.node_groups = names
    groups = [group for group in target.node_groups if group is not None]
    try:
        assert {group.get('qc_asset_id') for group in groups} == set(catalog.ASSETS)
        assert all(group.asset_data and str(group.asset_data.catalog_id) ==
                   catalog.catalog_id(catalog.ASSETS[group['qc_asset_id']][0]) for group in groups)
    finally:
        for group in reversed(groups):
            bpy.data.node_groups.remove(group, do_unlink=True)
    report['nine_packaged_assets'] = 'Passed'


def check_legacy_assets(report):
    library = module('blender.asset_library')
    with bpy.data.libraries.load(str(library.LIBRARY_FILE), link=False) as (source, target):
        target.node_groups = [next(name for name in source.node_groups if 'Slice' in name)]
    standard = target.node_groups[0]
    custom = standard.copy()
    try:
        for group in (standard, custom):
            if group.asset_data is None:
                group.asset_mark()
            group.asset_data.catalog_id = '00000000-0000-0000-0000-000000000000'
            group.asset_data.description = library._legacy_description(group['qc_asset_id'], group)
        custom['qc_custom_probe'] = 'preserve'
        signatures = {group.name: library._group_signature(group) for group in (standard, custom)}
        preview = library.preview_legacy_assets()
        assert (standard.name, 'standard; clear asset mark') in preview, preview
        assert (custom.name, 'custom or modified; skipped') in preview, preview
        count = len(bpy.context.scene.objects)
        assert bpy.ops.qcblender.cleanup_legacy_node_assets(preview=json.dumps(preview)) == {'FINISHED'}
        assert len(bpy.context.scene.objects) == count
        assert standard.asset_data is None and custom.asset_data is not None
        assert all(library._group_signature(group) == signatures[group.name] for group in (standard, custom))
        try:
            rejected = bpy.ops.qcblender.cleanup_legacy_node_assets(preview=json.dumps(preview))
        except RuntimeError as error:
            assert 'changed since preview' in str(error)
        else:
            assert rejected == {'CANCELLED'}
        assert len(bpy.context.scene.objects) == count
        report['legacy_asset_preview_cleanup'] = 'Passed'
    finally:
        for group in (custom, standard):
            bpy.data.node_groups.remove(group, do_unlink=True)


def check_socket_identity(report, field):
    tree = field.modifiers[0].node_group.copy()
    try:
        before = {item.name: item.identifier for item in tree.interface.items_tree
                  if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
        links = [(link.from_node.name, link.from_socket.identifier,
                  link.to_node.name, link.to_socket.identifier) for link in tree.links]
        names = [name for name in ('Isovalue', 'Positive Phase', 'Negative Phase') if name in before]
        assert len(names) == 3
        module('blender.views').group_sockets(tree, (('Foundation verification', names),))
        after = {item.name: item.identifier for item in tree.interface.items_tree
                 if item.item_type == 'SOCKET' and item.in_out == 'INPUT'}
        assert before == after
        assert links == [(link.from_node.name, link.from_socket.identifier,
                          link.to_node.name, link.to_socket.identifier) for link in tree.links]
        report['socket_identity_after_reordering'] = 'Passed'
    finally:
        bpy.data.node_groups.remove(tree, do_unlink=True)


def check_properties_pin(report, field):
    if bpy.app.background:
        report['properties_pin_real_area'] = 'Not Run: Properties context needs a visible redraw'
        return
    screen = bpy.context.screen
    view = next((area for area in screen.areas if area.type == 'VIEW_3D'), None)
    props = next((area for area in screen.areas if area.type == 'PROPERTIES'), None)
    if view is None or props is None:
        report['properties_pin_real_area'] = 'Not Run: real View3D and Properties areas required'
        return
    previous_pin = props.spaces.active.pin_id
    previous_context = props.spaces.active.context
    previous_use_pin = props.spaces.active.use_pin_id
    try:
        activate(field)
        window = next(region for region in view.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=view, region=window):
            assert bpy.ops.qcblender.open_properties(editor='OBJECT') == {'FINISHED'}
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        assert props.spaces.active.pin_id == field and props.spaces.active.context == 'OBJECT'
        other = next(obj for obj in bpy.context.scene.objects if obj != field and obj.type == 'MESH')
        activate(other)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        props_window = next(region for region in props.regions if region.type == 'WINDOW')
        with bpy.context.temp_override(area=props, region=props_window):
            assert bpy.context.object == field, 'Properties panel did not retain its pinned object'
        report['properties_pin_real_area'] = 'Passed'
    finally:
        props.spaces.active.pin_id = previous_pin
        props.spaces.active.context = previous_context
        props.spaces.active.use_pin_id = previous_use_pin


def check_gui_draw(report, objects):
    assert not bpy.app.background, 'GUI draw check requires visible Blender'
    area = next((area for area in bpy.context.screen.areas if area.type == 'VIEW_3D'), None)
    props = next((area for area in bpy.context.screen.areas if area.type == 'PROPERTIES'), None)
    assert area is not None and props is not None, 'Real View3D and Properties areas required'
    field = objects['field']
    activate(field)
    browser = module('blender.source_browser')
    browser.refresh_source(field)
    data_module = module('data')
    original_load, original_read = data_module.load_dataset, browser.read_metadata
    draws = []
    forbidden_calls = []
    draw_codes = {getattr(bpy.types, 'QCBLENDER_PT_' + name).draw.__code__: name
                  for name in (*N_PANELS, *OBJECT_PANELS)}
    previous_profile = sys.getprofile()
    def observed(frame, event, arg):
        if event == 'call' and frame.f_code in draw_codes:
            draws.append(draw_codes[frame.f_code])
    previous_pin, previous_context = props.spaces.active.pin_id, props.spaces.active.context
    try:
        props.spaces.active.pin_id = field
        props.spaces.active.context = 'OBJECT'
        def forbidden(*_args, **_kwargs):
            forbidden_calls.append('scientific dataset or manifest read')
            raise AssertionError('UI draw accessed a scientific dataset or manifest')
        data_module.load_dataset = forbidden
        browser.read_metadata = forbidden
        sys.setprofile(observed)
        area.tag_redraw()
        props.tag_redraw()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
    finally:
        sys.setprofile(previous_profile)
        data_module.load_dataset, browser.read_metadata = original_load, original_read
        props.spaces.active.pin_id, props.spaces.active.context = previous_pin, previous_context
    assert not forbidden_calls, forbidden_calls
    assert any(name in N_PANELS for name in draws), 'No QC N-panel was drawn in the real View3D'
    assert any(name in OBJECT_PANELS for name in draws), 'No QC Object Properties panel was drawn'
    report['gui_draw_uses_cached_metadata'] = {'status': 'Passed', 'drawn_panels': sorted(set(draws))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=('core', 'nbo', 'analysis', 'gui'), required=True)
    parser.add_argument('--fixture-blend', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to((ROOT / 'outputs').resolve()), 'Use an isolated Blender profile under outputs/'
    assert bpy.ops.preferences.addon_enable(module=MODULE) == {'FINISHED'}
    if args.fixture_blend:
        assert args.case != 'gui', 'Open the isolated GUI fixture before --case gui'
        source = args.fixture_blend.resolve(strict=True)
        assert bpy.ops.wm.open_mainfile(filepath=str(source)) == {'FINISHED'}
    elif args.case != 'gui':
        sys.path.insert(0, str(ROOT))
        from tools.prepare_sop_fixture import prepare as rebuild
        rebuild({'core': 'C04', 'nbo': 'NBO', 'analysis': 'C09'}[args.case])
        if args.case == 'core':
            field = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'field')
            activate(field)
            assert bpy.ops.qcblender.create_slice(resolution=21) == {'FINISHED'}
            activate(field)
            module('blender.fog').fog_view(field)
    installed = Path(module('blender.editor_ui').__file__).resolve()
    assert 'extensions' in installed.parts and installed != ROOT / 'qcblender/blender/editor_ui.py'
    report = {'case': args.case, 'candidate_module': str(installed),
              'fixture_blend': str(args.fixture_blend.resolve()) if args.fixture_blend else None,
              'gui_visual_inspection': 'Not Run: Computer Use'}
    target = output_dir / (args.case + '.json')
    failures = {}
    def run(label, function, *arguments):
        try:
            function(report, *arguments)
        except Exception as error:
            failures[label] = repr(error)
    try:
        run('panels', check_panels)
        run('data_records', check_data_records, output_dir)
        required = {'core': ('atoms', 'field', 'slice', 'fog'), 'nbo': ('nbo',),
                    'analysis': ('analysis',), 'gui': ('field',)}[args.case]
        objects = {kind: next(obj for obj in bpy.context.scene.objects
                              if obj.get('qc_view_kind') == kind) for kind in required}
        if args.case == 'core':
            run('capabilities', check_capabilities, objects)
            run('broken_source', check_broken_source, objects['field'])
            run('unknown_cube', check_unknown_cube, output_dir)
            run('materials', check_materials, objects)
            run('parameter_sections', check_parameter_sections, objects)
            run('assets', check_assets)
            run('legacy_assets', check_legacy_assets)
            run('socket_identity', check_socket_identity, objects['field'])
            run('properties_pin', check_properties_pin, objects['field'])
        elif args.case == 'gui':
            run('gui_draw', check_gui_draw, objects)
            run('properties_pin', check_properties_pin, objects['field'])
        else:
            run('capabilities', check_capabilities, objects)
        report['status'] = 'Failed' if failures else 'Passed'
        if failures:
            report['failures'] = failures
            raise AssertionError(failures)
    except Exception as error:
        report['status'] = 'Failed'
        report['error'] = repr(error)
        raise
    finally:
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
