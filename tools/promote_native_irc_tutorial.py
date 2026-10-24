"""Assemble Gaussian-v2 from frozen Gaussian-v1 and the native IRC supplement.

No calculation is rerun and no historical file is overwritten. Run with the
existing scientific Python environment: python -m tools.promote_native_irc_tutorial.
"""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

from tools.generate_gaussian_tutorial import write_json
from tools.local_inputs import verify_file

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'validation/shared/data/public'
DATASET = 'gaussian-v2'
BASE = PUBLIC / DATASET
PACKAGE = ROOT / 'validation/agent/packages/qcblender-public-tutorial-samples-v4.zip'
DELIVERY = ROOT / 'validation/agent/acceptance/tutorial-sample-delivery.json'


def identity(path):
    raw = path.read_bytes()
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def preserve_write(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise FileExistsError('Refusing to replace a different dataset artifact: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def build():
    from qcblender.readers import read_fchk, read_source
    from qcblender.gaussian_log import inspect_log
    from qcblender.irc import import_irc, import_irc_mayer

    old_path = PUBLIC / 'gaussian-v1/tutorial-samples.json'
    old = json.loads(old_path.read_text(encoding='utf-8'))
    native_root = PUBLIC / 'gaussian-native-irc-v1'
    native_path = native_root / 'native-irc.json'
    native = json.loads(native_path.read_text(encoding='utf-8'))
    delivery = json.loads(DELIVERY.read_text(encoding='utf-8'))
    manifest = copy.deepcopy(old)
    manifest.update(dataset_id=DATASET, date='2026-10-24', files={})
    manifest['scientific_scope']['irc'] = native['calculation']
    manifest['upstream_datasets'] = [
        dict(dataset_id='gaussian-v1', manifest=old_path.relative_to(ROOT).as_posix(), **identity(old_path)),
        dict(dataset_id=native['dataset_id'], manifest=native_path.relative_to(ROOT).as_posix(), **identity(native_path))]

    def add(sid, relative, raw, role, expected=None, calculation=None, producer=None, upstream=None):
        target = BASE / relative
        preserve_write(target, raw)
        row = dict(id=sid, path=target.relative_to(ROOT).as_posix(),
                   archive_path=DATASET + '/' + relative, **identity(target),
                   distribution='included', license='CC-BY-4.0',
                   license_evidence='https://creativecommons.org/licenses/by/4.0/',
                   attribution='QCBlender contributors', calculation_group=relative.split('/')[0],
                   role=role, expected=expected or {}, calculation=calculation or {},
                   producer=producer or 'Gaussian 16 C.01', quantity=None, unit=None)
        if upstream:
            row['upstream'] = upstream
        manifest['files'][sid] = row
        return row

    for sid, original in old['files'].items():
        if original['calculation_group'] in ('P04', 'P06'):
            continue
        source = ROOT / original['path']
        verify_file(source, original)
        row = copy.deepcopy(original)
        relative = Path(original['archive_path']).relative_to('gaussian-v1').as_posix()
        target = BASE / relative
        preserve_write(target, source.read_bytes())
        row.update(path=target.relative_to(ROOT).as_posix(), archive_path=DATASET + '/' + relative)
        row['upstream'] = dict(dataset_id='gaussian-v1', path=original['path'], sha256=original['sha256'])
        manifest['files'][sid] = row

    calc = dict(method='RHF', basis='STO-3G', charge=0, spin=0, multiplicity=1,
                electron_count=18, producer='Gaussian 16 C.01',
                path_integrator='Gaussian native GS2 segmented continuation (Forward/Reverse then Downhill)',
                geometry='Native Gaussian accepted point in the unchanged TS Cartesian frame')
    aliases = {'P04/ts.log': 'P04-ts-log',
               'P04/forward-endpoint-frequency.log': 'P04-forward-endpoint-log',
               'P04/reverse-endpoint-frequency.log': 'P04-reverse-endpoint-log'}
    for relative, original in native['files'].items():
        source = native_root / relative
        verify_file(source, original)
        sid = aliases.get(relative, relative.replace('/', '-'))
        expected = {}
        if source.suffix == '.fchk':
            data = read_fchk(source)
            expected = dict(atomic_numbers=data.arrays['atomic_numbers'].tolist(),
                            positions_angstrom=data.arrays['positions'].tolist(),
                            energy_hartree=data.metadata['energies'][0]['value_hartree'])
        calculation = dict(calc)
        if relative.startswith('diagnostics/'):
            calculation.pop('path_integrator')
            calculation['geometry'] = 'Preserved Gaussian diagnostic geometry; excluded from the accepted 53-frame SOP path'
        row = add(sid, relative, source.read_bytes(), 'energy_and_segment_mapping' if relative == 'P04/energies.csv' else original['role'], expected, calculation,
            upstream=dict(dataset_id=native['dataset_id'], path=source.relative_to(ROOT).as_posix(),
                          sha256=original['sha256']))
        row['calculation_group'] = 'P04'

    frames = native['frames']
    assert len(frames) == 53 and frames[26]['stage'] == 'transition_state'
    irc = import_irc(BASE / 'P04/steps.csv')
    mayer = import_irc_mayer(irc, BASE / 'P04/mayer.csv')
    ts_log = BASE / 'P04/ts.log'
    frequencies = read_source(ts_log, len(inspect_log(ts_log)['jobs'])-1).arrays['mode_frequencies'].tolist()
    report = dict(method='RHF', basis='STO-3G', charge=0, spin=0, multiplicity=1,
                  ts_step=27, ts_frequencies_cm_minus1=frequencies, imaginary_mode_count=1,
                  irc_direction='both', irc_status='converged both directions',
                  path_integrator=calc['path_integrator'], accepted_frame_count=53,
                  endpoint_relaxation_frame_count=0, monotonic_energy_tolerance_hartree=5e-9,
                  selected_steps=frames,
                  ts_mode_assignment=dict(mode='O-O torsion', out_of_plane_displacement_fraction=1.0),
                  endpoint_checks={key: dict(step=value['step'], frequencies_cm_minus1=value['frequencies_cm1'],
                      energy_hartree=value['energy_hartree'], gradient_max_hartree_per_bohr=value['gradient_max'],
                      status='Passed') for key, value in native['endpoints'].items()},
                  source_manifest='../gaussian-native-irc-v1/native-irc.json')
    manifest['files']['P04-steps.csv']['expected'] = dict(steps=53,
        energies_hartree=irc.arrays['irc_energies'].tolist(), irc_report=report)
    manifest['files']['P04-mayer.csv']['expected'] = dict(pairs=mayer.arrays['mayer_pairs'].tolist(),
        orders=mayer.arrays['mayer_orders'].tolist(), unit='dimensionless')
    for frame in frames:
        manifest['files'][f"P04-step-{frame['step']:03d}.fchk"]['expected'].update(
            direction=frame['direction'], path_stage=frame['stage'],
            source_segment=frame.get('source_segment'), parent_step=frame.get('parent_step'),
            local_accepted_point=frame.get('local_accepted_point'))

    source = json.loads((PUBLIC / 'gaussian-v1/P06/source.json').read_text(encoding='utf-8'))
    source['samples'] = source['samples'][:1]
    source['derivation'] = 'Native Gaussian FCHK coordinates; IRC representatives 1/27/53; XYZ contains no energy or wavefunction'
    water = PUBLIC / 'gaussian-v1/P06/water-dimer.xyz'
    add('P06-water-dimer.xyz', 'P06/water-dimer.xyz', water.read_bytes(), 'Same-source optimized P03 XYZ',
        dict(frames=1, source_ids=['P03-water-dimer']), producer='QCBlender coordinate export')
    xyz, records = [], []
    for number in (1, 27, 53):
        sid = f'P04-step-{number:03d}.fchk'
        row = manifest['files'][sid]
        wave = read_fchk(ROOT / row['path'])
        xyz += ['4', f'Native Gaussian GS2; P04 step {number}/53; source=../P04/step-{number:03d}.fchk']
        xyz += [symbol + ' ' + ' '.join(format(float(x), '.17g') for x in position)
                for symbol, position in zip(('O', 'O', 'H', 'H'), wave.arrays['positions'])]
        records.append(dict(id=sid, path=f'../P04/step-{number:03d}.fchk',
                            sha256=row['sha256'], source_step=number))
    raw = ('\n'.join(xyz) + '\n').encode('utf-8')
    row = add('P06-p04-three-frames.xyz', 'P06/p04-three-frames.xyz', raw,
              'Native IRC negative endpoint / TS / positive endpoint coordinates',
              dict(frames=3, source_ids=[item['id'] for item in records]), producer='QCBlender coordinate export')
    source['samples'].append(dict(file='p04-three-frames.xyz', sha256=row['sha256'], frames=3, sources=records))
    add('P06-source.json', 'P06/source.json', (json.dumps(source, ensure_ascii=False, indent=2)+'\n').encode(),
        'Exact FCHK to XYZ source mapping', producer='QCBlender coordinate export')
    for case, key in [('C10', 'fchk'), ('C11', 'mayer.txt')]:
        item = manifest['cases'][case]
        item['files'] = ['P04-steps.csv' if case == 'C10' else 'P04-mayer.csv'] + [
            f'P04-step-{number:03d}' + ('.fchk' if key == 'fchk' else '-mayer.txt') for number in range(1, 54)]
        item['gui_status'] = 'Not Run'
    manifest['cases']['C10']['gui'] = dict(step_numbers=list(range(1, 54)), ts_step=27)
    manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    preserve_write(BASE / 'tutorial-samples.json', manifest_raw)
    notice = ('# Public tutorial samples v4\n\nGaussian-v2: native Gaussian GS2 53-frame IRC, TS27; '
              'unchanged Gaussian-v1 P01/P02/P03/P05 science. CC BY 4.0; attribution QCBlender contributors. '
              'Gaussian-v1 69 frames and v3 remain separately recoverable.\n').encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        members = {row['archive_path']: (ROOT / row['path']).read_bytes() for row in manifest['files'].values()}
        members.update({'LICENSE': (PUBLIC / 'LICENSE').read_bytes(), 'NOTICE.md': notice,
                        'tutorial-samples.json': manifest_raw})
        for name, raw in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 24, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw, compresslevel=9)
    preserve_write(PACKAGE, buffer.getvalue())
    if delivery['dataset_id'] == DATASET:
        verify_file(BASE/'tutorial-samples.json', delivery['manifest'])
        verify_file(PACKAGE, delivery['package'])
        print(json.dumps(dict(status='Verified existing version; delivery unchanged', dataset_id=DATASET)))
        return
    if delivery['dataset_id'] not in ('gaussian-v1', DATASET):
        raise ValueError('Unexpected current dataset; review before promotion')
    history = copy.deepcopy(delivery.get('historical_datasets', {}))
    if delivery['dataset_id'] == 'gaussian-v1':
        history['gaussian-v1'] = {key: copy.deepcopy(delivery[key]) for key in ('dataset_id', 'manifest', 'package')}
    current = dict(schema=2, date='2026-10-24', status='Passed', dataset_id=DATASET,
        scope='Native Gaussian GS2 segmented 53-frame IRC; scientific, GUI and independent acceptance recorded separately',
        manifest=dict(path=(BASE/'tutorial-samples.json').relative_to(ROOT).as_posix(), **identity(BASE/'tutorial-samples.json')),
        package=dict(path=PACKAGE.relative_to(ROOT).as_posix(), **identity(PACKAGE)),
        historical_datasets=history, legacy_dataset=delivery['legacy_dataset'],
        checks=dict(scientific_data='Not Run', sample_package='Not Run', gui='Not Run', independent_human_review='Not Run'))
    write_json(DELIVERY, current)
    print(json.dumps(dict(dataset_id=DATASET, files=len(manifest['files']), package=current['package'])))


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT/'modules/science'))
    build()
