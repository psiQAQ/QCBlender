# 工程内显示参数复制

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按 ../spec.md 第四包实现，集成验收依赖 03。三个复制组可选，先检查全部目标再修改；材料独立，数据和布局不变。

## Comments

只支持当前工程一次性复制，跨工程预设不在范围内。

2026-09-28：已合并 `5d4dd25`、`c5b559f` 及主代理集成修复。最终 `04-copy-r4` 的三组复制、全目标预检、材质/色带独立、旧电荷登记兼容、原子选择/布局/裁剪/图例保留、自定义分支拒绝、撤销重做及双冷重开 Passed。7 项复制策略、48 项科学和独立安装 Passed；完整候选摘要与复现记录见 `docs/acceptance/vmd-parameters.md`。

真实 Gaussian 两段 Log：worker 分段导入、同源不同 job 分组、跨段复制、目标振动模式/振幅/相位/选择/位置保留和双冷重开 Passed。证据 `04-copy-r4/real-log-views/checks.json`。

最终候选通过 Computer Use 三组复制、撤销及菜单重做，不兼容目标报错且状态不变。GUI 工程原地和移动冷重开 Passed，四个工作树保全归档并保留开发分支，技术任务完成。
