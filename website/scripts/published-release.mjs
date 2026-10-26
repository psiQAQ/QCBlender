import { createHash } from 'node:crypto';

export const releaseTag = 'v0.1.0';
export const indexUrl = 'https://notes.psiqaq.cn/QCBlender/index.json';
const repository = 'https://github.com/psiQAQ/QCBlender';
const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');
const require = (condition, message) => { if (!condition) throw new Error(message); };

export function validatePublishedRelease(release, manifestBytes, indexBytes, sumsBytes, tag = releaseTag) {
  require(release.tag_name === tag && release.draft === false && release.prerelease === true, 'Release is not the requested public preview');
  const manifest = JSON.parse(manifestBytes);
  const index = JSON.parse(indexBytes);
  require(manifest.schema === 'qcblender.release.v1' && `v${manifest.version}` === tag, 'Published release manifest version mismatch');
  require(/^[a-f0-9]{40}$/.test(manifest.source_commit) && Number.isSafeInteger(manifest.candidate_run_id) && manifest.candidate_run_id > 0, 'Published candidate identity is missing');
  require(manifest.platform.os === 'windows' && manifest.platform.architecture === 'x64' && manifest.platform.blender === '5.1.1', 'Unsupported published platform');
  require(JSON.stringify(Object.keys(manifest.files).sort()) === JSON.stringify(['extension', 'repository_index', 'tutorial']), 'Unexpected published file roles');
  const expectedNames = {
    extension: `qcblender-${manifest.version}.zip`,
    tutorial: `qcblender-tutorial-${manifest.version}.zip`,
    repository_index: 'index.json',
  };
  const assets = new Map(release.assets.map((asset) => [asset.name, asset]));
  const names = [...Object.values(expectedNames), 'release-manifest.json', 'SHA256SUMS.txt'];
  require(assets.size === release.assets.length && assets.size === names.length && names.every((name) => assets.has(name)), 'Published asset inventory differs');
  const checksums = new Map();
  for (const line of sumsBytes.toString('utf8').trim().split(/\r?\n/)) {
    const match = /^([a-f0-9]{64})  ([A-Za-z0-9_.-]+)$/.exec(line);
    require(match && !checksums.has(match[2]), 'Invalid public checksum record');
    checksums.set(match[2], match[1]);
  }
  require(checksums.size === names.length - 1 && names.filter((name) => name !== 'SHA256SUMS.txt').every((name) => checksums.has(name)), 'Public checksum coverage differs');
  for (const [role, name] of Object.entries(expectedNames)) {
    const record = manifest.files[role];
    require(record.path === name && /^[a-f0-9]{64}$/.test(record.sha256) && Number.isSafeInteger(record.bytes) && record.bytes > 0, 'Invalid published asset record');
    require(checksums.get(name) === record.sha256 && assets.get(name).size === record.bytes, 'Published manifest/checksum/size mismatch');
  }
  const smallFiles = { 'release-manifest.json': manifestBytes, 'index.json': indexBytes, 'SHA256SUMS.txt': sumsBytes };
  for (const [name, asset] of assets) {
    const expectedUrl = `${repository}/releases/download/${tag}/${name}`;
    require(asset.browser_download_url === expectedUrl && asset.state === 'uploaded', 'Unexpected public asset URL or state');
    const sha = name === 'SHA256SUMS.txt' ? digest(sumsBytes) : checksums.get(name);
    require(asset.digest === `sha256:${sha}`, 'Public asset digest differs from GitHub');
    if (smallFiles[name]) require(digest(smallFiles[name]) === sha && smallFiles[name].length === asset.size, 'Downloaded public metadata bytes differ');
  }
  require(index.version === 'v1' && index.blocklist?.length === 0 && index.data?.length === 1, 'Unexpected extension repository contents');
  const entry = index.data[0];
  require(entry.id === 'qcblender' && entry.version === manifest.version && entry.type === 'add-on'
    && JSON.stringify(entry.platforms) === '["windows-x64"]'
    && entry.blender_version_min === '5.1.1' && entry.blender_version_max === '5.2.0', 'Published repository compatibility mismatch');
  require(entry.archive_url === assets.get(expectedNames.extension).browser_download_url
    && entry.archive_hash === `sha256:${manifest.files.extension.sha256}`
    && entry.archive_size === manifest.files.extension.bytes, 'Published repository points to a different extension');
  return { manifest, index, indexBytes, release_url: `${repository}/releases/tag/${tag}`,
    install_download: entry.archive_url, tutorial_download: assets.get(expectedNames.tutorial).browser_download_url,
    checksums_download: assets.get('SHA256SUMS.txt').browser_download_url, index_url: indexUrl };
}

export async function loadPublishedRelease({ fetcher = fetch, requiredTag = process.env.QCB_RELEASE_TAG, offline = process.env.QCB_RELEASE_OFFLINE === '1' } = {}) {
  require(!requiredTag || requiredTag === releaseTag, 'Unexpected requested release tag');
  // Offline mode is only for local source checks, never for a Pages deployment.
  if (offline) {
    require(!process.env.CI, 'CI must resolve the actual public release');
    return null;
  }
  const headers = { Accept: 'application/vnd.github+json', 'User-Agent': 'QCBlender-website' };
  if (process.env.GH_TOKEN) headers.Authorization = `Bearer ${process.env.GH_TOKEN}`;
  const response = await fetcher(`https://api.github.com/repos/psiQAQ/QCBlender/releases/tags/${releaseTag}`, { headers });
  if (response.status === 404 && !requiredTag) {
    const deployed = await fetcher(indexUrl);
    require(deployed.status === 404, 'Public release is unavailable but an index may already be deployed; refusing to erase it');
    return null;
  }
  require(response.ok, `Cannot resolve published release: HTTP ${response.status}`);
  const release = await response.json();
  require(release.draft === false, 'Draft releases must not become website downloads');
  const contents = [];
  for (const name of ['release-manifest.json', 'index.json', 'SHA256SUMS.txt']) {
    const result = await fetcher(`${repository}/releases/download/${releaseTag}/${name}`);
    require(result.ok, `Cannot download public metadata ${name}: HTTP ${result.status}`);
    contents.push(Buffer.from(await result.arrayBuffer()));
  }
  return validatePublishedRelease(release, ...contents);
}
