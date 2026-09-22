"""Export the qualified MO field unchanged to a shared Gaussian Cube comparison input."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs/science')]
from qcblender.data import BOHR_ANGSTROM, load_dataset
from qcblender.cube import read_cube

OUT = ROOT / 'outputs/vesta-comparison'
OUT.mkdir(parents=True, exist_ok=True)
root = ROOT / 'outputs/acceptance/moved 中文 path/mo8.qcdata'
scene = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
for relative in scene['datasets']:
    data = load_dataset(root / relative)
    if data.metadata.get('fields') and data.metadata['fields'][0]['quantity'] == 'orbital_amplitude':
        break
else:
    raise AssertionError('Generate the qualified MO project first')
field = data.metadata['fields'][0]
assert data.arrays[field['valid_mask']].all()
assert field['unit'] == 'bohr^-3/2'
numbers, positions = data.arrays['atomic_numbers'], data.arrays['positions'] / BOHR_ANGSTROM
origin, steps = np.array(field['origin']) / BOHR_ANGSTROM, np.array(field['steps']) / BOHR_ANGSTROM
path = OUT / 'ch4-alpha-mo8.cube'
with path.open('w', encoding='ascii', newline='\n') as stream:
    stream.write('QCBlender comparison: CH4 UHF/cc-pVDZ alpha MO 8\nSigned amplitude [bohr^-3/2]; unchanged qualified scientific grid\n')
    stream.write(f'{-len(numbers):5d} ' + ' '.join(f'{v:.15e}' for v in origin) + '\n')
    for count, step in zip(field['shape'], steps):
        stream.write(f'{count:5d} ' + ' '.join(f'{v:.15e}' for v in step) + '\n')
    for number, position in zip(numbers, positions):
        stream.write(f'{number:5d} {float(number):.8f} ' + ' '.join(f'{v:.15e}' for v in position) + '\n')
    stream.write('1 8\n')
    values = data.arrays[field['array']].ravel()
    for start in range(0, len(values), 6):
        stream.write(' '.join(f'{v:.15e}' for v in values[start:start+6]) + '\n')
reloaded = read_cube(path)
np.testing.assert_allclose(reloaded.arrays['cube_0'], data.arrays[field['array']], rtol=5e-15, atol=1e-16)
np.testing.assert_allclose(reloaded.metadata['fields'][0]['origin'], field['origin'], atol=1e-14)
np.testing.assert_allclose(reloaded.metadata['fields'][0]['steps'], field['steps'], atol=1e-14)
record = {'status': 'Passed', 'source_fchk_sha256': data.metadata['source']['sha256'],
          'source_dataset': relative, 'cube_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'quantity': field['quantity'], 'unit': field['unit'], 'isovalues': [-.05, .05],
          'shape': field['shape'], 'steps_angstrom': field['steps'], 'origin_angstrom': field['origin'],
          'cube_roundtrip': 'Passed', 'independent_field_reference': 'See science-reference.json',
          'external_renderer': 'Not Run', 'human_acceptance': 'Not Run'}
(OUT / 'input.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(record))
