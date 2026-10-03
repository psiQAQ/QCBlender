"""Pure boundary tests; real Blender runs remain separate integration evidence."""
import argparse
import json
from pathlib import Path
import tempfile
import unittest

from tools import benchmark_fields as benchmark


class PerformanceBoundaries(unittest.TestCase):
    def setUp(self):
        (benchmark.ROOT / 'outputs').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=benchmark.ROOT / 'outputs', prefix='benchmark-test-')
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def profile(self):
        paths = {}
        for key in ('config', 'extensions', 'temp'):
            target = self.root / key
            target.mkdir()
            paths[key] = target
        benchmark.validate_profile(self.root, paths)

    def test_external_profile_path_rejected_without_ownership_marker(self):
        with self.assertRaisesRegex(ValueError, 'strictly inside'):
            benchmark.validate_profile(self.root, {'config': self.root.parent})
        self.assertFalse((self.root / '.qc-performance-owner').exists())

    def test_missing_profile_path_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing'):
            benchmark.validate_profile(self.root, {'TEMP': None})

    def test_profile_cannot_be_claimed_twice(self):
        self.profile()
        with self.assertRaises(FileExistsError):
            benchmark.validate_profile(self.root, {'config': self.root / 'config'})

    def test_eviction_deletes_only_claimed_index_and_preserves_cached_arrays(self):
        self.profile()
        cache = self.root / 'extensions' / 'jobs' / 'cache'
        cache.mkdir(parents=True)
        index = cache / 'owned.json'
        index.write_bytes(b'{"dataset":"arrays"}')
        arrays = cache / 'arrays'
        arrays.mkdir()
        scientific = arrays / 'field.npy'
        scientific.write_bytes(b'scientific data')
        other = cache / 'other.json'
        other.write_bytes(b'{}')
        benchmark.evict_owned_index(index, benchmark.sha256(index), cache, self.root)
        self.assertFalse(index.exists())
        self.assertEqual(scientific.read_bytes(), b'scientific data')
        self.assertTrue(other.exists())

    def test_changed_index_and_external_index_rejected(self):
        self.profile()
        cache = self.root / 'extensions' / 'cache'
        cache.mkdir()
        index = cache / 'owned.json'
        index.write_bytes(b'original')
        digest = benchmark.sha256(index)
        index.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'changed'):
            benchmark.evict_owned_index(index, digest, cache, self.root)
        outside = self.root / 'outside.json'
        outside.write_bytes(b'outside')
        with self.assertRaisesRegex(ValueError, 'owned index'):
            benchmark.evict_owned_index(outside, benchmark.sha256(outside), cache, self.root)
        self.assertTrue(outside.exists())

    def test_output_cannot_overwrite_existing_evidence(self):
        args = argparse.Namespace(output=self.root, warmups=1)
        with self.assertRaises(FileExistsError):
            benchmark.setup(args, 'fields')

    def test_summary_uses_raw_times_and_memory_excludes_process_identity(self):
        actual = benchmark.summary([{'seconds': value, 'peak_mib': 2 * value, 'process_id': 500 + value}
                                    for value in (3, 1, 9, 4, 2)])
        self.assertEqual(actual['seconds'], {'median': 3, 'min': 1, 'max': 9})
        self.assertEqual(actual['peak_mib']['median'], 6)
        self.assertNotIn('process_id', actual)

    def test_incompatible_environment_not_compared_and_speed_change_does_not_fail(self):
        report = {'schema': 1, 'benchmark': 'fields', 'environment': {'blender': '5.1.1'},
                  'parameters': {'sizes': [64]}, 'source': {'sha256': 'source'}, 'status': 'Passed',
                  'summary': {'64': {'seconds': {'median': 2}}}}
        baseline = self.root / 'baseline.json'
        baseline.write_text(json.dumps(report), encoding='utf-8')
        report['summary']['64']['seconds']['median'] = 6
        result = benchmark.compare(report, baseline)
        self.assertEqual(result['status'], 'Compared')
        self.assertEqual(result['changes']['64/seconds']['percent_change'], 200)
        report['environment']['blender'] = 'different'
        self.assertEqual(benchmark.compare(report, baseline)['status'], 'Not Comparable')

    def test_nondefault_cli_and_grid_have_explicit_parameters(self):
        args = benchmark.parser('test').parse_args(['--output', str(self.root / 'out'), '--profile-root', str(self.root),
                                                  '--sizes', '64,128', '--repeats', '3', '--warmups', '2'])
        self.assertEqual((args.sizes, args.repeats, args.warmups), ([64, 128], 3, 2))
        self.assertEqual(benchmark.grid(31)['shape'], [31, 31, 31])
        self.assertAlmostEqual(benchmark.grid(31)['steps'][0][0], .2)
        with self.assertRaises(ValueError):
            benchmark.grid(1)


if __name__ == '__main__':
    unittest.main()
