"""Fetch local-only examples with fixed hashes; no Gaussian software is downloaded."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / 'outputs/log-examples'
target.mkdir(parents=True, exist_ok=True)
for record in json.loads((ROOT / 'tests/data/local-log-downloads.json').read_text(encoding='utf-8')):
    path = target / record['file']
    if not path.exists():
        with urlopen(record['url'], timeout=90) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != record['sha256']:
            raise ValueError('Download checksum mismatch: ' + path.name)
        path.write_bytes(content)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], path.name
    print('Verified: ' + path.name)
