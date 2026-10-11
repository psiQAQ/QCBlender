"""Check tutorial resources and links, optionally in a detached public copy."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[3]
PUBLIC_PARTS = ('human', 'shared/data/public', 'shared/install')
IMAGE_SUFFIXES = ('.png', '.jpg', '.jpeg', '.webp')
HUMAN_DIRECTORIES = ('topics', 'screenshots', 'renders')
LINK = re.compile(r'(!?)\[[^\]]*\]\((<[^>]*>|[^)\s]+)(?:\s+"[^"]*")?\)')
FORBIDDEN = re.compile(r'SHA[ -]?256|Get-FileHash|RECORD-TEMPLATE|\bPassed\b|\bFailed\b|\bNot Run\b|填写[^\n。]*结果|签署', re.I)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def slug(text):
    return re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')


def anchors(path):
    text = path.read_text(encoding='utf-8')
    explicit = re.findall(r'<a\s+id=["\']([^"\']+)["\']', text)
    headings = [slug(value) for value in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M)]
    return set(explicit + headings)


def safe_files(directory):
    """List files without following an unexpected link in the packaged tree."""
    if directory.is_symlink() or directory.is_junction():
        raise ValueError(f'Linked directory is not a portable resource: {directory}')
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.is_symlink() or path.is_junction():
            raise ValueError(f'Linked resource is not portable: {path}')
        if path.is_dir():
            yield from safe_files(path)
        elif path.is_file():
            yield path


def require_plain_path(path, boundary):
    """Reject linked ancestors before resolving a write destination."""
    absolute = path.absolute()
    boundary = boundary.absolute()
    if not absolute.is_relative_to(boundary):
        raise ValueError(f'Path leaves expected directory: {path}')
    for part in (absolute, *absolute.parents):
        if part.is_symlink() or part.is_junction():
            raise ValueError(f'Linked path is not allowed: {part}')
        if part == boundary:
            break
    if not absolute.resolve().is_relative_to(boundary.resolve()):
        raise ValueError(f'Path leaves expected directory: {path}')
    return absolute.resolve()


def check_materials(materials, install):
    public = materials / 'shared/data/public'
    manifest = json.loads((public / 'tutorial-samples.json').read_text(encoding='utf-8'))
    expected = set()
    for row in manifest['files'].values():
        if row['distribution'] != 'included':
            continue
        path = public / row['archive_path']
        if not path.resolve().is_relative_to(public.resolve()):
            raise ValueError(f'Public input escapes directory: {row["archive_path"]}')
        if row['license'] != 'CC-BY-4.0' or digest(path) != row['sha256']:
            raise ValueError(f'Public input identity or license differs: {path}')
        if path.stat().st_size != row['bytes']:
            raise ValueError(f'Public input size differs: {path}')
        expected.add(path.relative_to(public).as_posix())
    support = {'LICENSE', 'NOTICE.md', 'README.md', 'tutorial-samples.json', 'source.json'}
    actual = {path.relative_to(public).as_posix() for path in safe_files(public)}
    extras = actual - expected - support
    if extras:
        raise ValueError(f'Unexpected public resources: {sorted(extras)}')
    for name in ('LICENSE', 'NOTICE.md'):
        if not (public / name).is_file():
            raise FileNotFoundError(public / name)
    for name, column in (('steps.csv', 'fchk'), ('mayer-pyscf.csv', 'mayer_output')):
        path = public / 'P04' / name
        with path.open(encoding='utf-8', newline='') as stream:
            for row in csv.DictReader(stream):
                target = (path.parent / row[column]).resolve()
                if not target.is_relative_to(path.parent.resolve()) or not target.is_file():
                    raise ValueError(f'Broken P04 relative input: {path}: {row[column]}')
    candidate = materials / 'shared/install' / Path(install['path']).name
    if candidate.stat().st_size != install['bytes'] or digest(candidate) != install['sha256']:
        raise ValueError(f'Installer differs from selected candidate: {candidate}')
    with zipfile.ZipFile(candidate) as archive:
        if archive.testzip() is not None:
            raise ValueError('Installer CRC check failed')
        if 'blender_manifest.toml' not in archive.namelist():
            raise ValueError('Installer is missing its Blender manifest')
    installers = sorted(path.name for path in candidate.parent.glob('*.zip'))
    if installers != [candidate.name]:
        raise ValueError(f'Installation directory must contain one current ZIP: {installers}')
    return {'public_inputs': len(expected), 'p04_relative_files': 'Passed',
            'public_members': sorted(actual), 'installer': candidate.name}


def human_resources(human):
    """Reject work files before the complete human tree can be copied publicly."""
    files = list(safe_files(human))
    for path in sorted(human.rglob('*')):
        relative = path.relative_to(human)
        if path.is_dir() and relative.as_posix() not in HUMAN_DIRECTORIES:
            raise ValueError(f'Unexpected human directory: {relative.as_posix()}')
    images = set()
    for path in files:
        relative = path.relative_to(human)
        if relative.as_posix() in ('SOP.md', 'screenshots/.gitkeep', 'renders/.gitkeep') or (
                len(relative.parts) == 2 and relative.parts[0] == 'topics' and path.suffix == '.md'):
            continue
        elif (len(relative.parts) == 2 and relative.parts[0] in ('screenshots', 'renders')
              and path.suffix.lower() in IMAGE_SUFFIXES):
            images.add(path)
        else:
            raise ValueError(f'Unexpected human resource: {relative.as_posix()}')
    return images


def check_documents(materials, require_images=False):
    materials = materials.resolve()
    human = materials / 'human'
    supplied_images = human_resources(human)
    allowed = [(materials / part).resolve() for part in PUBLIC_PARTS]
    files = [p for part in PUBLIC_PARTS for p in safe_files(materials / part) if p.suffix == '.md']
    image_roots = [(human / name).resolve() for name in ('screenshots', 'renders')]
    image_slots = {}
    result = {'markdown_files': len(files), 'links': 0, 'numbered_operations': 0,
              'require_images': require_images}
    for path in files:
        text = path.read_text(encoding='utf-8')
        if path.is_relative_to(human):
            if FORBIDDEN.search(text):
                raise ValueError(f'Human document contains a technical result workflow: {path}')
            if re.search(r'\b[A-Za-z]:[\\/]|tests/data/|outputs/', text):
                raise ValueError(f'Human document depends on a repository or absolute path: {path}')
            result['numbered_operations'] += len(re.findall(r'^\d+\. ', text, re.M))
            for raw in re.findall(r'`(shared/data/public/[^`]+|shared/install/[^`]+)`', text):
                target = materials / raw
                if not target.exists():
                    raise FileNotFoundError(f'Tutorial input path does not exist: {raw} ({path})')
        for is_image, raw in LINK.findall(text):
            link = raw.strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', link):
                if is_image or not link.startswith(('https://', 'http://', 'mailto:')):
                    raise ValueError(f'Nonportable document reference: {path}: {link}')
                continue
            address, _, fragment = link.partition('#')
            target = (path.parent / address).resolve() if address else path.resolve()
            if not any(target.is_relative_to(root) for root in allowed):
                raise ValueError(f'Link leaves public package: {path}: {link}')
            result['links'] += 1
            if is_image:
                if target.parent not in image_roots or target.suffix.lower() not in IMAGE_SUFFIXES:
                    raise ValueError(f'Unsupported tutorial image path: {path}: {link}')
                image_slots[target] = {'path': target.relative_to(materials).as_posix(),
                                       'present': target.is_file()}
                continue
            if not target.exists():
                raise FileNotFoundError(f'Broken public link: {path}: {link}')
            if fragment and target.suffix == '.md' and fragment not in anchors(target):
                raise ValueError(f'Broken anchor: {path}: {link}')
    extra_images = supplied_images - image_slots.keys()
    if extra_images:
        raise ValueError('Unreferenced human images: ' + ', '.join(
            path.relative_to(human).as_posix() for path in sorted(extra_images)))
    result['image_slots'] = [image_slots[path] for path in sorted(image_slots)]
    result['images_supplied'] = sum(row['present'] for row in result['image_slots'])
    result['images_missing'] = [row['path'] for row in result['image_slots'] if not row['present']]
    # Keep the screenshot-only fields for existing report readers.
    result['screenshot_slots'] = [row for row in result['image_slots']
                                  if row['path'].startswith('human/screenshots/')]
    result['screenshots_supplied'] = sum(row['present'] for row in result['screenshot_slots'])
    if require_images and result['images_missing']:
        raise FileNotFoundError('Missing required tutorial images: ' + ', '.join(result['images_missing']))
    result['human_execution'] = 'Not Run'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--require-images', action='store_true',
                        help='Require every referenced screenshot and render; default allows image placeholders')
    parser.add_argument('--portable-dir', type=Path,
                        help='New directory beneath validation/work; only public roots are copied')
    args = parser.parse_args()
    root = args.root.resolve()
    materials = root / 'validation'
    report_path = require_plain_path(args.report, materials / 'agent/reports')
    if report_path.exists():
        raise FileExistsError(f'Choose an unused report path: {report_path}')
    for part in PUBLIC_PARTS:
        require_plain_path(materials / part, materials)
    install = json.loads((materials / 'agent/current-install.json').read_text(encoding='utf-8'))
    report = {'status': 'Failed', 'source_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(), 'candidate_sha256': install['sha256']}
    try:
        report['resources'] = check_materials(materials, install)
        report['documents'] = check_documents(materials, require_images=args.require_images)
        frozen = root / 'validation/agent/v1-acceptance/tutorial-samples.json'
        if (materials / 'shared/data/public/tutorial-samples.json').read_bytes() != frozen.read_bytes():
            raise ValueError('Public source manifest differs from the frozen original')
        if args.portable_dir is not None:
            detached = require_plain_path(args.portable_dir, materials / 'work')
            work = (materials / 'work').resolve()
            if not detached.is_relative_to(work) or detached == work or detached.exists():
                raise ValueError('Portable verification requires a new directory under validation/work')
            for part in PUBLIC_PARTS:
                shutil.copytree(materials / part, detached / part)
            report['portable'] = {'root': str(detached), 'resources': check_materials(detached, install),
                                  'documents': check_documents(detached, require_images=args.require_images)}
        report['status'] = 'Passed'
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('status', 'source_commit')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
