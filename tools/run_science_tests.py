"""Run numerical tests in a fresh Blender Python with isolated wheel imports."""
import argparse
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--site', type=Path, default=ROOT / 'outputs/science')
parser.add_argument('--output', type=Path, default=ROOT / 'outputs/science-reference.json')
args = parser.parse_args()
os.environ['PATH'] = os.pathsep.join([str(Path(sys.executable).parent),
                                     os.environ.get('SystemRoot', 'C:/Windows') + '/System32'])
sys.path[:0] = [str(ROOT), str(args.site.resolve())]
suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_science*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
from test_science_reference import METRICS
report = {'status': 'Passed' if result.wasSuccessful() else 'Failed',
          'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
          'metrics': METRICS}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(not result.wasSuccessful())
