"""Run with Blender --background --python this_file -- --root ... --sample ... --out ...

sample is the catalog root containing tests/data/local-inputs.json. No workers run.
"""
import argparse
import importlib
import json
from pathlib import Path
import sys
import subprocess
from types import SimpleNamespace

import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--sample', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
sys.path[:0] = [str(args.root), str(args.sample / 'outputs/science')]
import qcblender
from tools.local_inputs import input_path
from qcblender.data import save_dataset
from qcblender.gaussian_log import read_log
from qcblender.irc import import_irc
from qcblender.readers import read_source
from qcblender.blender.views import bind

qcblender.register()
args.out.mkdir(parents=True, exist_ok=True)
source = input_path('log-examples/water_neutral_nbo_opt_freq.out', args.sample)
dynamic = read_log(source, 0)
static = read_log(source, 1)
irc = import_irc(input_path('sop/c10-c13/peroxide-irc-pyscf', args.sample) / 'steps.csv')
xyz = args.out / 'frames.xyz'
xyz.write_text('1\nFrame one\nH 0 0 0\n1\nFrame two\nH 0 0 1\n', encoding='utf-8')
trajectory = read_source(xyz)
datasets = [('optimization', dynamic), ('irc', irc), ('xyz', trajectory)]
for name, data in datasets + [('static', static)]:
    save_dataset(data, args.out / name)


def object_for(name, directory, data):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    bind(obj, directory, data)
    obj['qc_view_kind'] = 'field'
    obj['qc_field'] = '{"quantity":"electrostatic_potential"}'
    obj['qc_analysis_role'] = 'ets_nocv'
    bpy.context.view_layer.objects.active = obj
    return obj


results = []
operator_names = ('import_paired_field', 'import_nbo', 'import_aim_analysis',
                  'import_esp_analysis', 'import_ets_nocv')
for name, data in datasets:
    root = object_for(name, args.out / name, data)
    child = object_for(name + ' static child', args.out / 'static', static)
    child.parent = root
    for target in (root, child):
        bpy.context.view_layer.objects.active = target
        for operator_name in operator_names:
            before = len(bpy.data.objects)
            operator = getattr(bpy.ops.qcblender, operator_name)
            assert not operator.poll(), (target.name, operator_name, 'dynamic reference was eligible')
            try:
                operator()
            except RuntimeError as error:
                assert '独立' in str(error), str(error)
            else:
                raise AssertionError('Dynamic operator did not refuse execution: ' + operator_name)
            assert len(bpy.data.objects) == before
            results.append({'object': target.name, 'operator': operator_name, 'status': 'Passed'})

        # Also exercise the operator bodies, independently of Blender poll.
        for module, cls_name in [('external_fields', 'QCBLENDER_OT_import_paired_field'),
                                 ('nbo', 'QCBLENDER_OT_import_nbo'),
                                 ('nocv', 'QCBLENDER_OT_import_nocv')]:
            cls = getattr(importlib.import_module('qcblender.blender.' + module), cls_name)
            before = len(bpy.data.objects)
            try:
                cls.begin(SimpleNamespace(), bpy.context)
            except ValueError as error:
                assert '独立' in str(error), str(error)
            else:
                raise AssertionError('Dynamic reference reached worker start: ' + module)
            assert len(bpy.data.objects) == before
            results.append({'object': target.name, 'begin': module, 'status': 'Passed'})

# Helpers are deliberately imported after the baseline operator checks so this
# script can first reproduce the original poll failure on an unmodified tree.
from qcblender.blender.static_reference import capture_reference, validate_reference
child.parent = None
snapshot = capture_reference(child)
assert validate_reference(snapshot) == child
for operator_name in operator_names:
    assert getattr(bpy.ops.qcblender, operator_name).poll(), operator_name
child.name = 'renamed static reference'
assert validate_reference(snapshot) == child
results.append({'check': 'static reference and rename preserve identity', 'status': 'Passed'})


def rejected(mutate, restore, label):
    before = len(bpy.data.objects)
    mutate()
    try:
        validate_reference(snapshot)
    except (ValueError, OSError):
        pass
    else:
        raise AssertionError('Changed reference accepted: ' + label)
    for module, cls_name in [('external_fields', 'QCBLENDER_OT_import_paired_field'),
                             ('nbo', 'QCBLENDER_OT_import_nbo'),
                             ('nocv', 'QCBLENDER_OT_import_nocv')]:
        cls = getattr(importlib.import_module('qcblender.blender.' + module), cls_name)
        try:
            cls.accept(SimpleNamespace(_reference_snapshot=snapshot), bpy.context, {})
        except (ValueError, OSError):
            pass
        else:
            raise AssertionError('Changed reference reached scene creation: ' + module)
    assert len(bpy.data.objects) == before
    restore()
    results.append({'check': label, 'status': 'Passed'})


saved_binding = child['qc_dataset']
rejected(lambda: child.__setitem__('qc_dataset', str(args.out / 'optimization')),
         lambda: child.__setitem__('qc_dataset', saved_binding), 'path binding changed')
rejected(lambda: setattr(child, 'parent', root), lambda: setattr(child, 'parent', None),
         'dynamic ancestor attached')
manifest = args.out / 'static/manifest.json'
raw = manifest.read_bytes()
rejected(lambda: manifest.write_bytes(raw + b' '), lambda: manifest.write_bytes(raw),
         'manifest digest changed')
old_name = child.name
bpy.data.objects.remove(child, do_unlink=True)
replacement = object_for(old_name, args.out / 'static', static)
try:
    validate_reference(snapshot)
except ValueError:
    pass
else:
    raise AssertionError('Same-name replacement accepted')
results.append({'check': 'deleted object and same-name replacement', 'status': 'Passed'})
report = {'status': 'Passed', 'checks': results,
          'source_commit': subprocess.check_output(['git', '-C', str(args.root), 'rev-parse', 'HEAD'],
                                                   text=True).strip()}
(args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('STATIC_REFERENCE_NATIVE_PASSED:', len(results))
