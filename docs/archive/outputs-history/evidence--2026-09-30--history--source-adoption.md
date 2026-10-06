# 2026-09-30 source-adoption

2026-09-27四批源码借鉴：AIM类型/坐标、ETS-NOCV已计算状态、正交相机、有效域剖面/CSV。最终 b2c227c，标签 qa/source-adoption-20260927-01至04；剖面是一次采样快照。

原目录：`outputs/evidence/2026-09-30/history/source-adoption/`。 2026-09-30是证据迁移日期，原执行日期依下列原报告身份；迁移不构成重新验证。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/source-adoption/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-09-30/history/source-adoption/02-nocv/qualification.json` | `source_commit` | `f55710a21ff8825912c1355208bb4fc9d01d216a` |
| `outputs/evidence/2026-09-30/history/source-adoption/03-camera/qualification.json` | `source_commit` | `8924b74a1177317028675d0b455fb4b9c7e55b29` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/history/source-adoption/qualification-tool-check/result.json` | `status`=Passed；`checks.valid-binding`=Passed；`checks.wrong-candidate`=Passed；`checks.stale-check`=Passed；`checks.changed-report`=Passed；`scope`=Qualification tool behavior only |
| `outputs/evidence/2026-09-30/history/source-adoption/02-nocv/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science.json.report.status`=Passed；`evidence.offline/extension.json.report.status`=Passed；`evidence.offline/extension.json.report.offline_install`=Passed；`evidence.offline/extension.json.report.worker_import_evaluate`=Passed；`evidence.offline/extension.json.report.cancel`=Passed；`evidence.offline/extension.json.report.lifecycle`=Passed；`evidence.offline/extension.json.report.repeated_field_cache`=Passed；`evidence.offline/extension.json.report.threshold_updates_geometry`=Passed；`evidence.offline/extension.json.report.phase_switches`=Passed；`evidence.offline/extension.json.report.field_cache_unchanged`=Passed；`evidence.offline/extension.json.report.cold_open`=Passed；`evidence.offline/extension.json.report.portable_archive`=Passed；`evidence.C12-C13/nocv.json.report.status`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=36；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/source-adoption/03-camera/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science.json.report.status`=Passed；`evidence.offline/extension.json.report.status`=Passed；`evidence.offline/extension.json.report.offline_install`=Passed；`evidence.offline/extension.json.report.worker_import_evaluate`=Passed；`evidence.offline/extension.json.report.cancel`=Passed；`evidence.offline/extension.json.report.lifecycle`=Passed；`evidence.offline/extension.json.report.repeated_field_cache`=Passed；`evidence.offline/extension.json.report.threshold_updates_geometry`=Passed；`evidence.offline/extension.json.report.phase_switches`=Passed；`evidence.offline/extension.json.report.field_cache_unchanged`=Passed；`evidence.offline/extension.json.report.cold_open`=Passed；`evidence.offline/extension.json.report.portable_archive`=Passed；`evidence.framing/camera.json.report.status`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.json.report.tests`=40；`evidence.science.json.report.failures`=0；`evidence.science.json.report.errors`=0；`evidence.science.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.json.report.metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/source-adoption/01-aim/science.json` | `status`=Passed；`tests`=30；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/source-adoption/02-nocv/science.json` | `status`=Passed；`tests`=36；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/source-adoption/03-camera/science.json` | `status`=Passed；`tests`=40；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/source-adoption/04-profile/science.json` | `status`=Passed；`tests`=45；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/source-adoption/04-profile/prior-r1/science.json` | `status`=Passed；`tests`=45；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/history/source-adoption/04-profile/final-sop/cases/C13/negative-pair-spin.json` | `negative_cases[0].result.status` | failed | negative_cases[0].result.error=ValueError: Selected pair and spin do not identify one ETS-NOCV table row |
| `outputs/evidence/2026-09-30/history/source-adoption/04-profile/final-sop/cases/C13/negative-pair-spin.json` | `negative_cases[1].result.status` | failed | negative_cases[1].result.error=ValueError: Selected pair and spin do not identify one ETS-NOCV table row |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
