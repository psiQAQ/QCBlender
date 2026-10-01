# 旧多选标量映射 GUI 入口

## 目标
在默认 Developer Extras 关闭时，通过对象右键和顶部 Object 菜单的 QCBlender 子菜单提供 qcblender.map_scalar，并使普通 F3 菜单搜索可发现此操作。

## 范围
qcblender/blender/editor_ui.py 的 QCBLENDER_MT_object.draw 增加既有操作；qcblender/__init__.py 向 VIEW3D_MT_object_context_menu 和 VIEW3D_MT_object 对称注册、注销同一回调。活动接收对象为 field、slice 或 atoms 且选中对象数为 2 时显示原英文操作标签。保持原 operator、公共接口、科学计算、偏好、依赖和教程不变。

## 验收
源码、Python 语法、差异和回调注册对称静态检查通过；主 Agent 完成默认偏好下的实际 GUI/F3 复验后任务才能 resolved。本子任务不启动或连接 Blender、MCP 或 Computer Use。

## 基线与依据
- Base: 92d498c2e7c378bece4ae38c6a9df640eb8f0bcf
- Branch: fix/tutorial-mapping-entry
- 官方 Blender UI 发布说明：普通搜索通过菜单项检索；Developer Extras 使 raw operators 出现在结果中。https://developer.blender.org/docs/release_notes/2.90/user_interface/
- 官方 Python API Operator 示例采用 bpy.types.VIEW3D_MT_object.append(menu_func)。https://docs.blender.org/api/3.6/bpy.types.Operator.html
- scalars.py 中既有 QCBLENDER_OT_map_scalar 保持 poll、invoke 和 execute。

## 完成状态
最小菜单修复已完成。主 Agent 在源码 b7090967e6618c15449efec278bcd47a0f018d54 对应候选、Blender 5.1.1 zh_HANS 和 Developer Extras=false 下验证顶部子菜单、F3 检索及新建未映射接收视图的实际执行。GUI 与取样证据、候选 SHA-256 和环境见 issues/01-add-mapping-entry.md。
完整 C04 教程与独立人工签署仍为 Not Run；本结论仅覆盖最小菜单修复。
