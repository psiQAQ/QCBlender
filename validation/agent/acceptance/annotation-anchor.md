# 圆弧中点引线与创建朝向验收

2026-10-16，Windows x64 / Blender 5.1.1。候选源码 `b02c9fac2bfbee90d1d7d761246032c29b5d3c3b`；ZIP 50,940,463 字节，SHA-256 `b134cc2f5faaf367a193dbfbc93f801d6b748d27fbdc6b27a186c27530ed6775`。安装入口见 [current-install.json](../current-install.json)，汇总见 [acceptance.json](../reports/2026-10-16/annotation-anchor/acceptance.json)。

## 行为

键角和二面角的引线从所显示圆弧的角度二分点出发；采样包含精确半角顶点，文字位置和偏移规则不变。正负二面角与 180° 均覆盖。零长或未定义圆弧保持无弧行为；旧版无 ARC 部件的标注在升级前保留原锚点。

四类标注创建时，存在场景相机就对本次新文字执行一次朝向相机，包含旋转父对象的补偿；无相机仍可创建。没有添加跟踪约束，之后移动相机或编辑标注不会自动重置文字朝向，打开旧工程不会批量旋转旧文字。

## 验证

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 标准库与公开科学 | Passed | [stdlib.json](../reports/2026-10-16/annotation-anchor/stdlib.json) 266 项；[science.json](../reports/2026-10-16/annotation-anchor/science.json) 96 项；无失败、错误或跳过。半角回归先在旧代码观察到 5 个子案例失败 |
| 安装后原生几何 | Passed | [annotation-geometry.json](../reports/2026-10-16/annotation-anchor/geometry/annotation-geometry.json) 与 [冷读](../reports/2026-10-16/annotation-anchor/geometry/annotation-geometry-reopen.json)：半角、引线、半径修改、文字位置、四类创建朝向、无相机、一次性语义、旧版兼容 |
| Computer Use 创建 | Passed | 实际点击 Properties 的 Angle、Dihedral；[gui-native.json](../reports/2026-10-16/annotation-anchor/gui-native.json) 核对 32.05° 与 10.36°、旋转父对象、世界朝向误差为零；[截图](../reports/2026-10-16/annotation-anchor/gui-created-angle-dihedral.png) |
| GUI 工程保存与冷读 | Passed | 自包含工程 `outputs/runs/annotation-anchor-20261016/gui-evidence/annotations.blend`；关闭原 PID 后新进程 [核对](../reports/2026-10-16/annotation-anchor/gui-native-cold.json) |
| 四类渲染与中文字体 | Passed | [render.json](../reports/2026-10-16/annotation-anchor/gallery/render.json)、[冷读渲染](../reports/2026-10-16/annotation-anchor/gallery/render-reopen.json)；没有额外调用朝向操作。Agent 检视初次与冷读图片，不代替独立人工接受 |
| 完整安装、计算、移动冷读 | Passed | `outputs/runs/annotation-anchor-20261016/extension/extension.json`；重建 9 个节点资产、复用原有 11 个锁定 wheel，安装文件与 ZIP 逐字节一致 |
| 日常安装和原保存工程 | Passed | [global-install.json](../reports/2026-10-16/annotation-anchor/global-install.json)、[后台冷读](../reports/2026-10-16/annotation-anchor/global-cold-background.json)、[GUI 冷读](../reports/2026-10-16/annotation-anchor/global-cold-gui.json)：10 项基线核对通过；[恢复观察](../reports/2026-10-16/annotation-anchor/global-user-restored.png) |
| 本批轨迹 GUI 切换、独立人工/科研接受 | Not Run | 自动几何更新覆盖不等同本批轨迹 GUI；独立使用者未签署 |
| 完整教程图片 | Failed | 既有 27 个占位仍缺 23 张，未以技术截图填充人工教程 |

## 保留与复现

日常 Blender 最终打开原保存工程 `outputs/projects/sidebar-preserved-20261016/user-session.blend`，原文件和 `.qcdata` 字节不变。较新恢复文件按用户澄清视为草稿，不作为恢复目标；已保全副本原位保留。后续涉及 Blender 的任务先请用户关闭当前 Blender，确认退出后开始，完成后打开原保存工程。

运行脚本、旧全局插件、偏好和旧当前 ZIP 位于 `outputs/runs/annotation-anchor-20261016/`；候选位于 `outputs/candidates/current/annotation-anchor-20261016-r1/`，工程与渲染在本批报告的 `gallery/`。旧对象均保留。自动审批曾因尚无明确退出证据拒绝冷重开；核对全部 Blender 进程为空后重试通过，没有并行启动。

重建使用 `tools/build_extension.py`；验证使用 `tools/run_stdlib_tests.py`、`tools/run_science_tests.py`、`tools/verify_extension.py`、`tools/verify_annotation_geometry.py`、`tools/render_annotation_gallery.py`。本地 main 综合验证、忽略文件保全与正常归档由本批 `delivery.json`、`worktree-retention.json`、`archive-local.json` 记录；标签 `archive/2026-10-16/fix/annotation-anchor`，不 push。产物入口：[ARTIFACTS](../../../docs/ARTIFACTS.md#annotation-anchor-20261016)。
