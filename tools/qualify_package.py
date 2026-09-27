"""Bind local qualification evidence to the exact extension ZIP and source tree."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import zipfile
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--candidate', type=Path, default=ROOT / 'outputs/dist/qcblender-0.0.1.zip')
parser.add_argument('--output', type=Path, default=ROOT / 'outputs/qualification.json')
parser.add_argument('--evidence-index', type=Path, help='Candidate-bound checks for an independent acceptance batch')
parser.add_argument('--installed-dir', type=Path, help='Installed extension Python source directory')
args = parser.parse_args()
archive_path = args.candidate.resolve()
digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
lock = json.loads((ROOT / 'dependencies.lock.json').read_text(encoding='utf-8'))
backend = json.loads((ROOT / 'outputs/backend-wheel.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(archive_path) as archive:
    names = set(archive.namelist())
    for source in (ROOT / 'qcblender').rglob('*.py'):
        ast.parse(source.read_bytes(), filename=str(source))
        relative = source.relative_to(ROOT / 'qcblender')
        assert archive.read(relative.as_posix()) == source.read_bytes(), source
        if args.installed_dir:
            assert (args.installed_dir / relative).read_bytes() == source.read_bytes(), relative
    assert {name for name in names if name.endswith('.py')} == {p.relative_to(ROOT / 'qcblender').as_posix() for p in (ROOT / 'qcblender').rglob('*.py')}
    packages = lock['packages'] + [backend]
    assert {n for n in names if n.endswith('.whl')} == {'wheels/' + p['filename'] for p in packages}
    for package in packages:
        raw = archive.read('wheels/' + package['filename'])
        assert hashlib.sha256(raw).hexdigest() == package['sha256'], package['filename']
    with zipfile.ZipFile(io.BytesIO(archive.read('wheels/' + backend['filename']))) as wheel:
        assert not any(n.endswith(('.pyd', '.dll', '.so')) or n.endswith('/libcint.py') for n in wheel.namelist())
        assert 'gbasis/QCBLENDER_BUILD.md' in wheel.namelist()
    assert {'LICENSE', 'THIRD_PARTY.md', 'science-sources.lock.json', 'dependencies.lock.json', 'backend-wheel.json'} <= names
    assert json.loads(archive.read('backend-wheel.json')) == backend
evidence = {}
if args.evidence_index:
    index = json.loads(args.evidence_index.read_text(encoding='utf-8'))
    assert index['candidate_sha256'] == digest, 'Evidence belongs to a different ZIP'
    assert args.installed_dir, 'Candidate-bound qualification requires an installed extension'
    assert index['checks'], 'No candidate checks recorded'
    for name, entry in index['checks'].items():
        assert entry['candidate_sha256'] == digest, (name, 'stale candidate')
        path = (args.evidence_index.parent / entry['path']).resolve(strict=True)
        assert path.is_relative_to(args.evidence_index.parent.resolve()), 'Evidence must remain inside this batch'
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry['sha256'], (name, 'changed evidence')
        report = json.loads(raw)
        assert report['status'] == 'Passed', (name, report)
        evidence[name] = {'sha256': entry['sha256'], 'report': report}
else:
    for relative in ('science-reference.json', 'scientific-convergence.json', 'field-performance.json',
                     'acceptance/extension.json', 'acceptance/recovery.json', 'visual-acceptance-v2/result.json',
                     'acceptance/failed-save.json', 'acceptance/storage-paths.json', 'acceptance/water-mode-cold-view.json',
                     'acceptance/density-esp-cold-view.json',
                     'animation-acceptance-v2/result.json', 'scalar-probe/result.json', 'vibration-probe.json',
                     'node-assets/report.json', 'fog-acceptance/report.json', 'layer-acceptance/report.json',
                     'composable/report.json'):
        path = ROOT / 'outputs' / relative
        report = json.loads(path.read_text(encoding='utf-8'))
        assert report['status'] == 'Passed', relative
        evidence[relative] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'report': report}
    assert evidence['acceptance/extension.json']['report']['cold_open'] == 'Passed'
    assert evidence['fog-acceptance/report.json']['report']['cold_open_render'] == 'Passed'
    assert evidence['layer-acceptance/report.json']['report']['cold_open'] == 'Passed'
    assert evidence['layer-acceptance/report.json']['report']['undo'] == 'Passed'
    assert evidence['layer-acceptance/report.json']['report']['vibration_copy_independence'] == 'Passed'
    assert evidence['fog-acceptance/report.json']['report']['plane_box_clip_render'] == 'Passed'
    assert evidence['fog-acceptance/report.json']['report']['opacity_curve_render'] == 'Passed'
    assert evidence['composable/report.json']['report']['phase_opacity_after_mapping'] == 'Passed'
    assert evidence['composable/report.json']['report']['surface_style_render'] == 'Passed'
report = {'status': 'Passed', 'scope': 'Local automated technical qualification; independent user acceptance pending',
          'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'evidence_index': str(args.evidence_index) if args.evidence_index else None,
          'installed_matches_archive': 'Passed' if args.installed_dir else 'Not Run',
          'archive': str(archive_path), 'bytes': archive_path.stat().st_size, 'sha256': digest,
          'backend': backend, 'source_matches_archive': 'Passed', 'wheel_checksums': 'Passed',
          'excluded_native_gbasis': 'Passed', 'evidence': evidence}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
(archive_path.parent / (archive_path.name + '.sha256')).write_text(digest + '  ' + archive_path.name + '\n', encoding='ascii')
print(json.dumps({key: value for key, value in report.items() if key != 'evidence'}, indent=2))
