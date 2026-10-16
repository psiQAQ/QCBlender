# 标注默认值和编辑窗口
Triage: ready-for-agent
Status: resolved

## 已批准目标

四类标注默认字号 0.5，已有字号保留；原子标注默认只显示元素符号，自定义前缀保留但不自动追加原子编号。已有文字在编辑确认或构型刷新时应用。新建和编辑的偏移 XYZ 一行等宽。每个来源编号右侧同行显示元素及当前源构型经对象 matrix_world 变换后的 Blender 全局坐标，固定两位小数；不包含振动演示位移。批量列表沿用同一行布局，编号范围、重复拒绝和旧 atoms 参数兼容。

## 实施与验收

工作树 `.worktrees/annotation-ui`，分支 `feat/annotation-ui`。主 Agent 串行维护共享标注模块和证据，复用现有科学依赖。定向模块 test_annotations_core、test_annotation_inputs、test_annotation_geometry、test_science_measurements、test_i18n_core、test_ui_localization；实际 Blender 验证当前构型及对象/父级变换、编号修改/交换/批量、四类创建和编辑、旧字号、自定义前缀、保存冷读；真实 GUI 验证横向偏移和同行预览。最终完整构建 ZIP 并隔离安装。独立人工/科研验收单列。

## Comments

- 2026-10-17：main 起点 8fd2452，工作区干净，Blender 无运行进程。全局安装和远端操作不在本次批准方案中。
- 2026-10-17：用户另行批准本地提交、ff-only 合入 main 及注释标签归档。源码提交 2bb5f72；266 标准库、100 公开科学、65 定向、完整构建/隔离安装、原生行为、四类新建弹窗和原子编辑/批量/编号实时预览、菜单撤销重做、保存冷读 Passed；Standards/Spec 各 0 发现。日常安装与独立人工/科研接受 Not Run。验收入口 `validation/agent/acceptance/annotation-ui.md`，产物由 `docs/ARTIFACTS.md` 路由。
