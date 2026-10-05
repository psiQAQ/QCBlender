# QCBlender v1 独立验收与发布门槛

Status: claimed

目标：以记录精确摘要的固定 ZIP 由使用者逐例验证全部输入、物理量、节点、渲染和可迁移工程。九片外部分析须有真实可追溯样本并由使用者成图签署。全部通过后，建立 Windows x64 / Blender 5.1.1 的 `v1.0.0` 标签构建、草稿 GitHub Release、确切 ZIP 复核和 Blender Extensions 上传机制。

验收清单：[SOP](../../docs/v1-acceptance/SOP.md)；样本与缺口：[SOURCES](../../docs/v1-acceptance/SOURCES.md)。

## 顺序

1. [01 样本来源与清单](issues/01-sources-and-sop.md)：S01–S35 真实样本已固定，摘要与来源核对 Passed。
2. [04 Agent 技术复跑](issues/04-agent-replay.md)：C01–C13 六栏与 N01–N18 Passed；技术证据不替代独立人工签署。
3. [优化轨迹浏览](../optimization-trajectory/spec.md)及技术验证已 Passed；人工阶段须确定确切候选，安排 VMD/VESTA 同输入同参数外部视觉对照；当前为 Not Run。
4. [02 独立人工验收](issues/02-human-acceptance.md)：使用者操作、渲染、冷重开与签署；Agent 可整理/修复并要求重做受影响例，不代签。
5. [03 发布机制](issues/03-release-mechanism.md)：仅在 02 全部通过后领取；先本地实现并验证工作流，再按明确批准执行对外动作。

正式 v1 任一案例 `Failed` 或 `Not Run`，或许可/包资格未通过时，维持正式候选状态，不推送 v1 发布标签、不公开正式 Release、不上传 Blender Extensions。后续功能候选和固定 SOP 候选分别保留证据；人工验收必须记录实际使用的候选摘要。

## 单独的 Alpha 准备与发布

用户批准的 [alpha-readiness](../alpha-readiness/spec.md) 单独准备 manifest 0.1.0 / 注释标签 v0.1.0 / GitHub prerelease。Alpha 要求本批技术资格、组件许可复核、独立短 SOP 试装和维护者明确公开批准，不要求提前完成全部正式 v1 案例。本规格 02/03 继续受完整独立人工与科研验收阻塞，不因 Alpha 准备或发布而 resolved。
