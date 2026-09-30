# QCBlender 清理复查补丁

Triage: ready-for-agent
Status: claimed
Type: task
Baseline: main@47fd82cef8d340fe80d45756df8333518114490a
Branch: chore/cleanup-followup

## 目标与授权

补齐界面操作说明、首次构建顺序、节点回归断言和验证证据索引。用户已批准在当前隔离工作树实施、创建本地提交、验收后合并本地 main，并保全必要内容后清理本轮 b48c 与上轮 f458 工作树。允许在本轮 outputs 中安装已有锁定的开发与测试依赖；不推送或发布。

仅修改文档、测试与任务记录。产品功能、公共接口、科学契约、AGENTS、依赖版本及锁文件保持现状；README 展示样本和效果图不在本轮范围内。

## 任务

| 编号 | 任务 | 前置 | 分派 |
| --- | --- | --- | --- |
| 01 | [用户指南](issues/01-user-guide.md) | 无 | ready-for-agent |
| 02 | [节点回归断言](issues/02-node-assertions.md) | 无 | ready-for-agent |
| 03 | [首次构建与开发说明](issues/03-first-build.md) | 01、02 | ready-for-agent |
| 04 | [按指南点击界面](issues/04-guide-walkthrough.md) | 03 | ready-for-human |
| 05 | [可复核验证索引](issues/05-validation-index.md) | 03、04 | ready-for-agent |
| 06 | [合并与工作树清理](issues/06-merge-cleanup.md) | 05 | ready-for-agent |

任务只在前置 resolved 后领取，按 pending → claimed → resolved 维护；结果与证据记录在各任务 Answer / Comments。

## 验收与保留

- 使用新输出目录和同批候选，核对真实输入摘要，执行科学回归、相关非科学单测、节点检查、安装与生命周期、保存冷重开、资产及图例专项。
- 先提交文档与测试，固定被验证提交，再保存验证索引与结果。每项检查明确 Passed / Failed / Not Run，旧报告不替代本轮复验。
- 人工只依据修订后的指南点击能量、振动、剖面和保存入口，通过后才合并；独立科研验收签署继续单独维护，Agent 不代签。
- 精简索引受版本控制；候选、完整报告、工程与受限样本留在忽略目录，记录保存位置及重建步骤。
- 在主检出执行 fast-forward 合并；清理前保全独有证据、输入、环境及工程配套数据，逐项核对摘要和路径映射。先旧工作树，后当前工作树。
- f458 已发现 11 个目录访问拒绝。保全未完成时保留受影响工作树并记录阻塞，不修改 ACL、取得所有权或强制删除。

## Comments

- 2026-09-30：当前工作树及 main 的 HEAD 均为基线，受跟踪工作区干净。已创建本地分支；尚未运行本轮测试、合并或清理。
