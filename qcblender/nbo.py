"""Selected Gaussian job NBO tables, kept separate from canonical orbitals."""
import re
from pathlib import Path

from .association import compare_sources
from .data import load_dataset
from .gaussian_log import split_jobs
from .gaussian_log import read_log

ORBITAL = re.compile(r'\s*(\d+)\.\s*(BD\*?|CR|LP\*?|RY\*?|LV|3C\*?)\s*\(\s*(\d+)\)\s*([A-Z][a-z]?)\s+(\d+)(?:\s*-\s*([A-Z][a-z]?)\s+(\d+))?')
FLOAT = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'


def orbital_prefix(text):
    match = ORBITAL.match(text)
    if not match:
        raise ValueError('Malformed NBO orbital record: ' + text[:100].strip())
    atoms = [{'symbol': match[4], 'number': int(match[5])}]
    if match[7]:
        atoms.append({'symbol': match[6], 'number': int(match[7])})
    return {'number': int(match[1]), 'type': match[2], 'subindex': int(match[3]),
            'atoms': atoms}, match.end()


def parse_nbo(path, job_index, block_index):
    path = Path(path)
    if path.stat().st_size > 512 * 1024**2:
        raise MemoryError('Gaussian Log exceeds import limit')
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    spans = split_jobs(lines)
    if not 0 <= job_index < len(spans):
        raise ValueError(f'Choose a Gaussian job from 1 to {len(spans)}')
    start, end = spans[job_index]
    section = lines[start:end]
    summaries = [i for i, line in enumerate(section) if 'Natural Bond Orbitals (Summary)' in line]
    if not 0 <= block_index < len(summaries):
        raise ValueError(f'Choose an NBO block from 1 to {len(summaries)} in this job')
    summary = summaries[block_index]
    next_summary = summaries[block_index + 1] if block_index + 1 < len(summaries) else len(section)
    orbitals = []
    complete = False
    for index in range(summary + 1, next_summary):
        line = section[index]
        if 'Total unit' in line:
            complete = True
            break
        if not ORBITAL.match(line):
            continue
        record, offset = orbital_prefix(line)
        values = re.match(r'\s*(' + FLOAT + r')\s+(' + FLOAT + r')\b', line[offset:])
        if values is None:
            raise ValueError(f'NBO summary line {start + index + 1} lacks occupancy/energy')
        record.update(occupancy=float(values[1].replace('D', 'E')),
                      energy_hartree=float(values[2].replace('D', 'E')),
                      source_line=start + index + 1, raw_line=line.rstrip())
        orbitals.append(record)
    if not complete or not orbitals or len({o['number'] for o in orbitals}) != len(orbitals):
        raise ValueError('NBO summary is missing or contains duplicate orbital numbers')
    previous_summary = summaries[block_index - 1] if block_index else 0
    e2_headers = [i for i in range(previous_summary, summary)
                  if 'Second Order Perturbation Theory Analysis' in section[i]]
    interactions = []
    if e2_headers:
        for index in range(e2_headers[-1] + 1, summary):
            line = section[index]
            if '/' not in line or not ORBITAL.match(line):
                continue
            donor_text, acceptor_text = line.split('/', 1)
            donor, _ = orbital_prefix(donor_text)
            acceptor, offset = orbital_prefix(acceptor_text)
            values = re.match(r'\s*(' + FLOAT + r')\s+(' + FLOAT + r')\s+(' + FLOAT + r')\s*$', acceptor_text[offset:])
            if values is None:
                raise ValueError(f'NBO E(2) line {start + index + 1} is incomplete')
            interactions.append({'donor': donor['number'], 'acceptor': acceptor['number'],
                                 'e2_kcal_mol': float(values[1]), 'delta_e_hartree': float(values[2]),
                                 'fij_hartree': float(values[3]), 'source_line': start + index + 1,
                                 'raw_line': line.rstrip()})
    known = {o['number'] for o in orbitals}
    if any(item['donor'] not in known or item['acceptor'] not in known for item in interactions):
        raise ValueError('E(2) references an orbital absent from the selected NBO summary')
    return {'job_number': job_index + 1, 'block_number': block_index + 1,
            'summary_line': start + summary + 1, 'orbitals': orbitals, 'interactions': interactions,
            'orbital_energy_unit': 'hartree', 'interaction_energy_unit': 'kcal/mol',
            'canonical_mo_mapping': 'none'}


def associated_nbo(path, job_index, block_index, reference_directory):
    import periodictable

    data = read_log(path, job_index)
    if any('Multiple geometries' in message for message in data.metadata['diagnostics']):
        raise ValueError('Selected Gaussian job has multiple geometries; NBO records cannot be assigned to its final geometry')
    result = parse_nbo(path, job_index, block_index)
    atom_count = len(data.arrays['atomic_numbers'])
    if any(atom['number'] < 1 or atom['number'] > atom_count
           for orbital in result['orbitals'] for atom in orbital['atoms']):
        raise ValueError('NBO atom number is outside the selected calculation')
    if any(atom['symbol'] != periodictable.elements[int(data.arrays['atomic_numbers'][atom['number'] - 1])].symbol
           for orbital in result['orbitals'] for atom in orbital['atoms']):
        raise ValueError('NBO atom symbol disagrees with the selected calculation')
    result['reference'] = compare_sources(load_dataset(reference_directory), data)
    result['kind'] = 'NBO'
    result['source'] = data.metadata['source']
    data.metadata['analysis'] = result
    return data
