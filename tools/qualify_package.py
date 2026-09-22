"""Bind local qualification evidence to the exact extension ZIP and source tree."""
import ast
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
archive_path = ROOT / 'outputs/dist/qcblender-0.0.1.zip'
digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
lock = json.loads((ROOT / 'dependencies.lock.json').read_text(encoding='utf-8'))
backend = json.loads((ROOT / 'outputs/backend-wheel.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(archive_path) as archive:
    names = set(archive.namelist())
    for source in (ROOT / 'qcblender').rglob('*.py'):
        ast.parse(source.read_bytes(), filename=str(source))
        assert archive.read(source.relative_to(ROOT / 'qcblender').as_posix()) == source.read_bytes(), source
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
for relative in ('science-reference.json', 'scientific-convergence.json', 'field-performance.json',
                 'acceptance/extension.json', 'acceptance/recovery.json', 'visual-acceptance/result.json',
                 'acceptance/failed-save.json', 'acceptance/water-mode-cold-view.json',
                 'acceptance/density-esp-cold-view.json',
                 'animation-acceptance/result.json', 'scalar-probe/result.json', 'vibration-probe.json'):
    path = ROOT / 'outputs' / relative
    report = json.loads(path.read_text(encoding='utf-8'))
    assert report['status'] == 'Passed', relative
    evidence[relative] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'report': report}
assert evidence['acceptance/extension.json']['report']['cold_open'] == 'Passed'
report = {'status': 'Passed', 'scope': 'Local automated technical qualification; independent user acceptance pending',
          'archive': archive_path.name, 'bytes': archive_path.stat().st_size, 'sha256': digest,
          'backend': backend, 'source_matches_archive': 'Passed', 'wheel_checksums': 'Passed',
          'excluded_native_gbasis': 'Passed', 'evidence': evidence}
(ROOT / 'outputs/qualification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
(archive_path.parent / (archive_path.name + '.sha256')).write_text(digest + '  ' + archive_path.name + '\n', encoding='ascii')
print(json.dumps({key: value for key, value in report.items() if key != 'evidence'}, indent=2))
