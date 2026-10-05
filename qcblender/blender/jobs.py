import json
import os
from pathlib import Path
import subprocess
import uuid

import bpy

_active = set()


class Job:
    def __init__(self, action, **parameters):
        root = Path(bpy.utils.extension_path_user(__package__.rsplit('.', 1)[0],
                                                path='jobs', create=True))
        self.directory = root / uuid.uuid4().hex
        self.directory.mkdir()
        self.cleanup_after_exit = None
        request = {'schema': 1, 'job_id': self.directory.name, 'action': action}
        if any(key in request for key in parameters):
            raise ValueError('Job identity cannot be overridden')
        request.update(parameters)
        (self.directory / 'request.json').write_text(json.dumps(request), encoding='utf-8')
        worker = Path(__file__).resolve().parents[1] / 'worker.py'
        module = __package__.rsplit('.', 1)[0]
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env['PYTHONNOUSERSITE'] = '1'
        with (self.directory / 'worker.log').open('wb') as log:
            self.process = subprocess.Popen(
                [bpy.app.binary_path, '--background', '--factory-startup', '--offline-mode',
                 '--disable-autoexec', '--python-exit-code', '1', '--python', str(worker),
                 '--', '--module', module, '--directory', str(self.directory)],
                env=env, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        _active.add(self)

    def poll(self):
        code = self.process.poll()
        if code is None:
            return None
        if not hasattr(self, 'cancellation') or self.cleanup_after_exit is None:
            _active.discard(self)
        path = self.directory / 'result.json'
        if code != 0 or not path.is_file():
            raise RuntimeError(f'Worker exited with {code}; see {self.directory / "worker.log"}')
        report = json.loads(path.read_text(encoding='utf-8'))
        if report.get('schema') != 1 or report.get('job_id') != self.directory.name:
            raise ValueError('Worker returned a different request identity')
        return report

    def progress(self):
        path = self.directory / 'progress.json'
        if not path.exists():
            return {'phase': 'Starting Blender', 'fraction': 0.0}
        return json.loads(path.read_text(encoding='utf-8'))

    def cancel(self):
        """Request cancellation and retain ownership until exit and cleanup are confirmed."""
        errors = []
        requested = False
        try:
            (self.directory / 'cancel').touch()
            requested = True
        except OSError as error:
            errors.append(f'Cancellation request: {type(error).__name__}: {error}')
        code = None
        try:
            code = self.process.poll()
            if code is None:
                try:
                    self.process.terminate()
                except OSError as error:
                    errors.append(f'Worker termination: {type(error).__name__}: {error}')
                else:
                    try:
                        self.process.wait(timeout=10)
                    except (OSError, subprocess.TimeoutExpired) as error:
                        errors.append(f'Worker exit wait: {type(error).__name__}: {error}')
                code = self.process.poll()
        except OSError as error:
            errors.append(f'Worker exit check: {type(error).__name__}: {error}')
        cleanup_pending = self.cleanup_after_exit is not None
        if code is not None and cleanup_pending:
            try:
                self.cleanup_after_exit()
            except (OSError, ValueError, RuntimeError) as error:
                errors.append(f'Export staging cleanup: {type(error).__name__}: {error}')
            else:
                self.cleanup_after_exit = None
                cleanup_pending = False
        if code is not None and not cleanup_pending:
            _active.discard(self)
        else:
            _active.add(self)
        report = {'status': 'exited' if code is not None else 'exit_unconfirmed',
                  'cancel_requested': requested, 'pid': self.process.pid,
                  'directory': str(self.directory), 'returncode': code,
                  'cleanup_pending': cleanup_pending, 'errors': errors}
        self.cancellation = report
        try:
            (self.directory / 'cancellation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        except OSError as error:
            errors.append(f'Cancellation record: {type(error).__name__}: {error}')
        return report


def cancel_all():
    reports = []
    for job in list(_active):
        try:
            report = job.cancel()
        except Exception as error:
            # Unregister must attempt every owned child even if one finalizer fails unexpectedly.
            report = {'status': 'exit_unconfirmed', 'pid': job.process.pid,
                      'directory': str(job.directory),
                      'errors': [f'Cancellation failed: {type(error).__name__}: {error}']}
            job.cancellation = report
        reports.append(report)
        if report['errors'] or report['status'] != 'exited':
            print('QCBlender cancellation: ' + json.dumps(report))
    return reports
