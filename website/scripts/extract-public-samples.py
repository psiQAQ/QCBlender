"""Extract only the reviewed frozen public archive, preserving relative references."""
import hashlib
import json
import pathlib
import sys
import zipfile

archive, destination, expected_hash, expected_members = sys.argv[1:]
archive = pathlib.Path(archive)
destination = pathlib.Path(destination)
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_hash:
    raise ValueError("Frozen public tutorial ZIP identity mismatch")
with zipfile.ZipFile(archive) as bundle:
    entries = bundle.infolist()
    if len(entries) != int(expected_members):
        raise ValueError("Frozen public tutorial ZIP member count mismatch")
    names = [entry.filename for entry in entries]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate ZIP members")
    records = []
    for entry in entries:
        name = pathlib.PurePosixPath(entry.filename)
        if (name.is_absolute() or ".." in name.parts or "\\" in entry.filename
                or name.parts[0] not in {"P01", "P03", "P04", "P05", "P06", "LICENSE", "NOTICE.md", "tutorial-samples.json"}
                or entry.is_dir() or (entry.external_attr >> 16) & 0o170000 == 0o120000):
            raise ValueError(f"Forbidden public ZIP member: {entry.filename}")
        data = bundle.read(entry)
        target = destination.joinpath(*name.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records.append({"path": entry.filename, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
print(json.dumps(records))
