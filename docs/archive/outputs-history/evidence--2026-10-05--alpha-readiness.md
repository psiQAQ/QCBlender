# 2026-10-05 alpha-readiness

2026-10-05本地Alpha，固定19e4cf0becf5a5173d692d1f4a9c621e6d01512e，run ID 0；127标准库/67公开科学/123完整科学、12次六视觉、真实GUI、取消、Undo/Redo和中文移动冷读Passed。GUI P01 alpha MO9，0.2 Å间距、3 Å余量、512 MiB预算、等值0.045 bohr^-3/2。许可/独立使用者及科研签署/发布门禁Not Run。

原目录：`outputs/evidence/2026-10-05/alpha-readiness/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/projects/alpha-readiness/`、`outputs/runs/alpha-summary/`、`outputs/ag1/`、`outputs/ag2/`、`outputs/ag3/`、`outputs/ag4/`、`outputs/ag5/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `docs/acceptance/alpha-readiness-validation.json` | `date` | `2026-10-05` |
| `docs/acceptance/alpha-readiness-validation.json` | `source_commit` | `19e4cf0becf5a5173d692d1f4a9c621e6d01512e` |
| `docs/acceptance/alpha-readiness-validation.json` | `product_tree` | `5db4996cbb456f52529c86219d85f0db0541ae49` |
| `docs/acceptance/alpha-readiness-validation.json` | `candidate.path` | `outputs/candidates/current/alpha-0.1.0-19e4cf0/qcblender-0.1.0.zip` |
| `docs/acceptance/alpha-readiness-validation.json` | `candidate.sha256` | `0c2d9add59b6332f243c5cd87b852a38b94090286f1b7671d7666694a4b73a03` |
| `docs/acceptance/alpha-readiness-validation.json` | `candidate.bytes` | `50656085` |
| `docs/acceptance/alpha-readiness-validation.json` | `candidate.candidate_run_id` | `0` |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `historical_failures[0].source_commit` | `78459e1` |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `historical_failures[1].source_commit` | `a5de54b` |

## 结果与条件

版本控制中的汇总索引：

| 记录 | 检查 | 历史状态或参数 |
| --- | --- | --- |
| `docs/acceptance/alpha-readiness-validation.json` | `status` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.stdlib_127` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.public_science_67_no_skip` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.full_science_123_no_skip` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.build_install_register_unregister` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.original_and_moved_cold` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.six_visual_fresh_and_cold_12` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.related_GUI` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.Standards` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `checks.Spec` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.status` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.async_qualification` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.pre_job_dialog_cancel` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.MO9_generation` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.menu_undo` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.menu_redo` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.live_isovalue` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.render` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.summary_export` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.summary_cancel` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.portable_save` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.chinese_move_hashes` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.new_process_cold` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.cold_summary_parity` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.checks.normal_exit` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gui.independent_human_acceptance` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `historical_failures[0].status` | `Failed` |
| `docs/acceptance/alpha-readiness-validation.json` | `historical_failures[1].status` | `Failed` |
| `docs/acceptance/alpha-readiness-validation.json` | `historical_failures[2].status` | `Passed` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.actual_GitHub_CI` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.draft_creation` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.component_license_review` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.independent_short_SOP_installation` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.maintainer_public_approval` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.post_release_download_hash` | `Not Run` |
| `docs/acceptance/alpha-readiness-validation.json` | `gates.full_v1_independent_human_and_science_acceptance` | `Not Run` |

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/completion.json` | `status`=Passed；`remote_steps`=Not Run |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/reports/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.stdlib.report.status`=Passed；`evidence.public-science.report.status`=Passed；`evidence.node-helpers.report.status`=Passed；`evidence.extension-install.report.status`=Passed；`evidence.extension-install.report.offline_install`=Passed；`evidence.extension-install.report.worker_import_evaluate`=Passed；`evidence.extension-install.report.cancel`=Passed；`evidence.extension-install.report.lifecycle`=Passed；`evidence.extension-install.report.repeated_field_cache`=Passed；`evidence.extension-install.report.threshold_updates_geometry`=Passed；`evidence.extension-install.report.phase_switches`=Passed；`evidence.extension-install.report.field_cache_unchanged`=Passed；`evidence.extension-install.report.cold_open`=Not Run；`scope`=Current-batch automated technical qualification；`evidence.stdlib.report.tests`=127；`evidence.stdlib.report.failures`=0；`evidence.stdlib.report.errors`=0；`evidence.stdlib.report.skipped`=0；`evidence.public-science.report.tests`=67；`evidence.public-science.report.failures`=0；`evidence.public-science.report.errors`=0；`evidence.public-science.report.skipped`=0；`evidence.public-science.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.public-science.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.public-science.report.metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.stdlib.report.status`=Passed；`evidence.public-science.report.status`=Passed；`evidence.node-helpers.report.status`=Passed；`evidence.extension-install.report.status`=Passed；`evidence.extension-install.report.offline_install`=Passed；`evidence.extension-install.report.worker_import_evaluate`=Passed；`evidence.extension-install.report.cancel`=Passed；`evidence.extension-install.report.lifecycle`=Passed；`evidence.extension-install.report.repeated_field_cache`=Passed；`evidence.extension-install.report.threshold_updates_geometry`=Passed；`evidence.extension-install.report.phase_switches`=Passed；`evidence.extension-install.report.field_cache_unchanged`=Passed；`evidence.extension-install.report.cold_open`=Not Run；`scope`=Current-batch automated technical qualification；`evidence.stdlib.report.tests`=127；`evidence.stdlib.report.failures`=0；`evidence.stdlib.report.errors`=0；`evidence.stdlib.report.skipped`=0；`evidence.public-science.report.tests`=67；`evidence.public-science.report.failures`=0；`evidence.public-science.report.errors`=0；`evidence.public-science.report.skipped`=0；`evidence.public-science.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.public-science.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.public-science.report.metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6-full-science.json` | `status`=Passed；`tests`=123；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `status`=Passed；`checks.stdlib_127`=Passed；`checks.public_science_67_no_skip`=Passed；`checks.full_science_123_no_skip`=Passed；`checks.build_install_register_unregister`=Passed；`checks.original_and_moved_cold`=Passed；`checks.six_visual_fresh_and_cold_12`=Passed；`checks.related_GUI`=Passed；`checks.Standards`=Passed；`checks.Spec`=Passed；`gui.status`=Passed；`gui.checks.async_qualification`=Passed；`gui.checks.pre_job_dialog_cancel`=Passed；`gui.checks.MO9_generation`=Passed；`gui.checks.menu_undo`=Passed；`gui.checks.menu_redo`=Passed；`gui.checks.live_isovalue`=Passed；`gui.checks.render`=Passed；`scope`=Local Alpha technical qualification；`gui.parameters.spin`=alpha；`gui.parameters.source_MO`=9；`gui.parameters.spacing_angstrom`=0.2；`gui.parameters.margin_angstrom`=3；`gui.parameters.memory_budget_MiB`=512；`gui.parameters.isovalue_bohr^-3/2`=0.045；`historical_failures[0].source_commit`=78459e1；`historical_failures[0].reason`=RNA membership expected string; fixed a5de54b；`historical_failures[1].source_commit`=a5de54b；`historical_failures[1].reason`=Generate dialog had no _job; fixed 19e4cf0；`historical_failures[2].source_commit`=19e4cf0becf5a5173d692d1f4a9c621e6d01512e |
| `outputs/evidence/2026-10-05/alpha-readiness/core-regressions.json` | `status`=Passed；`tests`=43；`failures`=0；`errors`=0；`skipped`=0 |
| `outputs/evidence/2026-10-05/alpha-readiness/core-science-full.json` | `status`=Passed；`tests`=115；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-05/alpha-readiness/core-science-initial.json` | `status`=Failed；`tests`=88；`failures`=0；`errors`=15；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/undo-failures.json` | `[0].redo` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/handoff-cancel-history.json` | `[0].status` | Failed | [0].reason=RNA membership expected string; fixed a5de54b |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/undo-failures.json` | `[0].status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/undo-failures.json` | `[1].redo` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/handoff-cancel-history.json` | `[1].status` | Failed | [1].reason=Generate dialog had no _job; fixed 19e4cf0 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/undo-failures.json` | `[1].status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `historical_failures[0].status` | Failed | historical_failures[0].reason=RNA membership expected string; fixed a5de54b |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `historical_failures[1].status` | Failed | historical_failures[1].reason=Generate dialog had no _job; fixed 19e4cf0 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/post-cleanup-verification.json` | `physical_cleanup[3].normal_remove_status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-distribution-extraction-ac3.json` | `previous_internal_gui_preparation.status` | Failed | previous_internal_gui_preparation.reason=WinError 5; internal directory owner CodexSandboxOffline with owner-only access |
| `outputs/evidence/2026-10-05/alpha-readiness/core-science-initial.json` | `status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/local-delivery-final.json` | `worktree_cleanup[3].normal_remove_status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/undo-failures.json` | `[0].independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/undo-failures.json` | `[1].independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/extension-install.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `current_original_artifact.copy_and_destination_verification` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/qualification.json` | `evidence.extension-install.report.cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/qualification.json` | `evidence.reproduction.report.gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/qualification.json` | `evidence.reproduction.report.independent_alpha_installation` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.actual_GitHub_CI` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.component_license_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.draft_creation` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.full_v1_independent_human_and_science_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.independent_short_SOP_installation` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.maintainer_public_approval` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gates.post_release_download_hash` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/reproduction.json` | `gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/alpha-final-index.json` | `gui.independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/sop-flow/local-delivery.json` | `independent_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/sop-flow/sop-flow-verification.json` | `independent_acceptance` | Not Run | scope=Documentation links, source/evidence parameters and preservation |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/reproduction.json` | `independent_alpha_installation` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/release-manifest.json` | `independent_alpha_installation.status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/gui-alpha/ac6-gui-cold.json` | `independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/local-delivery-final.json` | `independent_human_and_science_acceptance` | Not Run | scope=Local merge and Git archive complete; physical residue recorded separately |
| `outputs/evidence/2026-10-05/alpha-readiness/av2/atoms-cold/atoms.json` | `independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/reports/qualification.json` | `independent_user_acceptance` | Not Run | scope=Current-batch automated technical qualification |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/release-manifest.json` | `license_review.status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[0].migration_status` | Not Run | necessary_paths[0].reason=All GUI screenshots, source identities, state snapshots and failure/Undo evidence. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[10].migration_status` | Not Run | necessary_paths[10].reason=Preserve all generated SUMMARY exports and metadata without filtering failure batches. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[11].migration_status` | Not Run | necessary_paths[11].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[12].migration_status` | Not Run | necessary_paths[12].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[13].migration_status` | Not Run | necessary_paths[13].reason=Preserve all generated SUMMARY exports and metadata without filtering failure batches. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[14].migration_status` | Not Run | necessary_paths[14].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[15].migration_status` | Not Run | necessary_paths[15].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[16].migration_status` | Not Run | necessary_paths[16].reason=Preserve all generated SUMMARY exports and metadata without filtering failure batches. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[17].migration_status` | Not Run | necessary_paths[17].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[18].migration_status` | Not Run | necessary_paths[18].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[19].migration_status` | Not Run | necessary_paths[19].reason=Preserve all generated SUMMARY exports and metadata without filtering failure batches. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[1].migration_status` | Not Run | necessary_paths[1].reason=Independent original and fixed Spec reproductions with exact scripts and source-bound JSON. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[20].migration_status` | Not Run | necessary_paths[20].reason=Preserve all task test reports/logs/validation scripts, including initial and failed checks. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[21].migration_status` | Not Run | necessary_paths[21].reason=Preserve all task test reports/logs/validation scripts, including initial and failed checks. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[22].migration_status` | Not Run | necessary_paths[22].reason=Preserve all task test reports/logs/validation scripts, including initial and failed checks. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[23].migration_status` | Not Run | necessary_paths[23].reason=Keep native installation/user-preference configuration bytes as run provenance, including userpref.blend. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[24].migration_status` | Not Run | necessary_paths[24].reason=Autosave/quit recovery files have unresolved scientific references; preserve together and retain required referenced worker data. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[25].migration_status` | Not Run | necessary_paths[25].reason=Keep native installation/user-preference configuration bytes as run provenance, including userpref.blend. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[26].migration_status` | Not Run | necessary_paths[26].reason=Autosave/quit recovery files have unresolved scientific references; preserve together and retain required referenced worker data. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[27].migration_status` | Not Run | necessary_paths[27].reason=Keep native installation/user-preference configuration bytes as run provenance, including userpref.blend. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[28].migration_status` | Not Run | necessary_paths[28].reason=Autosave/quit recovery files have unresolved scientific references; preserve together and retain required referenced worker data. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[29].migration_status` | Not Run | necessary_paths[29].reason=Keep native installation/user-preference configuration bytes as run provenance, including userpref.blend. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[2].migration_status` | Not Run | necessary_paths[2].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[30].migration_status` | Not Run | necessary_paths[30].reason=Autosave/quit recovery files have unresolved scientific references; preserve together and retain required referenced worker data. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[31].migration_status` | Not Run | necessary_paths[31].reason=Keep native installation/user-preference configuration bytes as run provenance, including userpref.blend. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[32].migration_status` | Not Run | necessary_paths[32].reason=Autosave/quit recovery files have unresolved scientific references; preserve together and retain required referenced worker data. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[33].migration_status` | Not Run | necessary_paths[33].reason=Keep native installation/user-preference configuration bytes as run provenance, including userpref.blend. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[34].migration_status` | Not Run | necessary_paths[34].reason=Autosave/quit recovery files have unresolved scientific references; preserve together and retain required referenced worker data. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[3].migration_status` | Not Run | necessary_paths[3].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[4].migration_status` | Not Run | necessary_paths[4].reason=Preserve all generated SUMMARY exports and metadata without filtering failure batches. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[5].migration_status` | Not Run | necessary_paths[5].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[6].migration_status` | Not Run | necessary_paths[6].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[7].migration_status` | Not Run | necessary_paths[7].reason=Preserve all generated SUMMARY exports and metadata without filtering failure batches. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[8].migration_status` | Not Run | necessary_paths[8].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `necessary_paths[9].migration_status` | Not Run | necessary_paths[9].reason=Preserve every success/failure technical report/log and generated-node qualification asset. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[0].migration_status` | Not Run | project_migrations[0].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[10].migration_status` | Not Run | project_migrations[10].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[11].migration_status` | Not Run | project_migrations[11].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[12].migration_status` | Not Run | project_migrations[12].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[13].migration_status` | Not Run | project_migrations[13].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[14].migration_status` | Not Run | project_migrations[14].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[15].migration_status` | Not Run | project_migrations[15].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[16].migration_status` | Not Run | project_migrations[16].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[17].migration_status` | Not Run | project_migrations[17].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[18].migration_status` | Not Run | project_migrations[18].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[19].migration_status` | Not Run | project_migrations[19].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[1].migration_status` | Not Run | project_migrations[1].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[20].migration_status` | Not Run | project_migrations[20].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[21].migration_status` | Not Run | project_migrations[21].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[22].migration_status` | Not Run | project_migrations[22].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[23].migration_status` | Not Run | project_migrations[23].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[24].migration_status` | Not Run | project_migrations[24].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[25].migration_status` | Not Run | project_migrations[25].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[26].migration_status` | Not Run | project_migrations[26].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[27].migration_status` | Not Run | project_migrations[27].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[28].migration_status` | Not Run | project_migrations[28].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[29].migration_status` | Not Run | project_migrations[29].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[2].migration_status` | Not Run | project_migrations[2].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[30].migration_status` | Not Run | project_migrations[30].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[31].migration_status` | Not Run | project_migrations[31].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[32].migration_status` | Not Run | project_migrations[32].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[33].migration_status` | Not Run | project_migrations[33].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[34].migration_status` | Not Run | project_migrations[34].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[35].migration_status` | Not Run | project_migrations[35].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[3].migration_status` | Not Run | project_migrations[3].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[4].migration_status` | Not Run | project_migrations[4].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[5].migration_status` | Not Run | project_migrations[5].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[6].migration_status` | Not Run | project_migrations[6].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[7].migration_status` | Not Run | project_migrations[7].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[8].migration_status` | Not Run | project_migrations[8].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `project_migrations[9].migration_status` | Not Run | project_migrations[9].reason=Necessary native/installation/public-reproduction or visual validation project; preserve .blend, .qcdata, backups, render/report siblings together. |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/release-manifest.json` | `public_release_approval.status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/completion.json` | `remote_steps` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/post-cleanup-verification.json` | `remote_steps` | Not Run | scope=Post-cleanup integrity; unreadable cache residue excluded |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/local-delivery-final.json` | `remote_steps.status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `validation.cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `validation.migration_and_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/alpha-readiness/closing/agent-preservation-plan.json` | `worktrees[0].inventory_status` | Partial | worktrees[0].name=alpha-core |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
