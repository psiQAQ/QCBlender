"""Query historical GUI evidence and select checks by the changed behavior."""
import subprocess
from .records import digest, read


def query(repo, term, limit=5):
    records = read(repo / 'validation/agent/acceptance/blender-operations.json')['records']
    matches = [r for r in records if term.lower() in (r['id']+' '+r.get('title', '')).lower()]
    matches.sort(key=lambda r: (r['id'] != term, r['id']))
    result = []
    for item in matches[:limit]:
        gui = item.get('gui_validation', {})
        fingerprints = item.get('implementation_fingerprints', {})
        changed = [name for name, old in fingerprints.items() if not (repo/name).is_file() or digest(repo/name) != old]
        result.append(dict(id=item['id'], title=item.get('title'), gui_status=gui.get('status'),
            scope=gui.get('validated_scope'), entry=gui.get('visible_entry'),
            execution=item.get('execution'), changed_implementation=changed,
            evidence=gui.get('reports', []), requires_current_assertions=True))
    return dict(status='Passed', matches=len(matches), returned=len(result), records=result)


def plan(repo, kind, base=None, modules=()):
    paths = subprocess.check_output(['git','diff','--name-only',base or 'HEAD'],cwd=repo,text=True).splitlines()
    paths = sorted(set(paths + subprocess.check_output(
        ['git','ls-files','--others','--exclude-standard'],cwd=repo,text=True).splitlines()))
    selected = list(modules)
    mappings = (
        (('annotation_geometry.py','annotations.py'), ('test_annotation_geometry','test_annotations_core')),
        (('annotation_inputs.py',), ('test_annotation_inputs',)),
        (('object_summary.py','source_browser.py'), ('test_object_summary','test_source_summary_cache')),
        (('viewport_context.py',), ('test_property_viewport_context',)),
        (('dev_workflow/',), ('test_dev_workflow', 'test_dev_workflow_ops')),
    )
    for needles, names in mappings:
        if any(any(n in p for n in needles) for p in paths):
            selected.extend(n for n in names if (repo/'tests'/(n+'.py')).exists())
    product = any(p.startswith('qcblender/') or p in ('dependencies.lock.json','science-sources.lock.json') for p in paths)
    return dict(status='Passed', kind=kind, changed_paths=paths, modules=sorted(set(selected)),
        checks=['git diff --check'] + (['selected modules'] if selected else []) +
               (['one affected native Blender case'] if kind in ('geometry','ui','install') else []) +
               (['affected UI entry via Computer Use'] if kind == 'ui' else []) +
               (['full rebuild','isolated install smoke','global install and original-project restore'] if product or kind=='install' else []),
        review_needed=kind!='docs' and not selected,
        rule='Selection is a proposal: identify the affected behavior. Reuse valid exact-input results; unchanged UI uses MCP. Release gates remain separate.')
