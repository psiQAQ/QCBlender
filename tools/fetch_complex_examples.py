"""Fetch pinned public examples into ignored outputs; verify every byte on reuse."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tests/data/local/complex-examples'
MANIFEST = ROOT / 'tests/data/complex-example-sources.json'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads(MANIFEST.read_text(encoding='utf-8'))
    for record in records:
        path = OUT / record['file']
        if not path.exists():
            with urlopen(record['url'], timeout=120) as response:
                content = response.read()
            if hashlib.sha256(content).hexdigest() != record['sha256']:
                raise ValueError('Checksum mismatch: ' + path.name)
            path.write_bytes(content)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], path.name
        print('Verified:', path.name)


if __name__ == '__main__':
    main()
