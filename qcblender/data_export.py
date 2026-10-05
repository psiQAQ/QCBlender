"""Explicit scientific CSV and view-summary exports from saved Dataset records."""
import csv
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import uuid

import numpy as np


def _file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def documents_directory():
    """Resolve the Windows Documents Known Folder, including redirected folders."""
    if os.name != 'nt':
        raise OSError('Configure a data output directory on this platform')
    class GUID(ctypes.Structure):
        _fields_ = [('a', ctypes.c_uint32), ('b', ctypes.c_uint16),
                    ('c', ctypes.c_uint16), ('d', ctypes.c_ubyte * 8)]
    identifier = GUID.from_buffer_copy(uuid.UUID('FDD39AD0-238F-46AF-ADB4-6C85480369C7').bytes_le)
    value = ctypes.c_void_p()
    shell = ctypes.windll.shell32.SHGetKnownFolderPath
    shell.argtypes = [ctypes.POINTER(GUID), ctypes.c_uint32, ctypes.c_void_p,
                      ctypes.POINTER(ctypes.c_void_p)]
    shell.restype = ctypes.c_long
    result = shell(ctypes.byref(identifier), 0, None, ctypes.byref(value))
    if result != 0:
        raise OSError(f'Windows Documents Known Folder unavailable (HRESULT {result:#x})')
    try:
        return Path(ctypes.wstring_at(value))
    finally:
        ctypes.windll.ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
        ctypes.windll.ole32.CoTaskMemFree(value)


def default_output_directory(preference='', blend_filepath='', documents=documents_directory):
    if preference:
        path = Path(preference)
        if not path.is_absolute():
            raise ValueError('Data output preference must be an absolute directory')
        return path
    if blend_filepath:
        return Path(blend_filepath).resolve().parent
    return documents()


def available_exports(data):
    result = []
    arrays, meta = data.arrays, data.metadata
    if 'mode_frequencies' in arrays:
        result.append('IR')
    if meta.get('optimization', {}).get('status') == 'available':
        result.append('optimization')
    if 'irc_energies' in arrays:
        result.append('IRC')
    if 'mayer_orders' in arrays:
        result.append('Mayer')
    if 'profile' in meta:
        result.append('profile')
    if meta.get('analysis', {}).get('kind') in ('IGMH', 'IRI'):
        result.append('paired')
    if meta.get('analysis', {}).get('kind') == 'ESP':
        result.append('ESP_AREA')
    return result + ['SUMMARY']


def _tables(data, kind, filters, cancelled):
    arrays, meta = data.arrays, data.metadata
    if kind == 'IR':
        frequency = arrays['mode_frequencies']
        intensity = arrays.get('mode_ir_intensities')
        rows = ((i + 1, float(v), '' if intensity is None else float(intensity[i]), int(v < 0))
                for i, v in enumerate(frequency))
        yield 'ir.csv', ('mode', 'frequency_cm-1', 'ir_intensity_km_mol', 'imaginary'), rows, {'frequency': 'cm^-1', 'ir_intensity': 'km/mol'}
    elif kind == 'optimization':
        steps = meta['optimization']['steps']
        rows = ((s['step'], s['job_id'], (s.get('energy') or {}).get('value_hartree', ''),
                 s['energy_status'], s['status'], s['calculation_status'], s['line_start'], s['line_end']) for s in steps)
        yield 'optimization_steps.csv', ('step', 'job_id', 'energy_hartree', 'energy_status', 'step_status', 'calculation_status', 'line_start', 'line_end'), rows, {'energy': 'hartree'}
        convergence = ((s['step'], s['job_id'], r['quantity'], r['value'], r['threshold'], int(r['converged']),
                        r.get('unit') or '', (s.get('convergence_unit_system') or {}).get('text', ''), r['line_start'])
                       for s in steps for r in s['convergence'])
        yield 'optimization_convergence.csv', ('step', 'job_id', 'quantity', 'value', 'threshold', 'converged', 'unit', 'source_unit_system', 'line_start'), convergence, {'unit': 'source record; blank when unspecified'}
    elif kind == 'IRC':
        sources = meta['analysis']['steps']
        rows = ((i + 1, float(value), sources[i]['filename'], sources[i]['sha256']) for i, value in enumerate(arrays['irc_energies']))
        yield 'irc_steps.csv', ('step', 'energy_hartree', 'source_filename', 'source_sha256'), rows, {'energy': 'hartree'}
    elif kind == 'Mayer':
        pairs, values = arrays['mayer_pairs'], arrays['mayer_orders']
        rows = ((step + 1, int(pair[0]), int(pair[1]), float(values[step, index]))
                for step in range(len(values)) for index, pair in enumerate(pairs))
        yield 'mayer.csv', ('step', 'atom_a_1based', 'atom_b_1based', 'mayer_order'), rows, {'mayer_order': 'dimensionless'}
    elif kind == 'profile':
        rows = ((float(d), *map(float, p), float(v) if valid else '', meta['profile']['field']['unit'], int(valid))
                for d, p, v, valid in zip(arrays['profile_distance'], arrays['profile_positions'], arrays['profile_values'], arrays['profile_valid'], strict=True))
        yield 'profile.csv', ('distance_angstrom', 'x_angstrom', 'y_angstrom', 'z_angstrom', 'value', 'unit', 'valid'), rows, {'position': 'angstrom', 'value': meta['profile']['field']['unit']}
    elif kind == 'ESP_AREA':
        from .result_filters import area_selection
        analysis = meta['analysis']
        selection = area_selection(analysis, **filters)
        bins = analysis['area_bins']
        rows = ((i + 1, bins[i].get('begin', ''), bins[i].get('end', ''), bins[i]['center'], bins[i]['area'], bins[i]['percentage']) for i in selection['indexes'])
        yield 'esp_area.csv', ('source_bin', 'begin', 'end', 'center', 'area', 'source_percentage'), rows, {'center': analysis['distribution_center_unit'], 'area': analysis['area_unit'], 'source_percentage': '% (original source)'}
    elif kind == 'paired':
        from .result_filters import _range
        fields = meta['fields']
        x_field, y_field = filters.get('x_field', 1), filters.get('y_field', 0)
        if {x_field, y_field} != {0, 1}:
            raise ValueError('Choose distinct paired field value columns')
        _range(filters.get('x_min'), filters.get('x_max'), 'X')
        _range(filters.get('y_min'), filters.get('y_max'), 'Y')
        x, y = fields[x_field], fields[y_field]
        def rows():
            values_x, values_y = arrays[x['array']].ravel(), arrays[y['array']].ravel()
            valid_x, valid_y = arrays[x['valid_mask']].ravel(), arrays[y['valid_mask']].ravel()
            origin, axes = np.asarray(x['origin']), np.asarray(x['steps'])
            for start in range(0, len(values_x), 65536):
                if cancelled():
                    raise RuntimeError('Data export cancelled')
                stop = min(start + 65536, len(values_x))
                vx, vy = values_x[start:stop], values_y[start:stop]
                valid = valid_x[start:stop] & valid_y[start:stop] & np.isfinite(vx) & np.isfinite(vy)
                for key, v in (('x', vx), ('y', vy)):
                    if filters.get(key + '_min') is not None:
                        valid &= v >= filters[key + '_min']
                    if filters.get(key + '_max') is not None:
                        valid &= v <= filters[key + '_max']
                for flat in np.flatnonzero(valid) + start:
                    ijk = np.array(np.unravel_index(flat, x['shape']))
                    coordinate = origin + ijk @ axes
                    yield (int(flat), *map(int, ijk), *map(float, coordinate), float(values_x[flat]), float(values_y[flat]))
        yield 'paired_voxels.csv', ('flat_index_0based', 'i_0based', 'j_0based', 'k_0based', 'x_angstrom', 'y_angstrom', 'z_angstrom', 'x_value', 'y_value'), rows(), {'coordinate': meta['coordinate_unit'], 'x_value': x['unit'], 'y_value': y['unit']}


def cleanup_staging(output_directory, token):
    if not re.fullmatch(r'[0-9a-f]{32}', token):
        raise ValueError('Invalid export staging identity')
    staging = Path(output_directory) / ('.qc-export-' + token)
    if staging.is_symlink():
        raise ValueError('Export staging directory must not be a symbolic link')
    if staging.exists():
        shutil.rmtree(staging)


def export_dataset(dataset, output_directory, kind, scope='ALL', filters=None,
                   cancelled=lambda: False, token=None, expected_sha256=None, view_snapshot=None):
    from .data import load_dataset
    source = Path(dataset).resolve(strict=True)
    manifest_sha = hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest()
    if expected_sha256 is not None and expected_sha256 != manifest_sha:
        raise ValueError('Export Dataset changed after the request was created')
    data = load_dataset(source)
    if kind not in available_exports(data):
        raise ValueError('Selected export data is unavailable')
    if scope not in ('ALL', 'FILTERED') or (scope == 'FILTERED' and kind not in ('paired', 'ESP_AREA')):
        raise ValueError('Current filtering is available only for paired fields and ESP area bins')
    filters = dict(filters or {}) if scope == 'FILTERED' else {}
    permitted = {'x_field', 'y_field', 'x_min', 'x_max', 'y_min', 'y_max'} if kind == 'paired' else {'center_min', 'center_max', 'mode'} if kind == 'ESP_AREA' else set()
    if set(filters) - permitted:
        raise ValueError('Unsupported export filter')
    if kind == 'SUMMARY':
        from .view_summary import validate_snapshot, scientific_summary, render_summary
        if _file_sha256(source / 'manifest.json') != manifest_sha:
            raise ValueError('Export Dataset changed while loading the summary')
        summary = validate_snapshot(view_snapshot, manifest_sha)
        summary['scientific'] = scientific_summary(data, summary)
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    token = token or uuid.uuid4().hex
    if not re.fullmatch(r'[0-9a-f]{32}', token):
        raise ValueError('Invalid export staging identity')
    staging = output / ('.qc-export-' + token)
    basename = re.sub(r'[^\w.-]+', '_', Path(data.metadata['source']['filename']).stem).strip('._')[:80] or 'data'
    final = output / (basename + '-' + kind.lower() + '-' + token)
    if final.exists():
        raise FileExistsError(final)
    staging.mkdir()
    try:
        files = []
        if kind == 'SUMMARY':
            if cancelled():
                raise RuntimeError('Data export cancelled')
            path = staging / 'view-summary.md'
            path.write_text(render_summary(summary), encoding='utf-8')
            files.append({'filename': path.name, 'sha256': _file_sha256(path)})
        for filename, header, rows, units in _tables(data, kind, filters, cancelled):
            count = 0
            path = staging / filename
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream, lineterminator='\n')
                writer.writerow(header)
                for row in rows:
                    if count % 4096 == 0 and cancelled():
                        raise RuntimeError('Data export cancelled')
                    writer.writerow(row)
                    count += 1
            files.append({'filename': filename, 'columns': list(header), 'row_count': count,
                          'units': units, 'sha256': _file_sha256(path)})
        metadata = {'schema': 1, 'kind': kind, 'scope': scope, 'filters': filters,
                    'dataset_manifest_sha256': manifest_sha, 'source': data.metadata['source'],
                    'scientific_metadata': data.metadata, 'files': files}
        if kind == 'SUMMARY':
            metadata['view_summary'] = summary
        (staging / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        if cancelled():
            raise RuntimeError('Data export cancelled')
        if kind == 'SUMMARY' and _file_sha256(source / 'manifest.json') != manifest_sha:
            raise ValueError('Export Dataset changed before publishing the summary')
        if final.exists():
            raise FileExistsError(final)
        staging.rename(final)
        return {'directory': str(final), 'files': files}
    finally:
        cleanup_staging(output, token)


def export_report(request, directory, cancelled=lambda: False):
    return export_dataset(request['dataset'], request['output_directory'], request['kind'],
                          request.get('scope', 'ALL'), request.get('filters'), cancelled,
                          request.get('export_token'), request['dataset_sha256'], request.get('view_snapshot'))
