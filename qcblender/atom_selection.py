"""Fixed source-number selections; distances use scientific angstrom coordinates."""
import math

import numpy as np


def parse_numbers(text, count):
    selected = set()
    for item in text.replace(' ', '').split(','):
        parts = item.split('-')
        if not item or len(parts) > 2 or any(not part.isascii() or not part.isdecimal() for part in parts):
            raise ValueError('Use source atom numbers such as 1,3,7-10')
        first, last = int(parts[0]), int(parts[-1])
        if first < 1 or last > count or first > last:
            raise ValueError('Source atom number is outside the molecule or the range is reversed')
        selected.update(range(first, last + 1))
    return tuple(sorted(selected))


def select_numbers(positions, seeds, radius=None, include_seeds=True):
    points = np.asarray(positions)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError('Scientific atom coordinates are invalid')
    if not seeds or any(type(number) is not int or number < 1 or number > len(points) for number in seeds):
        raise ValueError('Source atom number is outside the molecule')
    if radius is None:
        return tuple(sorted(set(seeds)))
    if not math.isfinite(radius) or radius < 0:
        raise ValueError('Neighborhood radius must be finite and nonnegative')
    distances = np.full(len(points), np.inf)
    for number in seeds:
        distances = np.minimum(distances, np.linalg.norm(points - points[number - 1], axis=1))
    selected = {index for index, distance in enumerate(distances, 1) if distance <= radius}
    if include_seeds:
        selected.update(seeds)
    else:
        selected.difference_update(seeds)
    return tuple(sorted(selected))


def combine_numbers(current, selected, mode, count):
    universe = set(range(1, count + 1))
    current, selected = set(current), set(selected)
    if not current <= universe or not selected <= universe:
        raise ValueError('Selection contains an invalid source atom number')
    operations = {'REPLACE': lambda: selected, 'UNION': lambda: current | selected,
                  'INTERSECT': lambda: current & selected, 'DIFFERENCE': lambda: current - selected,
                  'INVERT': lambda: universe - current}
    if mode not in operations:
        raise ValueError('Unknown local selection operation')
    result = tuple(sorted(operations[mode]()))
    if not result:
        raise ValueError('Local selection would be empty')
    return result


def evaluate_steps(positions, steps):
    selected = tuple(range(1, len(positions) + 1))
    for step in steps:
        seeds = tuple(step.get('seeds', ()))
        members = () if step['mode'] == 'INVERT' else select_numbers(
            positions, seeds, step.get('radius'), step.get('include_seeds', True))
        selected = combine_numbers(selected, members, step['mode'], len(positions))
    return selected
