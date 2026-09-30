# 合并 main 并清理工作树

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: 05

## 目标与验收

- 01—05 验收后复核主检出、最终差异和保护对象，在 D:/workspace/QCBlender fast-forward 合并；不 push。
- 核对新旧工作树的提交、未跟踪及忽略内容，保全必要报告、候选、工程配套数据、独有输入和环境；记录路径映射和摘要。
- 清理目标为 f458/QCBlender 与 b48c/QCBlender；保留主检出，先旧后新，在主检出移除当前工作树。
- 未保全、未知归属、链接或权限拒绝项保持原位；不修改 ACL、取得所有权或强制删除。
- 核对 Git 登记、目录状态、提交可达性和归档摘要；保存主检出收据并提交任务收尾记录。所有条件满足才 resolved。

## Comments

- 2026-09-30：保全 Passed（b48c）：34,459 个文件、1,803,847,778 字节全部复制并逐文件核对源/副本 SHA-256，无链接或读取错误；f458 保全 Failed：14,489 个可读文件已归档，11 个目录和 3 个 ZIP 仍访问拒绝，保留该工作树。主检出归档为 outputs/cleanup-followup-20260930/{b48c,f458}，逐文件映射为 *-preserved.jsonl，完整收据为 preservation.json。
- 用户原有 PID 24852 的未保存工程已通过可见界面另存到主检出归档 user-session/未命名.blend + .qcdata；新可见 PID 47480 冷重开读取 Dataset、核对已存 manifest 摘要并记录所有科学数组摘要 Passed，证据为归档 qcf3/gui/user-cold-reopen.json 与两张保全截图。原会话及本轮验证进程均已正常退出。合并与当前工作树移除尚待执行，06 保持 claimed。

- 2026-09-30：01—05 均 resolved，领取任务。先复核 main 和保护对象、归档并核对逐文件摘要；受限旧工作树不强制移除。用户原有未保存 Blender 会话仍依赖 b48c 数据，必须先保全和冷重开后才可移除当前工作树。

- f458 的受限目录尚未完成保全，清理尚未执行。

- 2026-09-30：未领取，仅完成只读盘点。主检出仍在 47fd82c，Git 工作区无用户修改；两棵工作树仍登记。宿主及 Windows 扩展路径检查：f458 可读取 14,490 个文件，但 11 个目录和 3 个 portable.zip 仍访问拒绝，清单不完整，必须保留该工作树；b48c 可读取 24,294 个文件，无权限错误或链接。证据为 outputs/cleanup-followup/inventory/*-summary.json 与逐文件 JSONL 清单，记录大小和 SHA-256。清单中的单个 untracked 文件是 .git 指针，不是用户未跟踪内容。未迁移、合并或删除任何对象，清理状态 Not Run。
