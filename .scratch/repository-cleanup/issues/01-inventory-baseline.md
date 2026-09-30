# [P0] 建立清理清单与行为基线：先证明哪些内容可删、可合并

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 无

## 目标与范围

为后续代码、规则和文档清理提供可复核的清单和验证基线。本任务只调查、列清单和建立必要的行为测试，不先删除实现。遵守 [总规格](../spec.md)。

覆盖受跟踪的 `qcblender/`、`tests/`、`tools/`、根文档、`docs/` 和 `.scratch/` 中仍影响当前工作的记录；源码子模块只判断用途，不扫描其内部以凑清理量。不要把本机未下载的输入或忽略的生成物当成仓库死代码。

## 已知证据与容易误判的地方

- [qcblender/auto_load.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/auto_load.py) 通过 `pkgutil.walk_packages`、模块导入和类检查发现 Blender 类。缺少显式调用不能证明 Operator/Panel 等类无用。
- [qcblender/__init__.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/__init__.py) 注册了 hooks、timer、菜单和属性；这些不是普通函数调用图能完整表达的入口。
- [qcblender/blender/assets.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/assets.py) 的 `selection_group()` 仍调用 `views.atom_selection()`。后者不是已确认死代码。
- [tools/run_science_tests.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/tools/run_science_tests.py) 只发现 `test_science*.py`；其通过不能替代其它单测和原生 Blender 检查。
- 当前样例清理及重建边界见 [docs/agents/storage-maintenance.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/agents/storage-maintenance.md)，缺本地依赖不等于对应测试过时。

## 执行清单

- [x] 记录实际分支、HEAD、已有改动、Blender/科学测试环境及可取得的样本；不覆盖他人或用户未提交改动。
- [x] 盘点入口：模块导入、公开函数、动态注册、`bpy.ops` 字符串、RNA 属性回调、handlers/timers、工具 CLI、worker 动作、节点资产和保存字段。
- [x] 生成候选表，至少包含：路径/符号、类型、引用证据、可能动态引用、保留的等价实现、兼容风险、建议动作、验证方法。
- [x] 每项标为“已确认可删”“等价重复候选”“必须保留”“待核实”；没有找到死代码也是允许且需诚实记录的结果。
- [x] 对规则和文档另外记录：引用对象、适用范围、当前权威来源、重复/失效依据、建议处理方式。
- [x] 使用现有测试入口建立基线，记录科学测试及其它单测的实际数量、失败、跳过、环境和报告路径；不把历史 20/48/69 等计数当作当前结果。
- [x] 对计划删除/合并的路径映射验证项目，必要时先加能锁定当前行为的最小测试；不建立新测试框架。

## 交付物

在本任务的 Answer 中保存清单；清单较长时可附同目录 `inventory.md`，不要把一次性审计报告永久塞进 `docs/`。测试报告放仓库现行批准的输出位置，并在任务中记录来源提交和摘要。

每项至少回答“为什么可以处理”和“如何证明处理后行为不变”；仅有静态扫描工具的告警数量不算完成。

## 验收

- [x] 清单覆盖上列目录；覆盖不足和不可访问的本地输入明确列出。
- [x] 每个建议删除或合并项具有引用/行为证据和对应验证方法。
- [x] 不将动态入口、诊断分支、拒绝不支持输入的代码、许可证材料或独立参考数据误判为冗余。
- [x] 基线结果区分 Passed / Failed / Not Run，未执行的不冒充通过。
- [x] 后续任务可凭清单独立决定具体修改；本任务没有提前开展大规模删除。

## Comments

尚未执行。远端关键文件抽查只能提供上述起点，不构成完整死代码审计。

- 2026-09-30：领取任务。当前工作树 detached HEAD `1b87751616ecb03d89f6a8c0e96cac99544b420a`，初始 tracked diff 为空。任务稿从同 HEAD 的主仓库复制，主仓库仅有该未跟踪目录；原件不修改。规则与四份引用均已读取。证据保存在 `outputs/repository-cleanup/`，不会修改既有用户工程或依赖环境。

- 2026-09-30：完成基线和清单。5 个未使用导入可删除；2 个节点构造重复可比较；manifest 绑定及工具准备逻辑保留。未先删除实现。允许后续任务 02 领取。

## Answer

处置依据、入口图谱、环境及范围见 [清理清单](inventory.md)。新增原生 Blender 保护检查 `tools/verify_node_helpers.py`；其在未清理源码上通过。

| 验证 | 结果 | 证据 / SHA-256 |
| --- | --- | --- |
| 科学回归 | Passed，69/69，0 skipped | `outputs/repository-cleanup/baseline/science.json`；`fe05b6e626b883c0c8694029f79bb0b3bfe218829849cc14cd0596761fd54226` |
| 非科学单测 | Passed，11/11，0 skipped | `outputs/repository-cleanup/baseline/unit.json`；`e30a086395dd50fd5d6b8945499be1318ef9cea12647cc806c4d14978b30ac0a` |
| 原生节点与10组图快照 | Passed | `outputs/repository-cleanup/baseline/nodes.json`；`ad95ff48838b360bd559f2a8083b7d409fb9ae82bb98e6bc9ba4c477b925c897` |
| 文件/AST 清单 | Passed，全部受跟踪 Python 已扫描，候选经人工读码复核 | `outputs/repository-cleanup/inventory-baseline.json`；`4aa26ee9a567474fb25b601f556c3857cb05b3e479fa53d8d4b385be233675b0` |
| 真实输入 | Passed，104 项摘要匹配 | `outputs/repository-cleanup/inputs.json` |
| 完整新包安装 / 保存 / 冷重开 | Not Run，本任务建立源码基线，02/03 执行新候选验证 | 不引用旧候选 Passed |

基线提交为 `1b87751616ecb03d89f6a8c0e96cac99544b420a`；本轮未获提交授权，处置关联本工作树 diff 和文件摘要。
