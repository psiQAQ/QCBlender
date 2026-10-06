# 05 保留清单与执行

Triage: ready-for-agent
Status: resolved
Blocked by: 02, 03, 04
Owner: main agent

## Scope

保护用户工程、当前材料和环境，核对唯一科学来源、内容对象映射及批次摘要，生成准确退役清单。在重建与工具检查通过后按用户批准范围执行，保留变化/权限/未知项，清理确认空目录。

## Acceptance

执行前后保护摘要一致；所有删除有路径、摘要、用途和收据，失败记录原错误。提供已审查失败项的 PowerShell 删除命令和有身份复核的重试脚本。分别报告逻辑字节、磁盘变化及不可枚举范围。

## Answer

按普通权限精确清单删除 89,895 文件/8,545,515,461 字节，apply=Applied、保护预检Passed、删除失败0；成功逐文件收据为主检出 validation/agent/reports/2026-10-06/outputs-prune/apply/removed.jsonl.gz。清理后5,500个保护摘要、15个当前候选文件、210个补充只读保护对象核对Passed。确认空目录移除11,958个。

普通权限不可枚举/读取的5,039个已审查文件（739,869,148字节）保留；独立只读上下文已记录其SHA/stat，不混入普通apply。retry/commands.md给出准确路径、原错误及逐文件命令，retry-reviewed-files.ps1默认核验、-Apply才执行。五种自有fixture验证了正确删除及内容变化、时间变化、越界、目录拒绝；被改写清单整体拒绝，Passed。未知、用户与恢复对象不进入退役集合。用户工程新进程11原数组读回Passed，原工程未改写；未改ACL/所有权，没有force。
