# Cube 场与多场叠加

[返回教程目录](../SOP.md#topics)

## 目录

- [单场与双符号](#single)
  - [1. 导入 Cube 并声明物理量与单位](#step-01)
  - [2. 分别设置正负表面的阈值与显隐](#step-02)
  - [3. 切换表面样式并调整透明度](#step-03)
- [多 Cube 叠加](#overlay)
  - [4. 导入第二个 Cube 并设置等值表面](#step-04)
  - [5. 保留一份原子层并核对两场的独立阈值](#step-05)
  - [6. 观察叠加表面并保存工程](#step-06)
- [用另一个场着色](#mapping)
  - [7. 选择着色场并显示图例](#step-07)


路径相对材料根目录。按[准备新工程](../SOP.md#new-scene)创建场景，再开始本页操作。

本页截图使用案例 `P03-` 前缀。

> Cube 保存规则网格上的场值；标量场在每个网格点有一个数值。网格尺寸的三个数分别表示三个轴的采样点数。

<a id="single"></a>
## 单场与双符号

> `sign_lambda2_rho` 是外部分析生成的带符号电子密度，用于给相互作用区域着色；electron/bohr^3 表示每立方 bohr 的电子数。本例直接使用样本的原始数值。

<a id="step-01"></a>
### 1. 导入 Cube 并声明物理量与单位

**声明 Cube 物理量与单位（Identify Cube Quantity and Unit）** 用于告诉插件这些数值表示什么，供阈值、图例和后续分析使用。先根据生成 Cube 的计算确认量名与单位，再选择匹配的选项；声明操作不会换算数值。

> Alpha、Beta 是两个自旋通道；自旋密度在这里采用 Alpha 密度减去 Beta 密度的约定。轨道振幅表示轨道波函数的值，正负表示相位。

- **电子密度 [electron/bohr^3]（Electron density [electron/bohr^3]）**：用于电子总密度。
- **Alpha 减 Beta 自旋密度 [electron/bohr^3]（Alpha-minus-beta spin density [electron/bohr^3]）**：用于 Alpha 密度减去 Beta 密度的自旋密度。
- **静电势 [hartree/e]（ESP [hartree/e]）**：用于静电势。
- **轨道振幅 [bohr^-3/2]（Orbital amplitude [bohr^-3/2]）**：用于带正负相位的轨道振幅。
- **其他外部计算的标量场（Other externally computed scalar field）**：用于上面几项未涵盖的量。本例选择它，在 **物理量（Physical quantity）** 填量名，在 **单位（Unit）** 填原数值的单位；单位无法确认时填 `unknown`。

点击 **N 侧栏 → 导入与导出（Import and Export） → 导入（Import） → 导入 Gaussian / Cube / XYZ（Import Gaussian / Cube / XYZ）**，选择 [shared/data/public/P03/color.cube](../../shared/data/public/P03/color.cube)并完成导入。会新增六原子水二聚体和一个场表面；选中场表面，按 `F2` 命名为 **P03-color-surface**。点击 **打开对象属性（Open Object Properties）**，在对象属性点击 **声明 Cube 物理量与单位（Identify Cube Quantity and Unit）**，选择 **其他外部计算的标量场（Other externally computed scalar field）**，填 **物理量（Physical quantity）=sign_lambda2_rho**、**单位（无法确定时填 unknown）（Unit (use unknown if unavailable)）=electron/bohr^3**，点击 **确定（OK）** 并等待完成。对象属性应显示 **91×38×156 网格**与上述量、单位。

<a id="step-02"></a>
### 2. 分别设置正负表面的阈值与显隐

> 等值表面连接场值相同的位置。正、负阈值决定取哪一个场值画表面，单位沿用该场的单位；负值阈值（Negative Isovalue）填写绝对大小，例如填 `0.01` 表示取值为 `−0.01` 的表面。

- **显示正值（Show Positive Values）／显示负值（Show Negative Values）**：分别控制正侧和负侧表面是否可见，适合单独查看某一侧。
- **联动正负阈值（Link Thresholds）**：开启时，负侧沿用正侧阈值的大小，适合用相同绝对值比较两侧；取消后可分别设置两侧阈值。本例使用不同阈值，因此取消它。

在 **对象属性（Object Properties） → 几何表示（Geometry Representation）** 开启 **显示正值（Show Positive Values）、显示负值（Show Negative Values）**，取消 **联动正负阈值（Link Thresholds）**，设 **正值阈值（Positive Isovalue）=0.03、负值阈值（Negative Isovalue）=0.01**。在 **材质预览（Material Preview）** 中应看到两种符号的表面；分别关开正值、负值开关，确认对应部分能够独立显隐。截图保存为 `human/screenshots/P03-cube.png`。

![Cube 的正负表面、量名、单位及阈值](../screenshots/P03-cube.png)

<a id="step-03"></a>
### 3. 切换表面样式并调整透明度

> 样式决定等值表面怎样画出来；切换样式时仍使用同一场和阈值。

- **实面（Solid）**：显示连续表面，适合观察整体外形和颜色。
- **线框（Wireframe）**：显示表面的网格边，适合查看网格结构或减少遮挡；**线框半径（Wire Radius）** 调整线的粗细。
- **点（Points）**：显示表面的网格顶点，适合查看顶点分布；**点半径（Point Radius）** 调整点的大小。

> 正值不透明度（Positive Opacity）与负值不透明度（Negative Opacity）分别控制正、负表面的不透明度，值越小越透明；叠加场时可降低它们，让另一层表面更容易看见。

将 **样式（Style）** 依次切换为 **实面（Solid）、线框（Wireframe）、点（Points）**，应看到表面表示改变，最后恢复实面。在 **属性（Properties） → 材质（Material） → QCBlender · 节点材质（QCBlender · Node Materials）** 设 **正值不透明度（Positive Opacity）=0.6、负值不透明度（Negative Opacity）=0.3**，两种表面应有不同透明度。

<a id="overlay"></a>
## 多 Cube 叠加

> `delta_g_inter` 是该样本的片段间密度梯度差，单位 electron/bohr^4 比密度单位多除以一个长度单位。这里两份 Cube 来自同一水二聚体构型，原子顺序均为 O/H/H/O/H/H；两种场各自保留物理量和单位。

<a id="step-04"></a>
### 4. 导入第二个 Cube 并设置等值表面

再导入 [shared/data/public/P03/igmh/dg_inter.cub](../../shared/data/public/P03/igmh/dg_inter.cub)。这次也会新增一份原子层和一个场表面。选中新场表面，命名为 **P03-igmh-surface**，重新点击 **打开对象属性（Open Object Properties）**，使用同一声明按钮，选择 **其他外部计算的标量场（Other externally computed scalar field）**，填写 **物理量（Physical quantity）=delta_g_inter、单位（无法确定时填 unknown）（Unit (use unknown if unavailable)）=electron/bohr^4**，点击 **确定（OK）** 并等待完成。设 **正值阈值（Positive Isovalue）=0.005**，开启 **显示正值（Show Positive Values）**、关闭 **显示负值（Show Negative Values）**。

<a id="step-05"></a>
### 5. 保留一份原子层并核对两场的独立阈值

在 Outliner 保持 **P03-color-surface** 与 **P03-igmh-surface** 的眼睛、相机图标开启；保留 **color.cube** 来源分组的原子层，关闭另一份原子层的眼睛、相机图标，避免重叠。在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 用选择图标切换表面，每次重新点击 **打开对象属性（Open Object Properties）**：先将 **P03-color-surface** 的正值阈值（Positive Isovalue）暂改为 **0.02**，再选 **P03-igmh-surface**，它的阈值应仍为 **0.005**；将后者暂改为 **0.008**，返回前者确认仍为 **0.02**。最后分别恢复 **0.03 / 0.005**。

<a id="step-06"></a>
### 6. 观察叠加表面并保存工程

分别选中两层、重新打开各自的对象属性，在 **显示层管理（Display Layer Management）** 关闭、再开启眼睛图标，应只切换对应表面的视口可见性；相机图标控制该层是否参与渲染。最后让两层都可见，转到能分辨两个表面的角度。截图保存为 `human/screenshots/P03-cube-overlay.png`。

![同构型的两份 Cube 表面叠加及独立显示层](../screenshots/P03-cube-overlay.png)

在材料根目录创建 `work/human/P03/`，按[保存自包含工程](../SOP.md#save)保存为 `work/human/P03/P03-overlay.blend`，连同 `work/human/P03/P03-overlay.qcdata/` 一起保留。需要移动时，创建 `work/human/移动案例/`，将两者一起复制到该目录，重新打开其中的 `P03-overlay.blend`，两层应保留各自阈值与可见性。

<a id="mapping"></a>
## 用另一个场着色

> 几何场（Geometry Field）决定表面在哪里，着色场决定表面上各点的颜色。隐藏独立着色场表面后，其科学数据仍用于映射，图例采用着色场的单位。

<a id="step-07"></a>
### 7. 选择着色场并显示图例

**选择／替换着色场（Select / Replace Color Field）** 的 **场（Field）** 用来选提供颜色数值的场。本例保留 `delta_g_inter` 的表面外形，选择 `sign_lambda2_rho` 判断表面不同位置的场值。首次建立映射时，对话框的 **颜色最小值（Color minimum） / 颜色最大值（Color maximum）** 设置颜色范围；之后替换着色场会保留现有范围，需要按新场的单位自行核对。

> 色带把场值映射为颜色。颜色最小值（Color Minimum） / 颜色最大值（Color Maximum）指定色带两端对应的数值，颜色中心值（Color Center）指定中点对应的数值；范围外的有效值使用端点颜色，不会从科学数据中删去。

选 **P03-igmh-surface**，重新打开该对象属性，点击 **对象属性（Object Properties） → 颜色映射（Color Mapping） → 选择／替换着色场（Select / Replace Color Field）**，在 **场（Field）** 选择步骤 1 的 **P03-color-surface**，填 **颜色最小值（Color minimum）=−0.05、颜色最大值（Color maximum）=0.05**，点击 **确定（OK）**。在 Outliner 关闭 **P03-color-surface** 的眼睛和相机图标，保留映射后的 **P03-igmh-surface** 及步骤 5 的一份原子层。应看到 `delta_g_inter` 表面按 `sign_lambda2_rho` 场着色；开启 **图例排版（Legend Layout） → 显示图例（Show Legend）**，图例单位应为 **electron/bohr^3**。

需要更换配色时，接着使用[色带预设](03-density-esp.md#presets)；本专题保持 **颜色最小值（Color Minimum）=−0.05、颜色中心值（Color Center）=0、颜色最大值（Color Maximum）=0.05**，单位仍为 **electron/bohr^3**。
