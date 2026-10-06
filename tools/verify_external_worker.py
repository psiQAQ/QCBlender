"""Offline installed-extension worker checks for external result imports."""
import argparse
import hashlib
import importlib
from pathlib import Path
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--candidate', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--reference-root', type=Path, default=ROOT)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=False)
import bpy
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
from tools.comparison_fixture import comparison_source, write_comparison_cube
MODULE = 'bl_ext.user_default.qcblender'
config = Path(bpy.utils.user_resource('CONFIG')).resolve()
assert any(config.is_relative_to(ROOT / directory) for directory in ('outputs', 'validation/work'))
assert bpy.ops.extensions.package_install_files(
    filepath=str(args.candidate.resolve()), repo='user_default',
    enable_on_install=True, overwrite=True) == {'FINISHED'}
jobs = importlib.import_module(MODULE + '.blender.jobs')
storage = importlib.import_module(MODULE + '.data')


def run(action, **args):
    job = jobs.Job(action, **args)
    until = time.monotonic() + 180
    while time.monotonic() < until:
        report = job.poll()
        if report is not None:
            assert report['status'] == 'succeeded', (report, (job.directory / 'worker.log').read_text(errors='replace'))
            return storage.load_dataset(job.directory / 'dataset')
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


def identity(path):
    return str(path), hashlib.sha256((path / 'manifest.json').read_bytes()).hexdigest()


folder = input_path('sop/c07-c09-research/phenol-2026-09-27/igmh', args.reference_root)
geometry, color = folder / 'dg_inter.cub', folder / 'sl2r.cub'
cube_reader = importlib.import_module(MODULE + '.cube').read_cube
pair_reference = OUT / 'pair-reference.qcdata'
storage.save_dataset(cube_reader(geometry), pair_reference)
reference, digest = identity(pair_reference)
paired = run('import_pair', geometry_source=str(geometry), color_source=str(color),
             method='IGMH', geometry_unit='electron/bohr^4', color_unit='electron/bohr^3',
             reference_dataset=reference, reference_sha256=digest)
assert len(paired.metadata['fields']) == 2
assert paired.metadata['analysis']['reference']['status'] == 'geometry_matched'
for field in paired.metadata['fields']:
    assert field['vdb_sha256']

log = input_path('log-examples/water_neutral_nbo_opt_freq.out', args.reference_root)
nbo_reference = OUT / 'nbo-reference.qcdata'
storage.save_dataset(importlib.import_module(MODULE + '.gaussian_log').read_log(log, 1), nbo_reference)
reference, digest = identity(nbo_reference)
nbo = run('import_nbo', source=str(log), job_index=1, block_index=0,
          reference_dataset=reference, reference_sha256=digest)
assert len(nbo.metadata['analysis']['interactions']) == 2

wavefunction = OUT / 'wavefunction.qcdata'
storage.save_dataset(run('import', source=str(comparison_source(args.reference_root))), wavefunction)
field = run('evaluate', dataset=str(wavefunction),
            grid={'origin': [-3, -3, -3], 'steps': [[.2, 0, 0], [0, .2, 0], [0, 0, .2]],
                  'shape': [31, 31, 31]},
            parameters={'quantity': 'orbital_amplitude', 'orbital': 8, 'spin': 'alpha', 'memory_mb': 512})
cube = write_comparison_cube(field, OUT / 'ch4-alpha-mo8.cube')
table_file = OUT / 'synthetic-ets.txt'
table_file.write_text('Note: All energies are given in kcal/mol\n'
    'Pair Energy | Orbital Eigenvalue Energy | Orbital Eigenvalue Energy\n'
    '-----\n1 -2.50 6 0.12000 -3.10 7 -0.12000 0.60\n', encoding='utf-8')
table = OUT / 'table.qcdata'
storage.save_dataset(importlib.import_module(MODULE + '.analysis_data').import_ets(
    cube_reader(cube), table_file, 'kcal/mol'), table)
reference, digest = identity(table)
nocv = run('import_nocv', source=str(cube), table_dataset=reference,
           table_sha256=digest, pair_number=1, spin='Total', unit='electron/bohr^3')
assert nocv.metadata['analysis']['pair']['pair'] == 1
assert nocv.metadata['fields'][0]['vdb_sha256']
print('Offline installed extension import_pair, import_nbo, numeric import_nocv Passed; real NOCV fixture Not Run')
