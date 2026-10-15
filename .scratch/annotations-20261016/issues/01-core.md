# 标注几何与生命周期
Triage: ready-for-agent
Status: resolved

实现范围与验收见 [spec](../spec.md)。分支 `feat/annotations-core`。

## Comments
- 旧版实际复现：共享文字材质后编辑抛错；先单条朝向、再全部朝向会继承上一条编号。证据 `validation/agent/reports/2026-10-16/annotations/repro-material.json`、`repro-face-single.json`、`repro-face-last-click.json`。
