"""Skip native qualification only for explicitly unrelated changes; dispatch is always full."""
import json
import os
from pathlib import Path
import subprocess


LIGHT_FILES = frozenset(('README.md', 'README_zh.md', 'AGENTS.md', '.github/workflows/pages.yml'))
LIGHT_PREFIXES = ('website/', 'docs/agents/', '.agents/')


def requires_candidate(paths):
    # Empty or unknown changes must not be mistaken for a qualified candidate.
    return not paths or any(path not in LIGHT_FILES and not path.startswith(LIGHT_PREFIXES) for path in paths)


def changed_paths(event_name, event, root):
    if event_name == 'push':
        base, head = event.get('before'), event.get('after')
    elif event_name == 'pull_request':
        pr = event['pull_request']
        base, head = pr['base']['sha'], pr['head']['sha']
    else:
        return None, None
    if not base or not head or set(base) == {'0'}:
        return None, None
    try:
        if event_name == 'pull_request':
            base = subprocess.check_output(['git', 'merge-base', base, head], cwd=root, text=True).strip()
        # Treat renames as delete + add so moving a product file into docs cannot skip qualification.
        raw = subprocess.check_output(['git', 'diff', '--no-renames', '--name-only', '-z', base, head, '--'], cwd=root)
    except subprocess.CalledProcessError:
        return None, None
    return [path for path in raw.decode('utf-8').split('\0') if path], (base, head)


def main():
    root = Path(__file__).resolve().parents[1]
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    paths, commits = changed_paths(os.environ['GITHUB_EVENT_NAME'], event, root)
    full = requires_candidate(paths)
    if not full:
        subprocess.run(['git', 'diff', '--check', *commits, '--'], cwd=root, check=True)
    decision = 'Full candidate qualification' if full else 'Lightweight diff check; no candidate artifact'
    print(json.dumps({'full': full, 'decision': decision, 'changed_paths': paths}, ensure_ascii=False))
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
        stream.write(f'full={str(full).lower()}\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
        stream.write(f'### Candidate scope\n\n{decision}.\n\n'
                     'Manual dispatch and unclassified changes always require full qualification. '
                     'A lightweight run is not release evidence.\n')


if __name__ == '__main__':
    main()
