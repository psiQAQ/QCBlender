"""Check installed annotation defaults and previews with real source data and RNA."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback
from types import SimpleNamespace

import bpy
import numpy as np
from mathutils import Euler, Vector


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def labels(owner):
    return [child for child in owner.children if child.type == 'FONT' and child.get('qc_annotation')]


def state(owner, geometry):
    positions, record = geometry.current_geometry(owner)
    return {'positions': positions.tolist(), 'record': record,
            'labels': sorted([json.loads(child['qc_annotation'])['id'], child.data.body,
                              child.data.size, list(child.location)] for child in labels(owner))}


def run(args, report):
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    from tools.dev_workflow.blender_ops import _import, _object, _module
    annotation = _module('blender.annotations')
    geometry = _module('blender.geometry')
    package = Path(importlib.import_module(annotation.__package__).__file__).parent.parent
    report['installed_sources'] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                                   for name in ('blender/annotations.py', 'measurements.py', 'translations_annotations.py')}
    if args.reopen:
        expected = json.loads(bpy.context.scene['qc_annotation_dialog_expected'])
        for name, saved in expected.items():
            require(state(bpy.data.objects[name], geometry) == saved, 'Cold read differs for ' + name)
        report['cold_reopen'] = 'Passed'
        return
    result = _import({'source': str(args.source), 'name': 'Annotation UI source'})
    owner = _object(result['object'])
    before = geometry.current_geometry(owner)[0].copy()
    parent = bpy.data.objects.new('Annotation UI parent', None)
    bpy.context.collection.objects.link(parent)
    parent.location = (10, -3, 2)
    parent.rotation_euler = Euler((.2, -.3, .4))
    parent.scale = (2, 3, .5)
    owner.parent = parent
    owner.location = (1, 2, 3)
    owner.rotation_euler = Euler((.3, .1, -.2))
    owner.scale = (1.5, .7, 2)
    bpy.context.view_layer.update()
    bpy.types.Scene.qc_dialog_test_slots = bpy.props.CollectionProperty(type=annotation.QCAnnotationAtomInput)
    try:
        operator = SimpleNamespace(atom_inputs=bpy.context.scene.qc_dialog_test_slots)
        positions, _ = geometry.current_geometry(owner)
        annotation._init_atom_inputs(operator, [1, 2, 3, 4], len(positions))
        annotation._init_atom_preview(operator, owner, positions)
        world = np.asarray(parent.matrix_world) @ np.asarray(owner.matrix_basis) @ np.append(positions[0], 1)
        expected = f'({world[0]:.2f}, {world[1]:.2f}, {world[2]:.2f})'
        require(operator.atom_inputs[0].preview.endswith(expected), 'Parent/world coordinates differ')
        operator.swap_pair = '1'
        require(annotation._check_atom_inputs(operator), 'Swap did not request redraw')
        require(operator.atom_inputs[0].number == 2, 'Swap changed the wrong input')
        operator.atom_inputs[0].number = len(positions) + 10
        require(annotation._check_atom_inputs(operator), 'Clamp did not request redraw')
        require(operator.atom_inputs[0].number == len(positions), 'Input was not clamped')
        require(bool(operator.atom_inputs[0].preview), 'Preview was lost after clamp')
        report['native_rna_world_preview_swap_clamp'] = 'Passed'
    finally:
        del bpy.types.Scene.qc_dialog_test_slots
    for kind, numbers in [('ATOM', '1'), ('DISTANCE', '1,2'), ('ANGLE', '1,2,3'), ('DIHEDRAL', '1,2,3,4')]:
        require(bpy.ops.qcblender.add_annotation(kind=kind, atoms=numbers) == {'FINISHED'}, 'Creation failed: ' + kind)
        child = next(child for child in labels(owner) if json.loads(child['qc_annotation'])['kind'] == kind)
        require(child.data.size == .5, 'Unexpected default size: ' + kind)
        if kind == 'ATOM':
            require(child.data.body == 'O', 'Atom text is not the element alone')
            entry = json.loads(child['qc_annotation'])
            require(bpy.ops.qcblender.edit_annotation(annotation_id=entry['id'], size=.16,
                    prefix_mode='CUSTOM', prefix='氧：', offset=(.4, .5, .6)) == {'FINISHED'}, 'Atom edit failed')
            require(child.data.body == '氧：O', 'Custom atom prefix differs')
    annotation.update_annotations(owner, *geometry.current_geometry(owner))
    atom = next(child for child in labels(owner) if json.loads(child['qc_annotation'])['kind'] == 'ATOM')
    require(abs(atom.data.size - .16) < 1e-7, 'Refresh changed saved size')
    require(atom.data.body == '氧：O', 'Refresh changed custom prefix')
    np.testing.assert_array_equal(before, geometry.current_geometry(owner)[0])
    report['four_defaults_atom_text_custom_prefix_saved_size_science'] = 'Passed'
    multi = _object(_import({'source': str(root / 'validation/shared/data/public/P06/p04-three-frames.xyz'),
                             'name': 'Annotation UI trajectory'})['object'])
    require(bpy.ops.qcblender.add_annotation(kind='ATOM', atoms='1') == {'FINISHED'}, 'Trajectory atom creation failed')
    require(bpy.ops.qcblender.trajectory_frame(frame=3) == {'FINISHED'}, 'Frame change failed')
    positions, record = geometry.current_geometry(multi)
    require(record['step'] == 3, 'Wrong trajectory frame')
    bpy.types.Scene.qc_dialog_test_slots = bpy.props.CollectionProperty(type=annotation.QCAnnotationAtomInput)
    try:
        operator = SimpleNamespace(atom_inputs=bpy.context.scene.qc_dialog_test_slots)
        annotation._init_atom_inputs(operator, [1], len(positions))
        annotation._init_atom_preview(operator, multi, positions)
        point = multi.matrix_world @ Vector(positions[0])
        require(operator.atom_inputs[0].preview.endswith(f'({point.x:.2f}, {point.y:.2f}, {point.z:.2f})'),
                'Preview used an old frame')
    finally:
        del bpy.types.Scene.qc_dialog_test_slots
    report['current_xyz_frame_preview'] = 'Passed'
    _object(owner.name)
    bpy.context.scene['qc_annotation_dialog_expected'] = json.dumps({obj.name: state(obj, geometry) for obj in (owner, multi)})
    output = args.output / 'annotation-ui.blend'
    _module('blender.project').save_project(output)
    report['saved_project'] = str(output)
    report['self_contained_save'] = 'Passed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reopen', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.output.mkdir(parents=True, exist_ok=True)
    report = {'status': 'Failed', 'blender': bpy.app.version_string, 'gui': 'Not Run'}
    try:
        run(args, report)
        report['status'] = 'Passed'
    except Exception:
        report['error'] = traceback.format_exc()
        raise
    finally:
        name = 'native-reopen.json' if args.reopen else 'native.json'
        (args.output / name).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
