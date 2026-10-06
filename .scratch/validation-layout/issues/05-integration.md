# 05 整合与复核

Triage: ready-for-agent
Status: claimed
Blocked by: 02, 03, 04
Owner: main agent

## Scope

维护 `validation/README.md`、最新安装包与定位记录、根 AGENTS、存储规则、当前文档入口、ARTIFACTS/CHANGELOG 和综合验证。保留已有用户修改。串行协调子任务更新、合并，再直接检查 main 的实际内容与可复现行为。

## Acceptance

数据、教程、技术流程互相一致；公开允许集合脱离仓库可使用；相关测试和代表性 Blender 检查给出实测状态；人工作业不代签。保留/删除清单已可审查，删除仍由 06 控制。

## Comments

2026-10-06：02/03/04 已依次合入 main（d6a61d6、6e03549、fb860a6）。主 Agent 维护入口、长期规则与独立打包检查，接下来直接在 main 补齐忽略资源并运行综合验证。
