# 开发流程精简与 MCP 复用
Triage: ready-for-agent
Status: resolved

用户批准：整理最近四批复盘及共用脚本，真实打通现有 HTTP MCP；按影响范围选择必要检查，成功未变交互用 MCP 代替重复 Computer Use。保留最终产品整包重建、隔离冒烟、全局安装和原保存工程恢复。不批量删测试、历史材料，不修改发布 CI 门禁。全局 AGENTS 仅增加通用原则和本仓库条件指针，不复制细则。

主 Agent：统一 CLI、检查选择/结果复用、构建安装恢复及本地归档、真实集成验收、全局引用和证据索引。ops Agent：固定 Blender 操作及 CLI adapter。transport Agent：既有 MCP SDK 客户端与单进程管理。docs Agent：仓库流程入口与独立复盘。共享 Blender 由主 Agent 串行操作。

开始 Blender 实测前请用户保存关闭当前进程；完成后打开原保存工程，恢复草稿非目标。使用已有依赖，必要配置变化单独列明。不 push。技术结果分 Passed/Failed/Not Run，不代签独立人工接受。

## Answer

2026-10-16：统一入口、真实 HTTP MCP、完整重建、隔离/全局安装、保存冷读及原工程恢复通过；用户本次另授权直接关闭且不保存旧会话，并授权只同步客户端鉴权值。技术结果与限制见 `validation/agent/acceptance/dev-workflow.md`；提交与归档收据见其中入口。默认的先请用户保存关闭规则不变。
