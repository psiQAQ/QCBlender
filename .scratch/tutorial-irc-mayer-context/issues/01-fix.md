# 01 最小上下文修复与回归检查

Triage: ready-for-agent
Status: resolved
Blocked by: none

## Comments

2026-10-02：任务建立（pending）。原生 GUI 导入完成表数据后，自动绘图 poll 因 context.object 仍为旧 IRC 根对象失败。
2026-10-02：领取（claimed）。源码确认绘图 poll 与 execute 读取 context.object；显式覆盖 object 与 active_object。
2026-10-02：本任务静态验收完成（resolved）；Blender 专项及原生 GUI 由02独立验收。

## Answer

Passed：嵌套绘图调用以 context.temp_override(object=obj, active_object=obj) 使用新表对象；原选择逻辑保持。verify_irc.py 使用固定旧根对象的真实 bpy.context.temp_override 调用导入，检查 FINISHED、四数组、所选对与显示值、自动曲线/游标、当前第2步及游标位置；冷重开复用同组断言。未 mock Operator 或 poll，未修改科学契约、接口、依赖、教程、样本。

Passed：两个 Python 文件通过 compile，原 BOM/换行保持，git diff --check 无错误。证据：本工作树 outputs/evidence/2026-10-02/tutorial-irc-mayer-context/static.json。

Not Run：Blender 专项、候选安装、原生 GUI、保存与冷重开。02保持 pending，由主 Agent 验收；最终 CHANGELOG、ARTIFACTS 和教程证据索引由主 Agent 统一更新。
