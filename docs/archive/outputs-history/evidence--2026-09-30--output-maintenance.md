# 2026-09-30 output-maintenance

2026-09-30产物路由与保全清理。固定验证 aaf20f84，归档 archive/2026-09-30/chore/output-maintenance，main合并8188a41。清单删除67453文件/3279888606字节，同口径净减少2970132043字节。8边界/69科学、离线构建安装与双冷读Passed；168不可访问对象、两个占用日志及旧工作树阻塞使总体Failed；旧默认后端wheel不可读。

原目录：`outputs/evidence/2026-09-30/output-maintenance/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `verified_commit` | `aaf20f84f77afce366abcb75c3455707e447805d` |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `archive_tag` | `archive/2026-09-30/chore/output-maintenance` |

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `status`=Failed；`checks.storage_cleanup.status`=Failed；`checks.migration.status`=Passed；`checks.cleanup_boundaries.status`=Passed；`checks.input_hashes.status`=Passed；`checks.science_after.status`=Passed；`checks.rebuild_after.status`=Passed；`checks.install_and_lifecycle.status`=Passed；`checks.cold_original.status`=Passed；`checks.cold_chinese_moved.status`=Passed；`checks.retained_candidate_qualification.status`=Passed；`checks.user_project.status`=Passed；`checks.recovery_project.status`=Passed；`checks.original_backend_default.status`=Failed；`checks.independent_signature.status`=Not Run；`scope`=Safe partial storage maintenance; permission and active-session objects retained；`checks.cleanup_boundaries.tests`=8；`checks.science_after.tests`=69；`checks.science_after.failures`=0；`checks.science_after.errors`=0；`checks.science_after.skipped`=0；`checks.science_after.metrics.density_max_abs_error`=8.440006539212064e-07；`checks.science_after.metrics.esp_max_abs_error`=4.60872461194306e-06；`checks.science_after.metrics.electron_count`=9.999999997365176；`checks.retained_candidate_qualification.scope`=Byte/source/wheel identity plus original candidate-bound reports; does not rerun the historical full suite；`cleanup.skipped[0].reason`=[WinError 32] 另一个程序正在使用此文件，进程无法访问。: 'D:\\workspace\\QCBlender\\outputs\\cleanup-followup-20260930\\visible-user-error.log'；`cleanup.skipped[1].reason`=[WinError 32] 另一个程序正在使用此文件，进程无法访问。: 'D:\\workspace\\QCBlender\\outputs\\cleanup-followup-20260930\\visible-user.log' |
| `outputs/evidence/2026-09-30/output-maintenance/science.json` | `status`=Passed；`tests`=69；`failures`=0；`errors`=0；`skipped`=0；`metrics.density_max_abs_error`=8.440006539212064e-07；`metrics.esp_max_abs_error`=4.60872461194306e-06；`metrics.electron_count`=9.999999997365176 |
| `outputs/evidence/2026-09-30/output-maintenance/after-commands.json` | `[0].status`=Passed；`[1].status`=Passed |
| `outputs/evidence/2026-09-30/output-maintenance/after.json` | `scope`=Readable regular files under main outputs; inaccessible objects excluded on both scans; includes newly retained evidence, projects and qualified wheels; excludes own after inventory files |
| `outputs/evidence/2026-09-30/output-maintenance/cleanup-units-command.json` | `status`=Passed |
| `outputs/evidence/2026-09-30/output-maintenance/closing-git.json` | `status`=Passed；`independent_signature`=Not Run；`push`=Not Run；`scope`=Final Git and preserved-candidate check only; overall cleanup remains Failed |
| `outputs/evidence/2026-09-30/output-maintenance/closing.json` | `status`=Failed；`local_merge`=Passed；`current_worktree_removal`=Passed；`merged_branch_removal`=Passed；`existing_tags_preserved`=Passed；`submodules_preserved`=Passed；`candidate_and_original_reports_preserved`=Passed；`all_migration_targets_verified`=Passed；`push`=Not Run；`independent_signature`=Not Run；`scope`=Local merge/archive and current task worktree cleanup Passed; historical cleanup blockers retained |
| `outputs/evidence/2026-09-30/output-maintenance/environment.json` | `status`=Passed；`scope`=Explicit qualified wheel set and existing shared installed versions; original backend wheel unreadable |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-09-30/output-maintenance/rebuild-commands.json` | `[2].status` | Failed | [2].name=rebuild-install; [2].exit_code=1 |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `checks.original_backend_default.status` | Failed | checks.original_backend_default.reason=Main backend wheel unreadable; explicit qualified pair retained and validated |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `checks.storage_cleanup.status` | Failed | checks.storage_cleanup.reason=168 inaccessible scan/hash objects and two process-locked logs retained; old worktree blockers remain |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.b48c.status` | Failed | old_worktrees.b48c.reason=Empty root still locked by host process; normal Remove-Item failed. Branch retained. |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[0].status` | Failed | old_worktrees.f458.checks[0].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\profile\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\114e7635a429f6e0fd5d889f3ef827823eeaf04fbdad3862092ef2b985294ff2' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[10].status` | Failed | old_worktrees.f458.checks[10].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc03\\mo8.qcdata\\datasets\\0a16580b73c808e8f99ca2522619857752d75e77cff9605600b40c68f1e8e396' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[11].status` | Failed | old_worktrees.f458.checks[11].reason=[Errno 13] Permission denied: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc02\\portable.zip' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[12].status` | Failed | old_worktrees.f458.checks[12].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc02\\mo8.qcdata\\datasets\\114e7635a429f6e0fd5d889f3ef827823eeaf04fbdad3862092ef2b985294ff2' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[13].status` | Failed | old_worktrees.f458.checks[13].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc02\\mo8.qcdata\\datasets\\0a16580b73c808e8f99ca2522619857752d75e77cff9605600b40c68f1e8e396' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[1].status` | Failed | old_worktrees.f458.checks[1].reason=[Errno 13] Permission denied: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\acceptance\\portable.zip' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[2].status` | Failed | old_worktrees.f458.checks[2].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\acceptance\\mo8.qcdata\\datasets\\114e7635a429f6e0fd5d889f3ef827823eeaf04fbdad3862092ef2b985294ff2' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[3].status` | Failed | old_worktrees.f458.checks[3].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\acceptance\\mo8.qcdata\\datasets\\0a16580b73c808e8f99ca2522619857752d75e77cff9605600b40c68f1e8e396' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[4].status` | Failed | old_worktrees.f458.checks[4].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\final\\profile\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\643ca31775567f9319ad6dccce37df424d41928898294baa0b1033889544f3d8' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[5].status` | Failed | old_worktrees.f458.checks[5].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\final\\profile\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\518cf7605b8693bb1eaaa781334f06e02e840a6311305a47beff820112e8f770' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[6].status` | Failed | old_worktrees.f458.checks[6].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\recovery\\另一个目录\\datasets\\dd1241ed6eb88c4d9a5ae1ced3153520cff5a2d28d5882532b2bd3120d4def4f' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[7].status` | Failed | old_worktrees.f458.checks[7].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\recovery\\另一个目录\\datasets\\d9a30b5952c758d660d505fba71a137d4f5db1203ef7f02250e2c0afda73c01f' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[8].status` | Failed | old_worktrees.f458.checks[8].reason=[Errno 13] Permission denied: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc03\\portable.zip' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.checks[9].status` | Failed | old_worktrees.f458.checks[9].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc03\\mo8.qcdata\\datasets\\643ca31775567f9319ad6dccce37df424d41928898294baa0b1033889544f3d8' |
| `outputs/evidence/2026-09-30/output-maintenance/protection-checks.json` | `old_worktrees.f458.status` | Failed | old_worktrees.f458.checks[0].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\profile\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\114e7635a429f6e0fd5d889f3ef827823eeaf04fbdad3862092ef2b985294ff2'; old_worktrees.f458.checks[1].reason=[Errno 13] Permission denied: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\acceptance\\portable.zip'; old_worktrees.f458.checks[2].reason=[WinError 5] 拒绝访问。: '\\\\?\\C:\\Users\\ustcw\\.codex\\worktrees\\f458\\Q |
| `outputs/evidence/2026-09-30/output-maintenance/closing.json` | `status` | Failed | scope=Local merge/archive and current task worktree cleanup Passed; historical cleanup blockers retained |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `status` | Failed | scope=Safe partial storage maintenance; permission and active-session objects retained |
| `outputs/evidence/2026-09-30/output-maintenance/result.json` | `checks.independent_signature.status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/output-maintenance/short-install.json` | `cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/output-maintenance/retained-qualification.json` | `evidence.extension-install.json.report.cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/output-maintenance/rebuild-qualification.json` | `evidence.short-install.json.report.cold_open` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-09-30/output-maintenance/closing-git.json` | `independent_signature` | Not Run | scope=Final Git and preserved-candidate check only; overall cleanup remains Failed |
| `outputs/evidence/2026-09-30/output-maintenance/closing.json` | `independent_signature` | Not Run | scope=Local merge/archive and current task worktree cleanup Passed; historical cleanup blockers retained |
| `outputs/evidence/2026-09-30/output-maintenance/closing-git.json` | `push` | Not Run | scope=Final Git and preserved-candidate check only; overall cleanup remains Failed |
| `outputs/evidence/2026-09-30/output-maintenance/closing.json` | `push` | Not Run | scope=Local merge/archive and current task worktree cleanup Passed; historical cleanup blockers retained |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
