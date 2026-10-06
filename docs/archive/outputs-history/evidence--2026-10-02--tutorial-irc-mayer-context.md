# 2026-10-02 tutorial-irc-mayer-context

2026-10-02 IRC/Mayer计算步上下文修复。真实三构型波函数及对应PySCF Mayer数据属于集中原件；工程和报告属于验证生成物。

原目录：`outputs/evidence/2026-10-02/tutorial-irc-mayer-context/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/build.json` | `source_commit` | `deb9416d8362dc42460e79b1a5b37bfcd8a1df63` |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/build.json` | `candidate.sha256` | `c736bb906599b868f8a11f964355b4139b2b09efd55e126f67792e6fac095ae2` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/build.json` | `status`=Passed |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-command.json` | `status`=Passed |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-extension.json` | `status`=Passed；`offline_install`=Passed；`worker_import_evaluate`=Passed；`cancel`=Passed；`lifecycle`=Passed；`repeated_field_cache`=Passed；`threshold_updates_geometry`=Passed；`phase_switches`=Passed；`field_cache_unchanged`=Passed；`cold_open`=Not Run；`portable_archive`=Passed |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-summary.json` | `status`=Passed；`derived_fixture_real_IRC`=Not Run；`real_P04_GUI`=Not Run；`independent_signature`=Not Run；`scope`=Installed extension and existing derived IRC fixture with fixed stale invoking root; real P04 GUI separate |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installed-IRC-cold-command.json` | `status`=Passed |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installed-IRC-command.json` | `status`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-extension.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-summary.json` | `derived_fixture_real_IRC` | Not Run | scope=Installed extension and existing derived IRC fixture with fixed stale invoking root; real P04 GUI separate |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-summary.json` | `independent_signature` | Not Run | scope=Installed extension and existing derived IRC fixture with fixed stale invoking root; real P04 GUI separate |
| `outputs/evidence/2026-10-02/tutorial-irc-mayer-context/installation-summary.json` | `real_P04_GUI` | Not Run | scope=Installed extension and existing derived IRC fixture with fixed stale invoking root; real P04 GUI separate |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
