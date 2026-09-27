# C 创建正交取景相机

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

## 实施

独占新 `qcblender/framing.py`、`qcblender/blender/camera.py` 及专用数学测试；公共 UI 入口由主代理添加。操作符 `qcblender.create_framed_camera`，沿触发 VIEW_3D 的当前观察方向，为选中 QC 显示对象取景（没有有效选择时使用活动 QC 对象），不自动扩到全场景。

每次先完整验证，再新建带 QC 标记的正交相机并激活；默认每侧 5% 边距，按 render/pixel aspect 取景。当前帧已求值几何/体积的世界边界必须包含真实节点显示；排除 hide_render、渲染禁用集合和内部源数据。雾优先已求值体积边界，必要时使用绑定源体积边界；无有效边界报错。不修改既有相机、对象变换和灯光。支持原生 UNDO。不复制 MolecularNodes 场景系统，不新增依赖。

## 验收

纯 Python：非方画幅、旋转、多对象、单点/零跨度、5% 边距、无效坐标。主代理：真实原子/等值面/雾、多视图、隐藏对象、当前视角、横竖渲染、旧相机不变、撤销/重做、保存与移动冷重开。

## Comments

2026-09-27：主代理已完成 Blender 5.1.1 实际验收，Passed。40/40 科学回归、独立安装；原子、等值面、雾、多视图、变换、横竖画幅与像素比例的原生相机投影均在 5% 边距内；渲染隐藏及内部源排除，旧相机/灯光/对象变换保留；两种修改器开关冲突、空几何/仅隐藏对象拒绝且不新增相机。Computer Use 按钮、原生撤销、相机画面与错误提示，MCP 重做恢复状态；原地及移动后冷重开和渲染 Passed。`outputs/source-adoption/03-camera/qualification.json` 核对源码、ZIP、安装副本一致。

2026-09-27：本轮明确纳入正交自动取景；透视、灯光预设和自动排版仍后置。子代理不运行 Blender；运行期接口可静态阅读本机 API 文档。

2026-09-27：已在 `feat/adopt-camera` 实现 `qcblender.create_framed_camera`。纯数学拟合使用 VIEW_3D 当前方向、render/pixel aspect 和每侧默认 5% 边距；运行期先验证选中 QC 显示视图的已求值边界（包括 Geometry Nodes 实例），雾在自身边界缺失时读取绑定体积，全部验证后才新建带 `qc_camera` 标记的正交相机并设为 `scene.camera`。纯 Python 专用测试 Passed；Blender 原子、等值面、雾、隐藏对象、撤销及保存冷重开 Not Run，由主代理验收。任务保持 claimed。

2026-09-27：参与取景的 QC 视图若有 modifier 的 `show_viewport` 与 `show_render` 不一致，操作符在创建相机前报错，要求先匹配两项开关。纯数学四项测试 Passed；Blender 两种开关组合 Not Run，由主代理验收。
