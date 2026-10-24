import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { deploymentViolations, loadPublicSamples } from './public-samples.mjs';
import { mapping, rewriteTutorialUrl, tutorialImageSource } from './tutorial-links.mjs';

test('active licensed P02 is routed while old and unlisted P02 stay blocked', () => {
  const selected = loadPublicSamples();
  const member = selected.samples.find((entry) => entry.path.includes('/P02/')).path;
  assert.ok(member.startsWith(`${selected.archive.dataset_id}/P02/`));
  const asset = `tutorial-assets/shared/data/public/${member}`;
  assert.equal(rewriteTutorialUrl(`../shared/data/public/${member}`, 'validation/human/SOP.md', { tracked: new Set() }), `/QCBlender/${asset}`);
  assert.deepEqual(deploymentViolations([asset], new Map([[asset, 'hash']]), selected), []);
  for (const file of ['P02/private.out', 'tutorial-assets/shared/data/public/P02/private.out', `tutorial-assets/shared/data/public/${selected.archive.dataset_id}/P02/unlisted.out`]) {
    assert.ok(deploymentViolations([file], new Map([[file, 'pretend-allowlist']]), selected).length);
  }
  assert.throws(() => rewriteTutorialUrl('../shared/data/public/P02/private.out', 'validation/human/SOP.md', {
    tracked: new Set(), members: new Set(['P02/private.out']),
  }), /licensed ZIP allowlist/);
});

test('historical render links are copied as assets without becoming embedded figures', () => {
  const source = 'validation/human/SOP.md';
  assert.equal(tutorialImageSource('renders/P01-mo.png', source), 'validation/human/renders/P01-mo.png');
  assert.equal(tutorialImageSource('../screenshots/view.png#detail', 'validation/human/topics/02-cube.md'), 'validation/human/screenshots/view.png');
  assert.equal(tutorialImageSource('https://example.test/image.png', source), null);
  assert.equal(rewriteTutorialUrl('renders/P01-mo.png', source, {
    tracked: new Set(['validation/human/renders/P01-mo.png']),
  }), '/QCBlender/tutorial-assets/human/renders/P01-mo.png');
});

test('owned Gaussian log topic and active manifest are part of website mapping', () => {
  assert.equal(mapping.publicSamples.delivery, 'validation/agent/acceptance/tutorial-sample-delivery.json');
  assert.ok(mapping.pages.some((page) => page.source === 'validation/human/topics/12-gaussian-log.md'));
  assert.equal(rewriteTutorialUrl(`../shared/data/public/${loadPublicSamples().manifest_member}`, 'validation/human/SOP.md', {
    tracked: new Set(),
  }), '/QCBlender/tutorial-assets/shared/data/public/tutorial-samples.json');
});

test('current SOP ships native 53 frames and keeps the 69-frame v3 identity', () => {
  const delivery = JSON.parse(readFileSync(new URL('../../validation/agent/acceptance/tutorial-sample-delivery.json', import.meta.url)));
  const manifest = JSON.parse(readFileSync(new URL(`../../${delivery.manifest.path}`, import.meta.url)));
  const path = manifest.files['P04-steps.csv'].expected;
  assert.equal(path.steps, 53);
  assert.equal(path.irc_report.ts_step, 27);
  assert.match(path.irc_report.path_integrator, /Gaussian native GS2/);
  assert.equal(manifest.files['P04-mayer.csv'].expected.orders.flat().length, 318);
  assert.equal(delivery.historical_datasets['gaussian-v1'].package.sha256, 'c228f414c73f9d56ba264573d8f3526c96d1ebcf340030201e5acf5020a3369b');
});
