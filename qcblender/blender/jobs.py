import json
import os
from pathlib import Path
import subprocess
import uuid
import weakref

import bpy

_active = weakref.WeakSet()


class Job:
    def __init__(self, action, **parameters):
        root = Path(bpy.utils.extension_path_user(__package__.rsplit('.', 1)[0],
                                                path='jobs', create=True))
        self.directory = root / uuid.uuid4().hex
        self.directory.mkdir()
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
        (self.directory / 'cancel').touch()
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=10)
        _active.discard(self)


def cancel_all():
    for job in list(_active):
        job.cancel()
