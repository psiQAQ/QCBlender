# 分组参数面板

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按 ../spec.md 第一包实现。独占 parameters.py、ui.py；直接绑定实际节点，保留未知输入高级入口与已有 operator。

## Comments

Blender 验收由主代理执行；未运行时标为 Not Run。

2026-09-28：已合并 `1992f3d`、`67f8af9`；45 项科学回归、独立安装、三种原子/表面样式、MCP 撤销/重做、保存及两次冷重开 Passed。证据：`outputs/vmd-parameters/01-panel/`，汇总见 `docs/acceptance/vmd-parameters.md`。

最终 `04-copy-r4` 通过 Computer Use 切换实体样式并核对字段单位、MO 相位标签；GUI 工程保存、原地与移动冷重开 Passed。完整证据见 `04-copy-r4/gui-checks.json` 和 `gui/checks.json`，技术任务完成。
