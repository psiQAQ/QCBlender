# v1 历史验收材料

当前人工操作从 [validation/human/SOP.md](../../validation/human/SOP.md) 开始；安装包、输入和教程打包方法见 [validation](../../validation/README.md)，技术检查见 [Agent 流程](../../validation/agent/README.md)。

本目录包含仍被工具读取的冻结清单，以及不能由当前教程替代的来源和历史证据。`tutorial-samples.json` 用于数据准备、候选校验和发布检查，保持原路径与原始字节；419 张原截图各有不同的 SHA-256，其中240张被[Blender操作登记表](../acceptance/blender-operations.json)引用。其余图片保留历史参数、错误和恢复过程。

本目录保存历史候选的来源、科学条件和验收证据。文中的日期、路径、“当前”及 Passed / Failed / Not Run 对应各自批次；当前产物可用性和重建方法由 [ARTIFACTS](../ARTIFACTS.md) 定位。独立人工完成情况见 [任务 02](../../.scratch/v1-acceptance/issues/02-human-acceptance.md)。

| 历史材料 | 用途 |
| --- | --- |
| [HISTORY.md](HISTORY.md) | 历史批次说明、操作图注、技术边界及证据入口 |
| [SOURCES.md](SOURCES.md) | 来源 URL、许可、计算条件、原始路径及摘要 |
| [AGENT-REPLAY.md](AGENT-REPLAY.md) | 2026-09-27 固定候选的 C01–C13 / N01–N18 技术复跑结果 |
| [screenshot/](screenshot/) | 历史截图；保留原文件和所绑定候选身份 |
| [tutorial-samples.json](tutorial-samples.json) | 数据准备、候选和发布工具共用的冻结样本清单（保持原始字节）；`path` 为冻结时来源，当前输入按 `archive_path` 或稳定 key 在集中数据目录读取 |

历史材料保留科学记录和独立人工状态；本批及后续技术报告由 `validation/agent/` 维护。
