"""Installed-extension worker, provenance and portable-project regression."""
import hashlib
import argparse
import importlib
import json
from pathlib import Path
import shutil
import sys
import time
from unittest.mock import patch

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_inputs import input_path
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/result-browser/verification')
parser.add_argument('--candidate', type=Path, default=ROOT / 'outputs/result-browser/dist/qcblender-0.0.1.zip')
parser.add_argument('--reopen', action='store_true')
parser.add_argument('--use-installed', action='store_true', help='Use the existing isolated installation without reinstalling')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
MODULE = 'bl_ext.user_default.qcblender'


def finish(job):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        report = job.poll()
        if report is not None:
            return report
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


if not args.reopen and not args.use_installed:
    repo = next((r for r in bpy.context.preferences.extensions.repos if r.module == 'user_default'), None)
    if repo is None:
        bpy.context.preferences.extensions.repos.new(name='User Default', module='user_default')
    assert bpy.ops.extensions.package_install_files(
        filepath=str(args.candidate.resolve()),
        repo='user_default', enable_on_install=True, overwrite=True) == {'FINISHED'}
    bpy.ops.wm.save_userpref()
else:
    bpy.ops.preferences.addon_enable(module=MODULE)

storage = importlib.import_module(MODULE + '.data')
browser = importlib.import_module(MODULE + '.blender.source_browser')
views = importlib.import_module(MODULE + '.blender.views')
project = importlib.import_module(MODULE + '.blender.project')
Job = importlib.import_module(MODULE + '.blender.jobs').Job
report = {'status': 'Passed', 'blender': bpy.app.version_string}

if '--reopen' in sys.argv:
    expected = json.loads((OUT / 'before-save.json').read_text())
    for obj in bpy.context.scene.objects:
        if obj.name in expected:
            assert browser.source_group(obj)[0] == tuple(expected[obj.name]['group'])
            assert browser.source_details(obj) == [tuple(v) for v in expected[obj.name]['details']]
            directory = Path(bpy.path.abspath(browser.source_object(obj)['qc_dataset'])).resolve()
            assert directory.is_relative_to(Path(bpy.data.filepath).with_suffix('.qcdata'))
            data = storage.load_dataset(directory)
            assert {k: hashlib.sha256(v.tobytes()).hexdigest() for k,v in data.arrays.items()} == expected[obj.name]['arrays']
    report['cold_reopen'] = 'Passed'
else:
    source = input_path('log-examples/water_neutral_nbo_opt_freq.out', ROOT)
    before = set(bpy.data.objects.keys())
    job = Job('inspect_source', source=str(source))
    preview = finish(job)
    assert preview['status'] == 'succeeded', preview
    assert len(preview['jobs']) == 2
    assert set(bpy.data.objects.keys()) == before and not (job.directory / 'dataset').exists()
    report['preview_without_scene_or_dataset'] = 'Passed'
    from_source = []
    for i in range(2):
        job = Job('import', source=str(source), job_index=i, source_sha256=preview['source']['sha256'])
        receipt = finish(job)
        assert receipt['status'] == 'succeeded', receipt
        data = storage.load_dataset(job.directory / 'dataset')
        assert data.metadata['jobs'] == preview['jobs']
        assert data.metadata['selected_job'] == i
        from_source.append(views.atom_view(job.directory / 'dataset'))
    assert browser.source_group(from_source[0])[0] != browser.source_group(from_source[1])[0]
    report['selected_jobs'] = 'Passed'
    spectrum = from_source[1].qc_settings.spectrum
    assert spectrum and browser.source_group(spectrum)[0] == browser.source_group(from_source[1])[0]
    assert any(title == 'Spectrum' for title, _ in browser.source_details(spectrum))
    report['spectrum_parent_binding'] = 'Passed'
    changed = OUT / source.name
    changed.write_bytes(source.read_bytes() + b'\nchanged after preview\n')
    rejected = finish(Job('import', source=str(changed), job_index=0, source_sha256=preview['source']['sha256']))
    assert rejected['status'] == 'failed' and 'changed after preview' in rejected['error'], rejected
    report['changed_source_rejected'] = 'Passed'
    job = Job('import', source=str(changed), job_index=0)
    assert finish(job)['status'] == 'succeeded'
    other = views.atom_view(job.directory / 'dataset')
    assert browser.source_group(other)[0] != browser.source_group(from_source[0])[0]
    assert browser.source_group(other)[1].split(' | ')[0] == browser.source_group(from_source[0])[1].split(' | ')[0]
    report['same_filename_different_source'] = 'Passed'
    obj = from_source[1]
    bpy.context.view_layer.objects.active = obj
    assert bpy.ops.qcblender.layer_action(target=obj.name, action='DUPLICATE') == {'FINISHED'}
    duplicate = bpy.context.object
    assert browser.source_group(duplicate)[0] == browser.source_group(obj)[0]
    with patch.object(np, 'load', side_effect=AssertionError('Provenance loaded scientific arrays')):
        details = browser.source_details(obj)
        assert bpy.ops.qcblender.refresh_sources() == {'FINISHED'}
        assert any(title == 'Calculation' for title, _ in details)
    report['metadata_only_and_duplicate'] = 'Passed'
    original = obj['qc_dataset']
    obj['qc_dataset'] = str(OUT / 'missing.qcdata')
    assert 'error' in browser.source_details(obj)[0][1]
    obj['qc_dataset'] = original
    report['broken_binding'] = 'Passed'
    # Failed refresh must not merge legacy calculations with unknown job identity.
    legacy = [dict(qc_dataset=str(OUT / f'missing-{i}'), qc_source_sha256='same') for i in range(2)]
    for binding in legacy:
        browser.refresh_source(binding)
    assert browser.source_group(legacy[0])[0] != browser.source_group(legacy[1])[0]
    malformed = OUT / 'malformed'
    malformed.mkdir(exist_ok=True)
    for patch_meta in ({'selected_job': 0, 'jobs': [None]},
                       {'analysis': {'sources': ['bad']}}, {'analysis': {'geometry_source': 'bad'}}):
        meta = dict(source={}, **patch_meta)
        (malformed / 'manifest.json').write_text(json.dumps(
            dict(format='qcblender.project', schema=storage.SCHEMA, metadata=meta)))
        assert 'error' in browser.refresh_source({'qc_dataset': str(malformed)})
    for key in ('qc_field', 'qc_color_source', 'qc_association'):
        previous = obj.get(key)
        obj[key] = '[]'
        try:
            browser.source_details(obj)
        except ValueError as error:
            assert 'Invalid object source record' in str(error)
        else:
            raise AssertionError(key)
        if previous is None:
            del obj[key]
        else:
            obj[key] = previous
    report['malformed_and_legacy_missing_metadata'] = 'Passed'
    snapshot = {}
    for obj in bpy.context.scene.objects:
        if browser.source_object(obj).get('qc_dataset'):
            data = storage.load_dataset(bpy.path.abspath(browser.source_object(obj)['qc_dataset']))
            snapshot[obj.name] = {'group': browser.source_group(obj)[0], 'details': browser.source_details(obj),
                'arrays': {k: hashlib.sha256(v.tobytes()).hexdigest() for k,v in data.arrays.items()}}
    (OUT / 'before-save.json').write_text(json.dumps(snapshot), encoding='utf-8')
    project.save_project(OUT / 'sources.blend')
    moved = OUT / 'moved'
    moved.mkdir(exist_ok=True)
    shutil.copy2(OUT / 'sources.blend', moved / 'sources.blend')
    shutil.copytree(OUT / 'sources.qcdata', moved / 'sources.qcdata', dirs_exist_ok=True)
    report['portable_save'] = 'Passed'
    # Rebuild real source associations without historical evidence projects.
    from tools.prepare_sop_fixture import prepare as rebuild
    for case in ('C04', 'C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13'):
        rebuild(case)
        bpy.ops.preferences.addon_enable(module=MODULE)
        count = 0
        for obj in bpy.context.scene.objects:
            if browser.source_object(obj).get('qc_dataset'):
                with patch.object(np, 'load', side_effect=AssertionError('Provenance loaded scientific arrays')):
                    details = browser.source_details(obj)
                assert not any('error' in value for _, value in details), (case,obj.name,details)
                if obj.get('qc_color_source'):
                    volume = browser.color_volume(obj)
                    color_meta = browser.refresh_source(volume)
                    if json.loads(volume['qc_field']).get('role') == 'color':
                        assert dict(details)['Color source'] == color_meta['analysis']['color_source']
                        assert browser.source_group(volume)[0][0] == color_meta['analysis']['color_source']['sha256']
                    modifier = importlib.import_module(MODULE + '.blender.graph').view_modifier(obj)
                    sampler = next(n for n in modifier.node_group.nodes if n.bl_idname == 'GeometryNodeGroup'
                        and n.node_tree and n.node_tree.get('qc_asset_id') == 'qc.color_scalar.v2').inputs['Value'].links[0].from_node
                    link = sampler.inputs['Volume'].links[0]
                    socket = link.from_socket
                    modifier.node_group.links.remove(link)
                    assert any('error' in v for _,v in browser.source_details(obj)), obj.name
                    modifier.node_group.links.new(socket, sampler.inputs['Volume'])
                    assert browser.color_volume(obj) == volume
                count += 1
        assert count
        report[case] = {'status': 'Passed', 'sources': count}

destination = OUT / ('cold-reopen.json' if '--reopen' in sys.argv else 'checks.json')
destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
