# 06 文档工作树空目录残留
Triage: ready-for-human
Status: pending

## Comments

2026-10-15：正常 `git worktree remove` 已移除 Git 登记，但删除 `D:\workspace\QCBlender\.worktrees\i18n-docs` 返回 `Permission denied`；目录枚举为空。提交已合入 main，注释标签 `archive/2026-10-15/docs/i18n-sop` 可达，分支已正常删除，所有忽略证据先保全并核对摘要。保留空目录，不修改权限、不强制删除。

原始证据：`validation/agent/reports/2026-10-15/i18n/archive-local.json`、`worktree-retention.json`。产品实现与全局安装已完成，此项只跟踪目录清理。

占用或权限问题解除后，仅在确认仍为空时，可在 PowerShell 执行以下非递归删除；不使用 `-Force`。

```powershell
$residue = 'D:\workspace\QCBlender\.worktrees\i18n-docs'
if (Test-Path -LiteralPath $residue) {
    $entry = Get-Item -LiteralPath $residue
    if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw '拒绝处理链接目录' }
    if (@(Get-ChildItem -LiteralPath $residue -Force).Count -ne 0) { throw '目录不再为空，停止删除' }
    Remove-Item -LiteralPath $residue
}
```
