"""Assert that a native-unreadable VDB is rejected before field scene writes.

Run in a fresh Blender with --python-exit-code 1 --python this.py -- --dataset DIR.
The dataset must pass Python array/cache validation while Blender cannot load it.
"""
import argparse
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs/science')]
import qcblender
from qcblender.data import load_dataset, volume_cache
from qcblender.blender.views import field_view

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True, type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
qcblender.register()
data = load_dataset(args.dataset)
cache = volume_cache(args.dataset, data.metadata['fields'][0])
probe = bpy.data.volumes.new('native red probe')
try:
    probe.filepath = str(cache)
    loaded = probe.grids.load()
    reason = probe.grids.error_message
    assert not loaded, 'Fixture must reproduce native VDB load failure'
    print({'native_load': loaded, 'path': str(cache), 'reason': reason})
finally:
    bpy.data.volumes.remove(probe)
before = {name: set(getattr(bpy.data, name).keys())
          for name in ('objects', 'volumes', 'meshes', 'materials', 'node_groups')}
try:
    field_view(args.dataset)
except (ValueError, OSError, RuntimeError) as error:
    after = {name: set(getattr(bpy.data, name).keys()) for name in before}
    print({'field_error': str(error), 'new_datablocks':
           {name: sorted(after[name] - before[name]) for name in before}})
    assert str(cache) in str(error), str(error)
    assert reason in str(error), str(error)
else:
    raise AssertionError('Unreadable VDB accepted and field scene objects created')
after = {name: set(getattr(bpy.data, name).keys()) for name in before}
assert before == after, 'Rejected VDB left scene/datablock side effects'
print('native unreadable field rejection Passed')
