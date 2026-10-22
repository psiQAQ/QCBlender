# 宣传网站验收

日期：2026-10-23。网站已同步 main `22b0103` 的自动出图教程，并替换为本批三组真实 Blender 渲染。任务范围、授权和交接顺序见 [规格](../../../.scratch/website/spec.md)，日常维护见 [website/README](../../../website/README.md)。初始网页阶段 `29fa615` 的浏览器记录保留原身份。

## 当前结果

| 范围 | 状态 | 实际结果 |
| --- | --- | --- |
| 网页类型与内容检查 | Passed | Astro check：23 文件，0 errors / warnings / hints；6 项定向测试通过 |
| 生产构建 | Passed | Node 24.19.0、Astro 7.4.2、Starlight 0.42.6，生成 17 个 HTML 页面和 Pagefind 索引 |
| 来源与部署内容 | Passed | 11 篇原正文保持，79 步、28 图、86 details；1,126 个内部链接/资源引用有效；62 个公开资源 SHA-256 一致 |
| 实际浏览器 | Passed | Codex 内置浏览器：桌面 1265 px 内容宽度与手机 390 × 844 视口，首页/安装页无横向溢出；中文与英文宣传入口、深浅主题、主题跨页面保持、菜单、404 返回入口可用 |
| 中文搜索与教程交互 | Passed | “轨道”返回 6 页，“IGMH”返回 5 页；中文搜索文案、具体步骤跳转、Escape 关闭及 details 展开可用；同步新版 SOP 后“自动取景”返回 2 页，第 8 步跳转及新截图加载通过 |
| 自动主题 | Passed | 初始系统模式及从教程选择自动后返回首页均显示当前系统深色；未改变操作系统主题测试实时切换 |
| 公开样本下载 | Passed | 从本地预览服务器实际取回 12,175,753 字节，SHA-256 与冻结包一致 |
| 干净检出与远端网站 CI | Not Run | 待最终图片完成后推送并以精确 main HEAD 的 Website 工作流验证 |
| 新 Blender 宣传图 | Passed | 用户确认关闭后，MCP 实际渲染 MO、ESP、IGMH；三份自包含副本新进程冷读通过，科学数组和对象变换一致；详见下文 |
| 原工程保护与恢复 | Passed | 206 个原工程及配套文件 SHA-256 未变；P01 原保存工程恢复到 PID 22344，未修改状态，3 个 Dataset 视图可读取；未宣称与接管前 GUI 布局逐像素一致 |
| GitHub Pages 上线 | Not Run | 已启用 Actions 与 HTTPS；继承现有域名 https://notes.psiqaq.cn/QCBlender/，默认 github.io 地址实际 301 到此处；待本批推送部署 |
| 插件发布及独立科研验收 | Not Run | 本任务不发布插件安装 ZIP，不替代已有候选资格与独立签署 |

构建中的一条 Starlight 提示来自自定义 `404.md` 与框架专用 `/404` 路由：框架选择专用路由，实际 `404.html` 已生成，规范地址、搜索排除及返回链接已验证。无重复的 Astro 页面文件。首次配置和路径检查的失败已修正；同步新版 SOP 后清单检查准确报告 27→28 张图片的变化，复核来源后更新基线并通过。未把中间构建当作交付通过。

## Blender 出图与恢复

参数、输入与成图摘要以[图片来源说明](../../../website/src/assets/showcase/README.md)为公开入口。实际使用已安装候选 `8d2f83f`，未重装插件。复用 `qc-auto-output` 的已验收 GUI 入口及 `cold-open-and-render` 的保存/新进程检查，操作实现与当前安装一致；本次取景、渲染与保存实际通过 HTTP MCP 执行，冷读通过原生后台 CLI 执行，未改称本次 GUI 点击或独立科研验收。

工程保存在 `outputs/projects/website-showcase/{orbital,esp,igmh}/`，保留 `.blend + .qcdata`。`renders/{orbital,esp,igmh}.json` 记录每个数组摘要、对象变换、相机、输入与图像 SHA-256，`source-baseline.json` 记录原件身份。IGMH 首次主轴方向使表面侧对相机，最终仅调整观察角度 35° 并重做该图的渲染和冷读；最终成图身份以图片说明和 `igmh.json` 为准。

首次受沙箱限制的 PID 74352 无法访问日常 MCP 运行库，正常关窗后仍残留；核对路径、命令行和本批归属后结束该进程。此时未执行编辑或渲染。后续使用可读取现有扩展的实例，均正常退出；没有安装依赖或更改权限。原工程恢复快照位于 `runs/restore/original-restored.json` 及对应 `native-*/result.json`，实际核对范围为原件字节、已打开路径、未保存状态与数据读取。

## 证据与复现

技术截图保留在 `validation/agent/reports/2026-10-23/website/`：

- `preview-home-light.png`、`preview-en-dark.png`：两种语言与主题的首页观察。
- `preview-mobile-dark.png`：手机首页；`preview-docs-details-light.png`：桌面教程折叠说明。
- `preview-search-mobile.png`、`preview-search-igmh.png`：实际搜索结果。
- `final-home-light.png`、`final-en-dark.png`、`final-mobile-dark.png`：替换真实新图后的最终网页；`final-search-auto-output.png`：新版教程搜索。

上述截图是 Agent 浏览器操作与观察，不是独立用户验收。生成的来源清单位于 `website/reports/tutorial-manifest.json`，由 `prepare:docs` 重建；冻结公开包身份由 `website/tutorials.json` 固定。待推送的 195 个提交历史补丁已做高信号凭据检查，未发现私钥、GitHub/AWS/OpenAI 密钥模式；该检查不等同于完整安全审计。

本次在 `website/` 执行：`npm run prepare:docs`、`npm run check`、`npm test`、`npm run build`、`npm run verify`，Astro CLI 进程使用 `ASTRO_TELEMETRY_DISABLED=1`。本地预览入口为 `npm run preview -- --port 4321`；本批实际通过同一 Astro CLI 启动，PID 23572，日志在 `.tmp/runs/website/preview/`。

公开样本 SHA-256：`b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`。部署内容仅含白名单公开材料、页面和网站资源，未发现 P02、本地候选 ZIP、`.blend` 或 `.qcdata`。
