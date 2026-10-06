# 2026-09-30 result-browser

2026-09-27计算段与来源浏览。21项科学回归及GUI/冷读通过；归档 archive/2026-09-28/feat/result-browser；不自动跨段继承几何。

原目录：`outputs/evidence/2026-09-30/history/result-browser/`。 2026-09-30是证据迁移日期，原执行日期依下列原报告身份；迁移不构成重新验证。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/result-browser/`。

历史候选、源码提交或执行日期没有在本次可读机器摘要中取得完整绑定，保持未核定；不为目录补造身份。已知开发沿革另见 [CHANGELOG](../../CHANGELOG.md)。

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/history/result-browser/final-receipt.json` | `status`=Passed；`originals_unchanged`=Passed；`git_integrity`=Passed；`exclusive_commits_unresolvable`=Passed；`worktree_removed`=Passed |
| `outputs/evidence/2026-09-30/history/result-browser/gui-checks.json` | `cancel_preview`=Passed；`gui_second_job`=Passed；`energy_matches_direct`=Passed；`geometry_matches_direct`=Passed |
| `outputs/evidence/2026-09-30/history/result-browser/gui-cold-reopen.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/result-browser/lifecycle.json` | `undo`=Passed；`redo`=Passed；`array_hashes_unchanged`=Passed；`visibility`=Passed；`sorting`=Passed；`status`=Passed |
| `outputs/evidence/2026-09-30/history/result-browser/science-reference.json` | `status`=Passed；`tests`=21；`failures`=0；`errors`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/history/result-browser/maintenance/retirement.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/history/result-browser/offline-final-role/extension.json` | `status`=Passed；`offline_install`=Passed；`worker_import_evaluate`=Passed；`cancel`=Passed；`lifecycle`=Passed；`repeated_field_cache`=Passed；`threshold_updates_geometry`=Passed；`phase_switches`=Passed；`field_cache_unchanged`=Passed；`cold_open`=Passed；`portable_archive`=Passed |
| `outputs/evidence/2026-09-30/history/result-browser/offline-final/extension.json` | `status`=Passed；`offline_install`=Passed；`worker_import_evaluate`=Passed；`cancel`=Passed；`lifecycle`=Passed；`repeated_field_cache`=Passed；`threshold_updates_geometry`=Passed；`phase_switches`=Passed；`field_cache_unchanged`=Passed；`cold_open`=Passed；`portable_archive`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/history/result-browser/offline/extension.json` | `cold_open` | Not Run | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
