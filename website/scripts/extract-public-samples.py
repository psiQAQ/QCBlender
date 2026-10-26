"""Inspect or extract the active, licensed tutorial package without historical inputs."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))
from tools.candidate_artifacts import verify_samples
from tools.local_inputs import checked_path
from tools.tutorial_dataset import DELIVERY, load_dataset
from tools.tutorial_bundle import EXTRAS, supplemental_files


def public_samples(root, destination=None):
    selected = load_dataset(root)
    verify_samples(root=root)
    records, payloads = [], []
    with zipfile.ZipFile(selected['package_path']) as bundle:
        for entry in bundle.infolist():
            name = PurePosixPath(entry.filename)
            if (not name.parts or name.is_absolute() or '\\' in entry.filename
                    or any(part in ('', '.', '..') for part in entry.filename.split('/'))
                    or entry.is_dir() or (entry.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Forbidden public ZIP member: ' + entry.filename)
            data = bundle.read(entry)
            records.append(dict(path=entry.filename, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
            if destination is not None:
                payloads.append((checked_path(destination, entry.filename), data))
    supplemental = []
    if (root / EXTRAS).exists():
        for name, entry in supplemental_files(root, require_complete=False).items():
            member = name.removeprefix('validation/shared/data/public/')
            supplemental.append(dict(path=member, bytes=entry['bytes'], sha256=entry['sha256']))
            if destination is not None:
                payloads.append((checked_path(destination, member), checked_path(root, name).read_bytes()))
    # Verify every member and output path before creating any extracted data.
    for target, data in payloads:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    archive = dict(source=selected['package_record']['path'],
                   bytes=selected['package_record']['bytes'], sha256=selected['package_record']['sha256'],
                   download=selected['package_path'].name, members=len(records),
                   dataset_id=selected['dataset_id'])
    return dict(delivery=DELIVERY, archive=archive, samples=records, supplemental=supplemental,
                manifest_member='tutorial-samples.json' if selected['legacy'] else
                selected['manifest_record']['path'].split('/public/', 1)[1])


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--root', type=Path, default=REPOSITORY)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    if not args.inspect and args.destination is None:
        parser.error('Choose --inspect or --destination')
    if args.inspect and args.destination is not None:
        parser.error('--inspect does not write a destination')
    print(json.dumps(public_samples(args.root, args.destination)))


if __name__ == '__main__':
    main()
