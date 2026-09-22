"""Keep licensed cclib fixtures in tests and other downloaded evidence in outputs."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'outputs/log-fixtures'
target = ROOT / 'tests/data/cclib'
target.mkdir(parents=True, exist_ok=True)
records = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
public, downloads = [], []
for record in records:
    path = ROOT / record['path']
    if path.suffix.lower() not in ('.out', '.log'):
        continue
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
    entry = {'file': path.name, 'url': record['url'], 'sha256': record['sha256']}
    if record['url'].startswith('https://raw.githubusercontent.com/cclib/cclib/'):
        shutil.copy2(path, target / path.name)
        public.append(dict(entry, license='BSD-3-Clause'))
    else:
        downloads.append(entry)
if not any(item['file'] == 'issue746-dsdpbep86.log' for item in downloads):
    downloads.append({'file': 'issue746-dsdpbep86.log',
                      'url': 'https://github.com/cclib/cclib/files/3231956/g16.log',
                      'sha256': 'a43082b35aa8ea3c91a9ca242450bb6585a9c187dcef369d81c081499a7b7768'})
shutil.copy2(source / 'LICENSE', target / 'LICENSE')
(target / 'sources.json').write_text(json.dumps(public, indent=2) + '\n', encoding='utf-8')
(ROOT / 'tests/data/local-log-downloads.json').write_text(json.dumps(downloads, indent=2) + '\n', encoding='utf-8')
