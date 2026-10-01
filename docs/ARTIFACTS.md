# 产物查找入口

更新：2026-10-01。任务状态见 `.scratch/`，原始报告负责验证结论；本页路由现存文件、候选、工程、重建方法和阻塞，不改变历史 Passed 或独立人工签署。

## 目录与生命周期

| 位置 | 用途 |
| --- | --- |
| `outputs/evidence/<日期>/<任务>/` | 报告、成功与失败日志、生成脚本、来源、摘要、清理收据及被索引引用的必要截图 |
| `outputs/projects/<工程标识>/` | 用户 `.blend` 与完整 `.qcdata`，不按任务结束删除 |
| `outputs/candidates/current/` | 最新待验收 ZIP；替换前记录身份、资格和旧候选可用性 |
| `outputs/runs/<短任务名>/<短批次>/` | 临时工程、隔离配置及缓存，收尾保全后清理 |
| 共用环境及资料的现有路径 | `outputs/build-site`、`outputs/science`、`outputs/wheels`、构建源码及必要许可证；参考原件留在原资料目录 |

真实输入的唯一清单为 `tests/data/local-inputs.json`，来源见 [SOURCES](v1-acceptance/SOURCES.md)。没有确认用途的原件保留原位，具体路径见本批 `routes.json` 的 `unknown_inputs`；不把它们称为已迁移或已删除。

## 当前任务与候选

| 任务 / 日期 | 提交或标签 | 证据与主要报告 | 工程、候选与阻塞 | 重建入口 |
| --- | --- | --- | --- | --- |
| 教程点击补验与逐步骤截图 / 2026-10-01 | 验证1554ee2；截图初批90ff9bf，两批身份分列 | `outputs/evidence/2026-10-01/tutorial-cu/`；[补验索引](acceptance/tutorial-cu-validation.json)，动作/CSV/冷重开/原生测试/失败日志；24图在`docs/v1-acceptance/screenshot/` | 新候选`outputs/candidates/current/tutorial-cu-1554ee2/qcblender-0.0.1.zip`；工程`outputs/projects/tutorial-cu-20261001/tutorial-clicks.blend`及qcdata。完整点击02 claimed、03 pending，04截图resolved；用户与科研签署Not Run；本批退出配置与缓存已删8643项/488,083,431字节，未知恢复文件保留；归档收据见本批`closing.json` | [SOP](v1-acceptance/SOP.md)及索引重建步骤；旧初批候选保留历史基线身份 |
| 公共教程与节点可读性 / 2026-10-01 | 验证`90ff9bf`，已合入main；05/06 resolved；四个注释标签前缀`archive/2026-10-01/`，完整分支名与提交见验证索引 | `outputs/evidence/2026-10-01/public-tutorial-mcp/`：`qualification-mcp.json`、`cases.json`、`nodes-report.json`、`cold-{original,moved,unpacked}.json`、真实`screenshots/`及渲染；此前原生证据在`outputs/evidence/2026-09-30/public-tutorial/`；[索引](acceptance/tutorial-validation.json) | 最新候选`outputs/candidates/current/public-tutorial-90ff9bf/qcblender-0.0.1.zip`；新工程`outputs/projects/public-tutorial-mcp-20261001/tutorial.blend`及qcdata，归档ZIP在本批证据目录；`closing.json`与`cleanup-prep/{storage-result,preservation-mapping-final}.json`记录清理/旧路径映射，四新工作树/分支已正常移除。MCP技术验收Passed，用户复做/鼠标点击/独立签署Not Run；最终可见MCP进程PID21116使用独立`outputs/runs/pm/final-view/p`；旧活跃配置与历史权限阻塞保留 | [SOP](v1-acceptance/SOP.md)、manifest、[开发说明](DEVELOPMENT.md)及本批脚本；新批次不得覆盖历史证据 |
| 工作树与 outputs 维护 / 2026-09-30 | 验证 `aaf20f8`；已合并 `8188a41`，归档 `archive/2026-09-30/chore/output-maintenance` | `outputs/evidence/2026-09-30/output-maintenance/`：`result.json`、`cleanup-safe/{summary,applied}.json`、`before/after.jsonl.gz`、`path-map.jsonl.gz`、`routes.json`、`protection-checks.json`、`closing.json`、`worktree-preservation.json` | 本轮工作树及已合并分支已正常移除；旧权限/占用及未知对象保留，任务 02/03 保持 claimed | 本批命令 JSON（历史参数）；新批次按开发说明；[维护规则](agents/storage-maintenance.md) |
| 清理复查补丁 qcf3 / 2026-09-30 | 源码 `a7f9b43`；已合并 `20bfdcd` | `outputs/evidence/2026-09-30/cleanup-followup/qcf3/`：`qualification.json`、`evidence-index.json`、`gui/`；[验证索引](acceptance/cleanup-validation.json) | 历史 ZIP 暂保留于 `outputs/candidates/current/qcblender-0.0.1.zip`；签署 Not Run，待本轮验收后解除基线引用再清理 | [开发说明](DEVELOPMENT.md)；资格与 GUI 覆盖见验证索引 |
| 仓库清理 / 2026-09-30 | `47fd82c` | `outputs/evidence/2026-09-30/cleanup-followup/f458/`，按旧相对路径查报告；保全收据 `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | f458 的 11 个目录、3 个 ZIP 访问拒绝，旧工作树及分支保留；旧 ZIP 不作为可用候选 | 原任务 `.scratch/repository-cleanup/`；原始输入与共用环境 |
| 输入集中与产物维护 / 2026-09-29 | `archive/2026-09-29/chore/storage-cleanup` | `outputs/evidence/2026-09-30/history/storage-cleanup/`：`applied.json`、`branch-archive.json`、冷重开日志 | 用户保全工程见下表；旧验证不继承为本轮通过 | [历史记录](acceptance/storage-cleanup.md)及当前开发说明 |

本批IR显隐修复候选50,633,643字节，SHA-256 `694e27cbc328a64b9fe6bb07d6236273474de26de13af8d6f8e2c9cdbc98c4cd`；初批MCP教程基线候选仍保留，大小50,633,596字节，SHA-256：`4a0ac3e46c163dd32a53057ddb2f4e414901d7c56b95d59aa6d17a8df3b739ca`。公开样本包为`outputs/evidence/2026-09-30/public-tutorial/samples/qcblender-public-tutorial-samples-v1.zip`，SHA-256 `a4ccfc3ef91921817d17284196ba23ccfb7cce7b1643cdfa41af8e8a6103f85b`。本批新旧必要证据保全映射见`outputs/evidence/2026-10-01/public-tutorial-mcp/cleanup-prep/preservation-mapping-final.json`；历史路径按映射定位，不将已删除路径称为仍可直接取得。上轮qcf3候选暂保留，身份分别维护。上轮维护批次的重建探针通过安装、生命周期及双冷重开，随后清理其 ZIP、场景和隔离配置；保留命令、摘要和报告，不替换待验收候选，也不宣称 ZIP 字节复现。

本轮正式清理两次apply删除24,750个文件/1,845,200,762字节，执行失败0；清理后复验110项输入、69项科学回归及锁定环境重建Passed。盘点4,199,701,889→2,625,815,407字节，净减少1,573,886,482字节，包含新证据和独立最终可见配置；权限不可读目录内容不计入两端。保全映射1516项，旧报告字节保持；旧路径不再承诺直接可取，按映射查副本，已删除候选/缓存从保留输入和环境重建。`runs/pt/3/p`与`runs/pm/final-view/p`分别由活跃窗口使用，结束并保全后才清；未知输入/恢复文件与158项扫描阻塞原位保留。旧f458十四对象拒绝和b48c空根占用仍未解除，相关历史任务未resolved。

## 保全工程与共用环境

| 位置 | 当前核对与用途 |
| --- | --- |
| `outputs/projects/public-tutorial-mcp-20261001/tutorial.blend` + `tutorial.qcdata/` | MCP本批保全；55个科学对象绑定、1098次数组摘要、15个VDB，在原路径、中文移动和归档解包三个新可见进程Passed；截图/渲染/CSV/工程ZIP见本批证据和验证索引 |
| `outputs/projects/public-tutorial-90ff9bf/tutorial.blend` + `tutorial.qcdata/` | 本轮保全，256项副本摘要含候选/样本；42个科学对象绑定、785次数组摘要、12个VDB冷重开Passed；可见PID37508及独立`outputs/runs/pt/3/p`保持活跃保护 |
| `outputs/projects/user-session-20260930/current.blend` + `current.qcdata/` | 当前可见 Blender 工程；新进程 Dataset/11 项数组核对 Passed，见维护批次 `user-cold.json` |
| `outputs/projects/cleanup-followup-original/未命名.blend` + 同名 `.qcdata/` | 原任务保全快照，原字节与验证索引摘要一致 |
| `outputs/projects/recovery/pid3144-preserved/evidence.blend` + `evidence.qcdata/` | 历史用户工程；本轮新进程 4 个 Dataset、数组及 3 个 VDB 摘要和加载 Passed，见 `recovery-cold.json` |
| `outputs/recovery/`、`outputs/projects/recovery/另一个目录/` | 原始恢复资料及可读副本；部分对象访问拒绝，尚不能确认完整保全，原目录保留 |
| `outputs/build-site/`、`outputs/science/` | 共用构建工具和科学环境；现有锁定版本及清理后 69 项科学回归 Passed |
| `outputs/wheels/qualified/` | 显式核对的 11 个锁定 wheels 和 `backend-wheel.json`；版本/锁文件不变，见 `qualified-wheels.json`、`environment.json` |
| `outputs/backend-wheel.json` 与 `outputs/wheels/` 的旧后端 wheel | 默认记录对应的旧 wheel 不可读，原位保留；默认后端路径检查 Failed，不能当作已修复 |
| `outputs/cleanup-followup-20260930/b48c/outputs/qcf3/profile/` | 可见 Blender PID 14284 仍使用的安装配置；保留至会话正常退出后重新核对，不随旧任务删除 |
| `outputs/runs/pt/1`、`pt/2`、`outputs/runs/public-tutorial/` | 探索批次和子任务材料共约1.29GB；最终清理未执行，日志/原件归属及保全后按策略处理。`pt/3`为当前验收批次，活跃配置保留 |
| `outputs/blender-dev/`、`outputs/blender-runtime.json` | 运行时记录引用的现有配置，保留；其引用解除前不清理 |
| `outputs/build-python/`、`build-sources/`、`gbasis-build/`、`native-backend-licenses/`、`reference-tools/`、`m0-research/`、`visualization-adoption/`、`repaired-wheels/`、`unrepaired-wheels/` | 构建来源、许可证、参考资料或尚待用途确认的环境；保留原路径，不自动归为重复环境 |

当前可复用的后端是 `wheels/qualified/backend-wheel.json` 与同目录 wheels 的配对，不是根目录旧记录。新工作树先核对锁定摘要，再把这份记录显式复制到该工作树忽略的 `outputs/backend-wheel.json`；打包传入 `--wheels-dir <主检出>/outputs/wheels/qualified`，科学检查传入 `--site <主检出>/outputs/science`。本轮脚本 `rebuild.py`、`short-rebuild.py`、`after-validation.py` 和 `qualification.py` 保存实际参数；原工作树已移除，复验先创建干净工作树、显式复制并核对必要输入，然后改用新批次和报告位置，不能直接覆盖历史证据。新批次换成未使用的短目录，复用 [开发说明](DEVELOPMENT.md) 的退出码记录流程。

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

## 本轮清理结果与后续维护

正式摘要盘点的可读普通文件从 86,043 个 / 4,423,648,046 字节变为 29,291 个 / 1,453,516,003 字节，净减少 2,970,132,043 字节（约 2.97 GB）。同口径排除不可读对象，包含新增的必要证据、工程和 qualified wheels；此为收据时间点大小，后续日志增加会改变现值。按清单成功删除 67,453 个文件 / 3,279,888,606 字节，另合并 37 个已核对报告副本并移除 15,031 个空目录。

- Passed：11,063 项迁移目标摘要，33 份报告、8 张截图与 CSV，104 个输入摘要，8 项清理边界测试，科学 69/69，保留候选资格核对、重建/安装/生命周期和原地/中文移动冷重开，用户工程 Dataset/数组/VDB，既有标签和源码子模块。
- Failed：168 个访问拒绝盘点项、两份活跃进程日志无法删除；f458 14 项拒绝与 b48c 空根占用，旧工作树/分支保留；旧默认后端 wheel 不可读。本轮首次长批次安装在中文解压路径超过 Windows 长度限制，日志保留；短批次复验 Passed。
- Not Run：独立人工科研签署；未扩展到全量历史 SOP、ACL 修改、远端发布或 push。

后续任务从本页添加一行日期、提交/归档标签、证据、工程、候选可用性、重建步骤和阻塞；收尾更新清理收据及 CHANGELOG。任务 policy 和详细清单放本批 evidence。未知内容默认保留，不按扩展名或“测试目录”名字删除；权限、占用及保全失败项保持 claimed。具体实施规则见[存储维护](agents/storage-maintenance.md)。
