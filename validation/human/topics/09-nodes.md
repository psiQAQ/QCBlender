# 用公共几何节点组合显示

[返回教程目录](../SOP.md#topics) · [源属性与求值几何](#attributes)

路径相对材料根目录。本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。

> 几何节点用连线把选择、表示和裁剪组合起来。这里在显示副本上建立一个简单分支。

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，导入 [shared/data/public/P06/water-dimer.xyz](../../shared/data/public/P06/water-dimer.xyz)。选中新原子对象，在 **Display Layers → Duplicate** 创建副本，隐藏原层，保持副本活动。

2. 切换顶部 **Geometry Nodes** 工作区，打开副本已有的 **QC Atoms and Bonds** 修改器节点树。通过节点编辑器的 **添加** 菜单，放入下列三个公共节点。

| 菜单 | 节点 |
| --- | --- |
| 原子选择 | QC Select Atoms |
| 表示 → 原子与键 | QC Style Atoms and Bonds |
| 空间 → 裁剪 | QC Clip Geometry |

3. 按下表连接新分支；接入 **组输出 Geometry** 时替换原来接到该插口的连线。为新表示节点的 **Material** 选择副本原节点已经使用的元素材质。

| 起点 | 终点 |
| --- | --- |
| 组输入 Geometry | 新 QC Style Atoms and Bonds 的 Geometry |
| 新 QC Select Atoms 的 Selection | 新 QC Style Atoms and Bonds 的 Selection |
| 新 QC Style Atoms and Bonds 的 Geometry | 新 QC Clip Geometry 的 Geometry |
| 新 QC Clip Geometry 的 Geometry | 组输出 Geometry |

4. 在新选择节点开启 **Selection**，设 **Element (0 = all)=8、First Atom (1-based)=1、Last Atom (0 = all)=0**；在表示节点设 **Style (0 ball-stick, 1 space-fill, 2 bonds)=1**。应只看到两个氧球。再将 **Element=0、Style=0、Atom Radius=0.25、Bond Radius=0.07**，应恢复两个水分子的球棍。截图保存为 `human/screenshots/90-nodes.png`。

![公共选择、表示和裁剪节点的新分支及分子显示](../screenshots/90-nodes.png)

> Element 采用元素原子序数，氧为 8；First/Last 使用源原子编号，Last=0 表示不限制末尾。

5. 在新裁剪节点开启 **Plane Enabled**，设 **Plane Origin=(0,0,1.45)、Plane Normal=(0,0,1)**。应只剩上方水分子；关闭 **Plane Enabled**，恢复六原子显示。

如果要保存这个自定义工程，先选择 **File → External Data → Pack Linked Libraries**，再使用[保存自包含工程](../SOP.md#save)。

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

> POINT 是网格的点域。原子载体的每个点对应一个源原子；`qc_atom_id` 从 0 开始，界面使用的源编号等于它加 1。

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

自定义节点用 **Named Attribute** 读取属性时，先看它的 **Exists** 输出；属性存在后，再检查对应的有效标志。**QC Sample Scalar Field** 的 **Value** 与 **Valid** 应分别连接到 **QC Map Scalar Colors v2** 的同名输入。

标准着色中，无效区域显示为洋红色。网格外位置和内部缺失区域都不能按“真实零值”解读；更换预设或反转颜色不会使这些位置变成有效数据。导出剖面时，无效点在 CSV 中显示 **valid=0、value 留空**，有效零值则保留为数值零。剖面操作见[空间观察与数据导出](04-spatial-tools.md#profile)。
