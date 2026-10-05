"""Operator accept transaction boundary tests; native integration uses Blender separately."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def accept_method(module, class_name):
    """Execute the actual accept body without registering Blender RNA classes."""
    path = ROOT / 'qcblender/blender' / (module + '.py')
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'accept')
    namespace = {'__package__': 'qcblender.blender'}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['accept']


class MultiFieldAccept(unittest.TestCase):
    def setUp(self):
        self.directory = Path('completed-job') / 'dataset'
        self.parent = SimpleNamespace(name='original reference')
        self.fields = [{'vdb': 'first.vdb'}, {'vdb': 'second.vdb'}]
        self.data = SimpleNamespace(metadata={'fields': self.fields})
        self.checked = []
        self.writes = []
        self.operation = SimpleNamespace(
            _inspecting=False, _job=SimpleNamespace(directory=self.directory.parent),
            _reference_snapshot=(), _reference=self.parent, _reference_path=Path('reference'),
            report=lambda *args: None)

    def reject(self, directory, field):
        self.checked.append((directory, field['vdb']))
        if field is self.rejected:
            raise ValueError('native completed-result cache unreadable')

    def atom_view(self, *args):
        self.writes.append('atoms')
        raise AssertionError('Atom creation preceded complete field preflight')

    def field_view(self, *args):
        self.writes.append('field')
        raise AssertionError('Field creation preceded complete field preflight')

    def modules(self):
        return {
            'qcblender.data': SimpleNamespace(load_dataset=lambda directory: self.data),
            'qcblender.blender.views': SimpleNamespace(atom_view=self.atom_view, field_view=self.field_view),
            'qcblender.blender.native_volume': SimpleNamespace(check_field_cache=self.reject),
            'qcblender.blender.trajectory': SimpleNamespace(initialize_trajectory=lambda *args: None),
            'qcblender.association': SimpleNamespace(compare_sources=lambda *args: {}),
            'qcblender.blender.scalars': SimpleNamespace(add_mapping=lambda *args: None),
            'qcblender.blender.static_reference': SimpleNamespace(validate_reference=lambda snapshot: self.parent),
        }

    def test_import_first_unreadable_field_precedes_atom_creation(self):
        self.rejected = self.fields[0]
        accept = accept_method('ui', 'QCBLENDER_OT_import')
        with patch.dict(sys.modules, self.modules()):
            with self.assertRaisesRegex(ValueError, 'native completed-result cache unreadable'):
                accept(self.operation, None, {})
        self.assertEqual(self.checked, [(self.directory, 'first.vdb')])
        self.assertEqual(self.writes, [])

    def test_import_second_unreadable_field_precedes_atom_and_first_field_creation(self):
        self.rejected = self.fields[1]
        accept = accept_method('ui', 'QCBLENDER_OT_import')
        with patch.dict(sys.modules, self.modules()):
            with self.assertRaisesRegex(ValueError, 'native completed-result cache unreadable'):
                accept(self.operation, None, {})
        self.assertEqual(self.checked, [(self.directory, 'first.vdb'), (self.directory, 'second.vdb')])
        self.assertEqual(self.writes, [])

    def test_paired_second_unreadable_field_precedes_first_field_creation(self):
        self.rejected = self.fields[1]
        accept = accept_method('external_fields', 'QCBLENDER_OT_import_paired_field')
        with patch.dict(sys.modules, self.modules()):
            with self.assertRaisesRegex(ValueError, 'native completed-result cache unreadable'):
                accept(self.operation, None, {})
        self.assertEqual(self.checked, [(self.directory, 'first.vdb'), (self.directory, 'second.vdb')])
        self.assertEqual(self.writes, [])


if __name__ == '__main__':
    unittest.main()
