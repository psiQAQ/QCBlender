# 04 SOP Agent 全流程复跑

Triage: ready-for-human
Status: resolved
Type: task

## 工作与验收

执行用户于 2026-09-26 批准的 SOP 全流程复跑计划：C01–C13、N01–N18，补齐可追溯真实样本，GUI 操作配合 Blender MCP 核对，修复并复验；不填写独立人工签名。当前用户已授权分批本地提交修复及工作流迁移，不推送或发布。

技术报告：[Agent 复跑记录](../../../docs/v1-acceptance/AGENT-REPLAY.md)。

进度与证据索引：`outputs/v1-acceptance/replay/`。每例六项检查按 `Passed / Failed / Not Run` 记录，未验证的项目不能计入通过。

## Comments

2026-09-26：开始实施。ZIP SHA-256 `524ed52f4b71f8ce01ea7d4e702acb7847a956d6b69e40cad28e3b089282951d`；S01–S11 摘要已核对。Computer Use 可用。`blender-mcp --help` 在沙箱外成功，启动器没有损坏；沙箱内的路径错误属于访问限制，不需要重新安装。

2026-09-27：当前 ZIP 为 ace35d52a9f0ee967e07921293d488fa5788b76e8fc28294455bcd6e725a6f4b。UI-01/UI-02/PORT-01 修复通过；C01–C06、C10–C11 六项技术检查 Passed，C01–C03 首次 GUI 已确认，其余待补。科学 20/20、干净安装、源码/ZIP/安装一致性和 24 个样本摘要 Passed。报告为 outputs/v1-acceptance/AGENT-REPLAY.md。

2026-09-27 更新：Computer Use 已恢复，用户提供并授权使用本地 Multiwfn 2026.9.20。S01–S35 全部真实样本齐备且摘要匹配。ESP-01 修复真实 Multiwfn 最大/最小值独立编号的解析问题；当前 ZIP 为 03311fdeb0c83a38a546ebddedee1fe05e8dcb7260b53c889dd9fee3fa7ee231。C07/C08/C09/C12/C13 已完成导入、数值、节点和 PNG，正在最终候选完整复跑及冷重开。科学回归 20/20 Passed，全新配置离线安装 Passed。人工结果/签名不变，未提交、推送、发布。

2026-09-27 完成：固定03311候选 C01–C13 六栏、N01–N18全部Passed；26个独立可见进程的原目录/移动目录冷重开与重渲染全部通过。35/35样本、20/20科学回归、干净离线安装与移动冷重开、源码/ZIP/两套安装一致性通过。证据索引 outputs/v1-acceptance/replay/evidence-index.json；总报告 outputs/v1-acceptance/AGENT-REPLAY.md。独立人工验收及发布批准继续由用户填写。
