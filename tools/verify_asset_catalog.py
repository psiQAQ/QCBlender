"""Pure-Python checks for the shipped node catalog contract."""

from pathlib import Path
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qcblender.asset_catalog import ASSETS, CATEGORIES, catalog_id, catalog_text


assert len(ASSETS) == 9
assert len(CATEGORIES) == len(set(CATEGORIES))
assert len({catalog_id(path) for path in CATEGORIES}) == len(CATEGORIES)
assert all(UUID(catalog_id(path)).version == 5 for path in CATEGORIES)
assert all(category in CATEGORIES and factory.endswith('_group')
           for category, factory in ASSETS.values())
assert set(ASSETS) == {
    'qc.sample.v1', 'qc.atom_selection.v1', 'qc.atom_style.v1',
    'qc.surface_style.v1', 'qc.isosurface.v3', 'qc.volume_fog.v1',
    'qc.color_scalar.v2', 'qc.slice.v1', 'qc.clip.v1',
}
lines = catalog_text().splitlines()
assert lines[1] == 'VERSION 1'
assert len(lines[3:]) == len(CATEGORIES)
assert all(line.split(':')[0] == catalog_id(path)
           for line, path in zip(lines[3:], CATEGORIES))
print('ASSET_CATALOG_PASSED')
