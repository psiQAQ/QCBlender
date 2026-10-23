"""Verify the Gaussian tutorial dataset independently of the active delivery pointer."""
import argparse
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def verify(args):
    import numpy as np
    from iodata import load_one
    from iodata.overlap import compute_overlap
    from qcblender.readers import read_fchk,read_source
    from qcblender.evaluate import evaluate_points
    from qcblender.data import orbital_selection,BOHR_ANGSTROM
    from qcblender.external_fields import pair_cubes
    from qcblender.analysis_data import import_esp,import_aim,import_ets
    from qcblender.nocv import import_nocv
    from qcblender.nbo import parse_nbo
    from qcblender.irc import import_irc,import_irc_mayer
    from qcblender.cube import read_cube
    from tools.local_inputs import checked_path,verify_file
    from tools.generate_gaussian_tutorial import clean_science,sha
    manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    public=ROOT/'validation/shared/data/public'
    paths={}
    prohibited=re.compile(r'(?i)/home/|/opt/|GINC-(?!PUBLIC)[^\\\s]+|'
                          r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]|%NProc\w*\s*=|%Mem\s*=|MaxMem=|'
                          r'Number of parallel threads|processors via shared memory|\bssh\s+')
    identity_file=getattr(args,'private_identifiers',None)
    private_identifiers=[] if identity_file is None else json.loads(Path(identity_file).read_text(encoding='utf-8'))
    if not isinstance(private_identifiers,list) or any(not isinstance(value,str) or not value for value in private_identifiers):
        raise ValueError('Private identifier file must contain a nonempty-string list')
    waves={}
    source_folders={'P01-o2-uhf':'P01-final','P03-water-dimer':'P03-final',
                    'P05-complex':'P05-final','P05-co':'P05-co','P05-bh3':'P05-bh3'}
    for sid,record in manifest['files'].items():
        if record['distribution']!='included' or record['license']!='CC-BY-4.0':
            raise ValueError('Non-public input in Gaussian dataset: '+sid)
        if not record['archive_path'].startswith('gaussian-v1/'):
            raise ValueError('Input is outside Gaussian dataset: '+sid)
        path=checked_path(public,record['archive_path']);verify_file(path,record);paths[sid]=path
        text=path.read_text(encoding='utf-8')
        if prohibited.search(text) or any(value.casefold() in text.casefold() for value in private_identifiers):
            raise ValueError('Machine execution information remains in public input: '+sid)
        if path.suffix=='.fchk':
            if args.raw_root and sid in source_folders:
                assert path.read_bytes()==(args.raw_root/source_folders[sid]/'result.fchk').read_bytes()
            data=read_fchk(path);io=load_one(path);overlap=compute_overlap(io.obasis,io.atcoords)
            expected=record['expected'];waves[sid]=data
            np.testing.assert_array_equal(data.arrays['atomic_numbers'],expected['atomic_numbers'])
            np.testing.assert_allclose(data.arrays['positions'],expected.get('coordinates_angstrom',expected.get('positions_angstrom')),atol=1e-8,rtol=0)
            np.testing.assert_allclose(data.metadata['energies'][0]['value_hartree'],expected['energy_hartree'],atol=1e-10,rtol=0)
            density=io.one_rdms['scf'];nelectron=int(data.metadata['electron_count'])
            np.testing.assert_allclose(np.trace(density@overlap),nelectron,atol=3e-6,rtol=0)
            np.testing.assert_allclose(density,(io.mo.coeffs*io.mo.occs)@io.mo.coeffs.T,atol=2e-7,rtol=2e-6)
            assert record['calculation']['electron_count']==nelectron
        if 'same_as' in record['expected']:
            other=manifest['files'][record['expected']['same_as']]
            assert record['sha256']==other['sha256'] and record['bytes']==other['bytes']
    checks=['All file sizes/SHA-256/licenses','Public machine-detail scan','Native FCHK electron traces and MO density matrices']
    if 'P01-o2-uhf' in waves:
        oxygen=waves['P01-o2-uhf'];points=np.array([[.2,.3,.4],[1.,-.7,.6],[-2.,.8,-.3]])
        fields={kind:evaluate_points(oxygen,points,kind)[0] for kind in
                ('electron_number_density','alpha_density','beta_density','spin_density')}
        np.testing.assert_allclose(fields['electron_number_density'],fields['alpha_density']+fields['beta_density'],atol=1e-12)
        np.testing.assert_allclose(fields['spin_density'],fields['alpha_density']-fields['beta_density'],atol=1e-12)
        for spin in ('alpha','beta'):
            gui=manifest['cases']['C01']['gui']
            assert orbital_selection(oxygen,spin,'HOMO')['source_number']==gui[spin+'_homo']
            assert orbital_selection(oxygen,spin,'EXPLICIT',gui[spin+'_mo'])['source_number']==gui[spin+'_mo']
        assert oxygen.metadata['electron_count']==16 and oxygen.metadata['spin_polarization']==2
        checks.append('O2 spin identities and actual HOMO/MO source numbers')
    if 'P03-water-dimer' in waves:
        water=waves['P03-water-dimer']
        for kind,geometry,color,unit in [('IGMH','igmh-dg_inter.cub','igmh-sl2r.cub','electron/bohr^4'),
                                       ('IRI','iri-func2.cub','iri-func1.cub','a.u. (electron^-0.1 bohr^-0.7)')]:
            pair=pair_cubes(paths['P03-'+geometry],paths['P03-'+color],kind,unit,'electron/bohr^3',1.1 if kind=='IRI' else None)
            np.testing.assert_allclose(pair.arrays['positions'],water.arrays['positions'],atol=3e-6,rtol=0)
        esp=import_esp(water,paths['P03-esp-surfanalysis.pdb'],paths['P03-esp-stdout.log'],
                       'rho=0.001 electron/bohr^3','kcal/mol','kcal/mol','angstrom^2').metadata['analysis']
        aim=import_aim(water,paths['P03-aim-CPs.pdb'],paths['P03-aim-paths.pdb'],paths['P03-aim-CPprop.txt']).metadata['analysis']
        assert esp['extrema']==manifest['files']['P03-esp-surfanalysis.pdb']['expected']['extrema']
        assert esp['area_bins']==manifest['files']['P03-esp-stdout.log']['expected']['area_bins']
        for name,key in [('CPs.pdb','critical_points'),('paths.pdb','paths'),('CPprop.txt','properties')]:
            assert len(aim[key])==manifest['files']['P03-aim-'+name]['expected']['count']
        checks.append('IGMH/IRI grids, geometry, fragments and ESP/AIM association')
    if 'P02-water_neutral_nbo_opt_freq.out' in paths:
        source=paths['P02-water_neutral_nbo_opt_freq.out'];expected=manifest['files']['P02-water_neutral_nbo_opt_freq.out']['expected']
        opt,freq=[read_source(source,index) for index in range(2)];nbo=parse_nbo(source,1,0)
        assert len(opt.metadata['optimization']['steps'])==expected['optimization_step_count']
        np.testing.assert_array_equal(freq.arrays['mode_frequencies'],expected['frequencies_cm_minus1'])
        assert len(nbo['orbitals'])==expected['nbo_count'] and len(nbo['interactions'])==expected['e2_count']
        if args.raw_root:
            raw=args.raw_root/'P02-opt/output.log'
            for index,public_data in enumerate((opt,freq)):
                original=read_source(raw,index)
                assert set(original.arrays)==set(public_data.arrays)
                for key in original.arrays:
                    np.testing.assert_array_equal(original.arrays[key],public_data.arrays[key])
                assert clean_science(original.metadata['energies'])==clean_science(public_data.metadata['energies'])
                assert clean_science(original.metadata.get('optimization'))==clean_science(public_data.metadata.get('optimization'))
            assert clean_science(parse_nbo(raw,1,0))==clean_science(nbo)
        checks.append('Owned two-job optimization/frequency/NBO and raw/public scientific equality')
    if 'P05-complex' in waves:
        assert waves['P05-co'].metadata['electron_count']==14 and waves['P05-bh3'].metadata['electron_count']==8
        np.testing.assert_allclose(waves['P05-complex'].arrays['positions'][:2],waves['P05-co'].arrays['positions'],atol=2e-7,rtol=0)
        np.testing.assert_allclose(waves['P05-complex'].arrays['positions'][2:],waves['P05-bh3'].arrays['positions'],atol=2e-7,rtol=0)
        ets=import_ets(waves['P05-complex'],paths['P05-ets-nocv.txt'],'kcal/mol')
        nocv=import_nocv(paths['P05-nocv-pair1.cub'],ets,1,'Total','electron/bohr^3')
        assert ets.metadata['analysis']['pairs']==manifest['files']['P05-ets-nocv.txt']['expected']['pairs']
        if args.derived_root:
            get=lambda data:data.arrays[data.metadata['fields'][0]['array']]
            pair=ets.metadata['analysis']['pairs'][0];work=args.derived_root/'P05/nocv'
            error=np.max(np.abs(pair['positive_eigenvalue']*get(read_cube(work/'nocv-orb1.cub'))**2+
                               pair['negative_eigenvalue']*get(read_cube(work/'nocv-orb-negative.cub'))**2-get(nocv)))
            assert error<3e-6,error
        checks.append('Frozen NOCV fragment geometry/electron counts and signed pair density')
    if 'P04-steps.csv' in paths:
        irc=import_irc(paths['P04-steps.csv']);mayer=import_irc_mayer(irc,paths['P04-mayer.csv'])
        expected=manifest['files']['P04-steps.csv']['expected'];report=expected['irc_report']
        assert report['irc_status']=='converged both directions' and report['imaginary_mode_count']==1
        assert len(irc.arrays['irc_energies'])==expected['steps']
        np.testing.assert_allclose(irc.arrays['irc_energies'],expected['energies_hartree'],atol=1e-10,rtol=0)
        np.testing.assert_allclose(mayer.arrays['mayer_orders'],manifest['files']['P04-mayer.csv']['expected']['orders'],atol=1e-11,rtol=0)
        checks.append('Complete bidirectional IRC, first-order TS and all six Mayer atom pairs')
    if 'P06-source.json' in paths:
        source=json.loads(paths['P06-source.json'].read_text())
        for sample in source['samples']:
            xyz=paths['P06-source.json'].parent/sample['file'];assert sha(xyz)==sample['sha256']
            lines=xyz.read_text().splitlines();offset=0
            for record in sample['sources']:
                expected=read_fchk(paths[record['id']]);count=int(lines[offset]);assert count==len(expected.arrays['atomic_numbers'])
                coordinates=[[float(x) for x in line.split()[1:]] for line in lines[offset+2:offset+2+count]]
                np.testing.assert_allclose(coordinates,expected.arrays['positions'],atol=1e-14,rtol=0)
                assert record['sha256']==sha(paths[record['id']]);offset+=count+2
            assert offset==len(lines)
        checks.append('P06 same-source XYZ coordinates and source identities')
    if args.require_complete:
        assert set(manifest['groups'])=={'P01','P02','P03','P04','P05','P06'}
        assert set(manifest['cases'])=={f'C{number:02d}' for number in range(1,14)}
    if args.package:
        with zipfile.ZipFile(args.package) as archive:
            names=archive.namelist();expected={record['archive_path'] for record in manifest['files'].values()}
            assert len(names)==len(set(names)) and set(names)==expected|{'LICENSE','NOTICE.md','tutorial-samples.json'}
            assert archive.read('tutorial-samples.json')==args.manifest.read_bytes()
            for record in manifest['files'].values():
                assert archive.read(record['archive_path'])==paths[record['id']].read_bytes()
            assert archive.testzip() is None
        checks.append('Public ZIP exact membership, source bytes, license allowlist and CRC')
    return dict(status='Passed',dataset_id='gaussian-v1',manifest_sha256=sha(args.manifest),
                file_count=len(paths),groups=sorted(manifest['groups']),checks=checks,
                complete=bool(args.require_complete),gui='Not Run',independent_human_review='Not Run')


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--reference-root',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,default=ROOT/'validation/shared/data/public/gaussian-v1/tutorial-samples.json')
    parser.add_argument('--derived-root',type=Path)
    parser.add_argument('--raw-root',type=Path)
    parser.add_argument('--package',type=Path)
    parser.add_argument('--private-identifiers',type=Path,help='Private JSON string list; identifiers are never written to reports')
    parser.add_argument('--require-complete',action='store_true')
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args();sys.path[:0]=[str(args.reference_root.resolve()),str(ROOT)]
    from tools.generate_gaussian_tutorial import write_json
    report=verify(args);write_json(args.report,report);print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
