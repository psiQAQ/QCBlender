# B 场景编号与结构测量
Triage: ready-for-agent
Status: resolved

按 ../spec.md 的 B 合同实现纯 Python 数学及原生 FONT/CURVE 标注模块。独占新 measurements.py、blender/annotations.py 与专用测试；不修改共享入口。

验收：静态/优化/IRC 数据值、带符号二面角与退化、随步更新、布局/显隐/朝向、复制删除与冷重开。Blender: Passed。

## Comments

- 2026-09-28 主代理集成验收 Passed：`outputs/molecularnodes-parameters/02-annotations/qualification.json`。58 项科学回归、真实静态/优化/IRC 数值和锚点、非均匀缩放、真实振动、退化显示、损坏标注的换步事务、复制/删除/升级、GUI 入口和错误提示、撤销/重做、原地及移动冷重开均通过；独立人工验收 Not Run。

- 2026-09-28: B 模块与纯数值测试已实现；`measure` 覆盖 source/optimization/IRC、带符号二面角与退化。`update_annotations`、`copy_annotations`、`remove_annotations` 供主代理集成。纯 Python 测试 Passed；Blender 场景、GUI、保存冷重开 Not Run，保持 claimed 待整体验收。
- 2026-09-28: 测量可见文字补充源构型或 Optimization/IRC Step N；创建和编辑前校验编号、范围及有限的外观参数。纯数值测试增至 5 项 Passed。
- 2026-09-28: 测量源构型文字改为默认字体可显示的 `Source geometry`；EXEC_DEFAULT 按测量类型应用默认精度并保留显式精度；不同编号原子坐标重合时距离为 0 Å。
- 2026-09-28: 标注更新拆成无场景写入的 `prepare_annotations` 与 `apply_annotations`；复制预检源/目标身份及原生对象结构并清理失败副本。布局控件明确本地场景单位，选中标注子对象也可操作父 atom view。Blender 场景 Not Run。
- 2026-09-28: 编号解析拒绝空逗号段；二面角标注记录 B→C 轴、BA/CD 投影和 `atan2` 符号约定。
