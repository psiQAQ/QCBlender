# A AIM 属性关联校验

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: none

## 实施

仅修改 `qcblender/analysis_data.py` 的 AIM 导入校验，新增专用纯 Python 测试。CPprop 有类型/坐标时按编号与 CPs.pdb 核对，类型 C/N/O/F 分别对应 (3,-3)/(3,-1)/(3,+1)/(3,+3)。兼容 CP_type、CP type；逐轴坐标容差 0.0005001 Å。字段存在但格式损坏、非有限或冲突即拒绝。缺字段继续导入，并在已有 diagnostics 明确未核验；不扩 schema、不改公开导入接口、不修改 external_results.py。

## 验收

纯 Python：真实 C09 59 条 CP 正常；类型/坐标冲突、容差边界、缺字段、损坏内容分别检查。主代理：C09 真实导入和来源/属性核对；错误输入场景不增对象；诊断可见；保存移动冷重开。

## Comments

2026-09-27：用户批准；主代理负责 Blender 和最终状态。子代理将提交号、测试命令和结果追加于此。

2026-09-27：AIM 校验与专用测试提交 `16139eb`。Passed：真实 C09 59 CP / 58 路径、`CP_type` / `CP type`、类型与坐标冲突、逐轴容差两侧、缺字段诊断、损坏与非有限字段，4 个纯 Python 测试通过；`git diff --check` 通过。Not Run：Blender C09 导入、错误输入不增对象、诊断可见、保存移动冷重开，由主代理验收。

测试命令（PowerShell，工作目录 `D:\workspace\QCBlender\.worktrees\adopt-aim`；主目录样本与科学库只读）：

```powershell
$env:QCBLENDER_REFERENCE_ROOT='D:\workspace\QCBlender'
& 'C:\Program Files\Blender Foundation\Blender 5.1\5.1\python\bin\python.exe' -I -c "import sys,unittest; sys.path[:0]=[r'D:\workspace\QCBlender\.worktrees\adopt-aim',r'D:\workspace\QCBlender\outputs\science']; suite=unittest.defaultTestLoader.discover('tests',pattern='test_science_aim_association.py'); result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not result.wasSuccessful())"
```

2026-09-27：Spec 复核修复提交 `6986169`。真实 C09 属性表中同一 CP 的错误 `CP_type` 后接正确 `CP_type`、错误 `Position (Angstrom)` 后接正确坐标，以及无冒号裸行 `Position (Angstrom)`，修复前均被接受；现均拒绝。以上命令复验 **Passed：5/5**；`git diff --check` **Passed**。Blender 项仍 **Not Run**，Status 保持 claimed。
