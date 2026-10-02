"""Freeze real samples and package only owned CC BY 4.0 data."""
import argparse, hashlib, json, shutil, sys, urllib.request, zipfile
from pathlib import Path
p=argparse.ArgumentParser()
for n in ('reference-root','run','irc-run','evidence'):p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();ROOT=Path(__file__).resolve().parents[1];REF=a.reference_root.resolve();RUN=a.run.resolve();IRC=a.irc_run.resolve();E=a.evidence.resolve()
if E.exists():raise FileExistsError(E)
E.mkdir(parents=True)
sys.path[:0]=[str(REF/'outputs/science'),str(ROOT)]
import numpy as np
from qcblender.readers import read_fchk,read_source
from qcblender.evaluate import evaluate_points
from qcblender.external_fields import pair_cubes
from qcblender.analysis_data import import_esp,import_aim,import_ets
from qcblender.nocv import import_nocv
from qcblender.nbo import parse_nbo
from qcblender.irc import import_irc,import_irc_mayer
from qcblender.cube import read_cube
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={};sources={};checks={};records=json.loads((RUN/'generation-report.json').read_text());ir=json.loads((IRC/'report.json').read_text())
def include(sid,source,rel,role,expected=None,quantity=None,unit=None):
 base=ROOT/'tests/data/tutorial' if source.stat().st_size<512*1024 else REF/'tests/data/local/public-tutorial'
 target=base/rel;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():raise FileExistsError(target)
 shutil.copy2(source,target);path=target.relative_to(ROOT if base.is_relative_to(ROOT) else REF).as_posix()
 files[sid]=dict(id=sid,path=path,archive_path=rel,local_key=path.removeprefix('tests/data/local/') if 'tests/data/local/' in path else None,bytes=target.stat().st_size,sha256=sha(target),distribution='included',license='CC-BY-4.0',license_evidence='https://creativecommons.org/licenses/by/4.0/',source_url=None,acquire='Extract public tutorial ZIP retaining archive_path layout.',role=role,producer='PySCF 2.13.1 / Multiwfn 2026.9.20 / geomeTRIC 1.1.1; see evidence',calculation_group=rel.split('/')[0],quantity=quantity,unit=unit,expected=expected or {})
 sources[sid]=target
for key,r in records.items():
 g,n=key.split('/');include(g+'-'+n,RUN/g/(n+'.fchk'),key+'.fchk','reference wavefunction',r)
for g,n in [('P01','o2-uhf'),('P03','water-dimer')]:include(g+'-fch',RUN/g/(n+'.fchk'),g+'/'+n+'.fch','byte-identical alias',{'same_as':g+'-'+n})
for kind,names in {'igmh':['dg_inter.cub','sl2r.cub'],'iri':['func2.cub','func1.cub']}.items():
 for n in names:
  d=read_cube(RUN/'P03'/kind/n);f=d.metadata['fields'][0];v=d.arrays[f['array']];geo=n in ('dg_inter.cub','func2.cub')
  unit=('electron/bohr^4' if kind=='igmh' else 'a.u. (electron^-0.1 bohr^-0.7)') if geo else 'electron/bohr^3'
  include('P03-'+kind+'-'+n,RUN/'P03'/kind/n,'P03/'+kind+'/'+n,'geometry' if geo else 'color',dict(shape=f['shape'],origin=f['origin'],steps=f['steps'],minimum=float(v.min()),maximum=float(v.max())),('delta_g_inter' if kind=='igmh' else 'iri_function') if geo else 'sign_lambda2_rho',unit)
include('P03-cube',RUN/'P03/igmh/sl2r.cub','P03/color.cube','byte-identical alias',{'same_as':'P03-igmh-sl2r.cub'},'sign_lambda2_rho','electron/bohr^3')
for kind,names in {'esp':['surfanalysis.pdb','stdout.log'],'aim':['CPs.pdb','paths.pdb','CPprop.txt']}.items():
 for n in names:include('P03-'+kind+'-'+n,RUN/'P03'/kind/n,'P03/'+kind+'/'+n,'external '+kind+' records')
for n in ['steps.csv','mayer-pyscf.csv']+[f'step-{i:03d}{s}' for i in range(1,4) for s in ['.fchk','-mayer-pyscf.txt']]:include('P04-'+n,IRC/n,'P04/'+n,'genuine bidirectional IRC/Mayer')
for n in ('ets-nocv.txt','nocv-pair1.cub'):include('P05-'+n,RUN/'P05/nocv'/n,'P05/nocv/'+n,'external ETS-NOCV')
index=json.loads((ROOT/'tests/data/local-inputs.json').read_text(encoding='utf-8'));key='log-examples/water_neutral_nbo_opt_freq.out';item=index['files'][key];source=REF/item['path'];assert sha(source)==item['sha256']
url='https://raw.githubusercontent.com/cclib/cclib-data/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian16/water_neutral_nbo_opt_freq.out'
files['P02-water_neutral_nbo_opt_freq.out']=dict(id='P02-water_neutral_nbo_opt_freq.out',path=item['path'],archive_path=None,local_key=key,bytes=item['bytes'],sha256=item['sha256'],distribution='external-acquisition',license='unverified data permission',license_evidence='https://cclib.readthedocs.io/en/stable/how_to_install.html',source_url=url,acquire='Obtain fixed original URL separately and verify SHA; this grants no redistribution permission. Copy identical .log alias to test the other extension.',role='Gaussian multijob opt/freq/NBO',producer='Gaussian 16 A.03 / NBO 3.1',calculation_group='P02',expected={});sources['P02-water_neutral_nbo_opt_freq.out']=source
try:
 with urllib.request.urlopen(url,timeout=30) as response:blob=response.read()
 assert hashlib.sha256(blob).hexdigest()==item['sha256'];availability=dict(status='Passed',url=url,sha256=item['sha256'],bytes=len(blob),permission='unverified')
except (OSError,AssertionError) as error:availability=dict(status='Failed',url=url,error=str(error),permission='unverified')
d=read_fchk(sources['P01-o2-uhf']);pts=np.array([[.2,.3,.4],[1.,-.7,.6],[-2.,.8,-.3]]);v={q:evaluate_points(d,pts,q)[0] for q in ['electron_number_density','alpha_density','beta_density','spin_density']}
np.testing.assert_allclose(v['electron_number_density'],v['alpha_density']+v['beta_density'],atol=1e-12);np.testing.assert_allclose(v['spin_density'],v['alpha_density']-v['beta_density'],atol=1e-12);assert d.metadata['spin_polarization']==2 and d.metadata['electron_count']==16;checks['P01']='Passed'
d=read_fchk(sources['P03-water-dimer'])
for kind,geo,color,unit in [('IGMH','igmh-dg_inter.cub','igmh-sl2r.cub','electron/bohr^4'),('IRI','iri-func2.cub','iri-func1.cub','a.u. (electron^-0.1 bohr^-0.7)')]:
 paired=pair_cubes(sources['P03-'+geo],sources['P03-'+color],kind,unit,'electron/bohr^3',1.1 if kind=='IRI' else None);np.testing.assert_allclose(paired.arrays['positions'],d.arrays['positions'],atol=3e-6,rtol=0)
esp=import_esp(d,sources['P03-esp-surfanalysis.pdb'],sources['P03-esp-stdout.log'],'rho=0.001 electron/bohr^3','kcal/mol','kcal/mol','angstrom^2').metadata['analysis']
aim=import_aim(d,sources['P03-aim-CPs.pdb'],sources['P03-aim-paths.pdb'],sources['P03-aim-CPprop.txt']).metadata['analysis']
files['P03-esp-surfanalysis.pdb']['expected']=dict(extrema=esp['extrema'],area_sum_angstrom2=esp['area_sum']);files['P03-esp-stdout.log']['expected']=dict(area_bins=esp['area_bins'],area_sum_angstrom2=esp['area_sum'])
for n,k in [('CPs.pdb','critical_points'),('paths.pdb','paths'),('CPprop.txt','properties')]:files['P03-aim-'+n]['expected']=dict(count=len(aim[k]),records=aim[k])
checks['P03']='Passed';log=read_source(source,1);opt=read_source(source,0);nbo=parse_nbo(source,1,0);assert len(nbo['orbitals'])==7 and len(nbo['interactions'])==2
files['P02-water_neutral_nbo_opt_freq.out']['expected']=dict(job_number=2,job_index=1,block_number=1,block_index=0,atomic_numbers=log.arrays['atomic_numbers'].tolist(),positions_angstrom=log.arrays['positions'].tolist(),frequencies_cm_minus1=log.arrays['mode_frequencies'].tolist(),ir_intensities_km_mol=log.arrays['mode_ir_intensities'].tolist(),nbo_count=7,e2_count=2,nbo=nbo,optimization_job_number=1,optimization_step_count=len(opt.metadata['optimization']['steps']),optimization_energies_hartree=[s['energy']['value_hartree'] for s in opt.metadata['optimization']['steps']]);checks['P02_local']='Passed'
irc=import_irc(sources['P04-steps.csv']);mayer=import_irc_mayer(irc,sources['P04-mayer-pyscf.csv']);assert irc.arrays['irc_positions'].shape==(3,4,3)
files['P04-steps.csv']['expected']=dict(energies_hartree=irc.arrays['irc_energies'].tolist(),steps=3,irc_report=ir);files['P04-mayer-pyscf.csv']['expected']=dict(pairs=mayer.arrays['mayer_pairs'].tolist(),orders=mayer.arrays['mayer_orders'].tolist(),unit='dimensionless')
for i in range(1,4):
 d=read_fchk(sources[f'P04-step-{i:03d}.fchk']);files[f'P04-step-{i:03d}.fchk']['expected']=dict(atomic_numbers=d.arrays['atomic_numbers'].tolist(),positions_angstrom=d.arrays['positions'].tolist(),energy_hartree=d.metadata['energies'][0]['value_hartree'])
checks['P04']='Passed';ets=import_ets(read_fchk(sources['P05-complex']),sources['P05-ets-nocv.txt'],'kcal/mol');nocv=import_nocv(sources['P05-nocv-pair1.cub'],ets,1,'Total','electron/bohr^3');pair=ets.metadata['analysis']['pairs'][0];get=lambda d:d.arrays[d.metadata['fields'][0]['array']]
a=read_cube(RUN/'P05/nocv/nocv-orb1.cub');b=read_cube(RUN/'P05/nocv/nocv-orb-negative.cub');err=float(np.max(abs(pair['positive_eigenvalue']*get(a)**2+pair['negative_eigenvalue']*get(b)**2-get(nocv))));assert err<3e-6
files['P05-ets-nocv.txt']['expected']=dict(pairs=ets.metadata['analysis']['pairs'],energy_unit='kcal/mol',energy_method='Actual complex KS reconstruction; Multiwfn approximation, not F_TS',pair_density_formula_max_abs_error=err)
f=nocv.metadata['fields'][0];v=get(nocv);files['P05-nocv-pair1.cub']['expected']=dict(shape=f['shape'],minimum=float(v.min()),maximum=float(v.max()),net_integral_electron=float(v.sum()*abs(np.linalg.det(np.array(f['steps'])))/0.529177210903**3));checks['P05']='Passed'
cases={}
def case(cid,g,ids,**gui):cases[cid]=dict(group=g,files=ids,gui=gui,local_parse_status='Passed',gui_status='Not Run',display_defaults_status='proposed; root visual check required',public_material_status='external; permission unverified' if g=='P02' else 'included',grid_defaults=dict(spacing_angstrom=.7,margin_angstrom=3))
case('C01','P01',['P01-o2-uhf','P01-fch'],alpha_mo=9,beta_mo=7,alpha_homo=8,beta_homo=6,isovalue=.045,spin_isovalue=.002)
case('C02','P02',['P02-water_neutral_nbo_opt_freq.out'],job_number=2,mode_number=3,amplitude_angstrom=.35,cycles_per_second=1)
case('C03','P03',['P03-igmh-sl2r.cub','P03-cube'],quantity='sign_lambda2_rho',unit='electron/bohr^3',scale_factor=1,isovalue=.02)
case('C04','P03',['P03-water-dimer'],density_isovalue=.004,color_minimum=-.05,color_center=0,color_maximum=.05,color_unit='hartree/e',charge_method='mulliken',dipole_scale_angstrom_per_debye=1.5)
case('C05','P03',['P03-water-dimer','P03-fch'],keep_h_atom_number=2,oxygen_atom_numbers=[1,4])
case('C06','P02',['P02-water_neutral_nbo_opt_freq.out'],job_number=2,block_number=1,nbo_number=1,e2_record_number=1)
case('C07','P03',['P03-water-dimer','P03-igmh-dg_inter.cub','P03-igmh-sl2r.cub','P03-iri-func2.cub','P03-iri-func1.cub'],fragments_1based=[[1,2,3],[4,5,6]],igmh_isovalue=.005,iri_isovalue=1,iri_exponent=1.1,color_minimum=-.04,color_center=0,color_maximum=.04,color_unit='electron/bohr^3')
case('C08','P03',['P03-water-dimer','P03-esp-surfanalysis.pdb','P03-esp-stdout.log'],surface_definition='rho=0.001 electron/bohr^3',extrema_unit='kcal/mol',center_unit='kcal/mol',area_unit='angstrom^2')
case('C09','P03',['P03-water-dimer','P03-aim-CPs.pdb','P03-aim-paths.pdb','P03-aim-CPprop.txt'],coordinate_unit='angstrom',point_number=1)
case('C10','P04',['P04-steps.csv']+[f'P04-step-{i:03d}.fchk' for i in range(1,4)],step_numbers=[1,2,3])
case('C11','P04',['P04-mayer-pyscf.csv']+[f'P04-step-{i:03d}-mayer-pyscf.txt' for i in range(1,4)],atom_pair_1based=[1,2],unit='dimensionless')
case('C12','P05',['P05-complex','P05-ets-nocv.txt'],energy_unit='kcal/mol',pair_number=1,spin='Total')
case('C13','P05',['P05-complex','P05-ets-nocv.txt','P05-nocv-pair1.cub'],pair_number=1,spin='Total',unit='electron/bohr^3',isovalue=.003)
manifest=dict(schema=1,date='2026-09-30',attribution='QCBlender contributors',groups={g:dict(local_parse_status='Passed',public_material_status='external; permission unverified' if g=='P02' else 'included') for g in ['P01','P02','P03','P04','P05']},files=files,cases=cases,checks=checks,source_availability=availability,nodes={f'N{i:02d}':dict(case=c,status='Not Run') for i,c in enumerate(['C05','C05','C05','C01','C01','C04','C04','C04','C01','C01','C04','C02','C09','C07','C01','all','C04','all'],1)},interaction_examples=dict(atom_number_base=1,measurement_distance_atoms=[1,4],expected_distance_angstrom=2.9,measurement_angle_atoms=[2,1,3],label_atom_number=1,profile_start_angstrom=[0,-2,1.45],profile_end_angstrom=[0,2,1.45],profile_case='C04',slice_center_angstrom=[0,0,1.45],read_cursor_inside_angstrom=[0,0,1.45],read_cursor_invalid_angstrom=[0,0,0],read_cursor_outside_angstrom=[20,20,20]),blockers=[dict(group='P02',reason='Original Gaussian/NBO log excluded: data redistribution permission unverified. Separate acquisition grants no redistribution right.')],regression=dict(log_job_number=2,next_fchk='P03-water-dimer',expected_fchk_job_number=1,expected_fchk_atomic_numbers=[8,1,1,8,1,1],gui_status='Not Run'),tolerances=dict(coordinates_angstrom=3e-6,scalar_energy_hartree=6e-7,printed_log_energy_hartree=1e-9,cube_formula_abs=3e-6))
for sid,f in files.items():
 g=f['calculation_group'];base='P01-o2-uhf' if g=='P01' else 'P03-water-dimer' if g=='P03' else 'P05-complex' if g=='P05' else None
 if base:
  e=files[base]['expected'];f['calculation']={k:e[k] for k in ('method','basis','charge','spin','multiplicity','electron_count')};f['calculation']['reference_file_id']=base
 elif g=='P04':f['calculation']=dict(method='RHF',basis='STO-3G',charge=0,spin=0,multiplicity=1,electron_count=18,producer='PySCF 2.13.1 / geomeTRIC 1.1.1')
 else:f['calculation']=dict(method='RHF',basis='STO-3G',charge=0,spin=0,multiplicity=1,electron_count=10)
 f['producer']='Gaussian 16 A.03 / NBO 3.1' if g=='P02' else 'PySCF 2.13.1 / geomeTRIC 1.1.1' if g=='P04' else 'PySCF 2.13.1; IOData 1.0.1 FCHK writer' if '.fch' in f['path'] else 'Multiwfn 2026.9.20'
files['P05-nocv-pair1.cub'].update(quantity='nocv_deformation_density',unit='electron/bohr^3')
files['P05-ets-nocv.txt']['unit']='kcal/mol';files['P04-mayer-pyscf.csv']['unit']='dimensionless'
files['P03-esp-surfanalysis.pdb']['unit']='kcal/mol; coordinates angstrom'
files['P03-esp-stdout.log']['unit']='center kcal/mol; area angstrom^2; percentage %'
write(ROOT/'docs/v1-acceptance/tutorial-samples.json',manifest)
public=ROOT/'tests/data/tutorial';(public/'LICENSE').write_text('Generated sample data: CC BY 4.0\nAttribution: QCBlender contributors\nhttps://creativecommons.org/licenses/by/4.0/\nOnly distribution=included files are covered.\n',encoding='utf-8')
(public/'NOTICE.md').write_text('# Public tutorial samples\n\nOwned PySCF/geomeTRIC/Multiwfn data: CC BY 4.0, attribution QCBlender contributors. P01/P03/P05 are unoptimized illustrative geometries; P04 is a genuine optimized first-order saddle and converged bidirectional IRC. P02 is excluded; see manifest acquisition/licensing limitations.\n\nCite Multiwfn: Tian Lu, Feiwu Chen, J. Comput. Chem. 33, 580 (2012), DOI:10.1002/jcc.22885; Tian Lu, J. Chem. Phys. 161, 082503 (2024), DOI:10.1063/5.0216272. ETS-NOCV energies use actual complex KS reconstruction, an approximation rather than F_TS. No scientific grid-convergence claim. Identify Cube annotates values and performs no scaling.\n',encoding='utf-8')
for sid,item in files.items():
 if item['distribution']=='included' and item['local_key']:index['files'][item['local_key']]=dict(id=sid,path=item['path'],bytes=item['bytes'],sha256=item['sha256'],role=item['role'],license='CC-BY-4.0',source_url=None,provenance='Owned tutorial calculation; tutorial-samples.json',used_by=[c for c,v in cases.items() if sid in v['files']])
for key in index['files']:
 if key.startswith('complex-examples/') and index['files'][key].get('license')=='BSD-3-Clause':index['files'][key]['data_license_status']='unverified; code license does not establish data permission'
write(ROOT/'tests/data/local-inputs.json',index);shutil.copytree(RUN,E/'owned');shutil.copytree(IRC,E/'irc')
for n in ('generate_tutorial_samples.py','generate_tutorial_irc.py','finalize_tutorial_samples.py'):shutil.copy2(ROOT/'tools'/n,E/n)
write(E/'tutorial-samples.json',manifest);package=RUN.parent/'qcblender-public-tutorial-samples-v1.zip'
if package.exists():raise FileExistsError(package)
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(ROOT/'docs/v1-acceptance/tutorial-samples.json','tutorial-samples.json')
 for sid,item in files.items():
  if item['distribution']=='included':assert sha(sources[sid])==item['sha256'];z.write(sources[sid],item['archive_path'])
 for n in ('LICENSE','NOTICE.md'):z.write(public/n,n)
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None and all(not n.startswith('P02/') for n in z.namelist())
 for item in files.values():
  if item['distribution']=='included':assert hashlib.sha256(z.read(item['archive_path'])).hexdigest()==item['sha256']
report=dict(status='Passed',checks=checks,gui='Not Run',independent_human_review='Not Run',public_material_completion='partial: P02 separately acquired, redistribution permission unverified',package_path=str(package),package_sha256=sha(package),package_bytes=package.stat().st_size,included_files=sum(i['distribution']=='included' for i in files.values()),source_availability=availability)
write(E/'validation.json',report);write(E/'sha256.json',{p.relative_to(E).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='sha256.json'});print(json.dumps(report),flush=True)
