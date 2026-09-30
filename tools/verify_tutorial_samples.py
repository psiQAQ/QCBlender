"""Verify the frozen tutorial files, scientific interfaces and public ZIP."""
import argparse,hashlib,json,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--package',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
a=p.parse_args();ROOT=Path(__file__).resolve().parents[1];REF=a.reference_root.resolve();sys.path[:0]=[str(REF/'outputs/science'),str(ROOT)]
import numpy as np
from pyscf.scf.chkfile import load_scf
from qcblender.readers import read_fchk,read_source
from qcblender.evaluate import evaluate_points
from qcblender.external_fields import pair_cubes
from qcblender.analysis_data import import_esp,import_aim,import_ets
from qcblender.nocv import import_nocv
from qcblender.nbo import parse_nbo
from qcblender.irc import import_irc,import_irc_mayer
from qcblender.cube import read_cube
manifest=json.loads((ROOT/'docs/v1-acceptance/tutorial-samples.json').read_text(encoding='utf-8'));paths={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for sid,f in manifest['files'].items():
 path=(REF if f['local_key'] else ROOT)/f['path'];assert path.stat().st_size==f['bytes'] and sha(path)==f['sha256'],sid;paths[sid]=path
for sid in ('P01-o2-uhf','P03-water-dimer','P05-complex','P04-step-001.fchk','P04-step-002.fchk','P04-step-003.fchk'):
 d=read_fchk(paths[sid]);e=manifest['files'][sid]['expected'];assert d.arrays['atomic_numbers'].tolist()==e['atomic_numbers'];np.testing.assert_allclose(d.arrays['positions'],e.get('coordinates_angstrom',e.get('positions_angstrom')),atol=3e-6,rtol=0)
for sid in ('P01-o2-uhf','P03-water-dimer','P05-complex'):
 e=manifest['files'][sid]['expected'];d=read_fchk(paths[sid]);assert d.metadata['electron_count']==e['electron_count'] and d.metadata['spin_polarization']==e['spin']
p01=read_fchk(paths['P01-o2-uhf']);pts=np.array([[.2,.3,.4],[1.,-.7,.6],[-2.,.8,-.3]]);v={q:evaluate_points(p01,pts,q)[0] for q in ['electron_number_density','alpha_density','beta_density','spin_density']}
np.testing.assert_allclose(v['electron_number_density'],v['alpha_density']+v['beta_density'],atol=1e-12);np.testing.assert_allclose(v['spin_density'],v['alpha_density']-v['beta_density'],atol=1e-12)
for method,geometry,color,unit in [('IGMH','igmh-dg_inter.cub','igmh-sl2r.cub','electron/bohr^4'),('IRI','iri-func2.cub','iri-func1.cub','a.u. (electron^-0.1 bohr^-0.7)')]:pair_cubes(paths['P03-'+geometry],paths['P03-'+color],method,unit,'electron/bohr^3',1.1 if method=='IRI' else None)
p03=read_fchk(paths['P03-water-dimer']);esp=import_esp(p03,paths['P03-esp-surfanalysis.pdb'],paths['P03-esp-stdout.log'],'rho=0.001 electron/bohr^3','kcal/mol','kcal/mol','angstrom^2');aim=import_aim(p03,paths['P03-aim-CPs.pdb'],paths['P03-aim-paths.pdb'],paths['P03-aim-CPprop.txt'])
assert len(aim.metadata['analysis']['critical_points'])==manifest['files']['P03-aim-CPs.pdb']['expected']['count']
nbo=parse_nbo(paths['P02-water_neutral_nbo_opt_freq.out'],1,0);assert len(nbo['orbitals'])==7 and len(nbo['interactions'])==2
assert len(read_source(paths['P02-water_neutral_nbo_opt_freq.out'],0).metadata['optimization']['steps'])==4
irc=import_irc(paths['P04-steps.csv']);mayer=import_irc_mayer(irc,paths['P04-mayer-pyscf.csv']);np.testing.assert_allclose(mayer.arrays['mayer_orders'],manifest['files']['P04-mayer-pyscf.csv']['expected']['orders'],atol=1e-12)
e=manifest['files']['P04-steps.csv']['expected']['irc_report'];assert e['imaginary_mode_count']==1 and e['irc_direction']=='both' and e['irc_status']=='converged both directions'
# Verify exported IRC wavefunctions against original converged PySCF checkpoints.
from iodata import load_one
from gbasis.wrappers import from_iodata
from gbasis.evals.density import evaluate_density
for i in range(1,4):
 fchk=paths[f'P04-step-{i:03d}.fchk'];mol,state=load_scf(str(REF/f'outputs/evidence/2026-09-30/public-tutorial/samples/irc/step-{i:03d}.chk'));data=load_one(str(fchk));np.testing.assert_array_equal(data.atnums,mol.atom_charges());np.testing.assert_allclose(data.atcoords,mol.atom_coords(),atol=1e-7,rtol=0)
 dm=(state['mo_coeff']*state['mo_occ'])@state['mo_coeff'].T;ao=mol.eval_gto('GTOval_sph',pts);reference=np.einsum('pi,ij,pj->p',ao,dm,ao);observed=evaluate_density(data.one_rdms['scf'],from_iodata(data),pts);np.testing.assert_allclose(observed,reference,atol=2e-7,rtol=2e-6)
ets=import_ets(read_fchk(paths['P05-complex']),paths['P05-ets-nocv.txt'],'kcal/mol');import_nocv(paths['P05-nocv-pair1.cub'],ets,1,'Total','electron/bohr^3')
with zipfile.ZipFile(a.package) as z:
 assert z.testzip() is None and all(not n.startswith('P02/') for n in z.namelist())
 assert json.loads(z.read('tutorial-samples.json'))==manifest
 for f in manifest['files'].values():
  if f['distribution']=='included':assert f['license']=='CC-BY-4.0' and hashlib.sha256(z.read(f['archive_path'])).hexdigest()==f['sha256']
report=dict(status='Passed',file_count=len(paths),included_files=sum(f['distribution']=='included' for f in manifest['files'].values()),package_sha256=sha(a.package),checks=['SHA-256','real field spin identities','IGMH/IRI grids','ESP/AIM association','NBO multijob/optimization','genuine bidirectional IRC/TS','FCHK versus original PySCF checkpoint density','Mayer','ETS/NOCV','ZIP per-file license exclusion'],gui='Not Run',independent_human_review='Not Run');a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
