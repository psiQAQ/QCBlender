import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { unified } from '@astrojs/markdown-remark';
import { remarkTutorialLinks } from './scripts/tutorial-links.mjs';

export default defineConfig({
  site: 'https://notes.psiqaq.cn',
  base: '/QCBlender',
  trailingSlash: 'always',
  output: 'static',
  markdown: { processor: unified({ remarkPlugins: [remarkTutorialLinks], smartypants: false }) },
  integrations: [starlight({
    title: 'QCBlender',
    description: '在 Blender 中探索量子化学结果。',
    defaultLocale: 'root',
    locales: { root: { label: '简体中文', lang: 'zh-CN' } },
    components: {
      SiteTitle: './src/components/DocsSiteTitle.astro',
      Footer: './src/components/DocsFooter.astro',
    },
    customCss: ['./src/styles/docs.css'],
    social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/psiQAQ/QCBlender' }],
    sidebar: [
      { label: '教程导航', slug: 'docs' },
      { label: '安装与第一张轨道图', slug: 'docs/getting-started' },
      { label: '功能专题', items: [{ autogenerate: { directory: 'docs/topics' } }] },
      { label: '操作入口索引', slug: 'docs/reference' },
      { label: '版本与安装材料', link: '/downloads/' },
    ],
  })],
});
