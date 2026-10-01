Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

# 加入旧多选映射入口

## 验收
限定接收对象类型和恰好两对象选择，仅增加既有 operator 的菜单入口，并完成非 Blender 静态检查。

## Comments
- 主 Agent 提供默认 show_developer_ui=False、operator registered/poll True、F3 无结果的实测；原失败证据由主 Agent 保留。
- 已从指定基线创建独立工作树并领取；未启动或连接任何 Blender 进程。

## Answer
在 QCBLENDER_MT_object.draw 加入 qcblender.map_scalar；保留原英文 label，限定 field/slice/atoms 接收对象和恰好两个选中对象。原 operator 的 poll、参数对话框和 execute 未修改。

## Validation
- Passed: Python 3.13 AST parse 和 compile（不导入 bpy、不执行模块）。
- Passed: git diff --check。
- Passed: 对照基线确认源码仅新增三行，保留 BOM 状态和换行约定。
- Not Run: Blender 运行、F3 检索、右键点击、映射科学结果和安装验证；由主 Agent 在独占进程中复验。

## Comments
- 官方 Blender UI 发布说明支持菜单入口缺失为普通 F3 搜索不可见的原因；注册和 poll True 不保证普通搜索可发现。
- 交接后仍需主 Agent 保存新包/安装/GUI 证据；本任务 resolved 仅表示上述非 Blender 子任务交付完成。
