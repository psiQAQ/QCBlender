# QCBlender 0.1.0 操作入口索引

适用 Windows x64、Blender 5.1.1。版本及安装包可用性见 [README](../README.md)，技术范围见 [验证记录](VALIDATION.md)。

安装、样本获取、参数核对、渲染、保存和独立复做统一按 [跟随教程与独立人工验收 SOP](v1-acceptance/SOP.md) 执行。下面只保留入口索引；详细步骤和结果填写均在同一份 SOP。

## 操作入口与对象选择

以下使用插件实际绘制的按钮文字。`N 侧栏` 指 3D Viewport → N → QCBlender；`对象属性` 指 Properties → Object → **QCBlender · 对象与量子化学**。多数子面板默认折叠，需要展开。先切换物体模式并选中对应 QC 对象；按钮灰显时查看其下方原因。对象属性固定了其他对象时，先解除固定或改为当前对象。

| 操作 | 需要选中的对象 | 编辑器与面板路径 | 可见按钮或控件 |
| --- | --- | --- | --- |
| 导入计算结果 | 无 | N 侧栏 → 工作流 | 导入 Gaussian / Cube / XYZ |
| 生成 MO、密度或 ESP | 含轨道的 FCHK 原子视图 | N 侧栏 → 工作流 | 生成量子化学场 |
| 查看能量、选择振动模式 | 含相应记录的原子视图 | 对象属性 → 科学记录与振动模式 | 能量列表、模式列表 |
| 振动显示参数 | 已选模式的原子视图 | 对象属性 → 高级参数 | Animate、Amplitude (angstrom)、Phase、Cycles per second |
| 原子电荷着色 | 含电荷记录且未绑定着色场的原子视图 | 对象属性 → 科学记录与振动模式 | 设置原子电荷着色 |
| 创建偶极 | 含偶极记录的原子视图 | N 侧栏 → 创建视图与检查工具 | 创建偶极矢量 |
| 声明 Cube 量与单位 | unknown_scalar 场视图 | 对象属性的 QCBlender 主面板 | 声明 Cube 物理量与单位 |
| 绑定或替换着色场 | 要着色的几何视图 | 对象属性 → 颜色映射 | 选择／替换着色场 |
| 创建切片、等值面或体积雾 | 有关联体场的标量视图 | N 侧栏 → 创建视图与检查工具 | 创建切片、创建等值面层、创建体积雾 |
| 采样线剖面数据 | 有关联体场的场视图或切片 | N侧栏 → 创建视图与检查工具 | 记录剖面起点、采样线剖面数据 |
| 导出科学记录或当前视图摘要 | 含相应数据的原子、场或分析记录 | N侧栏 → 工程与诊断 | 导出数据与参数摘要；数据（Data）选择当前视图参数摘要或IR/optimization/IRC/Mayer/profile/paired/ESP_AREA |
| 查看XYZ多帧 | XYZ多帧原子对象 | Properties → QCBlender → XYZ Frames | Previous、Next、Choose XYZ Frame |
| 局部选择、氢显隐 | 原子视图 | 对象属性 → 局部选择与标注 | 设置局部选择、隐藏氢等 |
| 创建标注、优化视图 | 原子视图；优化需有逐步数据 | N 侧栏 → 创建视图与检查工具 | 创建编号／距离／角度／二面角标注、创建优化轨迹视图 |
| 查看来源 | 对应 QC 视图 | 对象属性的 QCBlender 主面板 | 来源详情、刷新来源、关联选中数据源 |
| 浏览外部结果 | 对应外部结果显示层 | 对象属性 → External Result Browser | 应用筛选、Apply Filter、Swap value columns |
| 管理显示层 | 对应 QC 显示层 | N 侧栏 → Display Layers | 显隐、复制、排序、删除图标；查看对象属性 |
| 复制显示参数 | 多选同类 QC 视图，最后选参数来源 | 3D Viewport → 对象右键菜单 → QCBlender | 复制显示参数到选中视图 |
| 创建相机 | 选中需要出图的 QC 视图 | N 侧栏 → 创建视图与检查工具 | 创建取景相机 |
| 保存与归档 | 已打开的 QC 工程 | N 侧栏 → 工程与诊断 | 保存自包含工程、归档工程 |
| 恢复显示缓存或数据路径 | 受影响的 QC 视图 | N 侧栏 → 工程与诊断 | 重建显示缓存、重新定位数据 |

对话框、属性和部分专项面板仍使用英文名称；以表中入口进入后再调整这些控件。后文括号中的英文操作名称仅辅助辨认搜索或日志，不代表侧栏按钮文字。

## 按任务进入教程

| 任务 | 教程位置 |
| --- | --- |
| 安装、文件摘要、对象/编辑器选择 | [准备与通用操作](v1-acceptance/SOP.md#0-准备安装与通用操作) |
| MO、开壳层密度、裁剪和体积雾 | [C01](v1-acceptance/SOP.md#c01-fchk开壳层轨道与密度) |
| 能量、振动、优化与Log后FCHK导入 | [C02](v1-acceptance/SOP.md#c02-logout-能量振动与优化) |
| Cube单位、别名及双符号 | [C03](v1-acceptance/SOP.md#c03-cubecub-物理量网格与双符号) |
| ESP、电荷/偶极、色标、切片、探针、剖面和CSV | [C04](v1-acceptance/SOP.md#c04-esp电荷偶极切片探针与剖面) |
| 氢、局部集合、标注、显示层和参数复制 | [C05](v1-acceptance/SOP.md#c05-氢显隐局部选择标注与显示层) |
| NBO、IGMH/IRI、ESP分析、AIM、IRC/Mayer、ETS-NOCV | [C06–C13](v1-acceptance/SOP.md#c06-nbo-与-e2)；格式说明见 [外部分析导入](EXTERNAL_ANALYSIS_IMPORT.md) |
| 取景、渲染、保存、搬移、归档与恢复 | [每例出图与保存](v1-acceptance/SOP.md#04-相机渲染保存与移动冷重开每例执行) |
| 节点、材质与交互覆盖 | [N01–N18](v1-acceptance/SOP.md#2-n01n18-节点与交互检查) |
| 标准XYZ、离散帧、测量与独立副本 | [X01](v1-acceptance/SOP.md#x01-标准xyz与离散帧) |
| CSV/metadata、默认目录、筛选与取消 | [通用数据导出](v1-acceptance/SOP.md#05-显式数据导出) |
| 用户截图、Agent点击/数据核对和独立科研签署 | [结果记录](v1-acceptance/SOP.md#3-结果记录与独立科研签署) |

源文件始终决定科学值和单位，显示操作不改科学数组。源编号从1起，坐标Å；键由距离推断，MO两符号表示相位，振动播放速度属于显示参数。两个来源关联、Cube单位声明、外部分析参数均须核对真实生成记录。保存使用 **N侧栏 → 工程与诊断 → 保存自包含工程**，并将同名 `.blend` 与 `.qcdata/` 一起移动。

## 当前步骤关联与共享对象

IRC和优化关联比较双方当前步骤的源Å坐标。最后选择的对象作为活动参考；在对象属性主面板点击 **关联选中数据源**。任一端换步后，来源详情中的Geometry association显示stale；返回原步仍需重新关联。旧工程关联、复制层和当前版本新视图也需重新建立关联。

原生Alt+D产生的共享原子mesh不能切换IRC/优化步骤。仅选要独立调整的副本，使用 **3D Viewport → Object → Relations → Make Single User → Object & Data**，再点击对应面板的Previous/Next/Choose Step。逐步截图和Undo/Redo验收见[当前构型复做](acceptance/audit-p1-validation.md#原生入口复做)。

## Gaussian 优化轨迹浏览

操作步骤集中在 [SOP C02](v1-acceptance/SOP.md#c02-logout-能量振动与优化)：导入P02的Job1、创建独立轨迹，选新对象后在对象属性 **Optimization Trajectory** 使用 **Previous / Next / Choose Step**。Job2的模式/能量在 **科学记录与振动模式**。轨迹源值、截图和复做记录统一填写在C02。

新建原子显示外层Quality=3，新建切片每轴201点；生成网格初值0.2 Å、边缘3 Å、512 MiB。公共QC Style Atoms and Bonds的Quality=2、QC Planar Slice的Resolution=101仍保留。Addon偏好“数据导出目录”留空时使用已保存.blend父目录，否则真实系统Documents；导出对话框Output directory可单次覆盖。导出目录不替代.qcdata工程数据。

## Alpha 首次出图与资源检查

按 [Alpha 短 SOP](v1-acceptance/SOP.md#alpha-首次出图与短验收) 完成 P01、Alpha 源 MO9、0.2 Å / margin 3 Å / 512 MiB、等值 0.045 bohr^-3/2 的路线。首次点击生成先异步科学预检，通过后打开参数对话框；网格、结果大小和求值预算即时更新，超限显示原因。资格绑定源 manifest 与科学指纹，重绑或新进程重开后重新检查。

选最终视图，在“工程与诊断 → 导出数据与参数摘要”选择“当前视图参数摘要”，得到中文 view-summary.md 与 metadata.json。摘要读取当前节点和材质，无法核实的自定义图和缺字段显示 partial/unverified。源科学数组、现有 CSV 数据格式不变。
