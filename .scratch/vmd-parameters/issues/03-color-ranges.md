# 异步色标范围

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: none

按 ../spec.md 第三包实现；纯计算/worker 可并行，主代理提供 Blender 操作，集成验收依赖 02。

## Comments

取消或源身份变化时不应用结果；不生成新科学 Dataset。

2026-09-28：已合并纯统计、worker、操作入口和完整绑定身份校验。`03-ranges-r2` 的对称范围、真实 ESP 异步读取、取消、来源/范围中途变化、常量/无有效点、撤销重做、双冷重开 Passed。最终 `04-copy-r4` 复验真实 ESP 与 C07 着色角色范围，48 项科学回归与安装 Passed。Computer Use 待桌面恢复，Status 保持 claimed；证据见 `docs/acceptance/vmd-parameters.md`。
