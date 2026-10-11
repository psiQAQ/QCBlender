# 外部 ESP 与 AIM 分析

[返回教程目录](../SOP.md#topics) · [ESP 极值与面积](#esp) · [AIM 点与路径](#aim)

路径相对材料根目录。接续[密度与 ESP](03-density-esp.md#mapping)步骤 1–5，使用 **P03-atoms**、**QC electron_number_density** 和 **QC electrostatic_potential**。在 **Display Layers** 隐藏切片、雾、偶极或其他案例对象，只保留本页需要的层。

本页截图使用案例 `P03-` 前缀。

<a id="esp"></a>
## ESP 极值与面积

> ESP 是静电势，描述单位正试探电荷在某位置的势能。ESP 极值是在指定表面上找到的最大值和最小值；本例外部分析使用电子密度为 0.001 electron/bohr^3 的等值面。

1. 选 **QC electron_number_density**，将 **几何表示 → 正值阈值** 改为 **0.001**。再选 **QC electrostatic_potential**，点击 **N 侧栏 → 导入外部结果 → ESP 表面分析**，按下表输入并确认。应新增 **QC ESP maximum、QC ESP minimum、QC ESP area data**。

> 最大值、最小值对象用于定位外部分析给出的 ESP 极值点；**QC ESP area data** 是面积分布的记录对象，用于查看和筛选各势值区间的面积及占比。

> PDB 是保存点坐标等记录的文本格式；Extrema PDB 提供极值点的位置与数值，Area distribution text 提供面积表。Surface definition 记录分析所用表面，rho 表示电子密度；Extrema value unit 与 Distribution center unit 分别声明极值与面积区间势值的单位。

> kcal/mol 表示千卡每摩尔，本例按外部分析的约定表达 ESP 数值；angstrom^2 是平方埃，用来表达表面积。导入时声明这些单位，不改变源表中的数值。

| 控件 | 输入值 |
| --- | --- |
| Extrema PDB | [shared/data/public/P03/esp/surfanalysis.pdb](../../shared/data/public/P03/esp/surfanalysis.pdb) |
| Area distribution text | [shared/data/public/P03/esp/stdout.log](../../shared/data/public/P03/esp/stdout.log) |
| Surface definition | rho=0.001 electron/bohr^3 |
| Extrema value unit | kcal/mol |
| Distribution center unit | kcal/mol |
| Area unit | angstrom^2 |

> External Analysis Records 查看源记录，Record 指当前对象记录表中的行位置；External Result Browser 查看筛选结果，Match 指当前匹配列表中的位置。两者从 1 开始，源编号用于回查原分析中的点。

2. 选 **QC ESP maximum**，打开 **对象属性 → External Analysis Records**，应有 **4 条记录**；将 **Record (1-based)** 设为 **2**，应显示源编号 **2**、值 **57.8 kcal/mol**。在 **External Result Browser** 设 **Match (1-based)=2**，点击 **应用筛选**，应突出该点并显示它的标签。选 **QC ESP minimum**，其记录应有 **3 条**，第 1 条值为 **−25.5 kcal/mol**。截图保存为 `human/screenshots/P03-esp-extrema.png`。

![ESP 最大值、最小值与所选源点标签](../screenshots/P03-esp-extrema.png)

> 面积区间（bin）按 ESP 值分组统计表面积。Area bin selection 选择筛选方式；Center in range 选取中心势值在范围内的完整区间，Center 的范围开关启用下限与上限。

> 源百分比沿用原分析表；本例以原分析的总表面积为分母。筛选后只加总选中区间的面积和源百分比，便于查看它们占整个表面的比例。

3. 选 **QC ESP area data**，在 **External Analysis Records** 应看到 **40 条记录**、总面积 **73.1833 angstrom^2**。在 **External Result Browser** 选 **Area bin selection=Center in range**，开启 **Center [kcal/mol]** 两端范围，填 **From=0、To=20**，点击 **应用筛选**。应显示面积 **14.4784 angstrom^2**、源百分比约 **19.7838%**。截图保存为 `human/screenshots/P03-esp-area.png`；看完后关闭两端范围并重新应用，恢复全表。

![ESP 面积分布的源总面积和范围内面积](../screenshots/P03-esp-area.png)

<a id="aim"></a>
## AIM 临界点与路径

> AIM（分子中的原子）拓扑分析从电子密度中找出临界点和路径。临界点（CP）处，电子密度向各方向的空间变化率均为零，用于描述密度分布的特征；本例文件中的 C/N 是类别编码，分别表示核临界点和键临界点。

4. 在 **Display Layers** 隐藏 ESP 极值和密度表面，只选 **P03-atoms**。点击 **N 侧栏 → 导入外部结果 → AIM 拓扑**，按下表选择三份文件并确认。应新增 **QC AIM CP C、QC AIM CP N、QC AIM bond paths**；C/N 两层分别有 **6/5 个点**。

> C/N 点对象用于在构型中定位临界点并查看其源属性；**QC AIM bond paths** 用于观察导入的路径及各路径的采样点记录。

> CPs PDB 保存临界点坐标，Paths PDB 保存路径上的采样点；CP properties text 提供临界点属性，按源编号与点对应。optional 表示可不提供属性表；本例提供它以查看电子密度。

| 控件 | 输入文件 |
| --- | --- |
| CPs PDB | [shared/data/public/P03/aim/CPs.pdb](../../shared/data/public/P03/aim/CPs.pdb) |
| Paths PDB | [shared/data/public/P03/aim/paths.pdb](../../shared/data/public/P03/aim/paths.pdb) |
| CP properties text (optional) | [shared/data/public/P03/aim/CPprop.txt](../../shared/data/public/P03/aim/CPprop.txt) |

> Density of all electrons 是该点的总电子密度；属性值来自输入分析表，本例单位为 electron/bohr^3。

5. 选 **QC AIM CP N**，在 **External Analysis Records** 将 **Record (1-based)** 设为 **3**。应显示源编号 **9**，位置约 **(0,0,1.451) Å**，`Density of all electrons` 为 **0.01088848625**。在 **External Result Browser** 设 **Match (1-based)=3**，点击 **应用筛选**，应突出两个水分子之间的该点。截图保存为 `human/screenshots/P03-aim-point.png`。

![AIM 源点 9 的位置及电子密度属性](../screenshots/P03-aim-point.png)

> Path 选择源路径中的第几条；points 是该路径包含的采样点数，用于了解导入曲线的离散记录。

6. 选 **QC AIM bond paths**，在 **External Result Browser** 应看到 **10 recorded AIM paths**。将 **Path (1-based)** 从 **1** 改为 **2**，面板应分别显示 **9 points / 47 points**。在视口旋转观察路径；如果原子球遮挡路径，可临时隐藏 **P03-atoms**。截图保存为 `human/screenshots/P03-aim-paths.png`。

![水二聚体的 AIM 路径及所选路径点数](../screenshots/P03-aim-paths.png)
