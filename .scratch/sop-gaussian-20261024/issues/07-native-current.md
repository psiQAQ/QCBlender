# 将原生 53 帧路径设为当前教程案例

Triage: ready-for-agent
Status: resolved
Blocked by: 06

## 目标

新增 Gaussian-v2 与 v4 样本包，以原生 GS2 分段续算的 53 帧（TS27）替换当前 P04 教程入口；P06 三帧映射到 1/27/53。保留 Gaussian-v1 的 69 帧数据、v3 包、旧工程和验证身份。

同步 SOP、配套工程、受影响截图和索引，实际执行 MCP、GUI 观察及串行冷重开；验证科学数组、Mayer 318 项、导出、移动与解包。复用当前有效安装，不 push。

## Comments

- 2026-10-24：开始时 main=459a1cc，工作区干净；`session list` 确认 Blender 进程为空，无用户工程恢复目标。在 `docs/native-irc-current-20261024` 分支实施。

## Answer

Gaussian-v2/v4 已设为当前入口，P04 原生53帧（TS27）、P06取1/27/53。新P04/P06工程、7张截图与全部映射已同步。50条MCP成功收据、实际GUI切帧和观察、4项串行冷读（含移动/解包）均Passed，0差异；51项工具检查、10项网站检查及当前独立材料通过。旧数据/工程/原生补充/v3共2,029文件未变，旧7图也保全。独立人工/科研和部署Not Run。

证据：[验收](../../../validation/agent/reports/2026-10-24/native-irc-current/acceptance.md)。按授权分项本地提交、快进main及带注释归档；不push。
