# 05 流式摘要与同口径实验

Triage: ready-for-agent
Status: claimed
Blocked by: 01, 02, 03, 04

## 范围与验收

遵循spec第三批。先固化改动前候选，后流式摘要候选同机1预热5正式测64³/128³/256³冷/热，逐数组摘要及缓存命中一致。明确峰值/时间指标与门槛，不把历史P2数据当当前候选基线，不改变数组加载或求值策略。

## Comments

2026-10-05：01至04技术前置已resolved；固定改前产品982e339及prehash-candidate.json候选。开始同机64/128/256、1预热5正式冷热基线；实施范围仅data.py三处大文件摘要与worker写后VDB摘要。
