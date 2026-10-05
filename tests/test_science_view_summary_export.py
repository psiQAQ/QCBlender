"""Summary exports exercise real Dataset loading and atomic publication."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qcblender.data import Dataset, save_dataset
from qcblender.data_export import available_exports, export_dataset, export_report


ROOT = Path(__file__).resolve().parents[1]


class SummaryExport(unittest.TestCase):
    def setUp(self):
        output = ROOT / 'outputs/runs/alpha-summary/export-tests'
        output.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        field = dict(array='values', valid_mask='valid', quantity='electrostatic_potential',
                     unit='hartree/e', origin=[0., 0., 0.], steps=np.eye(3).tolist(), shape=[2, 2, 2],
                     coordinate_unit='angstrom', nuclear_exclusion_radius_bohr=.02)
        self.data = Dataset({'source': {'filename': '来源|特殊.cube', 'sha256': 'a' * 64},
                             'coordinate_unit': 'angstrom', 'method': 'HF', 'basis_name': 'STO-3G',
                             'calculation_status': 'unknown', 'fields': [field]},
                            {'atomic_numbers': np.array([1]), 'positions': np.zeros((1, 3)),
                             'values': np.arange(8.).reshape((2, 2, 2)),
                             'valid': np.array([True] * 7 + [False]).reshape((2, 2, 2))})
        self.source = self.directory / 'dataset'
        save_dataset(self.data, self.source)
        self.digest = hashlib.sha256((self.source / 'manifest.json').read_bytes()).hexdigest()
        self.snapshot = {'schema': 1, 'dataset_manifest_sha256': self.digest,
                         'captured_at_utc': '2026-10-05T00:00:00+00:00',
                         'view': {'name': '视图|<文字>', 'kind': 'field', 'scene_frame': 1},
                         'fields': {'geometry': {'field': field, 'source': self.data.metadata['source'],
                                                  'dataset_manifest_sha256': self.digest}},
                         'display': {'status': 'captured', 'parameters': [
                             {'name': 'Isovalue', 'label': '阈值 [hartree/e]', 'socket_type': 'NodeSocketFloat',
                              'value': .03, 'location': 'QC / threshold'}], 'materials': [], 'reasons': []}}

    def export(self, **kwargs):
        return export_dataset(self.source, self.directory / 'results', 'SUMMARY',
                              expected_sha256=self.digest, view_snapshot=self.snapshot, **kwargs)

    def test_summary_contains_source_mask_and_live_snapshot_without_schema_change(self):
        report = self.export()
        result = Path(report['directory'])
        record = json.loads((result / 'metadata.json').read_text(encoding='utf-8'))
        summary = record['view_summary']
        self.assertEqual(record['schema'], 1)
        self.assertEqual(record['scientific_metadata'], self.data.metadata)
        self.assertEqual(summary['display']['parameters'][0]['value'], .03)
        self.assertEqual(summary['scientific']['fields'][0]['valid_sample_count'], 7)
        self.assertEqual(summary['scientific']['fields'][0]['field']['nuclear_exclusion_radius_bohr'], .02)
        self.assertEqual(record['files'][0]['sha256'], hashlib.sha256((result / 'view-summary.md').read_bytes()).hexdigest())
        text = (result / 'view-summary.md').read_text(encoding='utf-8')
        self.assertIn('hartree/e', text)
        self.assertIn('视图\\|&lt;文字&gt;', text)
        self.assertEqual({path.name for path in result.iterdir()}, {'view-summary.md', 'metadata.json'})

    def test_partial_and_missing_scientific_fields_are_explicit(self):
        self.data.metadata.pop('method')
        save_dataset(self.data, self.source)
        self.digest = hashlib.sha256((self.source / 'manifest.json').read_bytes()).hexdigest()
        self.snapshot['dataset_manifest_sha256'] = self.digest
        self.snapshot['fields']['geometry']['dataset_manifest_sha256'] = self.digest
        self.snapshot['display'].update(status='unverified', parameters=[], reasons=['Custom node graph'])
        record = json.loads((Path(self.export()['directory']) / 'metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(record['view_summary']['scientific']['status'], 'partial')
        self.assertIsNone(record['view_summary']['scientific']['method'])
        self.assertEqual(record['view_summary']['display']['parameters'], [])
        self.assertEqual(record['view_summary']['display']['status'], 'unverified')

    def test_snapshot_identity_and_non_finite_values_fail_before_publication(self):
        self.snapshot['dataset_manifest_sha256'] = '0' * 64
        self.assertRaisesRegex(ValueError, 'different Dataset', self.export)
        self.snapshot['dataset_manifest_sha256'] = self.digest
        self.snapshot['display']['parameters'][0]['value'] = float('nan')
        self.assertRaises(ValueError, self.export)
        self.assertFalse((self.directory / 'results').exists())

    def test_repeated_exports_cancellation_and_write_failure_preserve_results(self):
        first = self.export()
        before = (Path(first['directory']) / 'metadata.json').read_bytes()
        second = self.export()
        self.assertNotEqual(first['directory'], second['directory'])
        self.assertRaisesRegex(RuntimeError, 'cancelled', self.export, cancelled=lambda: True)
        with patch('qcblender.view_summary.render_summary', side_effect=OSError('disk full')):
            self.assertRaisesRegex(OSError, 'disk full', self.export)
        self.assertEqual((Path(first['directory']) / 'metadata.json').read_bytes(), before)
        self.assertEqual(len(list((self.directory / 'results').iterdir())), 2)

    def test_worker_report_reuses_export_and_requires_snapshot(self):
        request = dict(dataset=str(self.source), dataset_sha256=self.digest, kind='SUMMARY',
                       output_directory=str(self.directory / 'results'), view_snapshot=self.snapshot)
        self.assertTrue(Path(export_report(request, self.directory)['directory']).is_dir())
        request.pop('view_snapshot')
        self.assertRaisesRegex(ValueError, 'snapshot', export_report, request, self.directory)
        self.assertIn('SUMMARY', available_exports(self.data))

    def test_field_source_and_identity_must_match_dataset(self):
        self.snapshot['fields']['geometry']['source'] = {'sha256': '0' * 64}
        self.assertRaisesRegex(ValueError, 'field source differs', self.export)
        self.snapshot['fields']['geometry']['source'] = self.data.metadata['source']
        self.snapshot['fields']['geometry']['field'] = dict(self.data.metadata['fields'][0], unit='incorrect')
        self.assertRaisesRegex(ValueError, 'field differs', self.export)

    def test_dataset_change_before_publication_cleans_staging(self):
        from qcblender.view_summary import render_summary
        def change_manifest(summary):
            text = render_summary(summary)
            with (self.source / 'manifest.json').open('ab') as stream:
                stream.write(b'\n')
            return text
        with patch('qcblender.view_summary.render_summary', side_effect=change_manifest):
            self.assertRaisesRegex(ValueError, 'before publishing', self.export)
        self.assertEqual(list((self.directory / 'results').iterdir()), [])


if __name__ == '__main__':
    unittest.main()
