"""Record real-source integration convergence and charged-system ESP asymptotics."""
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'outputs/science')]
os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ['SystemRoot'] + '/System32'

import numpy as np
from qcblender.data import BOHR_ANGSTROM
from qcblender.evaluate import Grid, evaluate_field, evaluate_points
from qcblender.readers import read_source

data = read_source(ROOT / 'tests/data/iodata/li_h_3-21G_hf_g09.fchk')
center = data.arrays['positions'].mean(axis=0) / BOHR_ANGSTROM
records = []
for radius, spacing in [(8, .4), (8, .2), (8, .1), (12, .2), (16, .2)]:
    shape = [round(2 * radius / spacing) + 1] * 3
    grid = Grid((center - radius) * BOHR_ANGSTROM, np.eye(3) * spacing * BOHR_ANGSTROM, shape)
    record = {'radius_bohr': radius, 'spacing_bohr': spacing, 'shape': shape}
    started = time.perf_counter()
    for quantity, expected in [('electron_number_density', 3.), ('spin_density', 1.)]:
        field = evaluate_field(data, grid, quantity, memory_mb=512)
        value = float(field.arrays['field_values'].sum() * spacing**3)
        record[quantity] = {'integral': value, 'target': expected, 'error': abs(value - expected)}
    record['seconds'] = time.perf_counter() - started
    records.append(record)
    print(json.dumps(record), flush=True)
radii = np.array([50., 100., 200.])
points = (center + radii[:, None] * np.array([1., 0., 0.])) * BOHR_ANGSTROM
esp, valid = evaluate_points(data, points, 'electrostatic_potential')
scaled = esp * radii
report = {'status': 'Measured', 'source': data.metadata['source'], 'python': platform.python_version(),
          'cpu': platform.processor(), 'integration': records,
          'far_field': {'radii_bohr': radii.tolist(), 'r_times_esp': scaled.tolist(), 'target': data.metadata['charge']}}
path = ROOT / 'outputs/scientific-convergence.json'
path.write_text(json.dumps(report, indent=2), encoding='utf-8')
assert valid.all() and np.all(esp > 0)
assert abs(scaled[-1] - 1) < .01
assert abs(scaled[-1] - 1) < abs(scaled[0] - 1)
for quantity in ('electron_number_density', 'spin_density'):
    assert records[2][quantity]['error'] < records[0][quantity]['error']
    assert records[-1][quantity]['error'] < .005
report['status'] = 'Passed'
path.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report['far_field']), flush=True)
