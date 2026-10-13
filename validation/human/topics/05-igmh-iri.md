# IGMH 与 IRI

[返回教程目录](../SOP.md#topics)

## 目录

- [1. 导入水二聚体作为共同参考](#step-01)
- [2. 导入 IGMH 成对场并声明片段](#step-02)
- [3. 设置 IGMH 表面阈值和着色图例](#step-03)
- [4. 导入 IRI 成对场并单独观察表面](#step-04)
- [5. 筛选成对场数值并导出 CSV](#step-05)


路径相对材料根目录。先按[准备新工程](../SOP.md#new-scene)准备场景并打开 QCBlender 侧栏；本页使用同一个水二聚体参考对象完成两种分析。

本页截图使用案例 `P03-` 前缀。

<a id="step-01"></a>
### 1. 导入水二聚体作为共同参考

> IGMH 是按原子片段分析相互作用区域的一种方法；IRI 是相互作用区域指标，用于显示化学键及弱相互作用区域。这里读取已经算好的 Cube。

点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，导入 [shared/data/public/P03/water-dimer.fchk](../../shared/data/public/P03/water-dimer.fchk)，将原子对象命名为 **P03-atoms**。应看到两个水分子，共六个原子。

<a id="step-02"></a>
### 2. 导入 IGMH 成对场并声明片段

> 成对场在相同网格位置保存两个场值：一份决定表面位置，一份提供着色量。**QC paired field data** 是绑定两份网格值及分析声明的记录对象，用于后面的筛选和数据导出；三维表面用于观察相互作用区域。

**Analysis** 应与生成 Cube 的分析方法一致：

- **IGMH**：几何场为 delta-g，可声明分量及原子片段；本例读取两个水分子间的分量。
- **IRI**：几何场为 IRI，需要填写原计算使用的电子密度指数；本页步骤 4 单独导入它。

> sign(lambda2)rho 是电子密度乘以密度 Hessian 第二特征值的符号，用作相互作用区域的着色量。

- **Geometry Cube**：决定表面位置；本例使用 delta-g 的片段间分量。
- **sign(lambda2)rho Cube**：提供表面颜色；两种分析均使用这种着色量。
- **Geometry value unit / Color value unit**：分别声明两份场值的单位，填写单位不会换算网格数值。

**IGMH component** 记录源场的分量身份，应按原计算选择：

- **inter**：片段间分量，适合观察已定义片段之间的相互作用。
- **intra**：片段内分量，适合观察各片段内部的区域。
- **total**：总分量。
- **未声明 / unknown**：尚未核实分量身份时保留此项。

**Fragment atoms (JSON)** 用方括号列表列出各片段的源原子编号；**Declaration source** 记录声明的依据，optional 表示可留空。本例两组方括号分别指定两个水分子，成员编号沿用源 Cube 的原子顺序，从 1 开始。

只选 **P03-atoms**，点击 **N 侧栏 → 导入外部结果 → IGMH / IRI 成对场**。按下表输入 IGMH 参数，确认并等待完成；在 **Display Layers** 点击新建 **QC paired field data** 行最左侧的选择图标，将鼠标移入三维视口，按 `F2` 命名为 **IGMH-data**。

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

<a id="step-03"></a>
### 3. 设置 IGMH 表面阈值和着色图例

**正值阈值** 决定在哪个 delta-g 等值处生成表面；**Color Minimum / Center / Maximum** 决定如何将着色场的值分配到颜色，图例显示这份着色量及其单位。

在 **Display Layers** 选 **QC delta_g**，点击 **工作流 → 对象属性与显示参数**，在 **几何表示** 设 **正值阈值=0.005**；在 **颜色映射** 设 **Color Minimum/Center/Maximum=−0.04/0/0.04**，开启 **图例排版 → 显示图例**。应在两个水分子之间看到着色表面，图例单位为 **electron/bohr^3**；独立着色场保持隐藏。**IGMH 来源声明** 应显示 **inter** 及两组片段。截图保存为 `human/screenshots/P03-igmh.png`。

![水二聚体的 IGMH 表面、颜色范围及片段声明](../screenshots/P03-igmh.png)

<a id="step-04"></a>
### 4. 导入 IRI 成对场并单独观察表面

> IRI density exponent a 记录生成 IRI 时使用的电子密度指数；IRI 的单位随指数定义。a.u. 表示原子单位，本例括号中写出具体的单位幂次；此处按原计算填写，便于追溯这份场。

重新只选 **P03-atoms**，使用同一成对场入口导入下表 IRI 参数。完成后在 **Display Layers** 选新建的 **QC paired field data**，在三维视口按 `F2` 命名为 **IRI-data**；先前的记录对象已命名为 **IGMH-data**，可据此区分两份分析。再选 **QC iri_function**，点击 **工作流 → 对象属性与显示参数**，设 **正值阈值=1.0**、**Color Minimum/Center/Maximum=−0.04/0/0.04** 并开启图例。在 **Display Layers** 关闭 **QC delta_g** 的眼睛和相机图标，保留 **P03-atoms** 与 IRI 表面；两次导入的独立着色场均保持隐藏。应能单独观察 IRI 表面。截图保存为 `human/screenshots/P03-iri.png`。

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

<a id="step-05"></a>
### 5. 筛选成对场数值并导出 CSV

> External Result Browser 用于筛选分析记录。这里 X、Y 表示两列场值，可按数值范围提取要比较的网格点。

**Swap value columns** 决定两列各自使用哪份场：

- 关闭：X 为 `sign_lambda2_rho [electron/bohr^3]`，Y 为 `delta_g [electron/bohr^4]`。
- 开启：X 为 delta-g，Y 为 sign(lambda2)rho；相应范围也应按交换后的物理量填写。

每个 **From / To** 左侧都有独立范围开关：开启 From 后按下限筛选，开启 To 后按上限筛选，关闭两端则该列不限范围。X、Y 的所有已启用条件须同时满足，边界值也包含在内。**Apply Filter** 保存当前条件，三维表面继续由等值和颜色参数控制。

导出时 **Rows** 决定选取哪些数据行：

- **All source records**：导出两份场都有有效值的全部网格点，适合保留完整数据。
- **Current filter**：导出满足当前 X、Y 条件的有效网格点，适合只分析某个数值区域。

选 **IGMH-data**，点击 **工作流 → 对象属性与显示参数**，展开 **External Result Browser**。保持 **Swap value columns** 关闭，打开 X、Y 两行的全部范围开关，填 **X From=−0.04、To=0.04；Y From=0.001、To=0.02**，点击 **Apply Filter**。应提示 **Paired field filter saved for data export**。X 对应 `sign_lambda2_rho [electron/bohr^3]`，Y 对应 `delta_g [electron/bohr^4]`。保持 **IGMH-data** 活动，按[数据导出](../SOP.md#export)选择 **Data=paired、Rows=Current filter** 并设置输出目录，导出后应得到 `paired_voxels.csv` 与 `metadata.json`。

要练习交换两列，可保持 **IGMH-data** 活动，开启 **Swap value columns**，同时将范围改为 **X From=0.001、To=0.02；Y From=−0.04、To=0.04**，点击 **Apply Filter** 后再次按 **Rows=Current filter** 导出。两次 CSV 应选中相同的网格点，`x_value`、`y_value` 的内容及配套元数据中的单位互换。完成后关闭 **Swap value columns**，将 X、Y 范围恢复为本步最初的值，并再次点击 **Apply Filter**。

`paired_voxels.csv` 每行对应一个满足筛选条件的有效网格点，包含位置及 X、Y 两个场值，可用于绘制散点图或比较两场的数值关系。
