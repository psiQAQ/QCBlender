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

点击 **N 侧栏 → 导入与导出（Import and Export） → 导入（Import） → 导入 Gaussian / Cube / XYZ（Import Gaussian / Cube / XYZ）**，导入 [shared/data/public/P03/water-dimer.fchk](../../shared/data/public/P03/water-dimer.fchk)，将原子对象命名为 **P03-atoms**。应看到两个水分子，共六个原子。

<details>
<summary>了解 IGMH 与 IRI</summary>

> IGMH 是按原子片段分析相互作用区域的一种方法；IRI 是相互作用区域指标，用于显示化学键及弱相互作用区域。这里读取已经算好的 Cube。

</details>

<a id="step-02"></a>
### 2. 导入 IGMH 成对场并声明片段

分析方法、分量、片段和单位按生成 Cube 的原计算填写；声明单位不会换算网格数值。

- 只选 **P03-atoms**，点击 **N 侧栏 → 导入与导出（Import and Export） → 导入外部结果（Import External Results） → 空间场分析（Spatial Field Analysis） → IGMH / IRI 成对场（IGMH / IRI Paired Fields）**。
- 按下表输入 IGMH 参数，确认并等待完成；在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 点击新建 **QC paired field data** 行最左侧的选择图标，将鼠标移入三维视口，按 `F2` 命名为 **IGMH-data**。

| 控件 | 输入值 |
| --- | --- |
| 分析（Analysis） | IGMH |
| 几何场 Cube（Geometry Cube） | [shared/data/public/P03/igmh/dg_inter.cub](../../shared/data/public/P03/igmh/dg_inter.cub) |
| sign(lambda2)rho Cube | [shared/data/public/P03/igmh/sl2r.cub](../../shared/data/public/P03/igmh/sl2r.cub) |
| 几何场值单位（Geometry value unit） | electron/bohr^4 |
| 着色场值单位（Color value unit） | electron/bohr^3 |
| IGMH 分量（IGMH component） | inter |
| 片段原子（JSON）（Fragment atoms (JSON)） | `[[1,2,3],[4,5,6]]` |
| 声明来源（可选）（Declaration source (optional)） | P03 Multiwfn fragment setup |
| 颜色最小值（Color minimum） / 颜色最大值（Color maximum） | −0.04 / 0.04 |

<details>
<summary>了解成对场、IGMH 分量与片段声明</summary>

> 成对场在相同网格位置保存两个场值：一份决定表面位置，一份提供着色量。**QC paired field data** 是绑定两份网格值及分析声明的记录对象，用于后面的筛选和数据导出；三维表面用于观察相互作用区域。

**分析（Analysis）** 应与生成 Cube 的分析方法一致：

- **IGMH**：几何场（Geometry Field）为 delta-g，可声明分量及原子片段；本例读取两个水分子间的分量。
- **IRI**：几何场（Geometry Field）为 IRI，需要填写原计算使用的电子密度指数；本页步骤 4 单独导入它。

> sign(lambda2)rho 是电子密度乘以密度 Hessian 第二特征值的符号，用作相互作用区域的着色量。

- **几何场 Cube（Geometry Cube）**：决定表面位置；本例使用 delta-g 的片段间分量。
- **sign(lambda2)rho Cube**：提供表面颜色；两种分析均使用这种着色量。
- **几何场值单位（Geometry value unit） / 着色场值单位（Color value unit）**：分别声明两份场值的单位，填写单位不会换算网格数值。

**IGMH 分量（IGMH component）** 记录源场的分量身份，应按原计算选择：

- **inter**：片段间分量，适合观察已定义片段之间的相互作用。
- **intra**：片段内分量，适合观察各片段内部的区域。
- **total**：总分量。
- **未声明 / unknown（Undeclared / unknown）**：尚未核实分量身份时保留此项。

**片段原子（JSON）（Fragment atoms (JSON)）** 用方括号列表列出各片段的源原子编号；**声明来源（Declaration source (optional)）** 记录声明的依据，optional 表示可留空。本例两组方括号分别指定两个水分子，成员编号沿用源 Cube 的原子顺序，从 1 开始。

</details>

<a id="step-03"></a>
### 3. 设置 IGMH 表面阈值和着色图例

- 在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 选 **QC delta_g**，点击 **N 侧栏 → 当前 QC 对象（Current QC Object） → 打开对象属性（Open Object Properties）**，在 **几何表示（Geometry Representation）** 设 **正值阈值（Positive Isovalue）=0.005**；在 **颜色映射（Color Mapping）** 设 **颜色最小值（Color Minimum） / 颜色中心值（Color Center） / 颜色最大值（Color Maximum）=−0.04/0/0.04**，开启 **图例排版（Legend Layout） → 显示图例（Show Legend）**。应在两个水分子之间看到着色表面，图例单位为 **electron/bohr^3**；独立着色场保持隐藏。
- **IGMH 来源声明（IGMH Source Declaration）** 应显示 **inter** 及两组片段。
- 截图保存为 `human/screenshots/P03-igmh.png`。

![水二聚体的 IGMH 表面、颜色范围及片段声明](../screenshots/P03-igmh.png)

<details>
<summary>区分表面阈值与颜色范围</summary>

**正值阈值（Positive Isovalue）** 决定在哪个 delta-g 等值处生成表面；**颜色最小值（Color Minimum） / 颜色中心值（Color Center） / 颜色最大值（Color Maximum）** 决定如何将着色场的值分配到颜色，图例显示这份着色量及其单位。

</details>

<a id="step-04"></a>
### 4. 导入 IRI 成对场并单独观察表面

重新只选 **P03-atoms**，使用同一成对场入口导入下表 IRI 参数。

| 控件 | 输入值 |
| --- | --- |
| 分析（Analysis） | IRI |
| 几何场 Cube（Geometry Cube） | [shared/data/public/P03/iri/func2.cub](../../shared/data/public/P03/iri/func2.cub) |
| sign(lambda2)rho Cube | [shared/data/public/P03/iri/func1.cub](../../shared/data/public/P03/iri/func1.cub) |
| 几何场值单位（Geometry value unit） | a.u. (electron^-0.1 bohr^-0.7) |
| 着色场值单位（Color value unit） | electron/bohr^3 |
| IRI 密度指数 a（IRI density exponent a） | 1.1 |
| 颜色最小值（Color minimum） / 颜色最大值（Color maximum） | −0.04 / 0.04 |

- 完成后在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 选新建的 **QC paired field data**，在三维视口按 `F2` 命名为 **IRI-data**；先前的记录对象已命名为 **IGMH-data**，可据此区分两份分析。
- 再选 **QC iri_function**，点击 **N 侧栏 → 当前 QC 对象（Current QC Object） → 打开对象属性（Open Object Properties）**，设 **正值阈值（Positive Isovalue）=1.0**、**颜色最小值（Color Minimum） / 颜色中心值（Color Center） / 颜色最大值（Color Maximum）=−0.04/0/0.04** 并开启图例。
- 在 Outliner 关闭 **QC delta_g** 的眼睛和相机图标，保留 **P03-atoms** 与 IRI 表面；两次导入的独立着色场均保持隐藏。应能单独观察 IRI 表面。
- 截图保存为 `human/screenshots/P03-iri.png`。

![水二聚体的 IRI 表面与着色图例](../screenshots/P03-iri.png)

<details>
<summary>了解 IRI 密度指数与原始单位</summary>

> IRI 密度指数 a（IRI density exponent a）记录生成 IRI 时使用的电子密度指数；IRI 的单位随指数定义。a.u. 表示原子单位，本例括号中写出具体的单位幂次；此处按原计算填写，便于追溯这份场。

> 这份 IRI 使用指数 a=1.1，其单位沿用生成计算的定义。两种分析都用 `sign(lambda2)rho` 场着色，原值直接使用。

</details>

<a id="step-05"></a>
### 5. 筛选成对场数值并导出 CSV

- 选 **IGMH-data**，点击 **N 侧栏 → 当前 QC 对象（Current QC Object） → 打开对象属性（Open Object Properties）**，展开 **外部结果浏览器（External Result Browser）**。
- 保持 **交换数值列（Swap value columns）** 关闭，打开 X、Y 两行的全部范围开关，填 **X 从（From）=−0.04、至（To）=0.04；Y 从（From）=0.001、至（To）=0.02**，点击 **应用筛选（Apply Filter）**。应提示 **已保存成对场筛选以供数据导出（Paired field filter saved for data export）**。
- X 对应 `sign_lambda2_rho [electron/bohr^3]`，Y 对应 `delta_g [electron/bohr^4]`。
- 保持 **IGMH-data** 活动，按[数据导出](../SOP.md#export)选择 **数据（Data）=成对场（paired）、行（Rows）=当前筛选（Current filter）** 并设置输出目录，导出后应得到 `paired_voxels.csv` 与 `metadata.json`。

- 要练习交换两列，可保持 **IGMH-data** 活动，开启 **交换数值列（Swap value columns）**，同时将范围改为 **X 从（From）=0.001、至（To）=0.02；Y 从（From）=−0.04、至（To）=0.04**，点击 **应用筛选（Apply Filter）** 后再次按 **行（Rows）=当前筛选（Current filter）** 导出。
- 两次 CSV 应选中相同的网格点，`x_value`、`y_value` 的内容及配套元数据中的单位互换。
- 完成后关闭 **交换数值列（Swap value columns）**，将 X、Y 范围恢复为本步最初的值，并再次点击 **应用筛选（Apply Filter）**。

<details>
<summary>了解 X/Y 列、筛选条件与 CSV 范围</summary>

> 外部结果浏览器（External Result Browser）用于筛选分析记录。这里 X、Y 表示两列场值，可按数值范围提取要比较的网格点。

**交换数值列（Swap value columns）** 决定两列各自使用哪份场：

- 关闭：X 为 `sign_lambda2_rho [electron/bohr^3]`，Y 为 `delta_g [electron/bohr^4]`。
- 开启：X 为 delta-g，Y 为 sign(lambda2)rho；相应范围也应按交换后的物理量填写。

每个 **从（From） / 至（To）** 左侧都有独立范围开关：开启从（From）后按下限筛选，开启至（To）后按上限筛选，关闭两端则该列不限范围。X、Y 的所有已启用条件须同时满足，边界值也包含在内。**应用筛选（Apply Filter）** 保存当前条件，三维表面继续由等值和颜色参数控制。

导出时 **行（Rows）** 决定选取哪些数据行：

- **全部来源记录（All source records）**：导出两份场都有有效值的全部网格点，适合保留完整数据。
- **当前筛选（Current filter）**：导出满足当前 X、Y 条件的有效网格点，适合只分析某个数值区域。

`paired_voxels.csv` 每行对应一个满足筛选条件的有效网格点，包含位置及 X、Y 两个场值，可用于绘制散点图或比较两场的数值关系。

</details>
