# 空间观察与科学数据导出

[返回教程目录](../SOP.md#topics) · [切片](#slice) · [取点与剖面 CSV](#profile) · [裁剪与雾](#display)

路径相对材料根目录。完成[密度与 ESP](03-density-esp.md#mapping)步骤 1–5 后，在同一工程继续本页，无需完成该页其他小节。需要 **P03-atoms**、按 ESP 着色的 **QC electron_number_density** 和独立 **QC electrostatic_potential**；前两层可见，独立 ESP 表面隐藏。如已生成偶极或 P01 自旋密度，先在 **Display Layers** 隐藏这些额外层。

本页截图使用案例 `P03-` 前缀。

<a id="slice"></a>
## 切片与等值线

> 切片在一个平面上显示场值；Center 是视图局部坐标中的平面中心，局部坐标以该对象的原点和坐标轴为参考。Rotation 决定朝向，Width/Height 决定宽、高。101 点/轴表示平面有 101×101 个显示采样点，源网格仍为 0.2 Å。

1. 在 **Display Layers** 点击 **QC electrostatic_potential** 行最左侧的选择图标；它会重新显示该层。点击 **N 侧栏 → 创建视图与检查工具 → 创建切片**，点击 **OK**。新切片名为 **QC scalar slice**，选中它并点击 **对象属性与显示参数**。在 **空间观察** 设 **Center=(0,0,1.45) Å、Rotation=(0,0,0)、Width=6 Å、Height=6 Å**；在 **几何表示** 将 **显示采样数/轴** 设为 **101**，在 **颜色映射** 设 **Color Minimum/Center/Maximum=−0.05/0/+0.05 hartree/e**。关闭密度和独立 ESP 表面的眼睛图标，保留切片与 **P03-atoms** 可见；鼠标移入视口，按小键盘 `7`，或选择视口菜单 **View → Viewpoint → Top**，从顶面观察，应看到有颜色的平面。

> 等值线连接平面上相同场值的位置；阈值列表指定要画出的各个场值，数值标签在曲线旁标出该值。这里选择几何场，即切片自身的 ESP，线值单位为 hartree/e。

2. 在切片的 **切片等值线** 面板点击 **开启等值线**，选择 **几何场**，在 **阈值列表** 输入 **−0.02,0,0.02**，勾选 **数值标签**，点击 **更新等值线**。应在有效区域看到曲线和数值标签。截图保存为 `human/screenshots/P03-slice.png`。

![ESP 平面切片与三组等值线](../screenshots/P03-slice.png)

> Three source atoms 用三个源原子的位置确定平面，Associated atom view 指定提供这些原子的视图。Gizmo 是可用鼠标拖动的视图操作手柄。

3. 保持 **QC scalar slice** 活动，点击 **空间观察 → 按源网格或三个原子定平面**，选 **Plane=Three source atoms**、**Associated atom view=P03-atoms**，依次填 **First/Second/Third source atom=2、1、4**，点击 **OK**。切片应转到包含这三个原子的平面。鼠标移入三维视图，按 `T` 显示工具栏（若已显示则无需按），选择 **QC Slice Gizmo**，拖动一次平移或旋转手柄，应能直接调整切片；再点 **更新等值线**，曲线随当前平面更新。

<a id="profile"></a>
## 取点与剖面 CSV

> 3D Cursor 是可用坐标定位的三维游标；本页用它指定读取场值的位置和线剖面的两个端点。

4. 在 **Display Layers** 点击 **QC electrostatic_potential** 行最左侧的选择图标。打开 **3D Viewport → N → View → 3D Cursor**，将 **Location** 的 X/Y/Z 设为 **(0,0,1.45) Å**。切回 N 侧栏的 **QCBlender** 页，点击 **创建视图与检查工具 → 读取游标处场值**，底部提示应给出这个位置的 ESP 读数，单位为 **hartree/e**；读完后关闭独立 ESP 表面的眼睛图标。

> 探针（Probe）读取指定位置的场值。绑定色场是这层表面所采用的着色数据；在本例密度表面上读取的是 ESP，“几何场”则读取形成表面的密度。

5. 在 **Display Layers** 关闭 **QC scalar slice** 的眼睛图标，点击 **QC electron_number_density** 行最左侧的选择图标，显示并选中密度表面。点击 **创建视图与检查工具 → 点击探针 · 绑定色场**，将鼠标移入视口，在密度表面点击一个位置；看到有效的 ESP 读数后按 `Enter` 确认。应显示所点击位置的 ESP 及其单位。截图保存为 `human/screenshots/P03-probe.png`。

![密度表面上的取点位置及绑定 ESP 读数](../screenshots/P03-probe.png)

> 剖面沿一条直线采样，生成一组距离与场值。Sample field=Geometry 读取当前视图的几何场，Color 读取其绑定色场；本步选中 ESP 视图，因此 Geometry 读取 ESP。Samples 是包括两个端点在内的采样点数。**QC line profile data** 是这次采样的记录对象，供查看属性和导出 CSV。

6. 在 **Display Layers** 点击 **QC electrostatic_potential** 行最左侧的选择图标。切到 N 侧栏的 **View → 3D Cursor**，将 **Location** 设为 **(0,−2,1.45) Å**；切回 **QCBlender**，点击 **创建视图与检查工具 → 记录剖面起点**。再到 **View → 3D Cursor** 将游标改为 **(0,+2,1.45) Å**，切回 **QCBlender**，点击 **采样线剖面数据**。确认弹窗显示 **Sample field: Geometry**，设 **Samples=101** 并点击 **OK**。应新增并选中 **QC line profile data**。

7. 保持 **QC line profile data** 活动，按[共同导出方法](../SOP.md#export)打开 **工程与诊断 → 导出数据与参数摘要**，设 **Data=profile**，在 **Output directory** 选择材料根目录下 `work/human/exports/` 的实际绝对路径，点击 **OK** 并等待完成。按 **Data exported:** 提示打开新子目录，应有 **profile.csv** 和 **metadata.json**。CSV 应包含 **101 行数据（不含表头）**，`distance_angstrom` 从 **0** 到 **4**，`unit` 为 **hartree/e**，并带有 `valid` 列。

> `profile.csv` 保存采样点的距离、坐标、场值和单位，可在表格或绘图软件中查看沿线变化。`valid` 表示该采样点是否有有效场值；无效点的场值留空。配套 `metadata.json` 用于核对来源、单位和采样条件，应与 CSV 一起保留。

<a id="display"></a>
## 裁剪与体积雾

> 裁剪隐藏部分显示几何；原始原子坐标保持不变。Enabled 是对应裁剪的开关；Plane Origin 指定平面经过的位置，Plane Normal 指向保留的一侧。Box Minimum/Maximum 是盒子各轴的最小、最大坐标，盒外隐藏；这些位置均使用视图局部坐标。

8. 在 **Display Layers** 关闭其他显示层的眼睛图标，只显示并选中 **P03-atoms**，点击 **创建视图与检查工具 → 添加裁剪控件**。重新点击 **对象属性与显示参数**，在 **空间观察** 开启 **Plane Enabled**，设 **Plane Origin=(0,0,1.45) Å、Plane Normal=(0,0,1)**，应只显示上方水分子。关闭平面，开启 **Box Enabled**，设 **Box Minimum=(−0.5,−2,−2) Å、Box Maximum=(0.5,2,5) Å**，应看到两个氧及部分键几何。最后关闭两个 Enabled，恢复完整分子。

> 体积雾把场显示为空间中的半透明分布；Rendered 使用场景的渲染设置预览效果。Opacity Scale 是显示不透明度的缩放因子，设为 0 时透明，不改变电子密度值。

9. 在 **Display Layers** 点击 **QC electron_number_density** 行最左侧的选择图标，点击 **创建视图与检查工具 → 创建体积雾**。新雾层名为 **QC volume fog**；选中它，重新点击 **对象属性与显示参数**。在 **Display Layers** 关闭密度表面的眼睛图标，只保留雾层与 **P03-atoms** 可见。切到视口右上角 **Rendered**，再切到 **Properties → Material → QCBlender · 节点材质**，将 **Opacity Scale** 设为 **40**，应在分子周围看到雾；改为 **0**，雾应消失，再恢复 **40**。截图保存为 `human/screenshots/P03-fog.png`。

![密度体积雾及显示不透明度控件](../screenshots/P03-fog.png)

继续其他 P03 专题前，关闭雾层的眼睛、相机图标，显示 **P03-atoms** 和按 ESP 着色的密度表面，独立 ESP 表面保持隐藏；切回 **Material Preview**。
