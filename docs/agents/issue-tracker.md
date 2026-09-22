# 本地 Markdown 任务跟踪

需求和规格保存在本仓库 `.scratch/`，创建或更新本地任务不执行远端发布。

- 每个功能一个目录：`.scratch/<feature-slug>/`。
- 规格为 `spec.md`；实现任务分别为 `issues/<NN>-<slug>.md`，从 01 编号。
- 任务顶部用 `Status:` 保存 triage 状态，值遵循 [标签规则](triage-labels.md)。
- 讨论追加在任务文件的 `## Comments` 下，保留决策与证据。
- 技能要求发布到任务跟踪系统时，创建或更新对应本地文件。
- 技能要求读取任务时，按提供路径或编号读取；编号结合功能目录解释。

使用 wayfinder 时，地图为 `.scratch/<effort>/map.md`，子任务仍各自成文件。
`Type:` 为 research/prototype/grilling/task；`Status:` 为 claimed/resolved 等工作状态，
triage 标签另放 `Triage:`；`Blocked by: NN, NN` 引用同目录任务。
仅当前置任务均 resolved 时领取任务；先写 claimed，完成后追加 Answer 并更新地图证据。
