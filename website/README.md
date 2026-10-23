# QCBlender 网站

Astro 宣传页与 Starlight 中文教程共用一个静态构建。公开地址为 <https://notes.psiqaq.cn/QCBlender/>，继承账户现有 Pages 域名；默认 github.io 地址会重定向到这里。英文首页位于 `/QCBlender/en/`，全部中文教程位于 `/QCBlender/docs/`。英文宣传页标明教程语言。

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

宣传文案在 `src/data/`，宣传页在 `src/pages/`，共享样式在 `src/styles/`。科学图位于 `src/assets/showcase/`，真实渲染条件和来源见[图片说明](src/assets/showcase/README.md)。调整主题不会改变科学图片中的色标。

教程映射在 `tutorials.json`。正文只维护仓库原有 SOP、12 篇专题和 `docs/USER_GUIDE.md`；Gaussian日志专题使用当前自有P02。`prepare:docs` 生成的 Starlight 内容、复制资源和站点产物已忽略。嵌入图片及普通Markdown链接指向的历史图片均复制并核对摘要，普通链接不计入正文嵌入图片数。修改教程后重新构建；不要手工编辑生成内容。

公开样本通过 `validation/agent/acceptance/tutorial-sample-delivery.json` 选择当前dataset、ZIP及摘要，复用仓库的版本/许可白名单检查。目前为 `gaussian-v1` / v3，185个数据文件；下载名称、大小和摘要也由该记录生成。自有P02仅按具体文件身份与CC BY 4.0许可纳入，历史受限P02、非白名单输入及其改名副本仍拒绝；legacy-v2冻结原身份保留。安装 ZIP、其他本地材料、`.blend` 和 `.qcdata` 不在网站部署范围。公开 Release 尚不可用时，安装页提供状态说明和 Releases 入口，不能把源码 ZIP 当扩展安装包。

不需要Astro依赖的定向检查可在仓库根运行 `python -m unittest discover -s website/scripts -p test_public_samples.py` 和 `node --test website/scripts/public-samples.test.mjs`。这两项不替代上述完整构建检查。部署校验仍拒绝历史遗留的非当前资源；首次切换版本应在干净的生成目录构建，不把旧资源的存在视为许可依据。

## 发布

`.github/workflows/pages.yml` 在相关 main 变更后检查并部署，PR 仅检查。仓库 Settings → Pages 的 Source 使用 GitHub Actions，本站启用强制 HTTPS。工作流只上传本目录 `dist/`，不上传整个仓库。站点保留 `/QCBlender/` 项目路径；更换域名时同步 `astro.config.mjs`、布局 fallback、404 规范地址与链接校验 origin，项目路径变化还需修改 `tutorials.json`。

发布后的网页版本以精确 main 提交的成功 Pages job 和线上检查为准。插件候选工作流、安装包发布和独立科研验收各有自己的结果。

方案依据见 [网站研究](../docs/research/website-github-pages.md)。网站源码沿用仓库 GPL-3.0-or-later；公开科学样本的 CC BY 4.0 及第三方引用保留在样本许可和 NOTICE 中。
