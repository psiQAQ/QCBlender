# [P0][总控] QCBlender 大扫除：只清理代码、规则与文档，不增加功能

Triage: ready-for-agent
Status: resolved
Type: task
Baseline: main@1b87751616ecb03d89f6a8c0e96cac99544b420a

## 目标

完成维护者提出的四项清理：清理冗余代码并列出死代码/重复逻辑清单；核验 AGENTS 规则，删除失效内容并为每条保留规则写明理由；重写用户导向 README；整理只描述当前状态的开发文档。

本轮不增加产品功能，不重新设计架构，不扩大支持范围。验收时间点为各子任务 PR 合并前及总任务关闭前，不以任意删除数量或未经约定的日期驱动修改。

## 本次交付状态

2026-09-30：已在隔离工作树按 01 → 06 依赖顺序完成清理。六个任务均 resolved，各自保存 Answer、Comments、范围和验证证据。代码删除/合并、规则核验与逐份文档处置见 [清单](issues/inventory.md)、[规则依据](issues/rules-review.md)、[文档处置](issues/documents.md)。

基线 `1b87751616ecb03d89f6a8c0e96cac99544b420a`；用户已授权提交并合并回本地 `main`。清理按代码、规则、文档三个主题保存，实际提交可由 `git log 1b877516..main` 追溯；科学候选仍由源码摘要和资格报告固定。原任务稿在主检出 `outputs/repository-cleanup-merge/original-task-drafts/` 保全，不进行远端发布。

## 任务划分与依赖

| 本地编号 | 任务 | 优先级 | 前置 |
| --- | --- | --- | --- |
| 01 | [建立清理清单与行为基线](issues/01-inventory-baseline.md) | P0 | 无 |
| 02 | [删除已证实的死代码与冗余实现](issues/02-dead-code.md) | P1 | 01 |
| 03 | [合并等价重复逻辑](issues/03-duplicate-logic.md) | P1 | 02 |
| 04 | [核验 AGENTS 并解释每条保留规则](issues/04-agent-rules.md) | P1 | 03 |
| 05 | [整理只描述当前状态的文档](issues/05-current-docs.md) | P1 | 04 |
| 06 | [重写用户导向 README](issues/06-user-readme.md) | P2 | 05 |

这些是本地任务编号，不是已创建的 GitHub Issue 编号。按顺序交付，避免同时修改节点公共代码、规则和文档而产生相互矛盾的结果。

## 共同边界

1. 不新增物理量、格式、平台、UI 操作或用户功能；不升级依赖和锁文件，不建立新注册框架、插件系统、测试平台或 CI 工程。允许增加直接证明清理安全的特征/回归测试。
2. 不改变科学输出、单位、容差、缺失值/错误语义、来源校验、异步取消、失败回滚、工程格式、节点资产 ID/socket 标识、Operator ID 或保存工程兼容性。发现行为缺陷单独记录，不夹带修复。
3. `qcblender/` 与 `qcblender/blender/` 的同名文件可能分别承担科学逻辑与 Blender 适配职责；不能按文件名合并。动态注册、RNA 回调、handlers/timers、字符串调用和资产/持久化引用都计入有效引用。
4. 只修改清单明确列出的受跟踪源码、测试和文档。不清理用户 `.blend/.qcdata`、原始科学输入、共享环境、下载资料或源码子模块；不改写 Git 历史/标签，不扩大磁盘清理权限。
5. 规则中的安全、科学正确性、许可证和人工验收边界，不因缺少直接 Python 调用而失效。产品不变性约束也不能因“未实现某功能”而删除。
6. 每个实施 PR 对应一个清理主题，列出删除/合并/保留项、理由、影响范围和验证结果。无法证明安全的候选保留并注明原因；不设置代码行数下降的硬指标。
7. 文档以最终状态写作，不保留无意义的自我纠错过程。变更证据放任务记录/PR；必要历史由 Git、任务记录和 CHANGELOG 追溯，不另造一套长期重复文档。

## 本地任务与远端 Issue 的关系

先读取当前仓库 AGENTS 及其引用规则。现行规则默认使用本地 Markdown，见 [docs/agents/issue-tracker.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/issue-tracker.md)；本轮维护者另行要求生成 GitHub Issue，不等于将整个项目迁移为远端任务系统。

本地使用本目录记录规格、领取状态、清理清单和证据。若发布远端 Issue，在对应本地任务记录真实 URL；远端关闭时指向完成的本地记录及提交。不要复制多套规则，也不要让本地未完成、远端却宣称完成。提交、PR、远端发布继续遵循当前用户授权；不要以技能流程代替授权。

## 本地 agent 执行入口

读取本文件后从任务 01 开始。记录实际 HEAD 和已有工作区改动；若任务涉及的源码已经变化，重新核对证据，不回退覆盖现有工作。按每个任务的 Blocked by 顺序推进，未验证项写 Not Run。不要为了清理扩大功能范围，也不要直接操作用户工程或运行未经审查的删除计划。

## 总体验收

- [x] 每个候选都有删除、合并、保留或待核实结论及证据；实际处置关联基线、主题提交与候选摘要。
- [x] 已确认且获准处理的代码冗余完成清理，剩余不确定项有原因。
- [x] 每条保留的项目规则都有一句具体理由及代码、工具、工作流或风险依据；失效规则删除，引用闭合。
- [x] 当前文档没有重复段落、失效操作步骤或冒充当前状态的旧候选结论；必要科学依据和限制仍可追溯。
- [x] README 主体面向用户，开发者分类入口置于最后；没有假下载入口或未经验证的支持承诺。
- [x] 在同一最终源码/新构建候选上执行受影响科学回归、非科学单测、Blender 安装/注册/注销、核心流程及保存冷重开，记录 Passed / Failed / Not Run。
- [x] 没有功能增量、数值契约变化、依赖升级、扩大授权或未经授权的资料删除。
- [x] 必要验证缺失时，不将总任务标记 resolved，不用历史 Passed 替代。

## 依据

[AGENTS.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/AGENTS.md) · [docs/DEVELOPMENT.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/DEVELOPMENT.md) · [docs/VALIDATION.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/VALIDATION.md) · [docs/agents/storage-maintenance.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/storage-maintenance.md)

## Comments

- 任务稿建立时曾尝试创建 GitHub Issue，返回 `403: Resource not accessible by integration`，远端创建数量 0；该记录不代表本轮需要再次发布。
- 2026-09-30：按用户指令执行本地 01–06；没有提交、推送或发布。重复导入/节点 helper、规则及文档清理完成，不能证明等价的 manifest/工具流程保留。
- 最终复核 Standards 0、Spec 0 未解决项。主工作区、92 项保护文件、3 个源码子模块固定身份与依赖锁保持，验证日志、新包和本轮工程保留。


## Answer

已删除五个未使用导入，两处数学节点构造复用既有 `assets.math`；项目规则逐条说明依据；当前指南、架构/契约、构建/验证及 README 完成整理。三份重复迁移记录删除，科学/许可依据、独立历史证据和未决任务保留。

最终 ZIP SHA-256：`2cd8bd76b22c3ac0d5cecfa519463a3bd01b0df797508f9f9eb730354b1d42fb`。69 项科学回归、11 项非科学单测、十组节点结构/行为、安装生命周期、实际求值/渲染、资产导出、图例与兼容、保存恢复及原地/中文移动冷重开 Passed；源码、ZIP 和两份安装副本一致。完整证据见 [03](issues/03-duplicate-logic.md) 与 [当前验证](../../docs/VALIDATION.md)。

全量历史 SOP、此次 GUI 手动逐次操作、独立人工验收、其他平台和公开发布为 Not Run。它们未被历史 Passed 或本次文档清理改写；本任务要求的受影响行为检查已执行。最终检查收据为 `outputs/repository-cleanup/final-checks.json`。

- 2026-09-30：用户追加“合并到本仓库中”，授权将已验证结果提交并合并回本地 main。此前未提交记录描述前一阶段；本次合并检查与原稿保全收据位于主检出 `outputs/repository-cleanup-merge/`。
