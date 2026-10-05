# 11 Alpha 工作树磁盘残留

Triage: ready-for-human
Status: pending
Blocked by: 08

## 工作与验收

确认 `.worktrees/alpha-core` 残留对象的权限及可读性发生可核验变化后，重新审查保全清单并执行普通清理。不得修改 ACL、取得所有权或强制删除。此任务不阻塞已完成的本地 Git 归档和候选技术验证。

## Comments

2026-10-05：`git worktree remove` 返回 Directory not empty；Git 登记及 `feat/alpha-core` 分支已正常移除。四个缓存目录不可枚举，完整路径与失败输出保存在 `docs/acceptance/alpha-readiness-delivery.json`。已枚举内容全部保全，并在清理后再次验证摘要。清理 Failed，残留原位保留；未执行权限变更。其他三个 Alpha 工作树的磁盘移除 Passed。
