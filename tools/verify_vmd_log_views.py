"""Copy display settings between real Gaussian jobs without changing job identity."""
import argparse
import json
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_vmd_parameters as base


def finish(job):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        report = job.poll()
        if report is not None:
            assert report['status'] == 'succeeded', report
            return report
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


def check(out, reopen=False):
    bpy.ops.preferences.addon_enable(module=base.MODULE)
    browser = base.module('blender.source_browser')
    if reopen:
        before = json.loads((out / 'checks.json').read_text(encoding='utf-8'))
        for name, expected in before['real_jobs'].items():
            obj = bpy.data.objects[name]
            metadata = browser.read_metadata(obj)
            job = metadata['selected_job']
            assert metadata['jobs'][job] == expected['job']
            assert list(browser.source_group(obj)[0]) == expected['group']
            assert obj.qc_settings.active_mode == expected['active_mode']
        return base.check_reopen(out)

    out.mkdir(parents=True, exist_ok=True)
    source = base.ROOT / 'outputs/log-examples/water_neutral_nbo_opt_freq.out'
    Job = base.module('blender.jobs').Job
    preview = finish(Job('inspect_source', source=str(source)))
    assert len(preview['jobs']) == 2
    for obj in bpy.context.scene.objects:
        if obj.type not in ('CAMERA', 'LIGHT'):
            obj.hide_render = True
    objects, expected = [], {}
    for index in (0, 1):
        job = Job('import', source=str(source), job_index=index,
                  source_sha256=preview['source']['sha256'])
        finish(job)
        obj = base.module('blender.views').atom_view(job.directory / 'dataset')
        obj.name = f'VMD real Gaussian Job {index + 1}'
        obj.location.x = index * 3
        meta = browser.read_metadata(obj)
        assert meta['selected_job'] == index and meta['jobs'] == preview['jobs']
        assert meta['source']['sha256'] == preview['source']['sha256']
        objects.append(obj)
    first, second = objects
    assert browser.source_group(first)[0] != browser.source_group(second)[0]
    assert first['qc_source_sha256'] == second['qc_source_sha256']
    assert len(second.qc_settings.modes) > 1
    second.qc_settings.active_mode = 1
    first_mod, first_keys = base.controls(first)
    second_mod, second_keys = base.controls(second)
    first_mod[first_keys['Atom Radius']] = .41
    second_mod[second_keys['Amplitude (angstrom)']] = .23
    second_mod[second_keys['First Atom (1-based)']] = 2
    bpy.context.view_layer.update()
    before = base.display_state(second)
    arrays = base.hashes()
    base.activate(first)
    second.select_set(True)
    assert bpy.ops.qcblender.copy_display_parameters() == {'FINISHED'}
    assert second_mod[second_keys['Atom Radius']] == first_mod[first_keys['Atom Radius']]
    after = base.display_state(second)
    assert after['transform'] == before['transform']
    for name in ('Amplitude (angstrom)', 'Phase', 'Animate', 'First Atom (1-based)'):
        assert after['inputs'][name] == before['inputs'][name]
    assert second.qc_settings.active_mode == 1
    assert base.hashes() == arrays
    for obj in objects:
        meta = browser.read_metadata(obj)
        expected[obj.name] = {'group': list(browser.source_group(obj)[0]),
                             'job': meta['jobs'][meta['selected_job']],
                             'active_mode': obj.qc_settings.active_mode}
    report = {'real_log_two_jobs': 'Passed', 'copy_preserves_job_and_vibration': 'Passed',
              'source': preview['source'], 'real_jobs': expected,
              'scope': 'Real Log atom views and their calculation identity; no Log wavefunction field is inferred.',
              'render_pixels': base.render(out / 'evidence.png')}
    base.save_evidence(out, report)
    return {key: value for key, value in report.items() if key not in ('arrays', 'objects', 'real_jobs')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reopen', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    print(json.dumps(check(args.out, args.reopen), ensure_ascii=False))
