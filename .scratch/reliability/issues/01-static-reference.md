# 01 外部分析静态参考

Triage: ready-for-agent
Status: claimed
Blocked by: none

## 范围与验收

遵循spec第一批1。保存真实P04默认比较/当前步骤不一致的失败证据；入口拒绝动态Dataset和绑定祖先，静态P03/普通静态Log不回退。begin后换绑定、删除对象、切换构型在accept前拒绝且无新增对象。AIM/NBO/ETS/IGMH/IRI以及相关外部入口共享最小守卫，不改手动关联语义。单元与原生脚本先红后绿；主Agent串行原生和GUI验证。

## Comments

2026-10-05：领取。文件归属为静态参考helper、external_fields/external_results/nbo/capabilities及worker必要入口、相关专属测试脚本；不修改jobs/ui/project/views。

2026-10-05：实现专用外部静态参考守卫，覆盖AIM、ESP、ETS-NOCV、NBO、IGMH/IRI与NOCV Cube入口。检查当前对象及所有绑定祖先的优化可用状态、IRC和XYZ轨迹；异步accept核对原始RNA对象指针及有效性、祖先链、路径绑定、Dataset/source摘要和当前manifest摘要，在场景创建前拒绝。worker读取参考时再次核对静态Dataset与manifest摘要。手动当前构型关联的科学比较逻辑保持原契约。

验证：

- Passed：最小红能力测试在修复前运行，2 tests / 36 failing subcases，真实capability错误允许优化/IRC及动态祖先；修复后同命令2 tests全部通过。
- Passed：`QCBLENDER_REFERENCE_ROOT=D:/workspace/QCBlender`，Blender 5.1内置`python.exe -B -m unittest discover -s tests -p '*static_reference*.py'`，5 tests全部通过，包含真实优化Log、P04 IRC、独立step-001 FCHK和静态Log、实际多帧与单帧XYZ。
- Passed：既有`test_science_current_association`、`test_science_xyz`、`test_science_aim_association`、`test_science_nocv_status`，29 tests全部通过。实际运行通过`python.exe -B -c`显式加载主库`outputs/science`与本工作树`tests`，未安装依赖。
- Passed：主Agent串行原生基线红复现，动态Dataset的`bpy.ops.qcblender.import_paired_field.poll()`错误返回eligible；证据为主库`outputs/evidence/2026-10-05/reliability/logs/static-red.json`与同名`.log`。
- Passed：`git diff --check`，既有源码LF换行保持。
- Not Run：本分支候选原生绿色验证。交主Agent运行`tools/verify_static_reference.py`，参数`--root <候选树> --sample D:/workspace/QCBlender --out <本批证据目录>`；脚本覆盖真实Dataset绑定下的operator poll/execute拒绝、begin/accept正文守卫、路径绑定/动态祖先/manifest/删除同名替换与静态重命名。
- Not Run：主Agent负责真实atom_view/IRC显示层、P03 paired实际创建与数值检查、worker进程集成、GUI提示、Undo/Redo及新进程冷读；本子任务未启动Blender进程或GUI。

Status保持claimed，等待主Agent完成原生与界面验收。
