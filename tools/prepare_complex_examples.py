"""Inspect real examples and prepare external NCI Cubes in a background Blender."""
import hashlib
import importlib
import json
from pathlib import Path
from importlib.metadata import version
import time
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/complex-examples'
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
SOURCES = input_path('complex-examples')
MODULE = 'bl_ext.user_default.qcblender'
repo = next(r for r in bpy.context.preferences.extensions.repos if r.module == 'user_default')
if not (Path(repo.directory) / 'qcblender/blender_manifest.toml').is_file():
    bpy.ops.extensions.package_install_files(filepath=str(ROOT / 'outputs/dist/qcblender-0.0.1.zip'),
                                            repo='user_default', enable_on_install=True, overwrite=True)
else:
    bpy.ops.preferences.addon_enable(module=MODULE)
readers = importlib.import_module(MODULE + '.readers')
storage = importlib.import_module(MODULE + '.data')

report = {}
for name in ('dvb_un_sp.fchk', 'dvb_ir.out', 'Trp_polar.fchk', 'Trp_polar.log',
             'chemtools-h2o_dimer_pbe_sto3g.fchk'):
    data = readers.read_source(SOURCES / name)
    storage.save_dataset(data, OUT / 'prepared' / name)
    report[name] = {'metadata': data.metadata, 'arrays': {k: list(v.shape) for k, v in data.arrays.items()},
                    'dipole': data.arrays.get('dipole', np.array([])).tolist()}
    print(name, data.metadata.get('method'), len(data.arrays['positions']),
          data.metadata.get('electron_count'), report[name]['dipole'], flush=True)

fchk = storage.load_dataset(OUT / 'prepared/Trp_polar.fchk')
log = storage.load_dataset(OUT / 'prepared/Trp_polar.log')
np.testing.assert_array_equal(fchk.arrays['atomic_numbers'], log.arrays['atomic_numbers'])
error = float(np.max(np.abs(fchk.arrays['positions'] - log.arrays['positions'])))
assert error < 2e-5, error
assert np.linalg.norm(fchk.arrays['dipole']) > .1
report['tryptophan_pair_position_error_angstrom'] = error
np.testing.assert_allclose(fchk.arrays['dipole'] * 2.541746473, log.arrays['dipole'], atol=6e-5)
report['tryptophan_pair_dipole_check'] = 'Passed (e*bohr converted to Debye)'

# External case preparation only: these descriptors are not plugin evaluator options.
from gbasis.evals.density import evaluate_density, evaluate_density_gradient, evaluate_density_hessian
evaluator = importlib.import_module(MODULE + '.evaluate')
dimer = storage.load_dataset(OUT / 'prepared/chemtools-h2o_dimer_pbe_sto3g.fchk')
mol, basis, pa, pb = evaluator.prepare(dimer)
dm = pa + pb
coords = dimer.arrays['positions']
origin = coords.min(axis=0) - 1.5
spacing = .12
shape = np.ceil((coords.max(axis=0) + 1.5 - origin) / spacing).astype(int) + 1
points = origin + np.indices(shape).reshape(3, -1).T * spacing
start = time.monotonic()
rho, rdg, signed = (np.empty(len(points)) for _ in range(3))
for offset in range(0, len(points), 4096):
    end = min(offset + 4096, len(points))
    xyz = points[offset:end] / storage.BOHR_ANGSTROM
    density = evaluate_density(dm, basis, xyz)
    gradient = evaluate_density_gradient(dm, basis, xyz)
    hessian = evaluate_density_hessian(dm, basis, xyz)
    rho[offset:end] = density
    rdg[offset:end] = np.linalg.norm(gradient, axis=1) / (2 * (3*np.pi**2)**(1/3) * np.maximum(density, 1e-30)**(4/3))
    signed[offset:end] = np.sign(np.linalg.eigvalsh(hessian)[:, 1]) * density

# Independently check analytic density derivatives with centered finite differences.
probe = np.array([[.2, .1, .3], [-.3, -.2, .2]]) / storage.BOHR_ANGSTROM
step = 1e-4
numerical = np.column_stack([(evaluate_density(dm, basis, probe + np.eye(3)[i]*step)
                            - evaluate_density(dm, basis, probe - np.eye(3)[i]*step))/(2*step) for i in range(3)])
np.testing.assert_allclose(numerical, evaluate_density_gradient(dm, basis, probe), rtol=2e-5, atol=1e-8)
numerical_hessian = np.stack([(evaluate_density_gradient(dm, basis, probe + np.eye(3)[i]*step)
                              - evaluate_density_gradient(dm, basis, probe - np.eye(3)[i]*step))/(2*step) for i in range(3)], axis=2)
np.testing.assert_allclose(numerical_hessian, evaluate_density_hessian(dm, basis, probe), rtol=2e-5, atol=1e-8)
generated = OUT / 'external-fields'
generated.mkdir(exist_ok=True)

def cube(name, values, comment):
    path = generated / name
    with path.open('w', encoding='ascii', newline='\n') as stream:
        stream.write('Water dimer PBE/STO-3G | external preparation\n' + comment + '\n')
        stream.write(f'{len(coords)} ' + ' '.join(f'{v/storage.BOHR_ANGSTROM:.10f}' for v in origin) + '\n')
        for count, axis in zip(shape, np.eye(3)*spacing/storage.BOHR_ANGSTROM):
            stream.write(f'{count} ' + ' '.join(f'{v:.10f}' for v in axis) + '\n')
        for z, xyz in zip(dimer.arrays['atomic_numbers'], coords/storage.BOHR_ANGSTROM):
            stream.write(f'{z} {z:.1f} ' + ' '.join(f'{v:.10f}' for v in xyz) + '\n')
        for offset in range(0, len(values), 6):
            stream.write(' '.join(f'{v:.10e}' for v in values[offset:offset+6]) + '\n')
    readback = readers.read_source(path)
    np.testing.assert_allclose(readback.arrays['cube_0'].ravel(), values, rtol=1e-9, atol=1e-12)
    return {'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

files = [cube('rdg.cube', rdg, 'RDG dimensionless; unfiltered'),
         cube('signed-density.cube', signed, 'sign(lambda2)*rho electron/bohr^3; unscaled'),
         cube('rdg-display.cube', np.where((rho >= 1e-6) & (rho <= .05), rdg, 10.),
              'RDG display: rho outside [1e-6,0.05] electron/bohr^3 set to 10')]
report['external_preparation'] = {'status': 'Passed', 'backend': 'qc-gbasis ' + version('qc-gbasis'),
    'source_sha256': dimer.metadata['source']['sha256'], 'shape': shape.tolist(), 'spacing_angstrom': spacing,
    'seconds': time.monotonic()-start, 'derivative_finite_difference_check': 'Passed',
    'cube_roundtrip': 'Passed', 'rdg_formula': '|grad(rho)| / (2*(3*pi^2)^(1/3)*rho^(4/3))',
    'signed_density': 'sign(second eigenvalue of ascending density Hessian)*rho',
    'display_density_window_electron_bohr3': [1e-6, .05], 'outside_window_display_value': 10., 'files': files}
# NCIPLOT's archived density file stores 100*sign(lambda2)*rho, not raw rho.
reference = readers.read_source(SOURCES / 'chemtools-h2o_dimer_pbe_sto3g-dens.cube')
reference_rdg = readers.read_source(SOURCES / 'chemtools-h2o_dimer_pbe_sto3g-grad.cube')
np.testing.assert_allclose(reference.arrays['positions'], coords, atol=3e-7)
field = reference.metadata['fields'][0]
xyz = (np.array(field['origin']) + np.indices(field['shape']).reshape(3, -1).T @ np.array(field['steps'])) / storage.BOHR_ANGSTROM
ref_rho = evaluate_density(dm, basis, xyz)
ref_signed = np.sign(np.linalg.eigvalsh(evaluate_density_hessian(dm, basis, xyz))[:, 1]) * ref_rho
ref_s = np.linalg.norm(evaluate_density_gradient(dm, basis, xyz), axis=1) / (2*(3*np.pi**2)**(1/3)*ref_rho**(4/3))
printed_signed = reference.arrays['cube_0'].ravel() / 100
printed_s = reference_rdg.arrays['cube_0'].ravel()
unfiltered = printed_s < 99
np.testing.assert_allclose(printed_signed, ref_signed, atol=5e-6, rtol=1e-4)
np.testing.assert_allclose(printed_s[unfiltered], ref_s[unfiltered], atol=2e-4, rtol=1e-4)
report['external_preparation']['nciplot_reference'] = {
    'status': 'Passed', 'density_scale_removed': 100,
    'signed_density_max_abs_error': float(np.max(np.abs(printed_signed-ref_signed))),
    'rdg_max_abs_error_unfiltered': float(np.max(np.abs(printed_s[unfiltered]-ref_s[unfiltered]))),
    'excluded_rdg_sentinel_points': int((~unfiltered).sum())}
(OUT / 'source-inspection.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
