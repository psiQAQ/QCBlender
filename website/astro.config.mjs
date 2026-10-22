import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://psiQAQ.github.io',
  base: '/QCBlender',
  trailingSlash: 'always',
  output: 'static',
  integrations: [starlight({
    title: 'QCBlender',
    description: '在 Blender 中探索量子化学结果。',
    defaultLocale: 'root',
    locales: { root: { label: '简体中文', lang: 'zh-CN' } },
    social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/psiQAQ/QCBlender' }],
    sidebar: [
      { label: '教程导航', slug: 'docs' },
      { label: '安装与第一张轨道图', slug: 'docs/getting-started' },
      { label: '功能专题', autogenerate: { directory: 'docs/topics' } },
      { label: '操作入口索引', slug: 'docs/reference' },
      { label: '版本与安装材料', link: '/QCBlender/downloads/' },
    ],
  })],
});
