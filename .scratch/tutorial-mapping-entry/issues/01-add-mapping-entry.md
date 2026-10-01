Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

# 加入旧多选映射入口

## 验收
限定接收对象类型和恰好两对象选择，在右键和顶部 Object 菜单提供既有 operator。完成非 Blender 静态检查；主 Agent 已在默认 Developer Extras 关闭下完成 GUI/F3 实际复验。

## Answer
QCBLENDER_MT_object.draw 提供 qcblender.map_scalar，保留原英文 label，限定 field/slice/atoms 接收对象和恰好两个选中对象。qcblender/__init__.py 对 VIEW3D_MT_object_context_menu 和 VIEW3D_MT_object 对称追加、移除同一 object_context_menu 回调。原 operator 的 poll、参数对话框和 execute 未修改。

## Validation
- Passed: Python 3.13 AST parse 和 compile（不导入 bpy、不执行模块）。
- Passed: git diff --check。
- Passed: AST 对称注册断言：register/unregister 各包含两个目标菜单的同一回调，且新增注册处于 _hooks_registered=True 之前、注销处于同一现有 guard 内。
- Passed: 源码编码与换行约定保留；本次源码仅新增两个回调注册/注销行。
- Passed: 主 Agent 实际 Computer Use 确认 Object → QCBlender 子菜单可见、F3 完整英文标签可检索，并在新建未映射接收视图上确认参数对话框执行成功。
- Passed: 主 Agent 使用 MCP 设置选择并只读核对映射；162 顶点中 21 个 CPU 参考取样最大绝对误差 1.5265520153517897e-08 hartree/e。
- Not Run: 完整 C04 教程及独立人工签署。

## Comments
- 官方 Blender 发布说明与 Python API 示例支持通过顶部 Object 菜单提供入口；普通 F3 的发现性已由主 Agent 实测确认。
- 历次候选与失败证据见主 Agent 管理的 outputs/evidence/2026-10-01/tutorial-cu/full/C04/legacy；本任务不修改这些产物。

## GUI 验收证据
- Source commit: b7090967e6618c15449efec278bcd47a0f018d54
- Candidate ZIP SHA-256: 9795a9ea2c262f9c50f877a7373cf820a3a91794474817f515cdac4430dfe1d1
- 主 Agent 验证环境：Blender 5.1.1、zh_HANS、唯一可见 PID 10796、Developer Extras=false。
- 接收对象：QC electron_number_density.002；前置 fresh-unmapped-view.json 确认未映射。
- 结果：D:/workspace/QCBlender/outputs/evidence/2026-10-01/tutorial-cu/mapping-top-menu/GUI/F3-entry-and-sampling.json
- 前置：D:/workspace/QCBlender/outputs/evidence/2026-10-01/tutorial-cu/mapping-top-menu/GUI/fresh-unmapped-view.json
- 独立诊断：D:/workspace/QCBlender/outputs/evidence/2026-10-01/tutorial-cu/mapping-top-menu/GUI/already-mapped-rejection-diagnostic.json 记录已映射接收对象被既有保护逻辑拒绝；该记录不计为新映射执行成功。
- 本子 Agent 只读取上述证据并更新任务记录，未启动或连接 Blender。
