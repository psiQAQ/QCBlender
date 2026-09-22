"""Fetch exactly the wheels in the reviewed lock, without installing or resolving."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def fetch(info):
    package, version = info['name'], info['version']
    path = ROOT / 'outputs' / 'wheels' / info['filename']
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with urlopen(info['url'], timeout=120) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != info['sha256']:
            raise ValueError(f'{package}: download checksum mismatch')
        path.write_bytes(data)
    if hashlib.sha256(path.read_bytes()).hexdigest() != info['sha256']:
        raise ValueError(f'{package}: cached checksum mismatch')
    print(f'{package} {version}: verified {path.stat().st_size} bytes', flush=True)


if __name__ == '__main__':
    lock = json.loads((ROOT / 'dependencies.lock.json').read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch, lock['packages']))
