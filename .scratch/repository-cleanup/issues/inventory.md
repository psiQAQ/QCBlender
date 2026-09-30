# 仓库清理清单

基线：`1b87751616ecb03d89f6a8c0e96cac99544b420a`，Windows PowerShell 7，Blender 5.1.1 / CPython 3.13.9。当前工作树初始无修改。主仓库仅 `.scratch/repository-cleanup/` 未跟踪，任务稿已复制，本轮只在当前工作树实施。盘点时未创建提交；用户随后授权本地提交与合并，具体提交由 Git 记录追溯。

## 覆盖与入口

受跟踪清单覆盖 69 个 `qcblender/` 文件、49 个 `tests/` 文件、69 个 `tools/` 文件、50 个 `docs/` 文件、54 个 `.scratch/` 文件及根文档/锁文件。逐文件 SHA-256、AST 导入候选和字符串标识保存在 `outputs/repository-cleanup/inventory-baseline.json`。AST 覆盖所有受跟踪 Python；它只提供候选，不能证明所有运行分支可达性。本轮未发现有充分证据可删除的函数、Operator 或工具脚本。

| 入口 | 引用证据和保留理由 |
| --- | --- |
| 扩展生命周期 | `qcblender/__init__.py` → `auto_load.discover/register/unregister`；`pkgutil.walk_packages` + 类检查动态发现 Panel/Operator/PropertyGroup/Preferences/UIList/Menu。单次出现的 `QCBLENDER_*`、`QCBlenderPreferences` 均非死代码 |
| RNA / 菜单 / 工具 | `blender/properties.py` 的 update 回调、`editor_ui.object_context_menu`、`interaction.register_tool`、`charts.register`、`result_browser.attach_properties`；RNA 注解、ID 字符串和 UI 按钮是有效调用 |
| handlers / timers / 异步 | `source_browser.refresh_loaded_sources` 的 load/save hooks；`ui.AsyncOperation` modal timer；`jobs.Job` poll/cancel；注销必须取消操作并移除 hooks |
| worker | `worker.main` 动态导入已安装扩展，action 字符串包括 diagnose、inspect_source、contours、result_scatter、field_range、import/import_pair/import_nbo/import_nocv/evaluate/rebuild_cache/declare_field；请求身份、摘要、取消与进度边界保留 |
| 节点 / 工程 | `asset_catalog.ASSETS`、`assets`/`views`/`fog`/`inspection` 的九类节点；`qc_asset_id`、socket identifier、`qc_dataset*`、`qc_source*`、`qc_schema`、`qc_field`、视图/关联字段保存到工程；旧图匹配与拒绝自定义图分支保留 |
| 科学层 / 工具 | `readers`、`data`、`evaluate`、`project` 不与同名 Blender 适配器合并；`tools` 的 CLI 和独立数值参考是外部入口，不因无 import 删除。`Grid.__post_init__` 由 dataclass 调用 |
| 参考 / 许可 | 3 个 gitlink（GXNU-MolStudio、MolecularNodes、VTK）未初始化于此 worktree，固定提交可由索引核对；不扫描或修改内部。LICENSE、THIRD_PARTY、测试样本许可和独立数值参考必须保留 |

## 代码候选

| ID | 路径 / 符号 | 分类 | 引用与动态入口核对 | 等价实现 / 风险 | 动作与验证 |
| --- | --- | --- | --- | --- | --- |
| D01 | `qcblender/blender/legend.py` 导入 `view_modifier` | 已确认可删 | 全模块没有 Load；全仓无 `legend.view_modifier` 或该名称的重导出读取；auto_load 只发现本模块类 | 同一行保留 `tag_view`，`.graph` 仍加载；不是 RNA/资产字段 | 02 删除名称；AST 除导入外一致、原生注册/注销、图例与保存重开 |
| D02 | `tests/test_science_adapter.py` 导入 `wavefunction` | 已确认可删 | 测试实际通过 `read_source`/求值器使用科学数据；没有读取该导入名称 | 保留 readers 模块加载和实际公开函数 | 02 删除名称；69 项科学回归 |
| D03 | `tools/verify_analysis_gui.py` 导入 `importlib` | 已确认可删 | 整文件直接使用 bpy，未调用 importlib；独立 CLI 保留 | stdlib 导入不提供注册副作用，工具行为 AST 不变 | 02 删除导入；编译、AST 对照；完整 GUI 脚本不因该导入删除而宣称已重跑 |
| D04 | `tools/verify_project_recovery.py` 导入 `hashlib` | 已确认可删 | 整文件没有 hashlib 调用；恢复依赖 data/project 完整性验证 | stdlib 导入不是科学摘要校验逻辑 | 02 删除导入；AST 对照、实际新工程恢复检查 |
| D05 | `tools/verify_vmd_scalar_edges.py` 导入 `shutil` | 已确认可删 | 整文件无 shutil 调用；`prepare_sop_fixture.paired_dataset` 是真实准备入口 | stdlib 无必要副作用；不删除工具 | 02 删除导入；AST 对照与编译 |
| M01 | `views.atom_selection.math_node` 与 `assets.math` | 等价重复候选 | `assets.selection_group` 调用 atom_selection；后者 13 个数学节点构造调用；assets.math 被 assets、fog、inspection 使用 | 输入是 operation + 数字/socket，返回首个输出；相同 isinstance 和 links.new，无单位转换。在函数内导入 assets 可保持模块依赖顺序 | 03 复用 assets.math，保留 atom_selection；原生选择行为、10 组图结构快照、安装/保存重开 |
| M02 | `scalars.add_legend.math_node` 与 `assets.math` | 等价重复候选 | add_legend 的 component、fraction 调用；从映射、原子电荷及 legacy upgrade 进入 | 同样的变参处理、节点操作和 TypeError；布局计算/默认值保留 | 03 复用 assets.math；图例图快照、已有图例验收（含旧图升级） |
| M03 | views.bind / NBO / NOCV 的 manifest 读取 | 必须保留 | bind 记录绑定；NBO 保存对象后重验摘要；NOCV 还验证对象指针/父绑定/表身份 | `.resolve()` 与 `.resolve(strict=True)`、读取时点及错误语义不同；相同 SHA-256 一行不足以构成有收益的公共流程 | 保留全部校验，不引入跨层 helper |
| M04 | tools 的 fixture / wait / geometry helpers | 待核实 | 不同脚本的候选模块、输出目录、失败处理和冷重开前提不同 | 缺乏整段等价证据；独立数值参考合并会产生自我验证 | 保留；本轮不统一测试框架 |
| K01 | `views.atom_selection`、动态类、回调、拒绝分支、legacy 兼容 | 必须保留 | 上述入口与保存身份构成有效引用 | 删除会减少功能或破坏旧工程 | 全部保留 |

## 规则与文档候选

| ID | 对象 | 当前权威依据 | 处理 |
| --- | --- | --- | --- |
| R01 | 根 AGENTS + 四份 agents 规则 | `.scratch` 状态、CONTEXT、ADR、输入索引、prune_outputs CLI、锁文件 | 04 逐条补理由；已存在领域文件的启动期说明改为真实路径约束；技能缺失不视为规则失效 |
| R02 | 产物清理授权 / 人工验收 | storage-maintenance、storage-cleanup 已完成任务、未签署人工任务 | 保留既有边界，本次只清代码文档，不运行磁盘删除计划 |
| T01 | USER_GUIDE | 当前 editor_ui/ui/properties、VALIDATION | 删除重复 VMD 段、重复色标段；删除当前流程中的多个旧 ZIP；保留科学操作细节 |
| T02 | QCBLENDER_V1_DESIGN / DEVELOPMENT / VALIDATION | 源码模块、manifest、测试入口、此次候选证据 | 改为实际职责与现行命令；区分当前运行与历史验证；明确优化和外部 IRC 的各自边界 |
| T03 | RESULT_BROWSER / OPTIMIZATION_TRAJECTORY / 参数记录、acceptance、AGENT-REPLAY | 已完成任务及 CHANGELOG | 历史测试计数及摘要不改成此次结果；抽取当前用法到 USER_GUIDE，保留必要追溯并标明历史产物可用性 |
| T04 | specs / research / ADR / 来源许可 | 当前数值契约、独立参考、设计依据和许可风险 | 保留真实约束，逐份核查；研究快照不冒充当前支持列表 |
| T05 | docs/archive 与已完成 .scratch | 当前任务已迁移，归档清单给出 Git / SHA-256 | 逐份判定重复或唯一证据；未知/未解决/人工任务保留，不按日期批删 |
| T06 | README | 当前 USER_GUIDE / VALIDATION / manifest | 06 改为用户任务→兼容与获取→五步操作→保存限制→开发分类入口 |

允许修改清单：上述 D01–D05、M01–M02 文件；规则五文件；根 README；50 份受跟踪 docs 和54 份 .scratch 按逐份处置清单确认后仅更新/删除被证实项；新增本任务记录和直接保护行为的 `tools/verify_node_helpers.py`。锁文件、输入、子模块、用户工程不在修改清单。

## 行为基线与环境

- **Passed**：`tools/run_science_tests.py --site D:/workspace/QCBlender/outputs/science`，69 tests，0 failures/errors/skipped；`outputs/repository-cleanup/baseline/science.json` 和 `science.log`。
- **Passed**：现有非科学 unittest discovery，11 tests，0 failures/errors/skipped；同目录 `unit.json` / `unit.log`。使用 Blender Python 3.13.9，科学 site 只读复用，不安装/更新依赖。
- **Passed**：`tools/verify_node_helpers.py`，原生 Blender 5.1.1，元素、首末原子、布尔选择、空选择、asset 复用、socket identifier、数字/socket/错误输入；同目录 `nodes.log`。
- **Passed**：九类资产 + 原子选择/图例测试图共 10 组，operation、输入默认值、接口 identifier 和连接快照保存 `baseline/nodes.json`，供 03 逐项比较。
- **Passed**：104 个已有本地输入 SHA-256 与索引匹配。5 个必须从 ROOT 读取的 Log 复制到忽略的 `tests/data/local/log-examples`，其余使用 `QCBLENDER_REFERENCE_ROOT` 只读；见 `outputs/repository-cleanup/inputs.json`。
- **Not Run（基线阶段）**：完整候选安装/保存/冷重开；在 02 和 03 的新包执行。独立人工验收不属于 Agent 技术验证。
- `Get-CimInstance` 进程详情查询被宿主拒绝；`Get-Process blender` 未发现既有 Blender。本轮仅启动隔离后台进程并记录 PID，不操作用户会话。PowerShell 直接 git-submodule helper 缺少 bash 工具路径；用 `git ls-files --stage submodules` 核对 3 个 gitlink，不改动子模块。

证据摘要见任务 Answer；原始日志保留在忽略的 outputs 下。当前没有关联提交，后续提交需要维护者明确授权。
