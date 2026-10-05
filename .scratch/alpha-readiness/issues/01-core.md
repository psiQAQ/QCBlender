# 01 资源、缓存与异步科学资格

Triage: ready-for-agent
Status: resolved

## 工作与验收

实施spec的1–3项，科学实现与worker/generate UI串行修改。完成小上限、512³提前拒绝、科学指纹及资格生命周期回归，原数值参考保持；主Agent后续以最终候选完成GUI/冷读验证。

## Comments

2026-10-05：主Agent领取。

## Answer

统一1 GiB序列化数组契约；加载两阶段路径/总大小检查，保存/VDB/缓存/归档复用同一限制。求值先估算保留输入、替换后输出及.npy头，驻留旧场另计工作预算；512³在prepare和数组分配前拒绝。科学身份覆盖六个科学实现文件及四个依赖，cache key保留输入/grid/科学参数/Blender，memory_mb继续不改变科学缓存身份。

生成点击先启动独立qualify_science异步作业，再由绑定一致的轻量预览打开参数对话框。已知不支持返回eligible=false，完整性/环境失败保留真实worker失败。对话框显示网格、点数、Dataset大小、求值估算、预算及拒绝原因；冷重开和注销清除资格。后台在cache lookup和求值前重做资格与资源核验，源manifest变化拒绝发布结果。

Passed：18项科学定向回归、5项资格UI边界、18项取消回归，共41项，无skip。报告outputs/core-regressions.json，执行脚本outputs/core_regressions.py；git diff --check通过。首次完整suite因工作树未准备outputs和受限本地输入失败，保留outputs/core-science-initial.json；不作为通过证据。综合最终候选/原生GUI/Undo/Redo由07验收，当前Not Run。

核心预审发现自动资格检查也需nAO²矩阵预算。现已在数组加载/prepare前，从经过路径/总大小核验的manifest描述符估算驻留输入与六个密度矩阵；预算拒绝独立于科学不支持，不缓存资格。可承受的预算不足由同源绑定预算对话框重试，超过16 GiB直接拒绝。新增20000×1小系数矩阵在任何数组读取前拒绝及预算重试生命周期回归；43项定向回归Passed。另已复制并SHA核验110个索引内受限输入，完整科学suite115项Passed、无skip；报告outputs/core-science-full.json（摘要整合前的核心身份）。
