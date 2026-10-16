"""Small command receipts with exact-input reuse and full logs on disk."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def identity(repo, scopes, inputs=(), environment=None):
    repo = Path(repo).resolve()
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z', '--', *scopes], cwd=repo).decode().split('\0')
    files = {name: digest(repo / name) if (repo / name).is_file() else 'missing'
             for name in sorted(filter(None, names))}
    if not files:
        raise ValueError('No tracked implementation files matched the check scope')
    return dict(files=files, inputs={str(Path(p).resolve()): digest(p) for p in inputs}, environment=environment or {})


class Run:
    def __init__(self, repo, directory):
        self.repo, self.directory = Path(repo).resolve(), Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)

    def record(self, name, value):
        path = self.directory / (name + '.json')
        write(path, value)
        summary = self.directory / 'summary.json'
        index = read(summary) if summary.exists() else {'checks': {}}
        index['checks'][name] = {'status': value['status'], 'report': str(path),
                                 'sha256': digest(path), 'elapsed_seconds': value.get('elapsed_seconds')}
        write(summary, index)
        return {'status': value['status'], 'report': str(path), **({'reused_from': value['reused_from']} if 'reused_from' in value else {})}

    def command(self, name, command, key, *, expected_report=None, reuse=None, retry=False, env=None):
        if '/' in name or '\\' in name:
            raise ValueError('Check name must be a single filename component')
        target = self.directory / (name + '.json')
        previous = Path(reuse) if reuse else target
        if previous.exists():
            data = read(previous)
            outputs_valid = all(Path(p).is_file() and digest(p) == h for p, h in data.get('outputs', {}).items())
            if data.get('status') == 'Passed' and data.get('identity') == key and outputs_valid:
                if previous.resolve() == target:
                    return {'status': 'Passed', 'report': str(target), 'reused_from': str(previous)}
                return self.record(name, {**data, 'reused_from': str(previous.resolve()), 'elapsed_seconds': 0})
            if (previous.resolve() == target or data.get('status') == 'Failed') and not retry:
                raise ValueError(f'{name}: previous result is failed or stale; inspect it, then use --retry or a new run directory')
        log = self.directory / (name + '.log')
        if target.exists():
            suffix = str(time.time_ns())
            target.rename(target.with_name(name + '.previous-' + suffix + '.json'))
            if log.exists():
                log.rename(log.with_name(name + '.previous-' + suffix + '.log'))
        if expected_report and Path(expected_report).exists():
            old = Path(expected_report)
            old.rename(old.with_name(old.stem + '.previous-' + str(time.time_ns()) + old.suffix))
        started = time.monotonic()
        process_env = os.environ.copy()
        process_env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        process_env.update(env or {})
        with log.open('wb') as stream:
            result = subprocess.run([str(x) for x in command], cwd=self.repo, env=process_env, stdout=stream, stderr=subprocess.STDOUT)
        passed = result.returncode == 0
        if expected_report:
            passed = passed and Path(expected_report).exists() and read(expected_report).get('status') == 'Passed'
        outputs = {str(Path(expected_report).resolve()): digest(expected_report)} if expected_report and Path(expected_report).exists() else {}
        receipt = dict(status='Passed' if passed else 'Failed', command=[str(x) for x in command],
                       source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.repo, text=True).strip(),
                       exit_code=result.returncode, identity=key, outputs=outputs, log=str(log), log_sha256=digest(log),
                       log_bytes=log.stat().st_size, elapsed_seconds=time.monotonic()-started)
        response = self.record(name, receipt)
        if not passed:
            response['error_tail'] = log.read_text(encoding='utf-8', errors='replace')[-3000:]
        return response
