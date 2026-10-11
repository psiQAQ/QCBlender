# IGMH 与 IRI

[返回教程目录](../SOP.md#topics)

路径相对材料根目录。先按[准备新工程](../SOP.md#new-scene)准备场景并打开 QCBlender 侧栏；本页使用同一个水二聚体参考对象完成两种分析。

本页截图使用案例 `P03-` 前缀。

> IGMH 是按原子片段分析相互作用区域的一种方法；IRI 是相互作用区域指标，用于显示化学键及弱相互作用区域。这里读取已经算好的 Cube。

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，导入 [shared/data/public/P03/water-dimer.fchk](../../shared/data/public/P03/water-dimer.fchk)，将原子对象命名为 **P03-atoms**。应看到两个水分子，共六个原子。

2. 只选 **P03-atoms**，点击 **N 侧栏 → 导入外部结果 → IGMH / IRI 成对场**。按下表输入 IGMH 参数，确认并等待完成；在 **Display Layers** 点击新建 **QC paired field data** 行最左侧的选择图标，将鼠标移入三维视口，按 `F2` 命名为 **IGMH-data**。

> **QC paired field data** 是成对场的分析记录对象，绑定两份网格值及分析声明，用于后面的筛选和数据导出；三维表面用于观察相互作用区域。

> Geometry Cube 决定表面位置，sign(lambda2)rho Cube 提供带符号的电子密度着色量。Geometry value unit 与 Color value unit 分别声明两份场值的单位；填写单位不会换算网格数值。

> IGMH component 声明分量：inter 为片段间，intra 为片段内，total 为总分量。Fragment atoms (JSON) 用方括号列表列出各片段的源原子编号；Declaration source 记录这份声明的依据，optional 表示可留空。

| 控件 | 输入值 |
| --- | --- |
| Analysis | IGMH |
| Geometry Cube | [shared/data/public/P03/igmh/dg_inter.cub](../../shared/data/public/P03/igmh/dg_inter.cub) |
| sign(lambda2)rho Cube | [shared/data/public/P03/igmh/sl2r.cub](../../shared/data/public/P03/igmh/sl2r.cub) |
| Geometry value unit | electron/bohr^4 |
| Color value unit | electron/bohr^3 |
| IGMH component | inter |
| Fragment atoms (JSON) | `[[1,2,3],[4,5,6]]` |
| Declaration source (optional) | P03 Multiwfn fragment setup |
| Color minimum / maximum | −0.04 / 0.04 |

> 本例两组方括号分别指定两个水分子，成员编号沿用源 Cube 的原子顺序，从 1 开始。

3. 在 **Display Layers** 选 **QC delta_g**，点击 **工作流 → 对象属性与显示参数**，在 **几何表示** 设 **正值阈值=0.005**；在 **颜色映射** 设 **Color Minimum/Center/Maximum=−0.04/0/0.04**，开启 **图例排版 → 显示图例**。应在两个水分子之间看到着色表面，图例单位为 **electron/bohr^3**；独立着色场保持隐藏。**IGMH 来源声明** 应显示 **inter** 及两组片段。截图保存为 `human/screenshots/P03-igmh.png`。

![水二聚体的 IGMH 表面、颜色范围及片段声明](../screenshots/P03-igmh.png)

> IRI density exponent a 记录生成 IRI 时使用的电子密度指数；IRI 的单位随指数定义。a.u. 表示原子单位，本例括号中写出具体的单位幂次；此处按原计算填写，便于追溯这份场。

4. 重新只选 **P03-atoms**，使用同一成对场入口导入下表 IRI 参数。完成后在 **Display Layers** 选新建的 **QC paired field data**，在三维视口按 `F2` 命名为 **IRI-data**；先前的记录对象已命名为 **IGMH-data**，可据此区分两份分析。再选 **QC iri_function**，点击 **工作流 → 对象属性与显示参数**，设 **正值阈值=1.0**、**Color Minimum/Center/Maximum=−0.04/0/0.04** 并开启图例。在 **Display Layers** 关闭 **QC delta_g** 的眼睛和相机图标，保留 **P03-atoms** 与 IRI 表面；两次导入的独立着色场均保持隐藏。应能单独观察 IRI 表面。截图保存为 `human/screenshots/P03-iri.png`。

| 控件 | 输入值 |
| --- | --- |
| Analysis | IRI |
| Geometry Cube | [shared/data/public/P03/iri/func2.cub](../../shared/data/public/P03/iri/func2.cub) |
| sign(lambda2)rho Cube | [shared/data/public/P03/iri/func1.cub](../../shared/data/public/P03/iri/func1.cub) |
| Geometry value unit | a.u. (electron^-0.1 bohr^-0.7) |
| Color value unit | electron/bohr^3 |
| IRI density exponent a | 1.1 |
| Color minimum / maximum | −0.04 / 0.04 |

![水二聚体的 IRI 表面与着色图例](../screenshots/P03-iri.png)

> 这份 IRI 使用指数 a=1.1，其单位沿用生成计算的定义。两种分析都用 `sign(lambda2)rho` 场着色，原值直接使用。

> External Result Browser 用于筛选分析记录。这里 X、Y 表示两列场值；Swap value columns 交换两列对应的场。范围开关决定是否启用 From 下限、To 上限，两列条件同时满足才选入；Apply Filter 保存条件，Rows=Current filter 将它们用于导出。

5. 选 **IGMH-data**，点击 **工作流 → 对象属性与显示参数**，展开 **External Result Browser**。保持 **Swap value columns** 关闭，打开 X、Y 两行的全部范围开关，填 **X From=−0.04、To=0.04；Y From=0.001、To=0.02**，点击 **Apply Filter**。应提示 **Paired field filter saved for data export**。X 对应 `sign_lambda2_rho [electron/bohr^3]`，Y 对应 `delta_g [electron/bohr^4]`。保持 **IGMH-data** 活动，按[数据导出](../SOP.md#export)选择 **Data=paired、Rows=Current filter** 并设置输出目录，导出后应得到 `paired_voxels.csv` 与 `metadata.json`。

> 成对场在相同网格位置保存两个值。筛选作用于导出的数据行，三维表面继续由等值和颜色参数控制。

`paired_voxels.csv` 每行对应一个满足筛选条件的有效网格点，包含位置及 X、Y 两个场值，可用于绘制散点图或比较两场的数值关系。
