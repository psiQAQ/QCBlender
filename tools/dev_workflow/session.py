"""Inventory and launch one Blender process without terminating user processes."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time


_CHILDREN = {}


def list_blender_processes():
    """Return pid/exe/starttime using Get-Process, with no window automation."""
    if os.name != 'nt':
        raise RuntimeError('Blender process inventory currently requires Windows')
    script = (
        "$ErrorActionPreference = 'Stop'; "
        "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
        "$items = @(Get-Process | Where-Object { $_.ProcessName -like 'blender*' } | "
        "ForEach-Object { [pscustomobject]@{ pid = [int]$_.Id; "
        "exe = $_.Path; starttime = $_.StartTime.ToUniversalTime().ToString('o') } }); "
        'ConvertTo-Json -InputObject $items -Compress'
    )
    result = subprocess.run(['powershell.exe', '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script],
                            capture_output=True, text=True, encoding='utf-8',
                            creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    if result.returncode:
        raise RuntimeError('Windows Get-Process Blender inventory failed: ' + result.stderr.strip())
    return sorted(json.loads(result.stdout), key=lambda item: item['pid'])


def _write_receipt(path, receipt):
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def launch_blender(binary, args=(), profile=None, outputdir=None, wait=False, timeout=None):
    """Launch only when no Blender exists; optionally wait for background completion."""
    binary = Path(binary).resolve(strict=True)
    if binary.name.lower() != 'blender.exe':
        raise ValueError('Expected a Blender executable named blender.exe')
    existing = list_blender_processes()
    if existing:
        raise RuntimeError('Blender is already running; close it normally first. '
                           f"Existing PIDs: {[item['pid'] for item in existing]}")
    output = Path(outputdir or Path(__file__).resolve().parents[2] / 'outputs/dev-workflow/sessions').resolve()
    output.mkdir(parents=True, exist_ok=True)
    stem = f'blender-{time.time_ns()}'
    logfile = output / f'{stem}.log'
    receiptfile = output / f'{stem}.json'
    environment = os.environ.copy()
    if profile is not None:
        profile = Path(profile).resolve()
        profile.mkdir(parents=True, exist_ok=True)
        environment['BLENDER_USER_RESOURCES'] = str(profile)
        for kind in ('CONFIG', 'SCRIPTS', 'DATAFILES', 'EXTENSIONS', 'CACHE'):
            directory = profile / kind.lower()
            directory.mkdir(parents=True, exist_ok=True)
            environment['BLENDER_USER_' + kind] = str(directory)
    command = [str(binary), *map(str, args)]
    with logfile.open('wb') as log:
        child = subprocess.Popen(command, env=environment, stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    _CHILDREN[child.pid] = child
    receipt = {'status': 'Passed', 'running': True, 'pid': child.pid, 'exe': str(binary),
               'starttime': None,
               'launched_at': datetime.now(timezone.utc).isoformat(), 'args': command[1:],
               'profile': str(profile) if profile is not None else None,
               'log': str(logfile), 'receipt': str(receiptfile)}
    _write_receipt(receiptfile, receipt)
    try:
        identity = next((item for item in list_blender_processes() if item['pid'] == child.pid), {})
    except (RuntimeError, OSError, subprocess.TimeoutExpired):
        receipt.update(status='Failed', reason='post-launch process inventory failed')
        _write_receipt(receiptfile, receipt)
        return receipt
    receipt['starttime'] = identity.get('starttime')
    _write_receipt(receiptfile, receipt)
    if wait:
        receipt.update(wait_exit(child.pid, timeout))
        receipt['running'] = not receipt['exited']
        _write_receipt(receiptfile, receipt)
    return receipt


def wait_exit(pid, timeout=60):
    """Wait without killing; a timeout leaves Blender running and reports Failed."""
    pid = int(pid)
    if pid <= 0 or (timeout is not None and timeout < 0):
        raise ValueError('PID must be positive and timeout must be nonnegative')
    child = _CHILDREN.get(pid)
    if child is not None:
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'status': 'Failed', 'pid': pid, 'exited': False, 'reason': 'timeout'}
        _CHILDREN.pop(pid)
        return {'status': 'Passed' if code == 0 else 'Failed', 'pid': pid, 'exited': True, 'exit_code': code}
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        if not any(item['pid'] == pid for item in list_blender_processes()):
            return {'status': 'Passed', 'pid': pid, 'exited': True, 'exit_code': None}
        if deadline is not None and time.monotonic() >= deadline:
            return {'status': 'Failed', 'pid': pid, 'exited': False, 'reason': 'timeout'}
        time.sleep(0.25)
