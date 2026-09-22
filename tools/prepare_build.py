"""Prepare developer-only build tools under outputs; never alter Blender Python."""
import argparse
from importlib.metadata import distributions
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uv', default=shutil.which('uv'))
    args = parser.parse_args()
    if not args.uv:
        raise RuntimeError('Provide --uv with an existing uv executable')
    out = ROOT / 'outputs'
    env = os.environ.copy()
    for key, folder in [('UV_CACHE_DIR', 'uv-cache'),
                        ('TEMP', 'process-temp'), ('TMP', 'process-temp')]:
        (out / folder).mkdir(parents=True, exist_ok=True)
        env[key] = str(out / folder)
    python = Path(sys.executable)
    site = out / 'build-site'
    installed = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in distributions(path=[str(site)])}
    requirements = ROOT / 'tools/build-requirements.txt'
    expected = dict(line.split('==') for line in requirements.read_text(encoding='utf-8').splitlines() if line)
    if any(installed.get(name.lower().replace('_', '-')) != value for name, value in expected.items()):
        subprocess.run([args.uv, 'pip', 'install', '--python', str(python), '--target', str(site),
                        '--no-deps', '-r', str(requirements)], env=env, check=True)
    print('Developer build Python: ' + str(python))
    print('Developer build libraries: ' + str(site))


if __name__ == '__main__':
    main()
