"""Derive owned tutorial data from completed Gaussian outputs; never run Gaussian."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_REL = 'validation/shared/data/public'
DATASET = 'gaussian-v1'
MANIFEST_REL = PUBLIC_REL + '/' + DATASET + '/tutorial-samples.json'
PACKAGE_REL = 'validation/agent/packages/qcblender-public-tutorial-samples-v3.zip'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                              default=lambda item:item.tolist()) + '\n', encoding='utf-8', newline='\n')


def public_text(text):
    """Remove machine execution details while retaining printed scientific records."""
    result = []
    for line in text.splitlines():
        if re.search(r'^\s*%(?:NProc\w*|Mem|RWF|OldChk|LindaWorkers)\s*=|'
                     r'Will use up to|Job cpu time:|Elapsed time:|File lengths \(MBytes\)|'
                     r'Keep R\d.*ints in memory|nthreads\s*=|Number of parallel threads|Total.*(?:wall|CPU).*time', line, re.I):
            continue
        if re.match(r'\s*Leave Link\s+\d+',line):
            line=line.split(' at ',1)[0]
        elif 'Entering Gaussian System, Link 0=' in line:
            line = ' Entering Gaussian System, Link 0=Gaussian'
        elif re.search(r'Entering Link 1\s*=', line):
            line = ' Entering Link 1 = Gaussian'
        elif re.search(r'^\s*\(Enter /|^\s*/(?:home|opt|usr)/|\-scrdir=', line):
            continue
        line = re.sub(r'GINC-[^\\\s]+', 'GINC-PUBLIC', line)
        # Gaussian archive header: host, task, method, basis, formula, account, date.
        line = re.sub(r'(GINC-PUBLIC\\[^\\]+\\[^\\]+\\[^\\]+\\[^\\]+\\)[^\\]+\\',
                      r'\1PUBLIC\\', line)
        line = re.sub(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\s"<>]+', '[local-file]', line)
        line = re.sub(r'/(?:home|opt|usr|tmp|mnt)/[^\s"<>]+', '[local-file]', line)
        result.append(line)
    return '\n'.join(result) + '\n'


def public_input(text):
    return '\n'.join(line for line in public_text(text).splitlines()
                     if not line.lstrip().lower().startswith(('%nproc', '%mem'))) + '\n'


def decode_output(raw):
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        # The existing Windows Multiwfn binary prints its banner in the active codepage.
        return raw.decode('gb18030')


def clean_science(value):
    """Remove source locations for before/after scientific equality checks."""
    if isinstance(value, dict):
        return {key: clean_science(item) for key, item in value.items()
                if 'line' not in key and key not in ('source', 'sources', 'filename', 'sha256')}
    if isinstance(value, list):
        return [clean_science(item) for item in value]
    return value


class Generator:
    def __init__(self, args):
        self.args = args
        self.base = ROOT / PUBLIC_REL / DATASET
        self.base.mkdir(parents=True, exist_ok=True)
        self.private = args.derived_root.resolve()
        self.private.mkdir(parents=True, exist_ok=True)
        path = ROOT / MANIFEST_REL
        self.manifest = json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(
            schema=1, dataset_id=DATASET, date='2026-10-24', attribution='QCBlender contributors',
            groups={}, files={}, cases={}, checks={},
            tolerances=dict(coordinates_angstrom=3e-6, scalar_energy_hartree=1e-8, cube_formula_abs=3e-6),
            scientific_scope=dict(geometry='Optimized Gaussian structures; frozen complex fragment geometries',
                                  grid_convergence='Not claimed',
                                  nocv_energy='Actual complex KS reconstruction; Multiwfn approximation, not F_TS'))
        self.manifest.setdefault('nodes', {
            f'N{number:02d}':dict(case=case,status='Not Run') for number,case in enumerate(
                ['C05','C05','C05','C01','C01','C04','C04','C04','C01','C01','C04','C02','C09','C07','C01','all','C04','all'],1)})

    def freeze(self):
        write_json(ROOT / MANIFEST_REL, self.manifest)

    def add(self, sid, source, relative, role, expected=None, calculation=None, quantity=None, unit=None,
            sanitize=False, producer=None, derivation=None):
        target = self.base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = Path(source).read_bytes()
        if sanitize:
            raw = public_text(decode_output(raw)).encode('utf-8')
        if target.exists() and target.read_bytes() != raw and not self.args.refresh_generated:
            raise FileExistsError('Refusing to replace a different public input: ' + str(target))
        target.write_bytes(raw)
        record = dict(id=sid, path=PUBLIC_REL + '/' + DATASET + '/' + relative,
                      archive_path=DATASET + '/' + relative, bytes=len(raw), sha256=sha(target),
                      distribution='included', license='CC-BY-4.0',
                      license_evidence='https://creativecommons.org/licenses/by/4.0/',
                      attribution='QCBlender contributors', source_url=None, local_key=None,
                      calculation_group=relative.split('/')[0], role=role,
                      producer=producer or 'Gaussian 16 C.01', expected=expected or {},
                      calculation=calculation or {}, quantity=quantity, unit=unit)
        if derivation:
            record['derivation'] = derivation
        self.manifest['files'][sid] = record
        return target

    def wave(self, group, name, folder, optimization=None):
        source = self.args.raw_root / folder / 'result.fchk'
        data = read_fchk(source)
        io = load_one(source)
        overlap = compute_overlap(io.obasis, io.atcoords)
        density = io.one_rdms['scf']
        nelectron = float(np.trace(density @ overlap))
        np.testing.assert_allclose(nelectron, data.metadata['electron_count'], atol=3e-6, rtol=0)
        mo_density = (io.mo.coeffs * io.mo.occs) @ io.mo.coeffs.T
        np.testing.assert_allclose(density, mo_density, atol=2e-7, rtol=2e-6)
        calc = dict(method=data.metadata['method'], basis=data.metadata['basis_name'],
                    charge=int(data.metadata['charge']), spin=int(data.metadata['spin_polarization']),
                    multiplicity=int(data.metadata['spin_polarization'])+1,
                    electron_count=int(data.metadata['electron_count']),
                    basis_functions=io.obasis.nbasis,
                    geometry='Optimized complex geometry' if optimization else 'Frozen complex fragment geometry',
                    angular_representation='Pure 5D/7F where present',
                    producer='Gaussian 16 C.01; native formchk FCHK')
        expected = dict(**calc, atomic_numbers=data.arrays['atomic_numbers'].tolist(),
                        coordinates_angstrom=data.arrays['positions'].tolist(),
                        energy_hartree=data.metadata['energies'][0]['value_hartree'],
                        orbitals=data.metadata['orbitals'], electron_trace=nelectron,
                        mulliken_charges=data.arrays['charge_mulliken'].tolist(),
                        dipole_e_bohr=data.arrays['dipole'].tolist())
        if optimization:
            original = self.args.raw_root / optimization / 'output.log'
            frequencies = [float(x) for line in original.read_text().splitlines() if 'Frequencies --' in line
                           for x in line.split('--', 1)[1].split()]
            if not frequencies or min(frequencies) <= 0:
                raise ValueError('Optimized static structure lacks all-positive frequencies: ' + group)
            expected['frequencies_cm_minus1'] = frequencies
            self.add(group+'-optimization-log', original, group+'/optimization.log',
                     'Optimization and frequency evidence', calculation=calc, sanitize=True)
        final = self.add(group+'-'+name, source, group+'/'+name+'.fchk', 'Native Gaussian wavefunction', expected, calc)
        self.add(group+'-'+name+'-singlepoint-log', self.args.raw_root/folder/'output.log', group+'/'+name+'.log',
                 'Canonical single point scientific output', calculation=calc, sanitize=True)
        text = public_input((self.args.raw_root/folder/'input.gjf').read_text())
        input_path = self.private / (group+'-'+name+'.gjf')
        input_path.write_text(text, encoding='ascii', newline='\n')
        self.add(group+'-'+name+'-input', input_path, group+'/'+name+'.gjf', 'Portable scientific input', calculation=calc)
        return final, data, calc

    def multiwfn(self, group, kind, source, commands, expected, settings=None, fragments=()):
        package = self.args.reference_root / 'submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64'
        exe = package / 'Multiwfn.exe'
        work = self.private / group / kind
        record_path = work / 'run.json'
        identity = dict(input_sha256=sha(source), commands=commands,
                        settings=dict(nthreads='4', isilent='1', **(settings or {})),
                        fragment_sha256={Path(path).name: sha(path) for path in fragments},
                        executable_sha256=sha(exe))
        if record_path.exists():
            old = json.loads(record_path.read_text())
            if any(old[key] != value for key, value in identity.items()) or old['returncode'] != 0:
                raise ValueError('Existing analysis differs from requested calculation: ' + str(work))
            for name in expected:
                if sha(work/name) != old['outputs'][name]:
                    raise ValueError('Existing analysis output identity differs: ' + str(work/name))
            return work
        if work.exists():
            raise FileExistsError('Unfinished analysis directory retained: ' + str(work))
        work.mkdir(parents=True)
        shutil.copyfile(source, work / source.name)
        for path in fragments:
            shutil.copyfile(path, work / Path(path).name)
        text = (package/'settings.ini').read_text(encoding='utf-8')
        for key, value in identity['settings'].items():
            text, count = re.subn(rf'(?m)^(\s*{key}\s*=\s*)\S+', lambda match: match[1]+value, text)
            if count != 1:
                raise ValueError('Unknown Multiwfn setting: ' + key)
        (work/'settings.ini').write_text(text, encoding='utf-8', newline='\n')
        (work/'stdin.txt').write_bytes(('\r\n'.join(commands)+'\r\n').encode('ascii'))
        started = time.monotonic()
        env = dict(os.environ, OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', Multiwfnpath=str(package),
                   TMP=str(work), TEMP=str(work), TMPDIR=str(work))
        with (work/'stdin.txt').open('rb') as inp, (work/'stdout.log').open('wb') as out, (work/'stderr.log').open('wb') as err:
            result = subprocess.run([str(exe), source.name], cwd=work, env=env,
                                    stdin=inp, stdout=out, stderr=err, timeout=1800,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
        report = dict(identity, returncode=result.returncode, seconds=time.monotonic()-started,
                      outputs={name: sha(work/name) for name in expected if (work/name).is_file()})
        write_json(record_path, report)
        result.check_returncode()
        if len(report['outputs']) != len(expected) or 'Error:' in (work/'stdout.log').read_text(errors='replace'):
            raise ValueError('Multiwfn analysis did not produce complete valid outputs: ' + str(work))
        print(json.dumps(dict(group=group, analysis=kind, status='Passed')), flush=True)
        return work

    def case(self, cid, group, ids, **gui):
        self.manifest['cases'][cid] = dict(group=group, files=ids, gui=gui,
            local_parse_status='Passed', gui_status='Not Run', public_material_status='included',
            display_defaults_status='proposed; actual Blender verification required',
            grid_defaults=dict(spacing_angstrom=.2, margin_angstrom=3, memory_mb=512))

    def static(self):
        p01, oxygen, calc1 = self.wave('P01', 'o2-uhf', 'P01-final', 'P01-opt-r1')
        self.add('P01-fch', p01, 'P01/o2-uhf.fch', 'Byte-identical FCH alias', {'same_as':'P01-o2-uhf'}, calc1)
        norba=int(oxygen.metadata['orbitals']['norba'])
        self.case('C01', 'P01', ['P01-o2-uhf','P01-fch'], alpha_mo=int(np.sum(oxygen.arrays['mo_occs'][:norba])),
                  beta_mo=int(np.sum(oxygen.arrays['mo_occs'][norba:])),
                  alpha_homo=orbital_selection(oxygen,'alpha','HOMO')['source_number'],
                  beta_homo=orbital_selection(oxygen,'beta','HOMO')['source_number'],
                  isovalue=.045, spin_isovalue=.002)
        p03, water, calc3 = self.wave('P03', 'water-dimer', 'P03-final', 'P03-opt')
        self.add('P03-fch', p03, 'P03/water-dimer.fch', 'Byte-identical FCH alias', {'same_as':'P03-water-dimer'}, calc3)
        for kind, commands, names in [
            ('igmh',['20','11','2','1-3','4-6','-10','1','2','3','0','0','q'],['dg_inter.cub','sl2r.cub']),
            ('iri',['20','4','-10','1','2','3','0','0','q'],['func2.cub','func1.cub']),
            ('esp',['12','0','1','2','9','all','-100,100','40','3','-1','-1','q'],['surfanalysis.pdb']),
            ('aim',['2','2','3','4','8','-4','6','0','-5','6','0','7','0','-10','q'],['CPs.pdb','paths.pdb','CPprop.txt'])]:
            work = self.multiwfn('P03',kind,p03,commands,names,
                                {'IGMvdwscl':'0','IRI_rhocut':'0','uservar':'0'} if kind in ('igmh','iri') else {})
            for name in names + (['stdout.log'] if kind=='esp' else []):
                quantity=unit=None; expected={}
                if name.endswith('.cub'):
                    cube=read_cube(work/name); field=cube.metadata['fields'][0]; values=cube.arrays[field['array']]
                    geometry=name in ('dg_inter.cub','func2.cub')
                    quantity=('delta_g_inter' if kind=='igmh' else 'iri_function') if geometry else 'sign_lambda2_rho'
                    unit=('electron/bohr^4' if kind=='igmh' else 'a.u. (electron^-0.1 bohr^-0.7)') if geometry else 'electron/bohr^3'
                    expected=dict(shape=field['shape'],origin=field['origin'],steps=field['steps'],
                                  minimum=float(values.min()),maximum=float(values.max()))
                self.add('P03-'+kind+'-'+name,work/name,'P03/'+kind+'/'+name,'External '+kind+' result',
                         expected,calc3,quantity,unit,sanitize=True,producer='Multiwfn 2026.9.20',
                         derivation=dict(reference='P03-water-dimer',commands=commands,
                                         fragments_1based=[[1,2,3],[4,5,6]] if kind=='igmh' else None))
        self.add('P03-cube', self.base/'P03/igmh/sl2r.cub', 'P03/color.cube', 'Byte-identical Cube alias',
                 {'same_as':'P03-igmh-sl2r.cub'},calc3,'sign_lambda2_rho','electron/bohr^3')
        esp=import_esp(water,self.base/'P03/esp/surfanalysis.pdb',self.base/'P03/esp/stdout.log',
                       'rho=0.001 electron/bohr^3','kcal/mol','kcal/mol','angstrom^2').metadata['analysis']
        aim=import_aim(water,self.base/'P03/aim/CPs.pdb',self.base/'P03/aim/paths.pdb',self.base/'P03/aim/CPprop.txt').metadata['analysis']
        self.manifest['files']['P03-esp-surfanalysis.pdb']['expected']=dict(extrema=esp['extrema'],area_sum_angstrom2=esp['area_sum'])
        self.manifest['files']['P03-esp-stdout.log']['expected']=dict(area_bins=esp['area_bins'],area_sum_angstrom2=esp['area_sum'])
        for name,key in [('CPs.pdb','critical_points'),('paths.pdb','paths'),('CPprop.txt','properties')]:
            self.manifest['files']['P03-aim-'+name]['expected']=dict(count=len(aim[key]),records=aim[key])
        complex_file, complex_data, calc5=self.wave('P05','complex','P05-final','P05-opt')
        co, co_data, _=self.wave('P05','co','P05-co')
        bh3, bh3_data, _=self.wave('P05','bh3','P05-bh3')
        assert co_data.metadata['electron_count']==14 and bh3_data.metadata['electron_count']==8
        np.testing.assert_allclose(complex_data.arrays['positions'][:2],co_data.arrays['positions'],atol=2e-7,rtol=0)
        np.testing.assert_allclose(complex_data.arrays['positions'][2:],bh3_data.arrays['positions'],atol=2e-7,rtol=0)
        commands=['23','2','co.fchk','bh3.fchk','-2','-4','ets-nocv.txt','-5','1','7','1','nocv-pair1.cub','q',
                  '6','1','nocv-orb1.cub','6',str(complex_data.metadata['orbitals']['norba']),'nocv-orb-negative.cub','-10','q']
        work=self.multiwfn('P05','nocv',complex_file,commands,
                           ['ets-nocv.txt','nocv-pair1.cub','nocv-orb1.cub','nocv-orb-negative.cub'],fragments=(co,bh3))
        for name in ('ets-nocv.txt','nocv-pair1.cub'):
            self.add('P05-'+name,work/name,'P05/nocv/'+name,'External ETS-NOCV result',calculation=calc5,
                     unit='kcal/mol' if name.endswith('.txt') else 'electron/bohr^3',sanitize=True,
                     producer='Multiwfn 2026.9.20',derivation=dict(reference='P05-complex',fragments=['P05-co','P05-bh3'],
                     energy_method='Actual complex KS reconstruction; not F_TS'))
        ets=import_ets(complex_data,self.base/'P05/nocv/ets-nocv.txt','kcal/mol')
        nocv=import_nocv(self.base/'P05/nocv/nocv-pair1.cub',ets,1,'Total','electron/bohr^3')
        get=lambda data:data.arrays[data.metadata['fields'][0]['array']]
        pair=ets.metadata['analysis']['pairs'][0]
        err=float(np.max(np.abs(pair['positive_eigenvalue']*get(read_cube(work/'nocv-orb1.cub'))**2+
                    pair['negative_eigenvalue']*get(read_cube(work/'nocv-orb-negative.cub'))**2-get(nocv))))
        assert err<3e-6,err
        self.manifest['files']['P05-ets-nocv.txt']['expected']=dict(pairs=ets.metadata['analysis']['pairs'],
                      energy_unit='kcal/mol',energy_method='Actual complex KS reconstruction; not F_TS',pair_density_formula_max_abs_error=err)
        field=nocv.metadata['fields'][0]; values=get(nocv)
        self.manifest['files']['P05-nocv-pair1.cub']['expected']=dict(shape=field['shape'],
            minimum=float(values.min()),maximum=float(values.max()),
            net_integral_electron=float(values.sum()*abs(np.linalg.det(field['steps']))/BOHR_ANGSTROM**3))
        self.case('C03','P03',['P03-igmh-sl2r.cub','P03-cube'],quantity='sign_lambda2_rho',unit='electron/bohr^3',scale_factor=1,isovalue=.02)
        self.case('C04','P03',['P03-water-dimer'],density_isovalue=.004,color_minimum=-.05,color_center=0,color_maximum=.05,color_unit='hartree/e',charge_method='mulliken',dipole_scale_angstrom_per_debye=1.5)
        self.case('C05','P03',['P03-water-dimer','P03-fch'],keep_h_atom_number=2,oxygen_atom_numbers=[1,4])
        self.case('C07','P03',['P03-water-dimer','P03-igmh-dg_inter.cub','P03-igmh-sl2r.cub','P03-iri-func2.cub','P03-iri-func1.cub'],fragments_1based=[[1,2,3],[4,5,6]],igmh_isovalue=.005,iri_isovalue=1,iri_exponent=1.1,color_minimum=-.04,color_center=0,color_maximum=.04,color_unit='electron/bohr^3')
        self.case('C08','P03',['P03-water-dimer','P03-esp-surfanalysis.pdb','P03-esp-stdout.log'],surface_definition='rho=0.001 electron/bohr^3',extrema_unit='kcal/mol',center_unit='kcal/mol',area_unit='angstrom^2')
        self.case('C09','P03',['P03-water-dimer','P03-aim-CPs.pdb','P03-aim-paths.pdb','P03-aim-CPprop.txt'],coordinate_unit='angstrom',point_number=aim['critical_points'][0]['serial'])
        self.case('C12','P05',['P05-complex','P05-ets-nocv.txt'],energy_unit='kcal/mol',pair_number=1,spin='Total')
        self.case('C13','P05',['P05-complex','P05-ets-nocv.txt','P05-nocv-pair1.cub'],pair_number=1,spin='Total',unit='electron/bohr^3',isovalue=.003)
        for group in ('P01','P03','P05'):
            self.manifest['groups'][group]=dict(local_parse_status='Passed',public_material_status='included')
        self.manifest['regression']=dict(log_job_number=2,next_fchk='P03-water-dimer',
            expected_fchk_job_number=1,expected_fchk_atomic_numbers=water.arrays['atomic_numbers'].tolist(),gui_status='Not Run')
        self.manifest['interaction_examples']=dict(atom_number_base=1,measurement_distance_atoms=[1,4],
            expected_distance_angstrom=float(np.linalg.norm(water.arrays['positions'][0]-water.arrays['positions'][3])),
            measurement_angle_atoms=[2,1,3],label_atom_number=1,
            profile_start_angstrom=[0,-2,1.45],profile_end_angstrom=[0,2,1.45],profile_case='C04',
            slice_center_angstrom=[0,0,1.45],read_cursor_inside_angstrom=[0,0,1.45],
            read_cursor_invalid_angstrom=[0,0,0],read_cursor_outside_angstrom=[20,20,20])
        self.freeze()
        print('STATIC_DERIVATION_PASSED',flush=True)

    def p02(self):
        raw=self.args.raw_root/'P02-opt/output.log'
        target=self.add('P02-water_neutral_nbo_opt_freq.out',raw,'P02/water_neutral_nbo_opt_freq.out',
                        'Owned Gaussian multijob optimization/frequency/NBO',sanitize=True)
        signatures=[]
        for path in (raw,target):
            jobs=[read_source(path,index) for index in range(2)]
            nbo=parse_nbo(path,1,0)
            signatures.append(dict(jobs=[dict(arrays={k:v.tolist() for k,v in data.arrays.items()},
                          energies=clean_science(data.metadata['energies']),
                          optimization=clean_science(data.metadata.get('optimization')))
                          for data in jobs],nbo=clean_science(nbo)))
        if signatures[0]!=signatures[1]:
            raise AssertionError('Public Gaussian log changed scientific values')
        opt,freq=[read_source(target,index) for index in range(2)];nbo=parse_nbo(target,1,0)
        assert np.all(freq.arrays['mode_frequencies']>0)
        expected=dict(job_number=2,job_index=1,block_number=1,block_index=0,
            atomic_numbers=freq.arrays['atomic_numbers'].tolist(),positions_angstrom=freq.arrays['positions'].tolist(),
            frequencies_cm_minus1=freq.arrays['mode_frequencies'].tolist(),
            ir_intensities_km_mol=freq.arrays['mode_ir_intensities'].tolist(),
            nbo_count=len(nbo['orbitals']),e2_count=len(nbo['interactions']),nbo=nbo,
            optimization_job_number=1,optimization_step_count=len(opt.metadata['optimization']['steps']),
            optimization_energies_hartree=[step['energy']['value_hartree'] for step in opt.metadata['optimization']['steps']],
            scientific_sanitization_equality='Passed')
        record=self.manifest['files']['P02-water_neutral_nbo_opt_freq.out'];record['expected']=expected
        record['calculation']=dict(method='RHF',basis='STO-3G',charge=0,multiplicity=1,electron_count=10)
        self.add('P02-log-alias',target,'P02/water_neutral_nbo_opt_freq.log','Byte-identical log alias',
                 {'same_as':'P02-water_neutral_nbo_opt_freq.out'},record['calculation'])
        input_path=self.private/'P02-input.gjf'
        input_path.write_text(public_input((self.args.raw_root/'P02-opt/input.gjf').read_text()),encoding='ascii',newline='\n')
        self.add('P02-input',input_path,'P02/water.gjf','Owned Gaussian scientific input',calculation=record['calculation'])
        self.case('C02','P02',['P02-water_neutral_nbo_opt_freq.out'],job_number=2,mode_number=3,amplitude_angstrom=.35,cycles_per_second=1)
        self.case('C06','P02',['P02-water_neutral_nbo_opt_freq.out'],job_number=2,block_number=1,nbo_number=nbo['orbitals'][0]['number'],e2_record_number=1)
        self.manifest['groups']['P02']=dict(local_parse_status='Passed',public_material_status='included')
        self.freeze();print('P02_SANITIZED_SCIENCE_PASSED',flush=True)

    def xyz(self):
        symbols={1:'H',5:'B',6:'C',7:'N',8:'O'}
        sets=[('water-dimer.xyz',['P03-water-dimer'])]
        if 'P04-steps.csv' in self.manifest['files']:
            ts=self.manifest['files']['P04-steps.csv']['expected']['irc_report']['ts_step']
            count=self.manifest['files']['P04-steps.csv']['expected']['steps']
            sets.append(('p04-three-frames.xyz',[f'P04-step-{number:03d}.fchk' for number in (1,ts,count)]))
        samples=[]
        for name,ids in sets:
            lines=[];sources=[]
            for sid in ids:
                record=self.manifest['files'][sid];source=ROOT/record['path'];data=read_fchk(source)
                lines.extend([str(len(data.arrays['atomic_numbers'])),f'QCBlender {sid}; coordinates angstrom'])
                lines.extend(symbols[int(z)]+' '+' '.join(f'{v:.17g}' for v in point)
                             for z,point in zip(data.arrays['atomic_numbers'],data.arrays['positions']))
                sources.append(dict(id=sid,path='../'+record['archive_path'].split('/',1)[1],sha256=record['sha256']))
            target=self.private/name;target.write_text('\n'.join(lines)+'\n',encoding='ascii',newline='\n')
            self.add('P06-'+name,target,'P06/'+name,'Coordinate-only XYZ derived from native Gaussian FCHK',
                     dict(frames=len(ids),source_ids=ids),producer='QCBlender read_fchk; 17 significant digits',
                     unit='angstrom',derivation=dict(source_ids=ids))
            samples.append(dict(file=name,sha256=sha(target),frames=len(ids),sources=sources))
        source=self.private/'P06-source.json'
        write_json(source,dict(license='CC-BY-4.0',attribution='QCBlender contributors',
                   source_manifest='../tutorial-samples.json',coordinate_unit='angstrom',
                   derivation='Coordinates read from native Gaussian FCHK; no energy or wavefunction in XYZ',samples=samples))
        self.add('P06-source.json',source,'P06/source.json','XYZ derivation and exact source identities',
                 producer='QCBlender native Gaussian FCHK coordinate extraction')
        self.manifest['groups']['P06']=dict(local_parse_status='Passed',public_material_status='included')
        self.freeze();print('XYZ_DERIVATION_PASSED',flush=True)

    def irc(self):
        if self.args.irc_map is None:
            raise ValueError('--irc-map is required for the completed Gaussian IRC')
        mapping=json.loads(self.args.irc_map.read_text(encoding='utf-8'))
        if mapping['irc_status']!='converged both directions':
            raise ValueError('A complete converged bidirectional IRC is required')
        frequencies=mapping['ts_frequencies_cm_minus1']
        assert sum(value<0 for value in frequencies)==1
        selected=mapping['steps'];count=len(selected);ts=int(mapping['ts_step'])
        assert count>3 and 1<ts<count
        energies=np.asarray([item['energy_hartree'] for item in selected])
        tolerance=5e-9
        assert np.max(energies)<=energies[ts-1]+tolerance
        assert np.all(np.diff(energies[:ts])>=-tolerance)
        assert np.all(np.diff(energies[ts-1:])<=tolerance)
        assert max(energies[0],energies[-1])<energies[ts-1]-tolerance
        endpoint_checks={}
        for direction,index in [('reverse',0),('forward',count-1)]:
            log=Path(mapping['endpoint_logs'][direction])
            text=log.read_text()
            values=[float(value) for line in text.splitlines() if 'Frequencies --' in line
                    for value in line.split('--',1)[1].split()]
            assert values and min(values)>0,(direction,values)
            assert 'Normal termination of Gaussian' in text
            endpoint=read_source(log)
            data=read_fchk(Path(selected[index]['fchk']))
            np.testing.assert_allclose(endpoint.arrays['positions'],data.arrays['positions'],atol=3e-6,rtol=0)
            energy=float(re.findall(r'SCF Done:\s+E\([^)]+\)\s*=\s*([-\d.Ee+]+)',text)[-1])
            np.testing.assert_allclose(energy,energies[index],atol=5e-8,rtol=0)
            endpoint_checks[direction]=dict(step=index+1,frequencies_cm_minus1=values,
                                            energy_hartree=energy,status='Passed')
        calc=dict(method='RHF',basis='STO-3G',charge=0,spin=0,multiplicity=1,electron_count=18,
                  geometry='Accepted bidirectional IRC point; native Gaussian canonical single-point FCHK',
                  path_integrator=mapping['path_integrator'],
                  producer='Gaussian 16 C.01')
        steps=[];mayer=[];all_orders=[];source_records=[]
        for number,item in enumerate(selected,1):
            assert item['step']==number
            source=Path(item['fchk']);data=read_fchk(source);io=load_one(source)
            energy=data.metadata['energies'][0]['value_hartree']
            np.testing.assert_allclose(energy,item['energy_hartree'],atol=5e-8,rtol=0)
            if 'coordinates_angstrom' in item:
                np.testing.assert_allclose(data.arrays['positions'],item['coordinates_angstrom'],atol=3e-7,rtol=0)
            assert data.arrays['atomic_numbers'].tolist()==[8,8,1,1]
            name=f'step-{number:03d}';sid='P04-'+name+'.fchk'
            expected=dict(atomic_numbers=data.arrays['atomic_numbers'].tolist(),
                          positions_angstrom=data.arrays['positions'].tolist(),energy_hartree=energy,
                          source_irc_energy_hartree=item['energy_hartree'],
                          direction=item.get('direction'),irc_point=item.get('irc_point'),
                          path_stage=item.get('path_stage','irc'))
            target=self.add(sid,source,'P04/'+name+'.fchk','Native Gaussian wavefunction at accepted IRC point',expected,calc)
            overlap=compute_overlap(io.obasis,io.atcoords);ps=io.one_rdms['scf']@overlap
            centers=[]
            for shell in io.obasis.shells:
                centers.extend([int(shell.icenter)]*int(shell.nbasis))
            centers=np.asarray(centers);orders=[];symbols=['O','O','H','H']
            lines=['Producer: Gaussian native FCHK total SCF density and IOData overlap',
                   'Method: Mayer; sum((P S)_AB * (P S)_BA); unit dimensionless',
                   'Bond orders with absolute value >= 0.000000']
            for aa in range(4):
                for bb in range(aa+1,4):
                    a=np.flatnonzero(centers==aa);b=np.flatnonzero(centers==bb)
                    order=float(np.sum(ps[np.ix_(a,b)]*ps[np.ix_(b,a)].T))
                    orders.append([aa+1,bb+1,order])
                    lines.append(f'# {len(orders)}: {aa+1}({symbols[aa]}) {bb+1}({symbols[bb]}) {order:.12f}')
            text=self.private/(name+'-mayer.txt');text.write_text('\n'.join(lines)+'\n',encoding='ascii',newline='\n')
            self.add('P04-'+name+'-mayer.txt',text,'P04/'+name+'-mayer.txt','All six Mayer atom pairs from native Gaussian density',
                     dict(orders=orders),calc,unit='dimensionless',producer='Gaussian FCHK / IOData overlap / explicit Mayer contraction',
                     derivation=dict(reference=sid,formula='sum((P S)_AB * (P S)_BA)'))
            steps.append((number,name+'.fchk'));mayer.append((number,name+'-mayer.txt'));all_orders.append([value[2] for value in orders])
            source_records.append(dict(step=number,direction=item.get('direction'),irc_point=item.get('irc_point'),
                                       path_stage=item.get('path_stage','irc'),energy_hartree=energy,fchk_sha256=sha(target)))
        for name,column,rows in [('steps.csv','fchk',steps),('mayer.csv','mayer_output',mayer)]:
            path=self.private/name
            with path.open('w',encoding='utf-8',newline='') as stream:
                writer=csv.writer(stream);writer.writerow(['step',column]);writer.writerows(rows)
            self.add('P04-'+name,path,'P04/'+name,'Complete Gaussian IRC step association',calculation=calc)
        report=dict(method='RHF',basis='STO-3G',charge=0,spin=0,multiplicity=1,
                    ts_step=ts,ts_frequencies_cm_minus1=frequencies,imaginary_mode_count=1,
                    irc_direction='both',irc_status=mapping['irc_status'],path_integrator=mapping['path_integrator'],accepted_frame_count=count,
                    selected_steps=source_records,endpoint_checks=endpoint_checks,
                    monotonic_energy_tolerance_hartree=tolerance)
        self.manifest['files']['P04-steps.csv']['expected']=dict(steps=count,energies_hartree=[item['energy_hartree'] for item in source_records],irc_report=report)
        self.manifest['files']['P04-mayer.csv']['expected']=dict(pairs=[[a,b] for a in range(1,5) for b in range(a+1,5)],
                                                               orders=all_orders,unit='dimensionless')
        reference=self.base/f'P04/step-{ts:03d}.fchk'
        work=self.multiwfn('P04','mayer-reference',reference,['9','1','n','0','q'],['stdout.log'],{'bndordthres':'0'})
        actual=mayer_orders(work/'stdout.log',4)
        errors=[abs(row['order']-all_orders[ts-1][index]) for index,row in enumerate(actual)]
        assert len(actual)==6 and max(errors)<2e-7,errors
        report['mayer_multiwfn_reference']=dict(step=ts,pairs=actual,max_abs_error=max(errors),status='Passed')
        self.add('P04-mayer-reference.log',work/'stdout.log','P04/mayer-reference.log',
                 'Independent Multiwfn Mayer comparison at the transition state',calculation=calc,
                 sanitize=True,producer='Multiwfn 2026.9.20')
        for label,filename in mapping.get('source_logs',{}).items():
            if label=='ts':
                continue
            self.add('P04-'+label+'-log',Path(filename),'P04/'+label+'.log','IRC integrator and Gaussian convergence evidence',
                     calculation=calc,sanitize=True,producer=mapping.get('source_log_producers',{}).get(label,'Gaussian 16 C.01'))
        ts_log=Path(mapping['ts_log'])
        actual_frequencies=[float(value) for line in ts_log.read_text().splitlines() if 'Frequencies --' in line
                            for value in line.split('--',1)[1].split()]
        np.testing.assert_allclose(actual_frequencies,frequencies,atol=1e-8,rtol=0)
        from qcblender.gaussian_log import inspect_log
        ts_data=read_source(ts_log,len(inspect_log(ts_log)['jobs'])-1)
        mode=ts_data.arrays['mode_displacements'][int(np.argmin(ts_data.arrays['mode_frequencies']))]
        positions=ts_data.arrays['positions'];axis=positions[1]-positions[0]
        normal=np.cross(axis,positions[2]-positions[0]);normal/=np.linalg.norm(normal)
        out_of_plane=float(np.sum((mode@normal)**2)/np.sum(mode**2))
        assert out_of_plane>.99,out_of_plane
        report['ts_mode_assignment']=dict(mode='O-O torsion',out_of_plane_displacement_fraction=out_of_plane,
                                           evidence='Unique imaginary Gaussian printed normal mode; planar H-O-O-H')
        self.add('P04-ts-log',ts_log,'P04/ts.log','First-order saddle optimization and frequency evidence',
                 calculation=calc,sanitize=True)
        for direction,check in endpoint_checks.items():
            self.add('P04-'+direction+'-endpoint-log',Path(mapping['endpoint_logs'][direction]),
                     'P04/'+direction+'-endpoint.log','Same-coordinate IRC endpoint frequency evidence',
                     expected=check,calculation=dict(calc,geometry='Frequency at the accepted IRC endpoint'),sanitize=True)
        self.case('C10','P04',['P04-steps.csv']+[f'P04-step-{i:03d}.fchk' for i in range(1,count+1)],step_numbers=list(range(1,count+1)),ts_step=ts)
        self.case('C11','P04',['P04-mayer.csv']+[f'P04-step-{i:03d}-mayer.txt' for i in range(1,count+1)],atom_pair_1based=[1,2],unit='dimensionless')
        self.manifest['groups']['P04']=dict(local_parse_status='Passed',public_material_status='included')
        self.freeze();print('IRC_MAYER_DERIVATION_PASSED',flush=True)

    def package(self):
        from tools.verify_gaussian_tutorial import verify
        verify_args=argparse.Namespace(manifest=ROOT/MANIFEST_REL,raw_root=self.args.raw_root,
            derived_root=self.private,package=None,require_complete=True,
            private_identifiers=self.args.private_identifiers)
        report=verify(verify_args)
        notice=('# Public tutorial samples\n\n'
            'Current dataset: Gaussian-v1. Owned calculation data: CC BY 4.0; attribution QCBlender contributors. '
            'P01/P03/P05 are optimized structures at the original methods/bases; P02 is an owned two-job water '
            'optimization/frequency/NBO output. P04 contains a first-order saddle and a complete bidirectional '
            'geomeTRIC 1.1.1 IRC driven by real Gaussian energies and gradients, with Gaussian endpoint '
            'frequency checks; Gaussian built-in IRC attempts were not accepted as complete. '
            'P05 fragments retain their geometries in the optimized complex. P06 contains '
            'coordinate-only XYZ derivatives. Native FCHK files are produced by Gaussian formchk.\n\n'
            'Gaussian 16 Revision C.01 is the wavefunction producer. Multiwfn 2026.9.20 produces IGMH/IRI, '
            'ESP/AIM and NOCV analyses. Cite Tian Lu, Feiwu Chen, J. Comput. Chem. 33, 580 (2012), '
            'DOI:10.1002/jcc.22885; Tian Lu, J. Chem. Phys. 161, 082503 (2024), DOI:10.1063/5.0216272.\n\n'
            'IRC integration and endpoint relaxation use geomeTRIC 1.1.1; cite L.-P. Wang and C. Song, '
            'J. Chem. Phys. 144, 214108 (2016), DOI:10.1063/1.4952956.\n\n'
            'NOCV energies use the actual complex KS reconstruction and retain the Multiwfn approximation; '
            'they are not evaluated using F_TS. No basis-set or scientific grid-convergence claim is made. '
            'QCBlender display grids default to 0.2 angstrom; externally generated analysis grids are recorded '
            'separately in the current manifest. Original program outputs retain their scientific values; '
            'public copies omit machine execution details.\n\n'
            'Legacy-v2 inputs and their frozen manifest remain historical data. Their previous scientific and '
            'GUI evidence does not qualify this dataset. The old restricted P02 input is not included.\n')
        (ROOT/PUBLIC_REL/'NOTICE.md').write_text(notice,encoding='utf-8',newline='\n')
        readme=('# 公开案例输入\n\n'
            '当前教程使用 `gaussian-v1/` 中的 Gaussian 自有计算数据；各组文件及相对引用应一起保留。\n\n'
            '| 案例 | 当前输入路径 | 用途 |\n| --- | --- | --- |\n'
            '| P01 | [gaussian-v1/P01/o2-uhf.fchk](gaussian-v1/P01/o2-uhf.fchk) | 优化氧分子的轨道和自旋密度 |\n'
            '| P02 | [gaussian-v1/P02/water_neutral_nbo_opt_freq.out](gaussian-v1/P02/water_neutral_nbo_opt_freq.out) | 自有水分子的优化、频率、NBO |\n'
            '| P03 | [gaussian-v1/P03/water-dimer.fchk](gaussian-v1/P03/water-dimer.fchk) | 优化水二聚体及 IGMH/IRI、ESP、AIM 外部结果 |\n'
            '| P04 | [gaussian-v1/P04/steps.csv](gaussian-v1/P04/steps.csv)、[gaussian-v1/P04/mayer.csv](gaussian-v1/P04/mayer.csv) | 完整双向 IRC 和逐点 Mayer 键级 |\n'
            '| P05 | [gaussian-v1/P05/complex.fchk](gaussian-v1/P05/complex.fchk) | 优化 CO–BH3 及冻结片段 NOCV 分析 |\n'
            '| P06 | [gaussian-v1/P06/source.json](gaussian-v1/P06/source.json) | 新 P03 单帧、新 P04 首/TS/末三帧 XYZ |\n\n'
            '所有当前样本的身份、实际数值和计算条件见 [当前清单](gaussian-v1/tutorial-samples.json)。'
            '数据按 [LICENSE](LICENSE) 使用 CC BY 4.0，署名 QCBlender contributors。'
            '科学适用范围、软件引用及 NOCV 能量近似见 [NOTICE.md](NOTICE.md)。\n\n'
            '根目录旧 P01–P06 及根 `tutorial-samples.json` 保留为 legacy-v2 历史输入；'
            '旧验证结论不代表当前 Gaussian 数据已通过界面或独立科研验收。\n')
        (ROOT/PUBLIC_REL/'README.md').write_text(readme,encoding='utf-8',newline='\n')
        package=ROOT/PACKAGE_REL
        if package.exists():
            raise FileExistsError('An existing candidate package is retained: '+str(package))
        with zipfile.ZipFile(package,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            archive.write(ROOT/MANIFEST_REL,'tutorial-samples.json')
            for record in self.manifest['files'].values():
                archive.write(ROOT/record['path'],record['archive_path'])
            for name in ('LICENSE','NOTICE.md'):
                archive.write(ROOT/PUBLIC_REL/name,name)
        verify_args.package=package;report=verify(verify_args)
        report['package']=dict(path=PACKAGE_REL,bytes=package.stat().st_size,sha256=sha(package))
        write_json(self.private/'validation.json',report)
        delivery_path=ROOT/'validation/agent/acceptance/tutorial-sample-delivery.json'
        old=json.loads(delivery_path.read_text(encoding='utf-8'))
        if old['schema']==1:
            legacy=dict(dataset_id='legacy-v2',manifest=dict(old['manifest'],path='validation/agent/v1-acceptance/tutorial-samples.json'),
                        package=dict(old['package'],path='validation/agent/packages/qcblender-public-tutorial-samples-v2.zip'))
        else:
            legacy=old['legacy_dataset']
        for key in ('manifest','package'):
            path=ROOT/legacy[key]['path']
            assert path.stat().st_size==legacy[key]['bytes'] and sha(path)==legacy[key]['sha256']
        current=dict(schema=2,date='2026-10-24',status='Passed',dataset_id=DATASET,
                     scope='Current owned Gaussian scientific data; GUI and independent scientific acceptance remain separate',
                     manifest=dict(path=MANIFEST_REL,bytes=(ROOT/MANIFEST_REL).stat().st_size,sha256=sha(ROOT/MANIFEST_REL)),
                     package=report['package'],legacy_dataset=legacy,
                     checks=dict(scientific_data='Passed',sample_package='Passed',gui='Not Run',independent_human_review='Not Run'))
        write_json(delivery_path,current)
        from tools.candidate_artifacts import verify_samples
        verify_samples(root=ROOT)
        print(json.dumps(dict(status='Passed',package=report['package'],files=report['file_count'])),flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--reference-root',type=Path,required=True,help='Existing science package directory')
    parser.add_argument('--raw-root',type=Path,required=True)
    parser.add_argument('--derived-root',type=Path,required=True)
    parser.add_argument('--stage',choices=('static','p02','xyz','irc','package'),required=True)
    parser.add_argument('--irc-map',type=Path)
    parser.add_argument('--private-identifiers',type=Path,help='Private identifier list for final public-content validation')
    parser.add_argument('--refresh-generated',action='store_true',help='Replace only this unfinished dataset derived output')
    args=parser.parse_args()
    # reference-root points to modules/science; binaries live at its checkout root.
    science=args.reference_root.resolve();args.reference_root=science.parents[1]
    sys.path[:0]=[str(science),str(ROOT)]
    global np,read_fchk,read_source,load_one,compute_overlap,read_cube,import_esp,import_aim,import_ets,import_nocv,parse_nbo,BOHR_ANGSTROM,orbital_selection,mayer_orders
    import numpy as np
    from qcblender.readers import read_fchk,read_source
    from iodata import load_one
    from iodata.overlap import compute_overlap
    from qcblender.cube import read_cube
    from qcblender.analysis_data import import_esp,import_aim,import_ets
    from qcblender.nocv import import_nocv
    from qcblender.nbo import parse_nbo
    from qcblender.data import BOHR_ANGSTROM,orbital_selection
    from qcblender.external_results import mayer_orders
    generator=Generator(args)
    getattr(generator,args.stage)()


if __name__=='__main__':
    main()
