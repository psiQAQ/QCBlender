# 空间观察与科学数据导出

[返回教程目录](../SOP.md#topics)

## 目录

- [切片与等值线](#slice)
  - [1. 创建 ESP 切片并设置观察范围](#step-01)
  - [2. 绘制 ESP 等值线](#step-02)
  - [3. 按原子定平面并拖动切片](#step-03)
- [取点与剖面 CSV](#profile)
  - [4. 读取指定坐标处的 ESP](#step-04)
  - [5. 在密度表面点击读取 ESP](#step-05)
  - [6. 沿两个游标位置采样 ESP 剖面](#step-06)
  - [7. 导出剖面 CSV 并核对采样范围](#step-07)
- [裁剪与体积雾](#display)
  - [8. 用平面和盒子裁剪分子显示](#step-08)
  - [9. 创建密度体积雾并调整不透明度](#step-09)


路径相对材料根目录。完成[密度与 ESP](03-density-esp.md#mapping)步骤 1–5 后，在同一工程继续本页，无需完成该页其他小节。需要 **P03-atoms**、按 ESP 着色的 **QC electron_number_density** 和独立 **QC electrostatic_potential**；前两层可见，独立 ESP 表面隐藏。如已生成偶极或 P01 自旋密度，先在 **显示层（Display Layers）** 隐藏这些额外层。

本页截图使用案例 `P03-` 前缀。

<a id="slice"></a>
## 切片与等值线

<a id="step-01"></a>
### 1. 创建 ESP 切片并设置观察范围

> 切片在一个平面上显示场值，适合观察分子内部或两分子之间的分布。视图局部坐标以该对象的原点和坐标轴为参考。

- **中心（Center）**：平面的中心位置，用于移动观察截面。
- **旋转（Rotation）**：平面的朝向；本例先用零旋转从顶面观察。
- **宽度（Width） / 高度（Height）**：平面的宽、高，用于确定观察范围。
- **显示采样数/轴（Display Samples per Axis）**：每个方向的显示采样点数。101 表示 101×101 个点；加密显示采样不会加密源网格，本例源网格仍为 0.2 Å。

在 **显示层（Display Layers）** 点击 **QC electrostatic_potential** 行最左侧的选择图标；它会重新显示该层。点击 **N 侧栏 → 创建视图与检查工具（Create Views and Inspection Tools） → 创建切片（Create Slice）**，点击 **确定（OK）**。新切片名为 **QC scalar slice**，选中它并点击 **对象属性与显示参数（Object Properties and Display Parameters）**。在 **空间观察（Spatial View）** 设 **中心（Center）=(0,0,1.45) Å、旋转（Rotation）=(0,0,0)、宽度（Width）=6 Å、高度（Height）=6 Å**；在 **几何表示（Geometry Representation）** 将 **显示采样数/轴（Display Samples per Axis）** 设为 **101**，在 **颜色映射（Color Mapping）** 设 **颜色最小值（Color Minimum） / 颜色中心值（Color Center） / 颜色最大值（Color Maximum）=−0.05/0/+0.05 hartree/e**。关闭密度和独立 ESP 表面的眼睛图标，保留切片与 **P03-atoms** 可见；鼠标移入视口，按小键盘 `7`，或选择视口菜单 **视图（View） → 视图（Viewpoint） → 顶视图（Top）**，从顶面观察，应看到有颜色的平面。

<a id="step-02"></a>
### 2. 绘制 ESP 等值线

> 等值线连接平面上相同场值的位置，便于比较各区域的数值。阈值列表（Isovalue List）指定要画出的各个场值，数值标签（Value Labels）在曲线旁标出该值。

- **几何场（Geometry Field）**：读取切片自身的场；本例是 ESP，线值单位为 hartree/e。
- **绑定色场（Bound Color Field）**：读取另外绑定的着色场，适合切片自身的场与着色量不同时使用；需要先有色场绑定。

在切片的 **切片等值线（Slice Contours）** 面板点击 **开启等值线（Enable Contours）**，选择 **几何场（Geometry Field）**，在 **阈值列表（Isovalue List）** 输入 **−0.02,0,0.02**，勾选 **数值标签（Value Labels）**，点击 **更新等值线（Update Contours）**。应在有效区域看到曲线和数值标签（Value Labels）。截图保存为 `human/screenshots/P03-slice.png`。

![ESP 平面切片与三组等值线](../screenshots/P03-slice.png)

<a id="step-03"></a>
### 3. 按原子定平面并拖动切片

**平面（Plane）** 用于选择平面的定位依据。需要复现某个截面时按网格或原子定位；需要探索附近分布时可自由调整。

- **自由（Free）**：保留当前平面，之后用中心（Center）、旋转（Rotation）或手柄调整。
- **网格 ij（Grid ij） / 网格 jk（Grid jk） / 网格 ki（Grid ki）**：分别沿源网格的两条轴展开，在剩余轴上用 **网格位置（Grid position）** 定位。0 和 1 是该轴的两端，0.5 是中间；这些名称按源网格轴定义。
- **三个源原子（Three source atoms）**：用三个不共线的源原子位置确定平面；**关联原子视图（Associated atom view）** 指定提供原子的视图，编号沿用源文件中的原子顺序。

> Gizmo 是可用鼠标拖动的视图操作手柄。

保持 **QC scalar slice** 活动，点击 **空间观察（Spatial View） → 按源网格或三个原子定平面（Define Plane from Source Grid or Three Atoms）**，选 **平面（Plane）=三个源原子（Three source atoms）**、**关联原子视图（Associated atom view）=P03-atoms**，依次填 **第一／第二／第三源原子（First/Second/Third source atom）=2、1、4**，点击 **确定（OK）**。切片应转到包含这三个原子的平面。鼠标移入三维视图，按 `T` 显示工具栏（若已显示则无需按），选择 **QC 切片手柄（QC Slice Gizmo）**，拖动一次平移或旋转手柄，应能直接调整切片；再点 **更新等值线（Update Contours）**，曲线随当前平面更新。

<a id="profile"></a>
## 取点与剖面 CSV

<a id="step-04"></a>
### 4. 读取指定坐标处的 ESP

> 3D 游标（3D Cursor）是可用坐标定位的三维游标；本页用它指定读取场值的位置和线剖面的两个端点。

已知坐标时使用 **读取游标处场值（Read Field Value at Cursor）**；想从可见表面上选位置时使用下一步的点击探针。

在 **显示层（Display Layers）** 点击 **QC electrostatic_potential** 行最左侧的选择图标。打开 **3D 视图（3D Viewport） → N → 视图（View） → 3D 游标（3D Cursor）**，将 **位置（Location）** 的 X/Y/Z 设为 **(0,0,1.45) Å**。切回 N 侧栏的 **QCBlender** 页，点击 **创建视图与检查工具（Create Views and Inspection Tools） → 读取游标处场值（Read Field Value at Cursor）**，底部提示应给出这个位置的 ESP 读数，单位为 **hartree/e**；读完后关闭独立 ESP 表面的眼睛图标。

<a id="step-05"></a>
### 5. 在密度表面点击读取 ESP

> 探针（Probe）读取指定位置的场值；绑定色场（Bound Color Field）是这层表面所采用的着色数据。

- **点击探针 · 几何场（Click Probe · Geometry Field）**：读取形成当前表面的场；在本例密度表面上读取电子密度。
- **点击探针 · 绑定色场（Click Probe · Bound Color Field）**：在所点击的表面位置读取着色量；本例读取 ESP。

在 **显示层（Display Layers）** 关闭 **QC scalar slice** 的眼睛图标，点击 **QC electron_number_density** 行最左侧的选择图标，显示并选中密度表面。点击 **创建视图与检查工具（Create Views and Inspection Tools） → 点击探针 · 绑定色场（Click Probe · Bound Color Field）**，将鼠标移入视口，在密度表面点击一个位置；看到有效的 ESP 读数后按 `Enter` 确认。应显示所点击位置的 ESP 及其单位。截图保存为 `human/screenshots/P03-probe.png`。

![密度表面上的取点位置及绑定 ESP 读数](../screenshots/P03-probe.png)

<a id="step-06"></a>
### 6. 沿两个游标位置采样 ESP 剖面

> 剖面沿一条直线采样，生成一组距离与场值，用于观察两点之间的数值变化。**QC line profile data** 是这次采样的记录对象，供查看属性和导出 CSV。

**采样场（Sample field）** 决定沿线读取哪份数据：

- **几何（Geometry）**：读取当前视图的几何场（Geometry Field）；本步选中独立 ESP 视图，因此读取 ESP。
- **颜色（Color）**：读取当前视图的绑定色场（Bound Color Field）；例如在按 ESP 着色的密度表面上选择它，可沿线读取 ESP。只有存在色场绑定时才提供这个选项。

**采样点数（Samples）** 是包括两个端点在内的采样点数；它决定沿线取值的密度，源网格保持原样。起点记录在当前视图上，记录起点后应保持同一视图及其场绑定。

在 **显示层（Display Layers）** 点击 **QC electrostatic_potential** 行最左侧的选择图标。切到 N 侧栏的 **视图（View） → 3D 游标（3D Cursor）**，将 **位置（Location）** 设为 **(0,−2,1.45) Å**；切回 **QCBlender**，点击 **创建视图与检查工具（Create Views and Inspection Tools） → 记录剖面起点（Mark Profile Start）**。再到 **视图（View） → 3D 游标（3D Cursor）** 将游标改为 **(0,+2,1.45) Å**，切回 **QCBlender**，点击 **采样线剖面数据（Sample Line Profile Data）**。确认弹窗显示 **采样场（Sample field）: 几何（Geometry）**，设 **采样点数（Samples）=101** 并点击 **确定（OK）**。应新增并选中 **QC line profile data**。

<a id="step-07"></a>
### 7. 导出剖面 CSV 并核对采样范围

> `profile.csv` 保存采样点的距离、坐标、场值和单位，可在表格或绘图软件中查看沿线变化。`valid` 表示该采样点是否有有效场值；无效点的场值留空。配套 `metadata.json` 用于核对来源、单位和采样条件，应与 CSV 一起保留。

**数据（Data）=线剖面（profile）** 导出上一步保存的采样记录；导出前选择 **QC line profile data**，即可取得这条剖面。

保持 **QC line profile data** 活动，按[共同导出方法](../SOP.md#export)打开 **工程与诊断（Project and Diagnostics） → 导出数据与参数摘要（Export Data and Parameter Summary）**，设 **数据（Data）=线剖面（profile）**，在 **输出目录（Output directory）** 选择材料根目录下 `work/human/exports/` 的实际绝对路径，点击 **确定（OK）** 并等待完成。按 **数据已导出：（Data exported:）** 提示打开新子目录，应有 **profile.csv** 和 **metadata.json**。CSV 应包含 **101 行数据（不含表头）**，`distance_angstrom` 从 **0** 到 **4**，`unit` 为 **hartree/e**，并带有 `valid` 列。

<a id="display"></a>
## 裁剪与体积雾

<a id="step-08"></a>
### 8. 用平面和盒子裁剪分子显示

> 裁剪隐藏部分显示几何，用于看清被遮挡的内部区域；原始原子坐标保持不变。下列位置使用视图局部坐标。

- **启用平面裁剪（Plane Enabled）**：开启平面裁剪。**平面原点（Plane Origin）** 指定平面经过的位置，**平面法向量（Plane Normal）** 指向保留的一侧，适合沿一个截面观察。
- **启用包围盒裁剪（Box Enabled）**：开启盒子裁剪。**包围盒最小值（Box Minimum） / 包围盒最大值（Box Maximum）** 指定各轴的最小、最大坐标，盒外隐藏，适合保留一个有限区域。
- 两种裁剪同时开启时，仅保留同时满足两者的部分；要比较效果，先关闭一种再开启另一种。

在 **显示层（Display Layers）** 关闭其他显示层的眼睛图标，只显示并选中 **P03-atoms**，点击 **创建视图与检查工具（Create Views and Inspection Tools） → 添加裁剪控件（Add Clipping Controls）**。重新点击 **对象属性与显示参数（Object Properties and Display Parameters）**，在 **空间观察（Spatial View）** 开启 **启用平面裁剪（Plane Enabled）**，设 **平面原点（Plane Origin）=(0,0,1.45) Å、平面法向量（Plane Normal）=(0,0,1)**，应只显示上方水分子。关闭平面，开启 **启用包围盒裁剪（Box Enabled）**，设 **包围盒最小值（Box Minimum）=(−0.5,−2,−2) Å、包围盒最大值（Box Maximum）=(0.5,2,5) Å**，应看到两个氧及部分键几何。最后关闭 **启用平面裁剪（Plane Enabled）** 和 **启用包围盒裁剪（Box Enabled）**，恢复完整分子。

<a id="step-09"></a>
### 9. 创建密度体积雾并调整不透明度

> 体积雾把场显示为空间中的半透明分布，用于观察密度的空间延展。渲染（Rendered）使用场景的渲染设置预览效果。

**不透明度缩放（Opacity Scale）** 是显示不透明度的缩放因子：增大时雾更浓，设为 0 时透明；电子密度值保持原样。

在 **显示层（Display Layers）** 点击 **QC electron_number_density** 行最左侧的选择图标，点击 **创建视图与检查工具（Create Views and Inspection Tools） → 创建体积雾（Create Volume Fog）**。新雾层名为 **QC volume fog**；选中它，重新点击 **对象属性与显示参数（Object Properties and Display Parameters）**。在 **显示层（Display Layers）** 关闭密度表面的眼睛图标，只保留雾层与 **P03-atoms** 可见。切到视口右上角 **渲染（Rendered）**，再切到 **属性（Properties） → 材质（Material） → QCBlender · 节点材质（QCBlender · Node Materials）**，将 **不透明度缩放（Opacity Scale）** 设为 **40**，应在分子周围看到雾；改为 **0**，雾应消失，再恢复 **40**。截图保存为 `human/screenshots/P03-fog.png`。

![密度体积雾及显示不透明度控件](../screenshots/P03-fog.png)

继续其他 P03 专题前，关闭雾层的眼睛、相机图标，显示 **P03-atoms** 和按 ESP 着色的密度表面，独立 ESP 表面保持隐藏；切回 **材质预览（Material Preview）**。
