"""Run the explicit standard-library boundary suite without site-packages."""
import argparse
import json
from pathlib import Path
import sys
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/ci/stdlib.json')
    args = parser.parse_args()
    sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
    from tools.test_profiles import STDLIB
    (ROOT / 'outputs').mkdir(exist_ok=True)
    suite = unittest.defaultTestLoader.loadTestsFromNames(STDLIB)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    passed = result.wasSuccessful() and not result.skipped
    report = dict(status='Passed' if passed else 'Failed', suite='stdlib',
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  modules=list(STDLIB), tests=result.testsRun, failures=len(result.failures),
                  errors=len(result.errors), skipped=len(result.skipped))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(not passed)


if __name__ == '__main__':
    main()
