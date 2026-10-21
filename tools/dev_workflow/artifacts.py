"""Reuse existing package/build helpers and archive merged worktrees normally."""
from pathlib import Path
import shutil
import subprocess
import zipfile
from .records import digest, read, write


def prepare_build(repo, candidate):
    """Copy already installed locked wheels into this checkout's build directory."""
    wheels = repo/'modules/wheels'
    wheels.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate) as archive:
        backend = archive.read('backend-wheel.json')
        import json
        packages = read(repo/'dependencies.lock.json')['packages'] + [json.loads(backend)]
        for package in packages:
            content = archive.read('wheels/'+package['filename'])
            import hashlib
            if hashlib.sha256(content).hexdigest() != package['sha256']:
                raise ValueError('Existing wheel differs from current lock: '+package['filename'])
            target = wheels/package['filename']
            if not target.exists() or digest(target) != package['sha256']:
                target.write_bytes(content)
        (repo/'modules/backend-wheel.json').write_bytes(backend)
    return len(packages)


def compare_candidate(repo, candidate):
    with zipfile.ZipFile(candidate) as archive:
        sources = {p.relative_to(repo/'qcblender').as_posix():digest(p) for p in (repo/'qcblender').rglob('*.py')}
        for name in sources:
            if archive.read(name) != (repo/'qcblender'/name).read_bytes():
                raise ValueError('Candidate differs from source: '+name)
    return dict(status='Passed', path=str(candidate), sha256=digest(candidate), bytes=candidate.stat().st_size,
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(), source_files=sources)


def backup_install(directory, output):
    directory, output = Path(directory).resolve(), Path(output).resolve()
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(directory.rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts:
                archive.write(file, file.relative_to(directory).as_posix())
    return dict(path=str(output), sha256=digest(output), installation=str(directory))


def finish(repo, tree, directory, date, apply=False):
    repo, tree, directory = repo.resolve(), Path(tree).resolve(), Path(directory).resolve()
    if tree.parent != repo/'.worktrees' or tree.is_symlink() or directory.is_relative_to(tree):
        raise ValueError('Archive only a direct repo/.worktrees child; store evidence outside that checkout')
    def git(*args, cwd=repo):
        return subprocess.check_output(['git',*args],cwd=cwd,text=True,stderr=subprocess.STDOUT).strip()
    if git('status','--porcelain',cwd=tree):
        raise ValueError('Commit task changes before archiving')
    commit, branch = git('rev-parse','HEAD',cwd=tree), git('branch','--show-current',cwd=tree)
    if not branch or branch=='main':
        raise ValueError('Expected a named task branch')
    git('merge-base','--is-ancestor',commit,'main')
    names=git('ls-files','--others','--ignored','--exclude-standard','-z',cwd=tree).split('\0')
    files=[]
    for name in sorted(filter(None,names)):
        file=tree/name
        if file.is_symlink() or not file.resolve().is_relative_to(tree):
            raise ValueError('Preserve linked files manually: '+name)
        files.append(dict(path=name,sha256=digest(file),bytes=file.stat().st_size))
    plan=dict(status='Passed',worktree=str(tree),branch=branch,commit=commit,files=files,
              tag=f'archive/{date}/{branch}',action='preserve ignored files, normal worktree remove, branch -d')
    write(directory/(tree.name+'-retention.json'),plan)
    if not apply:
        return dict(status='Passed',mode='plan',files=len(files),report=str(directory/(tree.name+'-retention.json')))
    archive_path=directory/(tree.name+'-ignored.zip')
    with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for item in files:
            file=tree/item['path']
            if digest(file)!=item['sha256']:
                raise ValueError('File changed during archive: '+item['path'])
            archive.write(file,item['path'])
    import hashlib
    with zipfile.ZipFile(archive_path) as archive:
        for item in files:
            if hashlib.sha256(archive.read(item['path'])).hexdigest()!=item['sha256']:
                raise ValueError('Archive verification failed')
    existing=subprocess.run(['git','rev-parse','--verify',plan['tag']+'^{commit}'],cwd=repo,text=True,capture_output=True)
    if existing.returncode==0:
        if existing.stdout.strip()!=commit:
            raise ValueError('Archive tag already identifies a different commit')
    else:
        git('tag','-a',plan['tag'],commit,'-m','Local task archive; evidence: '+str(directory.relative_to(repo)))
    git('worktree','remove',str(tree))
    git('branch','-d',branch)
    plan.update(archive=str(archive_path),archive_sha256=digest(archive_path),removed=not tree.exists())
    write(directory/(tree.name+'-archive.json'),plan)
    return dict(status='Passed',report=str(directory/(tree.name+'-archive.json')),tag=plan['tag'])
