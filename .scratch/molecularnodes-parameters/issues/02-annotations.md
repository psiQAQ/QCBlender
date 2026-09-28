# B 场景编号与结构测量
Triage: ready-for-agent
Status: claimed

按 ../spec.md 的 B 合同实现纯 Python 数学及原生 FONT/CURVE 标注模块。独占新 measurements.py、blender/annotations.py 与专用测试；不修改共享入口。

验收：静态/优化/IRC 数据值、带符号二面角与退化、随步更新、布局/显隐/朝向、复制删除与冷重开。Blender: Not Run。

## Comments

- 2026-09-28: B 模块与纯数值测试已实现；`measure` 覆盖 source/optimization/IRC、带符号二面角与退化。`update_annotations`、`copy_annotations`、`remove_annotations` 供主代理集成。纯 Python 测试 Passed；Blender 场景、GUI、保存冷重开 Not Run，保持 claimed 待整体验收。
- 2026-09-28: 测量可见文字补充源构型或 Optimization/IRC Step N；创建和编辑前校验编号、范围及有限的外观参数。纯数值测试增至 5 项 Passed。
- 2026-09-28: 测量源构型文字改为默认字体可显示的 `Source geometry`；EXEC_DEFAULT 按测量类型应用默认精度并保留显式精度；不同编号原子坐标重合时距离为 0 Å。
