# 校验目录与人工教程整理计划

Triage: ready-for-agent
Status: claimed
Baseline: main@5ff3b67c594f77a8d81b1509f59b27571154bfd0
Date: 2026-10-06

## 目标

在仓库根目录建立 `validation/`，集中人工教程、Agent 校验入口和案例资源。人工教程能够连同公开输入、最新有效安装包及维护者补充的截图单独打包，解压到其他位置后仍可操作。

人工操作以成功安装、看见正确内容、调整显示、导入导出和保存重开为验收依据。人工 SOP 不要求 SHA-256、填写实际结果、复制记录模板或签署；技术验证和文件迁移核对由 Agent 维护，人工完成情况依据使用者反馈确认。

## 目录与接口

所有教程中的文件路径以 `validation/` 为材料根目录；Markdown 链接和图片使用相对文档的路径，不依赖本机盘符。

| 路径 | 内容与维护方式 |
| --- | --- |
| `validation/README.md` | 校验入口、目录说明和人工打包步骤 |
| `validation/human/SOP.md` | 安装开始的入门主流程、可跳转专题目录 |
| `validation/human/topics/` | 公开案例专题，复用共同操作 |
| `validation/human/screenshots/` | 维护者按步骤中的引用名称保存截图 |
| `validation/shared/data/public/` | 按冻结样本清单的 archive_path 组织 P01/P03/P04/P05/P06 全部 30 个公开输入及许可 |
| `validation/shared/data/local/` | 受限或本机计算原件；Git 忽略，公开打包排除 |
| `validation/shared/data/regression/` | 自动测试的小型输入；保持来源与原字节 |
| `validation/shared/install/` | 最新有效插件 ZIP；当前选择 alpha-ci-0.1.0-190e11e 的原始安装包 |
| `validation/agent/` | 技术校验流程、案例覆盖映射、清理待确认清单、冻结包与技术报告 |
| `validation/work/` | 人工和 Agent 运行生成的工程、导出及临时工作，不进入教程包 |

本地限定的 P02 人工案例放在 `validation/agent/LOCAL-CASES.md`，由校验入口链接；仅使用本机资料的人按需操作，公开主流程不依赖它。历史证据保持原始内容，通过迁移映射追溯。

公开教程包只选择 `human/`、`shared/data/public/` 和 `shared/install/`，保留它们相对于材料根目录的位置。P02、本地计算原件、回归输入、Agent 技术报告和工作产物不进入包。依赖版本、产品行为及数据协议保持现状。

## 人工教程要求

- 主流程目标约 12–15 个编号操作，从安装进入 P01 轨道图，完成一次渲染、参数摘要导出及自包含工程保存重开。
- 按需专题保留分子显示/XYZ、Cube、密度/ESP、切片/剖面、IGMH/IRI、ESP/AIM、IRC/Mayer、ETS-NOCV 和公共节点。使用同一输入的操作连续复用对象；保存、迁移和渲染不再逐例重复。
- 科学 CSV 与参数摘要分别练习一次，明确文件名、单位及最少量的可观察参照；实际导出子目录按插件提示定位。
- 开篇跳转目录；每步写清输入、选择对象、真实按钮/参数与预期。术语以独立的 `>` 行就地解释。
- 有可见结果的步骤后立即放截图引用和完整保存路径。截图由维护者补充，空位不伪造为已验证图片。
- 别名重复导入、错误输入、数组恒等式、完整撤销矩阵、三位置重开及多轮导出比较移交 Agent，旧检查编号保留覆盖映射。

## 并行分工和依赖

| 任务 | 负责范围 | 依赖与完成条件 |
| --- | --- | --- |
| [01 计划与接口](issues/01-plan.md) | 主 Agent：计划、接口与文件归属 | 计划进入 main 后下游领取 |
| [02 人工教程](issues/02-human-tutorial.md) | 教程子 Agent：human/ 和本地限定案例页 | 依赖 01；文档链接/参数/覆盖自查，本地提交 |
| [03 数据迁移](issues/03-data-paths.md) | 数据子 Agent：数据原件、索引、tools/tests 路径、忽略规则 | 依赖 01；迁移映射与相关测试，本地提交 |
| [04 Agent 校验与清理清单](issues/04-agent-checks.md) | 校验子 Agent：Agent 流程、旧检查覆盖、只读清理清单 | 依赖 01；逐文件清单和保留对象，不执行删除 |
| [05 整合与复核](issues/05-integration.md) | 主 Agent：入口、项目约定、文档路由及综合验证 | 依赖 02/03/04；按串行合并流程复核 main |
| [06 确认并清理历史文件](issues/06-cleanup-approval.md) | 主 Agent 与维护者：确认后逐文件删除 | 依赖 05 及维护者对准确清单的确认 |
| [07 本地交付与归档](issues/07-delivery.md) | 主 Agent：归档标签、工作树保全和正常移除 | 依赖 05；06 未确认时独立保留 pending |

子 Agent 在独立分支和 `.worktrees/` 工作。每个子任务完成自查及提交后报告主 Agent；获得串行合并轮次后先更新至当前 main、复验受影响内容，再 `git merge --ff-only` 合入 main。主 Agent 核对合并身份、差异和实际主分支结果。全程不 push。

主检出现有 `docs/ARTIFACTS.md`、`docs/CHANGELOG.md` 和 `.scratch/alpha-readiness/issues/11-worktree-residue.md` 的未提交修改完整保留。仅提交本任务拥有的变化，不把已有修改并入本次提交。

## 数据迁移与清理边界

公开文件按 `archive_path` 汇聚，P04 CSV 与其同目录文件成组保留。冻结 v2 ZIP 和其清单保持原字节；当前读取入口使用新位置，本地索引保持稳定 ID/key、来源、许可、摘要和历史 original_path。必要原始计算文件集中到 local/calculations；工程内部 `.qcdata` 不拆散。

已核实最新完整候选为 `outputs/candidates/current/alpha-ci-0.1.0-190e11e/`。计划清理的已知旧插件包为 15 个有名 ZIP 与 6 个按摘要命名的安装包副本，合计 1,063,580,687 字节；其他旧样本、复现 ZIP、CI 外层容器和不完整下载分别列项。此统计不是整个 outputs 的完整可读性声明。

迁移先复制并验证，更新读取入口后才请求删除旧的未跟踪副本。受 Git 跟踪数据的路径调整作为可恢复的迁移提交。历史安装包、旧输入副本和证据容器的实际删除另待逐文件清单确认。未知归属、链接、访问拒绝、用户工程和活跃环境保持原位；不修改 ACL、不强制删除。

## 综合验收

1. 公开 30 个输入齐全、P04 相对引用有效、P02 不在分发集合；本地索引可解析并保持内容身份。
2. SOP 与专题的跳转、资源路径、术语解释、截图名一致；无实际结果填写、签署或 SHA 操作。未补截图单独列为预定空位。
3. 在独立目录复制公开教程允许集合，检查不依赖仓库、本机绝对路径或 Agent 文件。
4. 运行相关 local_inputs、candidate_artifacts、storage_cleanup、受影响科学用例及 public-core；冻结包检查与必要 checkpoint 检查分别报告。
5. 主 Agent 在 main 做代表性输入读取、实际 Blender 导入/导出/保存重开检查；既有 GUI 入口复用规则适用。人工截图与使用者独立验证仍由维护者完成。
6. 验证记录明确 Passed / Failed / Not Run；清理审批与删除状态独立于文档、迁移完成状态。

## Comments

2026-10-06：用户要求先形成计划，并授权开始实施、使用子 Agent 完成后合入主分支、由主 Agent 检查。历史文件删除仍沿用用户要求，须先确认保留/删除清单。
