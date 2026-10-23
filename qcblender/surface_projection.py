"""Import fixed-frame Multiwfn depth maps as two-dimensional scientific records."""
import csv
import json
import math
from pathlib import Path
import re

import numpy as np

from .static_reference import require_static_reference
from .data import Dataset
from .readers import source_record

KIND = 'SurfaceDistanceProjection'
SCAN_FORMAT = 'qcblender.surface_projection.scan.v1'
MAX_POINTS = 250_000
XY_TOLERANCE = 5.01e-7
DEPTH_TOLERANCE = 5.01e-9
MISSED, VALID, UNKNOWN = 0, 1, 2
STATE_NAMES = ('missed', 'valid', 'unknown')


def _text(path):
    path = Path(path)
    if path.stat().st_size > 64 * 1024**2:
        raise MemoryError('Projection input exceeds the 64 MiB limit')
    return path.read_text(encoding='utf-8-sig')


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError('Projection scan parameters must be finite numbers')
    return float(value)


def scan_settings(record):
    """Require explicit units, frame, scaling and XY interpretation; never infer them."""
    if not isinstance(record, dict) or record.get('format') != SCAN_FORMAT:
        raise ValueError('Unsupported projection scan JSON format')
    if (record.get('coordinate_unit') != 'angstrom' or record.get('depth_unit') != 'angstrom'
            or record.get('coordinate_frame') != 'reference_cartesian'
            or record.get('depth_definition') != 'z_hit-z_start'):
        raise ValueError('Projection requires angstrom coordinates and z_hit-z_start in the generating reference frame')
    if _number(record.get('data_scale_factor')) != 1.0:
        raise ValueError('Projection input must contain unscaled depth values')
    if record.get('producer') != 'Multiwfn' or not isinstance(record.get('producer_version'), str) or not record['producer_version'].strip():
        raise ValueError('Projection scan must identify the Multiwfn version')
    result = dict(record)
    for key in ('nx', 'ny'):
        value = record.get(key)
        if type(value) is not int or value < 2:
            raise ValueError('Projection grid needs at least two points on each axis')
    if record['nx'] * record['ny'] > MAX_POINTS:
        raise MemoryError('Projection grid exceeds the 250000 point limit')
    for key, count in (('x_range_angstrom', record['nx']), ('y_range_angstrom', record['ny'])):
        value = record.get(key)
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError('Projection axis limits must contain two numbers')
        low, high = map(_number, value)
        if (high - low) / (count - 1) <= 2 * XY_TOLERANCE:
            raise ValueError('Projection axes must increase beyond the source coordinate precision')
        result[key] = [low, high]
    for key in ('z_start_angstrom', 'z_end_angstrom', 'z_step_angstrom'):
        result[key] = _number(record.get(key))
    if result['z_start_angstrom'] <= result['z_end_angstrom'] or result['z_step_angstrom'] <= 0:
        raise ValueError('Projection requires a positive step and a descending Z scan')
    mode = record.get('xy_mode')
    if mode not in ('absolute', 'relative_to_scan_min'):
        raise ValueError('Declare absolute XY coordinates or coordinates relative to the scan minimum')
    offset = record.get('xy_offset_angstrom')
    if not isinstance(offset, (list, tuple)) or len(offset) != 2:
        raise ValueError('Projection XY offset must contain two numbers')
    result['xy_offset_angstrom'] = list(map(_number, offset))
    expected = [0., 0.] if mode == 'absolute' else [result['x_range_angstrom'][0], result['y_range_angstrom'][0]]
    if result['xy_offset_angstrom'] != expected:
        raise ValueError('Projection XY offset conflicts with its declared coordinate mode')
    surface = record.get('surface')
    if surface == 'union_of_open_vdw_spheres':
        result['radius_scale'] = _number(record.get('radius_scale'))
        if result['radius_scale'] <= 0:
            raise ValueError('Projection vdW radius scale must be positive')
    elif surface in ('promolecular_density', 'electron_density'):
        result['density_isovalue_au'] = _number(record.get('density_isovalue_au'))
        if result['density_isovalue_au'] <= 0:
            raise ValueError('Projection density isovalue must be positive')
    else:
        raise ValueError('Unsupported projection surface definition')
    return result


def check_generation_log(text, scan):
    """Check the last printed scan setup, allowing only the log's printed precision."""
    version = re.search(r'(?m)^\s*Version\s+(\S+)', text)
    if not version or version[1] != scan['producer_version']:
        raise ValueError('Projection log version does not match the scan declaration')
    if 'plane data has been exported to distmap.txt' not in text:
        raise ValueError('Projection log does not record a distmap export')
    number = r'([-+]?\d+(?:\.\d+)?)'
    rules = [
        (r'range of X axis, current:\s*' + number + r'\s*to\s*' + number, scan['x_range_angstrom'], .000501),
        (r'range of Y axis, current:\s*' + number + r'\s*to\s*' + number, scan['y_range_angstrom'], .000501),
        (r'number of grids in X, current:\s*(\d+)', [scan['nx']], 0),
        (r'number of grids in Y, current:\s*(\d+)', [scan['ny']], 0),
        (r'Set stepsize for detection isosurface in Z, current:\s*' + number, [scan['z_step_angstrom']], .0000501),
        (r'Set Z position of starting detection, current:\s*' + number, [scan['z_start_angstrom']], .0000501),
        (r'Set Z position of ending detection, current:\s*' + number, [scan['z_end_angstrom']], .0000501),
    ]
    surface_patterns = {
        'union_of_open_vdw_spheres': ('Superposition of vdW spheres multiplied by', 'radius_scale', .000501),
        'promolecular_density': ('Promolecular density with isovalue of', 'density_isovalue_au', .00000501),
        'electron_density': ('Electron density with isovalue of', 'density_isovalue_au', .00000501),
    }
    phrase, key, tolerance = surface_patterns[scan['surface']]
    rules.append((re.escape(phrase) + r'\s*' + number, [scan[key]], tolerance))
    for pattern, expected, tolerance in rules:
        found = re.findall(pattern, text)
        values = found[-1] if found else ()
        values = (values,) if isinstance(values, str) else values
        if len(values) != len(expected) or any(abs(float(a) - b) > tolerance for a, b in zip(values, expected)):
            raise ValueError('Projection log scan parameters disagree with the declaration')


def parse_grid(text, scan):
    rows = []
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        parts = stripped.split()
        if len(parts) != 3:
            raise ValueError(f'Projection line {line_number} must contain X, Y and depth')
        try:
            row = tuple(float(part.replace('D', 'E').replace('d', 'e')) for part in parts)
        except ValueError as error:
            raise ValueError(f'Projection line {line_number} contains an invalid number') from error
        if not all(math.isfinite(value) for value in row):
            raise ValueError(f'Projection line {line_number} contains a nonfinite number')
        rows.append(row)
        if len(rows) > scan['nx'] * scan['ny']:
            raise ValueError('Projection row count does not match the declared grid')
    if len(rows) != scan['nx'] * scan['ny']:
        raise ValueError('Projection row count does not match the declared grid')
    table = np.asarray(rows, dtype=np.float64)
    sx, ix = np.unique(table[:, 0], return_inverse=True)
    sy, iy = np.unique(table[:, 1], return_inverse=True)
    if (len(sx), len(sy)) != (scan['nx'], scan['ny']):
        raise ValueError('Projection coordinate counts do not match the declared grid')
    if len(np.unique(ix * len(sy) + iy)) != len(rows):
        raise ValueError('Projection grid contains duplicate or missing coordinate pairs')
    x, y = sx + scan['xy_offset_angstrom'][0], sy + scan['xy_offset_angstrom'][1]
    for axis, limits in ((x, scan['x_range_angstrom']), (y, scan['y_range_angstrom'])):
        if not np.allclose(axis, np.linspace(*limits, len(axis)), atol=XY_TOLERANCE, rtol=0):
            raise ValueError('Projection coordinates disagree with the declared regular grid or XY offset')
    values = np.empty((len(x), len(y)), dtype=np.float64)
    values[ix, iy] = table[:, 2]
    floor = scan['z_end_angstrom'] - scan['z_start_angstrom']
    if np.any(values < floor - DEPTH_TOLERANCE) or np.any(values > DEPTH_TOLERANCE):
        raise ValueError('Projection depth lies outside the declared negative Z scan')
    state = np.where(np.abs(values - floor) <= DEPTH_TOLERANCE, UNKNOWN, VALID).astype(np.uint8)
    return {'projection_source_x': sx, 'projection_source_y': sy,
            'projection_x': x, 'projection_y': y,
            'projection_depth': values, 'projection_state': state}


def parse_mask(text, shape, values, floor):
    """Mask CSV uses zero-based canonical sorted grid indexes, never source row order."""
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != ['ix', 'iy', 'state']:
        raise ValueError('Projection mask CSV header must be ix,iy,state')
    result = np.full(shape, -1, dtype=np.int8)
    for row in reader:
        try:
            ix, iy, state = (int(row[key]) for key in ('ix', 'iy', 'state'))
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError('Projection mask needs integer indexes and states 0, 1 or 2') from error
        if None in row or not 0 <= ix < shape[0] or not 0 <= iy < shape[1] or state not in (MISSED, VALID, UNKNOWN):
            raise ValueError('Projection mask index or state is outside the allowed range')
        if result[ix, iy] != -1:
            raise ValueError('Projection mask contains a duplicate grid index')
        if state == MISSED and abs(values[ix, iy] - floor) > DEPTH_TOLERANCE:
            raise ValueError('A missed projection point must retain the scan bottom value')
        result[ix, iy] = state
    if np.any(result == -1):
        raise ValueError('Projection mask does not cover the full grid')
    return result.astype(np.uint8)


def import_projection(reference, data_path, settings_path, log_path, mask_path=None):
    require_static_reference(reference)
    reference.validate()
    if not len(reference.arrays['atomic_numbers']):
        raise ValueError('Projection needs a static reference with atoms in the generating orientation')
    scan = scan_settings(json.loads(_text(settings_path)))
    check_generation_log(_text(log_path), scan)
    arrays = parse_grid(_text(data_path), scan)
    if mask_path:
        arrays['projection_state'] = parse_mask(_text(mask_path), arrays['projection_depth'].shape,
                                               arrays['projection_depth'], scan['z_end_angstrom'] - scan['z_start_angstrom'])
    paths = [data_path, settings_path, log_path] + ([mask_path] if mask_path else [])
    sources = [source_record(Path(path), Path(path).suffix.lower().lstrip('.'),
                             'qcblender.surface_projection 0.1') for path in paths]
    arrays.update({key: np.array(reference.arrays[key], copy=True) for key in ('atomic_numbers', 'positions')})
    states = arrays['projection_state']
    metadata = {'source': sources[0], 'coordinate_unit': 'angstrom', 'fields': [],
                'charges': [], 'energies': [], 'title': 'Surface distance projection',
                'calculation_status': 'external_analysis', 'diagnostics': [],
                'analysis': {'kind': KIND, 'sources': sources, 'scan': scan,
                             'reference_source': reference.metadata['source']['sha256'],
                             'association': 'user_assigned_generating_orientation',
                             'validity_basis': 'explicit_mask' if mask_path else 'scan_bottom_unknown',
                             'state_names': list(STATE_NAMES),
                             'counts': {name: int(np.count_nonzero(states == index)) for index, name in enumerate(STATE_NAMES)}}}
    if np.any(states == UNKNOWN):
        metadata['diagnostics'].append('Projection points with unknown validity are excluded from contours and color range')
    data = Dataset(metadata, arrays)
    data.validate()
    return data


def validate_projection(data):
    analysis = data.metadata.get('analysis', {})
    if analysis.get('kind') != KIND:
        return
    scan = scan_settings(analysis.get('scan'))
    arrays = data.arrays
    required = ('projection_source_x', 'projection_source_y', 'projection_x', 'projection_y',
                'projection_depth', 'projection_state')
    if any(key not in arrays for key in required):
        raise ValueError('Projection scientific arrays are incomplete')
    shape = (scan['nx'], scan['ny'])
    if arrays['projection_depth'].shape != shape or arrays['projection_state'].shape != shape:
        raise ValueError('Projection depth and validity shapes disagree with the scan')
    for index, name in enumerate(('x', 'y')):
        axis, original = arrays['projection_' + name], arrays['projection_source_' + name]
        if axis.shape != (shape[index],) or original.shape != axis.shape:
            raise ValueError('Projection axis shape disagrees with the scan')
        if (not np.array_equal(axis, original + scan['xy_offset_angstrom'][index])
                or not np.allclose(axis, np.linspace(*scan[name + '_range_angstrom'], len(axis)), atol=XY_TOLERANCE, rtol=0)):
            raise ValueError('Projection saved coordinates contain a changed or repeated XY offset')
    state, depth = arrays['projection_state'], arrays['projection_depth']
    floor = scan['z_end_angstrom'] - scan['z_start_angstrom']
    if state.dtype.kind not in 'iu' or np.any((state < MISSED) | (state > UNKNOWN)):
        raise ValueError('Projection validity must use states 0, 1 or 2')
    if np.any(depth < floor - DEPTH_TOLERANCE) or np.any(depth > DEPTH_TOLERANCE):
        raise ValueError('Projection depth lies outside the declared negative Z scan')
    if np.any(np.abs(depth[state == MISSED] - floor) > DEPTH_TOLERANCE):
        raise ValueError('A missed projection point must retain the scan bottom value')
    if analysis.get('state_names') != list(STATE_NAMES) or analysis.get('counts') != {
            name: int(np.count_nonzero(state == index)) for index, name in enumerate(STATE_NAMES)}:
        raise ValueError('Projection validity metadata disagrees with its scientific arrays')
    if data.metadata.get('fields'):
        raise ValueError('A two-dimensional projection must not declare a three-dimensional field')


def color_range(data, manual=None):
    validate_projection(data)
    if manual is not None:
        if len(manual) != 2 or not all(math.isfinite(value) for value in manual) or manual[0] >= manual[1]:
            raise ValueError('Projection color range must be finite and increasing')
        return tuple(map(float, manual))
    values = data.arrays['projection_depth'][data.arrays['projection_state'] == VALID]
    if not len(values):
        scan = data.metadata['analysis']['scan']
        return scan['z_end_angstrom'] - scan['z_start_angstrom'], 0.
    low, high = float(values.min()), float(values.max())
    if low == high:
        return low - .5, high + .5
    return low, high


def grid_positions(data, z=0.):
    x, y = np.meshgrid(data.arrays['projection_x'], data.arrays['projection_y'], indexing='ij')
    return np.stack((x, y, np.full(x.shape, z)), axis=-1)
