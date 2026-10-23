# QCBlender 0.1.0 操作入口索引

适用 Windows x64、Blender 5.1.1。版本及安装包可用性见 [README](../README.md)，技术范围见 [验证记录](VALIDATION.md)。

安装、导入、渲染、导出与保存按 [人工 SOP](../validation/human/SOP.md) 执行。案例、截图和安装包集中在 [validation](../validation/README.md)，下面提供操作入口索引。

## 操作入口与对象选择

先切换物体模式，选中对应 QC 对象。每次换对象后，点击 **N 侧栏 → 当前 QC 对象 → 打开对象属性**，核对按钮旁的目标名。展开表中指定面板；按钮灰显时查看其下方原因。

`N 侧栏` 指 **3D Viewport → N → QCBlender**；`对象属性` 指 **Properties → Object → QCBlender · 对象与量子化学**。

| 操作 | 需要选中的对象 | 编辑器与面板路径 | 可见按钮或控件 |
| --- | --- | --- | --- |
| 导入计算结果 | 无 | N 侧栏 → 导入与导出 → 导入 | 导入 Gaussian / Cube / XYZ |
| 生成 MO、密度或 ESP | 含轨道的 FCHK 原子视图 | 对象属性 → 创建视图与工具 → 计算 | 生成量子化学场 |
| 查看能量、选择振动模式 | 含相应记录的原子视图 | 对象属性 → 科学记录与振动模式 | 能量列表、模式列表 |
| 振动显示参数 | 已选模式的原子视图 | 对象属性 → 高级参数 | Animate、Amplitude (angstrom)、Phase、Cycles per second |
| 原子电荷着色 | 含电荷记录且未绑定着色场的原子视图 | 对象属性 → 科学记录与振动模式 | 设置原子电荷着色 |
| 创建偶极 | 含偶极记录的原子视图 | 对象属性 → 创建视图与工具 → 空间工具 | 创建偶极矢量 |
| 声明 Cube 量与单位 | unknown_scalar 场视图 | 对象属性的 QCBlender 主面板 | 声明 Cube 物理量与单位 |
| 绑定或替换着色场 | 要着色的几何视图 | 对象属性 → 颜色映射 | 选择／替换着色场 |
| 应用色带预设、反转颜色 | 已有标量着色或电荷着色的 QC 表面、切片或原子视图 | Properties → Material → QCBlender · 节点材质 → Color map | 应用色带预设…；色带预设：QC Default / Viridis / Cividis；Reverse (0 or 1) |
| 创建切片、等值面或体积雾 | 有关联体场的标量视图 | 对象属性 → 创建视图与工具 → 空间工具（切片）／显示视图（等值面、体积雾） | 创建切片、创建等值面层、创建体积雾 |
| 采样线剖面数据 | 有关联体场的场视图或切片 | 对象属性 → 创建视图与工具 → 场值采样 | 记录剖面起点、采样线剖面数据 |
| 导出科学记录或当前视图摘要 | 含相应数据的原子、场或分析记录 | N 侧栏 → 导入与导出 → 导出 | 导出数据与参数摘要；数据（Data）选择当前视图参数摘要或IR/optimization/IRC/Mayer/profile/paired/ESP_AREA |
| 查看XYZ多帧 | XYZ多帧原子对象 | 对象属性 → XYZ Frames | Previous、Next、Choose XYZ Frame |
| Mayer 逐键着色 | 已导入 Mayer 结果的 IRC path 或其 Mayer 记录 | 对象属性 → IRC 路径 | 显示 Mayer 连线、Mayer 显示设置；整路径色域、手动范围、键级下限 |
| 局部选择、氢显隐 | 原子视图 | 对象属性 → 局部选择与标注 | 设置局部选择、隐藏氢等 |
| 创建标注、优化视图 | 原子视图；优化需有逐步数据 | 对象属性 → 局部选择与标注（标注）／Optimization Trajectory（优化视图） | 原子（Atoms）、距离（Distance）、角度（Angle）、二面角（Dihedral）；创建优化轨迹视图（Create Optimization View） |
| 查看来源 | 对应 QC 视图 | 对象属性的 QCBlender 主面板 | 来源详情、刷新来源、关联选中数据源 |
| 浏览外部结果 | 对应外部结果显示层 | 对象属性 → External Result Browser | 应用筛选、Apply Filter、Swap value columns |
| 管理显示层 | 对应 QC 显示层 | 对象属性 → 显示层管理 | 视口可见性、渲染可见性、复制、移除、上移、下移 |
| 复制显示参数 | 多选同类 QC 视图，最后选参数来源 | 3D Viewport → 对象右键菜单 → QCBlender | 复制显示参数到选中视图 |
| 创建相机 | 选中需要出图的 QC 视图 | 对象属性 → 创建视图与工具 → 相机 | 创建取景相机 |
| 保存与归档 | 已打开的 QC 工程 | N 侧栏 → 工程与维护 → 保存与归档 | 保存自包含工程、归档工程 |
| 恢复显示缓存或数据路径 | 受影响的 QC 视图 | N 侧栏 → 工程与维护 → 恢复与维护 | 重建显示缓存、重新定位数据 |

界面名称随 Blender 所选语言显示；中英文对照见 [人工 SOP](../validation/human/SOP.md)。后文英文名称用于辨认控件或日志。

<details>
<summary>了解编号边界、NOCV 与 NBO 记录选择</summary>

轨道编号按当前自旋的源轨道数限制，步、帧、原子和记录行按当前数据限制；输入超过范围时回到对应边界。NOCV Pair number 从该自旋实际存在的源编号中选择。NBO 记录先选择日志并确认检查，随后在第二个对话框选择 Gaussian job 和 NBO block；更换 Job 会同步更新 block 的范围。

</details>

## 按任务进入教程

| 任务 | 教程位置 |
| --- | --- |
| 安装、对象/编辑器选择、第一张 MO 图 | [入门主流程](../validation/human/SOP.md) |
| 能量、振动、优化与 NBO | [本机限定案例](../validation/agent/LOCAL-CASES.md) |
| Cube 单位、双符号、多场叠加与跨场着色 | [Cube 专题](../validation/human/topics/02-cube.md) |
| 密度、ESP、电荷/偶极、图例和色带预设 | [电子分布专题](../validation/human/topics/03-density-esp.md) |
| 切片、探针、剖面 CSV、裁剪和体积雾 | [空间观察专题](../validation/human/topics/04-spatial-tools.md) |
| 氢显隐、局部选择、标注、显示层、XYZ 与参数复制 | [分子显示专题](../validation/human/topics/01-molecule-xyz.md) |
| IGMH/IRI | [成对场专题](../validation/human/topics/05-igmh-iri.md) |
| ESP 极值、面积和 AIM | [点、路径和分析记录](../validation/human/topics/06-esp-aim.md) |
| IRC/Mayer | [反应路径专题](../validation/human/topics/07-irc-mayer.md) |
| ETS-NOCV 和 pair Cube | [NOCV 专题](../validation/human/topics/08-ets-nocv.md) |
| 公共几何节点 | [节点专题](../validation/human/topics/09-nodes.md) |
| 取景、渲染、参数摘要和保存重开 | [导出与保存](../validation/human/SOP.md#export) |
| 错误输入、筛选/取消、关联、恢复等技术边界 | [Agent 检查覆盖](../validation/agent/COVERAGE.md) |

保存使用 **N 侧栏 → 工程与维护 → 保存与归档 → 保存自包含工程**，并将同名 `.blend` 与 `.qcdata/` 一起移动。

<details>
<summary>了解科学值、源编号与显示参数</summary>

源文件始终决定科学值和单位，显示操作不改科学数组。源编号从1起，坐标Å；普通几何键由距离推断，Mayer 连线来自导入的计算原子对。MO两符号表示相位，振动播放速度属于显示参数。两个来源关联、Cube单位声明、外部分析参数均须核对真实生成记录。

</details>

## 色带预设与多场显示

按 [色带预设步骤](../validation/human/topics/03-density-esp.md#presets)选择预设、确认应用，并练习反转、取消、撤销和重做。需要独立配色时，先在 **对象属性 → 显示层管理 → 复制（Duplicate）** 创建展示副本。

<details>
<summary>了解共享材质、预设保留项与目标限制</summary>

对话框显示目标材质，并说明共享它的视图会同步更新。需要独立配色时，先在 **对象属性 → 显示层管理 → 复制（Duplicate）** 创建展示副本。预设用于标准标量/电荷着色；自定义图无法确认目标、目标只读或对话框打开后目标改变时，操作会报告原因，重新选择有效目标后再打开对话框。

在 **Properties → Material → QCBlender · 节点材质** 的 **Color map** 下点击 **应用色带预设…**，选择 **QC Default、Viridis 或 Cividis**，确认后替换当前材质的色阶与插值；选择菜单选项时尚未应用，取消保留原色带。**Reverse (0 or 1)** 独立控制反转。应用预设保留数值范围、中心值、反转值、透明度与图例布局；表面和图例使用同一材质。操作可通过 Blender 的 **Edit → Undo / Redo** 撤销或恢复。

</details>

多份 Cube 可以在同一场景各自生成表面，分别调整阈值与视口/渲染可见性；同构型示例见 [多 Cube 叠加](../validation/human/topics/02-cube.md#overlay)。把第二个场用于第一表面的着色，另用 **选择／替换着色场**。源文件的物理量与单位分别保留。

原子选择与标注始终使用源原子编号。

<details>
<summary>了解多场显示与源原子属性</summary>

球棍求值后，一个原子会生成多个球面顶点；求值网格的顶点行号不能当作源原子编号，球面位置也不是核位置。源 POINT 属性、缺失属性和有效标志的读法见 [节点专题](../validation/human/topics/09-nodes.md#attributes)。

</details>

## 当前步骤关联与共享对象

IRC和优化关联比较双方当前步骤的源Å坐标。最后选择的对象作为活动参考；在对象属性主面板点击 **关联选中数据源**。任一端换步后，来源详情中的Geometry association显示stale；返回原步仍需重新关联。旧工程关联、复制层和当前版本新视图也需重新建立关联。

原生Alt+D产生的共享原子mesh不能切换IRC/优化步骤。仅选要独立调整的副本，使用 **3D Viewport → Object → Relations → Make Single User → Object & Data**，再点击对应面板的Previous/Next/Choose Step。选择顺序、关联失效、单用户恢复和Undo/Redo检查见[Agent 覆盖](../validation/agent/COVERAGE.md)。

## Gaussian 优化轨迹浏览

按 [本机限定案例](../validation/agent/LOCAL-CASES.md)导入 P02 的 Job1，在 **对象属性 → Optimization Trajectory** 点击 **创建优化轨迹视图（Create Optimization View）**。选中新轨迹对象并重新打开对象属性，使用 **Previous / Next / Choose Step** 切步。Job2 的模式和能量在 **科学记录与振动模式**。

<details>
<summary>查阅新建视图默认值与导出目录规则</summary>

新建原子显示外层Quality=3，新建切片每轴201点；生成网格初值0.2 Å、边缘3 Å、512 MiB。公共QC Style Atoms and Bonds的Quality=2、QC Planar Slice的Resolution=101仍保留。Addon偏好“数据导出目录”留空时使用已保存.blend父目录，否则真实系统Documents；导出对话框Output directory可单次覆盖。导出目录不替代.qcdata工程数据。

</details>

## Alpha 首次出图与资源检查

按 [人工主流程](../validation/human/SOP.md#orbital) 完成 P01、Alpha 源 MO9、0.2 Å / margin 3 Å / 512 MiB、等值 0.045 bohr^-3/2 的路线。

<details>
<summary>了解首次预检与资源预算</summary>

首次点击生成先异步科学预检，通过后打开参数对话框；网格、结果大小和求值预算即时更新，超限显示原因。资格绑定源 manifest 与科学指纹，重绑或新进程重开后重新检查。

</details>

选最终视图，在“N 侧栏 → 导入与导出 → 导出 → 导出数据与参数摘要”选择“当前视图参数摘要”，得到中文 view-summary.md 与 metadata.json。

<details>
<summary>了解参数摘要的可核实范围</summary>

摘要读取当前节点和材质，无法核实的自定义图和缺字段显示 partial/unverified。源科学数组、现有 CSV 数据格式不变。

</details>
