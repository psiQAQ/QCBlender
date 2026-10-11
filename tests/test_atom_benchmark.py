"""Pure boundary checks; actual Geometry Nodes timings require Blender."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

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
        (ROOT / 'outputs').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='atom-benchmark-tests-', dir=ROOT / 'outputs') as temporary:
            directory = Path(temporary)
            previous = directory / 'report.json'
            previous.write_bytes(b'preserved evidence')
            args = self.arguments()
            args.output = directory
            with self.assertRaises(FileExistsError):
                atoms.bench.setup(args, 'atom-styles')
            self.assertEqual(previous.read_bytes(), b'preserved evidence')

    def test_dataset_identity_detects_changed_bytes_and_extra_files(self):
        (ROOT / 'outputs').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='atom-benchmark-tests-', dir=ROOT / 'outputs') as temporary:
            directory = Path(temporary)
            (directory / 'manifest.json').write_bytes(b'original')
            first = atoms.file_identity(directory)
            (directory / 'manifest.json').write_bytes(b'changed')
            second = atoms.file_identity(directory)
            self.assertNotEqual(first, second)
            (directory / 'extra.npy').write_bytes(b'added')
            self.assertNotEqual(second, atoms.file_identity(directory))


if __name__ == '__main__':
    unittest.main()
