"""Gaussian job boundaries, printed energy events and cclib property adaptation."""
from io import StringIO
import logging
from pathlib import Path
import re
from decimal import Decimal

import numpy as np

from .data import Dataset
from .readers import infer_bonds, source_record

NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[DEde][+-]?\d+)?'
SCF_METHODS = {'HF', 'B3LYP', 'PBE', 'PBEPBE', 'PBE1PBE', 'BLYP', 'BP86',
               'M06', 'M062X', 'M052X', 'WB97XD', 'CAM-B3LYP', 'LSDA'}


def number(value):
    result = float(value.replace('D', 'E').replace('d', 'e'))
    if not np.isfinite(result):
        raise ValueError('Non-finite Gaussian energy')
    return result


def split_jobs(lines):
    starts = [0]
    has_calculation = False
    for index, line in enumerate(lines):
        internal = 'Link1:  Proceeding to internal job step number' in line
        run_start = 'Entering Gaussian System, Link 0=' in line
        concatenated = run_start and has_calculation
        if index > starts[-1] and (internal or concatenated):
            starts.append(index)
            has_calculation = False
        if (line.lstrip().startswith('#') or 'SCF Done:' in line
                or 'Error termination' in line or 'Normal termination of Gaussian' in line
                or 'orientation:' in line.lower()):
            has_calculation = True
    return [(start, end) for start, end in zip(starts, starts[1:] + [len(lines)])]


def route_text(lines):
    for index, line in enumerate(lines):
        if line.lstrip().startswith('#'):
            route = [line.strip()]
            for following in lines[index + 1:]:
                if following.strip().startswith('---') or not following.strip():
                    break
                route.append(following.strip())
            return ' '.join(route)
    return None


def energy_events(lines, start_line, job_id, route, status):
    records, evaluation, state, selected_state = [], 0, None, None
    route_lower = (route or '').lower()
    requested = None
    for method in ('CCSD(T)', 'DSDPBEP86', 'B2PLYP', 'MP2'):
        if method.lower() in route_lower:
            requested = method
            break
    if re.search(r'\btd(?:\b|\()', route_lower):
        requested = 'TD-HF/TD-DFT'
    complex_context = re.search(r'\b(?:oniom|counterpoise|casscf|cbs|g[1-4]|mp[3-5]|ccsd|qcisd)\b', route_lower)

    def append(line_number, raw, label, text, method, kind='electronic_total', role='intermediate', unit='hartree'):
        value = number(text)
        evidence = 'archive' if '\\' in raw else 'body'
        if evidence == 'archive':
            role = 'archive_evidence'
        records.append({'id': f'{job_id}:eval{evaluation}:energy{len(records)}',
                        'job_id': job_id, 'evaluation_id': f'{job_id}:eval{evaluation}',
                        'kind': kind, 'method': method, 'method_ref': route, 'role': role,
                        'value_hartree': value if unit == 'hartree' else value / 27.211386245981,
                        'raw_value_text': text, 'raw_unit': unit, 'raw_label': label, 'raw_line': raw.rstrip(),
                        'evidence_type': evidence,
                        'line_start': line_number, 'line_end': line_number,
                        'state': state.copy() if state and method == 'TD-HF/TD-DFT' else None,
                        'geometry_ref': None, 'association_status': 'job_and_evaluation_only',
                        'calculation_status': status, 'parse_status': 'parsed',
                        'reader_version': 'qcblender.gaussian_log 0.1'})

    for offset, line in enumerate(lines):
        lineno = start_line + offset
        if '\\' in line:
            continue
        match = re.search(r'SCF Done:\s+E\(([^)]+)\)\s*=\s*(' + NUMBER + ')', line)
        if match:
            evaluation += 1
            state = None
            selected_state = None
            method = re.sub(r'^(?:RO|R|U)', '', match[1].upper())
            qualified = method in SCF_METHODS and re.search(r'(?<![A-Za-z0-9])(?:RO|R|U)?' + re.escape(method) + r'(?=[\s/(]|$)', route or '', re.I)
            append(lineno, line, 'SCF Done', match[2], match[1],
                   role='reference' if requested else 'target' if qualified and not complex_context else 'scf_candidate')
        match = re.search(r'Excited State\s+(\d+):\s+(\S+)\s+(' + NUMBER + r')\s+eV', line)
        if match:
            state = {'source_number': int(match[1]), 'spin_symmetry': match[2]}
            append(lineno, line, 'Excited State', match[3], 'TD-HF/TD-DFT', 'excitation', 'state_excitation', 'eV')
        if 'This state for optimization and/or second-order correction.' in line:
            selected_state = state.copy() if state else None
        patterns = [
            (r'\bEUMP2\s*=\s*(' + NUMBER + ')', 'EUMP2', 'MP2', 'electronic_total', 'target' if requested == 'MP2' else 'intermediate'),
            (r'\bE2\s*=\s*(' + NUMBER + ')', 'E2', 'MP2', 'correlation_correction', 'correction'),
            (r'CCSD\(T\)\s*=\s*(' + NUMBER + ')', 'CCSD(T)', 'CCSD(T)', 'electronic_total', 'target' if requested == 'CCSD(T)' else 'candidate'),
            (r'E\(CORR\)\s*=\s*(' + NUMBER + ')', 'E(CORR)', 'CCSD', 'electronic_total', 'iteration'),
            (r'Total Energy, E\(TD-HF/TD-DFT\)\s*=\s*(' + NUMBER + ')', 'E(TD-HF/TD-DFT)', 'TD-HF/TD-DFT', 'electronic_total', 'target' if requested == 'TD-HF/TD-DFT' else 'candidate'),
        ]
        for pattern, label, method, kind, role in patterns:
            match = re.search(pattern, line)
            if match:
                append(lineno, line, label, match[1], method, kind, role)
                if method == 'TD-HF/TD-DFT':
                    records[-1]['state'] = selected_state
                    if selected_state is None:
                        records[-1]['role'] = 'candidate'
                        records[-1]['association_status'] = 'excited_state_unresolved'
        for method in ('DSDPBEP86', 'B2PLYP'):
            for label, kind, role in [(f'E({method})', 'electronic_total', 'target' if requested == method and method == 'DSDPBEP86' else 'candidate'),
                                       (f'E2({method})', 'correlation_correction', 'correction')]:
                match = re.search(re.escape(label) + r'\s*=\s*(' + NUMBER + ')', line, re.IGNORECASE)
                if match:
                    append(lineno, line, label, match[1], method, kind, role)
        for label, kind in [('Zero-point correction', 'zpe_correction'),
                            ('Thermal correction to Energy', 'thermal_correction'),
                            ('Thermal correction to Enthalpy', 'enthalpy_correction'),
                            ('Thermal correction to Gibbs Free Energy', 'gibbs_correction'),
                            ('Sum of electronic and zero-point Energies', 'zero_point_total'),
                            ('Sum of electronic and thermal Energies', 'internal_energy'),
                            ('Sum of electronic and thermal Enthalpies', 'enthalpy'),
                            ('Sum of electronic and thermal Free Energies', 'gibbs_energy')]:
            match = re.search(re.escape(label) + r'\s*=\s*(' + NUMBER + ')', line)
            if match:
                append(lineno, line, label, match[1], route, kind, 'thermochemistry')
    archive_start, archive_lines = None, []
    archive_count = sum(bool(re.search(r'1\\1\\GINC-', line)) for line in lines)
    for offset, line in enumerate(lines):
        if re.search(r'1\\1\\GINC-', line):
            archive_start, archive_lines = start_line + offset, []
        if archive_start is None:
            continue
        archive_lines.append(line.strip())
        if '@' not in line:
            continue
        joined = ''.join(archive_lines)
        for match in re.finditer(r'\\(HF|MP2|MP3|MP4D|MP4DQ|MP4SDQ|CCSD|CCSD\(T\))=(' + NUMBER + r')(?=\\)', joined):
            label = match[1]
            scf = [r for r in records if r['evaluation_id'] == f'{job_id}:eval{evaluation}' and r['raw_label'] == 'SCF Done']
            method = scf[0]['method'] if label == 'HF' and len(scf) == 1 else label
            if label == 'MP2' and requested == 'DSDPBEP86':
                method = requested
            matches = [r for r in records if r['evidence_type'] == 'body' and r['method'] == method
                       and r['kind'] == 'electronic_total' and r['evaluation_id'] == f'{job_id}:eval{evaluation}']
            append(archive_start, joined, 'archive ' + label, match[2], method)
            archive = records[-1]
            archive['line_end'] = start_line + offset
            archive['association_status'] = 'archive_final_evaluation_only'
            archive['consistency'] = 'unmatched'
            if archive_count != 1:
                archive['association_status'] = 'multiple_archives_unresolved'
                archive['evaluation_id'] = None
            if len(matches) == 1 and archive_count == 1:
                body = matches[0]
                precision = lambda text: float(Decimal(1).scaleb(Decimal(text.replace('D', 'E').replace('d', 'e')).as_tuple().exponent))
                tolerance = .5 * (precision(match[2]) + precision(body['raw_value_text'])) + 1e-12
                status_match = 'matched' if abs(archive['value_hartree'] - body['value_hartree']) <= tolerance else 'conflicting'
                archive.update(consistency=status_match, body_record=body['id'], tolerance_hartree=tolerance)
                body['archive_consistency'] = status_match
        archive_start = None
    return records


def select_energy(records, status):
    targets = [r for r in records if r['role'] == 'target' and r['kind'] == 'electronic_total']
    result = {'record_id': None, 'candidate_ids': [r['id'] for r in targets]}
    if status != 'normal':
        return dict(result, status='unavailable', reason='Job is failed or incomplete; partial records remain inspectable')
    if any(r.get('archive_consistency') == 'conflicting' for r in records):
        return dict(result, status='conflicting', reason='Printed body and archive disagree beyond their rounding precision')
    if len(targets) != 1:
        return dict(result, status='ambiguous' if targets else 'unsupported',
                    reason='Choose an explicit evaluation/record' if targets else 'No verified target-energy rule matched')
    return dict(result, record_id=targets[0]['id'], status='available', reason='Unique method-specific result in a normally terminated job')


def summarize_jobs(lines):
    spans = split_jobs(lines)
    jobs = []
    for index, (start, end) in enumerate(spans):
        section = lines[start:end]
        status = 'failed' if any('Error termination' in line for line in section) else (
            'normal' if any('Normal termination of Gaussian' in line for line in section) else 'incomplete')
        route = route_text(section)
        job_id = f'job{index+1}'
        energies = energy_events(section, start+1, job_id, route, status)
        jobs.append({'id': job_id, 'line_start': start+1, 'line_end': end, 'route': route,
                     'status': status, 'energies': energies, 'energy_selection': select_energy(energies, status),
                     'explicit_geometry': any('orientation:' in line.lower() for line in section)})
    return jobs


def inspect_log(path):
    path = Path(path)
    if path.suffix.lower() not in ('.log', '.out'):
        raise ValueError('Calculation preview requires a Gaussian Log/Out file')
    if path.stat().st_size > 512 * 1024**2:
        raise MemoryError('Source exceeds the current 512 MiB import limit')
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines(keepends=True)
    return {'source': source_record(path, 'gaussian-log', 'qcblender.gaussian_log 0.1'),
            'jobs': summarize_jobs(lines)}


def read_log(path, job_index=0):
    from cclib.parser import Gaussian
    path = Path(path)
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines(keepends=True)
    spans = split_jobs(lines)
    if type(job_index) is not int or not 0 <= job_index < len(spans):
        raise ValueError(f'Choose a Gaussian job from 1 to {len(spans)}')
    jobs = summarize_jobs(lines)
    start, end = spans[job_index]
    section = lines[start:end]
    parsed = Gaussian(StringIO(''.join(section)), loglevel=logging.ERROR).parse()
    if not hasattr(parsed, 'atomcoords') or not hasattr(parsed, 'atomnos'):
        raise ValueError('Selected job has no explicit geometry; automatic inheritance is unavailable')
    arrays = {'atomic_numbers': np.asarray(parsed.atomnos, dtype=np.int32),
              'positions': np.asarray(parsed.atomcoords[-1], dtype=np.float64)}
    selected = jobs[job_index]
    metadata = {'source': source_record(path, 'gaussian-log', 'cclib 1.8.1 + qcblender.gaussian_log 0.1'),
                'coordinate_unit': 'angstrom', 'source_coordinate_unit': 'angstrom',
                'title': path.name + f' / Job {job_index+1}', 'jobs': jobs, 'selected_job': job_index,
                'method': selected['route'], 'basis_name': parsed.metadata.get('basis_set'),
                'charge': getattr(parsed, 'charge', None), 'multiplicity': getattr(parsed, 'mult', None),
                'calculation_status': selected['status'], 'geometry_source': 'last parsed orientation in selected job',
                'energies': selected['energies'], 'energy_selection': selected['energy_selection'],
                'fields': [], 'charges': [], 'diagnostics': []}
    from .optimization import optimization_records
    trajectory = optimization_records(section, start + 1, selected, parsed)
    if trajectory is not None:
        metadata['optimization'] = trajectory
        if trajectory['status'] == 'available':
            arrays['optimization_positions'] = np.asarray(parsed.atomcoords, dtype=np.float64)
    metadata['thermochemistry'] = []
    for offset, line in enumerate(section):
        condition = re.search(r'Temperature\s+(' + NUMBER + r')\s+Kelvin\.\s+Pressure\s+(' + NUMBER + r')\s+Atm', line)
        if condition:
            metadata['thermochemistry'].append({'temperature_kelvin': number(condition[1]),
                'pressure_atm': number(condition[2]), 'line_start': start + offset + 1,
                'job_id': selected['id'], 'convention': 'Gaussian printed thermochemistry; no cross-job transfer'})
    if hasattr(parsed, 'atommasses'):
        arrays['atomic_masses'] = np.asarray(parsed.atommasses, dtype=float)
    property_geometry_unique = np.allclose(parsed.atomcoords, parsed.atomcoords[-1], rtol=0, atol=1e-4)
    if not property_geometry_unique:
        metadata['diagnostics'].append('Multiple geometries in this job: per-step property association is not qualified; import a single-point/frequency job for property display')
    for method, values in getattr(parsed, 'atomcharges', {}).items():
        if not property_geometry_unique:
            continue
        if method.endswith('_sum'):
            metadata['diagnostics'].append(method + ': hydrogen-summed charge, excluded from atomic display')
            continue
        if method == 'natural' and sum('Summary of Natural Population Analysis' in s for s in section) > 1:
            metadata['diagnostics'].append('Repeated natural populations: geometry association ambiguous')
            continue
        array = np.asarray(values, dtype=float)
        if array.shape != (len(arrays['atomic_numbers']),) or not np.isfinite(array).all():
            metadata['diagnostics'].append(method + ': invalid atomic charge shape/values')
            continue
        key = 'charge_' + method
        arrays[key] = array
        metadata['charges'].append({'method': method, 'array': key, 'unit': 'e', 'job_id': selected['id']})
    moments = getattr(parsed, 'moments', [])
    if len(moments) > 1 and property_geometry_unique:
        arrays['dipole'] = np.asarray(moments[1], dtype=float)
        metadata['dipole'] = {'array': 'dipole', 'unit': 'debye', 'origin': list(moments[0]),
                               'job_id': selected['id']}
    if hasattr(parsed, 'vibfreqs') and hasattr(parsed, 'vibdisps') and property_geometry_unique:
        frequencies = np.asarray(parsed.vibfreqs, dtype=float)
        displacement = np.asarray(parsed.vibdisps, dtype=float)
        if displacement.shape != (len(frequencies), len(parsed.atomnos), 3):
            raise ValueError('Gaussian vibrational frequencies and displacement shapes disagree')
        arrays['mode_frequencies'] = frequencies
        arrays['mode_displacements'] = displacement
        lengths = np.linalg.norm(displacement, axis=2).max(axis=1)
        if np.any(lengths <= 0):
            raise ValueError('Gaussian mode has no nonzero displacement')
        arrays['mode_display_displacements'] = displacement / lengths[:, None, None]
        metadata['modes'] = {'frequency_unit': 'cm^-1', 'source_convention': 'Gaussian printed normal coordinates',
                             'display_normalization': 'maximum atom displacement = 1', 'job_id': selected['id']}
        if hasattr(parsed, 'vibirs'):
            intensities = np.asarray(parsed.vibirs, dtype=float)
            if intensities.shape == frequencies.shape and np.isfinite(intensities).all():
                arrays['mode_ir_intensities'] = intensities
                metadata['modes']['ir_unit'] = 'km/mol'
            else:
                metadata['diagnostics'].append('IR intensities missing/invalid; no zero-filled spectrum')
    data = Dataset(metadata, arrays)
    data.validate()
    infer_bonds(data)
    return data
