"""Run installed-package ColorRamp checks in an isolated Blender process.

blender --background --python tools/verify_color_presets.py -- \
    --module bl_ext.user_default.qcblender --field-dataset ABSOLUTE_QCDATA \
    --output ABSOLUTE_REPORT_JSON

The supplied field dataset must already contain a qualified VDB cache. The script
saves <report-stem>-scene.blend plus its self-contained .qcdata. Open that scene
for GUI apply/cancel/undo/redo checks. For a separate cold or relocated reopen:
blender SCENE --background --python tools/verify_color_presets.py -- \
    --module bl_ext.user_default.qcblender --reopen-check --output NEW_REPORT_JSON

Headless preflight and fault-injection checks do not claim GUI acceptance.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback


def digest_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(args, report):
    import bpy
    import numpy as np

    bpy.ops.preferences.addon_enable(module=args.module)
    module = lambda name: importlib.import_module(args.module + '.' + name)
    colors = module('blender.color_presets')
    tables = module('color_presets')
    views, storage = module('blender.views'), module('data')
    layers, scalars = module('blender.layers'), module('blender.scalars')
    graph, copies = module('blender.graph'), module('blender.copy_display')
    summary = module('blender.view_summary')
    package = Path(importlib.import_module(args.module).__file__).parent
    report.update(blender=bpy.app.version_string, installed_package=str(package),
                  installed_sources={name: digest_file(package / name) for name in
                                     ('color_presets.py', 'blender/color_presets.py')})

    def target(obj, role):
        return colors.preset_target(obj, role)

    def snapshot(obj, role):
        return colors.ramp_snapshot(target(obj, role)['node'].color_ramp)

    def science(obj):
        data = storage.load_dataset(bpy.path.abspath(obj['qc_dataset']))
        return {key: hashlib.sha256(array.tobytes()).hexdigest() for key, array in data.arrays.items()}

    def links(tree):
        return sorted((link.from_node.name, link.from_socket.identifier,
                       link.to_node.name, link.to_socket.identifier) for link in tree.links)

    def unchanged_controls(obj, role):
        captured = summary.capture_view_summary(obj, bpy.context.scene.frame_current)
        captured.pop('captured_at_utc')
        for mat in captured['display']['materials']:
            if mat['role'] == role:
                mat['controls'] = [item for item in mat['controls'] if item['name'] != 'color_ramp']
        return {'summary': captured, 'geometry_links': links(graph.view_modifier(obj).node_group),
                'material_links': links(target(obj, role)['material'].node_tree), 'science': science(obj)}

    def assert_preset(obj, role, identifier):
        actual = snapshot(obj, role)
        expected = tables.get_preset(identifier)
        for name in ('color_mode', 'interpolation', 'hue_interpolation'):
            assert actual[name] == getattr(expected, name), (identifier, name, actual[name])
        np.testing.assert_allclose([p for p, _ in actual['elements']],
                                   [p for p, _ in expected.elements], rtol=0, atol=1e-7)
        np.testing.assert_allclose([c for _, c in actual['elements']],
                                   [c for _, c in expected.elements], rtol=0, atol=1e-7)
        # Independently construct a native reference ramp and evaluate the live
        # Blender curve, including B_SPLINE values between the frozen stops.
        mat = bpy.data.materials.new('QC preset evaluation reference')
        mat.use_nodes = True
        try:
            reference = mat.node_tree.nodes.new('ShaderNodeValToRGB').color_ramp
            for item, (position, color) in zip(reference.elements, (expected.elements[0], expected.elements[-1])):
                item.position, item.color = position, color
            for position, color in expected.elements[1:-1]:
                reference.elements.new(position).color = color
            reference.color_mode = expected.color_mode
            reference.interpolation = expected.interpolation
            reference.hue_interpolation = expected.hue_interpolation
            ramp = target(obj, role)['node'].color_ramp
            fractions = np.linspace(0, 1, 65)
            np.testing.assert_allclose([ramp.evaluate(float(f))[:] for f in fractions],
                                       [reference.evaluate(float(f))[:] for f in fractions], rtol=0, atol=1e-7)
        finally:
            bpy.data.materials.remove(mat)

    if args.reopen_check:
        expected = json.loads(bpy.context.scene['qc_color_preset_verification'])
        for name, record in expected.items():
            obj = bpy.data.objects[name]
            assert json.loads(json.dumps(snapshot(obj, record['role']))) == record['ramp'], name
            assert science(obj) == record['science'], name
            assert json.loads(json.dumps(unchanged_controls(obj, record['role']))) == record['controls'], name
            assert target(obj, record['role'])['material'].name == record['material'], name
            current = summary.capture_view_summary(obj, bpy.context.scene.frame_current)
            assert current['dataset_manifest_sha256'] == record['dataset_manifest_sha256'], name
        report['cold_reopen'] = {'status': 'Passed', 'scene': bpy.data.filepath, 'objects': list(expected)}
        return

    if args.field_dataset is None or not args.field_dataset.is_absolute():
        raise ValueError('--field-dataset must be an absolute qualified Dataset path')
    work = args.output.parent / (args.output.stem + '-work')
    work.mkdir(parents=True, exist_ok=False)
    field_data = storage.load_dataset(args.field_dataset)
    report['field_input'] = {'path': str(args.field_dataset),
                             'manifest_sha256': digest_file(args.field_dataset / 'manifest.json'),
                             'source': field_data.metadata['source']}

    field = views.field_view(str(args.field_dataset))
    field.name = 'Preset scalar target'
    scalars.add_mapping(field, field, -.08, .12)
    second = views.field_view(str(args.field_dataset))
    second.name = 'Preset independent scalar'
    scalars.add_mapping(second, second, -.08, .12)
    assert target(field, 'scalar_map')['material'] != target(second, 'scalar_map')['material']

    charge_data = storage.Dataset(
        {'source': {'filename': 'color-presets-engineering-fixture',
                    'sha256': hashlib.sha256(b'color-presets-engineering-fixture-v1').hexdigest()},
         'calculation_status': 'synthetic', 'coordinate_unit': 'angstrom', 'fields': [],
         'charges': [{'method': 'engineering_fixture', 'array': 'charges', 'unit': 'e'}]},
        {'atomic_numbers': np.array([8, 1, 1], dtype=np.int32),
         'positions': np.array([[0., 0., 0.], [.8, .5, 0.], [-.8, .5, 0.]]),
         'bonds': np.array([[0, 1], [0, 2]], dtype=np.int32), 'charges': np.array([-.8, .4, .4])})
    storage.save_dataset(charge_data, work / 'engineering-charge.qcdata')
    charge = views.atom_view(work / 'engineering-charge.qcdata')
    charge.name = 'Preset engineering charge'
    layers.activate(bpy.context, charge)
    assert bpy.ops.qcblender.color_charge(method='engineering_fixture') == {'FINISHED'}
    report['charge_input'] = 'Engineering fixture; not a scientific acceptance sample'

    for obj, role in ((field, 'scalar_map'), (charge, 'charge_map')):
        material = target(obj, role)['material']
        controls = copies._material_role(material, role)
        controls['color_invert'].outputs[0].default_value = 1.
        state = copies._state(obj)
        state['modifier'][state['sockets']['Show Legend'].identifier] = True
        before = unchanged_controls(obj, role)
        layers.activate(bpy.context, obj)
        for identifier in tables.PRESETS:
            assert bpy.ops.qcblender.apply_color_preset('EXEC_DEFAULT', material_role=role,
                                                       preset=identifier) == {'FINISHED'}
            assert_preset(obj, role, identifier)
            assert unchanged_controls(obj, role) == before, (obj.name, identifier)
            live = summary.capture_view_summary(obj, bpy.context.scene.frame_current)
            exported = next(control['value'] for mat in live['display']['materials'] if mat['role'] == role
                            for control in mat['controls'] if control['name'] == 'color_ramp')
            np.testing.assert_allclose([item['color'] for item in exported['elements']],
                                       [color for _, color in snapshot(obj, role)['elements']])
            assert exported['interpolation'] == tables.PRESETS[identifier].interpolation
        # Explicitly applying a preset may replace a custom HSV ramp.
        ramp = target(obj, role)['node'].color_ramp
        ramp.color_mode, ramp.hue_interpolation = 'HSV', 'FAR'
        ramp.elements.new(.424).color = (.1, .6, .4, .7)
        ramp.interpolation = 'CONSTANT'
        custom = snapshot(obj, role)
        pending = target(obj, role)
        assert snapshot(obj, role) == custom  # dialog target preflight is read-only
        # Inject one real RNA-write failure; all later writes are the real restore.
        original_write = colors._write_ramp
        calls = 0

        def failing_once(native_ramp, values):
            nonlocal calls
            calls += 1
            if calls == 1:
                native_ramp.elements[0].color = (1., 0., 0., 1.)
                native_ramp.elements.remove(native_ramp.elements[-1])
                raise RuntimeError('injected ColorRamp write failure')
            original_write(native_ramp, values)

        colors._write_ramp = failing_once
        try:
            try:
                colors.apply_preset(obj, role, 'VIRIDIS')
            except RuntimeError as error:
                assert 'injected ColorRamp write failure' in str(error)
            else:
                raise AssertionError('Injected failure was not propagated')
        finally:
            colors._write_ramp = original_write
        assert snapshot(obj, role) == custom
        colors.apply_preset(obj, role, 'VIRIDIS', expected_identity=pending['identity'],
                            expected_pointers=pending['pointers'])
        assert_preset(obj, role, 'VIRIDIS')
    report['presets_modes_evaluation_controls_science_summary'] = 'Passed'
    report['partial_write_rollback_fault_injection'] = 'Passed'
    report['preflight_without_write'] = 'Passed'

    scalar_mat = target(field, 'scalar_map')['material']
    native = field.copy()
    bpy.context.collection.objects.link(native)
    native.name = 'Preset native shared material'
    duplicate = layers.copy_layer(field, bpy.context.collection)
    duplicate.name = 'Preset QC independent duplicate'
    original_copy = snapshot(duplicate, 'scalar_map')
    independent = snapshot(second, 'scalar_map')
    colors.apply_preset(field, 'scalar_map', 'CIVIDIS')
    assert_preset(native, 'scalar_map', 'CIVIDIS')
    assert snapshot(duplicate, 'scalar_map') == original_copy
    assert snapshot(second, 'scalar_map') == independent
    assert target(duplicate, 'scalar_map')['material'] != scalar_mat
    report['native_sharing_qc_copy_and_new_view_independence'] = 'Passed'

    unchanged = snapshot(field, 'scalar_map')
    denied = []

    def reject(label, action):
        try:
            action()
        except (ValueError, KeyError, TypeError, AttributeError, ReferenceError, RuntimeError) as error:
            denied.append({'case': label, 'error': str(error)})
        else:
            raise AssertionError('Expected refusal: ' + label)
        assert colors.ramp_snapshot(next(node for node in scalar_mat.node_tree.nodes
                                         if node.name == ramp_name).color_ramp) == unchanged

    original = target(field, 'scalar_map')
    ramp_node = original['node']
    ramp_name = ramp_node.name
    reject('active object changed', lambda: colors.apply_preset(second, 'scalar_map', 'QC_DEFAULT',
                                                               expected_identity=original['identity']))
    reject('unknown preset', lambda: colors.apply_preset(field, 'scalar_map', 'UNKNOWN'))
    reject('unsupported role', lambda: colors.apply_preset(field, 'fog', 'QC_DEFAULT'))
    del ramp_node['qc_role']
    try:
        reject('missing role', lambda: colors.apply_preset(field, 'scalar_map', 'QC_DEFAULT'))
        wrong = scalar_mat.node_tree.nodes.new('ShaderNodeValue')
        wrong['qc_role'] = 'color_ramp'
        try:
            reject('wrong node type', lambda: colors.apply_preset(field, 'scalar_map', 'QC_DEFAULT'))
        finally:
            scalar_mat.node_tree.nodes.remove(wrong)
    finally:
        ramp_node['qc_role'] = 'color_ramp'
    extra = scalar_mat.node_tree.nodes.new('ShaderNodeValToRGB')
    extra['qc_role'] = 'color_ramp'
    try:
        reject('duplicate role', lambda: colors.apply_preset(field, 'scalar_map', 'QC_DEFAULT'))
    finally:
        scalar_mat.node_tree.nodes.remove(extra)

    references = copies._state(field)['materials']['scalar_map'][1]
    assert all(kind == 'node' for kind, _, _ in references)

    def rebind(mat):
        for _, socket, _ in references:
            socket.default_value = mat

    changed_mat = scalar_mat.copy()
    try:
        rebind(changed_mat)
        reject('material changed during dialog', lambda: colors.apply_preset(
            field, 'scalar_map', 'QC_DEFAULT', expected_identity=original['identity']))
        assert colors.ramp_snapshot(copies._material_role(changed_mat, 'scalar_map')['color_ramp'].color_ramp) == unchanged
    finally:
        rebind(scalar_mat)
        bpy.data.materials.remove(changed_mat)
    library = work / 'read-only-material.blend'
    bpy.data.libraries.write(str(library), {scalar_mat})
    with bpy.data.libraries.load(str(library), link=True) as (available, loaded):
        loaded.materials = [scalar_mat.name]
    linked = loaded.materials[0]
    try:
        rebind(linked)
        reject('linked read-only material', lambda: colors.apply_preset(field, 'scalar_map', 'QC_DEFAULT'))
    finally:
        rebind(scalar_mat)
        bpy.data.materials.remove(linked)
    report['refused_targets'] = {'status': 'Passed', 'cases': denied}

    expected = {}
    for obj, role in ((field, 'scalar_map'), (native, 'scalar_map'), (duplicate, 'scalar_map'),
                      (second, 'scalar_map'), (charge, 'charge_map')):
        captured = summary.capture_view_summary(obj, bpy.context.scene.frame_current)
        expected[obj.name] = {'role': role, 'ramp': snapshot(obj, role), 'science': science(obj),
                              'controls': unchanged_controls(obj, role),
                              'material': target(obj, role)['material'].name,
                              'dataset_manifest_sha256': captured['dataset_manifest_sha256']}
    bpy.context.scene['qc_color_preset_verification'] = json.dumps(expected)
    layers.activate(bpy.context, field)
    scene = args.output.with_name(args.output.stem + '-scene.blend')
    if scene.exists() or scene.with_suffix('.qcdata').exists():
        raise FileExistsError('Use a fresh output filename for the saved scene')
    module('blender.project').save_project(str(scene))
    report['scene'] = str(scene)
    report['scene_sha256'] = digest_file(scene)
    report['gui_apply_cancel_undo_redo_render'] = 'Not Run: requires the separate GUI acceptance pass'
    report['cold_reopen'] = 'Not Run: run --reopen-check in a new Blender process'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', default='bl_ext.user_default.qcblender')
    parser.add_argument('--field-dataset', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reopen-check', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    if not args.output.is_absolute():
        parser.error('--output must be an absolute path')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {'status': 'Failed', 'script_sha256': digest_file(__file__)}
    try:
        run(args, report)
        report['status'] = 'Passed'
    except Exception:
        report['error'] = traceback.format_exc()
        raise
    finally:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
