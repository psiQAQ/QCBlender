"""Finite rectangular sections of affine scalar grids, in view-local angstroms."""
import itertools

import numpy as np


def _points_in_view(points, source_to_view):
    matrix = np.asarray(source_to_view, dtype=float)
    points = np.asarray(points, dtype=float)
    if matrix.shape != (4, 4) or points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(matrix).all() or not np.isfinite(points).all():
        raise ValueError('Plane coordinates and transform must be finite')
    if not np.allclose(matrix[3], (0, 0, 0, 1), atol=1e-10) or abs(np.linalg.det(matrix[:3, :3])) < 1e-12:
        raise ValueError('Source-to-view transform must be invertible and affine')
    return points @ matrix[:3, :3].T + matrix[:3, 3]


def _unit(vector):
    length = np.linalg.norm(vector)
    if not np.isfinite(length) or length < 1e-10:
        raise ValueError('Plane axes are collinear or degenerate')
    return vector / length


def validate_configuration(field_positions, field_numbers, atom_positions, atom_numbers,
                           field_to_view, atom_to_view, field_source, atom_source,
                           field_job, atom_job, association=None):
    """Require the selected atom geometry to coincide with the field's configuration."""
    if not field_source or not atom_source:
        raise ValueError('Field or atom source identity is missing')
    if field_source == atom_source:
        if field_job != atom_job:
            raise ValueError('Atom view and field select different calculations')
        tolerance = 1e-5
    else:
        record = association or {}
        if (record.get('status') != 'geometry_matched'
                or record.get('reference_source') != field_source
                or record.get('moving_source') != atom_source
                or record.get('atom_mapping') != list(range(len(atom_numbers)))):
            raise ValueError('Atom view has no verified association with this field')
        tolerance = record.get('tolerance_angstrom')
        if not isinstance(tolerance, (int, float)) or not np.isfinite(tolerance) or tolerance <= 0:
            raise ValueError('Association tolerance is invalid')
    if (not np.array_equal(field_numbers, atom_numbers)
            or len(field_numbers) == 0):
        raise ValueError('Atom identities or ordering differ from the field configuration')
    field = _points_in_view(field_positions, field_to_view)
    atoms = _points_in_view(atom_positions, atom_to_view)
    if field.shape != atoms.shape or np.linalg.norm(field - atoms, axis=1).max() > tolerance + 1e-9:
        raise ValueError('Selected atom geometry differs from the field configuration')


def plane_frame(field, mode, source_to_view, position=.5, atoms=None, source_numbers=None,
                atom_to_view=None):
    """Return center, XYZ column axes, width and height for a grid section.

    `atoms` is the associated configuration in its own source coordinates.
    Source numbers are one-based; the original array order is authoritative.
    """
    shape = np.asarray(field['shape'], dtype=int)
    steps = np.asarray(field['steps'], dtype=float)
    origin = np.asarray(field['origin'], dtype=float)
    if shape.shape != (3,) or np.any(shape < 2) or steps.shape != (3, 3) or origin.shape != (3,) or not np.isfinite(steps).all() or not np.isfinite(origin).all() or abs(np.linalg.det(steps)) < 1e-12:
        raise ValueError('Scalar grid must have three independent finite axes')
    indices = np.array(list(itertools.product(*[(0, int(n)-1) for n in shape])), dtype=float)
    corners = _points_in_view(indices @ steps + origin, source_to_view)
    if mode in ('ij', 'jk', 'ki'):
        if not np.isfinite(position) or not 0 <= position <= 1:
            raise ValueError('Grid plane position must be between 0 and 1')
        first, second = {'ij': (0, 1), 'jk': (1, 2), 'ki': (2, 0)}[mode]
        fixed = ({0, 1, 2} - {first, second}).pop()
        local_steps = _points_in_view(np.vstack((origin, origin + steps)), source_to_view)
        x_hint = local_steps[first+1] - local_steps[0]
        y_hint = local_steps[second+1] - local_steps[0]
        section_indices = indices.copy()
        section_indices[:, fixed] = position * (shape[fixed]-1)
        section = _points_in_view(section_indices @ steps + origin, source_to_view)
    elif mode == 'atoms':
        if atoms is None or source_numbers is None or len(source_numbers) != 3 or len(set(source_numbers)) != 3:
            raise ValueError('Choose three distinct source atom numbers from an associated configuration')
        atoms = np.asarray(atoms, dtype=float)
        if atoms.ndim != 2 or atoms.shape[1] != 3 or any(type(n) is not int or n < 1 or n > len(atoms) for n in source_numbers):
            raise ValueError('Associated source atom number is unknown')
        selected = _points_in_view(atoms[np.asarray(source_numbers)-1],
                                   source_to_view if atom_to_view is None else atom_to_view)
        x_hint, y_hint = selected[1]-selected[0], selected[2]-selected[0]
    else:
        raise ValueError('Unknown plane definition')
    x_axis = _unit(x_hint)
    z_axis = _unit(np.cross(x_axis, y_hint))
    y_axis = np.cross(z_axis, x_axis)
    if mode == 'atoms':
        center_on_plane = selected[0]
        section = []
        for a, b in ((0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6),
                     (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)):
            da, db = np.dot(corners[[a, b]] - center_on_plane, z_axis)
            if abs(da) <= 1e-9:
                section.append(corners[a])
            if da * db < 0 or abs(db) <= 1e-9:
                section.append(corners[a] + (-da / (db-da)) * (corners[b]-corners[a]) if abs(db-da) > 1e-12 else corners[b])
        if not section:
            raise ValueError('Atom plane does not intersect the scalar grid')
        section = np.asarray(section)
    projection = np.column_stack(((section - section[0]) @ x_axis, (section - section[0]) @ y_axis))
    low, high = projection.min(axis=0), projection.max(axis=0)
    width, height = high - low
    if min(width, height) < 1e-9:
        raise ValueError('Plane section has no rectangular area')
    center = section[0] + (low[0]+high[0])/2*x_axis + (low[1]+high[1])/2*y_axis
    return center, np.column_stack((x_axis, y_axis, z_axis)), float(width), float(height)
