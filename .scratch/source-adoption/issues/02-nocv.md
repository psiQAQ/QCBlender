# B ETS-NOCV 能量状态

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: none

## 实施

仅修改 `qcblender/external_results.py` 的 ETS-NOCV 解析，新增专用纯 Python 测试。按每张表附近的明确状态声明排除 not evaluated/all zero 占位表，后续已计算表仍可读；只有占位表给出专门错误。合法已计算零值不拒绝。显式未知或与用户选择冲突的单位拒绝；没有声明时使用已有必填 energy_unit 参数，不凭缺失声明假定 Hartree。保留正常 Alpha/Beta、pair 身份、重复冲突、原文行号和单位行为，不增加分析算法或新依赖。

## 验收

纯 Python：真实 COBH3 九对（pair 1 -77.88 kcal/mol）、仅占位、先占位后已计算、合法零值、单位缺失/错误/冲突。主代理：C12/C13 安装包路径导入、错误提示和场景完整性、保存移动冷重开。

## Comments

2026-09-27：用户批准；主代理负责 Blender 和最终状态。子代理将提交号、测试命令和结果追加于此。

2026-09-27：解析与纯 Python 测试提交 `3970ab2`。Passed：在 `adopt-nocv` 工作树设置 `QCBLENDER_REFERENCE_ROOT=D:\workspace\QCBlender`，运行 `C:\Program Files\Blender Foundation\Blender 5.1\5.1\python\bin\python.exe -I tests/test_science_nocv_status.py`，5 项测试通过；真实 COBH3 表读出 9 对，pair 1 为 -77.88 kcal/mol。`git diff --cached --check` Passed。Not Run：Blender 安装包导入、场景完整性、保存移动冷重开，由主代理验收。状态保持 claimed。
