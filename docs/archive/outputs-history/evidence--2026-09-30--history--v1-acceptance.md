# 2026-09-30 v1-acceptance

早期C01–C13/N01–N18技术SOP及案例资格。必要真实科学输入与来源条件集中保留；Agent技术检查与独立用户/科研签署分开。

原目录：`outputs/evidence/2026-09-30/history/v1-acceptance/`。 2026-09-30是证据迁移日期，原执行日期依下列原报告身份；迁移不构成重新验证。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/v1-acceptance/`。

历史候选、源码提交或执行日期没有在本次可读机器摘要中取得完整绑定，保持未核定；不为目录补造身份。已知开发沿革另见 [CHANGELOG](../../CHANGELOG.md)。

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/artifact-check.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/candidate-check.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/evidence-index.json` | `status`=Passed；`cases[0].status`=Passed；`cases[0].checks.import`=Passed；`cases[0].checks.source_units`=Passed；`cases[0].checks.nodes`=Passed；`cases[0].checks.PNG`=Passed；`cases[0].checks.reopen`=Passed；`cases[0].checks.moved`=Passed；`cases[0].GUI.status`=Passed；`cases[1].status`=Passed；`cases[1].checks.import`=Passed；`cases[1].checks.source_units`=Passed；`cases[1].checks.nodes`=Passed；`cases[1].checks.PNG`=Passed；`cases[1].checks.reopen`=Passed；`cases[1].checks.moved`=Passed；`cases[1].GUI.status`=Passed；`cases[2].status`=Passed；`scope`=Agent technical replay; independent human acceptance not signed；`cases[0].GUI.scope`=Previously confirmed GUI entry; final candidate repeated via MCP as requested；`cases[1].GUI.scope`=Previously confirmed GUI entry; final candidate repeated via MCP as requested；`cases[2].GUI.scope`=Previously confirmed GUI entry; final candidate repeated via MCP as requested |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/failed-save.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/runtime.json` | `modules[0].status`=Passed；`modules[1].status`=Passed；`modules[2].status`=Passed；`modules[3].status`=Passed；`modules[4].status`=Passed；`modules[5].status`=Passed；`modules[6].status`=Passed |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/science-reference-baseline.json` | `status`=Passed；`tests`=20；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/science-reference-final.json` | `status`=Passed；`tests`=20；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/science-reference.json` | `status`=Passed；`tests`=20；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/defects/ESP01/failure.json` | `status` | Failed | error=ESP extrema serial numbers are repeated |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/defects/PORT-01.json` | `status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-09-30/history/v1-acceptance/cases/C11/gui-duplicate-rejected.json` | `GUI_positive_import` | Not Run | operation=Repeat Mayer import on already populated IRC |
| `outputs/evidence/2026-09-30/history/v1-acceptance/replay/defects/N16-initial-observation.json` | `status` | Not Run | reason=Initial undo trial had MCP-created camera and display changes outside an explicit undo checkpoint; redo did not restore expected layer count. Retesting from saved project with explicit checkpoint. |
| `outputs/evidence/2026-09-30/history/v1-acceptance/cases/C07/negative-grid-check.json` | `expected_rejection.status` | failed | expected_rejection.error=ValueError: Geometry and color Cube grids differ; no resampling is inferred |
| `outputs/evidence/2026-09-30/history/v1-acceptance/cases/C13/negative-pair-spin.json` | `negative_cases[0].result.status` | failed | negative_cases[0].result.error=ValueError: Selected pair and spin do not identify one ETS-NOCV table row |
| `outputs/evidence/2026-09-30/history/v1-acceptance/cases/C13/negative-pair-spin.json` | `negative_cases[1].result.status` | failed | negative_cases[1].result.error=ValueError: Selected pair and spin do not identify one ETS-NOCV table row |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
