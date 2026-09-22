"""Bounded Gaussian Cube scalar/multiple-MO reader; datasets remain separate."""
import math
from pathlib import Path

import numpy as np

from .data import BOHR_ANGSTROM, Dataset
from .readers import infer_bonds, source_record


def read_cube(path, memory_mb=512):
    path = Path(path)
    with path.open('r', encoding='ascii') as stream:
        comments = [stream.readline().rstrip(), stream.readline().rstrip()]
        header = stream.readline().split()
        if len(header) not in (4, 5):
            raise ValueError('Cube atom/origin line must have four or five fields')
        atom_count = int(header[0])
        nvalues = int(header[4]) if len(header) == 5 else 1
        if abs(atom_count) > 100000 or not 1 <= nvalues <= 1024:
            raise ValueError('Cube atom or dataset count exceeds supported limits')
        origin = np.array([float(x.replace('D', 'E')) for x in header[1:4]])
        counts, steps = [], []
        for _ in range(3):
            row = stream.readline().split()
            if len(row) != 4:
                raise ValueError('Cube grid line requires count and three step components')
            counts.append(int(row[0]))
            steps.append([float(x.replace('D', 'E')) for x in row[1:]])
        if any(n == 0 for n in counts) or not (all(n > 0 for n in counts) or all(n < 0 for n in counts)):
            raise ValueError('Cube voxel counts must have a consistent nonzero sign')
        shape = tuple(abs(n) for n in counts)
        factor = BOHR_ANGSTROM if counts[0] > 0 else 1.0
        source_unit = 'bohr' if counts[0] > 0 else 'angstrom'
        steps = np.asarray(steps, dtype=float)
        if not np.isfinite(steps).all() or not np.isfinite(origin).all() or abs(np.linalg.det(steps)) < 1e-15:
            raise ValueError('Cube affine grid must be finite and nonsingular')
        numbers, nuclear, positions = [], [], []
        for _ in range(abs(atom_count)):
            row = stream.readline().split()
            if len(row) != 5:
                raise ValueError('Cube atom line requires atomic number, nuclear charge and position')
            numbers.append(int(row[0]))
            nuclear.append(float(row[1].replace('D', 'E')))
            positions.append([float(x.replace('D', 'E')) for x in row[2:]])
        tokens = (word for line in stream for word in line.split())
        identifiers = list(range(1, nvalues + 1))
        if atom_count < 0:
            if nvalues != 1:
                raise ValueError('Combined negative atom count and NVAL > 1 is unsupported')
            try:
                nvalues = int(next(tokens))
                if not 1 <= nvalues <= 1024:
                    raise ValueError('Cube orbital count must be from 1 to 1024')
                identifiers = [int(next(tokens)) for _ in range(nvalues)]
            except StopIteration as error:
                raise ValueError('Truncated Cube orbital identifiers') from error
            if len(set(identifiers)) != nvalues or min(identifiers) < 1:
                raise ValueError('Cube orbital identifiers must be unique positive source numbers')
        count = math.prod(shape) * nvalues
        if count * 17 > memory_mb * 1024**2:
            raise MemoryError('Cube exceeds import memory budget')
        try:
            values = np.fromiter((float(token.replace('D', 'E')) for token in tokens),
                                 dtype=np.float64, count=count)
        except ValueError as error:
            raise ValueError('Cube values are malformed or fewer than the declared grid size') from error
        if next(tokens, None) is not None:
            raise ValueError('Cube contains more values than its declared scalar datasets')
    values = values.reshape(shape + (nvalues,))
    arrays = {'atomic_numbers': np.asarray(numbers, dtype=np.int32),
              'positions': np.asarray(positions, dtype=float).reshape(-1, 3) * factor,
              'cube_nuclear_charges': np.asarray(nuclear, dtype=float)}
    fields = []
    for index, number in enumerate(identifiers):
        key, mask = f'cube_{index}', f'cube_{index}_valid'
        arrays[key] = np.ascontiguousarray(values[..., index])
        arrays[mask] = np.ones(shape, dtype=bool)
        fields.append({'quantity': 'orbital_amplitude' if atom_count < 0 else 'unknown_scalar',
                       'unit': 'bohr^-3/2' if atom_count < 0 else 'unknown', 'array': key, 'valid_mask': mask,
                       'origin': (origin * factor).tolist(), 'steps': (steps * factor).tolist(),
                       'shape': list(shape), 'coordinate_unit': 'angstrom', 'dataset_number': number,
                       'orbital_source_number': number if atom_count < 0 else None,
                       'spin': 'unknown', 'source_coordinate_unit': source_unit})
    metadata = {'source': source_record(path, 'gaussian-cube', 'qcblender.cube 0.1'),
                'coordinate_unit': 'angstrom', 'source_coordinate_unit': source_unit,
                'comments': comments, 'title': comments[0], 'calculation_status': 'unknown',
                'fields': fields, 'charges': [], 'energies': [],
                'diagnostics': ['Scalar quantity/unit need explicit user assignment'] if atom_count >= 0 else []}
    data = Dataset(metadata, arrays)
    data.validate()
    infer_bonds(data)
    return data
