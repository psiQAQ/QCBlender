# 11 Alpha 工作树磁盘残留

Triage: ready-for-human
Status: pending
Blocked by: 08

## 工作与验收

确认 `.worktrees/alpha-core` 残留对象的权限及可读性发生可核验变化后，重新审查保全清单并执行普通清理。不得修改 ACL、取得所有权或强制删除。此任务不阻塞已完成的本地 Git 归档和候选技术验证。

## Comments

2026-10-06：重试 `.worktrees/alpha-core` 普通清理。归档标签 `archive/2026-10-05/feat/alpha-core` 仍指向 `9cc9a005` 且可达 main；Git 工作树登记及任务分支已移除。按逐文件 SHA-256 清单删除 30,455 文件/2,671,377,950 字节，补存 7 文件/520,691,210 字节；7,503 份保全内容清理后摘要复核 Passed。现存仅 outputs，79 个扫描路径拒绝访问，目录完整移除 Failed，11 保持 pending；未修改 ACL/所有权或强制删除。清单、两批删除收据及最终复核在 `outputs/evidence/2026-10-06/alpha-core-cleanup/`，入口为 `final-verification.json`。产品测试及 Blender 复做 Not Run。

2026-10-05：`git worktree remove` 返回 Directory not empty；Git 登记及 `feat/alpha-core` 分支已正常移除。四个缓存目录不可枚举，完整路径与失败输出保存在 `docs/acceptance/alpha-readiness-delivery.json`。已枚举内容全部保全，并在清理后再次验证摘要。清理 Failed，残留原位保留；未执行权限变更。其他三个 Alpha 工作树的磁盘移除 Passed。
