"""Scientific records and array storage, independent of Blender."""
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import uuid

import numpy as np

# CODATA 2022, bohr radius in angstrom. Scalar field units remain atomic units.
BOHR_ANGSTROM = 0.529177210544
SCHEMA = '0.1'


def filesystem_path(path):
    """Use extended Windows paths for Python I/O, independent of the host manifest."""
    value = os.path.abspath(path)
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        value = '\\\\?\\UNC\\' + value[2:] if value.startswith('\\\\') else '\\\\?\\' + value
    return Path(value)


def unprefixed_path(path):
    """Keep Blender references and public dataset paths in ordinary path syntax."""
    value = str(path)
    if os.name == 'nt':
        if value.startswith('\\\\?\\UNC\\'):
            value = '\\\\' + value[8:]
        elif value.startswith('\\\\?\\'):
            value = value[4:]
    return Path(value)


def dataset_path_key(path):
    """Compare resolved host paths without filesystem access or storage prefixes."""
    if not path:
        return ''
    normalized = os.path.normpath(path)
    return os.path.normcase(os.path.normpath(unprefixed_path(normalized)))


def resolve_asset(directory, relative):
    root = filesystem_path(directory).resolve(strict=True)
    path = Path(relative)
    if path.is_absolute() or path.drive or '..' in path.parts:
        raise ValueError('Project asset must use a contained relative path')
    resolved = (root / path).resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError('Project asset escapes its data directory')
    return unprefixed_path(resolved)


def _file_sha256(path):
    with filesystem_path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def volume_cache(directory, scalar):
    path = resolve_asset(directory, scalar.get('vdb', 'field.vdb'))
    if scalar.get('vdb_sha256') and _file_sha256(path) != scalar['vdb_sha256']:
        raise ValueError('Volume cache checksum mismatch; rebuild it from scientific arrays')
    return path


def orbital_selection(data, spin, choice='EXPLICIT', number=1):
    info = data.metadata['orbitals']
    if spin not in ('alpha', 'beta'):
        raise ValueError('Choose alpha or beta orbitals')
    if info['kind'] == 'restricted':
        occupations = data.arrays['mo_occs']
        if 'mo_occs_aminusb' not in data.arrays and not np.allclose(occupations, np.round(occupations), atol=1e-8, rtol=0):
            raise ValueError('Fractional restricted occupations require explicit alpha-minus-beta occupations')
        difference = data.arrays.get('mo_occs_aminusb', np.minimum(occupations, 2 - occupations))
        occupations = (occupations + (difference if spin == 'alpha' else -difference)) / 2
        energies = data.arrays.get('mo_energies')
    elif info['kind'] == 'unrestricted':
        start, stop = (0, info['norba']) if spin == 'alpha' else (info['norba'], info['norba'] + info['norbb'])
        occupations = data.arrays['mo_occs'][start:stop]
        energies = data.arrays.get('mo_energies')
        energies = energies[start:stop] if energies is not None else None
    else:
        raise ValueError('Only restricted/unrestricted orbital selection is supported')
    if choice in ('HOMO', 'LUMO'):
        indices = np.flatnonzero(occupations > 1e-8 if choice == 'HOMO' else occupations <= 1e-8)
        if not len(indices):
            raise ValueError('No ' + choice + ' in the selected spin channel')
        if energies is None:
            raise ValueError('HOMO/LUMO selection requires orbital energies; choose a source number explicitly')
        index = indices[np.argmax(energies[indices]) if choice == 'HOMO' else np.argmin(energies[indices])]
    elif choice == 'EXPLICIT' and type(number) is int and 1 <= number <= len(occupations):
        index = number - 1
    else:
        raise ValueError('Orbital source number is outside the available range')
    return {'source_number': int(index) + 1, 'occupation': float(occupations[index]),
            'energy_hartree': float(energies[index]) if energies is not None else None, 'spin': spin}


@dataclass
class Dataset:
    metadata: dict
    arrays: dict[str, np.ndarray] = field(default_factory=dict)

    def validate(self):
        from .optimization import validate_optimization
        validate_optimization(self)
        from .xyz import validate_trajectory
        validate_trajectory(self)
        for name, array in self.arrays.items():
            if array.dtype.kind not in 'biuf' or array.ndim > 4 or not np.isfinite(array).all():
                raise ValueError(f'Invalid scientific array: {name}')
        numbers = self.arrays['atomic_numbers']
        coords = self.arrays['positions']
        if numbers.ndim != 1 or coords.shape != (len(numbers), 3):
            raise ValueError('Atom identities and positions must have shapes (N,) and (N,3)')
        if numbers.dtype.kind not in 'iu' or np.any((numbers < 0) | (numbers > 118)):
            raise ValueError('Atomic numbers must be integers from 0 to 118')
        if self.metadata.get('coordinate_unit') != 'angstrom':
            raise ValueError('Dataset coordinates must be in angstrom')
        bonds = self.arrays.get('bonds')
        if bonds is not None and (bonds.ndim != 2 or bonds.shape[1] != 2 or bonds.dtype.kind not in 'iu'
                                  or np.any(bonds < 0) or np.any(bonds >= len(numbers))):
            raise ValueError('Bond endpoints must reference existing atoms')
        for prop in self.metadata.get('charges', []):
            if self.arrays[prop['array']].shape != numbers.shape:
                raise ValueError('Atomic charge shape does not match geometry')
        for scalar in self.metadata.get('fields', []):
            values, mask = self.arrays[scalar['array']], self.arrays[scalar['valid_mask']]
            if values.shape != tuple(scalar['shape']) or values.ndim != 3 or mask.shape != values.shape or mask.dtype.kind != 'b':
                raise ValueError('Scalar field values/grid/validity shapes disagree')
            origin, steps = np.asarray(scalar['origin']), np.asarray(scalar['steps'])
            if (origin.shape != (3,) or steps.shape != (3, 3) or not np.isfinite(origin).all()
                    or not np.isfinite(steps).all() or abs(np.linalg.det(steps)) < 1e-15):
                raise ValueError('Scalar field affine grid is invalid')
        if 'modes' in self.metadata:
            count = len(self.arrays['mode_frequencies'])
            if self.arrays['mode_displacements'].shape != (count, len(numbers), 3):
                raise ValueError('Vibrational displacement shape does not match modes/atoms')


def save_dataset(data, directory):
    """Commit a new manifest only after all content-addressed arrays are written."""
    data.validate()
    directory = filesystem_path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    array_dir = directory / 'arrays'
    array_dir.mkdir(exist_ok=True)
    if not array_dir.resolve().is_relative_to(directory):
        raise ValueError('Array directory escapes project root')
    records = {}
    for name, array in data.arrays.items():
        temporary = array_dir / (uuid.uuid4().hex + '.pending')
        try:
            with temporary.open('xb') as stream:
                np.save(stream, array, allow_pickle=False)
            digest = _file_sha256(temporary)
            relative = f'arrays/{digest}.npy'
            destination = directory / relative
            if not destination.resolve().is_relative_to(directory):
                raise ValueError('Array path escapes project root')
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        records[name] = {'path': relative, 'sha256': digest,
                         'dtype': array.dtype.str, 'shape': list(array.shape)}
    manifest = {'format': 'qcblender.project', 'schema': SCHEMA,
                'metadata': data.metadata, 'arrays': records}
    pending = directory / (uuid.uuid4().hex + '.json.pending')
    try:
        pending.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        os.replace(pending, directory / 'manifest.json')
    finally:
        pending.unlink(missing_ok=True)
    return unprefixed_path(directory / 'manifest.json')


def load_dataset(directory, max_bytes=1024**3):
    directory = filesystem_path(directory).resolve(strict=True)
    manifest_path = directory / 'manifest.json'
    if manifest_path.stat().st_size > 16 * 1024**2:
        raise ValueError('Manifest exceeds size limit')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('format') != 'qcblender.project' or manifest.get('schema') != SCHEMA:
        raise ValueError('Unsupported QCBlender project schema')
    arrays, total = {}, 0
    for name, record in manifest['arrays'].items():
        relative = Path(record['path'])
        if relative.is_absolute() or relative.drive or '..' in relative.parts:
            raise ValueError(f'Unsafe array path: {name}')
        path = (directory / relative).resolve(strict=True)
        if not path.is_relative_to(directory):
            raise ValueError(f'Array escapes project: {name}')
        total += path.stat().st_size
        if total > max_bytes:
            raise MemoryError('Project arrays exceed memory budget')
        if _file_sha256(path) != record['sha256']:
            raise ValueError(f'Array checksum mismatch: {name}')
        array = np.load(path, allow_pickle=False, mmap_mode='r')
        if array.dtype.str != record['dtype'] or list(array.shape) != record['shape']:
            raise ValueError(f'Array layout mismatch: {name}')
        if array.nbytes > max_bytes or array.dtype.kind not in 'biuf' or array.ndim > 4:
            raise ValueError(f'Unsupported array layout: {name}')
        arrays[name] = np.array(array)
    result = Dataset(manifest['metadata'], arrays)
    result.validate()
    return result
