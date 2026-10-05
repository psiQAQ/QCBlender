# 04 发布流程研究

Triage: ready-for-agent
Status: resolved

## 工作与验收

将已核对的MolecularNodes、ChemBlender和官方优秀插件流程形成单一研究文档，记录源码身份、永久链接、采用及不采用部分、Alpha/正式版门槛。保持事实与建议/未执行状态分开。

## Comments

2026-10-05：发布研究 Agent 已领取；按实际参考文件、固定源码身份与官方文档形成研究结论。本任务不触发远端 workflow、创建 Release 或执行 Blender。

## Answer

2026-10-05：完成 [GitHub 发布流程研究](../../../docs/research/github-release-workflow.md)。核对 MolecularNodes 固定子模块源码、ChemBlender 两份干净工作区 workflow 及 SHA-256、BlenderKit 官方 actions、Sverchok 官方安装/兼容说明和 GitHub/Blender 官方接口；采用候选构建与精确原附件推广分离，Alpha `0.1.0`/`v0.1.0` 草稿及人工公开门禁，正式 v1 独立签署前置保留。

源码/来源核查 Passed；文档差异格式检查 Passed。实际远端 CI、草稿创建、人工试装、公开批准及 Blender Extensions 均 Not Run。05 仍待 03 完成后领取，不从研究结论推导发布通过。
