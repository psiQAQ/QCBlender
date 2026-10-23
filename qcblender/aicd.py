"""Gaussian CSGT response tensors, preserved samples and finite-grid display mapping."""
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np

from .data import BOHR_ANGSTROM, Dataset
from .gaussian_log import route_text, split_jobs
from .readers import infer_bonds, source_record
from .resources import dataset_bytes, enforce_dataset_limit
from .static_reference import require_static_reference

KIND = 'AICD'
FORMAT = 'qcblender.aicd.source.v1'
UNIT = 'au_current_density_per_au_field'
CHUNK = 2048


def _cancel(cancelled):
    if cancelled and cancelled():
        raise InterruptedError('AICD import cancelled')


def _budget(memory_mb):
    if type(memory_mb) is not int or not 32 <= memory_mb <= 16384:
        raise ValueError('Memory budget must be an integer from 32 to 16384 MiB')
    return memory_mb * 1024**2


def _rows(path, cancelled=None):
    """Validate section order and local row identities without buffering whole blocks."""
    section, counts, offset, block, header = -1, [0]*5, 0, 0, False
    with Path(path).open(encoding='ascii') as stream:
        for line_number, line in enumerate(stream, 1):
            if line_number % 4096 == 0:
                _cancel(cancelled)
            text = line.strip()
            if not text:
                continue
            if text == 'Gitterpunkte:':
                if block:
                    if section != 4 or not counts[0] or len(set(counts)) != 1:
                        raise ValueError('AICD block has missing or unequal sections')
                    offset += counts[0]
                block += 1
                section, counts, header = 0, [0]*5, True
                continue
            marker = 1 if text == 'Gewichtungsfaktoren:' else None
            match = re.fullmatch(r'Stromdichtetensor,\s*II=\s*([123])', text)
            if match:
                marker = int(match[1]) + 1
            if marker is not None:
                if marker != section + 1 or not counts[section]:
                    raise ValueError('AICD sections are missing, duplicated or out of order')
                section, header = marker, True
                continue
            if section < 0:
                raise ValueError('AICD data must begin with a point block')
            fields = text.split()
            expected = 1 if section == 1 else 3
            if header:
                if fields != [str(i+1) for i in range(expected)]:
                    raise ValueError('AICD section column header is invalid')
                header = False
                continue
            if len(fields) != expected + 1 or not fields[0].isdigit() or int(fields[0]) != counts[section]+1:
                raise ValueError('AICD row index or component count is invalid')
            try:
                values = tuple(float(v.replace('D', 'E').replace('d', 'e')) for v in fields[1:])
            except ValueError as error:
                raise ValueError('AICD numeric value is invalid') from error
            if not all(math.isfinite(v) for v in values):
                raise ValueError('AICD values must be finite')
            if section == 1 and values[0] < 0:
                raise ValueError('AICD quadrature weights cannot be negative')
            counts[section] += 1
            if section and counts[section] > counts[0]:
                raise ValueError('AICD section has too many rows')
            yield section, offset + counts[section] - 1, block, counts[section], values
    if section != 4 or not counts[0] or len(set(counts)) != 1 or header:
        raise ValueError('AICD file ends with an incomplete block')


def parse_dump(path, memory_mb=512, cancelled=None):
    budget = _budget(memory_mb)
    count = blocks = 0
    for section, index, block, local, values in _rows(path, cancelled):
        if section == 0:
            count += 1
            blocks = block
            if count * 240 + CHUNK * 4096 > budget:
                raise MemoryError('AICD samples exceed the working-memory budget')
    points, weights = np.empty((count, 3)), np.empty(count)
    tensors = np.empty((count, 3, 3))
    identifiers = np.empty((count, 2), dtype=np.int32)
    second_count = 0
    for section, index, block, local, values in _rows(path, cancelled):
        if index >= count:
            raise ValueError('AICD source changed while reading')
        if section == 0:
            second_count += 1
            points[index] = values
            identifiers[index] = block, local
        elif section == 1:
            weights[index] = values[0]
        else:
            tensors[index, :, section-2] = values
    if second_count != count:
        raise ValueError('AICD source changed while reading')
    return points, weights, tensors, identifiers, blocks


def anisotropy(tensors):
    t = np.asarray(tensors, dtype=np.float64)
    return np.sqrt(.5*((t[..., 0, 0]-t[..., 1, 1])**2 + (t[..., 1, 1]-t[..., 2, 2])**2
                      + (t[..., 2, 2]-t[..., 0, 0])**2)
                   + .75*((t[..., 0, 1]+t[..., 1, 0])**2 + (t[..., 1, 2]+t[..., 2, 1])**2
                           + (t[..., 0, 2]+t[..., 2, 0])**2))


def field_direction(field):
    field = np.asarray(field, dtype=float)
    if field.shape != (3,) or not np.isfinite(field).all() or not np.any(field):
        raise ValueError('AICD field direction must be a finite nonzero vector')
    field = field / np.max(np.abs(field))
    return field / np.linalg.norm(field)


def current(tensors, field=(0., 0., 1.)):
    return np.asarray(tensors) @ field_direction(field)


def grid_spec(positions, spacing=.25, padding=2.5):
    if not math.isfinite(spacing) or not math.isfinite(padding) or spacing < .0001 or padding < 0:
        raise ValueError('AICD spacing must be at least 0.0001 angstrom and padding nonnegative')
    lo, hi = positions.min(axis=0)-padding, positions.max(axis=0)+padding
    shape = tuple(max(2, math.ceil(float(v)/spacing)+1) for v in hi-lo)
    return lo, float(spacing), shape


def nearest_nodes(points, origin, spacing, shape):
    """Four nearest finite-grid nodes; ties use C-order flattened node numbers."""
    candidates = []
    for axis, size in enumerate(shape):
        width = min(5, size)
        base = np.clip(np.floor((points[:, axis]-origin[axis])/spacing)-2, 0, size-width).astype(np.int64)
        indices = base[:, None] + np.arange(width)
        distance = abs(origin[axis]+spacing*indices-points[:, axis, None])
        order = np.lexsort((indices, distance), axis=1)[:, :4]
        candidates.append(np.take_along_axis(indices, order, axis=1))
    x, y, z = candidates
    indices = ((x[:, :, None, None]*shape[1] + y[:, None, :, None])*shape[2]
               + z[:, None, None, :]).reshape(len(points), -1)
    distances = ((origin[0]+spacing*x-points[:, 0, None])**2)[:, :, None, None]
    distances = distances + ((origin[1]+spacing*y-points[:, 1, None])**2)[:, None, :, None]
    distances = distances + ((origin[2]+spacing*z-points[:, 2, None])**2)[:, None, None, :]
    distances = distances.reshape(len(points), -1)
    order = np.lexsort((indices, distances), axis=1)[:, :4]
    return np.take_along_axis(indices, order, axis=1), np.sqrt(np.take_along_axis(distances, order, axis=1))


def remap(points, tensors, values, origin, spacing, shape, memory_mb=512, cancelled=None):
    nodes = math.prod(shape)
    estimated = len(points)*240 + nodes*256 + CHUNK*4096
    if estimated > _budget(memory_mb):
        raise MemoryError('AICD grid and tensor cache exceed the working-memory budget')
    result = np.zeros((nodes, 10))
    sums = np.zeros(nodes)
    for start in range(0, len(points), CHUNK):
        _cancel(cancelled)
        stop = min(len(points), start+CHUNK)
        indexes, distances = nearest_nodes(points[start:stop], origin, spacing, shape)
        weights = 1 / np.maximum(distances, 1e-8)
        channels = np.column_stack((values[start:stop], tensors[start:stop].reshape(-1, 9)))
        np.add.at(sums, indexes.ravel(), weights.ravel())
        for channel in range(10):
            np.add.at(result[:, channel], indexes.ravel(), (channels[:, channel, None]*weights).ravel())
    valid = sums > 0
    result[valid] /= sums[valid, None]
    return result[:, 0].reshape(shape).copy(), result[:, 1:].reshape(shape+(9,)).copy(), valid.reshape(shape)


def _source_bundle(path):
    path = Path(path)
    if path.stat().st_size > 1024**2:
        raise MemoryError('AICD source declaration exceeds 1 MiB')
    record = json.loads(path.read_text(encoding='utf-8-sig'))
    if record.get('format') != FORMAT or record.get('coordinate_unit') != 'bohr' or record.get('response_unit') != UNIT:
        raise ValueError('AICD declaration requires the supported format and explicit source units')
    paths = {}
    for role in ('tensor', 'log', 'input'):
        item = record['files'][role]
        relative = Path(item['path'])
        if relative.is_absolute() or relative.drive or '..' in relative.parts:
            raise ValueError('AICD source files must be relative to their declaration')
        target = (path.parent/relative).resolve(strict=True)
        if not target.is_relative_to(path.parent.resolve()) or target.stat().st_size > 512*1024**2:
            raise ValueError('AICD source file escapes its directory or exceeds the import limit')
        with target.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != item['sha256']:
            raise ValueError('AICD source checksum does not match its declaration')
        paths[role] = target
    return record, paths


def _log_identity(path, input_path, dump_path, record):
    if path.stat().st_size > 64*1024**2 or input_path.stat().st_size > 1024**2:
        raise MemoryError('AICD identity text exceeds the import limit')
    lines = path.read_text(errors='replace').splitlines()
    jobs = split_jobs(lines)
    selected = record.get('job_index')
    if type(selected) is not int or not 0 <= selected < len(jobs):
        raise ValueError('AICD declaration must select an existing zero-based calculation segment')
    start, end = jobs[selected]
    section = lines[start:end]
    text = '\n'.join(section)
    route = route_text(section) or ''
    compact = re.sub(r'\s+', '', route).lower()
    if ('nmr=csgt' not in compact and 'nmr(csgt)' not in compact) or not re.search(r'iop\(10/93=[12]\)', compact):
        raise ValueError('AICD requires a Gaussian CSGT tensor-producing calculation')
    if 'Normal termination of Gaussian' not in text or 'Error termination' in text:
        raise ValueError('AICD calculation segment did not terminate normally')
    version = re.search(r'Gaussian\s+(\d+):\s*(\S+)', '\n'.join(lines[:start+100]))
    if not version:
        raise ValueError('AICD Gaussian version is missing')
    writes = list(re.finditer(r'Writing AICD.*?file "([^"]+)"', text))
    if len(writes) != 1 or Path(writes[0][1]).name != dump_path.name:
        raise ValueError('AICD calculation must identify exactly one matching tensor dump')
    preceding = text[:writes[0].start()]
    geometries = []
    for match in re.finditer(r'Standard orientation:[ \t]*\n[ \t]*-{5,}[ \t]*\n[^\n]+\n[^\n]+\n[ \t]*-{5,}[ \t]*\n(.*?)\n[ \t]*-{5,}', preceding, re.S):
        rows = [line.split() for line in match[1].splitlines()]
        geometries.append((np.array([int(row[1]) for row in rows], dtype=np.int32),
                           np.array([[float(v) for v in row[3:6]] for row in rows])))
    if not geometries:
        raise ValueError('AICD generating standard orientation is missing')
    numbers, positions = geometries[-1]
    if any(not np.array_equal(n, numbers) or not np.allclose(p, positions, atol=1e-6, rtol=0) for n, p in geometries):
        raise ValueError('AICD segment contains changing geometries; use a fixed single-point calculation')
    charge = re.search(r'Charge\s*=\s*(-?\d+)\s+Multiplicity\s*=\s*(\d+)', text)
    if not charge or int(charge[2]) != 1 or re.search(r'SCF Done:\s+E\(U', text):
        raise ValueError('AICD currently requires a closed-shell singlet')
    inp = input_path.read_text(errors='replace')
    input_route = re.search(r'(?ms)^\s*#.*?(?=\n\s*\n)', inp)
    if not input_route or re.sub(r'\s+', '', input_route[0]).lower() != compact:
        raise ValueError('AICD input route does not match the selected log segment')
    from iodata.periodic import sym2num
    geometry = re.search(r'(?m)^\s*(-?\d+)\s+(\d+)[ \t]*\n((?:[^\n]+\n)+?)[ \t]*\n', inp)
    if not geometry or tuple(map(int, geometry.group(1, 2))) != (int(charge[1]), 1):
        raise ValueError('AICD input needs explicit Cartesian atoms and matching charge/multiplicity')
    input_rows = [row.split() for row in geometry[3].splitlines()]
    if any(len(row) != 4 for row in input_rows):
        raise ValueError('AICD input needs explicit Cartesian atoms and matching charge/multiplicity')
    input_numbers = [int(row[0]) if row[0].isdigit() else sym2num.get(row[0].title(), 0) for row in input_rows]
    input_positions = np.array([[float(v.replace('D', 'E')) for v in row[1:]] for row in input_rows])
    if 'units=' in compact or 'units(' in compact:
        raise ValueError('AICD input must use default angstrom Cartesian coordinates')
    logged_input = re.search(r'Input orientation:[ \t]*\n[ \t]*-{5,}[ \t]*\n[^\n]+\n[^\n]+\n[ \t]*-{5,}[ \t]*\n(.*?)\n[ \t]*-{5,}', preceding, re.S)
    if not logged_input:
        raise ValueError('AICD log must retain the input orientation for source verification')
    logged_rows = [row.split() for row in logged_input[1].splitlines()]
    logged_numbers = [int(row[1]) for row in logged_rows]
    logged_positions = np.array([[float(v) for v in row[3:6]] for row in logged_rows])
    if (input_numbers != logged_numbers or not np.array_equal(logged_numbers, numbers)
            or not np.allclose(input_positions, logged_positions, atol=1e-6, rtol=0)):
        raise ValueError('AICD input atoms or coordinates differ from the generating log')
    component = record.get('component', 'unknown')
    if component not in ('all', 'pi', 'sigma', 'selected', 'unknown'):
        raise ValueError('Unknown AICD orbital contribution identity')
    occupation = re.search(r'CSGT:\s*Occupy MOs([^\n]*(?:\n\s+\d[^\n]*)*)', text)
    orbitals = [int(v) for v in re.findall(r'\d+', occupation[1])] if occupation else []
    if orbitals != record.get('orbitals', []):
        raise ValueError('AICD declared orbitals differ from the actual calculation')
    if component == 'all' and ('10/93=1' not in compact or orbitals):
        raise ValueError('AICD all-electron identity conflicts with the calculation')
    if component in ('pi', 'sigma', 'selected') and (not orbitals or '10/93=2' not in compact):
        raise ValueError('AICD selected contribution requires recorded orbital numbers')
    evidence = record.get('orbital_assignment_evidence', '').strip()
    if component in ('pi', 'sigma') and (not evidence or np.linalg.svd(positions-positions.mean(axis=0), compute_uv=False)[-1] > 1e-5):
        raise ValueError('AICD pi/sigma identity needs planar geometry and explicit orbital evidence')
    return numbers, positions, {'program': 'Gaussian '+version[1], 'version': version[2], 'route': route,
        'charge': int(charge[1]), 'multiplicity': 1, 'job_index': selected, 'line_start': start+1,
        'line_end': end, 'coordinate_frame': 'Gaussian Standard orientation', 'component': component,
        'orbitals': orbitals, 'spin': 'restricted', 'orbital_assignment_evidence': evidence,
        'assignment_status': 'log_verified' if component == 'all' else 'user_declared; orbital numbers verified against log'}


def import_aicd(reference, source_path, spacing=.25, padding=2.5, memory_mb=512, cancelled=None):
    require_static_reference(reference)
    _budget(memory_mb)
    record, paths = _source_bundle(source_path)
    numbers, positions, identity = _log_identity(paths['log'], paths['input'], paths['tensor'], record)
    if not np.array_equal(numbers, reference.arrays['atomic_numbers']) or not np.allclose(
            positions, reference.arrays['positions'], atol=1e-5, rtol=0):
        raise ValueError('AICD atoms must match the static reference in the generating orientation')
    origin, spacing, shape = grid_spec(positions, spacing, padding)
    if math.prod(shape)*256 + CHUNK*4096 > _budget(memory_mb):
        raise MemoryError('AICD grid exceeds the working-memory budget')
    p, w, t, ids, blocks = parse_dump(paths['tensor'], memory_mb, cancelled)
    points, a = p*BOHR_ANGSTROM, anisotropy(t)
    values, cache, mask = remap(points, t, a, origin, spacing, shape, memory_mb, cancelled)
    _cancel(cancelled)
    # Detect mutation between identity verification and the end of the streaming reads.
    after, unused = _source_bundle(source_path)
    if after != record:
        raise ValueError('AICD declaration changed during import')
    sources = [source_record(paths[key], key, 'qcblender.aicd 0.1') for key in ('tensor', 'log', 'input')]
    field = {'quantity': 'aicd_anisotropy', 'unit': UNIT, 'array': 'aicd_grid_aniso',
             'valid_mask': 'aicd_grid_valid', 'origin': origin.tolist(), 'steps': (np.eye(3)*spacing).tolist(),
             'shape': list(shape), 'formula': 'symmetric_traceless_frobenius_sqrt_3_over_2'}
    analysis = dict(identity, kind=KIND, sources=sources, declaration=record,
                    coordinate_unit='bohr', response_unit=UNIT, tensor_layout='point,current,field',
                    sample_count=len(p), block_count=blocks, reference_source=reference.metadata['source']['sha256'],
                    remap={'algorithm': 'point_to_four_nodes_idw_v1', 'spacing_angstrom': spacing,
                           'padding_angstrom': padding, 'distance_floor_angstrom': 1e-8,
                           'tie_order': 'C flattened node index', 'outside_points': 'nearest finite-grid nodes',
                           'quadrature_weights_used': False, 'aniso_before_remap': True,
                           'valid_nodes': int(mask.sum()), 'memory_mb': memory_mb})
    data = Dataset({'source': sources[0], 'coordinate_unit': 'angstrom', 'fields': [field],
                    'charges': [], 'energies': [], 'analysis': analysis, 'calculation_status': 'external_analysis',
                    'title': 'AICD '+identity['component'], 'diagnostics': []},
                   {'atomic_numbers': numbers, 'positions': positions,
                    'aicd_points_bohr': p, 'aicd_weights': w, 'aicd_tensors': t, 'aicd_ids': ids,
                    'aicd_aniso': a, 'aicd_grid_aniso': values, 'aicd_grid_tensors': cache, 'aicd_grid_valid': mask})
    infer_bonds(data)
    enforce_dataset_limit(dataset_bytes(data.arrays))
    data.validate()
    return data


def validate_aicd(data):
    analysis = data.metadata.get('analysis', {})
    if analysis.get('kind') != KIND:
        return
    a = data.arrays
    count = analysis['sample_count']
    for name, shape in [('points_bohr', (count, 3)), ('weights', (count,)), ('tensors', (count, 3, 3)),
                         ('ids', (count, 2)), ('aniso', (count,))]:
        if a['aicd_'+name].shape != shape:
            raise ValueError('AICD stored sample arrays have inconsistent shapes')
    field = data.metadata['fields'][0]
    if a['aicd_grid_tensors'].shape != tuple(field['shape'])+(9,):
        raise ValueError('AICD stored grid tensor cache has an invalid shape')
    if analysis.get('response_unit') != UNIT or analysis.get('tensor_layout') != 'point,current,field':
        raise ValueError('AICD stored response convention is invalid')


def sample_record(data, index, field=(0, 0, 1)):
    if type(index) is not int or not 0 <= index < data.metadata['analysis']['sample_count']:
        raise ValueError('AICD sample index is outside the source data')
    a = data.arrays
    return {'index': index, 'block': int(a['aicd_ids'][index, 0]), 'local_index': int(a['aicd_ids'][index, 1]),
            'position_angstrom': (a['aicd_points_bohr'][index]*BOHR_ANGSTROM).tolist(),
            'weight': float(a['aicd_weights'][index]), 'tensor': a['aicd_tensors'][index].tolist(),
            'aniso': float(a['aicd_aniso'][index]), 'field': field_direction(field).tolist(),
            'current': current(a['aicd_tensors'][index], field).tolist()}


def arrow_samples(data, isovalue, field, limit=1000):
    if type(limit) is not int or not 0 <= limit <= 1000:
        raise ValueError('AICD arrow count must be between 0 and 1000')
    scalar, valid = data.arrays['aicd_grid_aniso'], data.arrays['aicd_grid_valid']
    if not math.isfinite(isovalue) or isovalue <= 0 or not np.any(valid) or isovalue >= float(scalar[valid].max()):
        raise ValueError('Choose a positive AICD isovalue below the valid grid maximum')
    spec = data.metadata['fields'][0]
    spacing = spec['steps'][0][0]
    gradient = np.sqrt(sum(g*g for g in np.gradient(scalar, spacing)))
    near = valid & (np.abs(scalar-isovalue) <= .75*spacing*gradient)
    ids = np.flatnonzero(near)
    vectors = current(data.arrays['aicd_grid_tensors'].reshape(-1, 3, 3)[ids], field)
    nonzero = np.linalg.norm(vectors, axis=1) > 0
    ids, vectors = ids[nonzero], vectors[nonzero]
    chosen = np.linspace(0, len(ids)-1, min(limit, len(ids)), dtype=int)
    ids, vectors = ids[chosen], vectors[chosen]
    positions = np.array(np.unravel_index(ids, scalar.shape)).T*spacing+spec['origin']
    return positions, vectors, ids
