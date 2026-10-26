import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { loadPublishedRelease, validatePublishedRelease } from './published-release.mjs';

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
function fixture() {
  const url = 'https://github.com/psiQAQ/QCBlender/releases/download/v0.1.0/';
  const extension = Buffer.from('synthetic extension'), tutorial = Buffer.from('synthetic tutorial');
  const index = Buffer.from(JSON.stringify({ version: 'v1', blocklist: [], data: [{
    id: 'qcblender', type: 'add-on', version: '0.1.0', platforms: ['windows-x64'],
    blender_version_min: '5.1.1', blender_version_max: '5.2.0', archive_size: extension.length,
    archive_hash: `sha256:${sha(extension)}`, archive_url: `${url}qcblender-0.1.0.zip`,
  }] }));
  const files = {};
  for (const [role, path, bytes] of [['extension', 'qcblender-0.1.0.zip', extension],
    ['tutorial', 'qcblender-tutorial-0.1.0.zip', tutorial], ['repository_index', 'index.json', index]]) {
    files[role] = { path, bytes: bytes.length, sha256: sha(bytes) };
  }
  const manifest = Buffer.from(JSON.stringify({ schema: 'qcblender.release.v1', version: '0.1.0',
    source_commit: 'a'.repeat(40), candidate_run_id: 42, platform: { os: 'windows', architecture: 'x64', blender: '5.1.1' }, files }));
  const contents = { 'qcblender-0.1.0.zip': extension, 'qcblender-tutorial-0.1.0.zip': tutorial,
    'index.json': index, 'release-manifest.json': manifest };
  const sums = Buffer.from(Object.entries(contents).map(([name, bytes]) => `${sha(bytes)}  ${name}\n`).join(''));
  contents['SHA256SUMS.txt'] = sums;
  const release = { tag_name: 'v0.1.0', draft: false, prerelease: true,
    assets: Object.entries(contents).map(([name, bytes]) => ({ name, size: bytes.length, digest: `sha256:${sha(bytes)}`,
      browser_download_url: url + name, state: 'uploaded' })) };
  return { release, manifest, index, sums, contents };
}

test('public release validates exact metadata and fixed URLs', () => {
  const f = fixture();
  const result = validatePublishedRelease(f.release, f.manifest, f.index, f.sums);
  assert.equal(result.index_url, 'https://notes.psiqaq.cn/QCBlender/index.json');
  assert.match(result.tutorial_download, /v0\.1\.0\/qcblender-tutorial-0\.1\.0\.zip$/);
});

test('draft, extra attachments and changed index bytes cannot become downloads', () => {
  for (const mutation of [
    (f) => { f.release.draft = true; },
    (f) => { f.release.assets.push({ name: 'private-report.zip' }); },
    (f) => { f.index = Buffer.from('{}'); },
    (f) => { f.release.assets[0].browser_download_url = 'https://example.com/latest.zip'; },
  ]) {
    const f = fixture(); mutation(f);
    assert.throws(() => validatePublishedRelease(f.release, f.manifest, f.index, f.sums));
  }
});

test('unpublished release is allowed only if no public index exists', async () => {
  const missing = async () => new Response('', { status: 404 });
  assert.equal(await loadPublishedRelease({ fetcher: missing, offline: false, requiredTag: '' }), null);
  await assert.rejects(loadPublishedRelease({ fetcher: missing, offline: false, requiredTag: 'v0.1.0' }), /Cannot resolve/);
  let count = 0;
  const deployed = async () => new Response('', { status: ++count === 1 ? 404 : 200 });
  await assert.rejects(loadPublishedRelease({ fetcher: deployed, offline: false, requiredTag: '' }), /refusing to erase/);
});

test('normal deployments retrieve the same versioned public index', async () => {
  const f = fixture();
  const fetcher = async (url) => url.includes('api.github.com')
    ? Response.json(f.release) : new Response(f.contents[url.split('/').at(-1)]);
  const result = await loadPublishedRelease({ fetcher, offline: false, requiredTag: '' });
  assert.deepEqual(result.indexBytes, f.index);
});
