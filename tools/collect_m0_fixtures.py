"""Restore pinned regression inputs from current data or retained source archives."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GBASIS_COMMIT = '071969c900d6d7a9fbbdfe193c65ba3be177fbdf'
ARCHIVES = {'iodata': 'modules/sources/iodata/iodata.zip',
            'gbasis': f'modules/sources/gbasis/gbasis-{GBASIS_COMMIT}.zip'}
LICENSES = {'chemtools': 'LICENSE', 'iodata': 'LICENSE.txt', 'gbasis': 'LICENSE'}


def archive_member(archive, suffix):
    with zipfile.ZipFile(archive) as package:
        matches = [name for name in package.namelist() if name.endswith('/' + suffix)]
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one archive member: {suffix}')
        return package.read(matches[0])


def install_bytes(target, raw, expected=None):
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Pinned fixture checksum mismatch: ' + str(target))
    if target.exists():
        if target.read_bytes() != raw:
            raise ValueError('Refusing to replace changed fixture: ' + str(target))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def restore(reference_root, target_root=ROOT):
    reference_root, target_root = Path(reference_root), Path(target_root)
    for group, license_name in LICENSES.items():
        relative = Path('validation/shared/data/regression') / group
        directory, reference = target_root / relative, reference_root / relative
        index = directory / 'sources.json'
        if not index.exists():
            install_bytes(index, (reference / 'sources.json').read_bytes())
        records = json.loads(index.read_text(encoding='utf-8'))
        archive = reference_root / ARCHIVES[group] if group in ARCHIVES else None
        for record in records:
            target, source = directory / record['file'], reference / record['file']
            if target.is_file():
                raw = target.read_bytes()
            elif source.is_file():
                raw = source.read_bytes()
            elif archive is not None:
                # Frozen sources.json records an upstream commit followed by the member path.
                relative_member = record['url'].split('/', 6)[-1]
                raw = archive_member(archive, relative_member)
            else:
                raise FileNotFoundError(f'Required centralized fixture missing: {source}; source: {record["url"]}')
            install_bytes(target, raw, record['sha256'])
        target, source = directory / license_name, reference / license_name
        if source.is_file():
            raw = source.read_bytes()
        elif archive is not None:
            raw = archive_member(archive, license_name)
        else:
            raise FileNotFoundError('Required original fixture license missing: ' + str(source))
        install_bytes(target, raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-root', type=Path, default=ROOT)
    parser.add_argument('--output-root', type=Path, default=ROOT)
    args = parser.parse_args()
    restore(args.reference_root, args.output_root)
    print('PINNED_REGRESSION_INPUTS_PASSED')


if __name__ == '__main__':
    main()
