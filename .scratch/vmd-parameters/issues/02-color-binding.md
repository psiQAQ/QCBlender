# 显式着色场绑定

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按 ../spec.md 第二包实现。开发可并行；集成验收依赖 01。

## Comments

2026-09-28：已合并显式选择器、来源身份冻结及标准裁剪兼容。第二候选的真实密度/ESP、初建/替换、范围/图例保留、旧选择顺序入口、切片、错误图拒绝、MCP 撤销/重做、保存与原地/移动冷重开 Passed；45 项科学回归和独立安装 Passed。证据 `outputs/vmd-parameters/02-binding/`。

候选身份不采用文件名；先完整校验再变更引用、记录与图例。

最终 `04-copy-r4` 通过 Computer Use 选择同构型 ESP；不同分子的 MO 场明确拒绝，MCP 核对原映射和对象数不变。GUI 工程双冷重开 Passed，技术任务完成。
