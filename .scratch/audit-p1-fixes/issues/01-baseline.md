# 固定复现与接口

Triage: ready-for-agent
Status: resolved
Type: task

主Agent固定当前基线，复用真实P04/P02验证两项P1仍存在，保存本批失败断言与接口契约。源输入和历史失败证据不改写。

## Comments

- 2026-10-04：基线候选安装Passed。实际已安装operator运行8.54秒，四项缺陷均复现：IRC/优化异步骤仍关联成功，共享mesh切步污染原件；XYZ拒绝对照Passed。显式无缺陷断言按预期失败(exit 1)，报告为outputs/runs/audit-p1/1/baseline/blender/boundary-report.json，命令/日志为logs/baseline-red.*。接口已在spec固定。
