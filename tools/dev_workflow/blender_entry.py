"""Blender --python entry point for one fixed development operation."""
import argparse
import json
import os
from pathlib import Path
import sys
import traceback


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--owned-process', action='store_true',
                        help='Bind a request to this newly launched CLI process')
    args = parser.parse_args(argv if argv is not None else sys.argv[sys.argv.index('--') + 1:])
    request = {}
    try:
        request = json.loads(args.request.read_text(encoding='utf-8'))
        if args.owned_process:
            request['expected_pid'] = os.getpid()
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from tools.dev_workflow.blender_ops import dispatch
        report = dispatch(request)
        code = 0
    except Exception as error:
        report = {'status': 'Failed', 'action': request.get('action') if isinstance(request, dict) else None, 'pid': os.getpid(),
                  'error': f'{type(error).__name__}: {error}', 'traceback': traceback.format_exc()}
        code = 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return code


if __name__ == '__main__':
    if main():
        raise SystemExit(1)
