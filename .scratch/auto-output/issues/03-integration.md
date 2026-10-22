# 03 接入、实际验证、完整包和 SOP

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按 [spec](../spec.md) 接入完成模块并执行整体交付。前置结果已整合，Blender 会话由主 Agent 串行使用；用户确认已关闭原会话，并明确无需恢复原工程。

## Comments

2026-10-23：先准备几何读取、相机和界面，避免接入未经定向验证的算法结果。

2026-10-23：已领取接入与交付；59 项定向检查 Passed，真实 Blender 与候选安装待执行。用户确认无需恢复原工程。

2026-10-23：完成。累计去重 61 项定向检查、四类实际取景/渲染、科学数组及对象变换、共享场景隔离、GUI 撤销/重做/恢复、最终候选冷读与完整隔离安装 Passed。更新 SOP 第 8 步及对应截图、1280×720 实图。当前 ZIP 源码 8d2f83f，SHA-256 e73797010178657da9b950817f25a79786f2251832c9d04736c56b0dc00fa590；[验收](../../../validation/agent/acceptance/auto-output.md)。独立人工/科研、全量回归、日常安装和远端 CI Not Run。本地提交与工作树归档按项目流程收尾，不 push。

2026-10-23：用户追加授权日常安装且无需备份旧安装。相同候选已覆盖安装，128 成员一致、新进程自动启用、三种取景/三档实际渲染及保存冷读 Passed；[日常验证](../../../validation/agent/acceptance/auto-output.md#日常配置安装补充)。未重复日常 GUI 点击，独立人工/科研仍 Not Run。

2026-10-23：按追加要求补做日常 GUI 点击。主轴/减少遮挡、EEVEE 白底/Cycles 透明两次 1280×720 渲染、恢复原设置与副本冷读 Passed；科学数组和对象变换未变，原 P01 未覆盖。首轮观察脚本失败保留，经用户批准结束本批无响应进程，修正观察脚本后重试通过，产品代码未改动。[GUI 验收](../../../validation/agent/acceptance/auto-output.md#日常配置-gui-点击补充)。更新当前安装记录与操作登记表，按用户要求本地提交，不 push；独立人工/科研仍 Not Run。
