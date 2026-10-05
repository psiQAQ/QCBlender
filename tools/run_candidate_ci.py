"""Run serial native qualification, then assemble the exact public candidate."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.candidate_artifacts import REQUIRED_REPORTS, assemble
from tools.package_identity import extension_filename, file_record, source_identity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', type=Path, required=True)
    parser.add_argument('--site', type=Path, default=ROOT / 'outputs/science')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/candidate-ci')
    parser.add_argument('--run-id', type=int, required=True)
    parser.add_argument('--channel', choices=('alpha', 'preview'), default='alpha')
    args = parser.parse_args()
    commit, _ = source_identity()
    import numpy as np
    lock = json.loads((ROOT / 'dependencies.lock.json').read_text(encoding='utf-8'))
    if '.'.join(str(v) for v in sys.version_info[:2]) != lock['target']['python'] or np.__version__ != lock['host_provided']['numpy']:
        raise RuntimeError('Run candidate qualification with the locked Blender Python and host NumPy')
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    reports, logs = out / 'reports', out / 'logs'
    reports.mkdir()
    logs.mkdir()
    env = os.environ.copy()
    profile = out / 'profile'
    for key, path in {
            'BLENDER_USER_RESOURCES': profile, 'BLENDER_USER_CONFIG': profile / 'config',
            'BLENDER_USER_EXTENSIONS': profile / 'extensions', 'BLENDER_USER_DATAFILES': profile / 'datafiles',
            'BLENDER_USER_CACHE': out / 'cache', 'TEMP': out / 'process-temp', 'TMP': out / 'process-temp'}.items():
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    env.update(PYTHONNOUSERSITE='1', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    commands = []

    def run(name, command):
        log = logs / (name + '.log')
        with log.open('wb') as stream:
            process = subprocess.run([str(value) for value in command], cwd=ROOT, env=env,
                                     stdout=stream, stderr=subprocess.STDOUT)
        commands.append(dict(name=name, command=[str(v) for v in command], exit_code=process.returncode,
                             log=log.relative_to(out).as_posix(), log_sha256=file_record(log)['sha256']))
        (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
        if process.returncode:
            raise RuntimeError(f'{name} failed with exit code {process.returncode}; see {log}')

    def fresh_report(source, name, candidate=None):
        data = json.loads(Path(source).read_text(encoding='utf-8'))
        if data.get('status') != 'Passed' or data.get('source_commit') != commit:
            raise ValueError(name + ': missing current Passed report')
        if candidate is not None:
            if data.get('candidate_sha256') not in (None, candidate):
                raise ValueError(name + ': mismatched candidate report')
            data['candidate_sha256'] = candidate
        (reports / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        return data

    def native(name, scripts, script_args=(), blend=None):
        command = [args.blender, '--background']
        command.extend([blend] if blend else ['--factory-startup'])
        command.extend(['--offline-mode', '--disable-autoexec', '--python-exit-code', '1'])
        for script in scripts:
            command.extend(['--python', ROOT / 'tools' / script])
        if script_args:
            command.extend(['--', *script_args])
        run(name, command)

    run('stdlib', [sys.executable, '-I', '-S', '-B', ROOT / 'tools/run_stdlib_tests.py',
                   '--output', reports / 'stdlib.json'])
    run('public-science', [sys.executable, '-I', '-B', ROOT / 'tools/run_science_tests.py',
                           '--site', args.site, '--suite', 'public-core', '--output', reports / 'public-science.json'])
    run('build-extension', [sys.executable, '-B', ROOT / 'tools/build_extension.py',
                            '--blender', args.blender, '--output-dir', out / 'dist'])
    candidate = out / 'dist' / extension_filename()
    candidate_sha = file_record(candidate)['sha256']
    helper_report = reports / 'node-helpers.json'
    native('node-helpers', ['verify_node_helpers.py'], ['--report', helper_report])
    fresh_report(helper_report, 'node-helpers')
    assets_report = reports / 'node-assets.json'
    qa = out / 'installed-qualification'
    native('extension-install', ['verify_extension.py'],
           ['--candidate', candidate, '--output-dir', qa])
    initial = fresh_report(qa / 'extension.json', 'extension-install', candidate_sha)
    native('node-assets', ['verify_node_assets.py'], ['--report', assets_report], qa / 'mo8.blend')
    fresh_report(assets_report, 'node-assets', candidate_sha)
    native('cold-original', ['verify_extension.py'],
           ['--candidate', candidate, '--output-dir', qa, '--reopen'], qa / 'mo8.blend')
    fresh_report(qa / 'extension.json', 'cold-original', candidate_sha)
    native('cold-moved', ['verify_extension.py'],
           ['--candidate', candidate, '--output-dir', qa, '--reopen'], initial['relocated_blend'])
    fresh_report(qa / 'extension.json', 'cold-moved', candidate_sha)
    reproduction = out / 'public-reproduction'
    reproduction_report = reports / 'reproduction.json'
    native('public-reproduction', ['verify_alpha_workflow.py'],
           ['--candidate', candidate, '--output-dir', reproduction, '--report', reproduction_report])
    first_reproduction = json.loads(reproduction_report.read_text(encoding='utf-8'))
    native('public-reproduction-cold', ['verify_alpha_workflow.py'],
           ['--candidate', candidate, '--output-dir', reproduction, '--report', reproduction_report, '--reopen'],
           first_reproduction['moved_blend'])
    run('sample-package', [sys.executable, '-B', ROOT / 'tools/candidate_artifacts.py', 'check-samples',
                           '--output', reports / 'sample-package.json'])
    index = dict(candidate_sha256=candidate_sha, source_commit=commit, checks={})
    for name in REQUIRED_REPORTS:
        if name != 'qualification':
            record = file_record(reports / (name + '.json'), out)
            index['checks'][name] = dict(path=record['path'], sha256=record['sha256'], candidate_sha256=candidate_sha)
    index_path = out / 'evidence-index.json'
    index_path.write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8')
    installed = profile / 'extensions/user_default/qcblender'
    run('qualification', [sys.executable, '-B', ROOT / 'tools/qualify_package.py', '--candidate', candidate,
                          '--evidence-index', index_path, '--installed-dir', installed,
                          '--output', reports / 'qualification.json'])
    result = assemble(candidate, ROOT / 'tests/data/distribution/qcblender-public-tutorial-samples-v2.zip',
                      reproduction, reports, out / 'artifact', args.run_id, args.channel)
    print(result['artifact_name'])


if __name__ == '__main__':
    main()
