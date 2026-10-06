# 外部 ESP 与 AIM 分析

[返回教程目录](../SOP.md#topics) · [ESP 极值与面积](#esp) · [AIM 点与路径](#aim)

路径相对材料根目录。接续[密度与 ESP](03-density-esp.md#mapping)步骤 1–5，使用 **P03-atoms**、**QC electron_number_density** 和 **QC electrostatic_potential**。在 **Display Layers** 隐藏切片、雾、偶极或其他案例对象，只保留本页需要的层。

<a id="esp"></a>
## ESP 极值与面积

> ESP 极值是在指定表面上找到的静电势最大值和最小值。本例外部分析使用密度为 0.001 electron/bohr^3 的表面。

1. 选 **QC electron_number_density**，将 **几何表示 → 正值阈值** 改为 **0.001**。再选 **QC electrostatic_potential**，点击 **N 侧栏 → 导入外部结果 → ESP 表面分析**，按下表输入并确认。应新增 **QC ESP maximum、QC ESP minimum、QC ESP area distribution**。

| 控件 | 输入值 |
| --- | --- |
| Extrema PDB | [shared/data/public/P03/esp/surfanalysis.pdb](../../shared/data/public/P03/esp/surfanalysis.pdb) |
| Area distribution text | [shared/data/public/P03/esp/stdout.log](../../shared/data/public/P03/esp/stdout.log) |
| Surface definition | rho=0.001 electron/bohr^3 |
| Extrema value unit | kcal/mol |
| Distribution center unit | kcal/mol |
| Area unit | angstrom^2 |

2. 选 **QC ESP maximum**，打开 **对象属性 → External Analysis Records**，应有 **4 条记录**；将 **Record (1-based)** 设为 **2**，应显示源编号 **2**、值 **57.8 kcal/mol**。在 **External Result Browser** 设 **Match (1-based)=2**，点击 **应用筛选**，应突出该点并显示它的标签。选 **QC ESP minimum**，其记录应有 **3 条**，第 1 条值为 **−25.5 kcal/mol**。截图保存为 `human/screenshots/60-esp-extrema.png`。

![ESP 最大值、最小值与所选源点标签](../screenshots/60-esp-extrema.png)

> Record 是源记录中的行位置；Match 是当前匹配列表中的行位置。面板同时显示源编号，便于找到原来的点。

3. 选 **QC ESP area distribution**，在 **External Analysis Records** 应看到 **40 条记录**、总面积 **73.1833 angstrom^2**。在 **External Result Browser** 选 **Area bin selection=Center in range**，开启 **Center [kcal/mol]** 两端范围，填 **From=0、To=20**，点击 **应用筛选**。应显示面积 **14.4784 angstrom^2**、源百分比约 **19.7838%**。截图保存为 `human/screenshots/61-esp-area.png`；看完后关闭两端范围并重新应用，恢复全表。

![ESP 面积分布的源总面积和范围内面积](../screenshots/61-esp-area.png)

> 面积分布将表面按 ESP 值分成区间。Center in range 选择中心值落在范围内的完整区间。

<a id="aim"></a>
## AIM 临界点与路径

> AIM 拓扑分析从电子密度中找出临界点和路径。本例文件中的 C/N 是临界点类别编码，分别表示核临界点和键临界点。

4. 在 **Display Layers** 隐藏 ESP 极值和密度表面，只选 **P03-atoms**。点击 **N 侧栏 → 导入外部结果 → AIM 拓扑**，按下表选择三份文件并确认。应新增 **QC AIM CP C、QC AIM CP N、QC AIM bond paths**；C/N 两层分别有 **6/5 个点**。

| 控件 | 输入文件 |
| --- | --- |
| CPs PDB | [shared/data/public/P03/aim/CPs.pdb](../../shared/data/public/P03/aim/CPs.pdb) |
| Paths PDB | [shared/data/public/P03/aim/paths.pdb](../../shared/data/public/P03/aim/paths.pdb) |
| CP properties text (optional) | [shared/data/public/P03/aim/CPprop.txt](../../shared/data/public/P03/aim/CPprop.txt) |

5. 选 **QC AIM CP N**，在 **External Analysis Records** 将 **Record (1-based)** 设为 **3**。应显示源编号 **9**，位置约 **(0,0,1.451) Å**，`Density of all electrons` 为 **0.01088848625**。在 **External Result Browser** 设 **Match (1-based)=3**，点击 **应用筛选**，应突出两个水分子之间的该点。截图保存为 `human/screenshots/62-aim-point.png`。

![AIM 源点 9 的位置及电子密度属性](../screenshots/62-aim-point.png)

> 临界点属性来自输入的分析表；本例电子密度的单位是 electron/bohr^3。

6. 选 **QC AIM bond paths**，在 **External Result Browser** 应看到 **10 recorded AIM paths**。将 **Path (1-based)** 从 **1** 改为 **2**，面板应分别显示 **9 points / 47 points**。在视口旋转观察路径；如果原子球遮挡路径，可临时隐藏 **P03-atoms**。截图保存为 `human/screenshots/63-aim-paths.png`。

![水二聚体的 AIM 路径及所选路径点数](../screenshots/63-aim-paths.png)
