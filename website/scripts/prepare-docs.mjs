import { mkdir, readFile, writeFile, copyFile, readdir, unlink } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { parse } from 'smol-toml';
import { generatedPath, mapping, repositoryRoot, rewriteTutorialUrl, routeFor, siteUrl, trackedFiles, tutorialImageSource, walk, websiteRoot } from './tutorial-links.mjs';
import { loadPublicSamples } from './public-samples.mjs';
import { loadPublishedRelease } from './published-release.mjs';

export const sha256 = (data) => createHash('sha256').update(data).digest('hex');
export async function writeGenerated(target, value) {
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, value, 'utf8');
}

async function pruneGeneratedImages(allowed) {
  // Only generated image copies in these two fixed, ignored directories are removed.
  for (const kind of ['screenshots', 'renders']) {
    const directory = path.resolve(websiteRoot, 'public/tutorial-assets/human', kind);
    let entries;
    try { entries = await readdir(directory, { withFileTypes: true }); }
    catch (error) { if (error.code === 'ENOENT') continue; throw error; }
    for (const entry of entries) {
      const relative = `tutorial-assets/human/${kind}/${entry.name}`;
      if (allowed.has(relative)) continue;
      if (!entry.isFile() || !/\.(png|jpe?g|webp)$/i.test(entry.name)) {
        throw new Error(`Unexpected object in generated image directory: ${relative}`);
      }
      await unlink(path.join(directory, entry.name));
    }
  }
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
  const published = await loadPublishedRelease();
  if (published) await writeGenerated(path.join(websiteRoot, 'public/index.json'), published.indexBytes);
  const tracked = trackedFiles();
  const selected = loadPublicSamples();
  const publicSamples = selected.archive;
  if (selected.delivery !== mapping.publicSamples.delivery) throw new Error('Tutorial delivery entry differs from the dataset reader');
  const archive = path.join(repositoryRoot, publicSamples.source);
  if (!tracked.has(publicSamples.source) || !tracked.has(selected.delivery)) throw new Error('Public samples ZIP and delivery record must be tracked');
  const zipBytes = await readFile(archive);
  if (sha256(zipBytes) !== publicSamples.sha256) throw new Error('Current public tutorial ZIP identity mismatch');
  const extraction = spawnSync(process.env.PYTHON ?? 'python', [
    path.join(websiteRoot, 'scripts/extract-public-samples.py'), '--root', repositoryRoot,
    '--destination', path.join(websiteRoot, 'public/tutorial-assets/shared/data/public'),
  ], { encoding: 'utf8' });
  if (extraction.error) throw extraction.error;
  if (extraction.status !== 0) throw new Error(extraction.stderr || 'Public samples extraction failed');
  const { samples, supplemental } = JSON.parse(extraction.stdout);
  const members = new Set([...samples, ...supplemental].map((entry) => entry.path));
  const download = path.join(websiteRoot, 'public/downloads', publicSamples.download);
  await mkdir(path.dirname(download), { recursive: true });
  await copyFile(archive, download);

  const manifest = { pages: [], images: [], samples, supplemental, archive: publicSamples };
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
          const image = tutorialImageSource(node.url, page.source);
          if (image) imageSources.push(image);
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
    for (const source of imageSources) {
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
  await pruneGeneratedImages(new Set(manifest.images.map((entry) => entry.path)));
  const navigation = mapping.pages.find((page) => page.slug === 'docs');
  const links = mapping.pages.filter((page) => page.source).map((page) => `- [${page.title}](${siteUrl(routeFor(page))})`).join('\n');
  const index = `---\ntitle: ${JSON.stringify(navigation.title)}\nsidebar:\n  order: ${navigation.order}\n---\n\n从安装与第一张轨道图开始，再按当前任务选择专题。网页正文直接来自仓库中文教程；菜单路径、数值、单位、代码与操作顺序沿用原文。\n\n${links}\n\n## 准备教程材料\n\n[下载公开教程样本 ZIP](${siteUrl(`downloads/${publicSamples.download}`)})，解压后保留版本目录及 P01–P06 各组内部的相对路径。原教程中的数据路径相对材料根目录；在本机将样本放到 \`shared/data/public/\` 下。包内 NOTICE.md、LICENSE 和 tutorial-samples.json 说明计算条件、许可和文件身份。网页中的文件链接也可单独下载；含多个配套文件的案例建议下载整包。\n\n[查看插件版本与安装材料状态](${siteUrl('downloads/')})。插件安装包尚未公开发布，网站不提供本地候选 ZIP。\n\n<a id="local-data"></a>\n## 本机限定数据\n\n当前包按逐文件许可清单包含自有 P02 优化、频率与 NBO 日志，对应 Gaussian 日志专题。历史受限 P02 与其他本机限定输入仍不在网站或公开包中；Blender 工程也不部署。案例编号本身不授予再分发许可。[仓库中的本机限定案例说明](${mapping.repository}/blob/main/validation/agent/LOCAL-CASES.md)记录了范围与前提。\n`;
  const publishedIndex = published ? index.replace(
    /\[下载公开教程样本 ZIP\][\s\S]*?插件安装包尚未公开发布，网站不提供本地候选 ZIP。/,
    `[下载完整教程 ZIP](${published.tutorial_download})，解压后保留 human/ 与 shared/ 的相对位置；完整包包括入门 SOP、全部专题、图片和必需输入，包含表面距离投影与 AICD 案例。各组 NOTICE.md 与 LICENSE 保留计算条件和许可。网页中的文件也可单独下载。\n\n当前公开版本为 ${published.manifest.version} Alpha Preview。[安装 ZIP 与远程仓库两种方法](${siteUrl('downloads/')})见下载页。`) : index;
  await writeGenerated(generatedPath(navigation), publishedIndex);
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
    version: published?.manifest.version ?? productManifest.version,
    blender_min: productManifest.blender_version_min,
    blender_max: productManifest.blender_version_max,
    platforms: productManifest.platforms,
    platform: 'Windows x64',
    channel: currentInstall.channel,
    public_release: Boolean(published),
    install_download: published?.install_download ?? null,
    tutorial_download: published?.tutorial_download ?? null,
    checksums_download: published?.checksums_download ?? null,
    index_url: published?.index_url ?? null,
    index_sha256: published ? sha256(published.indexBytes) : null,
    release_url: published?.release_url ?? null,
    release_source_commit: published?.manifest.source_commit ?? null,
    release_candidate_run_id: published?.manifest.candidate_run_id ?? null,
    independent_human_review: currentInstall.independent_human_review,
    license_review: currentInstall.license_review,
    scientific_acceptance: currentInstall.scientific_acceptance,
    samples_download: siteUrl(`downloads/${publicSamples.download}`),
    samples_name: publicSamples.download,
    samples_bytes: publicSamples.bytes,
    samples_dataset_id: publicSamples.dataset_id,
    samples_sha256: publicSamples.sha256,
  };
  await writeGenerated(path.join(websiteRoot, 'src/data/generated-product.json'), JSON.stringify(product, null, 2) + '\n');
  await writeGenerated(path.join(websiteRoot, 'reports/tutorial-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  const totals = manifest.pages.reduce((sum, page) => ({ steps: sum.steps + page.steps, details: sum.details + page.details, images: sum.images + page.images }), { steps: 0, details: 0, images: 0 });
  console.log(`Prepared ${manifest.pages.length} source pages: ${totals.steps} steps, ${totals.images} images, ${totals.details} details; ${samples.length} licensed current sample members.`);
  return manifest;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await prepareDocs();
