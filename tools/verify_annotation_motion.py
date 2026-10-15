"""Installed annotation updates on real XYZ, IRC and optimization source steps."""
import argparse
import hashlib
import importlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path

MODULE = 'bl_ext.user_default.qcblender'


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def activate(obj):
    module('blender.layers').activate(bpy.context, obj)


def import_atoms(path):
    job = module('blender.jobs').Job('import', source=str(path), job_index=0)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return module('blender.views').atom_view(job.directory / 'dataset')
        time.sleep(.1)
    job.cancel()
    raise TimeoutError('Scientific input import')


def arrays(owner):
    data = module('data').load_dataset(bpy.path.abspath(owner['qc_dataset']))
    return {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in data.arrays.items()}


def independent_angle(kind, points):
    if kind == 'DISTANCE':
        return float(np.linalg.norm(points[1] - points[0]))
    if kind == 'ANGLE':
        a, b = points[0] - points[1], points[2] - points[1]
        return float(np.degrees(np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b))))
    axis = points[2] - points[1]
    axis /= np.linalg.norm(axis)
    a, b = points[0] - points[1], points[3] - points[2]
    a -= np.dot(a, axis) * axis
    b -= np.dot(b, axis) * axis
    angle = float(np.degrees(np.arctan2(np.dot(np.cross(a, b), axis), np.dot(a, b))))
    return 180. if angle <= -180. else angle


def verify(owner):
    positions, geometry = module('blender.geometry').current_geometry(owner)
    result = {}
    for obj in owner.children:
        if 'qc_annotation' not in obj:
            continue
        record = json.loads(obj['qc_annotation'])
        assert record['geometry'] == geometry
        points = positions[np.asarray(record['source_atom_numbers']) - 1]
        if record['kind'] != 'ATOM':
            np.testing.assert_allclose(record['value'], independent_angle(record['kind'], points), atol=1e-8)
        role = record['role']
        if role == 'LABEL':
            np.testing.assert_allclose(obj.location, points.mean(axis=0) + record['offset'], atol=2e-6)
            result[record['kind']] = {'body': obj.data.body, 'value': record['value'], 'geometry': geometry}
        elif role == 'DASH':
            np.testing.assert_allclose(obj.data.splines[0].points[0].co[:3], points[0], atol=2e-6)
            np.testing.assert_allclose(obj.data.splines[-1].points[-1].co[:3], points[1], atol=2e-6)
        elif role == 'ARC':
            if not obj.data.splines:
                assert abs(record['value']) < 1e-8 and obj.hide_render
                continue
            vertices = np.array([point.co[:3] for point in obj.data.splines[0].points])
            center = points[1] if record['kind'] == 'ANGLE' else (points[1] + points[2]) / 2
            np.testing.assert_allclose(np.linalg.norm(vertices - center, axis=1), record['arc_radius'], atol=2e-6)
            if record['kind'] == 'DIHEDRAL':
                axis = points[2] - points[1]
                axis /= np.linalg.norm(axis)
                np.testing.assert_allclose((vertices - center) @ axis, 0., atol=2e-6)
        elif role in ('PLANE_A', 'PLANE_B'):
            expected = points[:3] if role == 'PLANE_A' else points[1:]
            np.testing.assert_allclose([vertex.co[:] for vertex in obj.data.vertices], expected, atol=2e-6)
    return result


def add_all(owner):
    activate(owner)
    count = len(owner.data.vertices)
    positions, _ = module('blender.geometry').current_geometry(owner)
    kinds = [('ATOM', [1]), ('DISTANCE', [1, 2]), ('ANGLE', [1, 2, 3])]
    if count >= 4:
        numbers = next(numbers for numbers in itertools.permutations(range(1, min(count, 8) + 1), 4)
                       if np.linalg.norm(np.cross(positions[numbers[0]-1] - positions[numbers[1]-1],
                                                  positions[numbers[2]-1] - positions[numbers[1]-1])) > 1e-6
                       and np.linalg.norm(np.cross(positions[numbers[3]-1] - positions[numbers[2]-1],
                                                   positions[numbers[2]-1] - positions[numbers[1]-1])) > 1e-6)
        kinds.append(('DIHEDRAL', numbers))
    for kind, numbers in kinds:
        assert bpy.ops.qcblender.add_annotation(kind=kind, atoms=','.join(map(str, numbers))) == {'FINISHED'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.output.mkdir(parents=True, exist_ok=True)
    bpy.ops.preferences.addon_enable(module=MODULE)
    result = {'status': 'Running', 'checks': {}, 'blender': bpy.app.version_string}
    try:
        xyz = import_atoms(REFERENCE / 'validation/shared/data/public/P06/p04-three-frames.xyz')
        module('blender.trajectory').initialize_trajectory(xyz, module('data').load_dataset(bpy.path.abspath(xyz['qc_dataset'])))
        activate(xyz)
        add_all(xyz)
        before = arrays(xyz)
        frames = []
        for index in (1, 2, 3, 1):
            assert bpy.ops.qcblender.trajectory_frame(direction='GOTO', frame=index) == {'FINISHED'}
            frames.append(verify(xyz))
        assert arrays(xyz) == before
        result['checks']['xyz'] = frames
        assert bpy.ops.qcblender.import_irc_path(manifest_path=str(REFERENCE / 'validation/shared/data/public/P04/steps.csv')) == {'FINISHED'}
        irc = bpy.context.object
        add_all(irc)
        before = arrays(irc)
        steps = [verify(irc)]
        for direction in ('NEXT', 'NEXT', 'PREV'):
            assert bpy.ops.qcblender.irc_step(direction=direction) == {'FINISHED'}
            steps.append(verify(irc))
        assert arrays(irc) == before
        result['checks']['irc'] = steps
        source = import_atoms(input_path('log-examples/water_neutral_nbo_opt_freq.out', REFERENCE))
        activate(source)
        assert bpy.ops.qcblender.optimization_view() == {'FINISHED'}
        optimization = bpy.context.object
        add_all(optimization)
        before = arrays(optimization)
        steps = []
        for index in (1, 4, 2, 1):
            assert bpy.ops.qcblender.optimization_step(direction='GOTO', step=index) == {'FINISHED'}
            steps.append(verify(optimization))
        assert arrays(optimization) == before
        result['checks']['optimization'] = steps
        target = args.output / 'motion.blend'
        assert bpy.ops.qcblender.save_project(filepath=str(target)) == {'FINISHED'}
        result.update(status='Passed', project=str(target))
    except Exception as error:
        result.update(status='Failed', error=repr(error))
        raise
    finally:
        (args.output / 'motion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
