# 09 远端候选CI及草稿

Triage: ready-for-human
Status: pending
Blocked by: 08

## 工作与验收

提交可审查的具体推送/候选CI/发布标签与草稿动作，取得必要授权后执行。记录实际run/artifact与摘要，先dry-run验证，草稿创建需技术/许可门禁。配置真实受保护环境，不将未配置的审批写成已存在。

## Comments

2026-10-05：08 resolved，具体远端候选入口为 main 上的 `.github/workflows/extension-package.yml`；待维护者明确授权推送 main 并触发该候选 CI。当前本地 run ID 0，不能替代 GitHub run/artifact 身份。发布标签、草稿创建和公开批准另行执行相应门禁；组件许可复核仍 Not Run。
