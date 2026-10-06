# 2026-10-04 audit-p1

2026-10-04固定a4baaaf2修复动态构型关联和共享mesh边界：97科学、六视觉与迁移冷读、真实GUI/Undo/Redo及双冷读Passed；独立人工签署Not Run。

原目录：`outputs/evidence/2026-10-04/audit-p1/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/projects/audit-p1/`、`outputs/runs/audit-p1/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `docs/acceptance/audit-p1-validation.json` | `date` | `2026-10-04` |
| `docs/acceptance/audit-p1-validation.json` | `source_commit` | `a4baaaf2cf163d93d8d7e25f3c9bd5e96ae01c3d` |
| `docs/acceptance/audit-p1-validation.json` | `product_tree` | `c1a5bc48b035434c4a3245909e1e629bec4f0665` |
| `docs/acceptance/audit-p1-validation.json` | `candidate.path` | `outputs/candidates/current/audit-p1-a4baaaf/qcblender-0.0.1.zip` |
| `docs/acceptance/audit-p1-validation.json` | `candidate.sha256` | `039306fdcbf908bc020b29246f54dc2f8e2459e9413844b1a80a45ec5b036fb9` |
| `docs/acceptance/audit-p1-validation.json` | `candidate.bytes` | `50638451` |

## 结果与条件

版本控制中的汇总索引：

| 记录 | 检查 | 历史状态或参数 |
| --- | --- | --- |
| `docs/acceptance/audit-p1-validation.json` | `status` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.science.status` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.science.tests` | `97` |
| `docs/acceptance/audit-p1-validation.json` | `checks.science.skipped` | `0` |
| `docs/acceptance/audit-p1-validation.json` | `checks.native_association` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.shared_mesh` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.visual.status` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.gui_and_undo_redo` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.native_original_and_chinese_moved_cold` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `checks.independent_human_acceptance` | `Not Run` |
| `docs/acceptance/audit-p1-validation.json` | `review.status` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `review.standards.re_review` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `review.spec.re_review` | `Passed` |
| `docs/acceptance/audit-p1-validation.json` | `review.independent_human_acceptance` | `Not Run` |

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-04/audit-p1/closing/final-verification.json` | `status`=Passed；`operation_reports_and_screenshots`=Passed |
| `outputs/evidence/2026-10-04/audit-p1/science.json` | `status`=Passed；`tests`=97；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-04/audit-p1/final/science.json` | `status`=Passed；`tests`=97；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-04/audit-p1/baseline-source.json` | `scope`=P1 original native operators plus explicit fail-on-defect assertion; historical script preserved |
| `outputs/evidence/2026-10-04/audit-p1/complete-source-match.json` | `status`=Passed；`root_metadata`=Passed；`installed_archive_bytes`=Passed |
| `outputs/evidence/2026-10-04/audit-p1/preservation-map.json` | `status`=Passed |
| `outputs/evidence/2026-10-04/audit-p1/review.json` | `status`=Passed；`standards.re_review`=Passed；`spec.re_review`=Passed；`independent_human_acceptance`=Not Run |
| `outputs/evidence/2026-10-04/audit-p1/association-damaged-red/checks.json` | `status`=Failed；`independent_human_review`=Not Run；`checks.binding_rejections.atom_identity`=Passed；`checks.binding_rejections.manifest`=Passed；`checks.binding_rejections.selected_job`=Passed；`checks.irc.both_roles`=Passed；`checks.irc.same_source_other_view`=Passed；`checks.irc.rename`=Passed；`checks.irc.copy_layer_helper`=Passed；`checks.optimization.both_roles`=Passed；`checks.optimization.same_source_other_view`=Passed；`checks.optimization.rename`=Passed；`checks.optimization.copy_layer_helper`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-04/audit-p1/association-v1/saved-state-diagnostic.json` | `Binding rejection fixture.status` | Failed | Binding rejection fixture.error=Atom identities or ordering changed: qc_atom_id |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `checks.dynamic_association_irc.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `checks.dynamic_association_optimization.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `checks.shared_mesh_irc.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `checks.shared_mesh_optimization.status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `execution_status` | Failed | error=AssertionError('P1 defects reproduced: dynamic_association_irc, dynamic_association_optimization, shared_mesh_irc, shared_mesh_optimization') |
| `outputs/evidence/2026-10-04/audit-p1/association-damaged-red/checks.json` | `status` | Failed | error=AssertionError: Expected rejection, got {'FINISHED'} |
| `outputs/evidence/2026-10-04/audit-p1/association-v1/checks.json` | `status` | Failed | error=ValueError: Atom identities or ordering changed: qc_atom_id |
| `outputs/evidence/2026-10-04/audit-p1/logs/association-damaged-red.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-10-04/audit-p1/shared-red/checks.json` | `status` | Failed | error=AssertionError("Operation unexpectedly succeeded: {'FINISHED'}") |
| `outputs/evidence/2026-10-04/audit-p1/install-baseline/extension.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `gui` | Not Run | error=AssertionError('P1 defects reproduced: dynamic_association_irc, dynamic_association_optimization, shared_mesh_irc, shared_mesh_optimization') |
| `outputs/evidence/2026-10-04/audit-p1/delivery-cold/shared/checks.json` | `gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/shared-red/checks.json` | `gui` | Not Run | error=AssertionError("Operation unexpectedly succeeded: {'FINISHED'}") |
| `outputs/evidence/2026-10-04/audit-p1/baseline/blender/boundary-report.json` | `independent_human_acceptance` | Not Run | error=AssertionError('P1 defects reproduced: dynamic_association_irc, dynamic_association_optimization, shared_mesh_irc, shared_mesh_optimization') |
| `outputs/evidence/2026-10-04/audit-p1/review.json` | `independent_human_acceptance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/association-damaged-red/checks.json` | `independent_human_review` | Not Run | error=AssertionError: Expected rejection, got {'FINISHED'} |
| `outputs/evidence/2026-10-04/audit-p1/association-v1/checks.json` | `independent_human_review` | Not Run | error=ValueError: Atom identities or ordering changed: qc_atom_id |
| `outputs/evidence/2026-10-04/audit-p1/association-v2/checks.json` | `independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/shared-red/checks.json` | `independent_human_review` | Not Run | error=AssertionError("Operation unexpectedly succeeded: {'FINISHED'}") |
| `outputs/evidence/2026-10-04/audit-p1/delivery-cold/shared/checks.json` | `undo_redo` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-04/audit-p1/shared-red/checks.json` | `undo_redo` | Not Run | error=AssertionError("Operation unexpectedly succeeded: {'FINISHED'}") |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
