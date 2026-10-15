"""Bounded, read-only summaries of scientific metadata and array descriptors.

This module does not import Blender or NumPy and never opens a dataset. Values
are source records, not evaluated geometry or scientific array statistics.
"""


def array_descriptors(records):
    """Retain only valid dimensions/dtypes, never paths, hashes or array values."""
    result = {}
    if not isinstance(records, dict):
        return result
    for name, record in records.items():
        if not isinstance(name, str) or not isinstance(record, dict):
            continue
        shape = record.get('shape')
        dtype = record.get('dtype')
        if (not isinstance(shape, (list, tuple)) or len(shape) > 4
                or any(type(size) is not int or size < 0 for size in shape)
                or not isinstance(dtype, str) or not 0 < len(dtype) <= 64):
            continue
        result[name] = {'shape': tuple(shape), 'dtype': dtype}
    return result


def _text(value):
    if isinstance(value, str):
        return value if len(value) <= 256 else value[:255] + '…'
    return value if type(value) in (int, float, bool) else None


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, (list, tuple)) else ()


def _count(value):
    return value if type(value) is int and value >= 0 else None


def _row(key, label, value=None, unit=None, descriptor=None):
    descriptor = _dict(descriptor)
    return {'key': _text(key), 'label': label, 'value': _text(value), 'unit': _text(unit),
            'shape': list(descriptor['shape']) if 'shape' in descriptor else None,
            'dtype': _text(descriptor.get('dtype'))}


def _step(current, total):
    current, total = _count(current), _count(total)
    if current is None or current == 0:
        return None
    return f'{current} / {total}' if total else str(current)


def summarize_object(context, metadata, descriptors=None, limit=6):
    """Return UI rows for one explicit subject; missing values remain ``None``.

    ``context`` is a small snapshot of the selected object and its source owner.
    All indices in it are already one-based except ``selected_job`` in metadata.
    Category counts refer to fields, orbitals, modes, trajectory kinds, or
    external analyses respectively (one analysis record per Dataset). External
    table/array counts are separate rows. Each category has at most ``limit``
    rows; ``omitted`` counts rows hidden by that bound, not scientific entities.
    Row labels are canonical English messages; values/units are source data.
    """
    limit = min(16, max(1, limit)) if type(limit) is int else 6
    context, metadata = _dict(context), _dict(metadata)
    result = {'available': bool(context.get('is_qc')), 'state': 'empty',
              'short': [], 'details': [], 'categories': []}
    if not result['available']:
        return result
    short = result['short']
    short.append(_row('object', 'Object', context.get('object')))
    if context.get('owner'):
        short.append(_row('owner', 'Owner', context['owner']))
    short.append(_row('view_type', 'View Type', context.get('view_type')))
    result['state'] = ('unbound' if not context.get('bound') else
                       'error' if 'error' in metadata else
                       'ready' if metadata else 'uncached')
    error = metadata.get('error')
    if result['state'] != 'ready':
        metadata, descriptors = {}, {}
    source = _dict(metadata.get('source'))
    descriptors = array_descriptors(descriptors)
    atoms = descriptors.get('atomic_numbers', {}).get('shape', ())
    atom_count = atoms[0] if len(atoms) == 1 else _count(metadata.get('_atom_count'))
    short.extend([_row('atom_count', 'Source Atoms', atom_count),
                  _row('source', 'Source', source.get('filename'))])
    job = _count(metadata.get('selected_job'))
    short.append(_row('calculation', 'Calculation',
                      _step(job + 1, len(_list(metadata.get('jobs')))) if job is not None else None))
    trajectory = _dict(metadata.get('trajectory'))
    optimization = _dict(metadata.get('optimization'))
    analysis = _dict(metadata.get('analysis'))
    steps = (
        ('xyz', 'XYZ Frame', context.get('xyz_frame'),
         len(_list(trajectory.get('frames'))) or len(_list(metadata.get('xyz_frames')))),
        ('optimization', 'Optimization Step', context.get('optimization_step'),
         len(_list(optimization.get('steps')))),
        ('irc', 'IRC Step', context.get('irc_step'),
         len(_list(analysis.get('steps'))) if analysis.get('kind') == 'IRC' else 0),
    )
    for key, label, current, total in steps:
        if key == 'xyz' and current is None and len(_list(metadata.get('xyz_frames'))) == 1:
            current = 1
        if current is not None:
            short.append(_row(key, label, _step(current, total or context.get(key + '_count'))))
    details = result['details']
    for key, label, value in (
        ('method', 'Method', metadata.get('method', analysis.get('method'))),
        ('basis', 'Basis', metadata.get('basis_name', analysis.get('basis_name'))),
        ('status', 'Calculation Status', metadata.get('calculation_status')),
        ('parser', 'Parser', source.get('parser')),
        ('coordinate_unit', 'Coordinate Unit', metadata.get('coordinate_unit')),
        ('source_sha256', 'Source SHA-256', source.get('sha256')),
    ):
        details.append(_row(key, label, value))
    if error is not None:
        details.append(_row('error', 'Dataset', error))
    if 'positions' in descriptors:
        details.append(_row('positions', 'Source Coordinates', unit=metadata.get('coordinate_unit'),
                            descriptor=descriptors['positions']))

    def category(key, label, count, rows):
        result['categories'].append({'key': key, 'label': label,
                                     'count': count if result['state'] == 'ready' else None,
                                     'items': rows[:limit], 'omitted': max(0, len(rows) - limit)})

    fields = _list(metadata.get('fields'))
    # Only bounded field records are touched; grid samples and validity arrays
    # are deliberately not inspected or counted as measured valid points.
    field_rows = []
    for index, value in enumerate(fields[:limit]):
        field = _dict(value)
        descriptor = descriptors.get(field.get('array'))
        if descriptor is None:
            shape = field.get('shape')
            if (isinstance(shape, (list, tuple)) and len(shape) <= 4
                    and all(type(size) is int and size >= 0 for size in shape)):
                descriptor = {'shape': tuple(shape)}
        field_rows.append(_row(str(index), 'Field', field.get('quantity', field.get('name', field.get('array'))),
                               field.get('unit'), descriptor))
    profile = _dict(metadata.get('profile'))
    if profile and len(field_rows) < limit:
        field_rows.append(_row('profile', 'Profile Samples', _count(profile.get('sample_count')),
                               _dict(profile.get('field')).get('unit'), descriptors.get('profile_values')))
    field_total = len(fields) + bool(profile)
    category('fields', 'Fields', field_total, field_rows)
    result['categories'][-1]['omitted'] = max(0, field_total - limit)

    orbitals = _dict(metadata.get('orbitals'))
    coefficients = descriptors.get('mo_coeffs', {})
    orbital_count = coefficients.get('shape', (None,))[-1] if coefficients.get('shape') else None
    if orbital_count is None and orbitals:
        alpha, beta = _count(orbitals.get('norba')), _count(orbitals.get('norbb'))
        orbital_count = (alpha + beta if orbitals.get('kind') == 'unrestricted'
                         and alpha is not None and beta is not None else alpha)
    orbital_rows = []
    if orbitals:
        orbital_rows.append(_row('kind', 'Orbital Type', orbitals.get('kind')))
    for key, label, unit in (('mo_coeffs', 'Coefficients', None),
                             ('mo_occs', 'Occupations', None),
                             ('mo_energies', 'Orbital Energies', orbitals.get('energy_unit'))):
        if key in descriptors:
            orbital_rows.append(_row(key, label, None, unit, descriptors[key]))
    category('orbitals', 'Orbitals', orbital_count if orbitals or orbital_rows else 0, orbital_rows)

    modes = _dict(metadata.get('modes'))
    frequencies = descriptors.get('mode_frequencies', {}).get('shape', ())
    mode_rows = []
    for key, label, unit in (('mode_frequencies', 'Frequencies', modes.get('frequency_unit')),
                             ('mode_displacements', 'Displacements', None),
                             ('mode_ir_intensities', 'IR Intensities', modes.get('ir_unit'))):
        if key in descriptors:
            mode_rows.append(_row(key, label, None, unit, descriptors[key]))
    category('vibrations', 'Vibrations', frequencies[0] if len(frequencies) == 1 else None if modes else 0, mode_rows)

    trajectory_rows = []
    for key, label, info, array in (
        ('xyz', 'XYZ Frames', trajectory, trajectory.get('array', 'trajectory_positions')),
        ('optimization', 'Optimization Steps', optimization, 'optimization_positions'),
        ('irc', 'IRC Steps', analysis if analysis.get('kind') == 'IRC' else {}, 'irc_positions'),
    ):
        descriptor = descriptors.get(array)
        records = _list(info.get('frames' if key == 'xyz' else 'steps'))
        if info or descriptor:
            shape = descriptor.get('shape', ()) if descriptor else ()
            trajectory_rows.append(_row(key, label, len(records) or (shape[0] if shape else None),
                                        info.get('coordinate_unit', metadata.get('coordinate_unit')), descriptor))
    category('trajectories', 'Trajectories', len(trajectory_rows), trajectory_rows)

    external_rows = []
    external_total = 0

    def external(row):
        nonlocal external_total
        external_total += 1
        if len(external_rows) < limit:
            external_rows.append(row)

    external_analysis = bool(analysis) and analysis.get('kind') != 'IRC'
    if external_analysis:
        external(_row('kind', 'Analysis Type', analysis.get('kind')))
        for key, label, unit_key in (
            ('sources', 'Source Files', None), ('critical_points', 'Critical Points', 'coordinate_unit'),
            ('paths', 'Paths', 'coordinate_unit'), ('extrema', 'Extrema', 'extrema_unit'),
            ('area_bins', 'Area Bins', 'area_unit'), ('pairs', 'Pairs', 'energy_unit'),
            ('orbitals', 'NBO Orbitals', 'orbital_energy_unit'),
            ('interactions', 'NBO Interactions', 'interaction_energy_unit'),
            ('step_sources', 'Step Sources', None),
        ):
            records = analysis.get(key)
            if isinstance(records, list):
                external(_row(key, label, len(records), analysis.get(unit_key)))
        # Analysis array groups retain their stored dimensions, without walking
        # large per-atom/per-step numerical tables from the scientific arrays.
        for key, descriptor in descriptors.items():
            if key.startswith(('mayer_', 'nbo_', 'profile_', 'scatter_')):
                external(_row(key, 'Array', key, analysis.get('unit'), descriptor))
    category('external_analysis', 'External Analysis', int(external_analysis), external_rows)
    result['categories'][-1]['omitted'] = max(0, external_total - limit)
    return result
