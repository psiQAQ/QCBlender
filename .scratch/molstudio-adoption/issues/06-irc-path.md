# 06 IRC 能量路径

Triage: ready-for-human
Status: resolved
Blocked by: none

## Delivery

使用者明确排列多个 FCHK 步序；读取对应构型与电子总能量，选择步时同步结构和能量位置。

## Acceptance

- 真实 IRC 序列与手工顺序核对；原子身份变化、缺能量和重复/漏步报错。
- Blender 逐步显示、工程冷重开、GUI 顺序操作有证据。

## Comments

由真实 FCHK 数值派生的构型序列通过显式步序、错误输入、Blender 步骤切换、能量曲线、保存重开及 GUI 撤销/重做检查。缺真实 IRC 序列，科学验收 `Not Run`。

2026-09-27：真实样本及 Agent 技术检查已补齐并 Passed，详见 [SOP 复跑任务](../../v1-acceptance/issues/04-agent-replay.md) 和 [样本来源](../../../docs/v1-acceptance/SOURCES.md)。上方 Comments 为历史记录；独立人工验收由 v1-acceptance 任务 02 维护。
