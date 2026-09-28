# A 固定局部选择
Triage: ready-for-agent
Status: resolved

按 ../spec.md 的 A 合同实现纯 Python 选择和 Blender 操作模块。独占新 atom_selection.py、blender/atom_selection.py 与专用测试；不修改共享入口。

验收：编号/邻域/集合运算/氢掩码独立、源身份、固定成员、独立图层、失败无变化、保存及冷重开。Blender: Passed。

## Comments

- 2026-09-28 主代理验收 Passed：`outputs/molecularnodes-parameters/01-selection-r2/qualification.json` 绑定独立候选、安装副本、53 项科学回归、真实优化/IRC、GUI 选择/撤销/重做/错误提示、参数复制与 Gaussian 多段回归，以及原目录和移动目录的新进程重开。候选摘要及边界见 `docs/MOLECULARNODES_PARAMETERS.md`。

- 2026-09-28: A 纯 Python 编号、邻域、集合运算与显式重算已实现；Blender 局部布尔掩码通过现有氢门前的节点门与原有选择求交，复制层拒绝 IRC。`copy_selection(source, target)` 可从自定义源图复制经核验的掩码，目标图严格预检；无局部记录时 no-op。Passed: Blender 5.1 随附 Python 的 5 项纯 Python 测试、`py_compile`、`git diff --check`。Not Run: Blender GUI/MCP、保存和冷重开、完整安装包验收；本任务保持 claimed，待主代理集成与验收。
