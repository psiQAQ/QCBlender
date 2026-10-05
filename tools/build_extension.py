"""Stage verified dependencies and build with Blender's extension command."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs' / 'dist')
    parser.add_argument('--wheels-dir', type=Path, default=ROOT / 'outputs' / 'wheels')
    args = parser.parse_args()
    runtime = ROOT / 'outputs' / 'blender-runtime.json'
    blender = args.blender or Path(json.loads(runtime.read_text(encoding='utf-8'))['binary_path'])
    lock = json.loads((ROOT / 'dependencies.lock.json').read_text(encoding='utf-8'))
    backend_record = ROOT / 'outputs' / 'backend-wheel.json'
    if not backend_record.exists():
        raise RuntimeError('Build and qualify the science backend before packaging')
    packages = lock['packages'] + [json.loads(backend_record.read_text(encoding='utf-8'))]
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='extension-stage-', dir=ROOT / 'outputs') as directory:
        stage = Path(directory) / 'qcblender'
        shutil.copytree(ROOT / 'qcblender', stage, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        wheels = stage / 'wheels'
        wheels.mkdir()
        for package in packages:
            path = args.wheels_dir / package['filename']
            if hashlib.sha256(path.read_bytes()).hexdigest() != package['sha256']:
                raise ValueError(f'Wheel checksum mismatch: {path.name}')
            shutil.copy2(path, wheels / path.name)
        manifest = stage / 'blender_manifest.toml'
        text = manifest.read_text(encoding='utf-8')
        assert text.count('wheels = []') == 1
        text = text.replace('wheels = []', 'wheels = ' + json.dumps(['./wheels/' + p['filename'] for p in packages]))
        manifest.write_text(text, encoding='utf-8')
        shutil.copy2(ROOT / 'THIRD_PARTY.md', stage / 'THIRD_PARTY.md')
        shutil.copy2(ROOT / 'LICENSE', stage / 'LICENSE')
        shutil.copy2(ROOT / 'science-sources.lock.json', stage / 'science-sources.lock.json')
        shutil.copy2(ROOT / 'dependencies.lock.json', stage / 'dependencies.lock.json')
        shutil.copy2(backend_record, stage / 'backend-wheel.json')
        env = os.environ.copy()
        env['BLENDER_USER_RESOURCES'] = str(ROOT / 'outputs' / 'blender-build')
        env['BLENDER_USER_CACHE'] = str(ROOT / 'outputs' / 'blender-cache')
        subprocess.run([str(blender), '--background', '--factory-startup', '--offline-mode', '--disable-autoexec',
                        '--python-exit-code', '1', '--python', str(ROOT / 'tools' / 'build_node_assets.py'),
                        '--', '--package-root', str(stage)], env=env, check=True)
        subprocess.run([str(blender), '--background', '--factory-startup', '--offline-mode', '--disable-autoexec',
                        '--command', 'extension', 'build', '--source-dir', str(stage),
                        '--output-dir', str(output)], env=env, check=True)


if __name__ == '__main__':
    main()
