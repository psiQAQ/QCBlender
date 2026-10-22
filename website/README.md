# QCBlender 网站

Astro 宣传页与 Starlight 中文教程共用一个静态构建。中文首页位于 `/QCBlender/`，英文首页位于 `/QCBlender/en/`，全部中文教程位于 `/QCBlender/docs/`。英文宣传页标明教程语言。

## 本地开发

使用 Node 24.19.0 和 Python 3.13（仅标准库），在本目录运行：

```powershell
$env:ASTRO_TELEMETRY_DISABLED = '1'
npm ci --no-audit
npm run dev
```

打开命令输出的本地地址下的 `/QCBlender/`。npm 缓存由项目 `.npmrc` 指向仓库忽略的 `.tmp/cache/npm`；不改用户级 npm 设置。依赖更新需按仓库规则另行授权，日常使用锁文件安装。

## 构建与检查

```powershell
npm run prepare:docs
npm run check
npm test
npm run build
npm run verify
npm run preview
```

搜索索引在生产构建时生成；搜索验收使用 `preview` 或线上网站，不以开发服务器中能看到搜索框为通过。

## 内容来源

宣传文案在 `src/data/`，宣传页在 `src/pages/`，共享样式在 `src/styles/`。科学图位于 `src/assets/showcase/`。调整主题不会改变科学图片中的色标。

教程映射在 `tutorials.json`。正文只维护仓库原有 SOP、9 篇专题和 `docs/USER_GUIDE.md`；`prepare:docs` 生成的 Starlight 内容、复制资源和站点产物已忽略。修改教程后重新构建；不要手工编辑生成内容。

公开样本来自仓库冻结 ZIP，保留原包身份和许可。安装 ZIP、P02 本地材料、`.blend` 和 `.qcdata` 不在网站部署范围。公开 Release 尚不可用时，安装页提供状态说明和 Releases 入口，不能把源码 ZIP 当扩展安装包。

## 发布

`.github/workflows/pages.yml` 在相关 main 变更后检查并部署，PR 仅检查。仓库 Settings → Pages 的 Source 使用 GitHub Actions。工作流只上传本目录 `dist/`，不上传整个仓库。站点使用默认项目路径，配置自定义域名需同步修改 `site`、`base` 与链接策略。

发布后的网页版本以精确 main 提交的成功 Pages job 和线上检查为准。插件候选工作流、安装包发布和独立科研验收各有自己的结果。

方案依据见 [网站研究](../docs/research/website-github-pages.md)。网站源码沿用仓库 GPL-3.0-or-later；公开科学样本的 CC BY 4.0 及第三方引用保留在样本许可和 NOTICE 中。
