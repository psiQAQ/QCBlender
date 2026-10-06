# 04 Agent 校验与清理清单

Triage: ready-for-agent
Status: resolved
Blocked by: 01
Owner: validation agent

## Scope

负责 `validation/agent/` 中的 README、COVERAGE、CLEANUP、只读清理盘点工具及清单；不修改 packages、LOCAL-CASES 或其他任务文件。旧 A/C/N/P1 检查映射到现有工具和人工章节。按候选用途盘点，不按后缀统一删除。

## Acceptance

保留最新 190e11e 候选；旧安装包、有名/匿名重复包、样本包、复现工程包、CI 容器和损坏下载分别列明准确路径、大小、理由、文件身份和未检查范围。报告仅写真实执行状态；实现无删除行为。提交后等待主 Agent 分配合并轮次。

## Answer

已提供 `validation/agent/README.md` 的实际检查命令、`COVERAGE.md` 的 44 个旧编号映射、`CLEANUP.md` 的准确保留/待确认文件，以及 `tools/inventory_cleanup.py` 和其四项边界测试。

主检出只读快照在 `validation/agent/reports/2026-10-06/cleanup/inventory.json` 与 `inventory.md`：33 个待确认文件、1,216,475,400 字节，其中旧安装包 21 个、1,063,580,687 字节；保留最新 190e11e 整套及最新 CI 原始容器。19 个读取失败、434 个保护或排除目录有明确清单。没有删除旧文件，也没有启动 Blender。

- Passed：最新候选三份 ZIP 身份/CRC 与十份原报告核对；只读工具四项测试；44 个旧编号完整映射；54 个所引工具/测试路径存在；README 七段 PowerShell 语法；Python 语法与 `git diff --check`。
- Not Run：产品/Blender 复验、独立人工验收、实际清理。人工页面、主 Agent 的 `current-install.json`/`verify_workspace.py` 跨分支链接待串行整合后复核。

## Comments

2026-10-06：validation agent 在 `chore/validation-agent` 独立工作树领取；仅负责本任务范围。清理工具只读取源文件并生成候选清单，实际删除另由任务 06 确认。

2026-10-06：本子任务实施与自检完成；提交后等待串行合并轮次，跨分支链接与主检出综合复核由任务 05 完成。
