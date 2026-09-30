# 合并 main 并清理工作树

Triage: ready-for-agent
Status: pending
Type: task
Blocked by: 05

## 目标与验收

- 01—05 验收后复核主检出、最终差异和保护对象，在 D:/workspace/QCBlender fast-forward 合并；不 push。
- 核对新旧工作树的提交、未跟踪及忽略内容，保全必要报告、候选、工程配套数据、独有输入和环境；记录路径映射和摘要。
- 清理目标为 f458/QCBlender 与 b48c/QCBlender；保留主检出，先旧后新，在主检出移除当前工作树。
- 未保全、未知归属、链接或权限拒绝项保持原位；不修改 ACL、取得所有权或强制删除。
- 核对 Git 登记、目录状态、提交可达性和归档摘要；保存主检出收据并提交任务收尾记录。所有条件满足才 resolved。

## Comments

- f458 的受限目录尚未完成保全，清理尚未执行。
