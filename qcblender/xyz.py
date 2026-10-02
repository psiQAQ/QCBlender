"""Strict standard XYZ frames, parsed with the existing IOData backend."""
import hashlib
from importlib.metadata import version
from io import StringIO
from pathlib import Path
import re

import numpy as np

from .data import Dataset


def read_xyz(path):
    from iodata.formats.xyz import DEFAULT_ATOM_COLUMNS, load_many
    from iodata.periodic import sym2num
    from iodata.utils import LineIterator
    from .readers import infer_bonds, source_record
    path = Path(path)
    raw = path.read_bytes()
    lines = raw.decode('utf-8-sig', errors='strict').splitlines(keepends=True)
    frames, blocks, identities = [], [], None
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        start = index
        if not re.fullmatch(r'[1-9][0-9]*', lines[index].strip()):
            raise ValueError(f'XYZ line {index + 1}: expected a positive atom count')
        count = int(lines[index])
        if count > len(lines) - index - 2:
            raise ValueError(f'XYZ frame {len(frames) + 1}: truncated atom records')
        comment = lines[index + 1].rstrip('\r\n')
        if re.search(r'\b(?:Properties|Lattice|pbc)\s*=', comment, re.IGNORECASE):
            raise ValueError('Extended XYZ Properties, Lattice and PBC are not supported')
        numbers = []
        for offset in range(count):
            words = lines[index + 2 + offset].split()
            if len(words) != 4:
                raise ValueError(f'XYZ line {index + 3 + offset}: expected element and three coordinates')
            token = words[0]
            number = int(token) if token.isascii() and token.isdigit() else sym2num.get(token.title(), 0)
            if not 1 <= number <= 118:
                raise ValueError(f'XYZ line {index + 3 + offset}: unknown or dummy element {token}')
            try:
                coords = [float(word) for word in words[1:]]
            except ValueError as error:
                raise ValueError(f'XYZ line {index + 3 + offset}: invalid coordinates') from error
            if not np.isfinite(coords).all():
                raise ValueError(f'XYZ line {index + 3 + offset}: coordinates must be finite')
            numbers.append(number)
        if identities is None:
            identities = numbers
        elif numbers != identities:
            raise ValueError('XYZ frames must have the same atom count and element order')
        end = index + count + 2
        block = ''.join(lines[start:end])
        blocks.append(block.rstrip('\r\n') + '\n')
        frames.append({'frame': len(frames) + 1, 'comment': comment,
                       'line_start': start + 1, 'line_end': end,
                       'coordinate_line_start': start + 3, 'coordinate_line_end': end,
                       'sha256': hashlib.sha256((('\ufeff' if start == 0 and raw.startswith(b'\xef\xbb\xbf') else '')
                                                  + block).encode('utf-8')).hexdigest()})
        index = end
    if not frames:
        raise ValueError('XYZ source has no frames')
    # The documented column adapter retains native angstrom values. IOData's
    # default coordinate converter uses its own Bohr constant, not Dataset's.
    columns = [DEFAULT_ATOM_COLUMNS[0], ('atcoords', None, (3,), float, float, str)]
    iterator = LineIterator(str(path))
    iterator.fh = StringIO(''.join(blocks))
    parsed = list(load_many(iterator, atom_columns=columns))
    if len(parsed) != len(frames):
        raise ValueError('IOData did not parse all validated XYZ frames')
    positions = np.stack([item['atcoords'] for item in parsed])
    arrays = {'atomic_numbers': np.asarray(parsed[0]['atnums'], dtype=np.int32),
              'positions': positions[0].copy()}
    metadata = {'source': source_record(path, 'xyz', 'qc-iodata ' + version('qc-iodata')),
                'title': frames[0]['comment'], 'coordinate_unit': 'angstrom',
                'source_coordinate_unit': 'angstrom', 'calculation_status': 'unknown',
                'diagnostics': [], 'energies': [], 'charges': [], 'fields': [],
                'xyz_frames': frames}
    if len(frames) > 1:
        arrays['trajectory_positions'] = positions
        metadata['trajectory'] = {'kind': 'xyz', 'array': 'trajectory_positions',
                                  'coordinate_unit': 'angstrom', 'frames': frames}
    result = Dataset(metadata, arrays)
    infer_bonds(result)
    result.validate()
    return result


def validate_trajectory(data):
    info = data.metadata.get('trajectory')
    if info is None:
        return
    positions = data.arrays.get(info.get('array'))
    frames = info.get('frames', [])
    if (info.get('kind') != 'xyz' or info.get('coordinate_unit') != 'angstrom'
            or positions is None or positions.shape != (len(frames), len(data.arrays['atomic_numbers']), 3)
            or len(frames) < 2 or np.any(data.arrays['atomic_numbers'] < 1)
            or not np.array_equal(positions[0], data.arrays['positions'])):
        raise ValueError('Invalid XYZ trajectory layout or initial geometry')
    previous = 0
    for number, frame in enumerate(frames, 1):
        if (frame.get('frame') != number or not isinstance(frame.get('comment'), str)
                or not re.fullmatch(r'[0-9a-f]{64}', frame.get('sha256', ''))
                or type(frame.get('line_start')) is not int or frame['line_start'] <= previous
                or frame.get('coordinate_line_start') != frame['line_start'] + 2
                or frame.get('coordinate_line_end') != frame.get('line_end')
                or frame['line_end'] - frame['coordinate_line_start'] + 1 != len(data.arrays['atomic_numbers'])):
            raise ValueError('Invalid XYZ frame identity or source line range')
        previous = frame['line_end']
