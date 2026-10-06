# 2026-09-30 cleanup-followup

2026-09-30清理复查及文件对话框预览修复。qcf3候选资格绑定a7f9b43；科学、单测、安装、节点资产、恢复、图例、冷读与来源浏览Passed。用户未保存会话另存后冷读Passed；f458权限和当时b48c占用使清理总体Failed，不改变ACL。

原目录：`outputs/evidence/2026-09-30/cleanup-followup/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/cleanup-followup-20260930/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `docs/acceptance/cleanup-validation.json` | `date` | `2026-09-30` |
| `docs/acceptance/cleanup-validation.json` | `source.commit` | `a7f9b431f5cf15980fd373f4f6482ef0d4e128bd` |
| `docs/acceptance/cleanup-validation.json` | `source.product_tree` | `c0a54011974d7553a653b50ab12424769cde7ffe` |
| `docs/acceptance/cleanup-validation.json` | `candidate.path` | `outputs/candidates/current/qcblender-0.0.1.zip` |
| `docs/acceptance/cleanup-validation.json` | `candidate.sha256` | `1e473b32892eab06d399a7940a14abd947c59a29dca8afc18efc3ccd56655a7a` |
| `docs/acceptance/cleanup-validation.json` | `candidate.bytes` | `50632953` |
| `outputs/evidence/2026-09-30/cleanup-followup/qcf3/qualification.json` | `source_commit` | `a7f9b431f5cf15980fd373f4f6482ef0d4e128bd` |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/qualification.json` | `source_commit` | `87b5316e95552929bda8f0f7e74129ea84ab49bd` |
| `outputs/evidence/2026-09-30/cleanup-followup/f458/outputs/repository-cleanup/final/qualification.json` | `source_commit` | `1b87751616ecb03d89f6a8c0e96cac99544b420a` |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/checkpoints/850163e/qualification.json` | `source_commit` | `850163ec678173df982629cf88d5a9c3d12233b3` |

## 结果与条件

版本控制中的汇总索引：

| 记录 | 检查 | 历史状态或参数 |
| --- | --- | --- |
| `docs/acceptance/cleanup-validation.json` | `status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.science.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.science.tests` | `69` |
| `docs/acceptance/cleanup-validation.json` | `coverage.science.failures` | `0` |
| `docs/acceptance/cleanup-validation.json` | `coverage.science.errors` | `0` |
| `docs/acceptance/cleanup-validation.json` | `coverage.science.skipped` | `0` |
| `docs/acceptance/cleanup-validation.json` | `coverage.non_science_units.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.non_science_units.tests` | `11` |
| `docs/acceptance/cleanup-validation.json` | `coverage.node_helpers` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.installation_lifecycle_assets` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.original_and_chinese_moved_cold_reopen` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.recovery` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.legend_and_both_cold_reopens` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.result_browser_and_stale_preview_regression` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `coverage.full_historical_SOP` | `Not Run` |
| `docs/acceptance/cleanup-validation.json` | `coverage.performance_and_full_grid_convergence` | `Not Run` |
| `docs/acceptance/cleanup-validation.json` | `coverage.independent_scientific_signature` | `Not Run` |
| `docs/acceptance/cleanup-validation.json` | `coverage.other_platforms_and_public_release` | `Not Run` |
| `docs/acceptance/cleanup-validation.json` | `gui.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.build-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.cold-moved-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.cold-original-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.copy-inputs-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.environment-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.helpers-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.index-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.inputs-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.install-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.legend-cold-moved-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.legend-cold-original-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.legend-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.qualification-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.recovery-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.result-browser-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.science-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.test_copy_display-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.test_legend_layout-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.test_local_inputs-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.test_storage_cleanup-command.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.result-browser/checks.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.science.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.node-assets.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.extension-install.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.extension-cold-original.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.extension-cold-moved.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.recovery.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.legend-cold-moved.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.qualification.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.evidence-index.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.gui/profile-check.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.gui/cold-reopen.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `reports.gui/energy-animation.json.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `storage.user_cold_reopen.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `storage.cleanup.status` | `Failed` |
| `docs/acceptance/cleanup-validation.json` | `storage.cleanup.local_merge` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `storage.maintenance.status` | `Failed` |
| `docs/acceptance/cleanup-validation.json` | `history.baseline.status` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `history.qcf2.technical` | `Passed` |
| `docs/acceptance/cleanup-validation.json` | `history.qcf2.GUI_import` | `Failed` |

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/inventory/summary.json` | `[0].status`=Failed；`[1].status`=Passed；`[0].scope`=Read-only inventory; preservation and deletion Not Run；`[1].scope`=Read-only inventory; preservation and deletion Not Run |
| `outputs/evidence/2026-09-30/cleanup-followup/qcf3/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.result-browser/checks.json.report.status`=Passed；`evidence.result-browser/checks.json.report.preview_without_scene_or_dataset`=Passed；`evidence.result-browser/checks.json.report.selected_jobs`=Passed；`evidence.result-browser/checks.json.report.new_dialog_resets_previous_preview`=Passed；`evidence.result-browser/checks.json.report.spectrum_parent_binding`=Passed；`evidence.result-browser/checks.json.report.changed_source_rejected`=Passed；`evidence.result-browser/checks.json.report.same_filename_different_source`=Passed；`evidence.result-browser/checks.json.report.metadata_only_and_duplicate`=Passed；`evidence.result-browser/checks.json.report.broken_binding`=Passed；`evidence.result-browser/checks.json.report.malformed_and_legacy_missing_metadata`=Passed；`evidence.result-browser/checks.json.report.portable_save`=Passed；`evidence.result-browser/checks.json.report.C04.status`=Passed；`evidence.result-browser/checks.json.report.C07.status`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=69；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.skipped`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176；`evidence.legend-cold-moved.json.report.bars.default.vertices`=130；`evidence.legend-cold-moved.json.report.bars.horizontal.vertices`=130；`evidence.legend-cold-moved.json.report.bars.vertical.vertices`=130；`evidence.legend-cold-moved.json.report.bars.rotated.vertices`=130 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science.json.report.status`=Passed；`evidence.node-assets.json.report.status`=Passed；`evidence.node-assets.json.report.shared_unbound_asset`=Passed；`evidence.node-assets.json.report.independent_parameters`=Passed；`evidence.node-assets.json.report.independent_source_transforms`=Passed；`evidence.node-assets.json.report.preserved_branch`=Passed；`evidence.node-assets.json.report.library_roundtrip`=Passed；`evidence.extension-install.json.report.status`=Passed；`evidence.extension-install.json.report.offline_install`=Passed；`evidence.extension-install.json.report.worker_import_evaluate`=Passed；`evidence.extension-install.json.report.cancel`=Passed；`evidence.extension-install.json.report.lifecycle`=Passed；`evidence.extension-install.json.report.repeated_field_cache`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=69；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.skipped`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176；`evidence.legend-cold-moved.json.report.bars.default.vertices`=130；`evidence.legend-cold-moved.json.report.bars.horizontal.vertices`=130；`evidence.legend-cold-moved.json.report.bars.vertical.vertices`=130；`evidence.legend-cold-moved.json.report.bars.rotated.vertices`=130 |
| `outputs/evidence/2026-09-30/cleanup-followup/f458/outputs/repository-cleanup/final/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science.json.report.status`=Passed；`evidence.unit.json.report.status`=Passed；`evidence.extension.json.report.status`=Passed；`evidence.extension.json.report.offline_install`=Passed；`evidence.extension.json.report.worker_import_evaluate`=Passed；`evidence.extension.json.report.cancel`=Passed；`evidence.extension.json.report.lifecycle`=Passed；`evidence.extension.json.report.repeated_field_cache`=Passed；`evidence.extension.json.report.threshold_updates_geometry`=Passed；`evidence.extension.json.report.phase_switches`=Passed；`evidence.extension.json.report.field_cache_unchanged`=Passed；`evidence.extension.json.report.cold_open`=Passed；`evidence.extension.json.report.portable_archive`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=69；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.skipped`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176；`evidence.unit.json.report.tests`=11；`evidence.unit.json.report.failures`=0；`evidence.unit.json.report.errors`=0；`evidence.unit.json.report.skipped`=0 |
| `outputs/evidence/2026-09-30/cleanup-followup/f458/outputs/repository-cleanup/phase02/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science.json.report.status`=Passed；`evidence.unit.json.report.status`=Passed；`evidence.extension.json.report.status`=Passed；`evidence.extension.json.report.offline_install`=Passed；`evidence.extension.json.report.worker_import_evaluate`=Passed；`evidence.extension.json.report.cancel`=Passed；`evidence.extension.json.report.lifecycle`=Passed；`evidence.extension.json.report.repeated_field_cache`=Passed；`evidence.extension.json.report.threshold_updates_geometry`=Passed；`evidence.extension.json.report.phase_switches`=Passed；`evidence.extension.json.report.field_cache_unchanged`=Passed；`evidence.extension.json.report.cold_open`=Passed；`evidence.extension.json.report.portable_archive`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=69；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.skipped`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176；`evidence.unit.json.report.tests`=11；`evidence.unit.json.report.failures`=0；`evidence.unit.json.report.errors`=0；`evidence.unit.json.report.skipped`=0 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/checkpoints/850163e/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science.json.report.status`=Passed；`evidence.node-assets.json.report.status`=Passed；`evidence.node-assets.json.report.shared_unbound_asset`=Passed；`evidence.node-assets.json.report.independent_parameters`=Passed；`evidence.node-assets.json.report.independent_source_transforms`=Passed；`evidence.node-assets.json.report.preserved_branch`=Passed；`evidence.node-assets.json.report.library_roundtrip`=Passed；`evidence.extension-install.json.report.status`=Passed；`evidence.extension-install.json.report.offline_install`=Passed；`evidence.extension-install.json.report.worker_import_evaluate`=Passed；`evidence.extension-install.json.report.cancel`=Passed；`evidence.extension-install.json.report.lifecycle`=Passed；`evidence.extension-install.json.report.repeated_field_cache`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=69；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.skipped`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176；`evidence.legend-cold-moved.json.report.bars.default.vertices`=130；`evidence.legend-cold-moved.json.report.bars.horizontal.vertices`=130；`evidence.legend-cold-moved.json.report.bars.vertical.vertices`=130；`evidence.legend-cold-moved.json.report.bars.rotated.vertices`=130 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/node-assets/report.json` | `status`=Passed；`shared_unbound_asset`=Passed；`independent_parameters`=Passed；`independent_source_transforms`=Passed；`preserved_branch`=Passed；`library_roundtrip`=Passed |
| `outputs/evidence/2026-09-30/cleanup-followup/f458/outputs/node-assets/report.json` | `status`=Passed；`shared_unbound_asset`=Passed；`independent_parameters`=Passed；`independent_source_transforms`=Passed；`preserved_branch`=Passed；`library_roundtrip`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/inventory/summary.json` | `[0].status` | Failed | [0].scope=Read-only inventory; preservation and deletion Not Run |
| `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | `final.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/docs/acceptance/cleanup-validation.json` | `history.qcf2.GUI_import` | Failed | history.qcf2.scope=Historical; not inherited into qcf3 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/validation-index-draft.json` | `human_guide_check.checks.line_profile` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/validation-index-draft.json` | `human_guide_check.status` | Failed | human_guide_check.reason=New FCHK file dialog inherited previous Log preview digest/job; minimal product fix proposal awaiting scope decision |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/inventory/f458-summary.json` | `status` | Failed | scope=Read-only inventory; preservation and deletion Not Run |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf1/legend-command.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | `status` | Failed | scope=All readable regular files except Git pointers; blocked objects retained in original worktree |
| `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | `worktrees[0].status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf1/extension-install.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/docs/acceptance/cleanup-validation.json` | `coverage.full_historical_SOP` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/docs/acceptance/cleanup-validation.json` | `coverage.independent_scientific_signature` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/docs/acceptance/cleanup-validation.json` | `coverage.other_platforms_and_public_release` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/docs/acceptance/cleanup-validation.json` | `coverage.performance_and_full_grid_convergence` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/checkpoints/850163e/qualification.json` | `evidence.extension-install.json.report.cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | `final.push` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/validation-index-draft.json` | `human_guide_check.checks.portable_save_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/legend-cold-original.json` | `moved_cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/cleanup-followup/validation-index-draft.json` | `status` | Not Run | scope=Draft pending task 04; task 05 not claimed |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/legend-cold-original.json` | `status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/human/evidence/import-state-probe.json` | `checks.explicit_preview_digest_guard.worker_status` | failed | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/human/evidence/import-state-probe.json` | `checks.original.worker_status` | failed | 原字段未附原因 |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/human/evidence/import-diagnostic.json` | `observed_worker_status` | failed | scope=Read-only diagnosis of failed human FCHK import; product fix Not Run; error=ValueError: Source changed after preview; preview the file again |
| `outputs/evidence/2026-09-30/cleanup-followup/b48c/outputs/qcf2/human/evidence/failed-import-result.json` | `status` | failed | error=ValueError: Source changed after preview; preview the file again |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
