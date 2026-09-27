# 本地 Markdown 任务跟踪

需求和规格保存在本仓库 `.scratch/`，创建或更新本地任务不执行远端发布。

- 每个功能一个目录：`.scratch/<feature-slug>/`。
- 规格为 `spec.md`；实现任务分别为 `issues/<NN>-<slug>.md`，从 01 编号。
- 任务顶部用 `Triage:` 保存分派标签，值遵循 [标签规则](triage-labels.md)。
- `Status:` 保存执行状态：`pending`（未领取）、`claimed`（进行中）、`resolved`（任务验收完成）。技能的 `Execution: complete` 对应 `Status: resolved`；技能将 triage 写入 `Status:` 时，改写至 `Triage:`。
- 讨论追加在任务文件的 `## Comments` 下，保留决策与证据。
- 技能要求发布到任务跟踪系统时，创建或更新对应本地文件。
- 技能要求读取任务时，按提供路径或编号读取；编号结合功能目录解释。

使用 wayfinder 时，地图为 `.scratch/<effort>/map.md`，子任务仍各自成文件。
`Type:` 为 research/prototype/grilling/task；`Blocked by: NN, NN` 引用同目录任务。
仅当前置任务均 resolved 时领取任务；先写 claimed，完成后追加 Answer 并更新地图证据。

## 工作流与交接

- 规格记录目标、范围及验收标准；`to-tickets` 将明确的规格拆为任务，实施技能在对应任务更新状态与证据。
- 有未决问题时才使用 `wayfinder`，按问题选择 `research`、`grilling` 或 `prototype`；地图只索引决策，答案保存在任务中。
- 研究结论进入 `docs/research/`；领域定义和架构决策遵循 [领域规则](domain.md)；可复现缺陷与复验进入对应任务，通用经验进入 `docs/DEVELOPMENT_PITFALLS.md`。
- 评审使用 `code-review`，验证结果按 `Passed / Failed / Not Run` 记录。技术任务完成与独立人工签署分别维护，发布任务遵守人工验收前置条件。
- 需要跨会话继续时，`handoff` 写入 `outputs/handoffs/<feature>.md`，只保留下一步、阻塞及文档指针；持久状态仍写任务文件。此路径覆盖技能的系统临时目录默认值。
- `implement-spec` 的分支、worktree、提交和远端 PR 步骤按当前用户授权执行；技能流程本身不提供提交或外部发布授权。
- 项目使用上述文件维护状态，不创建 `.planning/`。旧记录仅在 [历史归档](../archive/planning-with-files/README.md) 查询；归档中的授权不作为当前授权。
