"""Run explicitly selected existing test modules, without restoring dependencies."""
import argparse
import json
from pathlib import Path
import sys
import unittest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--site', type=Path)
    parser.add_argument('--module', action='append', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.repo), str(args.repo / 'tests')] + ([str(args.site)] if args.site else [])
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(args.module))
    passed = result.wasSuccessful() and not result.skipped
    report = dict(status='Passed' if passed else 'Failed', modules=args.module, tests=result.testsRun,
                  failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    raise SystemExit(not passed)


if __name__ == '__main__':
    main()
