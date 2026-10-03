"""Repeated worker timings. Cold/hot reset application indices, not OS caches.

Run with Blender --background --python-exit-code 1 --python THIS_FILE -- ... .
Both modes use fresh workers and the same source Dataset. Import is uncached in
both modes. Evidence directories and isolated profiles must be new for each run.
"""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
SOURCE = ROOT / 'tests/data/chemtools/ch4_uhf_ccpvdz.fchk'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def module(name):
    return importlib.import_module(MODULE + '.' + name)


def verify_installed_python(installed, checkout):
    installed_hashes = {p.relative_to(installed).as_posix(): sha256(p) for p in sorted(installed.rglob('*.py'))}
    checkout_hashes = {p.relative_to(checkout).as_posix(): sha256(p) for p in sorted(checkout.rglob('*.py'))}
    if installed_hashes != checkout_hashes:
        changed = sorted(name for name in installed_hashes.keys() | checkout_hashes.keys()
                         if installed_hashes.get(name) != checkout_hashes.get(name))
        raise ValueError('Installed Python differs from current checkout: ' + ', '.join(changed))
    return installed_hashes


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('Expected a positive integer')
    return number


def integers(value):
    result = [positive(part) for part in value.split(',')]
    if len(set(result)) != len(result):
        raise argparse.ArgumentTypeError('Duplicate values are not supported')
    return result


def parser(description, kind='sizes', default='64,128,256'):
    result = argparse.ArgumentParser(description=description)
    result.add_argument('--output', type=Path, required=True, help='New evidence directory; never overwritten')
    result.add_argument('--profile-root', type=Path, required=True, help='Task-owned isolated profile root')
    result.add_argument('--candidate', type=Path, help='Optional candidate extension ZIP to install into fresh profile')
    result.add_argument('--repeats', type=positive, default=5)
    result.add_argument('--warmups', type=int, default=1)
    result.add_argument('--' + kind, type=integers, default=integers(default))
    result.add_argument('--timeout', type=positive, default=900)
    result.add_argument('--baseline', type=Path)
    return result


def cli_arguments():
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]


def validate_profile(root, paths):
    root = root.resolve(strict=True)
    if root == Path(root.anchor):
        raise ValueError('Profile root must be a dedicated directory')
    for label, path in paths.items():
        if not path:
            raise ValueError('Required isolated path missing: ' + label)
        resolved = Path(path).resolve(strict=True)
        if resolved == root or not resolved.is_relative_to(root):
            raise ValueError('Path must be strictly inside profile root: ' + label)
    with (root / '.qc-performance-owner').open('x', encoding='utf-8') as stream:
        stream.write(str(os.getpid()))
    return root


def setup(args, benchmark):
    if args.warmups < 0:
        raise ValueError('Warmups cannot be negative')
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'schema': 1, 'benchmark': benchmark, 'status': 'Running', 'trials': [], 'warmups': []}
    save(args.output, report)
    return report


def enable(args, report):
    import bpy
    paths = {key: os.environ.get(key) for key in ('BLENDER_USER_CONFIG', 'BLENDER_USER_EXTENSIONS', 'TEMP', 'TMP')}
    paths['actual_config'] = bpy.utils.user_resource('CONFIG')
    paths['actual_extensions'] = bpy.utils.user_resource('EXTENSIONS')
    profile = validate_profile(args.profile_root, paths)
    if args.candidate:
        repository = next((r for r in bpy.context.preferences.extensions.repos if r.module == 'user_default'), None)
        if repository is None:
            repository = bpy.context.preferences.extensions.repos.new(name='User Default', module='user_default')
        if repository is None or not Path(repository.directory).resolve().is_relative_to(profile):
            raise ValueError('Candidate install repository escapes isolated profile')
        outcome = bpy.ops.extensions.package_install_files(filepath=str(args.candidate.resolve(strict=True)),
            repo='user_default', enable_on_install=True)
        if outcome != {'FINISHED'}:
            raise RuntimeError('Candidate installation failed: ' + str(outcome))
        report['candidate'] = {'path': str(args.candidate), 'sha256': sha256(args.candidate)}
    bpy.ops.preferences.addon_enable(module=MODULE)
    jobs = Path(bpy.utils.extension_path_user(MODULE, path='jobs', create=True)).resolve(strict=True)
    if not jobs.is_relative_to(profile) or any(jobs.iterdir()):
        raise ValueError('Use a fresh isolated profile: jobs must be inside profile and initially empty')
    installed = Path(importlib.import_module(MODULE).__file__).resolve().parent
    if not installed.is_relative_to(profile):
        raise ValueError('Installed extension escapes isolated profile')
    installed_hashes = verify_installed_python(installed, ROOT / 'qcblender')
    from importlib.metadata import version
    cpu = platform.processor()
    if os.name == 'nt':
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0]
    report.update(environment={'blender': bpy.app.version_string, 'binary_sha256': sha256(bpy.app.binary_path),
        'system': platform.platform(), 'machine': platform.machine(), 'cpu': cpu, 'logical_cpus': os.cpu_count(),
        'python': platform.python_version(), 'numpy': version('numpy'), 'qc_gbasis': version('qc-gbasis')},
        provenance={'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    'installed_root': str(installed),
                    'installed_python_sha256': installed_hashes,
                    'checkout_python_match': True,
                    'tool_sha256': {name: sha256(ROOT / 'tools' / name) for name in ('benchmark_fields.py', 'benchmark_display.py')}},
        source={'path': str(SOURCE), 'sha256': sha256(SOURCE)}, isolated_profile=str(profile), jobs_root=str(jobs),
        parameters={'repeats': args.repeats, 'warmups': args.warmups, 'timeout': args.timeout,
                    'quantity': 'orbital_amplitude', 'spin': 'alpha', 'orbital': 8, 'memory_mb': 1024},
        timing_definition={'worker': 'Job creation through successful process completion, including startup and VDB publication',
            'import': 'Fresh worker every trial; no application import cache',
            'cold': 'Evaluation index absent; OS caches not flushed',
            'hot': 'Validated evaluation index present; fresh worker, same source Dataset',
            'memory': 'Windows process lifetime PeakWorkingSetSize, worker/UI separately'})
    return jobs


class MemoryCounters(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
        'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]


def process_peak(handle=None):
    if os.name != 'nt':
        raise RuntimeError('This baseline requires Windows GetProcessMemoryInfo')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    get_info = ctypes.WinDLL('psapi', use_last_error=True).GetProcessMemoryInfo
    get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
    get_info.restype = wintypes.BOOL
    memory = MemoryCounters()
    memory.cb = ctypes.sizeof(memory)
    if not get_info(handle if handle is not None else kernel.GetCurrentProcess(), ctypes.byref(memory), memory.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return memory.PeakWorkingSetSize / 1024**2


def run_job(action, timeout, **parameters):
    started = time.perf_counter()
    pending = module('blender.jobs').Job(action, **parameters)
    peak, progress_seen = 0., False
    try:
        while time.perf_counter() - started < timeout:
            peak = max(peak, process_peak(int(pending.process._handle)))
            progress_seen |= (pending.directory / 'progress.json').exists()
            result = pending.poll()
            if result is not None:
                if result['status'] != 'succeeded':
                    raise RuntimeError(result)
                return pending.directory / 'dataset', dict(seconds=time.perf_counter() - started,
                    peak_working_set_mib=peak, process_id=pending.process.pid, cache_hit=result.get('cache_hit', False),
                    cache_rejected=result.get('cache_rejected'), progress_seen=progress_seen,
                    job_directory=str(pending.directory), source_sha256=result['source_sha256'])
            time.sleep(.05)
        raise TimeoutError(str(pending.directory))
    except BaseException as error:
        error.job_directory = str(pending.directory)
        pending.cancel()
        raise


def dataset_identity(directory):
    """Validate actual arrays/VDB bytes, then return scientific identity independent of path."""
    import numpy as np
    data = module('data').load_dataset(directory)
    for field in data.metadata.get('fields', []):
        module('data').volume_cache(directory, field)
    return {'source_sha256': data.metadata['source']['sha256'], 'arrays': {
        name: {'dtype': array.dtype.str, 'shape': list(array.shape),
               'sha256': hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()}
        for name, array in sorted(data.arrays.items())}}


def grid(size):
    if size < 2:
        raise ValueError('Grid size must be at least 2')
    spacing = 6 / (size - 1)
    return {'origin': [-3., -3., -3.], 'steps': [[spacing, 0, 0], [0, spacing, 0], [0, 0, spacing]], 'shape': [size] * 3}


def evaluation(source, size):
    return dict(dataset=str(source), dataset_sha256=sha256(source / 'manifest.json'), grid=grid(size),
        parameters={'quantity': 'orbital_amplitude', 'spin': 'alpha', 'orbital': 8, 'memory_mb': 1024})


def owned_index(cache, before, dataset):
    new = set(cache.glob('*.json')) - before
    if len(new) != 1:
        raise ValueError('Expected exactly one new evaluation cache index')
    index = new.pop()
    cached = (cache / json.loads(index.read_text(encoding='utf-8'))['dataset']).resolve(strict=True)
    if not cached.is_relative_to(cache.resolve()) or cached == cache.resolve():
        raise ValueError('Cache index escapes task cache')
    if dataset_identity(cached) != dataset_identity(dataset):
        raise ValueError('Cache index points to a different scientific Dataset')
    return index, sha256(index)


def evict_owned_index(index, expected_digest, cache, profile):
    index, cache, profile = index.resolve(strict=True), cache.resolve(strict=True), profile.resolve(strict=True)
    if index.parent != cache or not cache.is_relative_to(profile) or not (profile / '.qc-performance-owner').is_file():
        raise ValueError('Cache eviction requires an owned index in the isolated profile')
    if sha256(index) != expected_digest:
        raise ValueError('Owned cache index changed before eviction')
    index.unlink()


def summary(records):
    result = {}
    for key in records[0]:
        if key.endswith(('seconds', '_mib')):
            values = [record[key] for record in records]
            result[key] = {'median': statistics.median(values), 'min': min(values), 'max': max(values)}
    return result


def compare(report, baseline):
    previous = json.loads(baseline.read_text(encoding='utf-8'))
    keys = ('schema', 'benchmark', 'environment', 'parameters')
    incompatible = [key for key in keys if report[key] != previous.get(key)]
    if report['source']['sha256'] != previous.get('source', {}).get('sha256'):
        incompatible.append('source SHA-256')
    if previous.get('status') != 'Passed':
        incompatible.append('baseline status')
    if incompatible:
        return {'status': 'Not Comparable', 'mismatches': incompatible}
    if not report.get('scientific_identity') or not previous.get('scientific_identity'):
        raise ValueError('Scientific identity is required in candidate and baseline reports')
    if report['scientific_identity'] != previous['scientific_identity']:
        raise ValueError('Scientific identity differs from baseline')
    changes = {}
    for group, metrics in report['summary'].items():
        for metric, value in metrics.items():
            old = previous['summary'][group][metric]['median']
            changes[group + '/' + metric] = {'baseline_median': old, 'candidate_median': value['median'],
                'percent_change': 100 * (value['median'] / old - 1) if old else None}
    return {'status': 'Compared', 'policy': 'Report only; no speed regression threshold', 'changes': changes}


def save(output, report):
    pending = output / 'report.pending.json'
    pending.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    pending.replace(output / 'report.json')


def main():
    args = parser(__doc__).parse_args(cli_arguments())
    report = setup(args, 'fields')
    try:
        jobs = enable(args, report)
        report['parameters']['sizes'] = args.sizes
        source, report['initial_import'] = run_job('import', args.timeout, source=str(SOURCE), source_sha256=sha256(SOURCE))
        original = dataset_identity(source)
        report['source_dataset'] = {'path': str(source), 'identity': original}
        report['scientific_identity'] = {'source': original, 'fields': {}}
        cache = jobs / 'cache'
        report['summary'] = {}
        for size in args.sizes:
            owned, expected = None, None
            for iteration in range(args.warmups + args.repeats):
                if owned:
                    evict_owned_index(*owned, cache, args.profile_root)
                before = set(cache.glob('*.json'))
                pair = {'size': size, 'iteration': iteration, 'source_dataset': str(source)}
                (report['warmups'] if iteration < args.warmups else report['trials']).append(pair)
                for mode in ('cold', 'hot'):
                    trial = pair[mode] = {}
                    imported, trial['import'] = run_job('import', args.timeout, source=str(SOURCE), source_sha256=sha256(SOURCE))
                    if dataset_identity(imported) != original:
                        raise ValueError('Repeated import changed scientific arrays')
                    output, trial['evaluate'] = run_job('evaluate', args.timeout, **evaluation(source, size))
                    actual = dataset_identity(output)
                    trial['identity'] = actual
                    if trial['evaluate']['cache_hit'] != (mode == 'hot') or trial['evaluate']['cache_rejected']:
                        raise ValueError('Unexpected cache hit/rejection: ' + mode)
                    if actual['source_sha256'] != original['source_sha256'] or (expected and actual != expected):
                        raise ValueError('Evaluation scientific arrays changed across trials')
                    expected = actual
                    if mode == 'cold':
                        owned = owned_index(cache, before, output)
                    if dataset_identity(source) != original or sha256(SOURCE) != report['source']['sha256']:
                        raise ValueError('Source Dataset or input changed during benchmark')
                    save(args.output, report)
            formal = [trial for trial in report['trials'] if trial['size'] == size]
            report['scientific_identity']['fields'][str(size)] = expected
            for mode in ('cold', 'hot'):
                for stage in ('import', 'evaluate'):
                    report['summary'][f'{size}/{mode}/{stage}'] = summary([trial[mode][stage] for trial in formal])
        report['status'] = 'Passed'
        if args.baseline:
            report['comparison'] = compare(report, args.baseline)
        save(args.output, report)
    except BaseException as error:
        report.update(status='Failed', error=f'{type(error).__name__}: {error}')
        if hasattr(error, 'job_directory'):
            report['failed_job_directory'] = error.job_directory
        save(args.output, report)
        raise


if __name__ == '__main__':
    main()
