# 添加和编辑标注弹窗宽度减半
Triage: ready-for-agent
Status: resolved

## 目标与验收

添加和编辑标注的 `invoke_props_dialog` 宽度从 760 改为 380，保留现有字号、文字、横排 XYZ 和编号同行预览行为。工作树 `.worktrees/annotation-dialog-width`，分支 `fix/annotation-dialog-width`，main 起点 `78f504f`。

复用现有标注定向测试，实际 GUI 检查添加和编辑窗口；完整重建并隔离安装候选，再更新同一插件的日常安装，保全旧包与偏好，核对安装字节和保存冷读。沿用既有本地提交、ff-only 合入与归档授权，不 push。

## Comments

- 2026-10-17：main 干净，Blender 无进程。沿用用户已保存关闭且无需恢复工程的确认，本次无用户工程需要恢复。产品仅修改两个弹窗宽度参数。

- 2026-10-17：源码 `0c08219`，35 项定向、构建、隔离/日常安装、原生/GUI/日常冷读和窄窗口实际操作 Passed；候选 `8c23eaff…`，原失败与输入来源保留。详细证据见 `validation/agent/acceptance/annotation-width.md`，收尾走本地 ff-only 与统一 finish。
