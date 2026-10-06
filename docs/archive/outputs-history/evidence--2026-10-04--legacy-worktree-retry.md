# 2026-10-04 legacy-worktree-retry

2026-10-04 f458正常清理重试：14816文件/798822391字节完整保全；11Dataset/600数组/8VDB新进程读回Passed；目录删除Failed（访问拒绝），不修改ACL/所有权。历史可用性受后续逐文件收据约束。

原目录：`outputs/evidence/2026-10-04/legacy-worktree-retry/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

历史候选、源码提交或执行日期没有在本次可读机器摘要中取得完整绑定，保持未核定；不为目录补造身份。已知开发沿革另见 [CHANGELOG](../../CHANGELOG.md)。

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/cold-data.json` | `status`=Passed；`independent_signoff`=Not Run |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/complete-preservation.json` | `status`=Passed |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/host-inventory.json` | `status`=Failed；`errors[0].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc02\\mo8.qcdata\\datasets\\0a16580b73c808e8f99ca2522619857752d75e77cff9605600b40c68f1e8e396'；`errors[1].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc02\\mo8.qcdata\\datasets\\114e7635a429f6e0fd5d889f3ef827823eeaf04fbdad3862092ef2b985294ff2'；`errors[2].reason`=[Errno 13] Permission denied: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc02\\portable.zip'；`errors[3].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc03\\mo8.qcdata\\datasets\\0a16580b73c808e8f99ca2522619857752d75e77cff9605600b40c68f1e8e396'；`errors[4].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc03\\mo8.qcdata\\datasets\\643ca31775567f9319ad6dccce37df424d41928898294baa0b1033889544f3d8'；`errors[5].reason`=[Errno 13] Permission denied: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\rc03\\portable.zip'；`errors[6].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\recovery\\另一个目录\\datasets\\d9a30b5952c758d660d505fba71a137d4f5db1203ef7f02250e2c0afda73c01f'；`errors[7].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\recovery\\另一个目录\\datasets\\dd1241ed6eb88c4d9a5ae1ced3153520cff5a2d28d5882532b2bd3120d4def4f'；`errors[8].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\final\\profile\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\518cf7605b8693bb1eaaa781334f06e02e840a6311305a47beff820112e8f770'；`errors[9].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\final\\profile\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\643ca31775567f9319ad6dccce37df424d41928898294baa0b1033889544f3d8'；`errors[10].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\acceptance\\mo8.qcdata\\datasets\\0a16580b73c808e8f99ca2522619857752d75e77cff9605600b40c68f1e8e396'；`errors[11].reason`=[WinError 5] 拒绝访问。: 'C:\\Users\\ustcw\\.codex\\worktrees\\f458\\QCBlender\\outputs\\repository-cleanup\\phase02\\acceptance\\mo8.qcdata\\datasets\\114e7635a429f6e0fd5d889f3ef827823eeaf04fbdad3862092ef2b985294ff2' |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/new-preservation.json` | `status`=Passed |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/removal.json` | `status`=Failed；`branch.status`=Not Run |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/residue-removal.json` | `status`=Failed |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/sandbox.json` | `objects[0].status`=Passed；`objects[1].status`=Passed；`objects[2].status`=Passed；`objects[3].status`=Passed；`objects[4].status`=Passed；`objects[5].status`=Passed；`objects[6].status`=Passed；`objects[7].status`=Passed；`objects[8].status`=Passed；`objects[9].status`=Passed；`objects[10].status`=Passed；`objects[11].status`=Passed；`objects[12].status`=Passed；`objects[13].status`=Passed；`b48c.status`=Passed；`mode`=sandbox |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/scientific-preservation.json` | `status`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/host-inventory.json` | `status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/residue-removal.json` | `status` | Failed | operation=Remove-Item -LiteralPath <verified f458 path> -Recurse |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/removal.json` | `branch.status` | Not Run | branch.reason=Worktree removal failed; branch retained |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/cold-data.json` | `independent_signoff` | Not Run | 原字段未附原因 |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
