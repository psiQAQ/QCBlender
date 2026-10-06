# 01 用户操作正文与验收记录分离

Triage: ready-for-agent
Status: resolved

## 工作与验收

依照本主题规格整理 SOP，校验材料、覆盖、链接、脚本示例和历史保留；同步失真的入口说明，在独立工作树完成本地合并与归档。

## Comments

2026-10-06：用户要求剥离 SOP 中历史和无关说明，并纳入所附详细操作流程。主工作树 `docs/sop-user-guide`；C01–C05、C06–C13/X01、N01–N18 在独立工作树整理，由主 Agent 串行集成。附件中的 P1 包为历史候选；当前材料按已有 0.1.0 文件重新核对。

## Answer

Passed：SOP 正文整理为 827 行连续用户步骤，保留完整 A/C/X/N 覆盖并加入 P1-A/P1-B；393 张原截图及图注迁至 HISTORY，材料与模板独立维护。44 项编号、原 C/X 标题、链接/锚点、文件编码、三份材料大小/SHA-256、五段 PowerShell 语法检查通过。维护规则同步为用户正文与技术日志分别保存。证据在 `outputs/evidence/2026-10-06/sop-user-guide/`，由 ARTIFACTS 路由。

Not Run：Blender 实际复做与独立人工/科研签署。本次仅改文档，产品及依赖未变，既有人工任务保持原状态。本地归档标签 `archive/2026-10-06/docs/sop-user-guide`；提交与清理实际结果由证据目录的 delivery.json 记录。
