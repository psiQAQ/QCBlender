# 文档索引

第一次使用从[人工教程](../validation/human/SOP.md)开始；安装包、输入和教程材料集中在 [validation](../validation/README.md)。本目录保存功能说明、开发约定、科学依据和历史摘要；按候选归档的技术验收材料集中在 `validation/agent/`。

## 当前使用与开发

| 要查什么 | 入口 |
| --- | --- |
| 界面入口与日常操作 | [用户指南](USER_GUIDE.md)；逐步操作见[人工教程](../validation/human/SOP.md) |
| 文件支持、物理量及科学限制 | [支持范围](VALIDATION.md) |
| 外部分析文件要求 | [外部结果导入](EXTERNAL_ANALYSIS_IMPORT.md) |
| 真实案例的计算条件与重建 | [复杂案例](COMPLEX_EXAMPLES.md) |
| 环境、打包与同批验证 | [开发说明](DEVELOPMENT.md)、[开发问题记录](DEVELOPMENT_PITFALLS.md) |
| 当前安装包、保留工程与重建位置 | [产物入口](ARTIFACTS.md) |
| 已完成变化 | [演进记录](CHANGELOG.md) |

## 设计、规则与证据

| 内容 | 入口与用途 |
| --- | --- |
| 领域与架构 | [领域词汇](../CONTEXT.md)、[架构职责](QCBLENDER_V1_DESIGN.md)、[单扩展 ADR](adr/0001-self-contained-extension.md) |
| 实现契约 | [科学数据](specs/qc-data-contract.md)、[几何节点](specs/geometry-nodes.md) |
| 研究依据 | [研究索引](research/README.md)：来源、输入语义、技术取舍和固定日期审查 |
| 技术验收 | [验收索引](../validation/agent/acceptance/README.md)：候选身份、GUI 操作登记和验证方法 |
| v1 来源与历史操作 | [v1 材料](../validation/agent/v1-acceptance/README.md)：冻结清单、来源条件、复跑记录与原截图 |
| 更早的规划与批次摘要 | [历史索引](archive/README.md) |
| Agent 约定 | [任务跟踪](agents/issue-tracker.md)、[分派标签](agents/triage-labels.md)、[领域文档](agents/domain.md)、[Blender 交互](agents/blender-interaction.md)、[存储维护](agents/storage-maintenance.md) |

当前操作和支持范围以本页上半部分入口为准。研究中的建议与旧候选的 Passed / Failed / Not Run 保留各自日期和范围；独立使用者操作与科研验收由实际反馈确认。
