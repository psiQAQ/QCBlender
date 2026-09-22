"""Run storage regressions inside the Blender process with its Windows path behavior."""
import json
from pathlib import Path
import sys
import unittest

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
suite = unittest.defaultTestLoader.loadTestsFromName('test_science_project')
result = unittest.TextTestRunner(verbosity=2).run(suite)
report = {'status': 'Passed' if result.wasSuccessful() else 'Failed',
          'blender': bpy.app.version_string, 'tests': result.testsRun,
          'scope': 'Real filesystem: long cache array paths, copy/reuse/archive and corruption rejection'}
output = ROOT / 'outputs/acceptance/storage-paths.json'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
if not result.wasSuccessful():
    raise RuntimeError('Blender storage regression failed')
