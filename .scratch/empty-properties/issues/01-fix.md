Triage: ready-for-agent
Status: resolved

# 修复空场景查看对象属性并更新安装包

## Comments

- 2026-10-10：Blender 5.1.1 窗口原生复现 `TypeError: enum "OBJECT" not found`；后台运行未触发动态上下文限制。验证报告位于 `validation/agent/reports/2026-10-10/empty-properties/`。

## Answer

源码 `2989bd6` 在属性切换及固定对象前检查活动对象；缺失时提示选择对象并返回 CANCELLED。当前 ZIP 已替换并复核摘要。10 项原生窗口回归、安装后窗口/后台回归、152 项基础测试、离线安装/计算/渲染及中文路径冷重开 Passed。Computer Use 点击因 helper 故障 Not Run；独立人工验收 Not Run。证据、候选与重建方法见 `validation/agent/acceptance/empty-properties.md`；本地流程不包含 push。
