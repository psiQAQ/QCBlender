import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, mkdir, mkdtemp, rm } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { generatedPath, mapping, repositoryRoot, rewriteTutorialUrl, remarkTutorialLinks, websiteRoot } from './tutorial-links.mjs';
import { deploymentViolations, internalTarget } from './verify-site.mjs';
import { sha256 } from './prepare-docs.mjs';

test('cross-directory links retain Chinese fragments and project base', () => {
  assert.equal(rewriteTutorialUrl('../SOP.md#保存工程', 'validation/human/topics/02-cube.md'), '/QCBlender/docs/getting-started/#保存工程');
  assert.equal(rewriteTutorialUrl('03-density-esp.md#presets', 'validation/human/topics/02-cube.md'), '/QCBlender/docs/topics/03-density-esp/#presets');
  assert.equal(rewriteTutorialUrl('VALIDATION.md#scope', 'docs/USER_GUIDE.md'), 'https://github.com/psiQAQ/QCBlender/blob/main/docs/VALIDATION.md#scope');
  assert.deepEqual(internalTarget('../03-density-esp/#电子密度', '/QCBlender/docs/topics/02-cube/'), { relative: 'docs/topics/03-density-esp/', hash: '电子密度' });
  assert.throws(() => internalTarget('/docs/', '/QCBlender/'), /drops project base/);
});

test('AST rewrite changes links and definitions while preserving inline and fenced code', async () => {
  const source = mapping.pages.find((page) => page.source === 'validation/human/SOP.md');
  const renderer = await createMarkdownProcessor({ remarkPlugins: [remarkTutorialLinks], syntaxHighlight: false, smartypants: false });
  const result = await renderer.render('[正文](topics/02-cube.md#overlay)\n\n[引用][cube]\n\n[cube]: topics/02-cube.md#overlay\n\n`topics/02-cube.md#overlay`\n\n```text\n[代码](topics/02-cube.md#overlay)\n```', { fileURL: pathToFileURL(generatedPath(source)) });
  assert.equal((result.code.match(/href="\/QCBlender\/docs\/topics\/02-cube\/#overlay"/g) ?? []).length, 2);
  assert.match(result.code, /<code>topics\/02-cube\.md#overlay<\/code>/);
  assert.match(result.code, /\[代码\]\(topics\/02-cube\.md#overlay\)/);
});

test('local candidates route to explicit status and private data stays unavailable', () => {
  assert.equal(rewriteTutorialUrl('../shared/install/qcblender-0.1.0.zip', 'validation/human/SOP.md'), '/QCBlender/downloads/');
  assert.equal(rewriteTutorialUrl('../validation/agent/LOCAL-CASES.md', 'docs/USER_GUIDE.md'), '/QCBlender/docs/#local-data');
  assert.equal(rewriteTutorialUrl('file:///D:/private/P02.log', 'docs/USER_GUIDE.md'), '/QCBlender/docs/#local-data');
  assert.throws(() => rewriteTutorialUrl('../shared/data/public/P02/private.log', 'validation/human/SOP.md', { tracked: new Set(), members: new Set() }), /absent from frozen ZIP/);
  assert.throws(() => rewriteTutorialUrl('../shared/data/unknown.xyz', 'validation/human/SOP.md', { tracked: new Set() }), /Unpublished tutorial link/);
});

test('frozen sample archive has the reviewed identity', async () => {
  const bytes = await readFile(path.join(repositoryRoot, mapping.publicSamples.source));
  assert.equal(sha256(bytes), mapping.publicSamples.sha256);
});

test('ZIP extractor rejects identity drift and traversal before writing member data', async () => {
  await mkdir(path.join(websiteRoot, 'reports'), { recursive: true });
  const root = await mkdtemp(path.join(websiteRoot, 'reports/test-zip-'));
  try {
    const archive = path.join(root, 'bad.zip');
    const make = spawnSync(process.env.PYTHON ?? 'python', ['-c', "import sys,zipfile; z=zipfile.ZipFile(sys.argv[1],'w'); z.writestr('../P02/private.log','private'); z.close()", archive], { encoding: 'utf8' });
    assert.equal(make.status, 0, make.stderr);
    const bytes = await readFile(archive);
    const extractor = path.join(websiteRoot, 'scripts/extract-public-samples.py');
    const run = (hash) => spawnSync(process.env.PYTHON ?? 'python', [extractor, archive, path.join(root, 'extracted'), hash, '1'], { encoding: 'utf8' });
    const identity = run('0'.repeat(64));
    assert.notEqual(identity.status, 0);
    assert.match(identity.stderr, /identity mismatch/);
    const traversal = run(sha256(bytes));
    assert.notEqual(traversal.status, 0);
    assert.match(traversal.stderr, /Forbidden public ZIP member/);
  } finally {
    await rm(root, { recursive: true });
  }
});

test('deployment check rejects local data, projects, stale assets and install ZIPs', () => {
  const publicZip = `downloads/${mapping.publicSamples.download}`;
  assert.deepEqual(deploymentViolations([publicZip, 'downloads/index.html', '_astro/app.js'], new Map([[publicZip, 'hash']])), []);
  for (const file of ['P02/input.log', 'tutorial-assets/shared/data/local/P02.log', 'renders/current.blend', 'renders/current.blend1', 'renders/current.qcdata/data.bin', 'downloads/qcblender-0.1.0.zip', 'downloads/unreviewed.html', 'unexpected/candidate.zip', 'tutorial-assets/old.png']) {
    assert.ok(deploymentViolations([file], new Map()).length, file);
  }
});
