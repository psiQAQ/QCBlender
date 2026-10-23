import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'parse5';
import { generatedPath, mapping, repositoryRoot, websiteRoot } from './tutorial-links.mjs';
import { sha256, sourceMetrics } from './prepare-docs.mjs';
import { deploymentViolations, loadPublicSamples } from './public-samples.mjs';
export { deploymentViolations } from './public-samples.mjs';

const origin = 'https://notes.psiqaq.cn';
export function internalTarget(value, fromRoute) {
  if (!value || /^(?:data:|mailto:|tel:|javascript:)/i.test(value)) return null;
  const url = new URL(value, origin + fromRoute);
  if (url.origin !== origin) return null;
  if (!(url.pathname === mapping.base || url.pathname.startsWith(mapping.base + '/'))) {
    throw new Error(`Internal URL drops project base: ${value} (from ${fromRoute})`);
  }
  const relative = decodeURIComponent(url.pathname.slice(mapping.base.length)).replace(/^\//, '');
  if (relative.split('/').includes('..')) throw new Error(`Internal URL escapes dist: ${value}`);
  return { relative, hash: decodeURIComponent(url.hash.slice(1)) };
}

export async function filesBelow(directory, prefix = '') {
  const entries = await readdir(directory, { withFileTypes: true });
  const result = [];
  for (const entry of entries) {
    if (entry.isSymbolicLink()) throw new Error(`Symlink in deployed output: ${prefix}${entry.name}`);
    const relative = prefix + entry.name;
    if (entry.isDirectory()) result.push(...await filesBelow(path.join(directory, entry.name), relative + '/'));
    else result.push(relative);
  }
  return result.sort();
}

function visit(node, callback) {
  callback(node);
  for (const child of node.childNodes ?? []) visit(child, callback);
}
const attributes = (node) => Object.fromEntries((node.attrs ?? []).map(({ name, value }) => [name, value]));
function textOf(node) {
  return (node.value ?? '') + (node.childNodes ?? []).map(textOf).join('');
}

export async function verifySite(dist = path.join(websiteRoot, 'dist')) {
  const files = await filesBelow(dist);
  const fileSet = new Set(files);
  const report = JSON.parse(await readFile(path.join(websiteRoot, 'reports/tutorial-manifest.json'), 'utf8'));
  const selected = loadPublicSamples();
  const publicSamples = selected.archive;
  const errors = [];
  const require = (condition, message) => { if (!condition) errors.push(message); };
  const html = new Map();
  for (const file of files.filter((entry) => entry.endsWith('.html'))) {
    const content = await readFile(path.join(dist, file), 'utf8');
    const tree = parse(content);
    const ids = new Set();
    const references = [];
    let article;
    visit(tree, (node) => {
      const attrs = attributes(node);
      if (attrs.id) ids.add(attrs.id);
      if ((attrs.class ?? '').split(/\s+/).includes('sl-markdown-content')) article = node;
      for (const key of ['href', 'src', 'poster']) if (attrs[key]) references.push(attrs[key]);
      if (attrs.srcset) references.push(...attrs.srcset.split(',').map((part) => part.trim().split(/\s+/)[0]));
    });
    html.set(file, { ids, references, article, content });
  }
  let links = 0;
  for (const [file, document] of html) {
    const route = `${mapping.base}/${file.replace(/index\.html$/, '')}`;
    for (const reference of document.references) {
      try {
        const target = internalTarget(reference, route);
        if (!target) continue;
        links++;
        const candidates = [target.relative, target.relative.replace(/\/$/, '') + '/index.html'];
        if (!target.relative) candidates.push('index.html');
        const found = candidates.find((entry) => fileSet.has(entry));
        require(found, `${file}: missing internal target ${reference}`);
        if (found && target.hash && html.has(found)) require(html.get(found).ids.has(target.hash), `${file}: missing anchor ${reference}`);
      } catch (error) { errors.push(`${file}: ${error.message}`); }
    }
  }
  require(JSON.stringify(report.samples) === JSON.stringify(selected.samples), 'Prepared sample allowlist differs from the active licensed package');
  require(JSON.stringify(report.archive) === JSON.stringify(publicSamples), 'Prepared archive differs from the active delivery');
  const expectedSources = mapping.pages.filter((page) => page.source).map((page) => page.source).sort();
  require(JSON.stringify(report.pages.map((page) => page.source).sort()) === JSON.stringify(expectedSources), 'Prepared tutorial page inventory differs from mapping');
  const totals = { steps: 0, details: 0, images: 0 };
  for (const page of report.pages) {
    const source = await readFile(path.join(repositoryRoot, page.source));
    require(sha256(source) === page.sha256, `Source changed after prepare: ${page.source}`);
    const expected = sourceMetrics(source.toString('utf8'));
    const pageMapping = mapping.pages.find((entry) => entry.source === page.source);
    const generated = await readFile(generatedPath(pageMapping), 'utf8');
    const originalBody = source.toString('utf8').replace(/^#[^\r\n]*(?:\r?\n)?/, '');
    require(generated.endsWith(originalBody), `Generated tutorial body differs from canonical source: ${page.source}`);
    const document = html.get(`${page.slug}/index.html`);
    require(document, `Missing tutorial page ${page.slug}`);
    if (!document) continue;
    require(document.article, `Missing tutorial content container: ${page.slug}`);
    const counts = { steps: 0, details: 0, images: 0 };
    if (document.article) visit(document.article, (node) => {
      if (node.tagName === 'details') counts.details++;
      if (node.tagName === 'img') counts.images++;
      if (node.tagName === 'h3' && /^\d+\.\s/.test(textOf(node))) counts.steps++;
    });
    for (const key of Object.keys(totals)) {
      require(counts[key] === expected[key], `${page.slug}: ${key} ${counts[key]} != source ${expected[key]}`);
      totals[key] += counts[key];
    }
    for (const anchor of [page.originalTitleAnchor, ...expected.explicitAnchors]) {
      require(document.ids.has(anchor), `${page.slug}: lost source anchor ${anchor}`);
    }
    const h1Count = (document.content.match(/<h1(?:\s|>)/g) ?? []).length;
    require(h1Count === 1, `${page.slug}: expected one page H1, got ${h1Count}`);
  }
  require(totals.steps === 98 && totals.images === 75 && totals.details === 110,
    `Tutorial inventory changed: ${JSON.stringify(totals)}`);

  const permittedAssets = new Map(report.images.map((entry) => [entry.path, entry.sha256]));
  for (const sample of report.samples) permittedAssets.set(`tutorial-assets/shared/data/public/${sample.path}`, sample.sha256);
  permittedAssets.set(`downloads/${publicSamples.download}`, publicSamples.sha256);
  for (const [relative, expectedHash] of permittedAssets) {
    require(fileSet.has(relative), `Missing reviewed public asset ${relative}`);
    if (fileSet.has(relative)) require(sha256(await readFile(path.join(dist, relative))) === expectedHash, `Public asset bytes changed: ${relative}`);
  }
  errors.push(...deploymentViolations(files, permittedAssets, selected));
  const product = JSON.parse(await readFile(path.join(websiteRoot, 'src/data/generated-product.json'), 'utf8'));
  require(product.public_release === false && product.install_download === null, 'Local install candidate must not become a public download');
  require(product.samples_sha256 === publicSamples.sha256 && product.samples_name === publicSamples.download
    && product.samples_bytes === publicSamples.bytes && product.samples_dataset_id === publicSamples.dataset_id, 'Public samples identity drift');
  for (const route of ['downloads/index.html', 'en/downloads/index.html']) {
    require(html.has(route), `Missing download status page: ${route}`);
  }
  if (errors.length) throw new Error(`Site verification failed (${errors.length}):\n${errors.join('\n')}`);
  console.log(`Passed: ${html.size} HTML pages, ${links} internal links/assets; ${totals.steps} steps, ${totals.images} images, ${totals.details} details; ${permittedAssets.size} reviewed public files with matching SHA-256. Chinese search and visual interaction require browser verification.`);
  return { pages: html.size, links, ...totals };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await verifySite(process.argv[2]);
