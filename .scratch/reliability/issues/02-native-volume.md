# 02 原生体场可读性

Triage: ready-for-agent
Status: resolved
Blocked by: none

## 范围与验收

遵循spec第一批2。相同VDB长路径加载失败、短路径成功；原生检查在场景写入/保存发布/重新绑定前运行，验证必要网格，错误保留具体路径与原生原因。覆盖中文/长路径、缺失损坏VDB、无权限/保存失败，失败保留原绑定和工程，临时datablock零泄漏。主Agent运行真实Blender与冷读。

## Comments

2026-10-05：领取。文件归属为原生VDB检查helper、blender/views.py、blender/project.py及专属脚本，不修改科学data.py、jobs/ui和外部导入文件。

## Answer

2026-10-05：实现完成；原生体场技术验收通过。`native_volume.check_field_cache` 在安全资产解析后先由 Blender 实际加载 `qc_value`、`qc_negative`、`qc_valid`，随后保留既有摘要核对。原生检查使用未关联的临时 Volume，并在成功、失败及异常路径释放。`field_view` 在场景写入前检查；`save_project` 在绑定、场景索引发布及 Blender 保存前检查最终副本；`rebind_dataset` 在修改任何绑定前检查替代 Dataset 及实际 Volume 目标。错误保留文件路径和原生原因；Windows 原生加载失败可提示较短工程位置，不以字符阈值代替加载判定。文件系统读写沿用 extended Windows path 边界，Blender 保留普通路径。

验证：

- **Passed**：`python -m unittest discover -s tests -p 'test_native_volume*.py'`，11 项 helper/事务边界测试；保存失败注入只隔离 Blender-save 边界，属于单元证据。
- **Passed**：专属产品与验证脚本 `py_compile`；`git diff --check`。
- **Passed**：主 Agent 串行执行真实 Blender 5.1.1 原生脚本 `tools/verify_native_volume.py`。报告：主仓库 `outputs/runs/rel/v-native2/report.json`；日志及命令：`outputs/evidence/2026-10-05/reliability/logs/volume-native2.log`、`volume-native2.json`（exit 0）。普通及中文路径加载全部三个网格；相同摘要长路径原生失败、缺失文件、损坏文件、缺 `qc_valid` 在创建场前拒绝，datablock/对象集合不变；长路径及损坏/缺网格重新绑定失败保留原绑定；真实 relocate/save operator 覆盖中文成功及长路径拒绝；真实 Blender save 因 `.blend` 目标是目录失败，原场景索引与绑定保留；最终副本不可读时原工程与原索引摘要保留。
- **Passed**：主 Agent 运行 `tools/verify_native_volume_red.py` 复验，见主仓库 `outputs/evidence/2026-10-05/reliability/logs/volume-green.*`。
- **Not Run**：自然无权限目标，未改变 ACL；界面提示、Undo/Redo、最终候选原地及移动后新进程冷读由 06 统一验证；独立人工及科学签署保持独立。

诊断历史：主 Agent 的原始产品 red 在原生 `grids.load() == False`、`field.vdb not found` 后，`field_view` 仍创建 source 对象并在更长 manifest 读取失败；见 `volume-red-prepared.*`。第一次 red 缺少生成 node assets，为验证前置失败，见 `volume-red.*`；完整原生初次复验发现重新绑定 strict resolve 尚未使用 extended path，见 `volume-native.*`。最终 `volume-native2` 覆盖修正后的文件系统边界。上述日志同在主仓库 `outputs/evidence/2026-10-05/reliability/logs/`，不将前置失败或部分复验计为通过。
