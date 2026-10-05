"""Version and file identities shared by local packaging and candidate CI."""
import hashlib
from pathlib import Path
import re
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def extension_manifest(root=ROOT):
    with (Path(root) / 'qcblender/blender_manifest.toml').open('rb') as stream:
        manifest = tomllib.load(stream)
    if not re.fullmatch(r'\d+\.\d+\.\d+', manifest['version']):
        raise ValueError('Extension version must contain three numeric components')
    return manifest


def extension_filename(root=ROOT):
    manifest = extension_manifest(root)
    return f"{manifest['id']}-{manifest['version']}.zip"


def file_record(path, relative_to=None):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return {'path': path.relative_to(relative_to).as_posix() if relative_to else path.name,
            'bytes': path.stat().st_size, 'sha256': digest.hexdigest()}


def source_identity(root=ROOT):
    root = Path(root)
    def git(*arguments):
        return subprocess.check_output(['git', *arguments], cwd=root, text=True).strip()
    commit = git('rev-parse', 'HEAD')
    if git('status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Candidate source has uncommitted or untracked changes')
    return commit, git('rev-parse', commit + ':qcblender')
