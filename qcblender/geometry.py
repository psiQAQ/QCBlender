"""Select real calculation coordinates without display transforms or vibrations."""
import numpy as np


def scientific_geometry(data, kind='source', step=None):
    meta, arrays = data.metadata, data.arrays
    if meta.get('coordinate_unit') != 'angstrom':
        raise ValueError('Scientific coordinates must be recorded in angstrom')
    record = {'kind': kind, 'step': step, 'coordinate_unit': 'angstrom',
              'source_sha256': meta['source']['sha256'],
              'selected_job': meta.get('selected_job')}
    if kind == 'source':
        if step is not None:
            raise ValueError('Static source geometry has no trajectory step')
        positions = arrays['positions']
    elif kind in ('optimization', 'irc'):
        if type(step) is not int or step < 1:
            raise ValueError('Calculation step must be a positive integer')
        if kind == 'optimization':
            trajectory = meta.get('optimization', {})
            if trajectory.get('status') != 'available':
                raise ValueError('Optimization trajectory is not available')
            positions = arrays[trajectory['array']]
            records = trajectory['steps']
        else:
            analysis = meta.get('analysis', {})
            if analysis.get('kind') != 'IRC':
                raise ValueError('Dataset is not an IRC path')
            positions = arrays['irc_positions']
            records = analysis['steps']
        if len(positions) != len(records) or step > len(positions):
            raise ValueError('Calculation step is outside the recorded trajectory')
        record['step_record'] = records[step - 1]
        positions = positions[step - 1]
    else:
        raise ValueError('Unknown scientific geometry kind')
    positions = np.array(positions, dtype=np.float64, copy=True)
    if positions.shape != (len(arrays['atomic_numbers']), 3) or not np.isfinite(positions).all():
        raise ValueError('Scientific atom coordinates are missing or invalid')
    positions.flags.writeable = False
    return positions, record
