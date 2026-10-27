import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { generatedPath, mapping, repositoryRoot, rewriteTutorialUrl, remarkTutorialLinks } from './tutorial-links.mjs';
import { deploymentViolations, internalTarget } from './verify-site.mjs';
import { sha256, sourceMetrics } from './prepare-docs.mjs';
import { loadPublicSamples } from './public-samples.mjs';

test('tutorial steps and appendix explanations have separate inventories', () => {
  const metrics = sourceMetrics('### 1. Import\n### A1. Units\n### A2. Provenance\n<details>More</details>\n![figure](image.png)');
  assert.deepEqual(metrics, { steps: 1, details: 1, appendices: 2, images: 1, explicitAnchors: [] });
});

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
  assert.throws(() => rewriteTutorialUrl('../shared/data/public/P02/private.log', 'validation/human/SOP.md', { tracked: new Set(), members: new Set() }), /absent from licensed ZIP allowlist/);
  assert.throws(() => rewriteTutorialUrl('../shared/data/unknown.xyz', 'validation/human/SOP.md', { tracked: new Set() }), /Unpublished tutorial link/);
});

test('current sample archive has the active delivery identity', async () => {
  const selected = loadPublicSamples();
  const bytes = await readFile(path.join(repositoryRoot, selected.archive.source));
  assert.equal(sha256(bytes), selected.archive.sha256);
});

test('ZIP extractor enforces dataset identity, licenses and safe extraction', () => {
  const result = spawnSync(process.env.PYTHON ?? 'python', ['-m', 'unittest', 'discover', '-s', 'website/scripts', '-p', 'test_public_samples.py'], { cwd: repositoryRoot, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
});

test('deployment check rejects local data, projects, stale assets and install ZIPs', () => {
  const publicZip = `downloads/${loadPublicSamples().archive.download}`;
  assert.deepEqual(deploymentViolations([publicZip, 'downloads/index.html', '_astro/app.js'], new Map([[publicZip, 'hash']])), []);
  for (const file of ['P02/input.log', 'tutorial-assets/shared/data/local/P02.log', 'renders/current.blend', 'renders/current.blend1', 'renders/current.qcdata/data.bin', 'downloads/qcblender-0.1.0.zip', 'downloads/unreviewed.html', 'unexpected/candidate.zip', 'tutorial-assets/old.png']) {
    assert.ok(deploymentViolations([file], new Map()).length, file);
  }
});
