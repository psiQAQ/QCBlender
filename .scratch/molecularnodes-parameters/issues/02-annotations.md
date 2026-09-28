# B 场景编号与结构测量
Triage: ready-for-agent
Status: claimed

按 ../spec.md 的 B 合同实现纯 Python 数学及原生 FONT/CURVE 标注模块。独占新 measurements.py、blender/annotations.py 与专用测试；不修改共享入口。

验收：静态/优化/IRC 数据值、带符号二面角与退化、随步更新、布局/显隐/朝向、复制删除与冷重开。Blender: Not Run。

## Comments

- 2026-09-28: B 模块与纯数值测试已实现；`measure` 覆盖 source/optimization/IRC、带符号二面角与退化。`update_annotations`、`copy_annotations`、`remove_annotations` 供主代理集成。纯 Python 测试 Passed；Blender 场景、GUI、保存冷重开 Not Run，保持 claimed 待整体验收。
