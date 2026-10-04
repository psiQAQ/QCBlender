# 产物查找入口

更新：2026-10-04。本页路由当前文件、归档身份、重建方法与阻塞；各原始报告保留其执行时的状态和候选身份。任务状态在 `.scratch/`，开发顺序见 [DEVELOPMENT](DEVELOPMENT.md)，保留与清理边界见 [维护规则](agents/storage-maintenance.md)。

## 当前交付

当前候选为`outputs/candidates/current/audit-p1-a4baaaf/qcblender-0.0.1.zip`，50638451字节，SHA-256 `039306fdcbf908bc020b29246f54dc2f8e2459e9413844b1a80a45ec5b036fb9`。产品源码`a4baaaf2cf163d93d8d7e25f3c9bd5e96ae01c3d`，产品树`c1a5bc48b035434c4a3245909e1e629bec4f0665`；[P1验证](acceptance/audit-p1-validation.md)及[机器索引](acceptance/audit-p1-validation.json)记录97科学测试、六视觉场景及其迁移冷读、原生关联/共享mesh、GUI/Undo/Redo和保存冷重开Passed。独立人工签署Not Run。

证据位于`outputs/evidence/2026-10-04/audit-p1/`；`evidence-index.json`及`qualification-main.json`绑定候选，`preservation-map.json`保存旧路径和原字节摘要。工程在`outputs/projects/audit-p1/{native,visual,gui}/`。完整本地归档与推送状态见[交付收据](acceptance/audit-p1-delivery.json)。重建沿用[开发说明](DEVELOPMENT.md)的共用环境与11锁定wheels，在新批次运行本批脚本并重新资格验证。

本批main已ff-only合并并普通HTTPS推送，远端回读`747ae8d`；三个注释归档标签、三个工作树/分支正常移除Passed。清单删除16,801文件/812,107,170字节，600个保护文件及2,407条保全映射摘要复核Passed。该数值为删除文件大小总和，不是全仓净空间变化。最终文档推送回读及完整身份见上述交付收据；旧权限/占用对象保持原状。

## 2026-10-04 P2与基准历史交付

该批候选为`outputs/candidates/current/audit-p2-49872b0/qcblender-0.0.1.zip`，50,635,805字节，SHA-256 `41cd978f36737236049fc901504c0196f4e6499adc891f1d2f09e2fabf4cebfd`。产品源码树`f3742ab452dd96a357bb7e17c1dfa55934b8897d`；[本批验证](acceptance/audit-p2-baselines-validation.md)、[机器索引](acceptance/audit-p2-baselines-validation.json)。本地资格Passed，独立人工签署Not Run。

证据位于`outputs/evidence/2026-10-04/audit-p2/`：`evidence-index.json`与`qualification.json`绑定当前候选；`preservation-map.json`保存原始路径及SHA-256，全部成功/失败报告字节保留。六个参考工程在`outputs/projects/audit-p2/visual/<case>/`，实际GUI工程在`outputs/projects/audit-p2/gui/p2-verified.blend + .qcdata/`；迁移后冷重开报告在`delivery-cold/`。基准PNG/JSON在`tests/data/visual-baseline/`，重建与运行见[基准说明](acceptance/visual-performance-baselines.md)。

本批五个注释归档标签、五工作树/分支正常移除及main推送Passed；清理27,111文件/6,425,543,091字节，475项保护文件摘要复核Passed。完整身份见[交付收据](acceptance/audit-p2-delivery.json)和`closing/`；原截图工作树路径由`closing/current-preservation-routes.json`映射到主检出。旧f458/b48c继续保持既有延期状态。

## 2026-10-02 显示/XYZ/CSV历史交付

| 对象 | 当前入口与状态 |
| --- | --- |
| 插件候选 | `outputs/candidates/current/display-xyz-export-9d3ff61/qcblender-0.0.1.zip`；源码`9d3ff61d2e32c47357fe624cf93052bfed6dd041`，SHA-256`362b87d3d1f41ec949da8597a47b248e7ef74ca574d96454d1dda31100556ce9`，50,635,717字节；本地资格Passed，未发布 |
| 当前验证 | [显示/XYZ/CSV索引](acceptance/display-xyz-export-validation.json)；`outputs/evidence/2026-10-02/display-xyz-export/final/`的42份通过报告、qualification.json、证据索引与完整命令/日志；早期目录缺陷Failed保持在同任务gui/ |
| 教程与截图 | [SOP](v1-acceptance/SOP.md)，C01–C13/N01–N18和新增X01；当前图位于`screenshot/display-xyz-export/`且紧接步骤，图注区分e317/9d及MCP准备；用户复做/独立签署Not Run |
| 公开样本 | [样本交付](acceptance/tutorial-sample-delivery.json)；`outputs/evidence/2026-10-02/display-xyz-export/final/samples/qcblender-public-tutorial-samples-v2.zip`；SHA-256`b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`，12,175,753字节；P06两份XYZ，自有数据CC BY 4.0；P02独立获取 |
| 保全工程与数据 | `outputs/projects/display-xyz-export/gui/evidence.blend + evidence.qcdata/`，12Dataset/249数组/1VDB，原地及中文移动冷读Passed；`final/data/native-exports/`保存全量/筛选CSV，`final/gui/exports/`保存实际点击导出 |
| 复用登记 | [Blender规则](agents/blender-interaction.md)、[操作登记](acceptance/blender-operations.json)；历史GUI身份不重写，产品单行目录修复后重新点击；旧图形工程另有兼容导出报告 |
| 构建与重建 | 共用`outputs/build-site/`、`outputs/science/`、`outputs/wheels/qualified/`及后端记录保持；当前索引列源文件/wheel摘要、实际命令和脚本，按[DEVELOPMENT](DEVELOPMENT.md)在新批次重建并重新验证ZIP身份 |
| 本轮归档与清理 | [清理收据](acceptance/display-xyz-export-cleanup.json)；四个注释标签及本轮工作树/分支清理Passed，另删一个已归档旧分支；11,095文件/1,073,258,330字节清理，63,383保留摘要核对。`closing/`保存映射和原收据；旧f458及空b48c占用按用户许可延期 |

本批82科学测试、21相关单测、严格XYZ和七类CSV/取消/旧谱图、显示精度、九公共资产、安装及冷重开通过。完整C/N历史范围见[教程历史资格](acceptance/tutorial-final-qualification.json)；本批仅对改动及其受影响范围复验，不将旧报告绑定新ZIP。科学输入的唯一清单仍为`tests/data/local-inputs.json`，来源见[SOURCES](v1-acceptance/SOURCES.md)。

本轮四个标签为`archive/2026-10-02/feat/display-precision`、`feat/xyz-import`、`feat/data-export`和`chore/display-xyz-export`（后三者沿用同一日期前缀），固定各分支最终提交；精确身份见清理收据。只保留9d3ff61候选，e317及b8a旧ZIP已删除，原科学/GUI报告、成功失败日志与摘要不改写。清理后离线重建Passed，临时ZIP已清理；新原生进程再次冷读保全工程Passed。原批命令中的runs/旧工作树路径通过`closing/preservation-map.json`、`workspace-preservation-final.json`定位保留字节，新验证使用新的批次。删除字节不计正常Git工作树移除及新增中央证据，不能当作全仓净空间变化。

## 历史教程归档、清理和阻塞

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

## 2026-10-03 完成度与参考实现调研

[完整报告](research/qcblender-completion-audit-2026-10-03.md)固定 main `96f9c7e`；报告和任务记录位于 `research/plugin-audit` 工作树，尚未提交或合并。产品源码、依赖和候选保持原身份。

| 对象 | 当前入口与状态 |
| --- | --- |
| 研究证据 | 主仓 `outputs/evidence/2026-10-03/plugin-audit/`；82科学测试、30相关单测通过，1项POSIX检查在Windows跳过；安装、XYZ/CSV、来源浏览和冷重开Passed |
| 缺陷与比较 | 四类产品缺陷未修复；两类P1经原生operator和实际Computer Use复现。报告含六个参考项目/软件的十维比较、已采用项、许可材料及五项改进建议；独立用户/科研签署及发布Not Run |
| 保全工程 | 主仓 `outputs/projects/plugin-audit/`，按原批次相对目录保留 `.blend + .qcdata`；`xyz-seeded/integration.blend`与`gui/linked-observed.blend`迁移后新进程冷读Passed，GUI工程有意保留缺陷状态 |
| 原始身份与映射 | `preservation-map.json`保存所有旧路径、目标、大小和SHA-256；`final-verification.json`复核保留副本、候选、当前主检出和链接；原始收据中的runs路径保持不变 |
| 清理与限制 | `cleanup-receipt.json`记录6,036文件/500,234,681字节删除，含已保全副本和本次独立profile；不是全仓净节省。74文件/207,636字节已复制核对，原件因十个目录权限边界保留；不修改ACL/所有权，清理状态Partial |

复跑先阅读证据目录`README.md`，复制所需脚本到新的runs批次，从保留候选重新安装隔离环境并生成前置fixture；科学输入沿用`tests/data/local-inputs.json`。不要直接运行归档脚本覆盖历史证据。旧路径通过映射解析；本次安装环境已经清理。
