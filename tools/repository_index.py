"""Generate a Blender repository index from the exact qualified extension ZIP."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.package_identity import extension_manifest, file_record

REPOSITORY = 'psiQAQ/QCBlender'
INDEX_URL = 'https://notes.psiqaq.cn/QCBlender/index.json'


def asset_url(version, name):
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
        raise ValueError('Invalid version or release asset name')
    return f'https://github.com/{REPOSITORY}/releases/download/v{version}/{name}'


def verify_index(document, manifest, candidate):
    if document.get('version') != 'v1' or document.get('blocklist') != [] or len(document.get('data', [])) != 1:
        raise ValueError('Repository must contain exactly one extension and no blocklist')
    item = document['data'][0]
    for key in ('id', 'version', 'type', 'blender_version_min', 'blender_version_max', 'platforms'):
        if item.get(key) != manifest.get(key):
            raise ValueError('Repository compatibility differs from extension manifest: ' + key)
    if item.get('platforms') != ['windows-x64']:
        raise ValueError('Preview repository supports only Windows x64')
    expected = dict(archive_size=candidate['bytes'], archive_hash='sha256:' + candidate['sha256'],
                    archive_url=asset_url(manifest['version'], candidate['path']))
    if any(item.get(key) != value for key, value in expected.items()):
        raise ValueError('Repository archive identity or fixed download URL differs from candidate')


def generate(blender, candidate, output, scan_dir, root=ROOT, env=None):
    candidate, output, scan_dir = Path(candidate), Path(output), Path(scan_dir)
    manifest = extension_manifest(root)
    record = file_record(candidate)
    if record['path'] != f"qcblender-{manifest['version']}.zip":
        raise ValueError('Unexpected candidate filename')
    if output.name != 'index.json':
        raise ValueError('Repository index must be named index.json')
    scan_dir.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(candidate, scan_dir / candidate.name)
    # Only the extension belongs in this directory; the tutorial is not an extension.
    command = [str(blender), '--background', '--factory-startup', '--offline-mode',
               '--command', 'extension', 'server-generate', '--repo-dir', str(scan_dir)]
    process = subprocess.Popen(command, cwd=root, env=env)
    receipt = dict(pid=process.pid, command=command, status='running')
    receipt_path = scan_dir / 'execution.json'
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    code = process.wait()
    receipt.update(status='Passed' if code == 0 else 'Failed', exit_code=code)
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    if code:
        raise subprocess.CalledProcessError(code, command)
    document = json.loads((scan_dir / 'index.json').read_text(encoding='utf-8'))
    if len(document.get('data', [])) != 1:
        raise ValueError('Official server-generate did not produce exactly one extension')
    document['data'][0]['archive_url'] = asset_url(manifest['version'], candidate.name)
    verify_index(document, manifest, record)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    return file_record(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('blender', 'candidate', 'output', 'scan-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.blender, args.candidate, args.output, args.scan_dir)))


if __name__ == '__main__':
    main()
