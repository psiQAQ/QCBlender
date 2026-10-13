# 用公共几何节点组合显示

[返回教程目录](../SOP.md#topics)

## 目录

- [1. 导入分子并创建显示副本](#step-01)
- [2. 添加选择、表示和裁剪节点](#step-02)
- [3. 连接新分支并接入组输出](#step-03)
- [4. 筛选氧原子并切换表示方式](#step-04)
- [5. 裁剪上方水分子并恢复完整显示](#step-05)
- [源属性与求值几何](#attributes)
  - [读取与几何对应的属性](#section-01)


路径相对材料根目录。先按[准备新工程](../SOP.md#new-scene)准备场景并打开 QCBlender 侧栏。

本页截图使用案例 `P06-` 前缀。

<a id="step-01"></a>
### 1. 导入分子并创建显示副本

> 几何节点（Geometry Nodes）用连线把选择、表示和裁剪组合起来。节点树是这组计算连接；修改器把节点树应用到对象，生成视口中看到的几何。这里在显示副本上建立一个简单分支。

点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，导入 [shared/data/public/P06/water-dimer.xyz](../../shared/data/public/P06/water-dimer.xyz)。选中新原子对象，在三维视口按 `F2` 命名为 **P06-original**。在 **Display Layers → Duplicate** 创建副本，将副本命名为 **P06-nodes**；关闭原层的眼睛和相机图标，保持副本活动。Duplicate 会为副本复制可编辑的外层节点树。

<a id="step-02"></a>
### 2. 添加选择、表示和裁剪节点

本例把显示过程分成三个环节，分别决定选择哪些原子、如何画出原子与键，以及保留哪个空间区域。

- **QC Select Atoms**：输出原子选择条件，交给表示节点使用。
- **QC Style Atoms and Bonds**：接收原子载体与选择条件，生成球、键或二者组合。
- **QC Clip Geometry**：裁剪已经生成的显示几何，便于查看局部空间。

切换顶部 **Geometry Nodes** 工作区，在 Outliner 选 **P06-nodes**。在 **Properties → Modifiers** 找到已有的 **QC Atoms and Bonds** 几何节点修改器；让下方几何节点编辑器显示这个修改器使用的 **QC Atoms View v2** 节点树副本，名称可能带 `.001` 等后缀。若编辑器固定在其他树，先取消其图钉固定；将鼠标移入节点编辑器，按 `Home` 查看全部节点，应能看到组输入、原有表示节点和组输出。通过节点编辑器的 **添加** 菜单，放入下列三个公共节点，并将它们摆在原节点下方的空白区域。

| 菜单 | 节点 |
| --- | --- |
| 原子选择 | QC Select Atoms |
| 表示 → 原子与键 | QC Style Atoms and Bonds |
| 空间 → 裁剪 | QC Clip Geometry |

<a id="step-03"></a>
### 3. 连接新分支并接入组输出

> 插口是节点边缘用于输入或输出数据的连接点；连线把上游输出交给下游输入。组输入接收对象的原子载体，组输出交付最终显示几何。

本分支使用三类接口：

- **Geometry**：传递几何和附在几何上的属性；表示节点接收源原子载体，裁剪节点接收表示节点生成的球棍网格。
- **Selection**：传递逐原子的真假条件；选择节点的输出连接到表示节点，由后者在收到的原子载体上判断哪些原子参与显示。
- **Material**：指定外观材质；本例沿用组输入传入的元素材质。

留在外层节点树，按下表从输出插口拖线到输入插口，连接新分支；接入 **组输出 Geometry** 时替换原来接到该插口的连线。组输入的 **Material** 沿用副本的元素材质。保留原节点，便于对照；本步完成后由新分支提供显示几何。

| 起点 | 终点 |
| --- | --- |
| 组输入 Geometry | 新 QC Style Atoms and Bonds 的 Geometry |
| 组输入 Material | 新 QC Style Atoms and Bonds 的 Material |
| 新 QC Select Atoms 的 Selection | 新 QC Style Atoms and Bonds 的 Selection |
| 新 QC Style Atoms and Bonds 的 Geometry | 新 QC Clip Geometry 的 Geometry |
| 新 QC Clip Geometry 的 Geometry | 组输出 Geometry |

<a id="step-04"></a>
### 4. 筛选氧原子并切换表示方式

**QC Select Atoms** 将输入的 Selection、元素条件和源编号范围共同使用；一个原子满足全部条件时才输出 true。

- **Selection**：未连接时，勾选表示允许所有原子继续接受元素和编号筛选，取消勾选则全部不选。连接上游选择条件后，以连线传来的条件为起点继续筛选。
- **Element (0 = all)**：填元素原子序数，例如氧为 8；0 表示所有元素。
- **First Atom (1-based)**、**Last Atom (0 = all)**：按源原子编号限定闭区间；First=1 从第一个原子开始，Last=0 不限制末尾。

**QC Style Atoms and Bonds → Style** 决定选中原子的表示方式：

- **0 ball-stick**：球棍；**Atom Radius** 调整原子球半径，**Bond Radius** 调整键半径。
- **1 space-fill**：空间填充球；用元素的范德华半径乘以 **VDW Scale**，适合观察原子占据的空间。
- **2 bonds**：只显示键；**Bond Radius** 调整键半径。

直接在新选择节点上开启 **Selection**，设 **Element (0 = all)=8、First Atom (1-based)=1、Last Atom (0 = all)=0**；在新表示节点上设 **Style (0 ball-stick, 1 space-fill, 2 bonds)=1**。应只看到两个氧球。可暂时关闭再开启选择节点的 **Selection**，观察两个氧球一起消失后恢复。

再将新选择节点的 **Element=0**，新表示节点的 **Style=0、Atom Radius=0.25、Bond Radius=0.07**，应恢复两个水分子的球棍。试将 **First Atom=4、Last Atom=6**，应只显示源编号 4–6 的上方水分子；随后恢复 **First Atom=1、Last Atom=0**，回到六原子显示。

这里修改新节点的输入值；修改器上的旧样式参数仍连接原分支。截图保存为 `human/screenshots/P06-nodes.png`。

![公共选择、表示和裁剪节点的新分支及分子显示](../screenshots/P06-nodes.png)

<a id="step-05"></a>
### 5. 裁剪上方水分子并恢复完整显示

**QC Clip Geometry** 按位置保留显示几何，源构型仍保留。节点提供两种可共同使用的裁剪条件：

- **Plane Enabled**：启用平面裁剪；**Plane Origin** 给出以视图对象原点和坐标轴为参考的平面位置，**Plane Normal** 用三个无量纲分量指定朝向，保留法向所指一侧。
- **Box Enabled**：启用方盒裁剪；**Box Minimum / Box Maximum** 给出各轴边界，保留盒内几何。与平面同时启用时，仅保留两种条件都允许的区域。

在新裁剪节点开启 **Plane Enabled**，设 **Plane Origin=(0,0,1.45)、Plane Normal=(0,0,1)**。应只剩上方水分子；关闭 **Plane Enabled**，恢复六原子显示。

> Pack Linked Libraries 将工程链接的外部库打包进 `.blend`，让这里使用的节点库随工程保存，便于移动后继续使用。

如果要保存这个自定义工程，在材料根目录创建 `work/human/P06/`。先选择 **File → External Data → Pack Linked Libraries**，再按[保存自包含工程](../SOP.md#save)保存为 `work/human/P06/P06-nodes.blend`；保留同目录的 `P06-nodes.qcdata/`。重新打开后，选 **P06-nodes** 检查新分支和六原子显示仍在。

> 保存得到的 `.blend` 保留本页的节点组合与显示设置，配套 `.qcdata/` 保存该工程引用的科学数据。两者一起保留，供重新打开、继续编辑或移动工程。

> Asset Browser 是可复用资产的浏览器；QCBlender Nodes 中的节点资产可以加入当前节点树，按需要组合显示。

在 **Asset Browser → QCBlender Nodes** 可找到全部公共节点；其他节点的用途如下。

| 节点 | 用途 |
| --- | --- |
| QC Sample Scalar Field | 从体场读取指定位置的值和有效状态 |
| QC Style Isosurface v3 | 生成带正负符号的等值面 |
| QC Surface Representation | 把表面改为实体、线框或点 |
| QC Style Volume Fog v1 | 给体积显示应用雾材质 |
| QC Map Scalar Colors v2 | 按数值和色域给几何着色 |
| QC Planar Slice | 生成平面采样几何 |

<a id="attributes"></a>
## 源属性与求值几何

> 属性是附在几何元素上的数据；POINT 表示属性按网格点保存。原子载体的每个点对应一个源原子；`qc_atom_id` 从 0 开始，界面使用的源编号等于它加 1。

步骤 4 中筛选氧后，仍使用原文件的氧 1、4。筛选输出的第几行不能代替源编号。制作自定义分支时，保留 `qc_atom_id`，将坐标、元素和可用电荷作为同一个原子的属性一起传递。

> 求值几何是节点运行后的显示结果。原子样式把一个点变成球面，键样式生成管面，因此一个原子可以产生很多顶点。

球棍的求值网格顶点数不等于原子数，球面或键面顶点的位置也不等于核位置。选择原子、创建距离标注或核对构型时，使用源编号与源构型；查看节点结果时，区分样式生成前的原子载体和样式生成后的球棍网格。

下表说明常见属性应如何读取；只有对应来源可用时才提供科学属性。

| 属性 | 读法 |
| --- | --- |
| `qc_atom_id`、`qc_atomic_number` | 源原子零起始编号与元素原子序数 |
| `qc_charge`、`qc_charge_valid` | 电荷值及其有效标志；未提供电荷数据时这两个属性可能都不存在 |
| `qc_mode_displacement` | 已选择振动模式的位移；没有模式数据时不要假定它存在 |
| `qc_scalar_value`、`qc_sample_valid` | 表面或切片上的场采样值及有效标志，应配对使用 |

> 有效标志说明当前位置或记录是否有可用数据。属性不存在、标志为 false、有效数值恰好为零，含义各不相同。

<a id="section-01"></a>
### 读取与几何对应的属性

> Named Attribute 按名称读取当前求值几何上的属性。节点输出要连接到使用该几何的下游节点，才能在相应几何上求值。

例如本页的 **QC Select Atoms** 按 `qc_atomic_number` 和 `qc_atom_id` 生成选择条件，条件在 **QC Style Atoms and Bonds** 收到的源原子载体上求值。保持组输入的原子载体连接到表示节点的 **Geometry**，就能按源元素和编号选择；若改接其他几何，需先确认其中保留了这些属性。

自定义节点用 **Named Attribute** 读取属性时，按属性类型选择数据类型，并将名称完整填入 **Name**。常用输出各有用途：

- **Attribute**：读取的属性值，例如 `qc_atomic_number` 的整数元素编号。
- **Exists**：当前几何上是否存在该属性；先检查它，再检查对应的有效标志。

> QC Sample Scalar Field 在指定位置探测体场；Value 是采样值，Valid 表示这个值是否有效，二者一起传递才能区分缺失数据和零值。

将采样用于着色时，接口按以下方式对应：

- **Volume**：接入要采样的体场。
- **Position**：接入需要采样的位置，须与体场采用同一坐标系。
- **Value / Valid**：分别连接到 **QC Map Scalar Colors v2** 的同名输入，同时将要着色的几何接入该节点的 **Geometry**。

本页 XYZ 样本提供原子坐标和元素。练习电荷或体场着色时，应先导入具有对应数据的来源；可按[电子密度、自旋密度与 ESP](03-density-esp.md)使用带场的案例。

标准着色中，无效区域显示为洋红色。网格外位置和内部缺失区域都不能按“真实零值”解读；更换预设或反转颜色不会使这些位置变成有效数据。导出剖面时，无效点在 CSV 中显示 **valid=0、value 留空**，有效零值则保留为数值零。剖面操作见[空间观察与数据导出](04-spatial-tools.md#profile)。
