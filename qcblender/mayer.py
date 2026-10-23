"""Mayer identities and display samples, independent of inferred molecular bonds."""
import numpy as np


def validate_mayer(data):
    record = data.metadata.get('analysis', {})
    if record.get('kind') != 'IRC-Mayer':
        return
    pairs, orders = data.arrays.get('mayer_pairs'), data.arrays.get('mayer_orders')
    count = len(data.arrays['atomic_numbers'])
    if (pairs is None or pairs.ndim != 2 or pairs.shape[1] != 2 or not len(pairs)
            or pairs.dtype.kind not in 'iu' or np.any(pairs < 1) or np.any(pairs > count)
            or np.any(pairs[:, 0] >= pairs[:, 1])
            or len(np.unique(pairs, axis=0)) != len(pairs)):
        raise ValueError('Mayer pairs must be unique ordered source atom pairs (1-based)')
    if (orders is None or orders.ndim != 2 or orders.shape[1] != len(pairs)
            or orders.shape[0] != len(record.get('step_sources', [])) or not len(orders)
            or orders.dtype.kind not in 'fiu' or not np.isfinite(orders).all()):
        raise ValueError('Mayer values must contain one finite value per pair and imported step')
    if (record.get('method') != 'Mayer' or record.get('unit') != 'dimensionless'
            or not isinstance(record.get('path_source'), str) or not record['path_source']):
        raise ValueError('Mayer method, unit or IRC source identity is missing')


def validate_binding(path, data):
    validate_mayer(data)
    record = data.metadata.get('analysis', {})
    if (record.get('kind') != 'IRC-Mayer' or path.metadata.get('analysis', {}).get('kind') != 'IRC'
            or record.get('path_source') != path.metadata['source']['sha256']
            or not np.array_equal(data.arrays['atomic_numbers'], path.arrays['atomic_numbers'])
            or not np.array_equal(data.arrays['positions'], path.arrays['positions'])
            or len(data.arrays['mayer_orders']) != len(path.arrays['irc_positions'])):
        raise ValueError('Mayer results do not match the IRC path identity, atoms or steps')
    if 'path_steps' in record and record['path_steps'] != [
            source['sha256'] for source in path.metadata['analysis']['steps']]:
        raise ValueError('Mayer results refer to different IRC step sources')


def display_samples(path, data, step):
    validate_binding(path, data)
    if type(step) is not int or not 1 <= step <= len(data.arrays['mayer_orders']):
        raise ValueError('Mayer display step is outside the imported path')
    pairs = data.arrays['mayer_pairs'] - 1
    endpoints = np.asarray(path.arrays['irc_positions'][step - 1])[pairs]
    if not np.isfinite(endpoints).all() or np.any(np.linalg.norm(endpoints[:, 1] - endpoints[:, 0], axis=1) <= 1e-12):
        raise ValueError('Mayer endpoints must be finite and have nonzero separation')
    return (endpoints.reshape(-1, 3), pairs.reshape(-1),
            np.repeat(data.arrays['mayer_orders'][step - 1], 2),
            np.repeat(np.arange(1, len(pairs) + 1), 2))


def color_range(data, manual=None):
    validate_mayer(data)
    if manual is None:
        values = data.arrays['mayer_orders']
        return float(values.min()), float(values.max())
    bounds = np.asarray(manual, dtype=float)
    if bounds.shape != (2,) or not np.isfinite(bounds).all() or bounds[0] >= bounds[1]:
        raise ValueError('Mayer manual color range requires finite minimum < maximum')
    return tuple(map(float, bounds))
