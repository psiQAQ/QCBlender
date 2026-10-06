# 03 数据迁移

Triage: ready-for-agent
Status: pending
Blocked by: 01
Owner: data agent

## Scope

负责 `validation/shared/data/`、`validation/agent/packages/`、数据当前索引、必要 tools/tests 路径适配、`.gitignore` 及迁移报告/工具。冻结 `docs/v1-acceptance/tutorial-samples.json` 内容不变；历史报告原字节不变。未跟踪数据先复制保全，不删除旧原件。安装包 shared/install 由主 Agent 集中。

## Acceptance

公开 30 输入和许可证齐全、CSV 同组相对引用有效；本地稳定 key 可用且无公开重复原件；单文件/目录 key、REFERENCE_ROOT 和边界拒绝通过；相关回归与冻结公开包检查通过，未执行检查明确列出。迁移映射可供 main 重放，旧原件删除待任务 06 确认。

## Comments
