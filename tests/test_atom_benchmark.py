"""Pure boundary checks; actual Geometry Nodes timings require Blender."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from tools.workspace_paths import temporary_tests_root

from tools import benchmark_atom_styles as atoms

ROOT = Path(__file__).resolve().parents[1]
NUMBERS = [6, 1, 1, 1, 1]
POSITIONS = [[0., 0., 0.], [1., 1., 1.], [1., -1., -1.], [-1., 1., -1.], [-1., -1., 1.]]
BONDS = [[0, 1], [0, 2], [0, 3], [0, 4]]


class EngineeringGeometry(unittest.TestCase):
    def test_partial_seed_keeps_source_order_and_only_valid_intracopy_bonds(self):
        original = copy.deepcopy((NUMBERS, POSITIONS, BONDS))
        generated, parameters = atoms.generate_geometry(NUMBERS, POSITIONS, BONDS, 32)
        self.assertEqual(len(generated['positions']), 32)
        self.assertEqual(generated['atomic_numbers'], NUMBERS * 6 + NUMBERS[:2])
        self.assertEqual(generated['positions'][:5], POSITIONS)
        self.assertEqual(len(generated['bonds']), 25)
        self.assertEqual(generated['bonds'][-1], [30, 31])
        for a, b in generated['bonds']:
            self.assertEqual(a // 5, b // 5)
            delta = [generated['positions'][a][i] - generated['positions'][b][i] for i in range(3)]
            self.assertEqual(sum(value * value for value in delta), 3.)
        self.assertEqual((NUMBERS, POSITIONS, BONDS), original)
        self.assertEqual(parameters['retained_atoms_in_last_copy'], 2)
        self.assertIn('not a new', parameters['scientific_scope'])

    def test_generator_is_reproducible_and_distinct_copies_do_not_overlap(self):
        first = atoms.generate_geometry(NUMBERS, POSITIONS, BONDS, 128)
        second = atoms.generate_geometry(NUMBERS, POSITIONS, BONDS, 128)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(len({tuple(point) for point in first[0]['positions']}), 128)
        self.assertEqual(first[0]['bonds'][4], [5, 6])

    def test_changed_seed_elements_or_bonds_fail_before_generating_load(self):
        with self.assertRaisesRegex(ValueError, 'five-atom CH4'):
            atoms.generate_geometry([8, 1, 1, 1, 1], POSITIONS, BONDS, 32)
        with self.assertRaisesRegex(ValueError, 'four C-H bonds'):
            atoms.generate_geometry(NUMBERS, POSITIONS, [[0, 1]] * 4, 32)
        with self.assertRaisesRegex(ValueError, 'finite'):
            atoms.generate_geometry(NUMBERS, [[float('nan'), 0, 0]] + POSITIONS[1:], BONDS, 32)


class BenchmarkBoundaries(unittest.TestCase):
    def arguments(self, *extra):
        return atoms.parser().parse_args(['--output', 'outputs/new-run', '--profile-root', 'outputs/profile', *extra])

    def test_default_matrix_is_bounded_and_warmups_are_counted(self):
        args = self.arguments()
        self.assertEqual(args.atoms, [32, 128, 512])
        self.assertEqual(args.qualities, [1, 3])
        self.assertEqual(args.repeats, 3)
        self.assertEqual(args.warmups, 1)
        budget = atoms.validate_budget(args)
        self.assertEqual(budget['cases'], 18)
        self.assertEqual(budget['trials_including_warmups'], 144)

    def test_excessive_geometry_or_trial_requests_require_explicit_budget(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            atoms.validate_budget(self.arguments('--qualities', '6'))
        with self.assertRaisesRegex(ValueError, 'budget'):
            atoms.validate_budget(self.arguments('--repeats', '1000'))
        accepted = atoms.validate_budget(self.arguments('--atoms', '5', '--qualities', '6', '--styles', 'bonds',
                                                      '--repeats', '1', '--warmups', '0'))
        self.assertEqual(accepted['cases'], 1)

    def test_negative_warmups_and_small_atom_counts_fail(self):
        with self.assertRaisesRegex(ValueError, 'Warmups'):
            atoms.validate_budget(self.arguments('--warmups', '-1'))
        with self.assertRaisesRegex(ValueError, 'Atom counts'):
            atoms.validate_budget(self.arguments('--atoms', '2'))

    def test_styles_and_sizes_cannot_duplicate_or_accept_unknown_values(self):
        for value in ('ball-stick,ball-stick', 'ball-stick,unknown', ''):
            with self.assertRaises(atoms.argparse.ArgumentTypeError):
                atoms.styles(value)
        with self.assertRaises(atoms.argparse.ArgumentTypeError):
            atoms.bench.integers('32,32')

    def test_existing_evidence_directory_and_files_are_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='atom-benchmark-tests-', dir=temporary_tests_root(ROOT)) as temporary:
            directory = Path(temporary)
            previous = directory / 'report.json'
            previous.write_bytes(b'preserved evidence')
            args = self.arguments()
            args.output = directory
            with self.assertRaises(FileExistsError):
                atoms.bench.setup(args, 'atom-styles')
            self.assertEqual(previous.read_bytes(), b'preserved evidence')

    def test_dataset_identity_detects_changed_bytes_and_extra_files(self):
        with tempfile.TemporaryDirectory(prefix='atom-benchmark-tests-', dir=temporary_tests_root(ROOT)) as temporary:
            directory = Path(temporary)
            (directory / 'manifest.json').write_bytes(b'original')
            first = atoms.file_identity(directory)
            (directory / 'manifest.json').write_bytes(b'changed')
            second = atoms.file_identity(directory)
            self.assertNotEqual(first, second)
            (directory / 'extra.npy').write_bytes(b'added')
            self.assertNotEqual(second, atoms.file_identity(directory))


class InstalledPackageIdentity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='atom-manifest-tests-', dir=temporary_tests_root(ROOT))
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'source'
        self.installed = Path(self.temporary.name) / 'installed'
        (self.root / 'qcblender').mkdir(parents=True)
        (self.root / 'modules').mkdir()
        (self.installed / 'wheels').mkdir(parents=True)
        self.wheels = [('test_dependency-1-py3-none-any.whl', b'locked dependency bytes'),
                       ('qc_gbasis-1-py3-none-any.whl', b'locked backend bytes')]
        records = []
        for name, raw in self.wheels:
            (self.installed / 'wheels' / name).write_bytes(raw)
            records.append({'name': name.split('-')[0], 'version': '1', 'filename': name,
                            'sha256': hashlib.sha256(raw).hexdigest()})
        self.source_manifest = (ROOT / 'qcblender/blender_manifest.toml').read_text(encoding='utf-8')
        (self.root / 'qcblender/blender_manifest.toml').write_text(self.source_manifest, encoding='utf-8')
        self.built_manifest = self.source_manifest.replace('wheels = []',
            'wheels = ' + json.dumps(['./wheels/' + name for name, _ in self.wheels]))
        (self.installed / 'blender_manifest.toml').write_text(self.built_manifest, encoding='utf-8')
        for source, destination, value in (
            ('dependencies.lock.json', 'dependencies.lock.json', {'packages': records[:1], 'host_provided': {}}),
            ('science-sources.lock.json', 'science-sources.lock.json', {'locked_science_source': 'fixture'}),
            ('modules/backend-wheel.json', 'backend-wheel.json', records[1]),
        ):
            path = self.root / source
            path.write_text(json.dumps(value), encoding='utf-8')
            shutil.copyfile(path, self.installed / destination)

    def test_build_expanded_wheel_manifest_is_accepted(self):
        identity = atoms.verify_installed_manifest(self.installed, self.root)
        self.assertEqual(identity['installed_manifest_sha256'], atoms.bench.sha256(self.installed / 'blender_manifest.toml'))

    def test_unrelated_manifest_change_is_rejected(self):
        path = self.installed / 'blender_manifest.toml'
        path.write_text(self.built_manifest.replace('version = "0.1.0"', 'version = "0.1.1"'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'manifest'):
            atoms.verify_installed_manifest(self.installed, self.root)

    def test_missing_extra_duplicate_and_reordered_manifest_wheels_are_rejected(self):
        expected = ['./wheels/' + name for name, _ in self.wheels]
        for wheel_list in (expected[:1], expected + ['./wheels/extra.whl'], expected + expected[:1], expected[::-1]):
            with self.subTest(wheels=wheel_list):
                text = self.source_manifest.replace('wheels = []', 'wheels = ' + json.dumps(wheel_list))
                (self.installed / 'blender_manifest.toml').write_text(text, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'manifest'):
                    atoms.verify_installed_manifest(self.installed, self.root)

    def test_changed_lock_and_backend_records_are_rejected(self):
        for name in ('dependencies.lock.json', 'science-sources.lock.json', 'backend-wheel.json'):
            path = self.installed / name
            original = path.read_bytes()
            with self.subTest(record=name):
                path.write_bytes(original + b' ')
                with self.assertRaisesRegex(ValueError, 'lock|backend'):
                    atoms.verify_installed_manifest(self.installed, self.root)
                path.write_bytes(original)

    def test_modified_wheel_bytes_and_unexpected_installed_wheel_are_rejected(self):
        name, original = self.wheels[0]
        path = self.installed / 'wheels' / name
        path.write_bytes(original + b' changed')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            atoms.verify_installed_manifest(self.installed, self.root)
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'membership'):
            atoms.verify_installed_manifest(self.installed, self.root)
        path.write_bytes(original)
        (self.installed / 'wheels/extra.whl').write_bytes(b'unexpected')
        with self.assertRaisesRegex(ValueError, 'membership'):
            atoms.verify_installed_manifest(self.installed, self.root)


if __name__ == '__main__':
    unittest.main()
