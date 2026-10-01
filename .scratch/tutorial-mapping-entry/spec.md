# 旧多选标量映射 GUI 入口

## 目标
在默认 Developer Extras 关闭时，将已注册的 qcblender.map_scalar 操作加入既有对象右键 QCBlender 子菜单，供普通 F3 菜单搜索发现。

## 范围
仅修改 qcblender/blender/editor_ui.py 的 QCBLENDER_MT_object.draw；活动接收对象为 field、slice 或 atoms 且选中对象数为 2 时显示原英文操作标签。保持原 operator、公共接口、科学计算、偏好、依赖和教程不变。

## 验收
本子任务验收仅包括源码修改、Python 语法和差异检查。Blender GUI、F3 检索和科学映射复验由主 Agent 执行，本子任务不启动或连接 Blender、MCP 或 Computer Use。

## 基线与依据
- Base: 92d498c2e7c378bece4ae38c6a9df640eb8f0bcf
- Branch: fix/tutorial-mapping-entry
- 官方 Blender 2.90 UI 发布说明：普通搜索通过菜单项检索；Developer Extras 使 raw operators 出现在结果中。https://developer.blender.org/docs/release_notes/2.90/user_interface/
- 当前 scalars.py 中 QCBLENDER_OT_map_scalar 已实现 poll、invoke 和 execute；editor_ui.py 对象子菜单尚无该操作入口。
