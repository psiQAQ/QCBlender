"""Foreground checks of the installed external-result browser and portable projects.

Run once per case with --check prepare in a fresh Blender session. Then open each
saved evidence.blend and moved 中文 path/evidence.blend in separate cold Blender
sessions and run --check reopen. No check is marked Passed before it executes.
"""
import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
from unittest.mock import patch

import bpy
import numpy as np


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qc_result_evidence', SCRIPT_ROOT / 'tools/verify_vmd_parameters.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
module = evidence.module
CASES = ('C07', 'C08', 'C09', 'C12', 'NBO')


def installed_extension():
    bpy.ops.preferences.addon_enable(module=evidence.MODULE)
    package = importlib.import_module(evidence.MODULE)
    location = Path(package.__file__).resolve()
    assert 'extensions' in location.parts and location.parent != (SCRIPT_ROOT / 'qcblender').resolve(), location
    assert hasattr(bpy.types.Object, 'qc_result_browser'), 'Result browser is not registered'
    module('blender.source_browser').refresh_loaded_sources()
    return str(location)


def active(obj):
    evidence.activate(obj)
    return obj


def role(name):
    return next(obj for obj in bpy.context.scene.objects if obj.get('qc_analysis_role') == name)


def finish_modal(operator_id, **kwargs):
    """Drive the real async operator and its Job without a synthetic worker result."""
    operations = module('blender.ui')._operations
    before = set(operations)
    result = getattr(bpy.ops.qcblender, operator_id)('EXEC_DEFAULT', **kwargs)
    assert result == {'RUNNING_MODAL'}, (operator_id, result)
    added = set(operations) - before
    assert len(added) == 1, (operator_id, added)
    operator = operations[added.pop()][0]
    event = type('TimerEvent', (), {'type': 'TIMER'})()
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        result = operator.modal(bpy.context, event)
        if result != {'RUNNING_MODAL'}:
            assert result == {'FINISHED'}, (operator_id, result, operator._job.directory)
            report = json.loads((operator._job.directory / 'result.json').read_text(encoding='utf-8'))
            assert report['status'] == 'succeeded', report
            return report
        time.sleep(.1)
    operator.cancel(bpy.context)
    raise TimeoutError(f'{operator_id}: {operator._job.directory}')


def reject_changed_modal(operator_id, change, **kwargs):
    """Let a real worker finish, then prove stale UI state cannot publish its result."""
    operations = module('blender.ui')._operations
    before = set(operations)
    assert getattr(bpy.ops.qcblender, operator_id)('EXEC_DEFAULT', **kwargs) == {'RUNNING_MODAL'}
    added = set(operations) - before
    assert len(added) == 1
    operator = operations[added.pop()][0]
    event = type('TimerEvent', (), {'type': 'TIMER'})()
    try:
        change()
        scene_after_change = {entry.name: object_snapshot(entry) for entry in bpy.context.scene.objects}
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            outcome = operator.modal(bpy.context, event)
            if outcome != {'RUNNING_MODAL'}:
                assert outcome == {'CANCELLED'}, (operator_id, outcome)
                worker = json.loads((operator._job.directory / 'result.json').read_text(encoding='utf-8'))
                assert worker['status'] == 'succeeded', worker
                assert scene_after_change == {entry.name: object_snapshot(entry)
                                              for entry in bpy.context.scene.objects}
                return operator._job.directory.name
            time.sleep(.1)
        raise TimeoutError(f'{operator_id}: {operator._job.directory}')
    finally:
        if id(operator) in operations:
            operator.cancel(bpy.context)


def metadata(obj):
    return module('blender.source_browser').read_metadata(obj)


def state(obj):
    return json.loads(obj['qc_result_displaystate'])


def source_arrays():
    result = {}
    for obj in bpy.context.scene.objects:
        if not obj.get('qc_dataset'):
            continue
        directory = module('data').filesystem_path(bpy.path.abspath(obj['qc_dataset']))
        manifest = (directory / 'manifest.json').read_bytes()
        assert hashlib.sha256(manifest).hexdigest() == obj['qc_dataset_sha256'], obj.name
        dataset = module('data').load_dataset(directory)
        key = obj['qc_dataset_sha256']
        arrays = {name: hashlib.sha256(values.tobytes()).hexdigest()
                  for name, values in dataset.arrays.items()}
        arrays['$metadata'] = hashlib.sha256(json.dumps(dataset.metadata, sort_keys=True,
                                                       ensure_ascii=False).encode('utf-8')).hexdigest()
        assert key not in result or result[key] == arrays
        result[key] = arrays
    return result


def focus_children(obj):
    markers = [child for child in obj.children if child.get('qc_result_focus')]
    assert len(markers) <= 1
    return markers


def object_snapshot(obj):
    mesh = obj.data if obj.type == 'MESH' else None
    vertices = np.array([tuple(vertex.co) for vertex in mesh.vertices], dtype=np.float64) if mesh else None
    return {'kind': obj.get('qc_view_kind'), 'role': obj.get('qc_analysis_role'),
            'dataset_sha256': obj.get('qc_dataset_sha256'),
            'displaystate': obj.get('qc_result_displaystate'),
            'sourceidentity': obj.get('qc_result_source_identity'),
            'vertices': len(mesh.vertices) if mesh else None,
            'vertex_sha256': hashlib.sha256(vertices.tobytes()).hexdigest() if mesh else None,
            'nbo_index': obj.get('qc_nbo_index'), 'e2_index': obj.get('qc_e2_index'),
            'parent': obj.parent.name if obj.parent else None,
            'focus': [{'name': child.name, 'parent': child.parent.name,
                       'location': list(child.location), 'hidden': child.hide_render,
                       'radius': next(node.inputs['Radius'].default_value
                                      for node in child.modifiers['QC Result Focus'].node_group.nodes
                                      if node.bl_idname == 'GeometryNodeMeshToPoints'),
                       'label': [(label.name, label.data.body, label.hide_render)
                                 for label in child.children if label.get('qc_result_label')]}
                      for child in focus_children(obj)]}


def reject_without_mutation(obj, action):
    before = {entry.name: object_snapshot(entry) for entry in bpy.context.scene.objects}
    error = evidence.expect_error(action, '')
    assert before == {entry.name: object_snapshot(entry) for entry in bpy.context.scene.objects}
    return error


def check_c07():
    scatter = next(obj for obj in bpy.context.scene.objects if obj.get('qc_view_kind') == 'scatter')
    active(scatter)
    data = module('data').load_dataset(bpy.path.abspath(scatter['qc_dataset']))
    before = source_arrays()
    browser = scatter.qc_result_browser
    browser.swap_axes = True
    fields = data.metadata['fields']
    x = data.arrays[fields[0]['array']].ravel()
    y = data.arrays[fields[1]['array']].ravel()
    valid = (data.arrays[fields[0]['valid_mask']].ravel() &
             data.arrays[fields[1]['valid_mask']].ravel() & np.isfinite(x) & np.isfinite(y))
    assert valid.any()
    x, y = x[valid], y[valid]
    browser.x_low_on = browser.x_high_on = browser.y_low_on = browser.y_high_on = True
    browser.x_low, browser.x_high = (float(np.nanquantile(x, q)) for q in (.2, .8))
    browser.y_low, browser.y_high = (float(np.nanquantile(y, q)) for q in (.2, .8))
    report = finish_modal('filter_result_scatter')
    saved = state(scatter)
    assert saved['x_field'] == 0 and saved['y_field'] == 1
    assert saved['matching_count'] == report['matching_count']
    assert saved['displayed_count'] == len(scatter.data.vertices) <= 50000
    assert saved['matching_count'] >= saved['displayed_count'] > 0
    assert 'dataset' not in saved and source_arrays() == before
    unchanged = object_snapshot(scatter)
    original_swap = browser.swap_axes
    changed_axes = reject_changed_modal('filter_result_scatter',
                                        lambda: setattr(browser, 'swap_axes', not original_swap))
    browser.swap_axes = original_swap
    original_name = scatter.name
    renamed = reject_changed_modal('filter_result_scatter',
                                   lambda: setattr(scatter, 'name', original_name + ' pending'))
    scatter.name = original_name
    source = scatter.parent
    assert source is not None
    original_source_sha = source.get('qc_source_sha256')
    assert isinstance(original_source_sha, str)
    changed_source = reject_changed_modal('filter_result_scatter',
                                          lambda: source.__setitem__('qc_source_sha256', '0' * 64))
    source['qc_source_sha256'] = original_source_sha
    assert object_snapshot(scatter) == unchanged
    job = module('blender.jobs').Job('result_scatter', dataset=str(Path(bpy.path.abspath(scatter['qc_dataset']))),
        dataset_sha256='0' * 64, x_field=0, y_field=1)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        failed = job.poll()
        if failed is not None:
            break
        time.sleep(.1)
    else:
        job.cancel()
        raise TimeoutError('Invalid scatter source digest')
    assert failed['status'] == 'failed' and 'source changed' in failed['error'].lower(), failed
    assert source_arrays() == before and object_snapshot(scatter) == unchanged
    return {'scatter_job': report, 'changed_axes': changed_axes,
            'renamed_target': renamed, 'changed_source': changed_source, 'bad_digest': 'Passed'}


def check_c08():
    minimum, area = role('esp_minimum'), role('esp_area')
    before = source_arrays()
    analysis = metadata(minimum)['analysis']
    row = next(row for row in analysis['extrema'] if row['kind'] == 'minimum')
    active(minimum)
    browser = minimum.qc_result_browser
    browser.source_number = row['serial']
    browser.esp_kind = 'minimum'
    browser.marker_size = .17
    browser.show_labels = True
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert len(state(minimum)['indexes']) == 1
    marker = focus_children(minimum)[0]
    assert marker.parent == minimum and len(marker.children) == 1
    assert marker.children[0]['qc_result_label']
    label = marker.children[0]
    layers = module('blender.layers')
    minimum.hide_set(True)
    minimum.hide_render = True
    layers.sync_chart_children(minimum)
    browser.show_labels = False
    with bpy.context.temp_override(object=minimum, active_object=minimum):
        assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert marker.hide_get() and label.hide_get() and marker.hide_render and label.hide_render
    assert not marker['qc_layer_restore_viewport'] and not marker['qc_layer_restore_render']
    assert label['qc_layer_restore_viewport'] and label['qc_layer_restore_render']
    browser.show_labels = True
    with bpy.context.temp_override(object=minimum, active_object=minimum):
        assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert not label['qc_layer_restore_viewport'] and not label['qc_layer_restore_render']
    browser.source_number = max(point['serial'] for point in analysis['extrema']) + 1
    with bpy.context.temp_override(object=minimum, active_object=minimum):
        assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert marker['qc_layer_restore_viewport'] and marker['qc_layer_restore_render']
    assert label['qc_layer_restore_viewport'] and label['qc_layer_restore_render']
    minimum.hide_set(False)
    minimum.hide_render = False
    layers.sync_chart_children(minimum)
    assert marker.hide_get() and label.hide_get() and marker.hide_render and label.hide_render
    browser.source_number = row['serial']
    active(minimum)
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert not marker.hide_get() and not label.hide_get()
    assert not marker.hide_render and not label.hide_render
    focus_tree = marker.modifiers['QC Result Focus'].node_group
    extra_node = focus_tree.nodes.new('GeometryNodeMeshToPoints')
    try:
        custom_graph_error = reject_without_mutation(
            minimum, lambda: bpy.ops.qcblender.apply_result_filter())
        assert 'focus graph' in custom_graph_error.lower(), custom_graph_error
    finally:
        focus_tree.nodes.remove(extra_node)
    browser.value_low_on = browser.value_high_on = True
    browser.value_low, browser.value_high = 1., -1.
    error = reject_without_mutation(minimum, lambda: bpy.ops.qcblender.apply_result_filter())
    browser.value_low_on = browser.value_high_on = False
    active(area)
    bins = metadata(area)['analysis']['area_bins']
    ordered = sorted(row['center'] for row in bins)
    state_area = area.qc_result_browser
    state_area.value_low_on = state_area.value_high_on = True
    state_area.value_low, state_area.value_high = ordered[len(ordered)//4], ordered[3*len(ordered)//4]
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    selected = state(area)
    assert 0 < selected['displayed_area'] <= selected['total_area']
    assert selected['displayed_source_percentage'] == sum(bins[i]['percentage'] for i in selected['indexes'])
    assert all(('begin' in row and 'end' in row) or ('begin' not in row and 'end' not in row) for row in bins)
    assert source_arrays() == before
    annotations = module('blender.annotations')
    original_copy_annotations = annotations.copy_annotations

    def fail_on_focus(source, target, collection):
        if source.get('qc_result_focus'):
            raise ValueError('Injected focus copy failure')
        return original_copy_annotations(source, target, collection)

    scene_before_failure = set(bpy.data.objects.keys())
    with patch.object(annotations, 'copy_annotations', side_effect=fail_on_focus):
        try:
            module('blender.layers').copy_layer(minimum, bpy.context.collection)
        except ValueError as copy_error:
            assert 'Injected focus copy failure' in str(copy_error)
        else:
            raise AssertionError('Focus copy unexpectedly succeeded during injected failure')
    assert set(bpy.data.objects.keys()) == scene_before_failure
    assert source_arrays() == before
    copied = module('blender.layers').copy_layer(minimum, bpy.context.collection)
    copied.name = 'QC copied ESP result'
    copied_name = copied.name
    copied_markers = focus_children(copied)
    assert len(copied_markers) == 1 and copied_markers[0] != marker
    assert len([child for child in copied_markers[0].children if child.get('qc_result_label')]) == 1
    original_display = object_snapshot(minimum)
    active(copied)
    copied.qc_result_browser.source_number = max(row['serial'] for row in analysis['extrema']) + 1
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert not state(copied)['indexes'] and len(copied.data.vertices) == 0
    assert object_snapshot(minimum) == original_display
    copied_marker_name = copied_markers[0].name
    from mathutils import Matrix
    user_child = bpy.data.objects.new('QC user note under focus', None)
    bpy.context.collection.objects.link(user_child)
    user_child.parent = copied_markers[0]
    user_child.matrix_world = Matrix.Translation((1.2, -2.3, 3.4)) @ Matrix.Rotation(.37, 4, 'Z')
    user_world = np.array(user_child.matrix_world)
    user_name = user_child.name
    copied_parent = copied.parent
    assert bpy.ops.qcblender.layer_action(target=copied_name, action='REMOVE') == {'FINISHED'}
    assert copied_name not in bpy.data.objects and marker.name in bpy.data.objects
    assert copied_marker_name not in bpy.data.objects
    assert user_name in bpy.data.objects and user_child.parent == copied_parent
    np.testing.assert_allclose(np.array(user_child.matrix_world), user_world, rtol=0, atol=1e-6)
    assert source_arrays() == before
    return {'point_error': error, 'custom_focus_graph': custom_graph_error,
            'hidden_owner_restore': 'Passed',
            'area': selected, 'copy_failure_cleanup': 'Passed', 'copy_remove': 'Passed',
            'user_child': {'name': user_name, 'parent': copied_parent.name if copied_parent else None,
                           'matrix_world': user_world.tolist()}}


def check_c09():
    point = role('aim_N')
    before = source_arrays()
    analysis = metadata(point)['analysis']
    first = next(row for row in analysis['critical_points'] if row['type'] == 'N')
    active(point)
    browser = point.qc_result_browser
    browser.source_number = first['serial']
    browser.aim_type = 'N'
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert len(state(point)['indexes']) == 1 and len(focus_children(point)) == 1
    numeric = next((key for values in analysis.get('properties', {}).values()
                    for key, value in values.items() if isinstance(value, (int, float))), None)
    assert numeric, 'Real AIM fixture has no numeric CP property'
    browser.source_number = 0
    browser.aim_numeric_key = numeric
    browser.value_high_on = True
    browser.value_high = max(float(values[numeric]) for values in analysis['properties'].values()
                             if numeric in values and isinstance(values[numeric], (int, float)))
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert state(point)['indexes'] and source_arrays() == before
    browser.value_low_on = True
    browser.value_low = browser.value_high + 1
    error = reject_without_mutation(point, lambda: bpy.ops.qcblender.apply_result_filter())
    browser.value_low_on = False
    return {'numeric_key': numeric, 'bad_range': error}


def check_c12(source_root):
    table = role('ets_nocv')
    active(table)
    rows = metadata(table)['analysis']['pairs']
    row = next(row for row in rows if row['pair'] == 1 and row['spin'] == 'Total')
    cube = source_root / 'outputs/v1-acceptance/sources/c10-c13/multiwfn-cobh3-20260927/COBH3-NOCV-pair1.cub'
    assert cube.is_file(), cube
    job = finish_modal('import_nocv_field', cube_path=str(cube), pair_number=1,
                       spin='Total', unit='electron/bohr^3')
    field = role('nocv_field')
    assert field['qc_ets_table_dataset_sha256'] == table['qc_dataset_sha256']
    before = source_arrays()
    active(table)
    browser = table.qc_result_browser
    browser.source_number = row['pair']
    browser.spin = row['spin']
    browser.eigen_side = 'positive'
    browser.sort_by = 'pair_energy'
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert bpy.context.object == field and len(state(table)['indexes']) == 1
    original_source = table['qc_source_sha256']
    active(table)
    stale_import = reject_changed_modal('import_nocv_field',
        lambda: table.__setitem__('qc_source_sha256', '0' * 64),
        cube_path=str(cube), pair_number=1, spin='Total', unit='electron/bohr^3')
    table['qc_source_sha256'] = original_source
    other_parent = table.parent.copy()
    bpy.context.collection.objects.link(other_parent)
    other_table = module('blender.layers').copy_layer(table, bpy.context.collection)
    other_table.parent = other_parent
    active(other_table)
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert bpy.context.object == other_table and len(state(other_table)['indexes']) == 1
    bpy.data.objects.remove(other_table, do_unlink=True)
    bpy.data.objects.remove(other_parent, do_unlink=True)
    saved_table_digest = field['qc_ets_table_dataset_sha256']
    del field['qc_ets_table_dataset_sha256']
    active(table)
    legacy_error = reject_without_mutation(table, lambda: bpy.ops.qcblender.apply_result_filter())
    assert 'no saved table dataset identity' in legacy_error.lower(), legacy_error
    field['qc_ets_table_dataset_sha256'] = saved_table_digest
    duplicate = module('blender.layers').copy_layer(field, bpy.context.collection)
    active(table)
    error = reject_without_mutation(table, lambda: bpy.ops.qcblender.apply_result_filter())
    assert bpy.context.object == table and 'several' in error.lower()
    bpy.data.objects.remove(duplicate, do_unlink=True)
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    assert bpy.context.object == field and source_arrays() == before
    return {'nocv_job': job, 'stale_import': stale_import,
            'different_parent': 'Passed', 'legacy_identity': legacy_error,
            'duplicate_error': error}


def check_nbo(source_root):
    source = source_root / 'outputs/log-examples/water_neutral_nbo_opt_freq.out'
    assert source.is_file(), source
    job = module('blender.jobs').Job('import', source=str(source), job_index=1)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        report = job.poll()
        if report is not None:
            break
        time.sleep(.1)
    else:
        job.cancel()
        raise TimeoutError('NBO reference import')
    assert report['status'] == 'succeeded', report
    reference = module('blender.views').atom_view(job.directory / 'dataset')
    active(reference)
    nbo_job = finish_modal('import_nbo', filepath=str(source), job_number=2, block_number=1)
    nbo = bpy.context.object
    assert nbo.get('qc_view_kind') == 'nbo'
    before = source_arrays()
    analysis = metadata(nbo)['analysis']
    assert analysis['orbitals'] and analysis['interactions']
    browser = nbo.qc_result_browser
    browser.source_number = 1
    browser.orbital_type = 'BD'
    browser.occupancy_low_on = True
    browser.occupancy_low = 1.9
    browser.donor = 1
    browser.acceptor = 7
    browser.e2_low_on = True
    browser.e2_low = .5
    assert bpy.ops.qcblender.apply_result_filter() == {'FINISHED'}
    selected = state(nbo)
    assert len(selected['orbitals']) == len(selected['interactions']) == 1, selected
    assert analysis['orbitals'][selected['orbitals'][0]]['number'] == 1
    assert analysis['interactions'][selected['interactions'][0]]['donor'] == 1
    assert source_arrays() == before
    browser.occupancy_high_on = True
    browser.occupancy_high = 1.0
    error = reject_without_mutation(nbo, lambda: bpy.ops.qcblender.apply_result_filter())
    browser.occupancy_high_on = False
    return {'nbo_job': nbo_job, 'bad_occupancy': error}


def snapshot():
    return {'arrays': source_arrays(),
            'objects': {obj.name: object_snapshot(obj) for obj in bpy.context.scene.objects
                        if obj.get('qc_result_displaystate')}}


def write_report(path, report):
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')


def case_fixture(case, source_root):
    if case in ('C07', 'C08', 'C09'):
        current = (source_root / 'outputs/multiwfn-parameters/01-foundation-r5/final-sop/cases'
                   / case / f'{case}.blend')
        if current.is_file():
            return current
    return source_root / f'outputs/v1-acceptance/cases/{case}/{case}.blend'


def prepare(case, out, source_root):
    out.mkdir(parents=True, exist_ok=True)
    original = None
    if case != 'NBO':
        original = case_fixture(case, source_root)
        assert original.is_file(), original
        bpy.ops.wm.open_mainfile(filepath=str(original))
        installed_extension()
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    region = next(region for region in area.regions if region.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        checks = {'C07': lambda: check_c07(), 'C08': lambda: check_c08(),
                  'C09': lambda: check_c09(), 'C12': lambda: check_c12(source_root),
                  'NBO': lambda: check_nbo(source_root)}[case]()
        expected = snapshot()
        assert expected['objects'] and expected['arrays']
        module('blender.project').save_project(out / 'evidence.blend')
        moved = out / 'moved 中文 path'
        moved.mkdir(exist_ok=True)
        shutil.copy2(out / 'evidence.blend', moved / 'evidence.blend')
        shutil.copytree(module('data').filesystem_path(out / 'evidence.qcdata'),
                        module('data').filesystem_path(moved / 'evidence.qcdata'), dirs_exist_ok=True)
        report = {'case': case, 'installed_module': str(Path(importlib.import_module(evidence.MODULE).__file__).resolve()),
                  'fixture': str(original) if original else None,
                  'checks': checks, 'expected': expected, 'prepare': 'Passed',
                  'cold_open': 'Not Run', 'moved_cold_open': 'Not Run', 'status': 'Not Run'}
        write_report(out / 'checks.json', report)
        return {'case': case, 'prepare': 'Passed', 'cold_open': 'Not Run', 'moved_cold_open': 'Not Run'}


def reopen(case, out):
    report_path = out / 'checks.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    assert report['case'] == case and report['prepare'] == 'Passed'
    blend = Path(bpy.data.filepath).resolve()
    assert blend.name == 'evidence.blend' and blend.parent in (out.resolve(), (out / 'moved 中文 path').resolve())
    actual = snapshot()
    assert actual == report['expected'], 'Saved result state, source arrays, or focus children changed after cold open'
    if case == 'C08':
        saved_child = report['checks']['user_child']
        child = bpy.data.objects.get(saved_child['name'])
        assert child is not None and (child.parent.name if child.parent else None) == saved_child['parent']
        np.testing.assert_allclose(np.array(child.matrix_world), saved_child['matrix_world'], rtol=0, atol=1e-6)
    for obj in bpy.context.scene.objects:
        if obj.get('qc_dataset'):
            dataset = Path(bpy.path.abspath(obj['qc_dataset'])).resolve()
            assert dataset.is_relative_to(blend.with_suffix('.qcdata')), (obj.name, dataset)
        if obj.get('qc_result_displaystate'):
            assert 'dataset' not in json.loads(obj['qc_result_displaystate'])
            metadata(obj)
    key = 'moved_cold_open' if blend.parent != out.resolve() else 'cold_open'
    report[key] = 'Passed'
    report['status'] = 'Passed' if report['cold_open'] == report['moved_cold_open'] == 'Passed' else 'Not Run'
    write_report(report_path, report)
    return {'case': case, key: 'Passed', 'status': report['status']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case', choices=CASES, required=True)
    parser.add_argument('--check', choices=('prepare', 'reopen'), required=True)
    parser.add_argument('--source-root', type=Path, default=SCRIPT_ROOT)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.out = args.out.resolve()
    args.source_root = args.source_root.resolve()
    installed_extension()
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    outcome = prepare(args.case, args.out, args.source_root) if args.check == 'prepare' else reopen(args.case, args.out)
    print(json.dumps(outcome, ensure_ascii=False))
