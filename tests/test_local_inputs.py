import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from tools.workspace_paths import temporary_tests_root
from unittest.mock import patch

from tools.local_inputs import CATALOG, DATA, ROOT, input_path, public_input_path


class LocalInputs(unittest.TestCase):
    def test_missing_changed_and_unindexed_input_fail(self):
        with tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT)) as directory:
            root = Path(directory)
            data = root / 'validation/shared/data/local'
            data.mkdir(parents=True)
            path = data / 'required.log'
            index = root / 'validation/shared/data/local-inputs.json'
            index.write_text(json.dumps({'files': {'required.log': {
                'path': 'validation/shared/data/local/required.log', 'sha256': hashlib.sha256(b'original').hexdigest()}}}), encoding='utf-8')
            with self.assertRaises(FileNotFoundError):
                input_path('required.log', root)
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                input_path('required.log', root)
            path.write_bytes(b'original')
            self.assertEqual(input_path('required.log', root), path)
            with self.assertRaises(KeyError):
                input_path('unknown.log', root)
            for invalid in ('../required.log', 'nested/../required.log', '/required.log',
                            'C:/required.log', 'nested\\required.log', ''):
                with self.subTest(key=invalid), self.assertRaises(ValueError):
                    input_path(invalid, root)

    def test_shared_public_keys_and_reference_root_use_one_verified_copy(self):
        with tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT)) as directory:
            root = Path(directory)
            public = root / DATA / 'public/P03/igmh'
            public.mkdir(parents=True)
            files = {}
            for name in ('geometry.cub', 'color.cub'):
                path = public / name
                path.write_bytes(name.encode())
                files['public-tutorial/P03/igmh/' + name] = dict(
                    path=path.relative_to(root).as_posix(), bytes=path.stat().st_size,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            (root / CATALOG).write_text(json.dumps(dict(files=files)), encoding='utf-8')
            with patch.dict(os.environ, {'QCBLENDER_REFERENCE_ROOT': str(root)}):
                self.assertEqual(input_path('public-tutorial/P03/igmh'), public)
                self.assertEqual(input_path('public-tutorial/P03/igmh/color.cub'), public / 'color.cub')
            self.assertFalse((root / DATA / 'local/public-tutorial').exists())
            (public / 'geometry.cub').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                input_path('public-tutorial/P03/igmh', root)

    def test_catalog_cannot_escape_data_or_merge_unrelated_directories(self):
        with tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT)) as directory:
            root = Path(directory)
            (root / DATA).mkdir(parents=True)
            for relative in ('outside.log', DATA + '/regression/outside.log', '../outside.log'):
                (root / CATALOG).write_text(json.dumps({'files': {'source.log': {
                    'path': relative, 'sha256': hashlib.sha256(b'data').hexdigest()}}}), encoding='utf-8')
                with self.subTest(path=relative), self.assertRaises(ValueError):
                    input_path('source.log', root)
            files = {}
            for name in ('first', 'second'):
                path = root / DATA / 'local' / name / (name + '.log')
                path.parent.mkdir(parents=True)
                path.write_bytes(b'data')
                files['combined/' + name + '.log'] = dict(
                    path=path.relative_to(root).as_posix(), sha256=hashlib.sha256(b'data').hexdigest())
            (root / CATALOG).write_text(json.dumps(dict(files=files)), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'multiple locations'):
                input_path('combined', root)
            with patch.object(Path, 'is_junction', return_value=True), self.assertRaisesRegex(ValueError, 'Linked'):
                input_path('combined/first.log', root)
            (root / CATALOG).write_text(json.dumps({'files': {
                'nested/other/first.log': files['combined/first.log']}}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'inconsistent relative paths'):
                input_path('nested', root)

    def test_public_input_uses_archive_location_and_frozen_identity(self):
        with tempfile.TemporaryDirectory(dir=temporary_tests_root(ROOT)) as directory:
            root = Path(directory)
            path = root / DATA / 'public/P01/example.fchk'
            path.parent.mkdir(parents=True)
            path.write_bytes(b'public input')
            record = dict(distribution='included', license='CC-BY-4.0',
                          archive_path='P01/example.fchk', path='tests/data/tutorial/P01/example.fchk',
                          bytes=12, sha256=hashlib.sha256(b'public input').hexdigest())
            self.assertEqual(public_input_path(record, root), path)
            with self.assertRaises(ValueError):
                public_input_path(dict(record, distribution='external-acquisition'), root)
            with self.assertRaises(ValueError):
                public_input_path(dict(record, archive_path='../local/private.log'), root)
            path.write_bytes(b'changed public input')
            with self.assertRaises(ValueError):
                public_input_path(record, root)
