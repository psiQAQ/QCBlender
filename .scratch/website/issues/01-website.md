# 宣传站与中文教程

Triage: ready-for-agent
Status: resolved

## Acceptance

按 ../spec.md 完成网站、来源适配、定向检查及真实浏览器预览；用户确认会话交接后完成新渲染、原工程恢复与精确 main HEAD 的网站部署。

## Comments

- 2026-10-23：从 main 建立 feat/website；保留主检出已有研究和子模块改动。网站构建与教程接入并行，主 Agent 串行整合。
- 2026-10-23：网页阶段完成并提供本地浏览器预览，结果统一记在 [验收](../../../validation/agent/acceptance/website.md)。等待用户确认已保存并关闭 Blender 及原工程路径；新图、最终整合与线上部署尚待完成。
- 2026-10-23：用户回复“已关闭”后完成三组真实出图、科学数组比较与副本冷读，原 P01 已恢复。同步 main 最新 SOP 后最终网站与浏览器复验 Passed；Pages 继承现有域名并启用 HTTPS，准备推送与线上验证。
- 2026-10-23：源码提交 `42566fb` 已推送，Website 构建与 Pages 部署 success；线上页面、404、公开下载哈希和中文搜索 Passed。插件候选 CI 的 3 项 stdlib 失败单独保留，不计作网站失败或插件发布成功。

## Answer

已上线 [中文首页](https://notes.psiqaq.cn/QCBlender/)、[英文首页](https://notes.psiqaq.cn/QCBlender/en/)及[完整中文教程](https://notes.psiqaq.cn/QCBlender/docs/)。新图、工程保护、浏览器与远端验证统一见[验收记录](../../../validation/agent/acceptance/website.md)。本任务三条分支按既有流程保全产物并本地归档；Node 环境在主检出复用，其他任务工作树和主检出原有研究改动保留。
