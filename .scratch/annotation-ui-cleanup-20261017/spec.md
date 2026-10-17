# 标注工作树权限诊断与归档清理
Triage: ready-for-agent
Status: resolved

## 目标与范围

用户要求检查 `.worktrees/annotation-ui` 权限，保全必要产物后完成本地归档清理；不得修改 ACL、取得所有权或强制删除。原任务已有本地提交、ff-only 合并和注释标签授权，不包含 push。

## 验收

核对四个目录在现有创建账户与日常账户下的读取结果。生成逐文件摘要和保全归档，将三套测试 `.blend + .qcdata` 复制到主仓库批次目录，在相同安装环境冷读。正常清理四个创建账户拥有的目录，再通过 `tools.dev_workflow finish` 保全剩余忽略文件、正常移除工作树和已合并分支。原标签不变；当前安装包、稳定候选、旧安装与偏好备份、报告保持摘要相同。同步产物入口、验收记录和 CHANGELOG。

## Comments

- 2026-10-17：main `2d6adf4` 干净，原工作树提交 `74ca98d` 已合入 main，原归档标签身份匹配。记录工作树 `.worktrees/annotation-ui-cleanup`，分支 `chore/annotation-ui-cleanup`。
- 2026-10-17：同一四路径在创建账户下可读，在日常用户账户下拒绝。Owner 为创建账户，ACL 仅 Owner Rights、SYSTEM、Administrators。`copy_dataset` 使用私有临时目录后发布到最终路径；本次不修改产品代码或 ACL。
- 2026-10-17：18 个受限文件 / 14,908 字节已归档并从日常账户核对，三套工程 37 个文件逐摘要复制成功。批次 `outputs/runs/annotation-ui-cleanup-20261017/`。删除未执行；发现新 Blender PID 70728，已请用户保存关闭后再进行副本冷读，不操作用户进程。

- 2026-10-17：用户批准保存关闭 Blender 后，三套保全工程新进程冷读 Passed。四个创建账户专属目录和其余 8,851 个忽略文件已分账户归档，原工作树及已合并分支正常移除；标签身份不变，当前候选和备份摘要复核 Passed。未修改 ACL、取得所有权或强制删除。清理报告 `validation/agent/acceptance/annotation-ui-cleanup.md`，完整收据 `outputs/runs/annotation-ui-cleanup-20261017/acceptance.json`。

## Answer

已完成账户差异诊断、逐文件保全、三套副本冷读及正常清理。原归档标签不变，无拒绝残留、无 ACL 或所有权变更、无强制删除；用户明确无需恢复工程，所有本批 Blender 进程已退出。
