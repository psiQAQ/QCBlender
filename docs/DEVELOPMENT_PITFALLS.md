# 开发问题与复验记录

仅记录实际观察到的问题。每条保留触发条件、原因证据、处理及复验状态；未验证的解释不作为结论。

## 2026-09-28：Properties 与真实重绘验收

- 注册扩展时 `bpy.data` 可能为 `_RestrictData`，来源缓存初始化需延迟到 timer；load/save handler 仍按保存身份刷新。独立安装和移动冷重开 Passed。
- 固定对象需要设置 `pin_id` 和 `use_pin_id`；Properties 上下文在可见窗口重绘后更新。后台 `temp_override` 不能替代这项验证。前台重绘与固定对象检查 Passed。
- 验收时临时替换已注册 Panel.draw 后调用 redraw_timer，Blender 5.1.1 发生 python313.dll 访问异常。改用 `sys.setprofile` 只读观察实际 draw，保留科学数组读取拦截后，同一重绘通过。证据保存在 `outputs/multiwfn-parameters/01-foundation-r4/`。
- GUI 撤销后修改样式，节点值和已求值网格已变化，视口仍保留旧几何；显式调用显示载体 `Mesh.update()` 后更新正确。样式操作补齐该刷新，最终候选复验待完成；科学数组不参与此更新。

## 2026-09-27：SOP 复跑缺陷

| 编号 | 触发与原因 | 修复及复验 |
| --- | --- | --- |
| UI-01 | 默认窄侧栏的显示层按钮被固定 `ui_units_x` 裁切 | 取消固定布局宽度；新进程默认侧栏 GUI 确认 Passed |
| UI-02 | `add_legend` 用材质输出变量覆盖几何输出，连接 Geometry 时抛出 KeyError | 分开变量；中文图例回归、GUI Map Colors、Charge/Slice 复验 Passed |
| PORT-01 | VDB 绝对路径令移动后的工程继续依赖原目录 | 保存相对路径并刷新体积缓存；首次保存、Save As、失败回滚及移动冷重开 Passed |
| ESP-01 | Multiwfn 最大/最小值各自从 1 编号，全局 serial 去重误拒绝真实输出 | 按 `(kind, serial)` 去重；同类重复仍拒绝，真实 19 点导入及 GUI 重试 Passed |

固定候选、逐例结果及原始日志见 [Agent 技术复跑记录](v1-acceptance/AGENT-REPLAY.md)。独立人工验收由 SOP 单独记录。

## 2026-09-23：Blender 5.1 视频输出设置

- 触发：48 帧振动 PNG 已输出，设置 `image_settings.file_format = 'FFMPEG'` 时抛出枚举错误。
- 原因证据：当前 RNA 提供 `image_settings.media_type`，旧图像格式枚举不含 FFMPEG；编译选项支持 FFmpeg。
- 处理：设置 `media_type = 'VIDEO'`，再配置 `render.ffmpeg` 的 MPEG4/H264；编码后恢复 IMAGE。
- 复验：原生序列编辑器成功编码 48 帧 MP4；新进程重新解码，帧数 48。见 `tools/verify_complex_examples.py`。

## 2026-09-23：NCIPLOT Cube 的量名与倍率

- 触发：对照 ChemTools 水二聚体 `dens.cube` 与波函数求值，数值相差约 100 倍；RDG 文件部分点为 100。
- 原因证据：密度参考实际为 100×sign(λ₂)ρ；457 个 RDG 点是过滤哨兵，不能当作未过滤物理值。
- 处理：仅在案例参考比较中去除倍率、排除哨兵；新生成文件显式保存单位及过滤条件，插件普通 Cube 导入继续要求声明量名。
- 复验：带符号密度最大绝对差 4.71e-6 electron/bohr³，未过滤 RDG 最大差 5.02e-5；导数差分及 Cube 往返通过。

## 2026-09-23：科学场演示的照明与文字可读性

- 触发：Standard 色彩管理下过强面积光令电荷颜色接近白色；普通文字材质也出现高光，图注局部难辨。
- 处理：案例使用较低照明强度、独立相机背景和不受光照影响的图注材质；偶极显示缩放明确标注，IR 保留其选中峰颜色属性。
- 复验：检查真实 PNG，ESP 正负区域、电荷渐变、偶极箭头和 IR 峰可辨；不改动科学值或插件默认材质。

## 2026-09-23：表面着色会覆盖相位材质的不透明度

- 静态发现：独立色场映射替换表面材质，原相位材质 Alpha 不再参与渲染。
- 处理：正负分支用公开 Opacity 插槽保存 `qc_opacity` 属性，映射材质读取该属性；无属性的原子和切片默认不透明。更新公共资产版本，避免已保存旧接口被隐式复用。
- 复验：`verify_composable.py` 在实际几何上验证映射后负相位 .25、正相位 1，Passed。

## 2026-09-23：Blender 内置字体依赖关系警告

- 触发：带几何节点图例的工程冷重开或 GUI 撤销，Blender 5.1.1 输出 `Failed to add relation VFont -> Node`。
- 当前证据：冷重开采样、图例范围、实际渲染和 GUI 撤销通过；已查看 `cold-density-esp.png`，图例文字可见。
- 状态：保留为宿主警告，根因未确认；不将无可见失败等同于已修复，也不屏蔽日志。

## 2026-09-23：节点拆分后振动箭头仍查找内部节点

- 触发：新版原子样式下导入包含振动的 Gaussian 日志，`verify_animation.py`。
- 现象：`add_mode_vectors` 查找顶层 `GeometryNodeDeleteGeometry` 抛出 `StopIteration`；节点已经封装在公共样式中。
- 处理：箭头改从公共原子样式的 Geometry / Selection 输入取得同一份变形后的原子几何及选择，叠加非零向量选择。
- 复验：真实水分子振动/IR、四帧动画与新进程冷重开 Passed；显示层复制检查另列任务证据。后续节点拆分须搜索所有调用方的节点类型查找，不只检查修改器顺序。

## 2026-09-23：blender-mcp 启动器无法解析路径

- 触发：受限执行环境运行 `blender-mcp --help`。
- 现象：`uv trampoline failed to canonicalize script path`；读取用户 uv 工具目录同时返回 Access denied。
- 处理：通过审批在沙箱外只运行同一个 `--help`，没有重装依赖或修改用户环境。
- 复验：Passed，退出码 0；随后 MCP 只读查询返回 Windows、Blender 5.1.1 和真实可执行路径。
- 后续检查：先区分沙箱文件访问限制和真正的安装损坏，避免因启动器消息直接重装。

## 2026-09-23：复用旧验收工程时 manifest 无法读取

- 触发：隔离配置 `outputs/blender-m7` 中运行 `verify_extension.py`，将相同科学数据保存至既有 `outputs/acceptance/mo8.qcdata`。
- 现象：`copy_dataset` 读取既有 manifest 返回 `PermissionError`。导入、求值及缓存检查已执行，保存未完成。
- 处理：不修改数据或 ACL，通过审批在沙箱外运行相同验收命令。
- 复验：Passed，离线安装、保存、节点资产往返及新进程冷重开均通过。此例支持沙箱访问限制的解释，不将其归为科学数据损坏。

- 后续发现：旧 `visual-acceptance` 和 `animation-acceptance` 内另有 manifest 在沙箱外仍不可读，不能将所有 PermissionError 归为同一原因。本轮使用独立 `visual-acceptance-v2`、`animation-acceptance-v2` 保存新验收，保留原文件及 ACL；不吞掉保存错误。新目录的保存与冷重开已独立验证 Passed。

## 2026-09-23：显示控制依赖第一个修改器

- 发现方式：源码审查，标量映射、原子电荷及振动代码直接访问 `obj.modifiers[0]`。用户调整修改器顺序后可能访问其他修改器。
- 处理：统一通过 QC 图标识查找；旧图只接受唯一可辨识的 QC 修改器，歧义时返回明确错误。
- 复验：`tools/verify_composable.py` 在真实 Blender 5.1.1 中将无关 Bevel 修改器移至首位，验证仍定位原 QC 图，Passed；旧工程完整回归另行执行。

## 2026-09-23：元素表包含非元素占位记录

- 触发：从 MolecularNodes `assets/data.py` 提取范德华半径，直接读取每条记录的 `vdw_radii`。
- 现象：`KeyError: 'vdw_radii'`；并非所有记录具有半径字段。
- 处理及复验：仅提取实际提供正半径的条目，单位从 pm 转为 angstrom；生成 103 条并验证碳空间填充半径。不为缺失半径编造科学值。
