# 标注几何、材质与面板验收（2026-10-16）

**当前结论：r2 的公开科学测试、原生标注几何与冷重开、连续 GUI 创建精度、整包安装/渲染、全局安装和原工程恢复均通过。独立人工与科研签署仍为 Not Run。** 总收据见 [acceptance.json](../reports/2026-10-16/annotations/acceptance.json)。

范围依据：[已批准规格](../../../.scratch/annotations-20261016/spec.md)。环境为 Windows x64、Blender 5.1.1；使用隔离扩展配置执行候选检查，无新增依赖。原始证据根目录为 `validation/agent/reports/2026-10-16/annotations/`；表中链接均指向该批实际报告或快照。原用户工程与候选试验工程分开保留。

## 候选身份与 r1 → r2

| 候选 | 源码提交 | ZIP 字节数 | ZIP SHA-256 |
| --- | --- | --- | --- |
| r1，历史候选 | `69dd8ff983b84e89079a54041e5bc5f2cca43cb2` | 50,928,784 | `5f9a3b86178ff3db2d876e320cbd8f386b7dcb526e10d0959be64ec1bdc5d661` |
| r2，当前交付候选 | `739c08b77bf5fbf35641f310681e24eb79cdb726` | 50,928,777 | `c93d7a6f8d99cae19af27994b577073a85171db4c51ce3b7319086e60bd22e67` |

两份清单分别为 [candidate-r1.json](../reports/2026-10-16/annotations/candidate-r1.json) 与 [candidate-r2.json](../reports/2026-10-16/annotations/candidate-r2.json)，均记录 `source_dirty=false`。整理时已读取实际 ZIP，重新核对以上字节数和 SHA-256。候选路径分别为 `outputs/candidates/current/annotations-20261016-r1/qcblender-0.1.0.zip` 和 `outputs/candidates/current/annotations-20261016-r2/qcblender-0.1.0.zip`，不能仅按相同版本号区分。

r1 的真实 GUI 按原子编号、距离、键角、二面角顺序连续创建时，四条标注的 `decimals` 都为 4。键角文字为 `Angle(1,2,3) = 32.0524 °`，二面角文字为 `Dihedral(1,2,3,4) = 10.8606 °`，没有采用计划中的角度默认 2 位。见 [gui-created-four.json](../reports/2026-10-16/annotations/gui-created-four.json) 与 [失败弹窗截图](../reports/2026-10-16/annotations/gui-angle-default-failed.png)。科学数值本身没有变化，问题影响的是连续创建时默认显示精度。

提交 `9bbdc5b1b0179280688a84b3e7da6ea043b5c651` 为新建标注的 `decimals` 属性增加 `options={'SKIP_SAVE'}`，避免 Blender 的上次操作历史把距离的 4 位精度带入下一种标注。原先 `is_property_set(..., ghost=False)` 的判断不足以排除已继承的 RNA 属性。类型默认仍为原子/距离 4 位、键角/二面角 2 位；当前窗口中显式输入的小数位数继续生效。新增三个边界回归测试，计入 r2 的 92 项公开科学测试；它们不替代真实 GUI 复验。

r2 在独立 GUI 进程中再次按同一顺序实际点击并确认四次，快照精度为 **`[4,4,2,2]`**，键角和二面角分别显示 `32.05 °`、`10.86 °`。见 [gui-created-four-r2.json](../reports/2026-10-16/annotations/gui-created-four-r2.json)、[键角默认 2 位弹窗](../reports/2026-10-16/annotations/gui-angle-default-r2-passed.png) 和 [二面角默认 2 位弹窗](../reports/2026-10-16/annotations/gui-dihedral-default-r2-passed.png)。这项原失败路径现记为 `Passed`。

## 已确认行为

新标注默认黑色、Metallic=1；每条标注的文字、引线、距离虚线或圆弧共享本条材质，不同条独立。二面角两个真实三角面共享另一份初始 Alpha=0.2、Metallic=0 的材质。创建时可选颜色，后期编辑通过 Blender 材质节点完成；布局与构型更新保留共享、自定义节点材质。

默认前缀固定为 `Atom: `、`Distance(...) = `、`Angle(...) = `、`Dihedral(...) = `；中文、空串和空格自定义前缀原样保留，尾部继续追加科学值及单位。距离虚线为实段/间隔 1:1；角度圆弧以第二原子为圆心，二面角圆弧以第二、第三原子中点为圆心并垂直于中间轴。二面角面对应输入的 1–2–3 和 2–3–4 三原子。显示尺寸不修改源科学数组。

旧标注首次显式编辑补齐测量部件，保留已有材质。显式“统一标注材质”建立每条独立、组内共享的副本，并保留旧材质与节点为可保存备份；重复操作幂等。全部朝向相机仅旋转当前原子视图的文字，不继承上次单条 ID，不改变测量几何或其他原子视图。人工操作入口见 [分子与标注教程](../../human/topics/01-molecule-xyz.md#step-05)。

## 实际检查与候选边界

| 状态 | 候选与检查 | 证据及范围 |
| --- | --- | --- |
| Passed | r2：92 项 `public-core` 测试，零失败、零错误、零跳过 | [science-public-r2.json](../reports/2026-10-16/annotations/science-public-r2.json)，源码提交为 `739c08b`；含精度历史、几何及标注边界回归。 |
| Passed | r2：真实 bpy 标注几何、默认材质、前缀、编辑、复制/删除、显隐、相机朝向、旧标注与材质统一、自包含保存 | [geometry-r2/annotation-geometry.json](../reports/2026-10-16/annotations/geometry-r2/annotation-geometry.json)；从实际源坐标独立核对端点、半径、平面、三角网格及数组摘要。进程退出码为 0。 |
| Passed | r2：标注工程在新进程冷重开 | [geometry-r2/annotation-geometry-reopen.json](../reports/2026-10-16/annotations/geometry-r2/annotation-geometry-reopen.json)；核对记录、材质节点、字体、相对数据路径、数组及几何；记录的安装源码哈希与 r2 对应。 |
| Passed | r2：真实 GUI 连续创建四类标注恢复默认精度 | `gui-created-four-r2.json` 及上述两张弹窗截图；原子/距离/键角/二面角为 `[4,4,2,2]`。 |
| Passed | r2：隔离配置安装文件与候选 ZIP 全部成员相等 | [isolated-r2-install.json](../reports/2026-10-16/annotations/isolated-r2-install.json)；仅代表隔离安装，不能替代用户全局安装验收。 |
| Passed | r1：221 项标准库测试，零失败、零错误、零跳过 | [stdlib-r1.json](../reports/2026-10-16/annotations/stdlib-r1.json)，绑定 `69dd8ff`；没有改记为在 r2 全量重跑。 |
| Passed | r1：真实 XYZ、IRC、优化构型切换，四类标注随步更新 | [motion-r1/motion.json](../reports/2026-10-16/annotations/motion-r1/motion.json)；序列分别为 XYZ `1→2→3→1`、IRC `1→2→3→2`、优化 `1→4→2→1`。 |
| Passed | r1：共享原子/标注数据的切步拒绝、独立副本导航及保全 | [shared-mesh-r1/checks.json](../reports/2026-10-16/annotations/shared-mesh-r1/checks.json)；其保存工程另在 r2 环境冷读成功，见 [shared-mesh-r2-reopen.log](../reports/2026-10-16/annotations/shared-mesh-r2-reopen.log) 和同目录进程记录。目录名 `shared-mesh-r1` 不代表后续冷读使用的仍是 r1 安装。 |
| Passed | r1：68 个 Operator、217 个属性/上下文变体，每变体 8 种语言/开关组合；另 2 个工作区工具各 8 组合 | [operator-tooltips-r1.json](../reports/2026-10-16/annotations/operator-tooltips-r1.json)；实际安装的 RNA、注册描述回调及 `pgettext_tip` 检查，没有执行全部 Operator。界面翻译和工具提示翻译分别开关。 |
| Passed | r1：四类标注及中文前缀渲染、中文路径工程冷读和再渲染 | [gallery-readable-r1/render.json](../reports/2026-10-16/annotations/gallery-readable-r1/render.json)、[render-reopen.json](../reports/2026-10-16/annotations/gallery-readable-r1/render-reopen.json)、[visual-review.json](../reports/2026-10-16/annotations/gallery-readable-r1/visual-review.json)。Agent 查看了完整渲染 PNG；独立人工审阅仍为 `Not Run`。 |
| Passed | r1：冷读前后渲染像素一致 | [gallery-readable-r1/pixel-comparison.json](../reports/2026-10-16/annotations/gallery-readable-r1/pixel-comparison.json)：5,600,000 个通道，最大差 0、变化通道 0。两张 PNG 文件 SHA-256 不同，结论是解码像素一致，不是文件字节一致。 |
| Passed | r1：离线安装、真实 worker 导入与轨道求值、取消、缓存、相位/阈值、渲染、中文迁移冷读 | `outputs/runs/annotations-20261016/extension-r1/extension.json`；绑定 r1 ZIP 的 SHA-256。r2 独立重跑结果见下行。 |
| Passed | r1：旧工程冷载入保留对象、字体和材质；共享自定义材质可编辑；原磁盘文件未改 | [legacy-project-r1.json](../reports/2026-10-16/annotations/legacy-project-r1.json)，`material_users=2`；保全文件清单见 [preservation-files.json](../reports/2026-10-16/annotations/preservation-files.json)。 |
| Passed | r2 最终整包安装、worker、重建资产渲染及中文路径冷读 | `outputs/runs/annotations-20261016/extension-r2/extension.json`；候选 SHA-256 与 r2 一致，所有检查及 `cold_open` 均 Passed，两个进程均退出 0。 |
| Passed | r2 四类标注渲染、中文路径冷读与解码像素一致 | [gallery-r2/render.json](../reports/2026-10-16/annotations/gallery-r2/render.json)、[render-reopen.json](../reports/2026-10-16/annotations/gallery-r2/render-reopen.json)、[pixel-comparison.json](../reports/2026-10-16/annotations/gallery-r2/pixel-comparison.json)、[视觉检查](../reports/2026-10-16/annotations/gallery-r2/visual-review.json)；两图已由 Agent 查看，像素最大差 0。 |
| Passed | 用户全局插件、当前安装 ZIP 更新与逐成员核对，以及原工程/语言恢复 | [global-install.json](../reports/2026-10-16/annotations/global-install.json)、[current-install-receipt.json](../reports/2026-10-16/annotations/current-install-receipt.json)、[global-cold-background.json](../reports/2026-10-16/annotations/global-cold-background.json)、[global-cold-gui.json](../reports/2026-10-16/annotations/global-cold-gui.json)；对象、数组、节点、父子关系、字体、材质、偏好和原文件共 10 项核对全通过，GUI PID 59380 留开。 |
| Not Run | 独立人工操作、独立科研判断、远端 CI 和公开发布 | 自动化、Agent GUI 与渲染检查不替代这些验收。 |

`geometry-r2` 报告中的 GUI/Undo/Redo 和轨迹切换仍为 `Not Run`：这表示该脚本没有执行这些动作。本报告分别引用真实 GUI 快照和 `motion-r1` 支持对应结论，没有改写原报告的检查边界。全量工具提示的元数据检查也不等于逐个按钮真实悬停；实际 GUI 只进行了代表性的面板与悬停检查，截图为 `gui-panels-zh.png`、`gui-tooltip-zh.png`。

## r1 证据的复用依据与限制

实际对比两份候选的 `source_files`，96 个 Python 文件中 **95 个 SHA-256 相同**，唯一不同的是 `blender/annotations.py`：

- r1：`4555710d649756392e5242acd041b1a5c7daa32ffbd53c353f36c8b6cf8c6bfc`
- r2：`c2afe94ab2f2c9843c868ff91a7be27adb647b296efba7eb7350353327cb49f5`

产品源码 diff 仅为新建 `decimals` 属性增加 `SKIP_SAVE`。`annotation_geometry.py`、`measurements.py`、`blender/geometry.py`、`blender/trajectory.py`、`blender/irc.py`、`blender/optimization.py`、`blender/layers.py`、`blender/annotation_fonts.py`、`blender/editor_ui.py`、`blender/project.py`、翻译词表及 `i18n.py` 均与 r1 哈希相同；完整摘要保留在两份 candidate 清单中。

因此，r1 的数值定义、已有标注随步更新、工具提示文本、原工程保全等可作为未变实现的既有证据。标注模块的更新、材质、复制、删除和朝向逻辑在上述源码 diff 中未变；r2 仍重新执行了原生几何及冷读，受精度历史影响的 GUI 创建路径也单独重新执行。r1 的 GUI 材质统一及 Undo/Redo、中文编辑记录保留其 r1 身份，不表述成 r2 又完成了同一轮 GUI。

此外，两包各 119 个 ZIP 成员中 **115 个成员内容哈希相同**；除了标注 Python 模块，`assets/nodes.blend`、`assets/en_US/nodes.blend`、`assets/zh_HANS/nodes.blend` 的文件哈希也不同。源生成代码相同不证明这三个重建资产逐字节相同。因此 r2 独立重跑最终安装、worker、资产渲染与中文冷读，并重新渲染四类标注；结果见上表。

## GUI、保全及失败记录

旧版问题在保全件和受控测试对象上复现：材质有两个使用者时编辑报“标注材质必须独立且使用节点”，原工程磁盘文件未改，见 `baseline-repro.log`、`repro-material.json`。旧版在单条朝向操作后，未显式传 ID 的全部朝向仍带入上一条 ID，只匹配一个标签，见 `repro-face-single.json`、`repro-face-last-click.json`；这与候选修复后的当前视图作用域检查分别记录。

r1 实际 GUI 完成四类创建、二面角自定义前缀改为 `二面角：`，以及单条后全部朝向相机。`gui-face-single.json` 的朝向数组为 `[true,false,false,false]`，`gui-face-all.json` 为 `[true,true,true,true]`；两个快照的非文字 `parts` 记录完全相等，说明这次操作没有转动引线、虚线、圆弧或三角面。

材质统一 GUI 使用了明确记录的受控“旧引线不同材质”夹具，`gui-unify-setup.json` 标记 `deliberate_fixture=true`。预览显示待处理 1 条，见 `gui-unify-preview.png`。统一后同条材质归组；`gui-unify-before.json` 与 `gui-unify-undo.json` 整份 JSON 相等，`gui-unify-after.json` 与 `gui-unify-redo.json` 整份 JSON 相等，Undo/Redo 快照完整恢复。这是实际菜单操作的证据，独立于后台脚本中的幂等性检查。

创建后的 Undo 把四条变成三条；工具发送预期的 `Ctrl+Shift+Z` 后，快照反而从三条变成两条，表现为继续撤销。随后通过 Blender 的 **Edit → Redo** 菜单恢复四条，记录为 `gui-undo-create.json`、`gui-redo-create.json`、`gui-menu-redo-create.json`。没有把这次工具输入路径未实现预期 Redo 的结果归因为插件产品缺陷，也没有将它记录为快捷键 Redo 通过。

早期 `render-r1.log` 曾因验证场景缺少 XYZ 当前帧身份而失败，错误为 `XYZ atom view is missing its current frame identity`。补齐验收脚本的轨迹初始化后再执行成功；最终可读图使用 `gallery-readable-r1`，没有将失败运行或较早的图替换为最终成功证据。所有原始失败日志、r1 候选及修复前精度截图继续保留。

原工程保全副本位于 `outputs/projects/annotations-preserved-20261016/user-session.blend` 及同名 `.qcdata/`；`preservation-files.json` 记录 6 个文件的大小与 SHA-256，`preserved-baseline.json`、`preserved-extra-baseline.json` 保存对象、字体及材质基线。原工程冷载入与磁盘原件未变已由 `legacy-project-r1.json` 支持，最终全局安装后的后台与 GUI 冷读也已通过上述 10 项核对。可继续 GUI/渲染检查的自包含工程为 `validation/agent/reports/2026-10-16/annotations/geometry-r2/annotations.blend` 与 `validation/agent/reports/2026-10-16/annotations/gallery-r2/标注与中文.blend`；各自同名 `.qcdata/` 一起保留。

## 最终交付与 GUI 补充

r2 的原子、距离、键角编辑弹窗由原生 `INVOKE_DEFAULT` 打开，随后通过 Computer Use 实际点击显示开关及确定。分别关闭原子引线、距离虚线、键角引线；距离引线与键角圆弧仍保留。`gui-edits-r2.json` 记录实际结果，`gui-edit-undo-r2.json` 和 `gui-edit-redo-r2.json` 证明编辑可撤销、菜单重做后完整恢复。二面角中文编辑的完整 GUI 入口验证保留在 r1。

原工程的全局 GUI 已恢复，[截图](../reports/2026-10-16/annotations/final-user-gui.png)与冷读快照对应同一进程；磁盘原件未修改。当前安装身份、可重建入口、备份和本地归档由 [ARTIFACTS](../../../docs/ARTIFACTS.md#annotations-20261016)统一定位。旧候选及失败日志保留，未 push 或发布。
