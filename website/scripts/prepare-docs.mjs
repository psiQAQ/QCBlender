import { mkdir, readFile, writeFile, copyFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { parse } from 'smol-toml';
import { generatedPath, mapping, repositoryRoot, rewriteTutorialUrl, routeFor, siteUrl, trackedFiles, walk, websiteRoot } from './tutorial-links.mjs';

export const sha256 = (data) => createHash('sha256').update(data).digest('hex');
export async function writeGenerated(target, value) {
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, value, 'utf8');
}

export function sourceMetrics(text) {
  return {
    steps: (text.match(/^### \d+\. /gm) ?? []).length,
    details: (text.match(/<details>/g) ?? []).length,
    images: (text.match(/^!\[/gm) ?? []).length,
    explicitAnchors: [...text.matchAll(/<a id="([^"]+)"\s*><\/a>/g)].map((match) => match[1]),
  };
}

export async function prepareDocs() {
  const tracked = trackedFiles();
  const archive = path.join(repositoryRoot, mapping.publicSamples.source);
  if (!tracked.has(mapping.publicSamples.source)) throw new Error('Public samples ZIP must be tracked');
  const zipBytes = await readFile(archive);
  if (sha256(zipBytes) !== mapping.publicSamples.sha256) throw new Error('Frozen public tutorial ZIP identity mismatch');
  const extraction = spawnSync(process.env.PYTHON ?? 'python', [
    path.join(websiteRoot, 'scripts/extract-public-samples.py'), archive,
    path.join(websiteRoot, 'public/tutorial-assets/shared/data/public'),
    mapping.publicSamples.sha256, String(mapping.publicSamples.members),
  ], { encoding: 'utf8' });
  if (extraction.error) throw extraction.error;
  if (extraction.status !== 0) throw new Error(extraction.stderr || 'Public samples extraction failed');
  const samples = JSON.parse(extraction.stdout);
  const members = new Set(samples.map((entry) => entry.path));
  const download = path.join(websiteRoot, 'public/downloads', mapping.publicSamples.download);
  await mkdir(path.dirname(download), { recursive: true });
  await copyFile(archive, download);

  const manifest = { pages: [], images: [], samples, archive: mapping.publicSamples };
  const copiedImages = new Set();
  for (const page of mapping.pages.filter((entry) => entry.source)) {
    const bytes = await readFile(path.join(repositoryRoot, page.source));
    const text = bytes.toString('utf8');
    let firstHeading;
    const imageSources = [];
    const inspect = () => (tree) => {
      firstHeading = tree.children.find((node) => node.type === 'heading' && node.depth === 1);
      if (!firstHeading || firstHeading.position.start.offset !== 0) throw new Error(`Expected leading H1: ${page.source}`);
      walk(tree, (node) => {
        if (['link', 'image', 'definition'].includes(node.type)) {
          rewriteTutorialUrl(node.url, page.source, { tracked, members });
          if (node.type === 'image') imageSources.push(node.url);
        }
      });
    };
    const renderer = await createMarkdownProcessor({ remarkPlugins: [inspect], syntaxHighlight: false, smartypants: false });
    const result = await renderer.render(text, { fileURL: pathToFileURL(path.join(repositoryRoot, page.source)) });
    const originalTitleAnchor = result.metadata.headings.find((heading) => heading.depth === 1)?.slug;
    if (!originalTitleAnchor) throw new Error(`Missing source H1 anchor: ${page.source}`);
    const body = text.slice(firstHeading.position.end.offset).replace(/^\r?\n/, '');
    const frontmatter = `---\ntitle: ${JSON.stringify(page.title)}\nsidebar:\n  order: ${page.order}\neditUrl: ${JSON.stringify(`${mapping.repository}/edit/main/${page.source}`)}\n---\n`;
    await writeGenerated(generatedPath(page), `${frontmatter}\n<a id="${originalTitleAnchor}"></a>\n${body}`);
    for (const image of imageSources) {
      const source = path.posix.normalize(path.posix.join(path.posix.dirname(page.source), image));
      if (copiedImages.has(source)) continue;
      const target = path.join(websiteRoot, 'public/tutorial-assets', source.slice('validation/'.length));
      await mkdir(path.dirname(target), { recursive: true });
      const imageBytes = await readFile(path.join(repositoryRoot, source));
      await writeFile(target, imageBytes);
      copiedImages.add(source);
      manifest.images.push({ source, path: `tutorial-assets/${source.slice('validation/'.length)}`, sha256: sha256(imageBytes) });
    }
    manifest.pages.push({ source: page.source, slug: page.slug, title: page.title, sha256: sha256(bytes), originalTitleAnchor, ...sourceMetrics(text) });
  }
  const navigation = mapping.pages.find((page) => page.slug === 'docs');
  const links = mapping.pages.filter((page) => page.source).map((page) => `- [${page.title}](${siteUrl(routeFor(page))})`).join('\n');
  const index = `---\ntitle: ${JSON.stringify(navigation.title)}\nsidebar:\n  order: ${navigation.order}\n---\n\n从安装与第一张轨道图开始，再按当前任务选择专题。网页正文直接来自仓库中文教程；菜单路径、数值、单位、代码与操作顺序沿用原文。\n\n${links}\n\n## 准备教程材料\n\n[下载公开教程样本 ZIP](${siteUrl(`downloads/${mapping.publicSamples.download}`)})，解压后保留 P01、P03、P04、P05、P06 各组内部的相对路径。原教程中的数据路径相对材料根目录；在本机将样本放到 \`shared/data/public/\` 下。包内 NOTICE.md、LICENSE 和 tutorial-samples.json 说明计算条件、许可和文件身份。网页中的文件链接也可单独下载；含多个配套文件的案例建议下载整包。\n\n[查看插件版本与安装材料状态](${siteUrl('downloads/')})。插件安装包尚未公开发布，网站不提供本地候选 ZIP。\n\n<a id="local-data"></a>\n## 本机限定数据\n\nP02 的能量、振动、优化与 NBO 案例依赖本机限定的计算输入，网站和公开样本 ZIP 均不包含这些文件或 Blender 工程。请使用自己有权使用的等价数据；公开网页无法提供同一输入的逐步复现。[仓库中的本机限定案例说明](${mapping.repository}/blob/main/validation/agent/LOCAL-CASES.md)记录了范围与前提。\n`;
  await writeGenerated(generatedPath(navigation), index);
  await writeGenerated(path.join(websiteRoot, 'src/content/docs/404.md'), `---
title: 页面未找到
template: splash
pagefind: false
editUrl: false
head:
  - tag: link
    attrs:
      rel: canonical
      href: https://notes.psiqaq.cn${mapping.base}/404.html
  - tag: meta
    attrs:
      property: og:url
      content: https://notes.psiqaq.cn${mapping.base}/404.html
  - tag: meta
    attrs:
      name: robots
      content: noindex
---

地址可能已变更。你可以从[首页](${siteUrl()})或[教程导航](${siteUrl('docs/')})继续。

Page not found. Continue from the [English home page](${siteUrl('en/')}).
`);

  const productManifest = parse(await readFile(path.join(repositoryRoot, 'qcblender/blender_manifest.toml'), 'utf8'));
  const currentInstall = JSON.parse(await readFile(path.join(repositoryRoot, 'validation/agent/current-install.json'), 'utf8'));
  const product = {
    version: productManifest.version,
    blender_min: productManifest.blender_version_min,
    blender_max: productManifest.blender_version_max,
    platforms: productManifest.platforms,
    platform: 'Windows x64',
    channel: currentInstall.channel,
    public_release: false,
    install_download: null,
    independent_human_review: currentInstall.independent_human_review,
    license_review: currentInstall.license_review,
    scientific_acceptance: currentInstall.scientific_acceptance,
    samples_download: siteUrl(`downloads/${mapping.publicSamples.download}`),
    samples_sha256: mapping.publicSamples.sha256,
  };
  await writeGenerated(path.join(websiteRoot, 'src/data/generated-product.json'), JSON.stringify(product, null, 2) + '\n');
  await writeGenerated(path.join(websiteRoot, 'reports/tutorial-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  const totals = manifest.pages.reduce((sum, page) => ({ steps: sum.steps + page.steps, details: sum.details + page.details, images: sum.images + page.images }), { steps: 0, details: 0, images: 0 });
  console.log(`Prepared ${manifest.pages.length} source pages: ${totals.steps} steps, ${totals.images} images, ${totals.details} details; ${samples.length} frozen public sample members.`);
  return manifest;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await prepareDocs();
