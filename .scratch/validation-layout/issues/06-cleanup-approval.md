# 06 确认并清理历史文件

Triage: ready-for-human
Status: pending
Blocked by: 05
Owner: main agent and maintainer

## Scope

主 Agent 在新入口可用、迁移副本和报告保全后，提交准确保留/删除清单。只有用户明确确认清单后执行对应删除。旧安装包、重复输入、CI 容器、第三方不完整下载分别确认；未知、拒绝访问及用户工程原位保留。

## Acceptance

记录用户确认范围；逐文件再次核对路径和未变更状态，正常删除并保留收据。核对保留对象、主分支和入口；失败项保留，不把未执行或权限拒绝记为完成。

## Comments

2026-10-06：用户已批准计划落地与实施，尚未批准逐文件删除清单。本任务保持 pending。
