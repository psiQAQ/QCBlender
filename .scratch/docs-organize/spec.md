# docs 文档整理

Triage: ready-for-agent
Status: resolved
Baseline: main@4313666
Date: 2026-10-06

## 目标

检查 docs/v1-acceptance 的保留价值，整理 docs 中当前说明、历史验收与研究材料的入口。用户已要求实施整理；按仓库本地工作流验证、提交、快进合并及注释归档，不 push。

## 范围

- 将 v1-acceptance 与 acceptance 迁至 validation/agent/：冻结 tutorial-samples.json 被工具与 CI 消费，来源、历史记录和419张截图具有独立价值；不改冻结字节、截图、机器验收记录或产品行为。
- 将 RESULT_BROWSER、OPTIMIZATION_TRAJECTORY、MOLECULARNODES_PARAMETERS、MULTIWFN_PARAMETERS 四份历史技术记录归入 validation/agent/acceptance/history/，保留事实、参数、候选身份和状态，更新可点击路径。
- 建立 docs、acceptance、research、archive 的分组索引；明确当前操作、科研边界与历史快照的不同用途。
- 修正已确认的文档状态歧义及 ARTIFACTS 中手动重试后的清理状态，不将历史 Passed 当作当前验收。
- docs/GPT-Web-Chat 和 docs/sobereva 中9份既有忽略资料保持原位，不修改。

## 验证

目录和文档链接/锚点检查；419张截图、冻结清单及机器记录摘要保持不变；移动文档的正文内容仅调整路径和明确的历史说明。同步工具与测试中的当前路径，运行候选、发布、数据准备的相关测试及实际冻结样本包和公开材料检查；迁移前发布标签仍可验证。产品科学测试和 Blender 操作按未变范围记 Not Run。

清理前后清单、子 Agent 只读审查和验证报告位于 validation/agent/reports/2026-10-06/docs-organize/。主 Agent 统一修改路径，避免跨文件竞争。

## 任务

- [01 结构和依赖审查](issues/01-audit.md)
- [02 归组与引用](issues/02-organize.md)
- [03 验证与归档](issues/03-delivery.md)
- [04 迁移至 Agent 校验目录](issues/04-migrate-acceptance.md)

## 结果

当前入口为 docs/README.md；技术验收与 v1 材料集中在 validation/agent/。本批最终迁移验证及本地归档见任务04与 ARTIFACTS。
