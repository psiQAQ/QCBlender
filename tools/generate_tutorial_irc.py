"""Owned H2O2 TS and genuine bidirectional IRC using existing PySCF/geomeTRIC."""
import argparse, csv, hashlib, json, os, sys
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser()
parser.add_argument('--reference-root',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args(); ROOT=Path(__file__).resolve().parents[1]; REF=a.reference_root.resolve(); RUN=a.output.resolve()
if RUN.exists(): raise FileExistsError(RUN)
RUN.mkdir(parents=True)
for key in ('TMP','TEMP','TMPDIR'): os.environ[key]=str(RUN)
sys.path[:0]=[str(REF/'outputs/science'),str(ROOT)]
import pyscf, geometric
from pyscf import gto,scf,lib
from pyscf.geomopt.geometric_solver import PySCFEngine
from pyscf.hessian.thermo import harmonic_analysis
from pyscf.tools import molden
from iodata import load_one,dump_one
from qcblender.readers import read_fchk
from qcblender.irc import import_irc,import_irc_mayer
lib.num_threads(2);lib.param.TMPDIR=str(RUN)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
mol=gto.M(atom='O 0 0 -0.725; O 0 0 0.725; H 0.92 0 -0.95; H -0.92 0 0.95',basis='sto-3g',unit='Angstrom',symmetry=False,verbose=4,output=str(RUN/'pyscf.log'))
initial_coords=mol.atom_coords(unit='Angstrom').copy()
mf=scf.RHF(mol);mf.conv_tol=1e-11;mf.max_cycle=100;mf.chkfile=str(RUN/'ts-initial.chk');mf.kernel();assert mf.converged
hess=mf.Hessian().kernel(); hp=RUN/'ts-initial-hessian.txt';np.savetxt(hp,hess.transpose(0,2,1,3).reshape(12,12))
engine=PySCFEngine(mf.nuc_grad_method().as_scanner());engine.assert_convergence=True;engine.M.build_topology()
trajectory=geometric.optimize.run_optimizer(customengine=engine,input=str(RUN/'ts'),transition=True,hessian='file:'+str(hp),maxiter=100,
 convergence_grms=1e-5,convergence_gmax=2e-5,convergence_energy=1e-9)
ts=engine.mol.copy();mf=scf.RHF(ts);mf.conv_tol=1e-11;mf.kernel();assert mf.converged
hess=mf.Hessian().kernel();frequencies=harmonic_analysis(ts,hess,imaginary_freq=False)['freq_wavenumber'];assert np.count_nonzero(frequencies<0)==1,frequencies
hp=RUN/'ts-hessian.txt';np.savetxt(hp,hess.transpose(0,2,1,3).reshape(12,12))
report=dict(producer={'pyscf':pyscf.__version__,'geometric':geometric.__version__},method='RHF',basis='STO-3G',charge=0,spin=0,
 initial_coordinates_angstrom=initial_coords.tolist(),ts_coordinates_angstrom=ts.atom_coords(unit='Angstrom').tolist(),
 ts_energy_hartree=float(mf.e_tot),ts_frequencies_cm_minus1=frequencies.tolist(),imaginary_mode_count=1,
 ts_gradient_max=float(abs(mf.nuc_grad_method().kernel()).max()),irc_direction='both',license='CC-BY-4.0')
write(RUN/'report.json',report)
engine=PySCFEngine(mf.nuc_grad_method().as_scanner());engine.assert_convergence=True;engine.M.build_topology()
evaluations=[]
def callback(env):
 evaluations.append(dict(cycle=env['self'].cycle,coordinates_bohr=env['coords'].tolist(),energy_hartree=float(env['energy']),gradient_hartree_per_bohr=env['gradients'].tolist()))
 write(RUN/'irc-evaluations.json',evaluations)
engine.callback=callback
progress=geometric.optimize.run_optimizer(customengine=engine,input=str(RUN/'irc'),irc=True,irc_direction='both',hessian='file:'+str(hp),maxiter=200,trust=.1,
 convergence_grms=3e-4,convergence_gmax=4.5e-4,convergence_energy=1e-6)
progress.write(str(RUN/'irc-accepted.xyz'))
coords=np.array(progress.xyzs)
errors=np.linalg.norm(coords-np.array(report['ts_coordinates_angstrom']),axis=(1,2));idx=int(np.argmin(errors))
assert errors[idx]<1e-5 and 0<idx<len(coords)-1,(idx,len(coords),errors.tolist())
chosen=[idx-1,idx,idx+1];steps=[];mayer=[]
for step,index in enumerate(chosen,1):
 name=f'step-{step:03d}';mol=ts.copy().set_geom_(coords[index],unit='Angstrom');mf=scf.RHF(mol);mf.conv_tol=1e-11;mf.chkfile=str(RUN/(name+'.chk'));mf.kernel();assert mf.converged
 molden.from_scf(mf,str(RUN/(name+'.molden')));data=load_one(str(RUN/(name+'.molden')));data.energy=float(mf.e_tot);data.lot='RHF';data.obasis_name='STO-3G';data.run_type='energy';data.title=f'QCBlender owned IRC; accepted frame {index}; CC BY 4.0'
 orbital=RUN/(name+'-orbitals.fchk');dump_one(data,str(orbital),fmt='fchk');data=load_one(str(orbital));data.one_rdms['scf']=(data.mo.coeffs*data.mo.occs)@data.mo.coeffs.T
 path=RUN/(name+'.fchk');dump_one(data,str(path),fmt='fchk');parsed=read_fchk(path)
 np.testing.assert_allclose(parsed.arrays['positions'],coords[index],atol=1e-7,rtol=0)
 ps=mf.make_rdm1()@mol.intor_symmetric('int1e_ovlp');slices=mol.aoslice_by_atom()[:,2:];orders=[];lines=['Producer: PySCF '+pyscf.__version__+'; actual converged RHF/STO-3G AO matrices','Mayer unit: dimensionless; Multiwfn-compatible syntax','Bond orders with absolute value']
 for aa in range(4):
  for bb in range(aa+1,4):
   p,q=slices[aa];r,s=slices[bb];value=float(np.sum(ps[p:q,r:s]*ps[r:s,p:q].T));orders.append([aa+1,bb+1,value]);lines.append(f'# {len(orders)}: {aa+1}({mol.atom_symbol(aa)}) {bb+1}({mol.atom_symbol(bb)}) {value:.12f}')
 text=RUN/(name+'-mayer-pyscf.txt');text.write_text('\n'.join(lines)+'\n',encoding='utf-8');mayer.append((step,text.name));steps.append((step,path.name))
 report.setdefault('selected_steps',[]).append(dict(step=step,accepted_frame_zero_based=index,energy_hartree=float(parsed.metadata['energies'][0]['value_hartree']),full_precision_energy_hartree=float(mf.e_tot),fchk_sha256=sha(path),mayer=orders))
for name,header,rows in [('steps.csv',['step','fchk'],steps),('mayer-pyscf.csv',['step','mayer_output'],mayer)]:
 with (RUN/name).open('w',encoding='utf-8',newline='') as stream:
  w=csv.writer(stream);w.writerow(header);w.writerows(rows)
irc=import_irc(RUN/'steps.csv');result=import_irc_mayer(irc,RUN/'mayer-pyscf.csv');assert result.arrays['mayer_orders'].shape==(3,6)
report.update(accepted_frame_count=len(coords),ts_accepted_frame_zero_based=idx,irc_status='converged both directions',parse_status='Passed')
write(RUN/'report.json',report);print(json.dumps(report),flush=True)
