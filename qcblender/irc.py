"""User ordered Gaussian FCHK reaction paths and per-step external Mayer results."""
import csv
from pathlib import Path

import numpy as np

from .data import Dataset
from .external_results import mayer_orders
from .readers import read_fchk, source_record


def ordered_files(manifest, value_column):
    manifest = Path(manifest).resolve(strict=True)
    with manifest.open('r', encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or set(reader.fieldnames) != {'step', value_column}:
            raise ValueError(f'Manifest header must be step,{value_column}')
        records = list(reader)
    if not records:
        raise ValueError('Step manifest has no rows')
    if len(records) > 10000:
        raise ValueError('Step manifest exceeds 10000 steps')
    files = []
    for index, record in enumerate(records, 1):
        try:
            valid = int(record['step']) == index and bool(record[value_column].strip())
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError('Step manifest has an invalid step or file path') from error
        if not valid:
            raise ValueError('Step numbers must be explicit, unique and contiguous from 1')
        candidate = Path(record[value_column])
        path = (candidate if candidate.is_absolute() else manifest.parent / candidate).resolve(strict=True)
        files.append(path)
    if len(set(files)) != len(files):
        raise ValueError('Step manifest repeats a file path')
    return files


def import_irc(manifest):
    files = ordered_files(manifest, 'fchk')
    steps = []
    for path in files:
        if path.suffix.lower() not in ('.fchk', '.fch'):
            raise ValueError('IRC step source must be FCHK/FCH')
        if path.stat().st_size > 512 * 1024**2:
            raise MemoryError('IRC FCHK step exceeds the 512 MiB import limit')
        steps.append(read_fchk(path))
    reference = steps[0]
    identity = ('method', 'basis_name', 'charge', 'spin_polarization')
    energies, sources = [], []
    for number, data in enumerate(steps, 1):
        if not np.array_equal(data.arrays['atomic_numbers'], reference.arrays['atomic_numbers']):
            raise ValueError(f'IRC step {number} changes atom identities or ordering')
        if any(data.metadata.get(key) != reference.metadata.get(key) for key in identity):
            raise ValueError(f'IRC step {number} changes method, basis, charge or spin')
        records = [record for record in data.metadata['energies'] if record['kind'] == 'electronic_total']
        if len(records) != 1 or not np.isfinite(records[0]['value_hartree']):
            raise ValueError(f'IRC step {number} lacks one finite total energy')
        energies.append(records[0]['value_hartree'])
        sources.append(data.metadata['source'])
    if len({record['sha256'] for record in sources}) != len(sources):
        raise ValueError('IRC sequence repeats identical FCHK content')
    arrays = {'atomic_numbers': np.array(reference.arrays['atomic_numbers'], copy=True),
              'positions': np.array(reference.arrays['positions'], copy=True),
              'irc_positions': np.stack([data.arrays['positions'] for data in steps]),
              'irc_energies': np.asarray(energies, dtype=float)}
    if 'bonds' in reference.arrays:
        arrays['bonds'] = np.array(reference.arrays['bonds'], copy=True)
    metadata = {'source': source_record(Path(manifest), 'irc-step-manifest', 'qcblender.irc 0.1'),
                'coordinate_unit': 'angstrom', 'title': 'IRC path', 'fields': [], 'charges': [],
                'energies': [], 'calculation_status': 'external_path', 'diagnostics': [],
                'analysis': {'kind': 'IRC', 'steps': sources,
                    'step_order': list(range(1, len(steps) + 1)), 'energy_unit': 'hartree',
                    'method': reference.metadata.get('method'), 'basis_name': reference.metadata.get('basis_name'),
                    'coordinate_unit': 'angstrom'}}
    result = Dataset(metadata, arrays)
    result.validate()
    return result


def import_irc_mayer(path_data, manifest):
    if path_data.metadata.get('analysis', {}).get('kind') != 'IRC':
        raise ValueError('Select an imported IRC path')
    files = ordered_files(manifest, 'mayer_output')
    count = len(path_data.arrays['irc_energies'])
    if len(files) != count:
        raise ValueError('Mayer step count differs from the IRC path')
    if any(path.stat().st_size > 64 * 1024**2 for path in files):
        raise MemoryError('Mayer output exceeds the 64 MiB import limit')
    all_rows = [mayer_orders(path, len(path_data.arrays['atomic_numbers'])) for path in files]
    pairs = sorted({tuple(row['atoms']) for row in all_rows[0]})
    if any(sorted({tuple(row['atoms']) for row in rows}) != pairs for rows in all_rows):
        raise ValueError('Mayer atom pairs are missing or differ across IRC steps')
    values = np.array([[next(row['order'] for row in rows if tuple(row['atoms']) == pair)
                        for pair in pairs] for rows in all_rows], dtype=float)
    arrays = {'atomic_numbers': np.array(path_data.arrays['atomic_numbers'], copy=True),
              'positions': np.array(path_data.arrays['positions'], copy=True),
              'mayer_pairs': np.array(pairs, dtype=np.int32), 'mayer_orders': values}
    metadata = {'source': source_record(Path(manifest), 'irc-mayer-manifest', 'qcblender.irc 0.1'),
                'coordinate_unit': 'angstrom', 'title': 'IRC Mayer bond orders',
                'fields': [], 'charges': [], 'energies': [],
                'analysis': {'kind': 'IRC-Mayer', 'method': 'Mayer', 'unit': 'dimensionless',
                             'path_source': path_data.metadata['source']['sha256'],
                             'step_sources': [source_record(path, 'multiwfn-output',
                                                            'qcblender.external_results 0.1') for path in files],
                             'association': 'user_assigned_step_and_atom_number'}}
    result = Dataset(metadata, arrays)
    result.validate()
    return result
