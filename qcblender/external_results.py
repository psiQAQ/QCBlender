"""Strict readers for externally generated analysis tables and PDB point records."""
import math
from pathlib import Path
import re


def pdb_rows(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if line[:6].strip() not in ('ATOM', 'HETATM'):
            continue
        if len(line) < 54:
            raise ValueError(f'PDB line {number} is truncated')
        try:
            serial = int(line[6:11])
            position = [float(line[start:start+8]) for start in (30, 38, 46)]
            residue = int(line[22:26]) if line[22:26].strip() else None
        except ValueError as error:
            raise ValueError(f'PDB line {number} has invalid serial, residue or coordinates') from error
        if not all(math.isfinite(value) for value in position):
            raise ValueError(f'PDB line {number} has nonfinite coordinates')
        rows.append({'serial': serial, 'name': line[12:16].strip(), 'residue': residue,
                     'position_angstrom': position, 'line': number, 'raw': line})
    if not rows:
        raise ValueError('PDB contains no ATOM/HETATM records')
    return rows


def esp_extrema(path):
    result = []
    for row in pdb_rows(path):
        if len(row['raw']) < 66:
            raise ValueError(f"ESP extrema PDB line {row['line']} lacks the value column")
        label = row['name'].upper()
        if label not in ('C', 'O'):
            raise ValueError(f"ESP extrema PDB line {row['line']} has unknown kind {label}")
        try:
            value = float(row['raw'][60:66])
        except ValueError as error:
            raise ValueError(f"ESP extrema PDB line {row['line']} has invalid value") from error
        if not math.isfinite(value):
            raise ValueError('ESP extrema value is nonfinite')
        result.append({'serial': row['serial'], 'kind': 'maximum' if label == 'C' else 'minimum',
                       'position_angstrom': row['position_angstrom'], 'value': value,
                       'source_line': row['line']})
    if len({(item['kind'], item['serial']) for item in result}) != len(result):
        raise ValueError('ESP extrema serial numbers are repeated within the same kind')
    return result


def esp_extrema_unit(path):
    """Return the ESP B-factor declaration, if the PDB contains one."""
    declaration = None
    for number, line in enumerate(Path(path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if line[:6].strip().upper() != 'REMARK' or 'unit of b-factor field' not in line.lower():
            continue
        match = re.fullmatch(r'REMARK\s+Unit of B-factor field \(i\.e\. ESP\) is\s+(\S+)\s*', line, re.I)
        if not match or match[1].lower() not in ('kcal/mol', 'ev', 'a.u.'):
            raise ValueError(f'ESP extrema PDB line {number} has an unsupported or non-ESP B-factor unit declaration')
        unit = {'kcal/mol': 'kcal/mol', 'ev': 'eV', 'a.u.': 'a.u.'}[match[1].lower()]
        if declaration and declaration['unit'] != unit:
            raise ValueError(f'ESP extrema PDB line {number} conflicts with B-factor unit on line {declaration["source_line"]}')
        declaration = {'unit': unit, 'source_line': number, 'raw': line}
    return declaration


def esp_area(path):
    lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    header = next((i for i, line in enumerate(lines) if 'Center' in line and 'Area' in line), None)
    if header is None:
        raise ValueError('ESP area table lacks Center/Area header')
    names = lines[header].split()
    if names not in (['Begin', 'End', 'Center', 'Area', '%'],
                     ['Center', 'Area', '%'], ['Center', 'Area', 'Percentage']):
        raise ValueError('ESP area table header must identify Begin/End/Center/Area/% or Center/Area/%')
    columns = len(names)
    records = []
    for number, line in enumerate(lines[header + 1:], header + 2):
        clean = line.strip()
        if not clean and records:
            break
        if not clean or clean.startswith(('---', '===', 'Sum')) or 'Area unit' in clean:
            continue
        values = clean.split()
        if len(values) != columns:
            if records and not re.match(r'^[+-]?\d', clean):
                break
            raise ValueError(f'ESP area line {number} has {len(values)} columns; expected {columns}')
        try:
            parsed = [float(value.replace('D', 'E')) for value in values]
            center, area, percent = parsed[-3:]
        except ValueError as error:
            raise ValueError(f'ESP area line {number} has invalid values') from error
        if not all(math.isfinite(value) for value in parsed) or area < 0 or not 0 <= percent <= 100:
            raise ValueError(f'ESP area line {number} has invalid area/percentage')
        begin, end = parsed[:2] if columns == 5 else (None, None)
        if columns == 5 and not begin < center < end:
            raise ValueError(f'ESP area line {number} has invalid interval bounds')
        records.append({'begin': begin, 'end': end, 'center': center, 'area': area,
                        'percentage': percent, 'source_line': number})
    if not records:
        raise ValueError('ESP area table has no data rows')
    return records


def aim_points(path):
    result = []
    for row in pdb_rows(path):
        if row['name'] not in ('C', 'N', 'O', 'F'):
            raise ValueError(f"AIM CP line {row['line']} has unknown type {row['name']}")
        result.append({'serial': row['serial'], 'type': row['name'],
                       'position_angstrom': row['position_angstrom'], 'source_line': row['line']})
    if len({item['serial'] for item in result}) != len(result):
        raise ValueError('AIM critical point serial numbers are repeated')
    return result


def aim_paths(path):
    paths = {}
    for row in pdb_rows(path):
        if row['residue'] is None:
            raise ValueError(f"AIM path line {row['line']} lacks a path residue number")
        paths.setdefault(row['residue'], []).append(row['position_angstrom'])
    if any(len(points) < 2 for points in paths.values()):
        raise ValueError('Each AIM path needs at least two points')
    return [{'residue': residue, 'points_angstrom': points} for residue, points in paths.items()]


def aim_properties(path, known_serials):
    result, current = {}, None
    for number, line in enumerate(Path(path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        match = re.search(r'CP\s+(\d+),\s*Type\s*\(([^)]+)\)', line) if line.lstrip().startswith('-') else None
        modern = re.match(r'\s*Critical point\s+(\d+)\s*:', line)
        if match or modern:
            current = int((match or modern)[1])
            if current not in known_serials or current in result:
                raise ValueError(f'AIM property line {number} has unknown or repeated CP {current}')
            result[current] = {'CP_type': '(' + match[2] + ')' if match else 'unknown'}
        elif current is not None and ':' in line:
            key, value = (part.strip() for part in line.split(':', 1))
            if key:
                try:
                    result[current][key] = float(value)
                except ValueError:
                    result[current][key] = value
    if not result:
        raise ValueError('AIM property file contains no CP records')
    return result


def mayer_orders(path, atom_count):
    pattern = re.compile(r'#\s*\d+:\s*(\d+)\([^)]*\)\s*(\d+)\([^)]*\)\s*([+-]?\d+(?:\.\d+)?)')
    rows, active = [], False
    for number, line in enumerate(Path(path).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if 'Bond orders with absolute value' in line:
            active = True
            continue
        if active and 'Total valences and free valences' in line:
            break
        match = pattern.search(line) if active else None
        if match:
            first, second, value = int(match[1]), int(match[2]), float(match[3])
            if not 1 <= first <= atom_count or not 1 <= second <= atom_count or first == second or not math.isfinite(value):
                raise ValueError(f'Mayer line {number} has invalid atom pair or value')
            rows.append({'atoms': sorted((first, second)), 'order': value, 'source_line': number})
    if not rows or len({tuple(row['atoms']) for row in rows}) != len(rows):
        raise ValueError('Mayer bond order table missing or repeats an atom pair')
    return rows


def ets_nocv_pairs(path, energy_unit):
    if energy_unit not in ('kcal/mol', 'hartree'):
        raise ValueError('Explicit ETS-NOCV energy unit must be kcal/mol or hartree')
    lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    pattern = re.compile(r'^\s*(\d+)\s+(' + r'[+-]?\d+\.\d+' + r')\s+(\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+(\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s*$')
    rows, spin, in_table = [], 'Total', False
    declared_units, not_evaluated, placeholder = [], False, False
    for number, line in enumerate(lines, 1):
        lower = line.lower()
        if ('energies of nocv orbitals have not been evaluated' in lower
                or 'nocv orbital energies are not calculated' in lower):
            not_evaluated = True
        unit_note = re.search(r'\b(?:all\s+)?energies?\s+(?:are\s+given\s+in|in|unit\s*(?:is|:))\s+(\S+)', line, re.I)
        if unit_note:
            declared_units.append(unit_note[1].rstrip('.,;').lower())
        if 'Alpha NOCV orbitals' in line:
            spin = 'Alpha'
        elif 'Beta NOCV orbitals' in line:
            spin = 'Beta'
        if re.search(r'Pair\s+Energy\s*\|\s*Orbital\s+Eigenvalue\s+Energy', line):
            for declared_unit in declared_units:
                if declared_unit not in ('kcal/mol', 'hartree'):
                    raise ValueError(f'ETS-NOCV table line {number} declares unsupported energy unit {declared_unit}')
                if declared_unit != energy_unit:
                    raise ValueError(f'ETS-NOCV table line {number} declares {declared_unit}, not {energy_unit}')
            in_table = not not_evaluated
            placeholder |= not_evaluated
            declared_units, not_evaluated = [], False
            continue
        match = pattern.match(line) if in_table else None
        if match:
            values = [float(value) for value in match.groups()]
            rows.append({'pair': int(values[0]), 'pair_energy': values[1],
                         'positive_orbital': int(values[2]), 'positive_eigenvalue': values[3],
                         'positive_energy': values[4], 'negative_orbital': int(values[5]),
                         'negative_eigenvalue': values[6], 'negative_energy': values[7],
                         'spin': spin, 'energy_unit': energy_unit, 'source_line': number})
        elif in_table and line.strip() and not set(line.strip()) <= set('-=+'):
            if re.match(r'^\s*\d+\s+', line):
                raise ValueError(f'ETS-NOCV pair line {number} is malformed or truncated')
            in_table = False
    unique = {}
    for row in rows:
        key = row['spin'], row['pair']
        if key in unique:
            first = unique[key]
            conflicts = [name for name in row
                         if name != 'source_line' and row[name] != first[name]]
            if conflicts:
                raise ValueError(
                    f'Conflicting ETS-NOCV pair {key}: {", ".join(conflicts)} '
                    f'at source lines {first["source_line"]} and {row["source_line"]}')
        else:
            unique[key] = row
    if not unique:
        if placeholder:
            raise ValueError('ETS-NOCV orbital energies have not been evaluated; pair energies are placeholders')
        raise ValueError('ETS-NOCV table has no pair rows')
    return list(unique.values())
