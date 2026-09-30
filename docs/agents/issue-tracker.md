# 本地 Markdown 任务跟踪

需求和规格保存在本仓库 `.scratch/`；技能提到任务跟踪系统时默认操作对应本地文件，不执行远端发布。理由：本地任务是执行状态的权威来源，技能流程本身不提供外部写入授权。

- 每个工作主题使用 `.scratch/<feature-slug>/`，规格为 `spec.md`，任务为从 01 编号的 `issues/<NN>-<slug>.md`。理由：将规格与实施结果放在同一目录，可避免跨主题编号冲突。
- 任务顶部用 `Triage:` 保存分派标签，值遵循 [标签规则](triage-labels.md)。理由：分派角色用于判断需要 Agent、维护者还是更多信息。
- `Status:` 保存执行状态：`pending`（未领取）、`claimed`（进行中）、`resolved`（任务验收完成）。技能的 `Execution: complete` 对应 `Status: resolved`；技能将 triage 写入 `Status:` 时，改写至 `Triage:`。理由：统一字段使依赖检查能区分执行完成与分派完成。
- 讨论追加在任务文件的 `## Comments` 下，保留决策与证据。理由：后续领取者需要看到决定的依据和验证范围。
- 读取任务时使用提供的路径或编号；编号结合主题目录解释。理由：不同主题都从 01 开始，编号本身不是全仓唯一 ID。

使用 wayfinder 时，地图为 `.scratch/<effort>/map.md`，子任务各自成文件；`Type:` 为 research/prototype/grilling/task，`Blocked by: NN, NN` 引用同目录任务。理由：地图索引问题和依赖，答案需要能独立回查。

仅当前置任务均 resolved 时领取任务；先写 claimed，完成后追加 Answer，并更新已有地图中的证据。理由：下游实现必须建立在已经验收的前置结论上。

## 工作流与交接

- 规格记录目标、范围及验收标准；使用 `to-tickets` 时拆分已明确的规格，实施技能在对应任务更新状态与证据。理由：验收条件需要在实施前可核对。
- 有未决问题时才使用 `wayfinder`，按问题选择 `research`、`grilling` 或 `prototype`；地图只索引决策，答案保存在任务中。理由：避免为已明确任务额外维护重复计划。
- 研究结论进入 `docs/research/`；领域定义和架构决策遵循 [领域规则](domain.md)；可复现缺陷与复验进入对应任务，通用经验进入 `docs/DEVELOPMENT_PITFALLS.md`。理由：读者能按研究、约束和操作故障找到各自权威来源。
- 评审使用 `code-review`，验证结果按 `Passed / Failed / Not Run` 记录；技能可用性按当前宿主核对，`skills-lock.json` 仅记录来源。理由：版本锁不证明本机已安装技能，未执行的检查也不能记为通过。
- 技术任务完成与独立人工签署分别维护，发布任务遵守人工验收前置条件。理由：自动化数值和界面检查不能代替使用者对操作及科研适用性的认可。
- 需要跨会话继续时，`handoff` 写入 `outputs/handoffs/<feature>.md`，只保留下一步、阻塞及文档指针；持久状态仍写任务文件。理由：交接是临时指针，不能成为第二份任务状态或散落系统临时目录。
- `implement-spec` 的分支、worktree、提交和远端 PR 步骤按当前用户授权执行。理由：技能流程不提供提交、发布或外部写入授权。
- 项目使用上述文件维护状态，不创建 `.planning/`；[历史归档](../archive/planning-with-files/README.md) 只用于追溯，旧授权不作为当前授权。理由：避免恢复过期任务状态或把历史许可扩大到当前工作。
