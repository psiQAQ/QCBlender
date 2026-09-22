"""Run with Blender's bundled Python -I; never imports the build environment."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ['PATH'] = os.pathsep.join([str(Path(sys.executable).parent),
                                     os.environ.get('SystemRoot', 'C:/Windows') + '/System32'])
sys.path.insert(0, str(ROOT / 'outputs' / 'science'))
import numpy as np
from iodata import load_one
from gbasis.wrappers import from_iodata
from gbasis.integrals.overlap import overlap_integral
from gbasis.evals.eval import evaluate_basis
from gbasis.evals.density import evaluate_density
from gbasis.evals.electrostatic_potential import electrostatic_potential
import gbasis

source = ROOT / 'tests/data/iodata/water_sto3g_hf_g03.fchk'
mol = load_one(str(source))
basis = from_iodata(mol)
s = overlap_integral(basis)
c = mol.mo.coeffs
p = (c * mol.mo.occs) @ c.T
points = np.array([[0.3, 0.2, 0.1], [1., 1., 1.], [-2., 1., 3.]])
ao = evaluate_basis(basis, points)
rho = evaluate_density(p, basis, points)
esp = electrostatic_potential(basis, p, points, mol.atcoords, mol.atnums.astype(float))
np.testing.assert_allclose(c.T @ s @ c, np.eye(c.shape[1]), atol=2e-7)
np.testing.assert_allclose(np.trace(p @ s), mol.nelec, atol=2e-6)
np.testing.assert_allclose(rho, np.einsum('mi,mn,ni->i', ao, p, ao), atol=1e-10)
assert np.isfinite(esp).all()
report = {'status': 'Passed', 'python': sys.executable, 'numpy': np.__version__,
          'numpy_origin': np.__file__, 'backend_origin': gbasis.__file__,
          'electron_count': float(np.trace(p @ s)),
          'orthonormality_max_error': float(np.max(np.abs(c.T @ s @ c - np.eye(c.shape[1])))),
          'density': rho.tolist(), 'esp': esp.tolist(),
          'limitation': 'Internal consistency only; independent reference is checked by run_science_tests.py'}
(ROOT / 'outputs/science-probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
