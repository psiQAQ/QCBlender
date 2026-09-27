# 08 ETS-NOCV 表格

Triage: ready-for-human
Status: resolved
Blocked by: none

## Delivery

导入外部 ETS-NOCV 输出表，展示 pair、Alpha/Beta、成对能量、轨道编号和单位，保留原始文本来源。

## Acceptance

- 真实闭壳层与开壳层输出核对行数、数值及单位；空表、重复 pair、截断行报错。
- Blender 列表、保存重开和源摘要有证据。

## Comments

构造 ETS 文本通过单位、截断行、Blender 导入操作、列表、冷重开及 GUI 撤销/重做检查。缺真实闭壳层与开壳层输出，科学验收 `Not Run`。

2026-09-27：真实样本及 Agent 技术检查已补齐并 Passed，详见 [SOP 复跑任务](../../v1-acceptance/issues/04-agent-replay.md) 和 [样本来源](../../../docs/v1-acceptance/SOURCES.md)。上方 Comments 为历史记录；独立人工验收由 v1-acceptance 任务 02 维护。
