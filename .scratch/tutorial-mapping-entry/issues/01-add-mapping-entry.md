Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: none

# 加入旧多选映射入口

## 验收
限定接收对象类型和恰好两对象选择，在右键和顶部 Object 菜单提供既有 operator。完成非 Blender 静态检查；主 Agent 在默认 Developer Extras 关闭下完成 GUI/F3 实际复验后更新 resolved。

## Answer
QCBLENDER_MT_object.draw 提供 qcblender.map_scalar，保留原英文 label，限定 field/slice/atoms 接收对象和恰好两个选中对象。qcblender/__init__.py 对 VIEW3D_MT_object_context_menu 和 VIEW3D_MT_object 对称追加、移除同一 object_context_menu 回调。原 operator 的 poll、参数对话框和 execute 未修改。

## Validation
- Passed: Python 3.13 AST parse 和 compile（不导入 bpy、不执行模块）。
- Passed: git diff --check。
- Passed: AST 对称注册断言：register/unregister 各包含两个目标菜单的同一回调，且新增注册处于 _hooks_registered=True 之前、注销处于同一现有 guard 内。
- Passed: 源码编码与换行约定保留；本次源码仅新增两个回调注册/注销行。
- Not Run: Blender 运行、F3 检索、菜单点击、映射科学结果和安装验证；由主 Agent 在独占进程中复验。

## Comments
- 官方 Blender 发布说明与 Python API 示例支持通过顶部 Object 菜单提供入口；普通 F3 的发现性以主 Agent 实测为准。
- 历次候选与失败证据见主 Agent 管理的 outputs/evidence/2026-10-01/tutorial-cu/full/C04/legacy；本任务不修改这些产物。
