# [P1] 把 AGENTS 规则当代码维护：删除失效条款，为每条保留规则写明理由

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 03

## 目标与范围

清理 [AGENTS.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/AGENTS.md) 及其引用的 `docs/agents/issue-tracker.md`、`triage-labels.md`、`domain.md`、`storage-maintenance.md`；同时检查清单发现的其它受跟踪 AGENTS 和规则反向引用。

每条保留的规范性要求旁边补一句具体的“为什么”。不能只在总开头写一句泛泛的维护性说明，也不能只给根 AGENTS 的链接加理由而遗漏被引用文件里的实际规则。遵守 [总规格](../spec.md)。

## 审核依据

规则的依据可以是代码、工具、目录/文档、实际工作流或仍存在的风险约束；并非每条规则都应对应 Python 函数。科学正确性、来源追踪、许可、用户工程保护和外部操作授权不因缺少直接调用而失效。

| 规则组 | 当前资料 | 审核重点 |
| --- | --- | --- |
| 本地任务/技能 | [docs/agents/issue-tracker.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/issue-tracker.md)、`.scratch/`、`skills-lock.json` | 是否仍是实际工作流；旧技能名、阶段映射和路径是否有效；锁文件不等于本地一定安装，缺少受跟踪技能目录也不等于全局技能不存在 |
| triage 与执行状态 | [docs/agents/triage-labels.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/triage-labels.md) | 保留分派角色和执行状态的必要区分；不要凭清理创建远端标签 |
| 领域定义 | [docs/agents/domain.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/domain.md)、`CONTEXT.md`、`docs/adr/` | 当前术语和决策位置；“文件不存在时”等初始化条款是否仍有适用场景，还是可删除的启动期说明 |
| 参考资料 | 根 AGENTS、`.gitignore`、`submodules/`、来源索引 | 已失效的软件目录/路径应删除或更正；保留有效来源、版本、摘要、许可及源码子模块边界 |
| 阶段产物 | [docs/agents/storage-maintenance.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/storage-maintenance.md)、`tools/prune_outputs.py` | 实际清理范围和已批准类别；保全用户工程、逐文件计划、链接边界与历史证据约束仍须核验和保留 |

## 执行清单

- [x] 在本任务记录“条款位置／现有要求／当前依据／适用条件／保留、合并或删除／理由”映射。
- [x] 对提到的命令、路径、配置、技能、阶段与引用逐项核验；不以搜索不到一个词就断言规则失效。
- [x] 删除引用已消失对象且已无适用条件的规则、被替代的旧流程和重复要求；将仍有效但过于宽泛的条款收敛到真实条件。
- [x] 为每条保留规则添加一句风险或目的明确的理由，例如“保留来源摘要，以防异步任务把已变化输入的结果绑定到旧数据”。
- [x] 科学、许可证、安全和人工验收要求不能因清理而放宽；`Passed / Failed / Not Run` 的证据含义保持。
- [x] 本轮要求远端 Issue 不等于永久取消本地任务流程；只澄清本轮与默认规则的关系，不擅自迁移项目管理体系。
- [x] 通过普通 diff、引用检查和现有验证评审规则变更；不新增强制规则引擎、Skill 依赖或 CI。

## 验收

- [x] 100% 保留的规范性条款有一句具体理由及可解释依据。
- [x] 每个删除条款有失效证据；无法确认本地技能/输入状态的条款列为待核实，而非擅删。
- [x] 被保留的路径和文档链接有效，CLI 与当前实现一致；本地依赖明确写明取得条件。
- [x] 根规则与被引用规则没有重复或冲突要求，初始化说明不会冒充现行操作规范。
- [x] 没有减少用户工程保护、输入校验、许可或人工验收约束，也没有扩大外部写入权限。
- [x] 规则文本简洁，清理过程留在任务记录，不塞进日常指令。

## Comments

尚未执行。远端已读到 `.scratch/` 工作流和真实维护工具的引用，不能把这些规则一概视为“代码里不存在的旧规矩”。

- 2026-09-30：03 已 resolved，领取本任务。主仓库技能目录与锁文件对应，当前工作树不携带忽略技能；保留按技能可用性执行的实际工作流，不安装技能。规则修改限根 AGENTS 及四份被引用文件。

- 2026-09-30：规则逐条核验完成。合并根目录重复的存储细则与任务规则重复句，替换已完成初始化的条件说明；所有保留条款已有具体理由。05 可领取。

## Answer

条款位置、原要求、现行依据、适用条件和处置理由见 [逐条核验表](rules-review.md)。五份规则共 11 个本地链接 **Passed**（`outputs/repository-cleanup/rules-links.json`），`prune_outputs.py --help` 与参数说明一致，`git diff --check` **Passed**。无失效技能被臆断删除，无锁文件/环境变更，无科学、许可、用户工程、独立人工签署或外部发布边界放宽。

磁盘清理及外部写入 **Not Run**；本任务只改规则正文。代码候选仍为 03 的 `2cd8bd76…42fb`，规则修改不改变其运行资格。未创建提交。
