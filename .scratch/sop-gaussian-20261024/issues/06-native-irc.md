# Gaussian 原生 IRC 续查

Triage: ready-for-agent
Status: resolved
Blocked by: 01, 03, 05

## 验收

复盘原生 Gaussian IRC 的失败输入、实际接受步与终止条件，针对证据用现有服务端 Gaussian 继续尝试完整双向路径。沿用 RHF/STO-3G、电荷 0、单重态，按已批准的资源上限串行执行，资源与运行收据私存。正常结束不能单独证明路径完整；需核对两侧实际路径、末端梯度与极小点频率。

保留既有 Gaussian-v1 数据、v3 包、geomeTRIC 有效结果和所有原始尝试，新尝试与私有收据单独存放在忽略目录。公开结论只记录科学条件、实际结果与可复核身份。完成后本地提交并归档，不 push。

## Comments

起点 `3e678c2`，工作区干净。本批先建立能识别“仅一个接受点却正常结束”的检查，再据实选择单变量尝试；不重跑未受影响的 Blender、截图、工程或网站验证。

Answer：常规单作业的假极小点早停和首点校正失败仍可复现，旧 Restart 另有 Hessian 更新失败；20 项对照保留原件。用官方 Downhill 从真实接受点开新段，得到 Gaussian 原生 GS2 两侧各 26 段、TS 在内共 53 帧。父构型/接受点/实际波函数对应、逐点下降、端点梯度与六正频、53 份 FCHK 原件身份及 318 项 Mayer/IRC 解析通过。234 个补充文件、移动副本、隐私与文档检查通过；190 个保护对象未变。GUI、独立科研签署未执行；未将分段结果冒充单作业修复。权威报告为 `validation/agent/reports/2026-10-24/gaussian-sop/native-irc.md`，补充数据为 `validation/shared/data/public/gaussian-native-irc-v1/`。本地提交归档，不 push。
