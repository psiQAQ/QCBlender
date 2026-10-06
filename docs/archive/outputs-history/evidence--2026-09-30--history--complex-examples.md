# 2026-09-30 complex-examples

外部真实波函数、Gaussian日志与场文件的来源检查。必要原件沿用集中输入；下载许可、构型、单位和场物理量声明属于保留条件。

原目录：`outputs/evidence/2026-09-30/history/complex-examples/`。 2026-09-30是证据迁移日期，原执行日期依下列原报告身份；迁移不构成重新验证。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/complex-examples/`。

历史候选、源码提交或执行日期没有在本次可读机器摘要中取得完整绑定，保持未核定；不为目录补造身份。已知开发沿革另见 [CHANGELOG](../../CHANGELOG.md)。

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/history/complex-examples/summary.json` | `status`=Passed；`cases.orbitals.checks.density_spin_identities`=Passed；`cases.orbitals.checks.occupations`=Passed；`cases.orbitals.checks.clip_phase_thresholds_cursor`=Passed；`cases.orbitals.checks.layer_duplicate_order_remove_independence`=Passed；`cases.orbitals.cold_open`=Passed；`cases.vibration.checks.54_modes_IR_source`=Passed；`cases.vibration.checks.48_frame_animation`=Passed；`cases.vibration.cold_open`=Passed；`cases.polar.checks.charge_slice_atom_mapping`=Passed；`cases.polar.cold_open`=Passed；`cases.interaction.checks.external_cube_values_coordinates_and_mapping`=Passed；`cases.interaction.cold_open`=Passed；`science_regression.status`=Passed；`human_acceptance`=Not Run；`science_regression.tests`=20；`science_regression.failures`=0；`science_regression.errors`=0；`science_regression.metrics.density_max_abs_error`=8.440006539212064e-07；`science_regression.metrics.esp_max_abs_error`=4.60872461194306e-06；`science_regression.metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/complex-examples/interaction/report.json` | `status`=Passed；`checks.external_cube_values_coordinates_and_mapping`=Passed；`human_acceptance`=Not Run；`layers[0].vertices`=54；`layers[1].vertices`=7504；`layers[2].vertices`=1020 |
| `outputs/evidence/2026-09-30/history/complex-examples/orbitals/report.json` | `status`=Passed；`checks.density_spin_identities`=Passed；`checks.occupations`=Passed；`checks.clip_phase_thresholds_cursor`=Passed；`checks.layer_duplicate_order_remove_independence`=Passed；`human_acceptance`=Not Run；`jobs[1].parameters.parameters.spin`=alpha；`jobs[2].parameters.parameters.spin`=beta；`layers[0].vertices`=3560；`layers[1].vertices`=3560；`layers[2].vertices`=2958；`layers[3].vertices`=2884；`layers[4].vertices`=3282；`layers[5].vertices`=2234；`layers[6].vertices`=1734；`layers[7].vertices`=2476 |
| `outputs/evidence/2026-09-30/history/complex-examples/polar/report.json` | `status`=Passed；`checks.charge_slice_atom_mapping`=Passed；`human_acceptance`=Not Run；`layers[1].vertices`=3846；`layers[2].vertices`=6841；`layers[3].vertices`=6561；`layers[4].vertices`=4374；`layers[5].vertices`=4814；`layers[6].vertices`=4814 |
| `outputs/evidence/2026-09-30/history/complex-examples/vibration/report.json` | `status`=Passed；`checks.54_modes_IR_source`=Passed；`checks.48_frame_animation`=Passed；`human_acceptance`=Not Run；`mode`=45；`playback_hz`=1；`layers[1].vertices`=4300 |
| `outputs/evidence/2026-09-30/history/complex-examples/source-inspection.json` | `external_preparation.status`=Passed；`external_preparation.derivative_finite_difference_check`=Passed；`external_preparation.cube_roundtrip`=Passed；`external_preparation.nciplot_reference.status`=Passed；`external_preparation.spacing_angstrom`=0.12 |
| `outputs/evidence/2026-09-30/history/complex-examples/interaction/reopen.json` | `status`=Passed；`relocated_cold_open`=Passed；`geometry_counts`=Passed；`scientific_and_cache_files_unchanged`=Passed；`human_acceptance`=Not Run |
| `outputs/evidence/2026-09-30/history/complex-examples/orbitals/reopen.json` | `status`=Passed；`relocated_cold_open`=Passed；`geometry_counts`=Passed；`scientific_and_cache_files_unchanged`=Passed；`human_acceptance`=Not Run |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/history/complex-examples/interaction/reopen.json` | `human_acceptance` | Not Run | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
