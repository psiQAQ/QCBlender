# 06 遗留工作树与占用目录延期清理

Triage: ready-for-human
Status: pending
Blocked by: 03

## 目标与边界

当前仅剩旧f458磁盘残留；其工作树登记与已合并chore/repository-cleanup分支已移除，旧b48c目录已不存在。用户允许无法处理的分支暂时保留；此任务不阻塞本轮教程归档验收。

## Comments

2026-10-04重试：完成14,816文件/798,822,391字节保全与摘要核对，补存327文件；新Blender进程11组Dataset/600数组/8VDB读取Passed。git worktree remove返回Directory not empty但已移除Git登记，随后git branch -d成功；当前只剩main。f458残留目录普通Remove-Item仍访问拒绝，b48c已不存在，任务保持pending。完整收据、原件映射与错误见outputs/evidence/2026-10-04/legacy-worktree-retry/completion.json；科学恢复数据在outputs/projects/recovery/worktree-f458/datasets/。

2026-10-02 领取前状态：f458的11目录/3ZIP仍WinError 5，已有archive/2026-09-30/chore/repository-cleanup指向47fd82c且提交可达main；原位保留，不宣称完整保全。b48c空根仍WinError 32，占用进程未擅自终止。原始和最新检查见outputs/evidence/2026-10-02/tutorial-cu/deferred-cleanup/legacy-deferred.json。

## 完成标准

权限/占用由宿主或维护者解除后，重新盘点并保全全部原件、核对摘要和工程读取；复核主分支、标签与提交可达性，正常移除工作树及使用git branch -d删除已合并分支。b48c仅对确认空目录执行正常移除。保存新收据并更新ARTIFACTS和CHANGELOG后才resolved。当前授权不包含修改ACL、取得所有权、force删除或停止未知进程；条件未满足时保留pending。
