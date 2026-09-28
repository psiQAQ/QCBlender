"""Summarize the original values of a stored scalar field."""

import numpy as np


def field_range(data, field_array):
    if not isinstance(field_array, str) or not field_array:
        raise ValueError('Choose a field array')
    fields = [field for field in data.metadata.get('fields', []) if field['array'] == field_array]
    if len(fields) != 1:
        raise ValueError('Field array must identify exactly one scalar field')
    field = fields[0]
    values = data.arrays[field_array]
    valid = data.arrays[field['valid_mask']]
    if values.ndim != 3 or valid.shape != values.shape or valid.dtype.kind != 'b':
        raise ValueError('Scalar field values and validity mask disagree')
    selected = values[valid]
    if not selected.size:
        raise ValueError('Field has no valid grid points')
    if not np.isfinite(selected).all():
        raise ValueError('Valid field values must be finite')
    minimum, maximum = float(selected.min()), float(selected.max())
    if not np.isfinite([minimum, maximum]).all() or minimum >= maximum:
        raise ValueError('Field range must be finite and increasing')
    center = 0.0 if minimum < 0 < maximum else minimum / 2 + maximum / 2
    if not np.isfinite(center) or not minimum < center < maximum:
        raise ValueError('Field range has no finite interior center')
    return {'minimum': minimum, 'center': center, 'maximum': maximum,
            'valid_count': int(selected.size), 'quantity': field['quantity'],
            'unit': field['unit'], 'field_array': field_array}
