"""Check repaired parsers through installed workers and native table operators."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path

MODULE = 'bl_ext.user_default.qcblender'


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def job(action, expected='succeeded', **arguments):
    pending = module('blender.jobs').Job(action, **arguments)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        receipt = pending.poll()
        if receipt is not None:
            require(receipt['status'] == expected, str(receipt))
            return pending.directory / 'dataset', receipt
        time.sleep(.05)
    pending.cancel()
    raise TimeoutError(str(pending.directory))


def snapshot():
    return {obj.name: {'manifest': obj['qc_dataset_sha256'],
        'arrays': {key: hashlib.sha256(value.tobytes()).hexdigest() for key, value in
            module('data').load_dataset(bpy.path.abspath(obj['qc_dataset'])).arrays.items()}}
        for obj in bpy.context.scene.objects if obj.get('qc_dataset')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reopen', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=bool(args.reopen))
    report = {'status': 'Running', 'independent_human_review': 'Not Run'}
    bpy.ops.preferences.addon_enable(module=MODULE)
    try:
        if args.reopen:
            bpy.ops.wm.open_mainfile(filepath=str(args.reopen.resolve()))
            original = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
            require(snapshot() == original['saved_snapshot'], 'Portable scientific identity changed')
            for obj in bpy.context.scene.objects:
                if obj.get('qc_dataset'):
                    require(Path(bpy.path.abspath(obj['qc_dataset'])).resolve().is_relative_to(
                        args.reopen.resolve().with_suffix('.qcdata')), 'Dataset outside portable project')
            report['cold_reopen'] = 'Passed'
        else:
            sources = out / 'sources'
            sources.mkdir()
            healthy = ROOT / 'tests/data/cclib/water_mp2.log'
            combined = sources / 'failed-then-water.log'
            combined.write_bytes(b' Entering Gaussian System, Link 0=g16\n # B3LYP/6-31G\n\n'
                                 b' Error termination via Lnk1e\n' + healthy.read_bytes())
            _, preview = job('inspect_source', source=str(combined))
            require([row['status'] for row in preview['jobs']] == ['failed', 'normal'], 'Gaussian statuses merged')
            selected, imported = job('import', source=str(combined), job_index=1,
                                    source_sha256=preview['source']['sha256'])
            plain, _ = job('import', source=str(healthy), job_index=0)
            selected_data, plain_data = [module('data').load_dataset(p) for p in (selected, plain)]
            require(selected_data.arrays.keys() == plain_data.arrays.keys(), 'Selected job array names differ')
            for key in selected_data.arrays:
                np.testing.assert_array_equal(selected_data.arrays[key], plain_data.arrays[key])
            _, failure = job('import', expected='failed', source=str(combined), job_index=0)
            require('explicit geometry' in failure['error'], 'Failed first job inherited geometry')
            report['gaussian'] = {'preview': preview, 'selected_import': imported, 'failed_first_job': failure,
                                  'all_arrays_match_standalone': 'Passed'}
            for obj in list(bpy.data.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            fchk = input_path('sop/c10-c13/multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/COBH3.fch')
            directory, _ = job('import', source=str(fchk))
            atoms = module('blender.views').atom_view(directory)
            atoms.name = 'P2 CO-BH3 reference'
            module('blender.layers').activate(bpy.context, atoms)
            table = input_path('sop/c10-c13/multiwfn-cobh3-20260927/COBH3-ETS-NOCV.txt')
            raw = table.read_text(encoding='utf-8')
            original = module('external_results').ets_nocv_pairs(table, 'kcal/mol')
            line_index = original[0]['source_line'] - 1
            lines = raw.splitlines()
            errors = {}
            for field, column in [('positive_eigenvalue', 3), ('negative_eigenvalue', 6),
                                  ('positive_energy', 4), ('negative_energy', 7)]:
                changed = list(lines)
                tokens = changed[line_index].split()
                tokens[column] = f'{float(tokens[column]) + .01:.5f}'
                changed[line_index] = ' '.join(tokens)
                path = sources / (field + '.txt')
                path.write_text(raw + '\n'.join(changed) + '\n', encoding='utf-8')
                before = snapshot(), set(bpy.data.objects.keys()), set(bpy.data.meshes.keys())
                try:
                    bpy.ops.qcblender.import_ets_nocv(output_path=str(path), energy_unit='kcal/mol')
                except RuntimeError as error:
                    require(field in str(error) and 'lines 7 and' in str(error), str(error))
                    errors[field] = str(error)
                else:
                    raise ValueError('Conflicting native import succeeded: ' + field)
                require(before == (snapshot(), set(bpy.data.objects.keys()), set(bpy.data.meshes.keys())),
                        'Rejected import changed scientific scene')
            identical = sources / 'identical-duplicate.txt'
            identical.write_text(raw + raw, encoding='utf-8')
            require(bpy.ops.qcblender.import_ets_nocv(output_path=str(identical), energy_unit='kcal/mol') == {'FINISHED'},
                    'Identical duplicates rejected')
            added = next(obj for obj in bpy.data.objects if obj.get('qc_analysis_role') == 'ets_nocv')
            pairs = module('data').load_dataset(bpy.path.abspath(added['qc_dataset'])).metadata['analysis']['pairs']
            require(pairs == original and len(pairs) == 9, 'Identical duplicates changed first provenance')
            module('blender.layers').activate(bpy.context, atoms)
            module('blender.project').save_project(out / 'p2-input.blend')
            report.update(nocv={'conflicts_rejected_without_scene_changes': errors, 'identical_pairs': pairs},
                          saved_snapshot=snapshot(), sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                                             for p in sorted(sources.iterdir())})
        report['status'] = 'Passed'
    except Exception as error:
        report.update(status='Failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        (out / ('cold-reopen.json' if args.reopen else 'checks.json')).write_text(
            json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
