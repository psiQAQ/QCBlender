# 表面距离投影

## 目录

- [理解深度和三态](#meaning)
- [导入并观察真实案例](#example)
  - [1. 准备同朝向的静态分子](#step-01)
  - [2. 导入距离图、扫描声明与日志](#step-02)
  - [3. 调整色表、原子投影和等值线](#step-03)
  - [4. 读取网格点并导出数据](#step-04)
  - [5. 保存并重新打开工程](#step-05)
- [准备自己的输入](#inputs)

本页路径相对材料根目录，即同时包含 `human/` 和 `shared/` 的目录。先按[入门教程](../SOP.md#install)安装插件。本例使用本机限定的 Multiwfn 官方 Ru 构型及实际计算结果，不在公开样本 ZIP 中；缺少材料时先准备下述完整输入，不能用任意分子与距离图配对。

<a id="meaning"></a>
## 理解深度和三态

> 表面距离投影是在每个 XY 网格位置沿负 Z 扫描，记录首次命中表面的深度 `z_hit-z_start`，单位为 Å。深度通常为负值；它不是三维电子密度场，也不是到原子核的距离。

> 有效性掩码是逐点说明“未命中、有效、未知”的 CSV。只凭原始三列距离图，等于扫描底值的点无法区分“未命中”和“恰在终点命中”。

有效点按深度着色，未命中点留空，未知点默认显示灰色。未知点不参与自动色域或等值线；关闭灰色显示只是隐藏这些点，不会把它们改为有效。原子小圆点使用生成时构型的 XY 坐标，图的 XY 轴保持等比例。

<a id="example"></a>
## 导入并观察真实案例

<a id="step-01"></a>
### 1. 准备同朝向的静态分子

按[准备新工程](../SOP.md#new-scene)进入物体模式，通过 **N 侧栏 → QCBlender → 导入与导出 → 导入 Gaussian / Cube / XYZ** 导入：

`shared/data/local/scientific-displays/ru-vdw-20261023/reference.xyz`

选中这个 61 原子的静态分子。它保留距离图生成时的笛卡尔朝向；不要用自动对齐后的另一份坐标替代。轨迹、优化或 IRC 动态对象不能作为首版投影的参考。

<a id="step-02"></a>
### 2. 导入距离图、扫描声明与日志

打开 **N 侧栏 → 导入与导出 → 导入外部结果 → 空间场分析 → 表面距离投影（Surface Distance Projection）**。四个输入分别选择：

| 输入框 | 相对材料根目录的路径 |
| --- | --- |
| 距离图文本（Distance map text） | `shared/data/local/scientific-displays/ru-vdw-20261023/distmap.txt` |
| 投影扫描 JSON（Projection scan JSON） | `shared/data/local/scientific-displays/ru-vdw-20261023/scan.json` |
| Multiwfn 生成日志（Multiwfn generation log） | `shared/data/local/scientific-displays/ru-vdw-20261023/mwfn_log.txt` |
| 有效性 CSV（Validity CSV） | `shared/data/local/scientific-displays/ru-vdw-20261023/validity.csv` |

确认后，分子旁生成独立二维投影图。打开新对象的对象属性，展开 **表面距离投影**，应显示 `61 × 41`、有效 `1406`、未命中 `1095`、未知 `0`。选中图后按小键盘 `.` 居中观察；需要清楚查看图表时关闭视口的“显示叠加层”，以隐藏网格和父子关系辅助线。

若保持前三项不变、留空有效性 CSV，本例将显示有效 `1406`、未知 `1095`；这些底值应为灰色。这两种结果对应不同的已知信息，不能把灰色点当作命中表面。

<a id="step-03"></a>
### 3. 调整色表、原子投影和等值线

点击 **表面投影显示设置（Surface Projection Display）**。Viridis 和 Cividis 只改变配色；自动色域取有效点的深度范围。比较多张图时，可以开启 **手动深度色域**，为它们输入相同的最小值和最大值；最小值必须小于最大值。

本例选择 Cividis，保留 **显示原子投影**、**显示深度色标**，开启 **显示投影等值线**，在深度等值值输入 `-4,-3,-2` 后确认。图中出现对应的三组线条；未命中和未知区域不跨接或填洞。深度框留空时，程序按当前色域自动选取内部等值值。

取消弹窗保留现有显示；确认后可通过 **编辑 → 撤销 / 重做**恢复前后设置。截图保存为 `human/screenshots/SD01-surface-projection.png`。

![真实 Ru 距离投影、Cividis 色表、等值线与点值面板](../screenshots/SD01-surface-projection.png)

<a id="step-04"></a>
### 4. 读取网格点并导出数据

点击 **读取投影网格点（Inspect Projection Point）**。索引从 `0` 开始，本例 X 为 `0–60`，Y 为 `0–40`。输入 `(30,20)` 后，面板应显示 X `0`、Y `0.5 Å`、深度 `-4.1 Å`、有效；输入 `(0,0)` 后应显示 X `-7`、Y `-6 Å`、深度 `-12 Å`、未命中。这里的 `-12` 是保留的扫描底值，不是已测得的表面深度。

点击面板中的 **导出科学数据**，数据类型选择 **PROJECTION**，按[公共导出步骤](../SOP.md#export)选择 `work/human/SD01-export/`。`surface_projection.csv` 保留全部 2,501 个点的索引、源 XY、绝对 XY、原始深度与状态；随附元数据保留扫描声明和来源。显示隐藏或色域裁剪不会删除导出点。

<a id="step-05"></a>
### 5. 保存并重新打开工程

按[保存与重开](../SOP.md#save)保存为 `work/human/SD01-projection.blend`，保留同名 `.qcdata/`。重开后检查点数、色表、等值线、原子投影与最后读取的网格点；再次读取一个点确认数据可用。移动工程时同时移动 `.blend` 和 `.qcdata/`。

<a id="inputs"></a>
## 准备自己的输入

距离图必须是未缩放的 Å 单位三列 `X Y depth`，每行一个点；支持乱序行和非方形规则网格。重复点、缺点、非有限值、非规则网格或与声明冲突的坐标会被拒绝。每轴至少两个点，总数不超过 250,000；每份文本输入不超过 64 MiB。

扫描 JSON 必须明确来源版本、物理量、坐标模式和范围。下面是本例的声明；自己的数据须按实际生成设置填写，不能直接套用其中数值：

```json
{
  "format": "qcblender.surface_projection.scan.v1",
  "producer": "Multiwfn",
  "producer_version": "2026.9.20",
  "coordinate_unit": "angstrom",
  "depth_unit": "angstrom",
  "coordinate_frame": "reference_cartesian",
  "depth_definition": "z_hit-z_start",
  "data_scale_factor": 1.0,
  "nx": 61,
  "ny": 41,
  "x_range_angstrom": [-7.0, 7.0],
  "y_range_angstrom": [-6.0, 7.0],
  "z_start_angstrom": 6.0,
  "z_end_angstrom": -6.0,
  "z_step_angstrom": 0.05,
  "surface": "union_of_open_vdw_spheres",
  "radius_scale": 1.0,
  "xy_mode": "relative_to_scan_min",
  "xy_offset_angstrom": [-7.0, -6.0]
}
```

`absolute` 表示源 XY 已是绝对坐标，偏移必须为 `[0,0]`；`relative_to_scan_min` 表示源 XY 从扫描起点计量，偏移必须等于 X、Y 下界，导入时只加一次。本例源 XY 为 `[0,14] × [0,13]`，应用偏移后为 `[-7,7] × [-6,7]`。

vdW 表面使用 `union_of_open_vdw_spheres` 和 `radius_scale`；若实际生成使用自由原子叠加密度或电子密度，分别声明 `promolecular_density` 或 `electron_density`，并提供 `density_isovalue_au`。这些类型的声明受支持，但本批真实数值参照仅覆盖上述 vdW 案例。

日志必须保留 Multiwfn 版本、最后一组扫描参数、表面条件及 `distmap.txt` 导出信息；声明和日志不符时应核查生成记录，不要修改日志来绕过检查。选择的静态分子与结果同源、同朝向仍由操作者确认，程序不能从三列数值证明任意分子的对应关系。

可选掩码的表头必须为 `ix,iy,state`，完整覆盖排序后的全部网格点。状态 `0` 为未命中、`1` 为有效、`2` 为未知；未命中只能用于扫描底值。只有生成过程或独立参照足以判断时才填写明确状态，否则省略掩码并保留未知。
