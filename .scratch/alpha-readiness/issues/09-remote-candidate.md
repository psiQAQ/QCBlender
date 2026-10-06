# 09 远端候选CI及草稿

Triage: ready-for-human
Status: pending
Blocked by: 08

## 工作与验收

提交可审查的具体推送/候选CI/发布标签与草稿动作，取得必要授权后执行。记录实际run/artifact与摘要，先dry-run验证，草稿创建需技术/许可门禁。配置真实受保护环境，不将未配置的审批写成已存在。

## Comments

2026-10-05：08 resolved，具体远端候选入口为 main 上的 `.github/workflows/extension-package.yml`；待维护者明确授权推送 main 并触发该候选 CI。当前本地 run ID 0，不能替代 GitHub run/artifact 身份。发布标签、草稿创建和公开批准另行执行相应门禁；组件许可复核仍 Not Run。

2026-10-06：用户授权为解决 Actions 失败执行 push。远端 da187c8 的候选 CI run 37305838293 在下载官方运行库校验清单时 HTTP 403，尚未生成候选 artifact；完整修复验证由 13 跟踪。草稿创建仍需组件许可和候选身份门禁，未据此创建发布标签或草稿。

2026-10-06：13 resolved，实际候选 run 37414740265 / artifact 11390153636 Passed，下载摘要与源码/wheels/公开材料复核 Passed。候选 CI 子步骤完成；剩余精确发布标签、dry-run 及草稿受组件许可/独立短 SOP 门禁和相应授权约束，任务仍 pending、ready-for-human。证据见 `docs/acceptance/actions-download-fix.md`，不将部分完成记为整个 09 resolved。
