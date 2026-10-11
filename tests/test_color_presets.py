"""Check frozen upstream colors without importing Blender or matplotlib."""
import ast
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import unittest

from qcblender.color_presets import PRESETS, get_preset


class ColorPresetData(unittest.TestCase):
    def test_complete_upstream_tables(self):
        # SHA-256 of compact JSON for the literal items tuples in the pinned
        # MolecularNodes file. These cover every position and RGBA component.
        expected = {
            'VIRIDIS': '8424e80d2cb5ec963681a1b9df10ef5f8b2baf25f4f35cb479bba13c03c45428',
            'CIVIDIS': '10c5b445bcd87270b272a9fb3a547b2d60bdf74ad82c66b6fc0cac86fc53025b',
        }
        for identifier, digest in expected.items():
            with self.subTest(identifier=identifier):
                preset = get_preset(identifier)
                self.assertEqual(len(preset.elements), 13)
                serialized = json.dumps(preset.elements, separators=(',', ':')).encode()
                self.assertEqual(hashlib.sha256(serialized).hexdigest(), digest)

    def test_default_matches_existing_material_colors(self):
        source = Path(__file__).resolve().parents[1] / 'qcblender/blender/scalars.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'scalar_material')
        colors = [ast.literal_eval(node.value) for node in function.body
                  if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Attribute)
                  and node.targets[0].attr == 'color']
        self.assertEqual(colors, [PRESETS['QC_DEFAULT'].elements[i][1] for i in (0, 2, 1)])

    def test_modes_and_positions(self):
        self.assertEqual(set(PRESETS), {'QC_DEFAULT', 'VIRIDIS', 'CIVIDIS'})
        for key, preset in PRESETS.items():
            with self.subTest(identifier=key):
                self.assertEqual(preset.color_mode, 'RGB')
                self.assertEqual(preset.interpolation, 'B_SPLINE' if key == 'VIRIDIS' else 'LINEAR')
                positions = [position for position, _ in preset.elements]
                self.assertEqual((positions[0], positions[-1]), (0., 1.))
                self.assertTrue(all(a < b for a, b in zip(positions, positions[1:])))
                self.assertTrue(all(len(color) == 4 and all(0 <= channel <= 1 for channel in color)
                                    for _, color in preset.elements))

    def test_tables_are_immutable(self):
        with self.assertRaises(TypeError):
            PRESETS['VIRIDIS'] = PRESETS['QC_DEFAULT']
        with self.assertRaises(FrozenInstanceError):
            PRESETS['VIRIDIS'].interpolation = 'LINEAR'
        with self.assertRaises(TypeError):
            PRESETS['VIRIDIS'].elements[0][1][0] = 1.

    def test_unknown_identifier_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError, 'Unknown color preset: CUSTOM'):
            get_preset('CUSTOM')


if __name__ == '__main__':
    unittest.main()
