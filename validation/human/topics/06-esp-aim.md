# 06. 外部 ESP 与 AIM 分析

[返回教程目录](../SOP.md#topics)

## 目录

- [ESP 极值与面积](#esp)
  - [1. 匹配密度等值面并导入 ESP 分析](#step-01)
  - [2. 浏览 ESP 极值并高亮指定源点](#step-02)
  - [3. 按 ESP 范围筛选表面积](#step-03)
- [AIM 临界点与路径](#aim)
  - [4. 导入 AIM 临界点和路径](#step-04)
  - [5. 查看并高亮分子间的 AIM 临界点](#step-05)
  - [6. 浏览 AIM 路径记录并观察曲线](#step-06)
- [附录：参数、原理与输入规范](#appendix)
  - [A1. 了解 ESP 表面分析、输入文件与单位](#appendix-step-01)
  - [A2. 区分源记录、匹配项与高亮标签](#appendix-step-02)
  - [A3. 了解面积区间、范围重叠与源百分比](#appendix-step-03)
  - [A4. 了解 AIM 临界点与路径输入](#appendix-step-04)
  - [A5. 了解临界点密度与记录编号](#appendix-step-05)
  - [A6. 了解路径编号、点数与曲线显示](#appendix-step-06)

本页接续[专题 03 步骤 1–5](03-density-esp.md#step-01)，在同一工程中保留 **P03-atoms、P03-density、P03-esp**。开始时显示原子层和已按 ESP 着色的密度表面，独立 ESP 表面保持隐藏。路径相对教程材料根目录；每次换对象后重新打开其对象属性。

---

<a id="esp"></a>
## ESP 极值与面积

<a id="step-01"></a>
### 1. 匹配密度等值面并导入 ESP 分析

详细说明见[附录 A1：了解 ESP 表面分析、输入文件与单位](#appendix-step-01)。

1. 在 **QC 对象导航** 中选中 **P03-density**，打开对象属性。
2. 将 **几何表示 → 正值阈值** 设置为 `0.001`（与本例外部 ESP 分析采用的密度表面一致）。
3. 导航选中 **P03-esp**（保持该场表面隐藏）。
4. 点击 **N 侧栏 → 导入与导出 → 导入外部结果 → 空间场分析 → ESP 表面分析（ESP Surface Analysis）**。
5. 配置导入参数：
   - **极值点 PDB（Extrema PDB）**：`shared/data/public/gaussian-v2/P03/esp/surfanalysis.pdb`
   - **面积分布文本（Area distribution text）**：`shared/data/public/gaussian-v2/P03/esp/stdout.log`
   - **表面定义（Surface definition）**：`rho=0.001 electron/bohr^3`
   - **极值单位（Extrema value unit）**：`kcal/mol`
   - **分布中心值单位（Distribution center unit）**：`kcal/mol`
   - **面积单位（Area unit）**：`angstrom^2`
6. 确认导入，生成对象 **QC ESP maximum**、**QC ESP minimum** 与 **QC ESP area data**。截图保存至 `human/screenshots/P03-esp-analysis-import.png`。

![ESP极值和面积输入、rho表面定义及各自单位](../screenshots/P03-esp-analysis-import.png)

<a id="step-02"></a>
### 2. 浏览 ESP 极值并高亮指定源点

详细说明见[附录 A2：区分源记录、匹配项与高亮标签](#appendix-step-02)。

1. 选中 **QC ESP minimum** 并打开对象属性，展开 **外部分析记录**。记录总数为 2，设置 `记录 = 1`，数值显示为 `-48.88 kcal/mol`。
2. 选中 **QC ESP maximum** 打开对象属性，记录总数为 3，设置 `记录 = 2`，对应源编号 2、数值 `57.88 kcal/mol`。
3. 展开 **外部结果浏览器**，设置 `匹配项（从1开始） = 2`，点击 **应用筛选（Apply Filter）**。视口中高亮该极值点并浮现标签。截图保存至 `human/screenshots/P03-esp-extrema.png`。

![ESP 最大值、最小值与所选源点标签](../screenshots/P03-esp-extrema.png)

<a id="step-03"></a>
### 3. 按 ESP 范围筛选表面积

详细说明见[附录 A3：了解面积区间、范围重叠与源百分比](#appendix-step-03)。

1. 选中 **QC ESP area data** 打开对象属性，确认总记录为 40 条、总表面积为 `74.6808 angstrom^2`。
2. 在 **外部结果浏览器** 中开启中心值上下限两端的开关，再设置过滤条件：
   - **面积分箱选择**：中心值在范围内（Center in range）
   - **中心（Center） [kcal/mol] 从 / 至**：`0 / 20`
3. 点击 **应用筛选**，界面回显筛选面积 `15.0671 angstrom^2`（占比 `20.1752%`）。截图保存至 `human/screenshots/P03-esp-area.png`。

![ESP 面积分布的源总面积和范围内面积](../screenshots/P03-esp-area.png)

4. 按[共同导出方法](../SOP.md#export)，选择 **数据=ESP_AREA、行=当前筛选**，保留 `esp_area.csv` 与 `metadata.json`；需要全表时改为 **行=全部**。完成后关闭中心值两端开关并应用筛选。

---

<a id="aim"></a>
## AIM 临界点与路径

<a id="step-04"></a>
### 4. 导入 AIM 临界点和路径

详细说明见[附录 A4：了解 AIM 临界点与路径输入](#appendix-step-04)。

1. 隐藏 ESP 极值与密度表面，仅保持选中 **P03-atoms**。
2. 点击 **N 侧栏 → 导入与导出 → 导入外部结果 → 原子与键分析 → AIM 拓扑（AIM Topology）**。
3. 选择对应输入文件：
   - **临界点 PDB（CPs PDB）**：`shared/data/public/gaussian-v2/P03/aim/CPs.pdb`
   - **路径 PDB（Paths PDB）**：`shared/data/public/gaussian-v2/P03/aim/paths.pdb`
   - **临界点属性文本（可选）**：`shared/data/public/gaussian-v2/P03/aim/CPprop.txt`
4. 确认后生成对象 **QC AIM CP C**（6点）、**QC AIM CP N**（5点）及 **QC AIM bond paths**。截图保存至 `human/screenshots/P03-aim-import.png`。

![同源AIM临界点、路径和临界点属性三份输入](../screenshots/P03-aim-import.png)

<a id="step-05"></a>
### 5. 查看并高亮分子间的 AIM 临界点

详细说明见[附录 A5：了解临界点密度与记录编号](#appendix-step-05)。

1. 选中 **QC AIM CP N** 打开对象属性，在 **外部分析记录** 中将 `记录` 设为 `2`。
2. 确认显示源编号 8，坐标约 `(0.037, 0, 1.670) Å`，全电子密度约为 `0.02243675`。
3. 在 **外部结果浏览器** 中设 `匹配项 = 2` 并点击 **应用筛选**。两分子间对应的键临界点被高亮突出。截图保存至 `human/screenshots/P03-aim-point.png`。

![AIM 源点 8 的位置及电子密度属性](../screenshots/P03-aim-point.png)

<a id="step-06"></a>
### 6. 浏览 AIM 路径记录并观察曲线

详细说明见[附录 A6：了解路径编号、点数与曲线显示](#appendix-step-06)。

1. 选中 **QC AIM bond paths** 打开对象属性，在 **外部结果浏览器** 中确认共有 10 条拓扑路径记录。
2. 将 `路径（从1开始）` 切换至 `2`（包含 49 个采样点）。
3. 视口中观察平滑连接各原子的拓扑键径曲线。截图保存至 `human/screenshots/P03-aim-paths.png`。

![水二聚体的 AIM 路径及所选路径点数](../screenshots/P03-aim-paths.png)

---

<a id="appendix"></a>
## 附录：参数、原理与输入规范

<a id="appendix-step-01"></a>
### A1. 了解 ESP 表面分析、输入文件与单位

> ESP 是静电势，描述单位正试探电荷在某位置的势能。ESP 极值是在指定表面上找到的最大值和最小值；本例外部分析使用电子密度为 0.001 electron/bohr^3 的等值面。

> 最大值、最小值对象用于定位外部分析给出的 ESP 极值点；**QC ESP area data** 是面积分布的记录对象，用于查看和筛选各势值区间的面积及占比。

> PDB 是保存点坐标等记录的文本格式；rho 表示电子密度。

- **极值点 PDB（Extrema PDB）**：提供极值点的位置与数值，用于在表面附近定位极值。
- **面积分布文本（Area distribution text）**：提供面积表，用于查看各 ESP 区间占据的表面积。
- **表面定义（Surface definition）**：记录外部分析所用表面，需与本例密度表面的阈值一致。
- **极值单位（Extrema value unit） / 分布中心值单位（Distribution center unit）**：分别声明极值与面积区间势值的单位。

> kcal/mol 表示千卡每摩尔，本例按外部分析的约定表达 ESP 数值；angstrom^2 是平方埃，用来表达表面积。导入时声明这些单位，不改变源表中的数值。

<a id="appendix-step-02"></a>
### A2. 区分源记录、匹配项与高亮标签

**外部分析记录（External Analysis Records）** 用于回查源数据，**外部结果浏览器（External Result Browser）** 用于筛选并高亮视口中的点。两个面板的编号各有用途：

- **记录（从1开始）（Record (1-based)）**：当前对象源记录表中的第几行，从 1 开始。改变它只浏览记录及属性。
- **匹配项（从1开始）（Match (1-based)）**：当前匹配列表中的第几个结果，从 1 开始；筛选条件改变后，匹配位置可能变化。设置后点击 **应用筛选（Apply Filter）**，更新视口中的高亮。

高亮点默认附带源编号及数值标签（Value Labels），方便将视口位置与源记录对应。

<a id="appendix-step-03"></a>
### A3. 了解面积区间、范围重叠与源百分比

> 面积区间（bin）按 ESP 值分组统计表面积。每个区间有中心势值，以及源表中记录的 Begin、End 边界。

**面积分箱选择（Area bin selection）** 决定怎样判断一个区间是否选入：

- **中心值在范围内（Center in range）**：中心势值在范围内就选入完整区间，适合按源表中心值分组比较。
- **记录区间与范围重叠（Recorded interval overlaps range）**：源区间的 Begin–End 与指定范围有重叠或边界接触，就选入完整区间，适合查找与某势值范围相关的源区间。仅在源表记录边界时可用，面积不会按重叠长度拆分。

范围两端的开关分别启用 **从（From）** 下限和 **至（To）** 上限；关闭一端表示该侧不限范围，边界值包含在内。

> 源百分比沿用原分析表；本例以原分析的总表面积为分母。筛选后只加总选中区间的面积和源百分比，便于查看它们占整个表面的比例。

#### 比较区间重叠模式

保持上下限开关开启和范围 0–20，改为 **区间与范围重叠** 并应用。本例还会选入 −5–0 与 20–25 kcal/mol 两个完整分箱，面积为 **22.9027 angstrom^2**、源百分比约 **30.6673%**；面积不会按重叠长度拆分。完成后恢复 **中心值在范围内**，关闭两端开关并应用，回到全表。

<a id="appendix-step-04"></a>
### A4. 了解 AIM 临界点与路径输入

> AIM（分子中的原子）拓扑分析从电子密度中找出临界点和路径。临界点（CP）处，电子密度向各方向的空间变化率均为零，用于描述密度分布的特征；本例文件中的 C/N 是类别编码，分别表示核临界点和键临界点。

> C/N 点对象用于在构型中定位临界点并查看其源属性；**QC AIM bond paths** 用于观察导入的路径及各路径的采样点记录。

- **临界点 PDB（CPs PDB）**：提供临界点坐标，用于在构型中定位点。
- **路径 PDB（Paths PDB）**：提供路径上的采样点，用于绘制曲线。
- **临界点属性文本（可选）（CP properties text (optional)）**：提供按源编号与点对应的临界点属性；optional 表示可不提供属性表，本例提供它以查看电子密度。

<a id="appendix-step-05"></a>
### A5. 了解临界点密度与记录编号

> Density of all electrons 是该点的总电子密度；属性值来自输入分析表，本例单位为 electron/bohr^3。

这里继续使用步骤 2 的记录（Record）与匹配项（Match）：记录（Record）在 **QC AIM CP N** 的五条源记录中定位一行，匹配项（Match）在当前筛选结果中选取要高亮的点。源编号沿用原分析，不会随筛选重新编号。

<a id="appendix-step-06"></a>
### A6. 了解路径编号、点数与曲线显示

> 路径（Path）选择源路径中的第几条；points 是该路径包含的采样点数，用于了解导入曲线的离散记录。

**路径（从1开始）（Path (1-based)）** 用于浏览各条路径的来源和点数；视口中的路径显示仍由对象的可见性和几何控件管理。
