"""Offline installed-extension worker checks for external result imports."""
import hashlib
import importlib
from pathlib import Path
import time

import bpy

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
assert Path(bpy.utils.user_resource('CONFIG')).resolve().is_relative_to(ROOT / 'outputs')
assert bpy.ops.extensions.package_install_files(
    filepath=str(ROOT / 'outputs/dist/qcblender-0.0.1.zip'), repo='user_default',
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


cube = ROOT / 'outputs' / 'vesta-comparison' / 'ch4-alpha-mo8.cube'
color = ROOT / 'outputs' / 'paired-fields' / 'numeric-color.cube'
table = ROOT / 'outputs' / 'nocv-acceptance' / 'table.qcdata'
reference, digest = identity(table)
paired = run('import_pair', geometry_source=str(cube), color_source=str(color),
             method='IGMH', geometry_unit='dimensionless', color_unit='electron/bohr^3',
             reference_dataset=reference, reference_sha256=digest)
assert len(paired.metadata['fields']) == 2
assert paired.metadata['analysis']['reference']['status'] == 'geometry_matched'
for field in paired.metadata['fields']:
    assert field['vdb_sha256']

log = ROOT / 'outputs' / 'log-examples' / 'water_neutral_nbo_opt_freq.out'
reference, digest = identity(ROOT / 'outputs' / 'nbo-acceptance' / 'reference.qcdata')
nbo = run('import_nbo', source=str(log), job_index=1, block_index=0,
          reference_dataset=reference, reference_sha256=digest)
assert len(nbo.metadata['analysis']['interactions']) == 2

reference, digest = identity(table)
nocv = run('import_nocv', source=str(cube), table_dataset=reference,
           table_sha256=digest, pair_number=1, spin='Total', unit='electron/bohr^3')
assert nocv.metadata['analysis']['pair']['pair'] == 1
assert nocv.metadata['fields'][0]['vdb_sha256']
print('Offline installed extension import_pair, import_nbo, import_nocv Passed')
