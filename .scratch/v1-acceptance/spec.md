# QCBlender v1 独立验收与发布门槛

Status: claimed

目标：以固定的 `0.0.1` ZIP 由使用者逐例验证全部输入、物理量、节点、渲染和可迁移工程。九片外部分析须有真实可追溯样本并由使用者成图签署。全部通过后，建立 Windows x64 / Blender 5.1.1 的 `v1.0.0` 标签构建、草稿 GitHub Release、确切 ZIP 复核和 Blender Extensions 上传机制。

验收清单：[SOP](../../docs/v1-acceptance/SOP.md)；样本与缺口：[SOURCES](../../docs/v1-acceptance/SOURCES.md)。

## 顺序

1. [01 样本来源与清单](issues/01-sources-and-sop.md)：当前可复做样本已固定；其余真实样本缺口开放。
2. [02 独立人工验收](issues/02-human-acceptance.md)：使用者操作、渲染、冷重开与签署；Agent 可整理/修复并要求重做受影响例，不代签。
3. [03 发布机制](issues/03-release-mechanism.md)：仅在 02 全部通过后领取；先本地实现并验证工作流，再按明确批准执行对外动作。

任一案例 `Failed` 或 `Not Run`，或许可/包资格未通过时，维持候选状态，不推送发布标签、不公开 Release、不上传 Blender Extensions。现有未跟踪 `docs/multiwfn.md` 与 `docs/visualization-sw.md` 不纳入本任务提交。
