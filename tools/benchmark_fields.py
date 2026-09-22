"""Measure complete Blender worker MO jobs, including arrays and VDB caches."""
import ctypes
from ctypes import wintypes
import importlib
import json
from pathlib import Path
import platform
import time

import bpy

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'bl_ext.user_default.qcblender'
bpy.ops.preferences.addon_enable(module=MODULE)
Job = importlib.import_module(MODULE + '.blender.jobs').Job


class MemoryCounters(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
        'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]


memory_info = ctypes.WinDLL('psapi').GetProcessMemoryInfo
memory_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
memory_info.restype = wintypes.BOOL


def measure(job):
    started, peak = time.perf_counter(), 0
    progress_seen = False
    while time.perf_counter() - started < 300:
        memory = MemoryCounters()
        memory.cb = ctypes.sizeof(memory)
        if memory_info(int(job.process._handle), ctypes.byref(memory), memory.cb):
            peak = max(peak, memory.PeakWorkingSetSize)
        progress_seen |= (job.directory / 'progress.json').exists()
        result = job.poll()
        if result is not None:
            assert result['status'] == 'succeeded', result
            return {'seconds': time.perf_counter() - started, 'peak_working_set_mib': peak / 1024**2,
                    'cache_hit': result.get('cache_hit', False), 'progress_seen': progress_seen}
        time.sleep(.1)
    job.cancel()
    raise TimeoutError(str(job.directory))


source = Job('import', source=str(ROOT / 'tests/data/chemtools/ch4_uhf_ccpvdz.fchk'))
measure(source)
report = {'status': 'Running', 'blender': bpy.app.version_string, 'cpu': platform.processor(),
          'system': platform.platform(), 'quantity': 'orbital_amplitude', 'orbital': 8,
          'spin': 'alpha', 'source': 'CH4 UHF/cc-pVDZ; 34 AO', 'jobs': []}
path = ROOT / 'outputs/field-performance.json'
for size in (64, 128, 256):
    spacing = 6 / (size - 1)
    parameters = dict(dataset=str(source.directory / 'dataset'),
        grid={'origin': [-3., -3., -3.], 'steps': [[spacing, 0, 0], [0, spacing, 0], [0, 0, spacing]], 'shape': [size]*3},
        parameters={'quantity': 'orbital_amplitude', 'spin': 'alpha', 'orbital': 8, 'memory_mb': 1024})
    first = measure(Job('evaluate', **parameters))
    repeated = measure(Job('evaluate', **parameters))
    assert repeated['cache_hit']
    report['jobs'].append({'shape': [size]*3, 'first': first, 'repeated': repeated})
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report['jobs'][-1]), flush=True)
report['status'] = 'Passed'
path.write_text(json.dumps(report, indent=2), encoding='utf-8')
