"""Fetch the fixed official portable runtime and verify its published SHA-256."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

VERSION = '5.1.1'
FILENAME = f'blender-{VERSION}-windows-x64.zip'
BASE_URL = 'https://download.blender.org/release/Blender5.1/'
USER_AGENT = 'QCBlender-CI (+https://github.com/psiQAQ/QCBlender)'


def open_download(url):
    request = Request(url, headers={'User-Agent': USER_AGENT})
    return urlopen(request, timeout=120)


def published_digest(text, filename=FILENAME):
    matches = [parts[0].lower() for line in text.splitlines()
               if len(parts := line.split()) == 2 and parts[1].lstrip('*') == filename]
    if len(matches) != 1 or len(matches[0]) != 64 or any(c not in '0123456789abcdef' for c in matches[0]):
        raise ValueError('Official Blender checksum list has no unique valid portable checksum')
    return matches[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    checksum = output / f'blender-{VERSION}.sha256'
    with open_download(BASE_URL + checksum.name) as response:
        checksum.write_bytes(response.read())
    expected = published_digest(checksum.read_text(encoding='ascii'))
    archive_path = output / FILENAME
    digest = hashlib.sha256()
    with open_download(BASE_URL + FILENAME) as response, archive_path.open('xb') as stream:
        while block := response.read(1024 * 1024):
            digest.update(block)
            stream.write(block)
    if digest.hexdigest() != expected:
        raise ValueError('Official Blender portable ZIP checksum mismatch')
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.namelist():
            if not (output / member).resolve().is_relative_to(output):
                raise ValueError('Unsafe portable archive member')
        archive.extractall(output)
    runtime = output / FILENAME.removesuffix('.zip')
    binary, python = runtime / 'blender.exe', runtime / '5.1/python/bin/python.exe'
    if not binary.is_file() or not python.is_file():
        raise FileNotFoundError('Official portable runtime layout differs')
    report = dict(status='Passed', version=VERSION, binary=str(binary), python=str(python),
                  url=BASE_URL + FILENAME, checksum_url=BASE_URL + checksum.name, sha256=expected)
    (output / 'runtime.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
