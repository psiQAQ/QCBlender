# 2026-10-01 tutorial-fog-92d498c

固定92d498c的体积雾修复候选：26单测/69科学、材质绑定、零不透明度、符号色、裁剪及冷读渲染Passed；263字符移动路径安装Failed，短路径复验Passed。该专用候选可见材质预览及原C01完整GUI/数组不变复验仍Not Run。

原目录：`outputs/evidence/2026-10-01/tutorial-fog-92d498c/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `source_commit` | `92d498c2e7c378bece4ae38c6a9df640eb8f0bcf` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `python_tests.status`=Passed；`science.status`=Passed；`fog.status`=Passed；`fog.material_slot_binding`=Passed；`fog.operator`=Passed；`fog.zero_opacity`=Passed；`fog.signed_color_render`=Passed；`fog.source_cache_unchanged`=Passed；`fog.cold_open_render`=Passed；`fog.plane_box_clip_render`=Passed；`fog.opacity_curve_render`=Passed；`vmd_copy_chain_status`=Passed；`initialization.status`=Passed；`initialization.fog_bindings[0].slot_socket_identity`=Passed；`initialization.material_preview_gui`=Not Run；`initialization.scientific_array_checks`=Not Run；`commands[0].status`=Passed；`commands[1].status`=Failed；`python_tests.tests`=26；`science.tests`=69；`science.failures`=0；`science.errors`=0；`science.skipped`=0；`science.metrics.density_max_abs_error`=8.440006539212064e-07；`science.metrics.esp_max_abs_error`=4.60872461194306e-06；`science.metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/fog-render/report.json` | `status`=Passed；`material_slot_binding`=Passed；`operator`=Passed；`zero_opacity`=Passed；`signed_color_render`=Passed；`source_cache_unchanged`=Passed；`cold_open_render`=Passed；`plane_box_clip_render`=Passed；`opacity_curve_render`=Passed |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/node-assets/report.json` | `status`=Passed；`shared_unbound_asset`=Passed；`independent_parameters`=Passed；`independent_source_transforms`=Passed；`preserved_branch`=Passed；`library_roundtrip`=Passed |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/source-tests/report.json` | `checks[0].status`=Passed；`checks[1].status`=Passed；`checks[2].status`=Passed；`checks[3].status`=Passed；`checks[4].status`=Passed；`syntax`=Passed；`diff_check`=Passed |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/science.json` | `status`=Passed；`tests`=69；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/build-command.json` | `status`=Passed |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/install-command.json` | `status`=Failed |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/preflight.json` | `status`=Passed；`failed_preflight_attempts[0].status`=Failed；`failed_preflight_attempts[1].status`=Failed；`failed_preflight_attempts[2].status`=Failed；`failed_preflight_attempts[3].status`=Failed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `commands[1].status` | Failed | commands[1].name=outputs/runs/fog-candidate-92d498c/install-command; commands[1].exit_code=1 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `failed_attempts.preflight[0].status` | Failed | failed_attempts.preflight[0].exit_code=1; failed_attempts.preflight[0].error=PermissionError: [Errno 13] Permission denied |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `failed_attempts.preflight[1].status` | Failed | failed_attempts.preflight[1].exit_code=1; failed_attempts.preflight[1].error=PermissionError: [Errno 13] Permission denied |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `failed_attempts.preflight[2].status` | Failed | failed_attempts.preflight[2].exit_code=1; failed_attempts.preflight[2].error=PermissionError: [Errno 13] Permission denied |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `failed_attempts.preflight[3].status` | Failed | failed_attempts.preflight[3].exit_code=1; failed_attempts.preflight[3].error=UnicodeDecodeError: gbk decode of UTF-8 input catalog |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/preflight.json` | `failed_preflight_attempts[0].status` | Failed | failed_preflight_attempts[0].exit_code=1; failed_preflight_attempts[0].error=PermissionError: [Errno 13] Permission denied |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/preflight.json` | `failed_preflight_attempts[1].status` | Failed | failed_preflight_attempts[1].exit_code=1; failed_preflight_attempts[1].error=PermissionError: [Errno 13] Permission denied |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/preflight.json` | `failed_preflight_attempts[2].status` | Failed | failed_preflight_attempts[2].exit_code=1; failed_preflight_attempts[2].error=PermissionError: [Errno 13] Permission denied |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/preflight.json` | `failed_preflight_attempts[3].status` | Failed | failed_preflight_attempts[3].exit_code=1; failed_preflight_attempts[3].error=UnicodeDecodeError: gbk decode of UTF-8 input catalog |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/build-science-and-failed-long-path/install-command.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/qualification/extension-install.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/qualification/fog-initial.json` | `cold_open_render` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `initialization.material_preview_gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `initialization.scientific_array_checks` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/original-C01-initialization/visible-init-background.json` | `material_preview_gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/qualification/vmd-copy-initial.json` | `moved_cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `remaining.material_preview_visible_GUI` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/summary.json` | `remaining.original_C01_GUI_and_scientific_array_invariance` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/source-tests/native-report.json` | `render` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/original-C01-initialization/visible-init-background.json` | `scientific_array_checks` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/source-tests/native-report.json` | `scientific_arrays` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-01/tutorial-fog-92d498c/qualification/vmd-copy-initial.json` | `status` | Not Run | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
