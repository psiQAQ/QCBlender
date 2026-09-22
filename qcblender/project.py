"""Create immutable dataset copies for relocatable Blender projects."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from .data import load_dataset, resolve_asset, volume_cache


def copy_dataset(source, project_root):
    source, root = Path(source).resolve(strict=True), Path(project_root).resolve()
    data = load_dataset(source)
    manifest_bytes = (source / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    identity = hashlib.sha256(manifest_bytes).hexdigest()
    destination = root / 'datasets' / identity
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.parent.resolve().is_relative_to(root):
        raise ValueError('Dataset destination escapes project root')
    if destination.exists():
        if hashlib.sha256((destination / 'manifest.json').read_bytes()).hexdigest() != identity:
            raise ValueError('Stored dataset manifest does not match its identity')
        load_dataset(destination)
        for scalar in data.metadata.get('fields', []):
            volume_cache(destination, scalar)
        return destination
    with tempfile.TemporaryDirectory(prefix='.dataset-', dir=destination.parent) as temporary:
        # Keep staging short enough for Windows CopyFile2; final identity belongs only in destination.
        candidate = Path(temporary) / 'data'
        candidate.mkdir()
        assets = {a['path']: resolve_asset(source, a['path']) for a in manifest['arrays'].values()}
        assets.update({f.get('vdb', 'field.vdb'): volume_cache(source, f) for f in data.metadata.get('fields', [])})
        for name, original in assets.items():
            target = candidate / name
            if not target.resolve().is_relative_to(candidate.resolve()):
                raise ValueError('Unsafe volume cache destination')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, target)
        (candidate / 'manifest.json').write_bytes(manifest_bytes)
        try:
            os.replace(candidate, destination)
        except OSError:
            if not destination.exists():
                raise
            # Another worker may have published the same immutable identity first.
            # Reuse only after the same manifest, array and cache checks above pass.
            return copy_dataset(source, root)
    return destination


def archive_project(blend_path, archive_path):
    import zipfile
    blend_path, archive_path = Path(blend_path).resolve(strict=True), Path(archive_path).resolve()
    data_root = blend_path.with_suffix('.qcdata')
    manifest = json.loads((data_root / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format') != 'qcblender.scene' or manifest.get('schema') != '0.1':
        raise ValueError('Unsupported scene package')
    members = {blend_path: blend_path.name, data_root / 'manifest.json': data_root.name + '/manifest.json'}
    for relative in manifest['datasets']:
        dataset = resolve_asset(data_root, relative)
        load_dataset(dataset)
        metadata = json.loads((dataset / 'manifest.json').read_text(encoding='utf-8'))
        for scalar in metadata['metadata'].get('fields', []):
            volume_cache(dataset, scalar)
        paths = ['manifest.json'] + [a['path'] for a in metadata['arrays'].values()]
        paths += [f.get('vdb', 'field.vdb') for f in metadata['metadata'].get('fields', [])]
        for name in paths:
            path = resolve_asset(dataset, name)
            members[path] = data_root.name + '/' + path.relative_to(data_root).as_posix()
    if archive_path in members:
        raise ValueError('Archive cannot overwrite a project member')
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.qc-archive-', dir=archive_path.parent) as directory:
        temporary = Path(directory) / 'project.zip'
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=3) as archive:
            for path, name in sorted(members.items(), key=lambda item: item[1]):
                archive.write(path, name)
        os.replace(temporary, archive_path)
    return archive_path
