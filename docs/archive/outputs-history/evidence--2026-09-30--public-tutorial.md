# 2026-09-30 public-tutorial

2026-09-30公开样本、节点可读性及教程构建。冻结公开输入与许可保持集中入口；早期Computer Use阻塞和技术检查分开。

原目录：`outputs/evidence/2026-09-30/public-tutorial/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/runs/public-tutorial/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification.json` | `source_commit` | `90ff9bf799aaa299225cd188ce8f05e1b6baf895` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.browser-command.report.status`=Passed；`evidence.browser-initial.report.status`=Passed；`evidence.browser-initial.report.preview_without_scene_or_dataset`=Passed；`evidence.browser-initial.report.selected_jobs`=Passed；`evidence.browser-initial.report.new_dialog_resets_previous_preview`=Passed；`evidence.browser-initial.report.spectrum_parent_binding`=Passed；`evidence.browser-initial.report.changed_source_rejected`=Passed；`evidence.browser-initial.report.same_filename_different_source`=Passed；`evidence.browser-initial.report.metadata_only_and_duplicate`=Passed；`evidence.browser-initial.report.broken_binding`=Passed；`evidence.browser-initial.report.malformed_and_legacy_missing_metadata`=Passed；`evidence.browser-initial.report.portable_save`=Passed；`evidence.browser-initial.report.C04.status`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.legend-cold-moved.report.bars.default.vertices`=130；`evidence.legend-cold-moved.report.bars.horizontal.vertices`=130；`evidence.legend-cold-moved.report.bars.vertical.vertices`=130；`evidence.legend-cold-moved.report.bars.rotated.vertices`=130 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/science.json` | `status`=Passed；`tests`=69；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r2/science.json` | `status`=Passed；`tests`=69；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/science.json` | `status`=Passed；`tests`=69；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `status`=Not Run；`blockers[0].status`=Not Run；`blockers[1].status`=Not Run；`blockers[2].status`=Not Run；`blockers[2].historical_status`=Failed；`blockers[3].status`=Not Run；`blockers[3].historical_status`=Failed；`scope`=Cleanup preparation only; integrated GUI gate is pending |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `status`=Not Run；`technical_merge_and_preservation`=Passed；`product_tree_unchanged`=Passed；`main_clean`=Passed；`branches.chore/tutorial-samples.reachable_from_main`=Passed；`branches.chore/node-layout.reachable_from_main`=Passed；`branches.docs/public-tutorial.reachable_from_main`=Passed；`branches.chore/tutorial-validation.reachable_from_main`=Passed；`computer_use`=Not Run；`screenshots`=Not Run；`archive_and_worktree_cleanup`=Not Run；`push`=Not Run；`independent_signature`=Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/computer-use-blocker.json` | `status`=Not Run；`actual_clicks`=Not Run；`screenshots`=Not Run；`new_candidate_mcp`=Not Run；`independent_signature`=Not Run；`scope`=Approved Computer Use runtime reset and list_apps retried |
| `outputs/evidence/2026-09-30/public-tutorial/preservation.json` | `status`=Passed；`scope`=Verified copies; original runs and profiles retained pending GUI |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/public-tutorial/integration/commands.json` | `[17].status` | Failed | [17].name=profile; [17].exit_code=1 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/commands.json` | `[18].status` | Failed | [18].name=profile-r2; [18].exit_code=1 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/attempt-1/commands.json` | `[1].status` | Failed | [1].name=samples; [1].exit_code=1 |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `blockers[2].historical_status` | Failed | blockers[2].reason=Prior receipt records 14 inaccessible objects; retained without ACL changes |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `blockers[3].historical_status` | Failed | blockers[3].reason=Prior receipt records process lock; still empty and retained |
| `outputs/evidence/2026-09-30/public-tutorial/integration/attempt-1/samples-command.json` | `status` | Failed | name=samples; exit_code=1 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/profile-command.json` | `status` | Failed | name=profile; exit_code=1 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/profile-r2-command.json` | `status` | Failed | name=profile-r2; exit_code=1 |
| `outputs/evidence/2026-09-30/public-tutorial/preflight/first-attempt.json` | `status` | Failed | error=UnicodeDecodeError: gbk cannot decode UTF-8 local-inputs.json |
| `outputs/evidence/2026-09-30/public-tutorial/computer-use-blocker.json` | `actual_clicks` | Not Run | scope=Approved Computer Use runtime reset and list_apps retried; error=Computer Use native pipe is unavailable |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `archive_and_worktree_cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `blockers[0].status` | Not Run | blockers[0].reason=Task 05 actual Computer Use validation not completed |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `blockers[1].status` | Not Run | blockers[1].reason=Preservation completed; final cleanup waits for integrated acceptance |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `blockers[2].status` | Not Run | blockers[2].reason=Prior receipt records 14 inaccessible objects; retained without ACL changes |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `blockers[3].status` | Not Run | blockers[3].reason=Prior receipt records process lock; still empty and retained |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/tutorial-native-progress.json` | `cases.N17_native.invalid_point_gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/extension-install.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `computer_use` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/tutorial-cold-moved.json` | `computer_use` | Not Run | scope=New native process reads portable tutorial datasets, array digests and VDB grids; GUI Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/visible-launch.json` | `computer_use` | Not Run | scope=Visible Blender launch and native initialization only; Computer Use clicks, screenshots and new-candidate MCP Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/preflight/environment.json` | `computer_use.status` | Not Run | computer_use.error=Computer Use native pipe is unavailable |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.camera-initial.report.moved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.camera-initial.report.saved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.camera-saved.report.moved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.checkpoints.report.gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.checkpoints.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.extension-install.report.cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.native-summary.report.computer_use` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.native-summary.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.profile-initial.report.moved_cold_reopen_csv` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.profile-initial.report.saved_cold_reopen_csv` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.profile-saved.report.moved_cold_reopen_csv` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.samples.report.gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.samples.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.samples.report.original_checkpoint_density` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.tutorial-cold-moved.report.computer_use` | Not Run | evidence.tutorial-cold-moved.report.scope=New native process reads portable tutorial datasets, array digests and VDB grids; GUI Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.tutorial-cold-original.report.computer_use` | Not Run | evidence.tutorial-cold-original.report.scope=New native process reads portable tutorial datasets, array digests and VDB grids; GUI Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/qualification-retained.json` | `evidence.tutorial-native.report.cases.N17_native.invalid_point_gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/checkpoints.json` | `gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/checkpoints.json` | `independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/preflight/environment.json` | `independent_scientific_signature` | Not Run | scope=Preparation only; no new-candidate qualification or GUI acceptance |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `independent_signature` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/computer-use-blocker.json` | `independent_signature` | Not Run | scope=Approved Computer Use runtime reset and list_apps retried; error=Computer Use native pipe is unavailable |
| `outputs/evidence/2026-09-30/public-tutorial/integration/legend-cold-original.json` | `moved_cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r2/camera-initial.json` | `moved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r2/profile-initial.json` | `moved_cold_reopen_csv` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/computer-use-blocker.json` | `new_candidate_mcp` | Not Run | scope=Approved Computer Use runtime reset and list_apps retried; error=Computer Use native pipe is unavailable |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/visible-launch.json` | `new_candidate_mcp` | Not Run | scope=Visible Blender launch and native initialization only; Computer Use clicks, screenshots and new-candidate MCP Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r2/samples.json` | `original_checkpoint_density` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `push` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r2/camera-initial.json` | `saved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r2/profile-initial.json` | `saved_cold_reopen_csv` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `screenshots` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/computer-use-blocker.json` | `screenshots` | Not Run | scope=Approved Computer Use runtime reset and list_apps retried; error=Computer Use native pipe is unavailable |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/visible-launch.json` | `screenshots` | Not Run | scope=Visible Blender launch and native initialization only; Computer Use clicks, screenshots and new-candidate MCP Not Run |
| `outputs/evidence/2026-09-30/public-tutorial/cleanup-pending.json` | `status` | Not Run | scope=Cleanup preparation only; integrated GUI gate is pending |
| `outputs/evidence/2026-09-30/public-tutorial/closing-progress.json` | `status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/public-tutorial/computer-use-blocker.json` | `status` | Not Run | scope=Approved Computer Use runtime reset and list_apps retried; error=Computer Use native pipe is unavailable |
| `outputs/evidence/2026-09-30/public-tutorial/integration/r3/tutorial-native-progress.json` | `status` | Not Run | scope=Partial native checks only; GUI Not Run |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
