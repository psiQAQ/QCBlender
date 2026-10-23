import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadPublicSamples } from './public-samples.mjs';

export const websiteRoot = fileURLToPath(new URL('../', import.meta.url));
export const repositoryRoot = path.resolve(websiteRoot, '..');
export const mapping = JSON.parse(readFileSync(new URL('../tutorials.json', import.meta.url), 'utf8'));
export const posix = (value) => value.split(path.sep).join('/');
export const siteUrl = (route = '') => `${mapping.base}/${route.replace(/^\//, '')}`;
export const routeFor = (page) => `${page.slug}/`;
export const generatedPath = (page) => path.join(websiteRoot, 'src/content/docs', page.slug === 'docs' ? 'docs/index.md' : `${page.slug}.md`);

let trackedCache;
export function trackedFiles() {
  trackedCache ??= new Set(execFileSync('git', ['ls-files', '-z'], { cwd: repositoryRoot, encoding: 'utf8' }).split('\0').filter(Boolean));
  return trackedCache;
}

export function walk(tree, callback) {
  callback(tree);
  for (const child of tree.children ?? []) walk(child, callback);
}

export function tutorialImageSource(url, source) {
  if (!url || /^(?:[a-z][a-z\d+.-]*:|\/)/i.test(url)) return null;
  const target = decodeURIComponent(url.split(/[?#]/, 1)[0]);
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(source), target));
  return /^validation\/human\/(screenshots|renders)\/[^/]+\.(?:png|jpe?g|webp)$/i.test(resolved) ? resolved : null;
}

export function rewriteTutorialUrl(url, source, { tracked = trackedFiles(), members } = {}) {
  if (/^(?:file:|[a-z]:[\\/])/i.test(url)) return siteUrl('docs/#local-data');
  if (!url || url.startsWith('#') || /^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(url)) return url;
  if (url.startsWith(`${mapping.base}/`)) return url;
  if (url.startsWith('/')) throw new Error(`Root-relative tutorial URL is not source-relative: ${url}`);
  const separator = url.search(/[?#]/);
  const target = separator === -1 ? url : url.slice(0, separator);
  const suffix = separator === -1 ? '' : url.slice(separator);
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(source), decodeURIComponent(target)));
  if (resolved.startsWith('../')) throw new Error(`Tutorial URL escapes repository: ${url}`);
  const page = mapping.pages.find((entry) => entry.source === resolved);
  if (page) return siteUrl(routeFor(page)) + suffix;
  if (resolved.startsWith('validation/shared/install/')) return siteUrl('downloads/') + suffix;
  if (resolved === 'validation/agent/LOCAL-CASES.md' || resolved.startsWith('validation/shared/data/local/')) {
    return siteUrl('docs/#local-data');
  }
  const publicPrefix = 'validation/shared/data/public/';
  if (resolved.startsWith(publicPrefix)) {
    const selected = loadPublicSamples();
    let member = resolved.slice(publicPrefix.length);
    if (member === selected.manifest_member) member = 'tutorial-samples.json';
    const allowed = new Set(selected.samples.map((entry) => entry.path));
    if (!allowed.has(member) || (members && !members.has(member))) throw new Error(`Public tutorial input is absent from licensed ZIP allowlist: ${member}`);
    return siteUrl(`tutorial-assets/shared/data/public/${member}`) + suffix;
  }
  if (/^validation\/human\/(screenshots|renders)\//.test(resolved)) {
    if (!tracked.has(resolved)) throw new Error(`Untracked tutorial image: ${resolved}`);
    return siteUrl(`tutorial-assets/${resolved.slice('validation/'.length)}`) + suffix;
  }
  if (!tracked.has(resolved)) throw new Error(`Unpublished tutorial link: ${source} → ${url}`);
  return `${mapping.repository}/blob/main/${resolved.split('/').map(encodeURIComponent).join('/')}${suffix}`;
}

// Operate on link nodes rather than source strings, leaving code and inline paths intact.
export function remarkTutorialLinks() {
  return (tree, file) => {
    const absolute = path.resolve(file.path ?? '');
    const page = mapping.pages.find((entry) => entry.source && path.resolve(generatedPath(entry)) === absolute);
    if (!page) return;
    walk(tree, (node) => {
      if (['link', 'image', 'definition'].includes(node.type)) node.url = rewriteTutorialUrl(node.url, page.source);
    });
  };
}
