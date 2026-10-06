"""Rebuild the numeric MO Cube used by comparison and import checks."""
import hashlib
import json
from pathlib import Path


def comparison_source(root):
    root = Path(root)
    directory = root / 'validation/shared/data/regression/chemtools'
    name = 'ch4_uhf_ccpvdz.fchk'
    record = next(row for row in json.loads((directory / 'sources.json').read_text(encoding='utf-8'))
                  if row['file'] == name)
    path = directory / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError('Comparison wavefunction checksum mismatch: ' + str(path))
    return path


def write_comparison_cube(data, destination):
    import numpy as np
    from qcblender.data import BOHR_ANGSTROM
    from qcblender.cube import read_cube

    path = Path(destination)
    if path.exists():
        raise FileExistsError('Choose an unused comparison Cube path: ' + str(path))
    field = data.metadata['fields'][0]
    if field['quantity'] != 'orbital_amplitude' or field['unit'] != 'bohr^-3/2':
        raise ValueError('Comparison input requires an orbital amplitude in bohr^-3/2')
    if not data.arrays[field['valid_mask']].all():
        raise ValueError('Comparison Cube requires a fully valid grid')
    path.parent.mkdir(parents=True, exist_ok=True)
    numbers = data.arrays['atomic_numbers']
    positions = data.arrays['positions'] / BOHR_ANGSTROM
    origin = np.asarray(field['origin']) / BOHR_ANGSTROM
    steps = np.asarray(field['steps']) / BOHR_ANGSTROM
    with path.open('x', encoding='ascii', newline='\n') as stream:
        stream.write('QCBlender comparison: CH4 UHF/cc-pVDZ alpha MO 8\n'
                     'Signed amplitude [bohr^-3/2]; scientific grid unchanged\n')
        stream.write(f'{-len(numbers):5d} ' + ' '.join(f'{v:.15e}' for v in origin) + '\n')
        for count, step in zip(field['shape'], steps):
            stream.write(f'{count:5d} ' + ' '.join(f'{v:.15e}' for v in step) + '\n')
        for number, position in zip(numbers, positions):
            stream.write(f'{number:5d} {float(number):.8f} ' + ' '.join(f'{v:.15e}' for v in position) + '\n')
        stream.write('1 8\n')
        values = data.arrays[field['array']].ravel()
        for start in range(0, len(values), 6):
            stream.write(' '.join(f'{v:.15e}' for v in values[start:start+6]) + '\n')
    reread = read_cube(path)
    np.testing.assert_allclose(reread.arrays['cube_0'], data.arrays[field['array']], rtol=5e-15, atol=1e-16)
    np.testing.assert_allclose(reread.metadata['fields'][0]['origin'], field['origin'], atol=1e-14)
    np.testing.assert_allclose(reread.metadata['fields'][0]['steps'], field['steps'], atol=1e-14)
    return path


def prepare_comparison_cube(reference_root, output_directory):
    import numpy as np
    from qcblender.readers import read_source
    from qcblender.evaluate import Grid, evaluate_field

    source = comparison_source(reference_root)
    grid = Grid([-3, -3, -3], np.eye(3) * .2, (31, 31, 31))
    data = evaluate_field(read_source(source), grid, 'orbital_amplitude', spin='alpha', orbital=8)
    return write_comparison_cube(data, Path(output_directory) / 'ch4-alpha-mo8.cube')
