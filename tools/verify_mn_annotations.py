"""Installed B annotation checks on the saved A feature project."""
import argparse
import importlib.util
from itertools import combinations
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
spec = importlib.util.spec_from_file_location('qc_evidence', ROOT / 'tools/verify_vmd_parameters.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
module = evidence.module


def labels(owner):
    return {entry['id']: (child, entry) for child in owner.children
            if child.type == 'FONT' and 'qc_annotation' in child
            for entry in [json.loads(child['qc_annotation'])] if entry['role'] == 'LABEL'}


def leaders(owner):
    return {entry['id']: (child, entry) for child in owner.children
            if child.type == 'CURVE' and 'qc_annotation' in child
            for entry in [json.loads(child['qc_annotation'])] if entry['role'] == 'LEADER'}


def snapshot(owner):
    result = {}
    for key, (child, entry) in labels(owner).items():
        result[key] = {'record': entry, 'body': child.data.body,
                       'location': list(child.location), 'visible': [child.hide_viewport, child.hide_render]}
    return json.loads(json.dumps(result, ensure_ascii=False))


def assert_values(owner):
    positions, record = module('blender.geometry').current_geometry(owner)
    measurements = module('measurements')
    found = labels(owner)
    assert set(found) == set(leaders(owner)), owner.name
    for key, (child, entry) in found.items():
        assert child.parent == owner and entry['geometry'] == record, (owner.name, key)
        assert entry['source_sha256'] == record['source_sha256']
        assert entry['dataset_sha256'] == record['dataset_sha256']
        assert entry['selected_job'] == record['selected_job']
        points = positions[np.array(entry['source_atom_numbers']) - 1]
        anchor = points.mean(axis=0)
        np.testing.assert_allclose(child.location, anchor + entry['offset'], atol=2e-6)
        leader, leader_entry = leaders(owner)[key]
        assert leader.parent == owner and leader_entry['geometry'] == record
        np.testing.assert_allclose(leader.data.splines[0].points[0].co[:3], anchor, atol=2e-6)
        np.testing.assert_allclose(leader.data.splines[0].points[1].co[:3], child.location, atol=2e-6)
        if entry['kind'] == 'ATOM':
            assert entry['value'] is None and child.data.body == entry['symbols'][0] + str(entry['source_atom_numbers'][0])
            continue
        try:
            value = measurements.measure(entry['kind'], positions, entry['source_atom_numbers'])
        except ValueError as error:
            assert 'undefined:' in str(error) and entry['value'] is None
            assert entry['undefined_reason'] == str(error) and 'undefined' in child.data.body
        else:
            assert entry['undefined_reason'] is None
            np.testing.assert_allclose(entry['value'], value, rtol=0, atol=1e-10)
            assert child.data.body == measurements.measurement_text(
                entry['kind'], entry['source_atom_numbers'], value, record, entry['decimals'])


def add(owner, kind, numbers, decimals=None):
    evidence.activate(owner)
    before = set(labels(owner))
    options = {'kind': kind, 'atoms': numbers}
    if decimals is not None:
        options['decimals'] = decimals
    assert bpy.ops.qcblender.add_annotation(**options) == {'FINISHED'}, (owner.name, kind)
    created = set(labels(owner)) - before
    assert len(created) == (len(numbers.split(',')) if kind == 'ATOM' else 1)
    assert_values(owner)
    return [labels(owner)[key][0] for key in created]


def reject(action, owner):
    before = snapshot(owner)
    scene_objects = set(bpy.context.scene.objects)
    error = evidence.expect_error(action, '')
    assert snapshot(owner) == before and set(bpy.context.scene.objects) == scene_objects
    return error


def moving_pair(owner, kind, other_step):
    current, _ = module('blender.geometry').current_geometry(owner)
    data = module('data').load_dataset(bpy.path.abspath(owner['qc_dataset']))
    other, _ = module('geometry').scientific_geometry(data, kind, other_step)
    pairs = list(combinations(range(len(current)), 2))
    pair = max(pairs, key=lambda ids: np.linalg.norm(current[list(ids)].mean(axis=0)
                                              - other[list(ids)].mean(axis=0)))
    assert np.linalg.norm(current[list(pair)].mean(axis=0) - other[list(pair)].mean(axis=0)) > 1e-6
    return ','.join(str(index + 1) for index in pair)


def evaluated_vertices(owner):
    owner.update_tag()
    bpy.context.view_layer.update()
    evaluated = owner.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return np.array([vertex.co[:] for vertex in mesh.vertices])
    finally:
        evaluated.to_mesh_clear()


def check_annotations(out):
    out.mkdir(parents=True, exist_ok=True)
    before_arrays = evidence.hashes()
    methane = bpy.data.objects['MN local selection source']
    optimization = bpy.data.objects['MN fixed optimization neighborhood']
    irc = next(obj for obj in bpy.context.scene.objects if obj.get('qc_irc'))
    assert len(methane.data.vertices) == 5 and optimization['qc_optimization_count'] == 4
    assert irc['qc_irc_step'] == 2

    atom = add(methane, 'ATOM', '1,2')
    distance = add(methane, 'DISTANCE', '1,2')[0]
    angle = add(methane, 'ANGLE', '2,1,3')[0]
    dihedral = add(methane, 'DIHEDRAL', '2,1,3,4')[0]
    for child in (*atom, distance, angle, dihedral):
        entry = json.loads(child['qc_annotation'])
        assert entry['decimals'] == (2 if entry['kind'] in ('ANGLE', 'DIHEDRAL') else 4)
    original = snapshot(methane)
    transform = methane.matrix_world.copy()
    methane.location.x += 2.0
    methane.rotation_euler.z += .35
    assert_values(methane)
    assert snapshot(methane) == original  # Display transform cannot change scientific values or local anchors.
    methane.matrix_world = transform

    # Explicit synthetic fixture checks the undefined branch; it is not a real calculation step.
    positions, record = module('blender.geometry').current_geometry(methane)
    degenerate = positions.copy()
    degenerate[1] = degenerate[0]
    fixture = module('data').Dataset(
        {'source': {'sha256': record['source_sha256']}, 'selected_job': record['selected_job'],
         'coordinate_unit': 'angstrom'},
        {'atomic_numbers': np.array([item.value for item in methane.data.attributes['qc_atomic_number'].data]),
         'positions': degenerate})
    fixture_positions, fixture_record = module('geometry').scientific_geometry(fixture)
    fixture_record['dataset_sha256'] = record['dataset_sha256']
    module('blender.annotations').update_annotations(methane, fixture_positions, fixture_record)
    assert json.loads(angle['qc_annotation'])['value'] is None
    assert 'undefined' in angle.data.body
    module('blender.annotations').update_annotations(methane, positions, record)
    assert_values(methane)

    errors = {text: reject(lambda text=text: bpy.ops.qcblender.add_annotation(
                  kind='DISTANCE', atoms=text), methane) for text in ('1,1', '0,2', '1,6', '1-2')}
    errors['zero_arm'] = reject(lambda: bpy.ops.qcblender.add_annotation(
        kind='ANGLE', atoms='1,1,2'), methane)

    # Edit native text/leader styling, then verify saved style and visibility.
    distance_id = json.loads(distance['qc_annotation'])['id']
    evidence.activate(methane)
    assert bpy.ops.qcblender.edit_annotation(annotation_id=distance_id, size=.21,
        color=(.3, .6, .9), offset=(.4, .1, .2), decimals=3,
        line_width=.025, show_leader=False, visible=False) == {'FINISHED'}
    styled = labels(methane)[distance_id][1]
    assert abs(styled['size'] - .21) < 1e-6 and styled['decimals'] == 3
    assert distance.hide_viewport and distance.hide_render
    assert leaders(methane)[distance_id][0].hide_render
    assert_values(methane)
    assert bpy.context.scene.camera is not None
    angle_id = json.loads(angle['qc_annotation'])['id']
    assert bpy.ops.qcblender.face_annotations(annotation_id=angle_id) == {'FINISHED'}
    expected_rotation = methane.matrix_world.to_quaternion().inverted() @ bpy.context.scene.camera.matrix_world.to_quaternion()
    assert abs(angle.rotation_quaternion.dot(expected_rotation)) > 1 - 1e-6

    # Layer duplication owns its own label, curve and material data.
    assert bpy.ops.qcblender.layer_action(target=methane.name, action='DUPLICATE') == {'FINISHED'}
    copied = bpy.context.object
    copied.name = 'MN annotation copy'
    assert set(labels(copied)) == set(labels(methane))
    for key, (label, _) in labels(copied).items():
        source_label = labels(methane)[key][0]
        assert label != source_label and label.data != source_label.data
        assert label.data.materials[0] != source_label.data.materials[0]
        assert leaders(copied)[key][0].data != leaders(methane)[key][0].data
    copied_before = snapshot(copied)
    source_before = snapshot(methane)
    key = next(iter(labels(copied)))
    assert bpy.ops.qcblender.remove_annotation(annotation_id=key) == {'FINISHED'}
    assert key not in labels(copied) and key in labels(methane)
    assert snapshot(methane) == source_before
    module('blender.copy_display').copy_parameters(methane, [copied], geometry=True,
                                                   appearance=False, numerical=False)
    assert snapshot(copied) == {k: v for k, v in copied_before.items() if k != key}
    copied_children = set(copied.children)
    copied_name = copied.name
    child_names = {child.name for child in copied_children}
    assert bpy.ops.qcblender.layer_action(target=copied_name, action='REMOVE') == {'FINISHED'}
    assert copied_name not in bpy.data.objects and all(name not in bpy.data.objects for name in child_names)
    assert snapshot(methane) == source_before

    # Optimization step changes refresh both a number and its anchor; upgrade keeps step, mask and labels.
    opt_label = add(optimization, 'DISTANCE', moving_pair(optimization, 'optimization', 1))[0]
    opt_before = snapshot(optimization)
    opt_anchor = np.array(opt_label.location)
    evidence.activate(optimization)
    opt_mesh = np.array([vertex.co[:] for vertex in optimization.data.vertices])
    opt_step = optimization['qc_optimization_step']
    for child in (opt_label, leaders(optimization)[json.loads(opt_label['qc_annotation'])['id']][0]):
        material = child.data.materials[0]
        child.data.materials[0] = None
        try:
            errors['corrupt_' + child.type.lower()] = reject(
                lambda: bpy.ops.qcblender.optimization_step(direction='GOTO', step=1), optimization)
            assert optimization['qc_optimization_step'] == opt_step
            np.testing.assert_array_equal([vertex.co[:] for vertex in optimization.data.vertices], opt_mesh)
            assert snapshot(optimization) == opt_before
        finally:
            child.data.materials[0] = material
    assert bpy.ops.qcblender.optimization_step(direction='GOTO', step=1) == {'FINISHED'}
    assert_values(optimization)
    assert json.loads(opt_label['qc_annotation'])['geometry']['step'] == 1
    assert snapshot(optimization) != opt_before
    assert np.linalg.norm(np.array(opt_label.location) - opt_anchor) > 1e-6
    assert bpy.ops.qcblender.optimization_step(direction='GOTO', step=4) == {'FINISHED'}
    assert_values(optimization)
    assert snapshot(optimization) == opt_before
    previous_selection = optimization.get('qc_local_selection_record')
    assert bpy.ops.qcblender.new_current_view() == {'FINISHED'}
    upgraded = bpy.context.object
    upgraded.name = 'MN annotation upgraded optimization'
    assert upgraded['qc_optimization_step'] == 4
    assert upgraded.get('qc_local_selection_record') == previous_selection
    assert snapshot(upgraded) == opt_before
    assert all(labels(upgraded)[key][0].data != labels(optimization)[key][0].data
               for key in labels(optimization))
    assert_values(upgraded)

    irc_label = add(irc, 'DISTANCE', moving_pair(irc, 'irc', 1))[0]
    irc_before = snapshot(irc)
    irc_anchor = np.array(irc_label.location)
    evidence.activate(irc)
    assert bpy.ops.qcblender.irc_step(direction='PREV') == {'FINISHED'}
    assert_values(irc)
    assert json.loads(irc_label['qc_annotation'])['geometry']['step'] == 1
    assert snapshot(irc) != irc_before
    assert np.linalg.norm(np.array(irc_label.location) - irc_anchor) > 1e-6
    assert bpy.ops.qcblender.irc_step(direction='NEXT') == {'FINISHED'}
    assert_values(irc)
    assert snapshot(irc) == irc_before
    assert evidence.hashes() == before_arrays

    # The second real Gaussian job has the frequency modes used by its GN displacement.
    mn_spec = importlib.util.spec_from_file_location('mn_evidence', ROOT / 'tools/verify_mn_parameters.py')
    mn_evidence = importlib.util.module_from_spec(mn_spec)
    mn_spec.loader.exec_module(mn_evidence)
    directory = mn_evidence.import_source(input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT), job_index=1)
    water = module('blender.views').atom_view(directory)
    water.name = 'MN real water vibration Job 2'
    vibration_arrays = evidence.hashes()
    assert water.get('qc_optimization_step') is None and len(water.qc_settings.modes) > 1
    water_label = add(water, 'DISTANCE', '1,2')[0]
    water_before = snapshot(water)
    source_positions, source_record = module('blender.geometry').current_geometry(water)
    initial_scale = water.scale.copy()
    water.scale = (1.7, .65, 1.25)
    assert_values(water)
    assert snapshot(water) == water_before
    np.testing.assert_array_equal(module('blender.geometry').current_geometry(water)[0], source_positions)
    water.scale = initial_scale
    water.qc_settings.active_mode = 1
    data = module('data').load_dataset(bpy.path.abspath(water['qc_dataset']))
    assert np.max(np.abs(data.arrays['mode_display_displacements'][1])) > 0
    modifier, sockets = evidence.controls(water)
    modifier[sockets['Amplitude (angstrom)']] = .75
    modifier[sockets['Animate']] = False
    modifier[sockets['Phase']] = 0.
    still = evaluated_vertices(water)
    modifier[sockets['Phase']] = math.pi / 2
    displaced = evaluated_vertices(water)
    assert still.shape == displaced.shape and len(still) > 0
    assert np.max(np.linalg.norm(displaced - still, axis=1)) > 1e-5
    modifier[sockets['Animate']] = True
    assert_values(water)
    assert snapshot(water) == water_before
    modifier[sockets['Animate']] = False
    assert json.loads(water_label['qc_annotation'])['geometry'] == source_record
    np.testing.assert_array_equal(module('blender.geometry').current_geometry(water)[0], source_positions)
    assert evidence.hashes() == vibration_arrays

    report = {'checks': {'four_kinds_and_defaults': 'Passed', 'source_values_and_transform': 'Passed',
        'optimization_and_irc_steps': 'Passed', 'copy_edit_remove': 'Passed',
        'upgrade_step_selection_labels': 'Passed', 'error_transaction': 'Passed',
        'parameter_copy_preserves_labels': 'Passed',
        'style_visibility_and_face_camera': 'Passed',
        'corrupt_annotation_step_transaction': 'Passed',
        'nonuniform_scale_science_invariant': 'Passed',
        'real_vibration_science_invariant': 'Passed',
        'synthetic_degenerate_fixture': 'Passed'}, 'errors': errors,
        'annotations': {obj.name: snapshot(obj) for obj in (methane, optimization, upgraded, irc, water)},
        'render_pixels': evidence.render(out / 'evidence.png')}
    evidence.save_evidence(out, report)
    return report


def check_reopen(out):
    report = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
    for name, expected in report['annotations'].items():
        owner = bpy.data.objects[name]
        assert snapshot(owner) == expected, name
        assert_values(owner)
    return evidence.check_reopen(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', choices=['annotations', 'reopen'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.preferences.addon_enable(module=evidence.MODULE)
    assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(args.out.parent.resolve())
    result = {'annotations': check_annotations, 'reopen': check_reopen}[args.check](args.out)
    print(json.dumps(result, ensure_ascii=False))
