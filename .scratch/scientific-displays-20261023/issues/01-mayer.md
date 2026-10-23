# 01 IRC Mayer 逐键着色

Triage: ready-for-agent
Status: resolved

## Delivery

按 [规格](../spec.md) 实施可撤销 Mayer 显示、整路径固定色域、阈值筛选及 IRC 联动，保留原科学数组、原子编号和数据导出。

## Acceptance

P04 数值与几何绑定、过滤、错误预检、切步、GUI、渲染、Undo/Redo、便携工程冷读、最终整包隔离安装。

## Comments

2026-10-23：在 `feat/irc-mayer-color` 领取。主检出现有研究/子模块改动不在本任务提交范围。

2026-10-23：非 Blender 实现与定向检查完成。用户确认 Blender 已关闭、无需恢复原工程后，真实 P04 原生、渲染及新进程冷读通过；图例排版问题已修复。继续最终整包隔离安装与 GUI 验证，未合入 main。

2026-10-23：最终完整候选、131 成员隔离安装、原生 P04、实际中文 GUI 开关/阈值/切步/撤销/菜单重做、便携工程及冷重开 Passed。产品提交 `4b90967`；证据见 [Mayer 验收](../../../validation/agent/acceptance/mayer.md)。按授权本地 ff-only 合入及归档，不推送；02–05 继续等待真实参照前置。
