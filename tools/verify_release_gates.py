"""Check a human review record's candidate identity and evidence hashes locally."""

import argparse
import json
from pathlib import Path

from release_candidate import verify_release_gates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--candidate-manifest', type=Path, required=True)
    parser.add_argument('--artifact-id', type=int, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.candidate_manifest.read_text(encoding='utf-8'))
    record = json.loads(args.record.read_text(encoding='utf-8'))
    gates = verify_release_gates(record, manifest, args.artifact_id, args.record.parent)
    report = {'status': 'Passed', 'scope': 'Review record identity and evidence consistency; review decisions are human',
              'candidate_run_id': manifest['candidate_run_id'], 'artifact_id': args.artifact_id,
              'extension_sha256': manifest['files']['extension']['sha256'], 'gates': gates,
              'public_readiness': ('Failed' if any(gate['status'] == 'Failed' for gate in gates.values()) else
                                   'Passed' if all(gate['status'] == 'Passed' for gate in gates.values()) else 'Not Run')}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
