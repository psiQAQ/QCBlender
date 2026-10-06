# 04 迁移至 Agent 校验目录

Triage: ready-for-agent
Status: resolved
Blocked by: 02
Owner: main agent; tool paths: docs_v1_audit

## Scope

将 docs/v1-acceptance 和 docs/acceptance 迁至 validation/agent/；主 Agent 维护移动、Markdown、AGENTS 指针及归档，子 Agent 在独立工作树修改工具和测试。

## Acceptance

当前入口、链接和工具使用新路径；历史机器报告、冻结清单和419张截图保持主检出迁移前字节，原路径有明确映射。相关自动测试、实际样本包和公开材料检查通过，旧布局发布标签可验证。仅本地提交和归档，不改变独立人工状态。

## Answer

454个文件迁至新目录；436份非 Markdown 材料字节核对 Passed，16份历史正文仅重写链接。操作登记表的263条截图引用按公开路径映射定位，240张独有截图与原摘要一致。48项候选/发布/数据准备测试和实际冻结包检查 Passed，包括真实新旧布局 Git 标签及缺失记录拒绝。

数据准备会校验样本包目录 README：路径更新后的当前大小/摘要已同步迁移表，原来源身份保存在 source_identity。冻结 ZIP、科学输入及来源字段未改。main@10576e7 的实际冻结样本、数据准备及当前教程材料复核 Passed；138份文档、1,286个本地链接/锚点零错误。证据目录为 validation/agent/reports/2026-10-06/docs-organize/migration/；最终本地归档由上一级 delivery.json 记录。Blender、远端 CI、独立人工和科研复验 Not Run。
