# 分组参数面板

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: none

按 ../spec.md 第一包实现。独占 parameters.py、ui.py；直接绑定实际节点，保留未知输入高级入口与已有 operator。

## Comments

Blender 验收由主代理执行；未运行时标为 Not Run。

2026-09-28：已合并 `1992f3d`、`67f8af9`；45 项科学回归、独立安装、三种原子/表面样式、MCP 撤销/重做、保存及两次冷重开 Passed。证据：`outputs/vmd-parameters/01-panel/`，汇总见 `docs/acceptance/vmd-parameters.md`。

Computer Use 因桌面访问/监视器捕获失败仍 Not Run，未完成整批验收；Status 保持 claimed。
