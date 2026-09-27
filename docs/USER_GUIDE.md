# QCBlender 0.0.1 操作指南

适用 Windows x64、Blender 5.1.1。此版本为本地验收候选，支持范围见 [验收记录](VALIDATION.md)。安装包包含解析及求值依赖，可断网安装和运行。

## 安装与首次导入

1. 在 Blender Preferences → Get Extensions 的菜单中选择 **Install from Disk**，安装 `outputs/dist/qcblender-0.0.1.zip` 并启用。
2. 在 Add-ons 中展开 QCBlender，可用 **Check Scientific Runtime** 检查随包组件。
3. 在 3D Viewport 按 N 打开侧栏，选择 **QCBlender → Import**。导入 `.fchk/.fch`、`.cube/.cub` 或 Gaussian `.log/.out`。
4. 结果浏览开发候选中的 Log/Out 导入先异步显示 **Choose Gaussian Calculation**。选择计算段，核对 route、终止状态、原文行区间、能量和显式几何提示，再确认导入；取消不会创建科学 Dataset 或场景对象。预览后源文件改变时须重新预览。优化后频率计算通常属于另一个 Link1 job，应选择包含频率的段；缺少显式几何时不从其他段继承。脚本/MCP 的 `job_number` 仍从 1 开始，worker 的 `job_index` 从 0 开始。优化轨迹开发候选在导入后提供独立逐步视图，见下文；外部 IRC FCHK 序列入口见[导入说明](EXTERNAL_ANALYSIS_IMPORT.md)。

结果浏览功能使用独立候选 `outputs/result-browser/dist/qcblender-0.0.1.zip`，技术证据见[结果浏览验收记录](RESULT_BROWSER.md)。固定 SOP 包 `outputs/dist/qcblender-0.0.1.zip` 继续保留原段号导入流程。

坐标统一为 Å，1 Blender 单位表示 1 Å。原子之间的连线由元素半径和距离推断，不代表计算所得键级。原始电荷、坐标、轨道和场保存在科学数据中；对象移动和节点样式不会修改它们。

`.chk` 不能直接读取。在已有 Gaussian 的机器上执行 `formchk calculation.chk calculation.fchk`，再导入生成的 FCHK。本扩展不提供 Gaussian 可执行文件。

## 轨道、电子密度与 ESP

选择 FCHK 原子对象，点击 **Generate Field**。选择 Molecular orbital、Electron density、Alpha/Beta density、Spin density 或 Electrostatic potential。

MO 可按 Alpha/Beta 通道选择 HOMO、LUMO 或从 1 开始的源编号；对话框显示占据数和轨道能量。HOMO/LUMO 按该通道的真实占据和能量选择，缺少能量时使用明确源编号。简并子空间的轨道形状不唯一，不能仅凭图形不同断言计算不同。

网格间距与边缘宽度使用 Å。建议先用默认 0.2 Å 间距预览，再同时检查更细间距和更大空间范围。Memory budget 约束数值数组估计，不是整个 Blender 进程的硬内存上限。大网格，尤其 ESP，可能耗时较长；侧栏显示阶段和进度，Esc 取消当前操作。

生成后，侧栏和 Geometry Nodes 修改器共享参数：**Isovalue** 为物理场阈值，**Positive/Negative Phase** 分别控制蓝色正面和红色负面，**Smooth Normals** 只改变法线着色。阈值、颜色和法线调整不重新求值；改变 MO 或网格需要重新 Generate Field。

| 量 | 数值单位 |
| --- | --- |
| MO 振幅 | bohr^-3/2 |
| 总/Alpha/Beta/自旋电子数密度 | electron/bohr^3 |
| ESP | hartree/e |
| 轨道和电子总能量 | Hartree |

ESP 来自核与电子密度库仑势；距核小于 0.02 bohr 的点标为无效。无效掩码不是物理零值。振动仅移动分子显示，静态 MO/密度不随之变形成时变波函数。

## Cube、双场颜色和切片

多 MO Cube 保留各数据集编号。普通 Cube 的数值类型不能仅从文件名或注释确定，因此初始显示 `unknown_scalar` / `unknown`。核对生成程序和单位后，可选场对象点击 **Identify Cube**，显式声明物理量及其已有原子单位；操作记录为用户标注，**不换算数值**。其他单位的场须先正确转换。

生成同一 FCHK 的电子密度和 ESP 后，先选 ESP 表面，再 Shift 选密度表面，使密度成为活动对象，点击 **Map Colors**。密度定义表面形状，ESP 定义颜色；隐藏 ESP 表面即可保留单个成图表面。不要删除其隐藏的 volume 数据对象。

**Color Minimum / Center / Maximum** 应严格递增。默认红→白→蓝，中心对应白色；**Show Legend** 和 **Legend Position** 控制与实际范围联动的图例。紫红色表示采样超出有效域。原生材质可继续编辑；为科学比较应记录范围、颜色方案和 Blender 的色彩管理设置。

选择场对象，点击 **Slice** 创建切片，可调中心、旋转、尺寸和分辨率。场坐标及对象相对变换由节点处理。整体移动数据及其视图时优先移动原子父对象。

两个来源需先检查原子顺序和构型。选两个原子对象，最后选参考对象，点击 **Associate**；需要时启用刚体旋转/平移。线性或单中心结构无法唯一确定轨道方向，因此不自动刚体配准。关联保留各来源自己的能量和性质，不据几何相同推断理论层次相同。

## 电荷、偶极、能量和振动

原子对象上的 **Charge** 只列出实际读到的布居方法；电荷值以电子电荷单位显示。**Dipole** 显示物理偶极矢量，节点的 Angstrom per Debye 仅为箭头显示比例。**Distance** 使用源原子编号和原始平衡构型测距，结果为 Å；不测动画瞬时距离。

侧栏能量列表保留方法、总量/校正类型、来源位置和角色。MP2、CCSD(T)、DSDPBEP86、具备明确选态标记的 TD 输出分别保留目标值与参考 SCF；热校正、ZPE、焓和自由能单列。只有正常终止且目标唯一时自动选择。多个计算步、正文/archive 冲突或尚未验证的方法显示候选/诊断，不自动选最后一条 SCF。

频率 job 导入后在 **Vibration / IR** 列表选择模式，IR 棒状图同步突出显示。**Animate** 开启动画，**Amplitude (angstrom)** 控制最大原子显示位移，**Phase** 控制相位，**Cycles per second** 控制播放速度。位移来自真实正常模式；每个模式统一归一化到最大原子位移为 1 后供显示。播放速度不是物理振动频率，源频率始终以 cm^-1 保留。**Show Displacement Vectors** 显示位移方向/幅度；负频率标注 imaginary。

## Gaussian 优化轨迹浏览

使用[优化轨迹独立候选](OPTIMIZATION_TRAJECTORY.md)，导入含 `Opt` 的 Log/Out 并选择计算段。选中原子视图，在 **Optimization Trajectory → Create Optimization View** 创建位于原视图旁边的独立视图。通过 **Previous / Next / Choose Step** 切换，查看步号、该步能量、计算终止状态、收敛数值/阈值及原文位置。**Source Details → Optimization step** 保留当前步的完整记录。

坐标为 Å，能量为 Hartree；收敛表保留 Gaussian 打印的内部单位声明，不按显示坐标单位换算。缺失或歧义能量明确显示状态；失败或截断日志只能浏览具有明确步号和构型的已有记录。扫描、重启、QST2/QST3 和复合路径当前显示不可用及原因；普通导入仍保留原行为。

优化步是离散迭代，不代表物理时间。轨迹视图不携带最终构型的电荷、偶极、振动或空间场，原视图保留这些已核实的属性。默认空间填充显示；若改用球棍，键连接是第 1 步推断的固定显示连接，不是逐步键级。复制后可独立切步，保存和搬移方式与其他 QC 工程相同。旧工程没有逐步数组时，需要从原始 Log/Out 重新导入。

## 保存、移动与导出

结果浏览开发候选的 **Display Layers** 按源文件 SHA-256 和计算段分组。选择显示层后点击 **Source Details**，通过 **Source record** 分别查看几何来源、计算段、场量及单位、着色来源和外部分析关联。详情只读；计算段编号从 1 开始，完整摘要用于区分同名文件。IR 谱图和偶极沿其父原子对象读取来源。

**Refresh Sources** 按需刷新关联数据的 metadata。旧工程刷新前可能显示“未记录”并保守分组；没有记录的信息不作推断，缺失或损坏的关联显示错误。刷新与查看详情不加载科学数组；显示层的复制、显隐、排序和节点编辑继续使用原有操作。

使用 **Save Portable QC Project** 保存 `.blend` 和同名 `.qcdata/`。两者必须一起移动。`.qcdata` 包含数值数组、来源/单位和可重建的 VDB 显示缓存；`.blend` 保存节点、材质、选择和动画设置。

**Package QC Project** 打包磁盘上最近保存的工程；先保存最新修改，再打包。接收者解压整个 ZIP 后打开 `.blend`。仅使用 Blender 默认保存，可能仍引用扩展任务目录；正式交付前使用 QCBlender 的配套保存。

缺少 VDB 时选择受影响对象，使用 **Rebuild Volume Cache**；若整个数据目录移动，使用 **Relocate Scientific Dataset** 选择相同数据集的 `manifest.json`，内容摘要必须匹配。科学数组丢失时无法从表面网格恢复波函数。

设置 Blender 相机、灯光和输出后，使用原生 **Render Image** 或 **Render Animation**。推荐动画输出 PNG 序列，保留项目作为可编辑来源。图注应记录计算方法/基组、源文件摘要、场量/单位、MO 编号和自旋、网格/等值、色标；振动另记模式频率、显示振幅和非物理播放速度。这些值分别在侧栏、修改器和 `.qcdata` manifest 中保存。

缓存位于此扩展的用户数据目录 `jobs/`。当前不自动清理。清理前保存所有需要的配套工程、确认无正在运行的 QC 任务，再处理不再需要的任务目录；不在使用中卸载或移动其文件。
