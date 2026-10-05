"""Restricted entry point executed by the same Blender binary in background mode."""
import argparse
import importlib
import json
import os
from pathlib import Path
import sys
import traceback
import hashlib
import shutil
import time


def main():
    import bpy
    parser = argparse.ArgumentParser()
    parser.add_argument('--module', required=True)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    directory = args.directory.resolve(strict=True)
    report = {'status': 'failed'}
    cache_key, cache_hit, cache_rejected = None, False, None
    last_progress = 0.0

    def progress(fraction, phase='Evaluating field'):
        nonlocal last_progress
        now = time.monotonic()
        if fraction < 1 and now - last_progress < .2:
            return
        last_progress = now
        candidate = directory / 'progress.pending.json'
        candidate.write_text(json.dumps({'phase': phase, 'fraction': fraction}), encoding='utf-8')
        os.replace(candidate, directory / 'progress.json')

    try:
        progress(0, 'Loading scientific runtime')
        if not args.module.startswith('bl_ext.') or args.module.rsplit('.', 1)[-1] != 'qcblender':
            raise ValueError('Expected an installed QCBlender extension module')
        bpy.ops.preferences.addon_enable(module=args.module)
        package = importlib.import_module(args.module)
        if Path(package.__file__).resolve().parent != Path(__file__).resolve().parent:
            raise ValueError('Worker and enabled extension have different origins')
        request = json.loads((directory / 'request.json').read_text(encoding='utf-8'))
        if request.get('schema') != 1 or request.get('job_id') != directory.name:
            raise ValueError('Invalid worker request identity or schema')
        if request['action'] == 'diagnose':
            diagnostics = importlib.import_module(args.module + '.diagnostics')
            report = diagnostics.check_runtime()
            report['status'] = 'succeeded' if report['ok'] else 'failed'
        elif request['action'] == 'inspect_source':
            source = Path(request['source'])
            if source.stat().st_size > 512 * 1024**2:
                raise MemoryError('Source exceeds 512 MiB import limit')
            snapshot = directory / 'input' / source.name
            snapshot.parent.mkdir()
            shutil.copy2(source, snapshot)
            gaussian = importlib.import_module(args.module + '.gaussian_log')
            report = dict(gaussian.inspect_log(snapshot), status='succeeded')
        elif request['action'] == 'contours':
            storage = importlib.import_module(args.module + '.data')
            contours = importlib.import_module(args.module + '.contours')
            report = contours.contour_report(request, storage.load_dataset, lambda: (directory / 'cancel').exists())
        elif request['action'] == 'export_data':
            exports = importlib.import_module(args.module + '.data_export')
            report = dict(exports.export_report(request, directory,
                          lambda: (directory / 'cancel').exists()), status='succeeded')
        elif request['action'] == 'field_range':
            storage = importlib.import_module(args.module + '.data')
            summarize = importlib.import_module(args.module + '.field_ranges').field_range
            report = field_range_report(request, storage, summarize, lambda: (directory / 'cancel').exists())
        elif request['action'] in ('import', 'import_pair', 'import_nbo', 'import_nocv', 'evaluate', 'rebuild_cache', 'declare_field'):
            storage = importlib.import_module(args.module + '.data')
            static_reference = importlib.import_module(args.module + '.static_reference')
            if request['action'] == 'import_nocv':
                source = Path(request['source'])
                if source.stat().st_size > 512 * 1024**2:
                    raise MemoryError('Source exceeds 512 MiB import limit')
                snapshot = directory / 'input' / source.name
                snapshot.parent.mkdir()
                shutil.copy2(source, snapshot)
                table_dir = Path(request['table_dataset'])
                digest = hashlib.sha256((table_dir / 'manifest.json').read_bytes()).hexdigest()
                if digest != request['table_sha256']:
                    raise ValueError('ETS-NOCV table changed during import')
                table = static_reference.load_static_reference(table_dir, request['table_sha256'])
                nocv = importlib.import_module(args.module + '.nocv')
                data = nocv.import_nocv(snapshot, table,
                                        request['pair_number'], request['spin'], request['unit'])
            elif request['action'] == 'import_nbo':
                source = Path(request['source'])
                if source.stat().st_size > 512 * 1024**2:
                    raise MemoryError('Source exceeds 512 MiB import limit')
                snapshot = directory / 'input' / source.name
                snapshot.parent.mkdir()
                shutil.copy2(source, snapshot)
                reference_dir = Path(request['reference_dataset'])
                digest = hashlib.sha256((reference_dir / 'manifest.json').read_bytes()).hexdigest()
                if digest != request['reference_sha256']:
                    raise ValueError('Reference calculation changed during import')
                static_reference.load_static_reference(reference_dir, request['reference_sha256'])
                nbo = importlib.import_module(args.module + '.nbo')
                data = nbo.associated_nbo(snapshot, request['job_index'], request['block_index'], reference_dir)
            elif request['action'] == 'import_pair':
                external = importlib.import_module(args.module + '.external_fields')
                paths = [Path(request[key]) for key in ('geometry_source', 'color_source')]
                if any(path.stat().st_size > 512 * 1024**2 for path in paths):
                    raise MemoryError('Source exceeds 512 MiB import limit')
                snapshot = directory / 'input'
                snapshot.mkdir()
                copied = []
                for index, path in enumerate(paths):
                    target = snapshot / f'{index}-{path.name}'
                    shutil.copy2(path, target)
                    copied.append(target)
                data = external.pair_cubes(*copied, request['method'],
                                           request['geometry_unit'], request['color_unit'],
                                           request.get('iri_exponent'),
                                           igmh_component=request.get('igmh_component', 'unknown'),
                                           igmh_fragments=request.get('igmh_fragments'),
                                           igmh_declaration_source=request.get('igmh_declaration_source', ''))
                data.metadata['source']['filename'] = paths[0].name
                data.metadata['analysis']['geometry_source']['filename'] = paths[0].name
                data.metadata['analysis']['color_source']['filename'] = paths[1].name
                reference_dir = Path(request['reference_dataset'])
                reference_digest = hashlib.sha256((reference_dir / 'manifest.json').read_bytes()).hexdigest()
                if reference_digest != request['reference_sha256']:
                    raise ValueError('Reference calculation changed during import')
                association = importlib.import_module(args.module + '.association')
                data.metadata['analysis']['reference'] = association.compare_sources(
                    static_reference.load_static_reference(reference_dir, request['reference_sha256']), data)
            elif request['action'] == 'import':
                readers = importlib.import_module(args.module + '.readers')
                source = Path(request['source'])
                if source.stat().st_size > 512 * 1024**2:
                    raise MemoryError('Source exceeds 512 MiB import limit')
                snapshot = directory / 'input' / source.name
                snapshot.parent.mkdir()
                shutil.copy2(source, snapshot)
                expected = request.get('source_sha256')
                if expected and hashlib.sha256(snapshot.read_bytes()).hexdigest() != expected:
                    raise ValueError('Source changed after preview; preview the file again')
                data = readers.read_source(snapshot, job_index=request.get('job_index', 0))
            else:
                digest = hashlib.sha256((Path(request['dataset']) / 'manifest.json').read_bytes()).hexdigest()
                if request.get('dataset_sha256', digest) != digest:
                    raise ValueError('Dataset changed after the request was created')
                data = storage.load_dataset(request['dataset'])
                if request['action'] == 'declare_field':
                    units = {'orbital_amplitude': 'bohr^-3/2', 'electron_number_density': 'electron/bohr^3',
                             'spin_density': 'electron/bohr^3', 'electrostatic_potential': 'hartree/e'}
                    scalar = next(f for f in data.metadata['fields'] if f['array'] == request['field_array'])
                    if scalar['quantity'] != 'unknown_scalar' or request['quantity'] not in (*units, 'custom'):
                        raise ValueError('Only unknown scalar fields accept a supported user interpretation')
                    quantity = request['quantity']
                    unit = units.get(quantity)
                    if quantity == 'custom':
                        quantity, unit = request.get('custom_quantity', '').strip(), request.get('custom_unit', '').strip()
                        if (not quantity or not unit or len(quantity) > 120 or len(unit) > 80
                                or any(ord(c) < 32 for c in quantity + unit)):
                            raise ValueError('Custom quantity and unit must be nonempty printable text')
                    scalar.update(quantity=quantity, unit=unit,
                                  interpretation='user_assigned', original_quantity='unknown_scalar',
                                  numeric_conversion='none; user confirmed values use declared units')
                if request['action'] == 'evaluate':
                    from importlib.metadata import version
                    evaluator = importlib.import_module(args.module + '.evaluate')
                    parameters = {k: v for k, v in request['parameters'].items() if k != 'memory_mb'}
                    identity = {'dataset': digest, 'grid': request['grid'], 'parameters': parameters,
                                'backend': version('qc-gbasis'),
                                'evaluator': hashlib.sha256(Path(evaluator.__file__).read_bytes()).hexdigest(),
                                'numpy': version('numpy'), 'blender': bpy.app.version_string}
                    cache_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
                    cache_root = directory.parent / 'cache'
                    index = cache_root / (cache_key + '.json')
                    if index.exists():
                        try:
                            cached = storage.resolve_asset(cache_root, json.loads(index.read_text(encoding='utf-8'))['dataset'])
                            candidate = storage.load_dataset(cached)
                            for scalar in candidate.metadata['fields']:
                                storage.volume_cache(cached, scalar)
                            cache_hit = True
                        except (ValueError, OSError, KeyError) as error:
                            cache_rejected = str(error)
                    if cache_hit:
                        shutil.copytree(storage.filesystem_path(cached), storage.filesystem_path(directory / 'dataset'))
                    grid = evaluator.Grid(**request['grid'])
                    if not cache_hit:
                        data = evaluator.evaluate_field(data, grid, **request['parameters'],
                            cancelled=lambda: (directory / 'cancel').exists(), progress=progress)
            if (directory / 'cancel').exists():
                raise InterruptedError('Request cancelled before publishing results')
            if not cache_hit:
                progress(1, 'Building display cache')
                (directory / 'dataset').mkdir()
                for index, field in enumerate(data.metadata.get('fields', [])):
                    field['vdb'] = 'field.vdb' if index == 0 else f'field-{index}.vdb'
                    write_volume(data, directory / 'dataset' / field['vdb'], index)
                    field['vdb_sha256'] = storage._file_sha256(directory / 'dataset' / field['vdb'])
                    field['display_precision'] = 'float32'
                storage.save_dataset(data, directory / 'dataset')
                if cache_key:
                    project = importlib.import_module(args.module + '.project')
                    copied = project.copy_dataset(directory / 'dataset', cache_root)
                    pending_index = cache_root / (directory.name + '.pending.json')
                    pending_index.write_text(json.dumps({'dataset': copied.relative_to(cache_root).as_posix()}), encoding='utf-8')
                    os.replace(pending_index, cache_root / (cache_key + '.json'))
            report = {'status': 'succeeded', 'dataset': 'dataset',
                      'source_sha256': data.metadata['source']['sha256'],
                      'cache_hit': cache_hit, 'cache_rejected': cache_rejected}
        else:
            raise ValueError('Unsupported worker action: ' + str(request['action']))
    except Exception as error:
        report = {'status': 'failed', 'error': f'{type(error).__name__}: {error}'}
        traceback.print_exc()
    report.update(schema=1, job_id=directory.name)
    candidate = directory / 'result.pending.json'
    candidate.write_text(json.dumps(report, indent=2), encoding='utf-8')
    os.replace(candidate, directory / 'result.json')


def field_range_report(request, storage, summarize, cancelled):
    expected = request.get('dataset_sha256')
    if not isinstance(expected, str) or not expected:
        raise ValueError('Dataset manifest SHA-256 is required')
    dataset = Path(request['dataset'])
    manifest = dataset / 'manifest.json'

    def check_source():
        if hashlib.sha256(manifest.read_bytes()).hexdigest() != expected:
            raise ValueError('Dataset changed after the request was created')
        if cancelled():
            raise InterruptedError('Request cancelled before publishing results')

    check_source()
    data = storage.load_dataset(dataset)
    if cancelled():
        raise InterruptedError('Request cancelled before publishing results')
    summary = summarize(data, request['field_array'])
    check_source()
    return dict(summary, status='succeeded', dataset_sha256=expected)


def write_volume(data, path, index=0):
    import numpy as np
    import openvdb
    field = data.metadata['fields'][index]
    matrix = np.eye(4)
    matrix[:3, :3] = field['steps']
    matrix[3, :3] = field['origin']
    transform = openvdb.createLinearTransform(matrix.tolist())
    values = data.arrays[field['array']]
    valid = data.arrays[field['valid_mask']]
    grids = []
    for name, array in [('qc_value', values), ('qc_negative', -values), ('qc_valid', valid)]:
        grid = openvdb.FloatGrid()
        grid.name = name
        grid.copyFromArray(np.ascontiguousarray(array, dtype=np.float32))
        grid.transform = transform
        grids.append(grid)
    openvdb.write(str(path), grids=grids)


if __name__ == '__main__':
    main()
