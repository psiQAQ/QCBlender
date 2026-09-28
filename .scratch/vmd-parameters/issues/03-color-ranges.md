# 异步色标范围

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按 ../spec.md 第三包实现；纯计算/worker 可并行，主代理提供 Blender 操作，集成验收依赖 02。

## Comments

取消或源身份变化时不应用结果；不生成新科学 Dataset。

2026-09-28：已合并纯统计、worker、操作入口和完整绑定身份校验。`03-ranges-r2` 的对称范围、真实 ESP 异步读取、取消、来源/范围中途变化、常量/无有效点、撤销重做、双冷重开 Passed。最终 `04-copy-r4` 复验真实 ESP 与 C07 着色角色范围，48 项科学回归与安装 Passed；证据见 `docs/acceptance/vmd-parameters.md`。

最终候选通过 Computer Use 输入 R=0.08 并应用对称范围，再点击读取真实 ESP 的 73508 个有效格点范围。GUI 工程双冷重开 Passed，技术任务完成。
