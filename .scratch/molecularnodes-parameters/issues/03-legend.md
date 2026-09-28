# C 图例排版
Triage: ready-for-agent
Status: claimed

按 ../spec.md 的 C 合同扩展已有 GN 图例，可抽取到 blender/legend.py，独占 scalars.py 的 add_legend 函数及专用测试。不改共享入口与复制检查。

验收：三点范围与原色带一致、横竖/大小/精度/旋转、旧默认、升级预检、保存冷重开。Blender: Not Run。

## Comments

- 2026-09-28: 已实现 GN 图例布局输入与显式 `qcblender.upgrade_legend`；仅预检通过的已知旧 QC 图例进入复制图升级，自定义连接拒绝。Passed: Python 3.13 纯布局测试、compileall、`git diff --check`。Not Run: Blender 5.1.1 节点执行、保存冷重开、GUI/MCP 与视觉验收；任务继续保持 claimed。
