# ETS-NOCV 完整冲突校验

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按上级spec修复AUDIT-03；文件归属qcblender/external_results.py、tests/test_science_nocv_status.py及本任务记录。不更新其他共享文档。分别改变遗漏字段的失败/通过证据、真实表及零值对照记录于Answer。

## Comments

- 2026-10-03：原缺陷在main复现：冲突行静默保留首条。

## Answer

- 修复：同 `(spin, pair)` 的重复行逐项精确比较全部规范化字段，唯一排除 `source_line`；单位参与比较。冲突保留 `Conflicting ETS-NOCV pair`，列出全部不一致字段及首条、重复条来源行号。相同重复保留首行记录及来源，不使用浮点近似容差。
- **Failed（修复前预期 RED）**：在 `26fa9c9` 基线上先增加并实际运行 `test_duplicate_scientific_field_conflicts`，仅独立变更 `positive_eigenvalue`、`negative_eigenvalue`、`positive_energy`、`negative_energy`。四个 subTest 均为 `AssertionError: ValueError not raised`；1 test，4 failures，exit 1。
- **Passed（修复后 GREEN）**：`test_science_nocv_status.py` 的11项及 `test_science_result_filters.py` 的4项，共15 tests通过（exit 0）。覆盖四个遗漏字段、pair energy及正负轨道编号冲突、多字段错误、极小数值差异、Alpha/Beta身份、规范化相同重复保留首行、两种合法单位和显式单位拒绝、合法零值与明确未计算占位。
- **Passed（真实输入）**：通过 `QCBLENDER_REFERENCE_ROOT=D:/workspace/QCBlender` 读取真实 COBH3 表及stdout；真实表9行保持原科学数值和来源，第1条来源行7。重复完整真实表保留首表全部记录；在第二表独立变更正负本征值及正负单轨道能量均报对应字段和两条实际来源行。
- **Passed（原审计复现）**：`outputs/evidence/2026-10-03/plugin-audit/logic/nocv-scientific-conflict.txt` 现报四字段冲突、来源行2和5；pair-energy冲突仍拒绝，相同重复仍保留来源行2。
- 运行：PowerShell，工作目录 `.worktrees/nocv-conflicts`；`& 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe' -B outputs/nocv-fix/verify.py`。该脚本显式加入主仓库 `outputs/science` 并设置真实输入根；证据为工作树 `outputs/nocv-fix/green-tests.txt`、`original-repro-green.json`。未安装或更新依赖。
- **Passed**：`git diff --check`。**Not Run**：Blender入口、候选构建、保存/冷重开及独立人工验收，由主Agent综合验证；本任务未启动Blender。
