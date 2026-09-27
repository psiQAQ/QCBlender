# 02 独立人工验收

Triage: ready-for-human
Status: pending
Type: task
Blocked by: 01

## 工作

排期：在 [优化轨迹浏览](../../optimization-trajectory/spec.md)及技术验证完成后，与外部视觉对照一起执行。当前仍为 **Not Run**；开始前确认最终候选及摘要，不将旧候选证据自动转移给新候选。

使用者按 `docs/v1-acceptance/SOP.md` 在 Blender 5.1.1 中逐例导入、核对源数值和单位、修改每个可用节点、渲染 PNG、保存及移动后冷重开。Agent 可整理证据、修复缺陷；受影响例须用新候选包重做。

## 验收

C01–C13 与 N01–N18 均有真实输入、结果、成品图、`.blend + .qcdata` 和使用者签名；九片分析的真实样本与用户成图全部完成。不得用自动化报告或 Agent 画面代签。

## Comments

2026-09-26：使用者在简体中文 Blender 5.1.1 导入时遇到材质节点查找失败；已修复并生成新候选 ZIP。当前打开的 Blender 工程有未保存修改，未在该会话中覆盖已安装扩展；使用者保存工程并重启后应安装 SOP 中的新 ZIP，重做受影响案例。Agent 未代签。

2026-09-23：尚未开始独立人工操作；所有结果均为 `Not Run`，签署栏为空。

2026-09-27：任务 01 来源整理与任务 04 Agent 技术复跑完成，固定候选见 SOP。UI-01/UI-02/PORT-01/ESP-01 修复与复验 Passed。独立人工检查仍为 Not Run，签名留空。
