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
