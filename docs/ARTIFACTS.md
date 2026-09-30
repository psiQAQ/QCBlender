# 产物查找入口

更新：2026-09-30。任务状态见 `.scratch/`，原始报告负责验证结论；本页路由现存文件、候选、工程、重建方法和阻塞，不改变历史 Passed 或独立人工签署。

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
| 工作树与 outputs 维护 / 2026-09-30 | 验证 `aaf20f8`；归档 `archive/2026-09-30/chore/output-maintenance` | `outputs/evidence/2026-09-30/output-maintenance/`：`result.json`、`cleanup-safe/{summary,applied}.json`、`before/after.jsonl.gz`、`path-map.jsonl.gz`、`routes.json`、`protection-checks.json` | 安全部分完成；权限、占用和未知归属项保留，任务 02/03 保持 claimed | 本批脚本及命令 JSON；[维护规则](agents/storage-maintenance.md) |
| 清理复查补丁 qcf3 / 2026-09-30 | 源码 `a7f9b43`；已合并 `20bfdcd` | `outputs/evidence/2026-09-30/cleanup-followup/qcf3/`：`qualification.json`、`evidence-index.json`、`gui/`；[验证索引](acceptance/cleanup-validation.json) | 最新 ZIP 为 `outputs/candidates/current/qcblender-0.0.1.zip`；独立签署 Not Run | [开发说明](DEVELOPMENT.md)；资格与 GUI 覆盖见验证索引 |
| 仓库清理 / 2026-09-30 | `47fd82c` | `outputs/evidence/2026-09-30/cleanup-followup/f458/`，按旧相对路径查报告；保全收据 `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | f458 的 11 个目录、3 个 ZIP 访问拒绝，旧工作树及分支保留；旧 ZIP 不作为可用候选 | 原任务 `.scratch/repository-cleanup/`；原始输入与共用环境 |
| 输入集中与产物维护 / 2026-09-29 | `archive/2026-09-29/chore/storage-cleanup` | `outputs/evidence/2026-09-30/history/storage-cleanup/`：`applied.json`、`branch-archive.json`、冷重开日志 | 用户保全工程见下表；旧验证不继承为本轮通过 | [历史记录](acceptance/storage-cleanup.md)及当前开发说明 |

待验收候选大小 50,632,953 字节，SHA-256：`1e473b32892eab06d399a7940a14abd947c59a29dca8afc18efc3ccd56655a7a`。本轮重建探针通过安装、生命周期及双冷重开，随后清理其 ZIP、场景和隔离配置；保留命令、摘要和报告，不替换待验收候选，也不宣称 ZIP 字节复现。

## 保全工程与共用环境

| 位置 | 当前核对与用途 |
| --- | --- |
| `outputs/projects/user-session-20260930/current.blend` + `current.qcdata/` | 当前可见 Blender 工程；新进程 Dataset/11 项数组核对 Passed，见维护批次 `user-cold.json` |
| `outputs/projects/cleanup-followup-original/未命名.blend` + 同名 `.qcdata/` | 原任务保全快照，原字节与验证索引摘要一致 |
| `outputs/projects/recovery/pid3144-preserved/evidence.blend` + `evidence.qcdata/` | 历史用户工程；本轮新进程 4 个 Dataset、数组及 3 个 VDB 摘要和加载 Passed，见 `recovery-cold.json` |
| `outputs/recovery/`、`outputs/projects/recovery/另一个目录/` | 原始恢复资料及可读副本；部分对象访问拒绝，尚不能确认完整保全，原目录保留 |
| `outputs/build-site/`、`outputs/science/` | 共用构建工具和科学环境；现有锁定版本及清理后 69 项科学回归 Passed |
| `outputs/wheels/qualified/` | 显式核对的 11 个锁定 wheels 和 `backend-wheel.json`；版本/锁文件不变，见 `qualified-wheels.json`、`environment.json` |
| `outputs/backend-wheel.json` 与 `outputs/wheels/` 的旧后端 wheel | 默认记录对应的旧 wheel 不可读，原位保留；默认后端路径检查 Failed，不能当作已修复 |
| `outputs/cleanup-followup-20260930/b48c/outputs/qcf3/profile/` | 可见 Blender PID 14284 仍使用的安装配置；保留至会话正常退出后重新核对，不随旧任务删除 |
| `outputs/blender-dev/`、`outputs/blender-runtime.json` | 运行时记录引用的现有配置，保留；其引用解除前不清理 |
| `outputs/build-python/`、`build-sources/`、`gbasis-build/`、`native-backend-licenses/`、`reference-tools/`、`m0-research/`、`visualization-adoption/`、`repaired-wheels/`、`unrepaired-wheels/` | 构建来源、许可证、参考资料或尚待用途确认的环境；保留原路径，不自动归为重复环境 |

当前可复用的后端是 `wheels/qualified/backend-wheel.json` 与同目录 wheels 的配对，不是根目录旧记录。新工作树先核对锁定摘要，再把这份记录显式复制到该工作树忽略的 `outputs/backend-wheel.json`；打包传入 `--wheels-dir <主检出>/outputs/wheels/qualified`，科学检查传入 `--site <主检出>/outputs/science`。本轮可执行示例为证据中的 `rebuild.py`、`short-rebuild.py`、`after-validation.py` 和 `qualification.py`；它们固定本轮路径。新批次换成未使用的短目录，复用 [开发说明](DEVELOPMENT.md) 的退出码记录流程。

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

根目录零散历史报告、脚本和日志集中在 `outputs/evidence/2026-09-30/history/root/`。全部任务原路径到现位置的 SHA-256 映射见维护批次 `path-map.jsonl.gz`；`routes.json` 按原任务名称定位。原报告中的旧路径是历史信息，不能直接视为仍存在；未迁移且保留的科学原件另列 unknown_inputs。

## 本轮清理结果与后续维护

正式摘要盘点的可读普通文件从 86,043 个 / 4,423,648,046 字节变为 29,291 个 / 1,453,516,003 字节，净减少 2,970,132,043 字节（约 2.97 GB）。同口径排除不可读对象，包含新增的必要证据、工程和 qualified wheels；此为收据时间点大小，后续日志增加会改变现值。按清单成功删除 67,453 个文件 / 3,279,888,606 字节，另合并 37 个已核对报告副本并移除 15,031 个空目录。

- Passed：11,063 项迁移目标摘要，33 份报告、8 张截图与 CSV，104 个输入摘要，8 项清理边界测试，科学 69/69，保留候选资格核对、重建/安装/生命周期和原地/中文移动冷重开，用户工程 Dataset/数组/VDB，既有标签和源码子模块。
- Failed：168 个访问拒绝盘点项、两份活跃进程日志无法删除；f458 14 项拒绝与 b48c 空根占用，旧工作树/分支保留；旧默认后端 wheel 不可读。本轮首次长批次安装在中文解压路径超过 Windows 长度限制，日志保留；短批次复验 Passed。
- Not Run：独立人工科研签署；未扩展到全量历史 SOP、ACL 修改、远端发布或 push。

后续任务从本页添加一行日期、提交/归档标签、证据、工程、候选可用性、重建步骤和阻塞；收尾更新清理收据及 CHANGELOG。任务 policy 和详细清单放本批 evidence。未知内容默认保留，不按扩展名或“测试目录”名字删除；权限、占用及保全失败项保持 claimed。具体实施规则见[存储维护](agents/storage-maintenance.md)。
