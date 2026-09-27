"""Audit Gaussian optimization frames against printed step and geometry evidence."""
import re

import numpy as np


def optimization_records(lines, start_line, job, parsed):
    from .gaussian_log import NUMBER, number, select_energy

    route = job['route'] or ''
    if not re.search(r'\bopt\b', route, re.I):
        return None

    def unavailable(reason):
        return {'status': 'unavailable', 'reason': reason, 'steps': []}

    if re.search(r'\b(?:irc|scan|oniom|counterpoise|restart|qst2|qst3)\b', route, re.I) or hasattr(parsed, 'scancoords'):
        return unavailable('Scan, restart and composite optimization paths require separate step association')
    markers = [(i, int(m[1])) for i, line in enumerate(lines)
               if (m := re.match(r'\s*Step number\s+(\d+)\s+out of', line))]
    if not markers:
        return unavailable('No explicit optimization step records')
    if len(markers) > 10000:
        return unavailable('Optimization exceeds 10000 steps')
    if [step for _, step in markers] != list(range(1, len(markers) + 1)):
        return unavailable('Optimization step numbers must be unique and contiguous from 1')
    coords = np.asarray(parsed.atomcoords, dtype=np.float64)
    if coords.shape != (len(markers), len(parsed.atomnos), 3) or not np.isfinite(coords).all():
        return unavailable('Parsed geometries do not match the explicit optimization steps')
    orientation = 'Standard orientation:' if any(line.strip() == 'Standard orientation:' for line in lines) else None
    headers = [i for i, line in enumerate(lines) if line.strip() == orientation or
               (orientation is None and line.strip() in ('Input orientation:', 'Z-Matrix orientation:'))]
    records = []
    previous = -1
    for index, (marker, step) in enumerate(markers):
        candidates = [i for i in headers if previous < i < marker]
        if len(candidates) != 1:
            return unavailable(f'Step {step} has no unique printed orientation')
        begin = candidates[0]
        # Audit the cclib frame using the exact printed table, including atom order.
        if begin + 5 >= marker or 'Angstroms' not in lines[begin + 2]:
            return unavailable(f'Step {step} has an unsupported coordinate table')
        rows = []
        end = begin + 5
        while end < marker and lines[end].strip() and set(lines[end].strip()) != {'-'}:
            rows.append(lines[end].split())
            end += 1
        if end >= marker or len(rows) != len(parsed.atomnos) or any(len(row) != 6 for row in rows):
            return unavailable(f'Step {step} has an incomplete coordinate table')
        if ([int(row[0]) for row in rows] != list(range(1, len(rows) + 1)) or
                [int(row[1]) for row in rows] != list(parsed.atomnos)):
            raise ValueError(f'Optimization step {step} changes atom identities or ordering')
        printed = np.array([[number(value) for value in row[-3:]] for row in rows])
        if not np.allclose(printed, coords[index], rtol=0, atol=5e-7):
            return unavailable(f'Step {step} differs from the parsed geometry')
        energies = [e for e in job['energies'] if start_line + begin <= e['line_start'] <= start_line + marker
                    and e['evidence_type'] == 'body']
        selection = select_energy(energies, 'normal')
        energy = next((e for e in energies if e['id'] == selection['record_id']), None)
        if energy:
            energy = dict(energy, geometry_ref=f'{job["id"]}:optimization:{step}',
                          association_status='explicit_optimization_step')
            selection['reason'] = 'Unique target-method energy printed for this step; job status is recorded separately'
        # Per-step energy is an observed result, never a claim of job convergence.
        limit = min([i for i in headers if i > marker] + [len(lines)])
        limit = min(limit, markers[index + 1][0] if index + 1 < len(markers) else len(lines))
        convergence = []
        unit_system = next(({'text': lines[i].strip(), 'line_start': start_line + i}
                            for i in range(marker + 1, limit) if 'All quantities printed in internal units' in lines[i]), None)
        for i in range(marker + 1, limit):
            match = re.match(r'\s*(Maximum Force|RMS\s+Force|Maximum Displacement|RMS\s+Displacement)\s+'
                             r'(' + NUMBER + r')\s+(' + NUMBER + r')\s+(YES|NO)\s*$', lines[i])
            if match:
                label = ' '.join(match[1].split())
                convergence.append({'quantity': label, 'value': number(match[2]),
                    'threshold': number(match[3]), 'converged': match[4] == 'YES',
                    'unit': None, 'line_start': start_line + i})
        status = ('converged' if any('Optimization completed.' in s for s in lines[marker:limit]) else
                  'stopped' if any('Optimization stopped.' in s for s in lines[marker:limit]) else 'not_completed')
        records.append({'step': step, 'job_id': job['id'], 'line_start': start_line + begin,
            'line_end': start_line + limit - 1, 'step_line': start_line + marker,
            'geometry_line_start': start_line + begin, 'geometry_line_end': start_line + end,
            'orientation': lines[begin].strip(), 'coordinate_unit': 'angstrom',
            'energy': energy, 'energy_status': selection['status'], 'energy_reason': selection['reason'],
            'energy_candidate_ids': selection['candidate_ids'], 'convergence': convergence,
            'convergence_unit_system': unit_system,
            'status': status, 'calculation_status': job['status']})
        previous = marker
    return {'status': 'available', 'array': 'optimization_positions', 'steps': records,
            'coordinate_unit': 'angstrom', 'energy_unit': 'hartree',
            'association': 'explicit_step_and_orientation_audited_against_cclib'}


def validate_optimization(data):
    record = data.metadata.get('optimization')
    if not record or record.get('status') != 'available':
        return
    steps = record.get('steps', [])
    coords = data.arrays.get(record.get('array'))
    if (not steps or len(steps) > 10000 or coords is None or
            coords.shape != (len(steps), len(data.arrays['atomic_numbers']), 3) or
            [s.get('step') for s in steps] != list(range(1, len(steps) + 1))):
        raise ValueError('Optimization steps and coordinate arrays disagree')
