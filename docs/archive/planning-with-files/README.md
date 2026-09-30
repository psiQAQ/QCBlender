# planning-with-files 历史归档

2026-09-27 从 `.planning/` 逐字节归档。只作演进记录，不继续维护；旧状态、路径和操作授权不代表当前状态或授权。当前入口如下。2026-09-30 移除 `qcblender-v1/` 下三份重复迁移记录；它们的实施结论已在对应 M0–M8 任务保存，原文可用 `git show 1b877516:docs/archive/planning-with-files/qcblender-v1/<文件名>` 读取。设计及复跑子目录保留唯一决策/数值线索；下表仍是原迁移摘要，不表示所有文件继续存在。

| 内容 | 当前维护位置 |
| --- | --- |
| V1 实施、M0–M8 进度 | [规格及任务](../../../.scratch/qcblender-v1/spec.md) |
| 设计与研究 | [设计](../../QCBLENDER_V1_DESIGN.md)、[领域规则](../../agents/domain.md)、`docs/research/` |
| SOP 技术复跑 | [任务 04](../../../.scratch/v1-acceptance/issues/04-agent-replay.md)、[技术报告](../../v1-acceptance/AGENT-REPLAY.md) |
| 样本及计算条件 | [SOURCES](../../v1-acceptance/SOURCES.md)、`docs/research/sop-real-sources-*.md` |
| 缺陷与复验 | [开发问题记录](../../DEVELOPMENT_PITFALLS.md) |
| 独立人工验收与发布 | [验收规格](../../../.scratch/v1-acceptance/spec.md) |
| 后续工作流 | [任务规则](../../agents/issue-tracker.md) |

迁移前后逐字节核对：

| 原 `.planning/` 下路径 | SHA-256 |
| --- | --- |
| `qcblender-v1/design-archive/findings.md` | `3e0bb94ec682784b38131db37f7c5b05078631d9614cddc541dedda323e8f5d1` |
| `qcblender-v1/design-archive/progress.md` | `084d23d4490f2599b2c829fdb1dae5c8509699a681cd1eabdda265f9e2a524de` |
| `qcblender-v1/design-archive/task_plan.md` | `f43b848a30e5d235df47fef75488d3c0f5b9f7850fca6607be3b7d20af0dcc29` |
| `qcblender-v1/findings.md` | `491162098105ada5f752490aff01f2fd2bcc7327e9f79a48c18652d5e3f21873` |
| `qcblender-v1/progress.md` | `2ed629e8a035ba49f115240d04370d26f267543df80f791452dc4e7f7b35ac8c` |
| `qcblender-v1/task_plan.md` | `491162098105ada5f752490aff01f2fd2bcc7327e9f79a48c18652d5e3f21873` |
| `v1-acceptance-replay/findings.md` | `58eab8d6e6afa30102c4c5576e846b60fe88aa35ccd69533ba2251486fb04876` |
| `v1-acceptance-replay/progress.md` | `97bbbac2905587220fd8a0bc0bc3a105842ff8ff614188709c2f37766a949350` |
| `v1-acceptance-replay/task_plan.md` | `7d71baf292725efa575579802642ffbaf4a629a6234e733a697587c2b241ced9` |
