# 2026-10-03 plugin-audit

2026-10-03固定96f9c7e的完成度与参考实现调研：82科学、30相关单测通过，1项POSIX在Windows跳过。四类缺陷未在本批修复，其中两类P1通过原生operator和Computer Use复现；gui/linked-observed工程有意保存缺陷状态。权限清理Partial；产品修复、独立人工/科研签署及发布Not Run。

原目录：`outputs/evidence/2026-10-03/plugin-audit/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/projects/plugin-audit/`、`outputs/runs/plugin-audit/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-10-03/plugin-audit/final-verification.json` | `source_commit` | `96f9c7ea0c41c63f8b689a766ffafeb14aa3bb48` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-03/plugin-audit/final-verification.json` | `status`=Passed；`cleanup_status`=Partial；`independent_human_acceptance`=Not Run；`scope`=Five uncommitted research documents; product, tests, dependencies and main unchanged |
| `outputs/evidence/2026-10-03/plugin-audit/science.json` | `status`=Passed；`tests`=82；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-03/plugin-audit/logs/science.json` | `status`=Passed |
| `outputs/evidence/2026-10-03/plugin-audit/cleanup-receipt.json` | `status`=Partial |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `product_tree.status`=Passed；`core_file_verification[0].status`=Passed；`core_file_verification[1].status`=Passed；`core_file_verification[1].recorded_report_status`=Passed；`core_file_verification[2].status`=Passed；`core_file_verification[3].status`=Passed；`core_file_verification[3].recorded_report_status`=Passed；`core_file_verification[4].status`=Passed；`core_file_verification[4].recorded_report_status`=Passed；`core_file_verification[5].status`=Passed；`core_file_verification[5].recorded_report_status`=Passed；`core_file_verification[6].status`=Passed；`core_file_verification[6].recorded_report_status`=Passed；`core_file_verification[7].status`=Passed；`core_file_verification[7].recorded_report_status`=Passed；`core_file_verification[8].status`=Passed；`core_file_verification[8].recorded_report_status`=Passed；`core_file_verification[9].status`=Passed；`recorded_science_report.tests`=82；`recorded_science_report.failures`=0；`recorded_science_report.errors`=0；`recorded_science_report.skipped`=0；`recorded_science_report.metrics.density_max_abs_error`=8.440006539212064e-07；`recorded_science_report.metrics.esp_max_abs_error`=4.60872461194306e-06；`recorded_science_report.metrics.electron_count`=9.999999997365176；`recorded_scientific_scope.tests`=82；`recorded_scientific_scope.failures`=0；`recorded_scientific_scope.errors`=0；`recorded_scientific_scope.skipped`=0 |
| `outputs/evidence/2026-10-03/plugin-audit/gui-fixture-copy.json` | `status`=Passed |
| `outputs/evidence/2026-10-03/plugin-audit/retained-gui.json` | `status`=Passed；`scope`=Retained-path binding, arrays and volumes cold read; GUI defect state also preserved |
| `outputs/evidence/2026-10-03/plugin-audit/retained-integration.json` | `status`=Passed；`scope`=Retained-path binding, arrays and volumes cold read; GUI defect state also preserved |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-03/plugin-audit/gui/verification.json` | `association.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `cases[2].product_behavior_status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `cases[4].product_behavior_status` | Failed | cases[4].observation.jobs[0].energy_selection.reason=Job is failed or incomplete; partial records remain inspectable |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `cases[7].product_behavior_status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json` | `checks.dynamic_association_irc.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json` | `checks.dynamic_association_optimization.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json` | `checks.shared_mesh_irc.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json` | `checks.shared_mesh_optimization.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/gui/verification.json` | `product_behavior_status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/gui/verification.json` | `shared_mesh.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/logs/xyz.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-10-03/plugin-audit/xyz-report.json` | `status` | Failed | error=StopIteration() |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `xyz_fixture_followup.current_failure.recorded_status` | Failed | xyz_fixture_followup.current_failure.error=StopIteration() |
| `outputs/evidence/2026-10-03/plugin-audit/install/extension.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.Blender_GUI_execution` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.Blender_MCP_execution` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.cold_reopen_execution` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.independent_scientific_signature` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.independent_user_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.remote_release_query` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json` | `current_audit_checks.scientific_test_execution` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json` | `gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/xyz-report.json` | `gui` | Not Run | error=StopIteration() |
| `outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json` | `independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/final-verification.json` | `independent_human_acceptance` | Not Run | scope=Five uncommitted research documents; product, tests, dependencies and main unchanged |
| `outputs/evidence/2026-10-03/plugin-audit/xyz-report.json` | `independent_human_acceptance` | Not Run | error=StopIteration() |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `public_entrypoints.AUDIT-01.blender_execution` | Not Run | public_entrypoints.AUDIT-01.reason=Poll accepts two atom views and has no IRC/optimization-step restriction; execute loads their base Datasets. |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `public_entrypoints.AUDIT-02.blender_execution` | Not Run | public_entrypoints.AUDIT-02.reason=Log GUI preview calls inspect_log as reproduced here; direct import also uses split_jobs. |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `public_entrypoints.AUDIT-03.blender_execution` | Not Run | public_entrypoints.AUDIT-03.reason=A bound static QC view enables nocv_table; import_ets calls ets_nocv_pairs with no additional duplicate check. |
| `outputs/evidence/2026-10-03/plugin-audit/final-verification.json` | `cleanup_status` | Partial | scope=Five uncommitted research documents; product, tests, dependencies and main unchanged |
| `outputs/evidence/2026-10-03/plugin-audit/cleanup-receipt.json` | `status` | Partial | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `cases[4].observation.jobs[0].energies[0].calculation_status` | failed | 原字段未附原因 |
| `outputs/evidence/2026-10-03/plugin-audit/logic/results.json` | `cases[4].observation.jobs[0].status` | failed | cases[4].observation.jobs[0].energy_selection.reason=Job is failed or incomplete; partial records remain inspectable |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
