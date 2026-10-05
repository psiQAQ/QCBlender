"""Serialized dataset limit and conservative evaluation working-memory estimates."""
from io import BytesIO
import math

import numpy as np

DATASET_MAX_BYTES = 1024**3


def array_descriptor(array):
    return {'dtype': array.dtype.str, 'shape': list(array.shape),
            'fortran_order': bool(array.flags.f_contiguous and not array.flags.c_contiguous)}


def npy_bytes(record):
    dtype = np.dtype(record['dtype'])
    shape = tuple(record['shape'])
    if dtype.kind not in 'biuf' or dtype.hasobject or len(shape) > 4:
        raise ValueError('Unsupported scientific array layout')
    if any(type(n) is not int or n < 0 for n in shape):
        raise ValueError('Array dimensions must be nonnegative integers')
    header = BytesIO()
    np.lib.format.write_array_header_1_0(header, {
        'descr': np.lib.format.dtype_to_descr(dtype), 'shape': shape,
        'fortran_order': record.get('fortran_order', False)})
    return header.tell() + math.prod(shape) * dtype.itemsize


def dataset_bytes(arrays):
    return sum(npy_bytes(array_descriptor(array)) for array in arrays.values())


def enforce_dataset_limit(size, max_bytes=DATASET_MAX_BYTES):
    if size > max_bytes:
        raise MemoryError(f'Scientific dataset arrays require {size} bytes; limit is {max_bytes} bytes')
    return size


def field_resources(records, shape, nbasis, quantity, memory_mb=512,
                    max_bytes=DATASET_MAX_BYTES, validate=True):
    if type(memory_mb) is not int or not 32 <= memory_mb <= 16384:
        raise ValueError('Memory budget must be an integer from 32 to 16384 MiB')
    if len(shape) != 3 or any(type(n) is not int or n < 2 for n in shape):
        raise ValueError('Grid shape requires three integers >= 2')
    count = math.prod(shape)
    result_bytes = sum(npy_bytes(record) for name, record in records.items()
                       if name not in ('field_values', 'field_valid'))
    result_bytes += sum(npy_bytes({'dtype': dtype, 'shape': list(shape)}) for dtype in ('<f8', '|b1'))
    input_bytes = sum(math.prod(record['shape']) * np.dtype(record['dtype']).itemsize
                      for record in records.values())
    # Input arrays remain resident, including any field arrays being replaced.
    fixed = input_bytes + count * 17 + nbasis**2 * 8 * 6
    per_point = max(256, nbasis * 8 * 12,
                    nbasis**2 * 8 * 8 if quantity == 'electrostatic_potential' else 0)
    budget = memory_mb * 1024**2
    reason = None
    if result_bytes > max_bytes:
        reason = f'Scientific dataset arrays require {result_bytes} bytes; limit is {max_bytes} bytes'
    elif fixed + per_point > budget:
        reason = f'Evaluation working-memory estimate exceeds {memory_mb} MiB; reduce resolution or increase budget'
    if reason and validate:
        raise MemoryError(reason)
    return {'voxel_count': count, 'dataset_bytes': result_bytes, 'input_bytes': input_bytes,
            'minimum_working_bytes': fixed + per_point, 'budget_bytes': budget,
            'chunk': min(4096, max(1, (budget - fixed) // per_point)), 'refusal_reason': reason}
