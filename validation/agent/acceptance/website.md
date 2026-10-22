# 宣传网站验收

日期：2026-10-23。网页阶段验证源码为 `29fa615`；底图仍是现有教程素材。任务范围、授权和交接顺序见 [规格](../../../.scratch/website/spec.md)，日常维护见 [website/README](../../../website/README.md)。

## 当前结果

| 范围 | 状态 | 实际结果 |
| --- | --- | --- |
| 网页类型与内容检查 | Passed | Astro check：23 文件，0 errors / warnings / hints；6 项定向测试通过 |
| 生产构建 | Passed | Node 24.19.0、Astro 7.4.2、Starlight 0.42.6，生成 17 个 HTML 页面和 Pagefind 索引 |
| 来源与部署内容 | Passed | 11 篇原正文保持，79 步、27 图、86 details；1,125 个内部链接/资源引用有效；61 个公开资源 SHA-256 一致 |
| 实际浏览器 | Passed | Codex 内置浏览器：桌面 1265 px 内容宽度与手机 390 × 844 视口，首页/安装页无横向溢出；中文与英文宣传入口、深浅主题、主题跨页面保持、菜单、404 返回入口可用 |
| 中文搜索与教程交互 | Passed | “轨道”返回 6 页，“IGMH”返回 5 页；中文搜索文案、具体步骤跳转、Escape 关闭及 details 展开可用 |
| 自动主题 | Passed | 初始系统模式及从教程选择自动后返回首页均显示当前系统深色；未改变操作系统主题测试实时切换 |
| 公开样本下载 | Passed | 从本地预览服务器实际取回 12,175,753 字节，SHA-256 与冻结包一致 |
| 干净检出与远端网站 CI | Not Run | 待最终图片完成后推送并以精确 main HEAD 的 Website 工作流验证 |
| 新 Blender 宣传图 | Not Run | 按用户要求，网页完成后等待“已保存并关闭”及原工程路径再接管 |
| GitHub Pages 上线 | Not Run | 尚未启用或部署；目标为 https://psiQAQ.github.io/QCBlender/ |
| 插件发布及独立科研验收 | Not Run | 本任务不发布插件安装 ZIP，不替代已有候选资格与独立签署 |

构建中的一条 Starlight 提示来自自定义 `404.md` 与框架专用 `/404` 路由：框架选择专用路由，实际 `404.html` 已生成，规范地址、搜索排除及返回链接已验证。无重复的 Astro 页面文件。首次配置和路径检查的失败已修正；未把中间构建当作交付通过。

## 证据与复现

技术截图保留在 `validation/agent/reports/2026-10-23/website/`：

- `preview-home-light.png`、`preview-en-dark.png`：两种语言与主题的首页观察。
- `preview-mobile-dark.png`：手机首页；`preview-docs-details-light.png`：桌面教程折叠说明。
- `preview-search-mobile.png`、`preview-search-igmh.png`：实际搜索结果。

上述截图是 Agent 浏览器操作与观察，不是独立用户验收。生成的来源清单位于 `website/reports/tutorial-manifest.json`，由 `prepare:docs` 重建；冻结公开包身份由 `website/tutorials.json` 固定。

本次在 `website/` 执行：`npm run prepare:docs`、`npm run check`、`npm test`、`npm run build`、`npm run verify`，Astro CLI 进程使用 `ASTRO_TELEMETRY_DISABLED=1`。本地预览入口为 `npm run preview -- --port 4321`；本批实际通过同一 Astro CLI 启动，PID 23572，日志在 `.tmp/runs/website/preview/`。

公开样本 SHA-256：`b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`。部署内容仅含白名单公开材料、页面和网站资源，未发现 P02、本地候选 ZIP、`.blend` 或 `.qcdata`。
