# 2026-10-02 tutorial-aim-records

2026-10-02 AIM属性类型和来源记录修复/补验。早期安装和断言失败按原报告保留，最终v3安装及AIM报告分别记录。

原目录：`outputs/evidence/2026-10-02/tutorial-aim-records/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-10-02/tutorial-aim-records/build.json` | `source_commit` | `13401c6a42dabd3844d7f1896ebdd6106188f774` |
| `outputs/evidence/2026-10-02/tutorial-aim-records/build.json` | `candidate.sha256` | `cc4e7ac23d22a0c6c5f919c72b15615d8e440fe630838e64853512cfaa356ffd` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-02/tutorial-aim-records/build-input-diagnostic.json` | `status`=Failed；`scope`=Build input lookup before Blender launch |
| `outputs/evidence/2026-10-02/tutorial-aim-records/build.json` | `status`=Passed |
| `outputs/evidence/2026-10-02/tutorial-aim-records/input-map-v2.json` | `status`=Passed |
| `outputs/evidence/2026-10-02/tutorial-aim-records/input-map.json` | `status`=Passed |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-command.json` | `status`=Failed |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-summary.json` | `status`=Passed；`installed_AIM.status`=Passed；`installed_AIM.valid_association`=Passed；`installed_AIM.errors_preserve_scene`=Passed；`installed_AIM.missing_diagnostics`=Passed；`installed_AIM.point_path_visibility_render`=Passed；`installed_AIM.panel_labels_before_and_after_refresh`=Passed；`installed_AIM.saved_cold_reopen`=Not Run；`installed_AIM.moved_cold_reopen`=Not Run；`visible_GUI`=Not Run；`independent_signature`=Not Run |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-v2-command.json` | `status`=Failed |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-v3-command.json` | `status`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-02/tutorial-aim-records/build-input-diagnostic.json` | `status` | Failed | scope=Build input lookup before Blender launch |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-command.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-v3-extension.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-summary.json` | `independent_signature` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-02/tutorial-aim-records/science-tests.json` | `independent_signature` | Not Run | scope=Targeted scientific regression; installed panel and GUI checks separate |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-summary.json` | `installed_AIM.moved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-summary.json` | `installed_AIM.saved_cold_reopen` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-02/tutorial-aim-records/previous-process-exit.json` | `preserved.exit` | Not Run | preserved.scope=Preserve failing GUI-import project before normal exit; product panel defect remains Failed |
| `outputs/evidence/2026-10-02/tutorial-aim-records/installation-summary.json` | `visible_GUI` | Not Run | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
