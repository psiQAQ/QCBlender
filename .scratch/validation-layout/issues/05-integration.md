# 05 整合与复核

Triage: ready-for-agent
Status: resolved
Blocked by: 02, 03, 04
Owner: main agent

## Scope

维护 `validation/README.md`、最新安装包与定位记录、根 AGENTS、存储规则、当前文档入口、ARTIFACTS/CHANGELOG 和综合验证。保留已有用户修改。串行协调子任务更新、合并，再直接检查 main 的实际内容与可复现行为。

## Acceptance

数据、教程、技术流程互相一致；公开允许集合脱离仓库可使用；相关测试和代表性 Blender 检查给出实测状态；人工作业不代签。保留/删除清单已可审查，删除仍由 06 控制。

## Comments

2026-10-06：02/03/04 已依次合入 main（d6a61d6、6e03549、fb860a6）。主 Agent 维护入口、长期规则与独立打包检查，接下来直接在 main 补齐忽略资源并运行综合验证。

## Answer

已在 main 补齐集中数据和唯一教程安装包，完成公开材料独立复制检查。134 项基础、67 项公开科学、123 项完整科学测试均为 Passed，无失败或跳过；真实安装、Alpha MO9、摘要导出、XYZ/CSV 与中文路径冷重开 Passed。测试脚本缺少剖面场对象的首轮失败已保留，补齐前置场景后受影响检查与冷重开通过。产品源码和依赖锁未变。

根 AGENTS 保存人工教程和清理习惯；按用户新增要求，子 Agent 默认 `gpt-6.1-sol`、`high`，仅用户指定其他模型时覆盖。公开教程 29 张、本机页 3 张截图仍待维护者补入。GUI 点击、独立人工/科研验收和 checkpoint 复算为 Not Run。

证据见 `validation/agent/VALIDATION.md`。历史删除范围为 33 个压缩包或安装对象及 224 个旧输入副本，元数据与集中副本均已核对，交由 06 单独确认。
