# 保存可复核验证索引

Triage: ready-for-agent
Status: pending
Type: task
Blocked by: 03, 04

## 目标与验收

- 在 docs/acceptance/cleanup-validation.json 保存唯一精简索引：提交、产品源码树与文件摘要、候选摘要、环境、命令、范围、报告摘要、保存位置和重建方法。
- 上轮证据和本轮复验分别记录；上轮 source-hashes 的 69 个文件已逐项匹配基线提交。
- VALIDATION 引用索引，当前状态不再描述为基线加未提交修改；CHANGELOG 记录本轮变化和保留情况。
- 全部引用可定位；不提交大文件或受限样本，不以历史 Passed 填补本轮 Not Run。

## Comments
