import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.local_inputs import ROOT, input_path


class LocalInputs(unittest.TestCase):
    def test_missing_changed_and_unindexed_input_fail(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as directory:
            root = Path(directory)
            data = root / 'tests/data/local'
            data.mkdir(parents=True)
            path = data / 'required.log'
            index = root / 'tests/data/local-inputs.json'
            index.write_text(json.dumps({'files': {'required.log': {
                'path': 'tests/data/local/required.log', 'sha256': hashlib.sha256(b'original').hexdigest()}}}), encoding='utf-8')
            with self.assertRaises(FileNotFoundError):
                input_path('required.log', root)
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                input_path('required.log', root)
            path.write_bytes(b'original')
            self.assertEqual(input_path('required.log', root), path)
            with self.assertRaises(KeyError):
                input_path('../required.log', root)
