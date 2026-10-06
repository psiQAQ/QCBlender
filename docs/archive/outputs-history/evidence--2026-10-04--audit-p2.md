# 2026-10-04 audit-p2

2026-10-04 Gaussian首段SCF失败后计算段边界、ETS-NOCV重复记录及基准。最终索引源码ad2a936f，候选名49872b0；91科学/17单测、18重复视觉/6冷读及4变异检测Passed；性能64³/128³/256³、1/8/32视图、1预热/5重复。独立签署Not Run。

原目录：`outputs/evidence/2026-10-04/audit-p2/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/projects/audit-p2/`、`outputs/runs/audit-p2/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `docs/acceptance/audit-p2-baselines-validation.json` | `date` | `2026-10-04` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `source_commit` | `ad2a936f2d99fa5af6b37ff720d5ccb3abd0845a` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `product_tree` | `f3742ab452dd96a357bb7e17c1dfa55934b8897d` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `candidate.path` | `outputs/candidates/current/audit-p2-49872b0/qcblender-0.0.1.zip` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `candidate.sha256` | `41cd978f36737236049fc901504c0196f4e6499adc891f1d2f09e2fabf4cebfd` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `candidate.bytes` | `50635805` |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `source_commit` | `57cae3874231f176fe9c375ac2437f7efc148961` |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.logs/baseline-unit-tests.json.report.source_commit` | `b59700ce288926586e4375f923838a83d79978ca` |
| `outputs/evidence/2026-10-04/audit-p2/logs/science.json` | `source_commit` | `49872b02401227cb17e0bf282f445419c8dfe2b6` |

## 结果与条件

版本控制中的汇总索引：

| 记录 | 检查 | 历史状态或参数 |
| --- | --- | --- |
| `docs/acceptance/audit-p2-baselines-validation.json` | `status` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.science.status` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.science.tests` | `91` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.science.skipped` | `0` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.baseline_unit_tests.status` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.baseline_unit_tests.tests` | `17` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.visual.status` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.performance.status` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.performance.warmups` | `1` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.performance.repeats` | `5` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.native_gui_and_saved_project` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `checks.independent_human_acceptance` | `Not Run` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `review.status` | `Passed` |
| `docs/acceptance/audit-p2-baselines-validation.json` | `review.independent_human_acceptance` | `Not Run` |

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science-complete.json.report.status`=Passed；`evidence.logs/baseline-unit-tests.json.report.status`=Passed；`evidence.install/extension-install.json.report.status`=Passed；`evidence.install/extension-install.json.report.offline_install`=Passed；`evidence.install/extension-install.json.report.worker_import_evaluate`=Passed；`evidence.install/extension-install.json.report.cancel`=Passed；`evidence.install/extension-install.json.report.lifecycle`=Passed；`evidence.install/extension-install.json.report.repeated_field_cache`=Passed；`evidence.install/extension-install.json.report.threshold_updates_geometry`=Passed；`evidence.install/extension-install.json.report.phase_switches`=Passed；`evidence.install/extension-install.json.report.field_cache_unchanged`=Passed；`evidence.install/extension-install.json.report.cold_open`=Not Run；`evidence.install/extension-install.json.report.portable_archive`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science-complete.json.report.tests`=91；`evidence.science-complete.json.report.failures`=0；`evidence.science-complete.json.report.errors`=0；`evidence.science-complete.json.report.skipped`=0；`evidence.science-complete.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science-complete.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science-complete.json.report.metrics.electron_count`=9.999999997365176；`evidence.logs/baseline-unit-tests.json.sha256`=492c1b1fedf2b3efd61e2b086150fdde922e3e3f3b4bed0c268911ef50c7d952；`evidence.logs/baseline-unit-tests.json.report.source_commit`=b59700ce288926586e4375f923838a83d79978ca |
| `outputs/evidence/2026-10-04/audit-p2/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science-complete.json.report.status`=Passed；`evidence.logs/baseline-unit-tests.json.report.status`=Passed；`evidence.install/extension-install.json.report.status`=Passed；`evidence.install/extension-install.json.report.offline_install`=Passed；`evidence.install/extension-install.json.report.worker_import_evaluate`=Passed；`evidence.install/extension-install.json.report.cancel`=Passed；`evidence.install/extension-install.json.report.lifecycle`=Passed；`evidence.install/extension-install.json.report.repeated_field_cache`=Passed；`evidence.install/extension-install.json.report.threshold_updates_geometry`=Passed；`evidence.install/extension-install.json.report.phase_switches`=Passed；`evidence.install/extension-install.json.report.field_cache_unchanged`=Passed；`evidence.install/extension-install.json.report.cold_open`=Not Run；`evidence.install/extension-install.json.report.portable_archive`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science-complete.json.report.tests`=91；`evidence.science-complete.json.report.failures`=0；`evidence.science-complete.json.report.errors`=0；`evidence.science-complete.json.report.skipped`=0；`evidence.science-complete.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science-complete.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science-complete.json.report.metrics.electron_count`=9.999999997365176；`evidence.logs/baseline-unit-tests.json.sha256`=492c1b1fedf2b3efd61e2b086150fdde922e3e3f3b4bed0c268911ef50c7d952；`evidence.logs/baseline-unit-tests.json.report.source_commit`=b59700ce288926586e4375f923838a83d79978ca |
| `outputs/evidence/2026-10-04/audit-p2/performance-display-v2/report.json` | `status`=Passed；`parameters.spin`=alpha |
| `outputs/evidence/2026-10-04/audit-p2/performance-display/report.json` | `status`=Failed；`parameters.spin`=alpha |
| `outputs/evidence/2026-10-04/audit-p2/performance-fields/report.json` | `status`=Passed |
| `outputs/evidence/2026-10-04/audit-p2/science.json` | `status`=Failed；`tests`=88；`failures`=0；`errors`=1；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-04/audit-p2/logs/science.json` | `status`=Failed |
| `outputs/evidence/2026-10-04/audit-p2/evidence-index.json` | `checks.logs/baseline-unit-tests.json.sha256`=492c1b1fedf2b3efd61e2b086150fdde922e3e3f3b4bed0c268911ef50c7d952 |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[20].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[20].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[20].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[20].expected` | Failed | checks[20].name=visual-controlled-hide-negative |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[20].observed` | Failed | checks[20].name=visual-controlled-hide-negative |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite.json` | `checks[24].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite.json` | `checks[24].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite.json` | `checks[24].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite.json` | `checks[24].expected` | Failed | checks[24].name=visual-controlled-hide-negative |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite.json` | `checks[24].observed` | Failed | checks[24].name=visual-controlled-hide-negative |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[25].comparison.regions.legend_title.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[25].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[25].expected` | Failed | checks[25].name=visual-controlled-v2-legend-unit |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[25].observed` | Failed | checks[25].name=visual-controlled-v2-legend-unit |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].comparison.regions.legend.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].comparison.regions.legend_title.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].expected` | Failed | checks[26].name=visual-controlled-v2-legend-position |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[26].observed` | Failed | checks[26].name=visual-controlled-v2-legend-position |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[27].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[27].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[27].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[27].expected` | Failed | checks[27].name=visual-controlled-v2-disable-valid-mask |
| `outputs/evidence/2026-10-04/audit-p2/visual-suite-v2.json` | `checks[27].observed` | Failed | checks[27].name=visual-controlled-v2-disable-valid-mask |
| `outputs/evidence/2026-10-04/audit-p2/visual-checks/visual-controlled-hide-negative/signed-mo.json` | `comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-checks/visual-controlled-v2-legend-position/legend-annotations.json` | `comparison.regions.legend.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-checks/visual-controlled-v2-legend-position/legend-annotations.json` | `comparison.regions.legend_title.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-checks/visual-controlled-hide-negative/signed-mo.json` | `comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/visual-checks/visual-controlled-hide-negative/signed-mo.json` | `comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[20].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[20].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[20].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[20].expected` | Failed | evidence.visual-suite-v2.json.report.checks[20].name=visual-controlled-hide-negative |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[20].observed` | Failed | evidence.visual-suite-v2.json.report.checks[20].name=visual-controlled-hide-negative |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[25].comparison.regions.legend_title.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[25].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[25].expected` | Failed | evidence.visual-suite-v2.json.report.checks[25].name=visual-controlled-v2-legend-unit |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[25].observed` | Failed | evidence.visual-suite-v2.json.report.checks[25].name=visual-controlled-v2-legend-unit |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].comparison.regions.legend.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].comparison.regions.legend_title.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].expected` | Failed | evidence.visual-suite-v2.json.report.checks[26].name=visual-controlled-v2-legend-position |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[26].observed` | Failed | evidence.visual-suite-v2.json.report.checks[26].name=visual-controlled-v2-legend-position |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[27].comparison.regions.full.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[27].comparison.regions.molecule.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[27].comparison.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[27].expected` | Failed | evidence.visual-suite-v2.json.report.checks[27].name=visual-controlled-v2-disable-valid-mask |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.checks[27].observed` | Failed | evidence.visual-suite-v2.json.report.checks[27].name=visual-controlled-v2-disable-valid-mask |
| `outputs/evidence/2026-10-04/audit-p2/logs/performance-display.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-10-04/audit-p2/performance-display/report.json` | `status` | Failed | error=ValueError: Expected nonempty rendered meshes: [[0, 0], [874, 1632]] |
| `outputs/evidence/2026-10-04/audit-p2/science.json` | `status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/install/extension-install.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.delivery-cold/atoms/atoms.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.delivery-cold/density-esp/density-esp.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.delivery-cold/fog/fog.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.delivery-cold/legend-annotations/legend-annotations.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.delivery-cold/signed-mo/signed-mo.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.delivery-cold/slice-contours/slice-contours.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.gui/checks.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.gui/cold-reopen.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.install/extension-install.json.report.cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.installed-p2/checks.json.report.independent_human_review` | Not Run | evidence.installed-p2/checks.json.report.gaussian.preview.jobs[0].energy_selection.reason=Job is failed or incomplete; partial records remain inspectable; evidence.installed-p2/checks.json.report.gaussian.preview.jobs[1].energy_selection.reason=Unique method-specific result in a normally terminated job |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.installed-p2/cold-reopen.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.review.json.report.independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.visual-suite-v2.json.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/review.json` | `independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/delivery-cold/atoms/atoms.json` | `independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.installed-p2/checks.json.report.gaussian.failed_first_job.status` | failed | evidence.installed-p2/checks.json.report.gaussian.failed_first_job.error=ValueError: Selected job has no explicit geometry; automatic inheritance is unavailable |
| `outputs/evidence/2026-10-04/audit-p2/qualification-main.json` | `evidence.installed-p2/checks.json.report.gaussian.preview.jobs[0].status` | failed | evidence.installed-p2/checks.json.report.gaussian.preview.jobs[0].energy_selection.reason=Job is failed or incomplete; partial records remain inspectable |
| `outputs/evidence/2026-10-04/audit-p2/installed-p2/checks.json` | `gaussian.failed_first_job.status` | failed | gaussian.failed_first_job.error=ValueError: Selected job has no explicit geometry; automatic inheritance is unavailable |
| `outputs/evidence/2026-10-04/audit-p2/installed-p2/checks.json` | `gaussian.preview.jobs[0].status` | failed | gaussian.preview.jobs[0].energy_selection.reason=Job is failed or incomplete; partial records remain inspectable |
| `outputs/evidence/2026-10-04/audit-p2/gui/gaussian-normal-readback.json` | `jobs[0].status` | failed | jobs[0].energy_selection.reason=Job is failed or incomplete; partial records remain inspectable |
| `outputs/evidence/2026-10-04/audit-p2/closing/worktree-files/gaussian-segments/outputs/green.json` | `original_repro.failed-then-normal.log[0].status` | failed | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
