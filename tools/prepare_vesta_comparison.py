"""Rebuild the comparison MO Cube from the centralized wavefunction."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--reference-root', type=Path, default=ROOT)
    args = parser.parse_args()
    sys.path[:0] = [str(ROOT), str(args.reference_root / 'modules/science')]
    from tools.comparison_fixture import prepare_comparison_cube, comparison_source
    from qcblender.cube import read_cube

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    path = prepare_comparison_cube(args.reference_root, output)
    field = read_cube(path).metadata['fields'][0]
    record = {'status': 'Passed', 'source_fchk_sha256': hashlib.sha256(comparison_source(args.reference_root).read_bytes()).hexdigest(),
              'cube_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'quantity': 'orbital_amplitude', 'unit': 'bohr^-3/2', 'isovalues': [-.05, .05],
              'shape': field['shape'], 'steps_angstrom': field['steps'], 'origin_angstrom': field['origin'],
              'cube_roundtrip': 'Passed', 'external_renderer': 'Not Run', 'human_acceptance': 'Not Run'}
    (output / 'input.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
