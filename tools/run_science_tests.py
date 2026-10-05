"""Run numerical tests in a fresh Blender Python with isolated wheel imports."""
import argparse
import json
import os
from pathlib import Path
import sys
import subprocess
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--site', type=Path, default=ROOT / 'outputs/science')
parser.add_argument('--output', type=Path, default=ROOT / 'outputs/science-reference.json')
parser.add_argument('--suite', choices=('full', 'public-core'), default='full')
args = parser.parse_args()
(ROOT / 'outputs').mkdir(exist_ok=True)
git = shutil.which('git')
if git is None:
    raise RuntimeError('Git is required to bind numerical reports to their source commit')
os.environ['PATH'] = os.pathsep.join([str(Path(sys.executable).parent),
                                     os.environ.get('SystemRoot', 'C:/Windows') + '/System32'])
sys.path[:0] = [str(ROOT), str(args.site.resolve()), str(ROOT / 'tests')]
if args.suite == 'public-core':
    from tools.test_profiles import PUBLIC_SCIENCE
    suite = unittest.defaultTestLoader.loadTestsFromNames(PUBLIC_SCIENCE)
else:
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_science*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
from test_science_reference import METRICS
passed = result.wasSuccessful() and (args.suite != 'public-core' or not result.skipped)
report = {'status': 'Passed' if passed else 'Failed', 'suite': args.suite,
          'modules': list(PUBLIC_SCIENCE) if args.suite == 'public-core' else None,
          'source_commit': subprocess.check_output([git, 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
          'skipped': len(result.skipped), 'metrics': METRICS}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(not passed)
