"""Identity of scientific implementation and installed numerical dependencies."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

SOURCE_MEMBERS = ('evaluate.py', 'readers.py', 'data.py', 'resources.py',
                  'science_identity.py', 'science_preflight.py')
DEPENDENCIES = ('qc-gbasis', 'qc-iodata', 'numpy', 'scipy')


def scientific_identity(root=None, dependency_version=version):
    root = Path(root) if root is not None else Path(__file__).parent
    members = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
               for name in SOURCE_MEMBERS}
    dependencies = {name: dependency_version(name) for name in DEPENDENCIES}
    identity = {'schema': 1, 'sources': members, 'dependencies': dependencies}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return dict(identity, sha256=digest)


def field_cache_key(dataset_sha256, grid, parameters, blender_version, identity=None):
    identity = scientific_identity() if identity is None else identity
    payload = {'dataset': dataset_sha256, 'grid': grid,
               'parameters': {key: value for key, value in parameters.items() if key != 'memory_mb'},
               'science': identity['sha256'], 'blender': blender_version}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
