import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repository = fileURLToPath(new URL('../../', import.meta.url));
const extractor = fileURLToPath(new URL('./extract-public-samples.py', import.meta.url));
const cache = new Map();

export function loadPublicSamples(root = repository) {
  root = path.resolve(root);
  if (!cache.has(root)) {
    const result = execFileSync(process.env.PYTHON ?? 'python', [extractor, '--root', root, '--inspect'], { encoding: 'utf8' });
    cache.set(root, JSON.parse(result));
  }
  return cache.get(root);
}

export function deploymentViolations(files, permittedAssets, selected = loadPublicSamples()) {
  const errors = [];
  const members = new Set(selected.samples.map((entry) => `tutorial-assets/shared/data/public/${entry.path}`));
  for (const file of files) {
    if (/^(tutorial-assets|downloads)\//.test(file) && file !== 'downloads/index.html' && !permittedAssets.has(file)) errors.push(`Unexpected file in public materials: ${file}`);
    if (/(?:^|\/)(?:local|\.local|\.tmp|candidates|node_modules)(?:\/|$)/i.test(file)
      || (/(?:^|\/)P02(?:\/|$)/i.test(file) && !members.has(file))) errors.push(`Private deployment path: ${file}`);
    if (/\.(?:blend\d*|qcdata)(?:\/|$)/i.test(file)) errors.push(`Blender project in deployment: ${file}`);
    if (/\.zip$/i.test(file) && file !== `downloads/${selected.archive.download}`) errors.push(`Unpublished ZIP in deployment: ${file}`);
  }
  return errors;
}
