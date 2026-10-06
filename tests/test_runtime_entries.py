import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.collect_m0_fixtures import archive_member, install_bytes, restore
from tools.comparison_fixture import candidate_node_library
from tools.runtime_cleanup_plan import build_file_sets, plan, verify_canonical_wheels

ROOT = Path(__file__).resolve().parents[1]


class RuntimeEntries(unittest.TestCase):
    def setUp(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / 'outputs')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_build_record_shared_files_and_path_escape(self):
        tools = self.root / 'tools'
        tools.mkdir()
        (tools / 'build-requirements.txt').write_text('build==1.3.0\n', encoding='utf-8')
        site = self.root / 'outputs/build-site'
        metadata = site / 'build-1.3.0.dist-info'
        metadata.mkdir(parents=True)
        (metadata / 'METADATA').write_text('Name: build\nVersion: 1.3.0\n', encoding='utf-8')
        (site / 'shared.py').write_text('value = 1\n', encoding='utf-8')
        (site / 'native-only.dll').write_bytes(b'obsolete')
        record = metadata / 'RECORD'
        with record.open('w', newline='', encoding='utf-8') as stream:
            csv.writer(stream).writerows([['shared.py', '', ''], ['build-1.3.0.dist-info/METADATA', '', ''],
                                         ['build-1.3.0.dist-info/RECORD', '', '']])
        _, keep, retired, errors = build_file_sets(self.root)
        self.assertIn('shared.py', keep)
        self.assertEqual(retired, ['native-only.dll'])
        self.assertEqual(errors, [])
        record.write_text('../outside.py,,\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'escapes build-site'):
            build_file_sets(self.root)

    def test_changed_pinned_input_and_ambiguous_archive_are_rejected(self):
        target = self.root / 'input.fchk'
        raw = b'original'
        digest = hashlib.sha256(raw).hexdigest()
        install_bytes(target, raw, digest)
        install_bytes(target, raw, digest)
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            install_bytes(target, b'changed', digest)
        with self.assertRaisesRegex(ValueError, 'Refusing to replace'):
            install_bytes(target, b'changed')
        archive = self.root / 'source.zip'
        with zipfile.ZipFile(archive, 'w') as package:
            package.writestr('first/LICENSE', raw)
            package.writestr('second/LICENSE', raw)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            archive_member(archive, 'LICENSE')

    def test_canonical_wheels_missing_mismatched_and_verified(self):
        directory = self.root / 'outputs/wheels'
        directory.mkdir(parents=True)
        records = [{'name': name, 'version': '1.0', 'filename': name + '-1.0-py3-none-any.whl',
                    'sha256': hashlib.sha256(name.encode()).hexdigest()}
                   for name in ('dependency', 'backend')]
        (self.root / 'dependencies.lock.json').write_text(json.dumps({'packages': records[:1]}), encoding='utf-8')
        (self.root / 'outputs/backend-wheel.json').write_text(json.dumps(records[1]), encoding='utf-8')
        with self.assertRaisesRegex(FileNotFoundError, 'canonical wheel missing'):
            plan(self.root)
        for record in records:
            (directory / record['filename']).write_bytes(record['name'].encode())
        source = directory / 'qualified' / records[1]['filename']
        source.parent.mkdir()
        source.write_bytes(b'backend')
        (directory / records[1]['filename']).write_bytes(b'wrong same-version copy')
        with self.assertRaisesRegex(ValueError, 'Canonical wheel checksum mismatch'):
            plan(self.root)
        (directory / records[1]['filename']).write_bytes(source.read_bytes())
        actual = verify_canonical_wheels(self.root)
        self.assertEqual(len(actual), 2)
        for row in actual:
            self.assertEqual(row['status'], 'Passed')
            self.assertEqual(row['expected_sha256'], row['actual_sha256'])

    def test_candidate_node_library_extract_and_reopen_identity(self):
        candidate = self.root / 'candidate.zip'
        output = self.root / 'batch/library'
        with zipfile.ZipFile(candidate, 'w') as archive:
            archive.writestr('qcblender/assets/nodes.blend', b'node library fixture')
        target = candidate_node_library(candidate, output)
        self.assertEqual(target.read_bytes(), b'node library fixture')
        before = target.stat().st_mtime_ns
        self.assertEqual(candidate_node_library(candidate, output), target)
        self.assertEqual(target.stat().st_mtime_ns, before)
        with zipfile.ZipFile(candidate, 'w') as archive:
            archive.writestr('assets/nodes.blend', b'different library')
        with self.assertRaisesRegex(ValueError, 'differs from the existing batch'):
            candidate_node_library(candidate, output)
        self.assertEqual(target.read_bytes(), b'node library fixture')
        for members in ([], ['assets/nodes.blend', 'qcblender/assets/nodes.blend']):
            with zipfile.ZipFile(candidate, 'w') as archive:
                for name in members:
                    archive.writestr(name, b'node library fixture')
            with self.subTest(members=members), self.assertRaisesRegex(ValueError, 'exactly one'):
                candidate_node_library(candidate, self.root / 'invalid')

    def test_restore_missing_inputs_from_one_archive_without_extracted_tree(self):
        reference, target = self.root / 'reference', self.root / 'target'
        for group, license_name in {'chemtools': 'LICENSE', 'iodata': 'LICENSE.txt', 'gbasis': 'LICENSE'}.items():
            source = reference / 'validation/shared/data/regression' / group
            source.mkdir(parents=True)
            raw = group.encode()
            record = {'file': 'sample.fchk', 'sha256': hashlib.sha256(raw).hexdigest(),
                      'url': f'https://raw.githubusercontent.com/theochem/{group}/commit/tests/sample.fchk'}
            (source / 'sources.json').write_text(json.dumps([record]), encoding='utf-8')
            (source / license_name).write_bytes(b'original license')
            if group == 'chemtools':
                (source / 'sample.fchk').write_bytes(raw)
            else:
                from tools.collect_m0_fixtures import ARCHIVES
                archive = reference / ARCHIVES[group]
                archive.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(archive, 'w') as package:
                    package.writestr(f'{group}-commit/tests/sample.fchk', raw)
        restore(reference, target)
        for group in ('chemtools', 'iodata', 'gbasis'):
            self.assertEqual((target / 'validation/shared/data/regression' / group / 'sample.fchk').read_bytes(), group.encode())
        changed = target / 'validation/shared/data/regression/gbasis/sample.fchk'
        changed.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            restore(reference, target)


if __name__ == '__main__':
    unittest.main()
