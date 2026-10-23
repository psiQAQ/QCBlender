# QCBlender 宣传与教程网站方案

核对日期：2026-10-23。网站是插件的展示与教程入口；网站部署不构成插件安装包或独立科研验收。

## 选择

采用 Astro 7.4.2、Starlight 0.42.6、Node 24.19.0。npm 官方元数据确认 Starlight 要求 Astro ^7.2.10，可配 @astrojs/markdown-remark ^7.3.0；项目固定 7.3.4 并提交完整锁文件。

| 方案 | 适用点 | 本项目取舍 |
| --- | --- | --- |
| Astro + Starlight | 自定义宣传页与 Markdown 文档共存，内置文档导航和静态搜索 | 采用；宣传视觉与中文教程各用适合的布局，统一一次构建 |
| VitePress | 以 Markdown 为中心，默认主题面向技术文档，也支持 Vue 自定义主题 | 能实现，但本项目需要较多宣传布局定制 |
| 原生 HTML/CSS/JS | 固定少量页面无需构建框架 | 完整教程、搜索和主题同步需要自行维护，未采用 |

上述维护成本是针对本项目的判断，不是性能基准。用户选择宣传双语、教程中文，英文页面明确链接同一份中文教程，不以 fallback 页面宣称完成翻译。

## 内容与发布边界

- 中文正文来源为现有 SOP、9 篇专题和用户操作索引，生成内容不提交第二份可编辑副本。Markdown 链接在 AST 中映射；原行内路径、参数与代码保持。
- 初始来源为 79 个步骤、27 个图片引用、86 个 details；最终同步 main 的自动出图教程后图片为 28 个。Starlight 原生支持 details 内 Markdown；迁移检查逐篇比对原正文、相对链接和锚点。
- 公开输入从冻结样本 ZIP 恢复并核对 SHA-256，保留 LICENSE、NOTICE 和来源清单。P02、本地安装候选、科研工程与配套数据不进入站点产物。
- 2026-10-23 查询仓库为 public、默认分支 main、has_pages=false，公开 Releases 列表为空。因此网站安装页展示 Alpha 状态，不能提供未公开候选的假下载。
- 启用时 Pages API 确认继承账户现有域名 `notes.psiqaq.cn`；默认项目地址 https://psiQAQ.github.io/QCBlender/ 实际返回 301 到 https://notes.psiqaq.cn/QCBlender/。沿用该域名，启用本站 HTTPS；静态资源和内部导航保留 /QCBlender/ 前缀。无需新增服务器、账户、统计脚本或 DNS 配置。
- GitHub Actions 构建上传静态 artifact，Pages 部署 job 使用 github-pages environment、pages:write 和 id-token:write。PR 仅检查，main 才部署。
- Pagefind 按语言建立索引；中文分词依赖 extended release，须在真实构建产物上检索中文词，不能只检查搜索框存在。

## 一手来源

| 事实 | 来源 |
| --- | --- |
| Astro 静态站与项目 base 配置 | [Astro GitHub Pages](https://docs.astro.build/en/guides/deploy/github/) |
| 自定义 Astro 页面与 Starlight 文档共存 | [Starlight pages](https://starlight.astro.build/guides/pages/) |
| Markdown、标题与 details | [Authoring content](https://starlight.astro.build/guides/authoring-content/) |
| 缺译 fallback 不是英文正文 | [Starlight i18n](https://starlight.astro.build/guides/i18n/) |
| 内置静态搜索 | [Starlight search](https://starlight.astro.build/guides/site-search/) |
| 中文分词与 extended release | [Pagefind multilingual](https://pagefind.app/docs/multilingual/) |
| Pages 部署权限、artifact 与 environment | [GitHub custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) |
| 项目站继承用户站自定义域名 | [Using a custom domain across multiple repositories](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages#using-a-custom-domain-across-multiple-repositories) |
| VitePress 定位与自定义主题 | [VitePress introduction](https://vitepress.dev/guide/what-is-vitepress) |
| 固定版本与兼容范围 | [Astro npm metadata](https://registry.npmjs.org/astro/7.4.2)、[Starlight npm metadata](https://registry.npmjs.org/@astrojs/starlight/0.42.6) |

官方文档示例中的 Action 主版本可能落后于发布版本；本次 workflow 按已核实的官方发布 tag 解析 commit SHA 固定，版本说明留在行内注释。网站运行和线上部署的实际结果见任务验收记录，不由本研究代替。
