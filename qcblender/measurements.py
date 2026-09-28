"""Structural measurements from real, source-ordered coordinates in angstrom."""

import math

import numpy as np


ATOM_COUNTS = {'DISTANCE': 2, 'ANGLE': 3, 'DIHEDRAL': 4}


def parse_source_atom_numbers(expression, atom_count):
    """Read a comma/space separated list of distinct 1-based source numbers."""
    try:
        numbers = [int(piece) for piece in expression.replace(',', ' ').split()]
    except ValueError as error:
        raise ValueError('Enter source atom numbers separated by commas') from error
    if not numbers or len(numbers) != len(set(numbers)) or any(n < 1 or n > atom_count for n in numbers):
        raise ValueError('Choose distinct, existing source atom numbers')
    return numbers


def geometry_label(record):
    """Short visible context for a saved scientific geometry record."""
    kind, step = record['kind'], record['step']
    if kind == 'source' and step is None:
        return '源构型'
    if kind in ('optimization', 'irc') and type(step) is int and step > 0:
        return f'{"Optimization" if kind == "optimization" else "IRC"} Step {step}'
    raise ValueError('Annotation geometry kind or step is invalid')


def measurement_text(kind, numbers, value, record, decimals, reason=None):
    prefix = f"{'-'.join(map(str, numbers))} · {geometry_label(record)}: "
    if reason:
        return f'{prefix}undefined ({reason})'
    unit = 'Å' if kind == 'DISTANCE' else '°'
    return f'{prefix}{value:.{decimals}f} {unit}'


def validate_annotation_style(entry):
    """Reject invalid saved or edited style before touching Blender objects."""
    try:
        size, width = float(entry['size']), float(entry['line_width'])
        color = np.asarray(entry['color'], dtype=float)
        offset = np.asarray(entry['offset'], dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError('Annotation style must contain numeric values') from error
    if (not np.isfinite([size, width]).all() or size <= 0 or width <= 0
            or color.shape != (3,) or not np.isfinite(color).all()
            or (color < 0).any() or (color > 1).any()
            or offset.shape != (3,) or not np.isfinite(offset).all()
            or type(entry['decimals']) is not int or not 0 <= entry['decimals'] <= 10):
        raise ValueError('Annotation size, color, offset, width and decimals must be finite and valid')


def measure(kind, positions, source_atom_numbers):
    """Return angstrom or degrees; dihedral sign follows B→C and BA/CD projections."""
    count = ATOM_COUNTS.get(kind)
    numbers = list(source_atom_numbers)
    coords = np.asarray(positions, dtype=np.float64)
    if (count is None or len(numbers) != count or any(type(n) is not int for n in numbers)
            or len(set(numbers)) != count or coords.ndim != 2 or coords.shape[1] != 3
            or any(n < 1 or n > len(coords) for n in numbers)):
        raise ValueError('Choose distinct, existing source atom numbers in measurement order')
    points = coords[np.array(numbers) - 1]
    if not np.isfinite(points).all():
        raise ValueError('Measurement coordinates must be finite')
    if kind == 'DISTANCE':
        distance = float(np.linalg.norm(points[1] - points[0]))
        if distance <= 1e-12:
            raise ValueError('Distance is undefined: coincident atoms')
        return distance
    first, second = points[0] - points[1], points[2] - points[1]
    if kind == 'ANGLE':
        if min(np.linalg.norm(first), np.linalg.norm(second)) <= 1e-12:
            raise ValueError('Angle is undefined: zero-length arm')
        return math.degrees(math.atan2(float(np.linalg.norm(np.cross(first, second))),
                                       float(np.dot(first, second))))
    axis = points[2] - points[1]
    axis_length = float(np.linalg.norm(axis))
    if axis_length <= 1e-12:
        raise ValueError('Dihedral is undefined: zero-length central bond')
    axis /= axis_length
    last = points[3] - points[2]
    v = first - np.dot(first, axis) * axis
    w = last - np.dot(last, axis) * axis
    if min(np.linalg.norm(v), np.linalg.norm(w)) <= 1e-12:
        raise ValueError('Dihedral is undefined: terminal arm lies on central axis')
    angle = math.degrees(math.atan2(float(np.dot(np.cross(v, w), axis)), float(np.dot(v, w))))
    return 180.0 if angle <= -180.0 else angle
