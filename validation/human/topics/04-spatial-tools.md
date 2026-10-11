# 空间观察与科学数据导出

[返回教程目录](../SOP.md#topics) · [切片](#slice) · [取点与剖面 CSV](#profile) · [裁剪与雾](#display)

路径相对材料根目录。接续[密度与 ESP](03-density-esp.md#mapping)的步骤 1–5；需要 **P03-atoms**、**QC electron_number_density** 和 **QC electrostatic_potential**。如已生成偶极或 P01 自旋密度，先在 **Display Layers** 隐藏这些额外层。

本页截图使用案例 `P03-` 前缀。

<a id="slice"></a>
## 切片与等值线

> 切片在一个平面上显示场值；Center 是视图局部坐标中的平面中心，Rotation 决定朝向，Width/Height 决定宽、高。101 点/轴表示平面有 101×101 个显示采样点，源网格仍为 0.2 Å。

1. 在 **Display Layers** 选 **QC electrostatic_potential**，点击 **创建视图与检查工具 → 创建切片**，确认对话框后选中新切片。在 **对象属性 → 空间观察** 设 **Center=(0,0,1.45) Å、Rotation=(0,0,0)、Width=6 Å、Height=6 Å**；在 **几何表示** 将 **显示采样数/轴** 设为 **101**，在 **颜色映射** 设 **−0.05 / 0 / +0.05 hartree/e**。隐藏两个独立场表面，按小键盘 `7` 从顶面观察，应看到有颜色的平面。

> 等值线连接平面上相同场值的位置；阈值列表指定要画出的各个场值，数值标签在曲线旁标出该值。这里选择几何场，即切片自身的 ESP，线值单位为 hartree/e。

2. 在切片的 **切片等值线** 面板点击 **开启等值线**，选择 **几何场**，在 **阈值列表** 输入 **−0.02,0,0.02**，勾选 **数值标签**，点击 **更新等值线**。应在有效区域看到曲线和数值标签。截图保存为 `human/screenshots/P03-slice.png`。

![ESP 平面切片与三组等值线](../screenshots/P03-slice.png)

> Three source atoms 用三个源原子的位置确定平面，Associated atom view 指定提供这些原子的视图。Gizmo 是可用鼠标拖动的视图操作手柄。

3. 在 **空间观察 → 按源网格或三个原子定平面** 中，选 **Plane=Three source atoms**、**Associated atom view=P03-atoms**，输入源编号 **2、1、4**。确认后，切片应转到包含这三个原子的平面。在三维视图工具栏选择 **QC Slice Gizmo**，拖动一次平移或旋转手柄，应能直接调整切片；再点 **更新等值线**，曲线随当前平面更新。

<a id="profile"></a>
## 取点与剖面 CSV

4. 在 **Display Layers** 选 **QC electrostatic_potential**；打开 **3D Viewport → N → View → 3D Cursor**，设坐标 **(0,0,1.45) Å**。点击 **QCBlender → 创建视图与检查工具 → 读取游标处场值**，应得到这个位置的 ESP 读数，单位为 **hartree/e**。

> 探针（Probe）读取指定位置的场值。绑定色场是这层表面所采用的着色数据；在本例密度表面上读取的是 ESP，“几何场”则读取形成表面的密度。

5. 在 **Display Layers** 显示并选中 **QC electron_number_density**，点击 **创建视图与检查工具 → 点击探针 · 绑定色场**。在表面点击一个位置，按 `Enter` 确认；应显示所点击位置的 ESP 及其单位。截图保存为 `human/screenshots/P03-probe.png`。

![密度表面上的取点位置及绑定 ESP 读数](../screenshots/P03-probe.png)

> 剖面沿一条直线采样，生成一组距离与场值。Sample field=Geometry 读取当前视图的几何场，Color 读取其绑定色场；本步选中 ESP 视图，因此 Geometry 读取 ESP。Samples 是包括两个端点在内的采样点数。**QC line profile data** 是这次采样的记录对象，供查看属性和导出 CSV。

6. 重新选 **QC electrostatic_potential**，将 **3D Cursor** 设为 **(0,−2,1.45) Å**，点击 **创建视图与检查工具 → 记录剖面起点**。将游标改为 **(0,+2,1.45) Å**，点击 **采样线剖面数据**，设 **Sample field=Geometry、Samples=101** 并确认。应新增 **QC line profile data**。

7. 选 **QC line profile data**，点击 **工程与诊断 → 导出数据与参数摘要**，设 **Data=profile**，选择材料根下 `work/human/exports/` 的实际绝对路径并确认。按 **Data exported:** 提示打开新子目录，应有 **profile.csv** 和 **metadata.json**。CSV 应包含 **101 行数据（不含表头）**，`distance_angstrom` 从 **0** 到 **4**，`unit` 为 **hartree/e**，并带有 `valid` 列。

> `profile.csv` 保存采样点的距离、坐标、场值和单位，可在表格或绘图软件中查看沿线变化。`valid` 表示该采样点是否有有效场值；无效点的场值留空。配套 `metadata.json` 用于核对来源、单位和采样条件，应与 CSV 一起保留；共同文件说明见[数据导出](../SOP.md#export)。

<a id="display"></a>
## 裁剪与体积雾

> 裁剪隐藏部分显示几何；原始原子坐标保持不变。Enabled 是对应裁剪的开关；Plane Origin 指定平面经过的位置，Plane Normal 指向保留的一侧。Box Minimum/Maximum 是盒子各轴的最小、最大坐标，盒外隐藏；这些位置均使用视图局部坐标。

8. 在 **Display Layers** 只显示并选中 **P03-atoms**，点击 **创建视图与检查工具 → 添加裁剪控件**。在 **对象属性 → 空间观察** 开启 **Plane Enabled**，设 **Plane Origin=(0,0,1.45) Å、Plane Normal=(0,0,1)**，应只显示上方水分子。关闭平面，开启 **Box Enabled**，设 **Box Minimum=(−0.5,−2,−2) Å、Box Maximum=(0.5,2,5) Å**，应看到两个氧及部分键几何。最后关闭两个 Enabled，恢复完整分子。

> 体积雾把场显示为空间中的半透明分布；Opacity Scale 是显示不透明度的缩放因子，设为 0 时透明，不改变电子密度值。

9. 选 **QC electron_number_density**，点击 **创建视图与检查工具 → 创建体积雾**，选新雾层。在 **Display Layers** 只保留雾层与 **P03-atoms** 可见；切到视口右上角 **Rendered**。在 **Properties → Material → QCBlender · 节点材质** 将 **Opacity Scale** 设为 **40**，应在分子周围看到雾；改为 **0**，雾应消失，再恢复 **40**。截图保存为 `human/screenshots/P03-fog.png`。

![密度体积雾及显示不透明度控件](../screenshots/P03-fog.png)
