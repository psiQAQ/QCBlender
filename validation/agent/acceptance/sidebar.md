# Sidebar 摘要与标注编号输入验收

2026-10-16，Windows x64 / Blender 5.1.1。最终候选源码 `8e085f0f674cbebfa1f42ce7233b1632562603b1`，ZIP 50,940,317 字节，SHA-256 `08e53572ce691104a463a56b76d2c7c6c38d0192ff175571726cf8973b057b5b`。安装入口由 [current-install.json](../current-install.json) 定位，机器结果见 [acceptance.json](../reports/2026-10-16/sidebar/acceptance.json)。

## 用户可见结果

Sidebar 保留导入导出、当前 QC 对象、折叠数据与来源详情、折叠对象导航、工程维护。计算、显示视图、空间工具、场值采样及相机集中到对象属性；原子标注保留在局部选择与标注。导航只选择对象，不改变其隐藏状态。Sidebar 摘要读取三维视图的活动对象，固定的 Properties 目标单独生效；标注子对象明确显示所属来源。

摘要显示源原子总数、源文件、计算段及当前构型。详情按类别展示场、轨道、振动、轨迹与外部分析的数量、单位和维度；长列表有界，不加载数组。隐藏原子不减少源总数，缓存缺失明确显示未知，普通对象和空选择不沿用上一个 QC 对象。

四类标注均采用独立整数输入，支持键入及左右步进。越界钳制到 `1..源原子总数`；若钳制后的编号与同组其它编号重复，保留该控件原值。测量使用 2/3/4 个编号，原子标注支持批量数量；交换按钮可调整满组编号顺序。编辑同步各几何部件的 `source_atom_numbers`，字符串 `atoms` 程序调用继续兼容。

## 验证范围

| 检查 | 状态 | 实际证据 |
| --- | --- | --- |
| 标准库与公开科学 | Passed | [stdlib-r2.json](../reports/2026-10-16/sidebar/stdlib-r2.json) 266 项；[science-r2.json](../reports/2026-10-16/sidebar/science-r2.json) 94 项，均无失败、错误或跳过 |
| 原生摘要与无 IO 绘制 | Passed | [native-summary.json](../reports/2026-10-16/sidebar/native-summary.json) 9 项：真实 4 原子/3 帧 XYZ、隐藏源总数、标注归属、普通/空选择、缓存缺失及恢复。大类别、振动、外部表格和优化/IRC 的单位维度使用合成缓存，未冒充真实科学计算 |
| Properties 固定目标与相机 | Passed | [native-context.json](../reports/2026-10-16/sidebar/native-context.json)：属性相机只取固定对象，3D 入口保留多选；实际窗口只有一个 VIEW_3D。最终清理恢复选择、pin、相机，临时对象无残留 |
| 原生上下文边界 | Not Run | 多 VIEW_3D 最大区域的原生比较未执行；非 Object pin 受 Blender 动态 RNA 类型限制。两者有边界单元测试，不能等同原生通过 |
| 标注整数 GUI | Passed | [gui-annotation-validation.json](../reports/2026-10-16/sidebar/gui-annotation-validation.json)：四类创建、键入/左右步进、上下界、重复拒绝、二面角交换、批量 4 标签、距离编辑至 `[1,3]`；撤销及 Edit 菜单 Redo 已观察并核对记录 |
| 隐藏对象导航 | Passed | [gui-navigation.json](../reports/2026-10-16/sidebar/gui-navigation.json)：实际点击选中隐藏源，`hide_get` / `hide_render` 均保持 true |
| 迁移入口 GUI | Passed | 实际导入 CH4 fchk、生成 alpha HOMO MO5、39×40×39 场、创建切片/体积雾、导出当前雾视图摘要；R2 实际点击 Properties 探针、三维表面、Enter 保存和创建相机，见 [gui-final-r2.json](../reports/2026-10-16/sidebar/gui-final-r2.json) |
| 双语与独立工具提示开关 | Passed | 窄 Sidebar 英/中文截图与 [operator-tooltips-r2.json](../reports/2026-10-16/sidebar/operator-tooltips-r2.json)；开关组合为原生 RNA/翻译检查，不宣称逐按钮悬停 |
| 标注真实几何与冷读 | Passed | [annotation-geometry.json](../reports/2026-10-16/sidebar/geometry-r2-static/annotation-geometry.json)、[annotation-geometry-reopen.json](../reports/2026-10-16/sidebar/geometry-r2-static/annotation-geometry-reopen.json) |
| 完整包安装、worker、渲染、移动冷读 | Passed | `outputs/runs/sidebar-20261016/extension-r2/extension.json`；真实计算、9 个重建节点资产及中文路径工程。全部安装文件与 ZIP 相同，产品 Python 与候选源码逐字节相同 |
| 全局安装与原工程恢复 | Passed | [global-install.json](../reports/2026-10-16/sidebar/global-install.json)、[后台](../reports/2026-10-16/sidebar/global-cold-background.json)和 [GUI](../reports/2026-10-16/sidebar/global-cold-gui.json)冷重开：10 项基线比较全通过，原文件摘要、对象、数据、材质节点、字体、父子关系与语言偏好保持 |
| 完整教程图片 | Failed | 27 个引用现有 4 张，23 张仍待实际操作者补入。保留既有图片，未以技术截图代替教程人工截图 |
| 独立人工与科研验收 | Not Run | Agent 自动检查及 Computer Use 不代替使用者独立判断，未 push 或发布 |

真实 GUI 图：[英文 Sidebar](../reports/2026-10-16/sidebar/sidebar-en.png)、[最终中文 Sidebar](../reports/2026-10-16/sidebar/sidebar-zh-r2.png)、[边界与重复编号](../reports/2026-10-16/sidebar/distance-clamp-and-duplicate.png)、[二面角顺序](../reports/2026-10-16/sidebar/dihedral-inputs-en.png)、[批量原子](../reports/2026-10-16/sidebar/batch-inputs-en.png)、[Properties 探针](../reports/2026-10-16/sidebar/probe-properties-r2.png)、[取景相机](../reports/2026-10-16/sidebar/camera-properties-r2.png)、[原工程恢复观察](../reports/2026-10-16/sidebar/global-user-restored.png)。

## 候选与失败记录

R1 为入口及整数控件的主要 GUI 验证对象。R2 产品只修改 `translations_sidebar.py` 的七个视图标签与 `blender/interaction.py` 的探针元数据比较，见 [candidate-r2.json](../reports/2026-10-16/sidebar/candidate-r2.json)。其余相关产品文件与 R1 相同；最终包重新执行安装、几何、渲染、冷读、上下文和探针 GUI。

探针初次运行发现 manifest 读取器添加的 `_atom_count` 被与持久化 Dataset metadata 直接比较，导致正常场误报“Dataset changed”。现仅从比较副本移除这个派生键，保留其它身份变更检测；新增两项真实 Dataset IO 回归。初次失败证据原样保留。

测试脚本曾因动态 RNA pin 类型及不存在的 `Event.timer` 属性失败，修订后在新隔离进程复跑。此前临时状态没有保存覆盖；失败快照单独保留。标注几何工具首轮误用未初始化轨迹的 XYZ 数据失败，改用其要求的静态 Dataset 复验通过。快捷键 `Ctrl+Shift+Z` 注入曾观察到再次撤销，因此 Redo 使用 Edit 菜单验证，不把该注入当成功。

## 保留与复现

原工程副本：`outputs/projects/sidebar-preserved-20261016/user-session.blend` 及同名 `.qcdata`；验收工程：`outputs/runs/sidebar-20261016/gui-evidence-r1/`、`gui-evidence-r2/`。全局旧插件、偏好、旧当前 ZIP、维护与探针脚本留在本批 runs；R1/R2 候选和失败报告保留。重建使用 `tools/build_extension.py`，相关检查使用 `tools/run_stdlib_tests.py`、`tools/run_science_tests.py`、`tools/verify_extension.py`、`tools/verify_annotation_geometry.py`、`tools/verify_operator_tooltips.py`。

本地快进整合、忽略文件逐项保全与四个注释归档标签由 [ARTIFACTS](../../../docs/ARTIFACTS.md#sidebar-20261016) 及本批 `worktree-retention.json`、`archive-local.json`、`delivery.json` 定位。历史不相关残留不清理。
