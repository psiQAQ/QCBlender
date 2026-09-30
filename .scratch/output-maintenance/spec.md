# 工作树与 outputs 维护统一

Triage: ready-for-agent
Status: claimed
Type: task
Baseline: main@f6418a4
Branch: chore/output-maintenance

## 目标与验收

按批准方案统一仓库内 .worktrees 开发、ff-only 合并、带注释 archive 标签和分支清理；分类历史 outputs，保留最新待验收包、共用环境、用户工程、必要输入和可复核证据。修改根指令、维护规则、唯一产物路由及既有清理工具和测试；不修改产品、依赖版本或全局记忆，不 push。

## 任务

- 01：规则、policy 工具与边界测试。
- 02：盘点、证据迁移、用户工程保全和按清单清理；依赖 01。
- 03：验证、路由与收据、合并和归档；依赖 01，可核对 02 的部分清理结果。

权限拒绝、链接、未知归属和活跃环境保留；实际删除失败不计入完成。不继承历史验证状态。
