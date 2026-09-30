"""Generate owned tutorial wavefunctions and Multiwfn results; no dependency installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--reference-root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1]
REF = args.reference_root.resolve()
RUN = args.output.resolve()
if any(RUN.iterdir()) if RUN.exists() else False:
    raise FileExistsError(f'Refusing to overwrite run: {RUN}')
RUN.mkdir(parents=True, exist_ok=True)
for key in ('TMP', 'TEMP', 'TMPDIR'):
    os.environ[key] = str(RUN)
sys.path.insert(0, str(REF / 'outputs/science'))
sys.path.insert(0, str(ROOT))
import numpy as np
import pyscf
from pyscf import gto, scf, dft, lib
from pyscf.tools import molden
from iodata import load_one, dump_one
from iodata.overlap import compute_overlap
from gbasis.wrappers import from_iodata
from gbasis.evals.density import evaluate_density
from qcblender.readers import read_fchk

lib.num_threads(2)
records = {}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def calculate(group, name, atoms, spin=0, method='RHF', basis='sto-3g'):
    folder = RUN / group
    folder.mkdir(exist_ok=True)
    mol = gto.M(atom=atoms, basis=basis, spin=spin, charge=0, symmetry=False,
                unit='Angstrom', verbose=4, output=str(folder / (name + '-scf.log')))
    mf = scf.UHF(mol) if spin else (dft.RKS(mol) if method == 'RB3LYP' else scf.RHF(mol))
    if method == 'RB3LYP':
        mf.xc = 'b3lyp'
        mf.grids.level = 3
    mf.conv_tol = 1e-10
    mf.max_cycle = 100
    mf.chkfile = str(folder / (name + '.chk'))
    energy = mf.kernel()
    assert mf.converged, f'{name}: SCF not converged'
    molden.from_scf(mf, str(folder / (name + '.molden')))
    data = load_one(str(folder / (name + '.molden')))
    data.energy, data.lot, data.obasis_name = float(energy), method, basis
    data.run_type = 'energy'
    data.title = f'QCBlender tutorial; PySCF {pyscf.__version__}; {name}; CC BY 4.0'
    orbital = folder / (name + '-orbitals.fchk')
    dump_one(data, str(orbital), fmt='fchk')
    data = load_one(str(orbital))
    if spin:
        ca, cb = data.mo.coeffs[:, :data.mo.norba], data.mo.coeffs[:, data.mo.norba:]
        oa, ob = data.mo.occs[:data.mo.norba], data.mo.occs[data.mo.norba:]
        da, db = (ca * oa) @ ca.T, (cb * ob) @ cb.T
        data.one_rdms['scf'], data.one_rdms['scf_spin'] = da + db, da - db
    else:
        data.one_rdms['scf'] = (data.mo.coeffs * data.mo.occs) @ data.mo.coeffs.T
    data.atcharges['mulliken'] = mf.mulliken_pop(verbose=0)[1]
    data.moments[(1, 'c')] = mf.dip_moment(unit='AU', verbose=0)
    final = folder / (name + '.fchk')
    dump_one(data, str(final), fmt='fchk')
    # Multiwfn reads electron counts consecutively; preserve all values in Gaussian order.
    lines = final.read_text(encoding='ascii').splitlines()
    counts = [next(line for line in lines if line.startswith(label)) for label in
              ('Number of electrons ', 'Number of alpha electrons ', 'Number of beta electrons ')]
    lines = [line for line in lines if line not in counts[1:]]
    index = lines.index(counts[0])
    lines[index+1:index+1] = counts[1:]
    final.write_text('\n'.join(lines)+'\n', encoding='ascii', newline='\n')
    reread = load_one(str(final))
    parsed = read_fchk(final)
    np.testing.assert_allclose(parsed.arrays['positions'], mol.atom_coords(unit='Angstrom'), atol=1e-7, rtol=0)
    np.testing.assert_allclose(reread.energy, energy, atol=6e-7, rtol=0)
    density = (reread.mo.coeffs * reread.mo.occs) @ reread.mo.coeffs.T
    overlap = compute_overlap(reread.obasis, reread.atcoords)
    np.testing.assert_allclose(np.trace(density @ overlap), mol.nelectron, atol=2e-6)
    points = np.array([[0.1,0.2,0.3], [1.2,-0.7,0.6], [-2.,0.8,-0.3]])
    ao = mol.eval_gto('GTOval_sph', points)
    dm = mf.make_rdm1()
    if spin:
        dm = dm.sum(axis=0)
    reference = np.einsum('pi,ij,pj->p', ao, dm, ao)
    observed = evaluate_density(density, from_iodata(reread), points)
    np.testing.assert_allclose(observed, reference, atol=2e-7, rtol=2e-6)
    records[group + '/' + name] = dict(producer='PySCF', version=pyscf.__version__, method=method,
        basis=basis, charge=0, spin=spin, multiplicity=spin+1, coordinates_angstrom=parsed.arrays['positions'].tolist(),
        atomic_numbers=parsed.arrays['atomic_numbers'].tolist(), electron_count=mol.nelectron,
        energy_hartree=float(reread.energy), full_precision_energy_hartree=float(energy),
        orbitals=parsed.metadata['orbitals'], mulliken_charges=parsed.arrays['charge_mulliken'].tolist(),
        dipole_e_bohr=parsed.arrays['dipole'].tolist(), fchk_sha256=sha(final),
        density_max_abs_error=float(np.max(abs(observed-reference))), scf_converged=True)
    (RUN / 'generation-report.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    mol.stdout.close()
    print(json.dumps({'sample':group+'/'+name,'energy_hartree':float(energy)}), flush=True)

calculate('P01','o2-uhf', 'O 0 0 -0.6; O 0 0 0.6', spin=2, method='UHF')
water = 'O 0 0 0; H 0.7586 0 0.5043; H -0.7586 0 0.5043; O 0 0 2.9; H 0.7586 0 3.4043; H -0.7586 0 3.4043'
calculate('P03','water-dimer',water, basis='6-31g(d)')
co = 'C 0 0 0; O 0 0 -1.13'
bh3 = 'B 0 0 1.7; H 1.19 0 1.7; H -0.595 1.03057 1.7; H -0.595 -1.03057 1.7'
for name, atoms in [('complex',co+'; '+bh3),('co',co),('bh3',bh3)]:
    calculate('P05',name,atoms,method='RB3LYP',basis='6-31g(d)')

PACKAGE = REF / 'submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64'
EXE = PACKAGE / 'Multiwfn.exe'

def multiwfn(group, analysis, source, commands, settings_overrides=None):
    work = RUN / group / analysis
    work.mkdir()
    settings = (PACKAGE / 'settings.ini').read_text(encoding='utf-8')
    for key, value in dict(nthreads='4', isilent='1', **(settings_overrides or {})).items():
        settings, count = re.subn(rf'(?m)^(\s*{key}\s*=\s*)\S+', lambda m: m[1]+value, settings)
        assert count == 1, key
    (work / 'settings.ini').write_bytes(settings.encode('utf-8'))
    shutil.copyfile(RUN / group / source, work / source)
    if group == 'P05':
        for name in ('co.fchk','bh3.fchk'):
            shutil.copyfile(RUN / group / name, work / name)
    (work / 'stdin.txt').write_bytes(('\r\n'.join(commands)+'\r\n').encode('ascii'))
    env = dict(os.environ, OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', Multiwfnpath=str(PACKAGE))
    started = time.monotonic()
    with (work/'stdin.txt').open('rb') as inp, (work/'stdout.log').open('wb') as out, (work/'stderr.log').open('wb') as err:
        result = subprocess.run([str(EXE), source], cwd=work, env=env, stdin=inp, stdout=out, stderr=err,
                                timeout=1800, creationflags=subprocess.CREATE_NO_WINDOW)
    report = dict(producer='Multiwfn', version='2026.9.20', executable_sha256=sha(EXE),
                  input_sha256=sha(work/source), commands=commands, settings_overrides=settings_overrides or {},
                  returncode=result.returncode, seconds=time.monotonic()-started)
    (work/'run.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    result.check_returncode()
    log = (work/'stdout.log').read_text(encoding='utf-8', errors='replace')
    if 'Error:' in log:
        raise RuntimeError(f'Multiwfn error: inspect {work / "stdout.log"}')
    expected = {'igmh':'dg_inter.cub', 'iri':'func2.cub', 'esp':'surfanalysis.pdb',
                'aim':'CPprop.txt', 'nocv':'nocv-pair1.cub'}[analysis]
    if not (work/expected).is_file():
        raise FileNotFoundError(f'Multiwfn did not generate {work/expected}')
    print(json.dumps({'analysis':analysis, **report}),flush=True)

multiwfn('P03','igmh','water-dimer.fchk',['20','11','2','1-3','4-6','-10','1','2','3','0','0','q'],
         {'IGMvdwscl':'0','IRI_rhocut':'0','uservar':'0'})
multiwfn('P03','iri','water-dimer.fchk',['20','4','-10','1','2','3','0','0','q'],
         {'IGMvdwscl':'0','IRI_rhocut':'0','uservar':'0'})
multiwfn('P03','esp','water-dimer.fchk',['12','0','1','2','9','all','-100,100','40','3','-1','-1','q'])
multiwfn('P03','aim','water-dimer.fchk',['2','2','3','4','8','-4','6','0','-5','6','0','7','0','-10','q'])
multiwfn('P05','nocv','complex.fchk',['23','2','co.fchk','bh3.fchk','-2','-4','ets-nocv.txt','-5','1',
         '7','1','nocv-pair1.cub','q','6','1','nocv-orb1.cub','6',str(records['P05/complex']['orbitals']['norba']),'nocv-orb-negative.cub','-10','q'])
print('GENERATION_PASSED', flush=True)
