# 产物查找入口

更新：2026-10-02。本页路由当前文件、归档身份、重建方法与阻塞；各原始报告保留其执行时的状态和候选身份。任务状态在 `.scratch/`，开发顺序见 [DEVELOPMENT](DEVELOPMENT.md)，保留与清理边界见 [维护规则](agents/storage-maintenance.md)。

## 当前交付

| 对象 | 当前入口与状态 |
| --- | --- |
| 插件候选 | `outputs/candidates/current/tutorial-main-b8a63cd/qcblender-0.0.1.zip`，源码 `b8a63cd8c7a2afe1edd50085ff41c862e9005868`，SHA-256 `706f760b248a7775206e7361460f85645573490ebf3e566f40d05e97eeec4c44`；本地资格 Passed，未发布 |
| 受控验证索引 | [最终技术资格](acceptance/tutorial-final-qualification.json)，同批 `outputs/evidence/2026-10-02/tutorial-cu/main-qualification/`，38份摘要绑定报告、命令、日志与原生渲染；源码、ZIP与安装原字节一致 |
| 教程与截图 | [SOP](v1-acceptance/SOP.md) 保留 C01–C13 / N01–N18；截图紧接步骤，`docs/v1-acceptance/screenshot/`；Agent验收 Passed，用户复做/独立科研签署 Not Run |
| 公开样本 | [样本交付](acceptance/tutorial-sample-delivery.json)；`outputs/evidence/2026-10-02/tutorial-cu/final-samples/qcblender-public-tutorial-samples-v1.zip`，SHA-256 `56faa42ad555d1e9fce9e33bc839779ab92935a89429dcae8db29d53b92e3b4f`；27科学文件与许可原字节保留，C01固定轨道与自动HOMO身份分开 |
| 新候选保全工程 | `outputs/projects/tutorial-cu-full/qualification-main-b8a63cd/{install/mo8,legend/evidence}.blend` 及完整 `.qcdata`；188文件逐项摘要和新进程冷读 Passed，映射在同批 `project-path-map.json` |
| 操作复用 | [Blender规则](agents/blender-interaction.md)、[68项登记](acceptance/blender-operations.json)；已确认且实现未变的操作优先MCP/命令行，首次/变更用CU；各旧GUI身份保持不变 |

69科学测试无失败/错误/跳过；31相关单测30通过、1项POSIX专用在Windows跳过；节点原子身份/固定接口、安装生命周期、九公共资产完整签名、原地/中文移动/统一工程冷读、缓存恢复、图例与原生渲染 Passed。新候选同旧GUI候选的三处文本仅有CRLF/LF差异，Python AST/JSON值一致；审阅见本批 `GUI-reuse-review.json`。样本输入的唯一清单为 `tests/data/local-inputs.json`，来源为 [SOURCES](v1-acceptance/SOURCES.md)。

## 归档、清理和阻塞

主分支已本地 ff-only 合并到固定源码提交；八个带注释标签 `archive/2026-10-02/<完整分支名>` 的身份和提交可达性 Passed，详细分支名见 `outputs/evidence/2026-10-02/tutorial-cu/archive-preparation-final/closing/tags.json`。八个本轮工作树及已合并分支均正常移除；没有 push。

本次继续处理收据位于 `outputs/evidence/2026-10-02/tutorial-cu/deferred-cleanup/`：`preflight.json`和`ignored-preservation.jsonl.gz`逐文件复核111份剩余材料，两份旧工作副本与main及原文件/基线/补丁完全一致；`worktree-removal.json`记录最后两个工作树及分支正常移除。31份恢复数据完整迁入 `outputs/projects/recovery/worktree-tutorial-irc-mayer-context/`，原文件没有删除，`recovery-move.json`保存全旧新路径与摘要，`recovery-cold.json`记录新Blender进程Dataset/科学数组/VDB读取Passed。`completion.json`及`legacy-deferred.json`记录本轮完成和用户允许延期的旧阻塞。

上一批清理收据保留在 `outputs/evidence/2026-10-02/tutorial-cu/archive-preparation-final/closing/`：

| 入口 | 内容 |
| --- | --- |
| `post-cleanup.json` | 清理后70项源码/JSON、110输入、11锁定wheels、188工程文件、38报告与1,934保留文件摘要核对；同口径目标清单前后空间 |
| `cleanup.json` 与上级 `cleanup/<任务>/applied.json` | 七工作树的36,895文件 / 2,164,204,797字节已删除；31恢复数据当时由既有保护拒绝；本次已完整迁入受保护projects/recovery，见新收据 |
| `retired-candidates-applied.json` | 11旧ZIP / 556,975,546字节已删除，最新候选保留；旧报告/摘要/源码标签保留，新重建需重新资格 |
| `main-test-cleanup/` | 本批隔离测试环境与重复生成物4,987文件 / 338,705,325字节已删除；原worker请求、成功失败日志、结果与路径映射保留 |
| `worktree-removal.json`、`legacy-blockers.json` | 真实移除/保留状态；权限及占用对象未强制处理 |
| `retired-preservation-routes.json` | 历史保全映射中指向已删除旧候选的可用性覆盖；优先于原直接路径 |

清单实际删除41,893文件 / 3,059,885,668字节（约3.06GB），这是已删除文件大小总和，排除正常Git工作树移除与新增中央证据，不作为整个仓库的净空间变化。前后目标清单统计见 `post-cleanup.json.measurements`。

| 未完成对象 | 当前原因与保留位置 |
| --- | --- |
| 旧 f458 / `chore/repository-cleanup` | 11目录、3ZIP访问拒绝；原对象/分支保留，未修改ACL或所有权 |
| 旧 b48c | 空 `outputs` 已正常移除，空根目录仍 WinError 32 占用；保留 |
| 默认旧后端wheel | `outputs/wheels/<后端wheel>`不可读，原位保留；当前根后端记录与 `outputs/wheels/qualified/` 的可读wheel已配对核对 |

按用户“无法处理的分支可以暂时放着”的最新范围，03已resolved；本轮八工作树归档清理Passed，旧f458/b48c清理单独延期到 `.scratch/tutorial-cu/issues/06-deferred-cleanup.md`（pending / ready-for-human）。旧权限检查仍Failed、延期清理Not Run，不改写旧结果；未知恢复文件及未解除引用的旧配置保留，不按进程名关闭未知窗口。

归档前逐文件原始清单为上级 `inventory.jsonl.gz`，文本保全、独有二进制及旧新路径为 `working-source-map.json`、`binary-preservation.json` 和 `content/<sha256>`。原报告字节不改写；工作树旧路径通过映射定位。需恢复时另建目录、按映射核对摘要并冷重开，不覆盖现存用户工程。早期 `archive-preparation/` 为只读历史盘点，最终以 `archive-preparation-final/` 和本节收据为准。

## 共用环境与保全项目

| 位置 | 保留用途 |
| --- | --- |
| `outputs/build-site/`、`outputs/science/` | 共用锁定构建/科学环境；本批预检与69科学测试 Passed |
| `outputs/wheels/qualified/`、`outputs/backend-wheel.json` | 显式配对的11锁定wheels与当前后端记录；打包传入 `--wheels-dir`，不凭同名旧wheel复用 |
| `outputs/projects/recovery/worktree-tutorial-irc-mayer-context/` | 31份完整迁入的回归恢复数据，原数组/体积/manifest摘要不变；新原生Blender读取Passed，旧新路径见本次recovery-move.json |
| `outputs/projects/tutorial-cu-full/` | 各案例原工程、中文移动和解包副本、撤销恢复/内部掩码/独立资产/最后Remove工程；按下表批次的 `project-path-map.json` 查摘要 |
| `outputs/projects/public-tutorial-mcp-20261001/`、`public-tutorial-90ff9bf/` | 前批教程项目和科学配套保全；历史状态见各原报告 |
| `outputs/projects/user-session-20260930/`、`cleanup-followup-original/`、`recovery/`、`outputs/recovery/` | 用户与恢复工程，含尚未完整保全的权限对象；保护 |
| `outputs/cleanup-followup-20260930/b48c/outputs/qcf3/profile/`、`outputs/blender-dev/` | 用户/运行时配置引用，保留待逐项解除引用 |
| `outputs/runs/{cu/3/p,cu/4/p,pt/3/p,pm/final-view/p}` | 历史安装配置，工程引用及可读取性需单独核对；本次未清理 |
| `tests/data/local/`、`submodules/` 与既有资料目录 | 必要科学输入、参考源码和原件；不重复复制进证据 |
| 既有构建源码、许可证、参考工具及未分类环境 | 沿用现有位置，未知归属默认保留 |

重建：取回索引中的固定源码，按 [DEVELOPMENT](DEVELOPMENT.md) 核对输入和环境，显式使用 qualified wheels 与当前后端记录，在新的短输出批次依次检查、构建、安装、保全工程及冷读、生成证据索引和资格。保存新ZIP摘要；不宣称逐字节复现已删除旧候选。已归档脚本含旧路径，复跑必须选择新目录，避免覆盖历史收据。

## 教程与维护批次路由

| 批次 | 原始证据、工程与状态入口 |
| --- | --- |
| 2026-10-02后续工作树收尾 | `outputs/evidence/2026-10-02/tutorial-cu/deferred-cleanup/`；本轮八工作树/分支移除完毕，旧权限/占用按用户允许延期；31恢复文件完整迁移与原生读回 |
| 2026-10-02 当前main技术资格 | `outputs/evidence/2026-10-02/tutorial-cu/main-qualification/`；[最终索引](acceptance/tutorial-final-qualification.json) |
| 2026-10-02 GUI/MCP边界与完整案例 | `outputs/evidence/2026-10-02/tutorial-cu/full/`：C05各子批、C06–C13、`remaining-boundaries/{C01-density,field-guards,undo,public-surfaces,layer-removal}`；[补验索引](acceptance/tutorial-cu-validation.json) |
| 2026-10-01 GUI/MCP与修复 | `outputs/evidence/2026-10-01/tutorial-cu/`：`full/C01-*.json`平铺报告、`full/C02`至`C05`、fog/mapping/slice；缺陷和修复证据保留原身份 |
| 2026-10-02旧固定候选资格 | `outputs/evidence/2026-10-02/tutorial-cu/final-qualification/`；原a67d4b3/bd3a78e报告和工程仍保留，旧ZIP已删除 |
| 2026-10-01公共教程MCP资格 | `outputs/evidence/2026-10-01/public-tutorial-mcp/`；[历史索引](acceptance/tutorial-validation.json)，四工作树已归档；旧ZIP已删除 |
| 2026-09-30样本、节点与布局 | `outputs/evidence/2026-09-30/public-tutorial/`；原公开样本包及来源/许可保留 |
| 2026-09-30outputs维护 | `outputs/evidence/2026-09-30/output-maintenance/`；逐文件映射/策略/空间统计/阻塞/收据，`archive/2026-09-30/chore/output-maintenance` |
| 2026-09-30清理复查qcf3与f458 | `outputs/evidence/2026-09-30/cleanup-followup/`；[历史索引](acceptance/cleanup-validation.json)，qcf3旧ZIP已删除，f458权限对象仍保留 |

## 历史任务路由

以下为 2026-09-30 的迁移日期；各任务的原执行日期、源码身份和 Passed/Failed 保持在原报告与 [CHANGELOG](CHANGELOG.md) 中。历史相对层级和字节不变。旧候选、可重建测试工程及孤立配置不再承诺可用；权限拒绝对象可能仍原位存在，不作为已保留的可用交付。需要复跑时，从对应任务工具、保留输入及当前锁定环境重建并重新资格检查。

| 历史任务 | 保留证据目录（相对 outputs） | 查找入口 |
| --- | --- | --- |
| acceptance | `evidence/2026-09-30/history/acceptance/` | `density-esp-cold-view.json`、`extension.json` |
| analysis-gui | `evidence/2026-09-30/history/analysis-gui/` | `esp.json`、`irc.json` |
| animation-acceptance | `evidence/2026-09-30/history/animation-acceptance/` | `result.json` |
| animation-acceptance-v2 | `evidence/2026-09-30/history/animation-acceptance-v2/` | `result.json` |
| atom-visibility | `evidence/2026-09-30/history/atom-visibility/` | `gui.json`、`reopened.json` |
| blender-acceptance | `evidence/2026-09-30/history/blender-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| blender-analysis-gui | `evidence/2026-09-30/history/blender-analysis-gui/` | 批次内原相对层级；完整路径见 routes.json |
| blender-external-worker | `evidence/2026-09-30/history/blender-external-worker/` | 批次内原相对层级；完整路径见 routes.json |
| blender-final-acceptance | `evidence/2026-09-30/history/blender-final-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| blender-localized-install | `evidence/2026-09-30/history/blender-localized-install/` | 批次内原相对层级；完整路径见 routes.json |
| blender-m7 | `evidence/2026-09-30/history/blender-m7/` | 批次内原相对层级；完整路径见 routes.json |
| blender-m8 | `evidence/2026-09-30/history/blender-m8/` | 批次内原相对层级；完整路径见 routes.json |
| blender-pure-acceptance | `evidence/2026-09-30/history/blender-pure-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| branch-archive | `evidence/2026-09-30/history/branch-archive/` | 批次内原相对层级；完整路径见 routes.json |
| committed-build-d1abfe8 | `evidence/2026-09-30/history/committed-build-d1abfe8/` | `result.json` |
| complex-examples | `evidence/2026-09-30/history/complex-examples/` | `source-inspection.json`、`summary.json` |
| composable | `evidence/2026-09-30/history/composable/` | `report.json` |
| diagnostics | `evidence/2026-09-30/history/diagnostics/` | 批次内原相对层级；完整路径见 routes.json |
| extension-cleanup | `evidence/2026-09-30/history/extension-cleanup/` | `applied.json`、`cold-reopen.json` |
| external-results | `evidence/2026-09-30/history/external-results/` | `gui.json` |
| external-worker | `evidence/2026-09-30/history/external-worker/` | 批次内原相对层级；完整路径见 routes.json |
| fog-acceptance | `evidence/2026-09-30/history/fog-acceptance/` | `report.json` |
| handoffs | `evidence/2026-09-30/history/handoffs/` | 批次内原相对层级；完整路径见 routes.json |
| irc-acceptance | `evidence/2026-09-30/history/irc-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| layer-acceptance | `evidence/2026-09-30/history/layer-acceptance/` | `report.json` |
| log-fixtures | `evidence/2026-09-30/history/log-fixtures/` | `cclib-data-tree.json`、`cclib-tree.json` |
| molecularnodes-parameters | `evidence/2026-09-30/history/molecularnodes-parameters/` | `a-precheck-science.json` |
| multiwfn-parameters | `evidence/2026-09-30/history/multiwfn-parameters/` | `worktree-retirement.json` |
| nbo-acceptance | `evidence/2026-09-30/history/nbo-acceptance/` | `gui-undo.json` |
| nocv-acceptance | `evidence/2026-09-30/history/nocv-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| node-assets | `evidence/2026-09-30/history/node-assets/` | `report.json` |
| optimization-trajectory | `evidence/2026-09-30/history/optimization-trajectory/` | `candidate.json`、`document-checks.json` |
| repository-cleanup-merge | `evidence/2026-09-30/history/repository-cleanup-merge/` | `merge-receipt.json` |
| result-browser | `evidence/2026-09-30/history/result-browser/` | `final-receipt.json`、`gui-checks.json` |
| scalar-probe | `evidence/2026-09-30/history/scalar-probe/` | `manifest.json`、`result.json` |
| source-adoption | `evidence/2026-09-30/history/source-adoption/` | `final-audit.json`、`wheel-recovery.json` |
| storage-cleanup | `evidence/2026-09-30/history/storage-cleanup/` | `applied.json`、`branch-archive.json` |
| v1-acceptance | `evidence/2026-09-30/history/v1-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| vesta-comparison | `evidence/2026-09-30/history/vesta-comparison/` | `input.json` |
| visual-acceptance | `evidence/2026-09-30/history/visual-acceptance/` | `result.json` |
| visual-acceptance-v2 | `evidence/2026-09-30/history/visual-acceptance-v2/` | `result.json` |
| vmd-parameters | `evidence/2026-09-30/history/vmd-parameters/` | 批次内原相对层级；完整路径见 routes.json |
| volume-probe | `evidence/2026-09-30/history/volume-probe/` | `result.json` |
| workflow-migration | `evidence/2026-09-30/history/workflow-migration/` | 批次内原相对层级；完整路径见 routes.json |

根目录零散历史报告、脚本和日志集中在 `outputs/evidence/2026-09-30/history/root/`。全部任务原路径到现位置的 SHA-256 映射见维护批次 `path-map.jsonl.gz`；主检出源码引用同时记录固定 source_commit/source_path，main 后续改动时按该 Git 身份取回并核对摘要。本轮已改动文件的少量字节副本位于 `fixed-source-reference/`，修正收据为 `source-reference-fix.json`；`routes.json` 按原任务名称定位。原报告中的旧路径是历史信息，不能直接视为仍存在；未迁移且保留的科学原件另列 unknown_inputs。


## 持续维护

每次收尾更新本页当前交付与批次路由、任务状态、清理收据和 [CHANGELOG](CHANGELOG.md)。详细逐文件清单与策略留本批忽略目录；历史路径失效时明确可用性与重建方法，原始报告保持字节不变。未知、权限、占用或未保全对象原位保留，不以安全部分完成代替全部验收。
