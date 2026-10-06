# 历史批次 environment-history

2026-09-22起的研究、构建和安装环境。GBasis固定源码071969c的纯Python发行路径与可选libcint实验分开：native CBasis.overlap()在Windows触发0xc0000374堆损坏，native独立对照Failed，h及以上产品资格未放开；当前纯Python发行无需C/C++编译器。完整许可证、必要源码归档和第三方资料仍保留一份，环境退役集合由逐文件用途与当前引用核对决定。

本页汇总下列旧研究、构建、安装和临时数据目录。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/m0-research/`、`outputs/build-python/`、`outputs/build-sources/`、`outputs/gbasis-build/`、`outputs/reference-tools/`、`outputs/native-backend-licenses/`、`outputs/repaired-wheels/`、`outputs/unrepaired-wheels/`、`outputs/science-aim-association/`、`outputs/science-field-ranges/`、`outputs/science-multiwfn-metadata/`、`outputs/science-profile/`、`outputs/science-result-filters/`、`outputs/policy-tests/`、`outputs/release-verifier-tests/`、`outputs/tests/`、`outputs/blender-dev/`、`outputs/dist/`、`outputs/paired-fields/`、`outputs/runs/retire/`、`outputs/process-temp/`。

历史候选、源码提交或执行日期没有在本次可读机器摘要中取得完整绑定，保持未核定；不为目录补造身份。已知开发沿革另见 [CHANGELOG](../../CHANGELOG.md)。

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/history/root/qualification.json` | `status`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.science-reference.json.report.status`=Passed；`evidence.scientific-convergence.json.report.status`=Passed；`evidence.field-performance.json.report.status`=Passed；`evidence.acceptance/extension.json.report.status`=Passed；`evidence.acceptance/extension.json.report.offline_install`=Passed；`evidence.acceptance/extension.json.report.worker_import_evaluate`=Passed；`evidence.acceptance/extension.json.report.cancel`=Passed；`evidence.acceptance/extension.json.report.lifecycle`=Passed；`evidence.acceptance/extension.json.report.repeated_field_cache`=Passed；`evidence.acceptance/extension.json.report.threshold_updates_geometry`=Passed；`evidence.acceptance/extension.json.report.phase_switches`=Passed；`evidence.acceptance/extension.json.report.field_cache_unchanged`=Passed；`evidence.acceptance/extension.json.report.cold_open`=Passed；`evidence.acceptance/extension.json.report.portable_archive`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science-reference.json.report.tests`=20；`evidence.science-reference.json.report.failures`=0；`evidence.science-reference.json.report.errors`=0；`evidence.science-reference.json.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science-reference.json.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science-reference.json.report.metrics.electron_count`=9.999999997365176；`evidence.acceptance/storage-paths.json.report.tests`=2；`evidence.acceptance/storage-paths.json.report.scope`=Real filesystem: long cache array paths, copy/reuse/archive and corruption rejection；`evidence.acceptance/water-mode-cold-view.json.sha256`=12f2bf2b367b760e5a7c2b21367fa4916e8e4ef5085cfe2700c0541fa7e80eeb；`evidence.animation-acceptance-v2/result.json.report.mode`=2；`evidence.animation-acceptance-v2/result.json.report.frequency_cm-1`=4141.3837 |
| `outputs/evidence/2026-09-30/history/root/blender-bootstrap.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/root/design-validation.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/root/extension-runtime.json` | `modules[0].status`=Passed；`modules[1].status`=Passed；`modules[2].status`=Passed；`modules[3].status`=Passed；`modules[4].status`=Passed；`modules[5].status`=Passed；`modules[6].status`=Passed |
| `outputs/evidence/2026-09-30/history/root/field-performance.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/root/qualify-high-l-both-python.json` | `cases[0].native_phase`=Not Run；`cases[1].native_phase`=Not Run；`scope`=basis-level only; product h-shell rejection remains unchanged |
| `outputs/evidence/2026-09-30/history/root/qualify-high-l-native-failure.json` | `status`=Failed；`scope`=basis-level native cross-validation, not product end-to-end；`failure_operation`=CBasis.overlap()；`windows_exception_hex`=0xc0000374；`windows_exception_name`=STATUS_HEAP_CORRUPTION；`root_cause`=Not established; source inspected, no native source modification or rebuild performed |
| `outputs/evidence/2026-09-30/history/root/qualify-high-l.json` | `scope`=basis-level only; product h-shell rejection remains unchanged |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/history/root/qualify-high-l-native-failure.json` | `status` | Failed | scope=basis-level native cross-validation, not product end-to-end |
| `outputs/evidence/2026-09-30/history/root/qualify-high-l-both-python.json` | `cases[0].native_phase` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/history/root/qualify-high-l-both-python.json` | `cases[1].native_phase` | Not Run | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
