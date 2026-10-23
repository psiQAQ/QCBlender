# 密度、ESP、电荷与偶极

[返回教程目录](../SOP.md#topics)

## 目录

- [密度表面按 ESP 着色](#mapping)
  - [1. 导入水二聚体并查看计算记录](#step-01)
  - [2. 生成电子密度场](#step-02)
  - [3. 生成静电势场](#step-03)
  - [4. 用 ESP 为密度表面着色](#step-04)
  - [5. 设置颜色范围与图例布局](#step-05)
- [应用色带预设](#presets)
  - [6. 应用 Viridis 色带预设](#step-06)
  - [7. 比较 Cividis 并练习撤销与重做](#step-07)
  - [8. 核对颜色反转与预设保留的参数](#step-08)
- [原子电荷与偶极](#charges)
  - [9. 按 Mulliken 电荷为原子着色](#step-09)
  - [10. 创建偶极箭头并调整显示长度](#step-10)
- [选择其他密度](#densities)
  - [11. 生成氧分子的非零自旋密度](#step-11)

路径相对材料根目录。按[准备新工程](../SOP.md#new-scene)创建场景。完成本页步骤 1–5 后，即可接着做[空间观察](04-spatial-tools.md)或[外部 ESP 与 AIM](06-esp-aim.md)，两页继续使用这里的 P03 对象。

本页水二聚体截图使用 `P03-` 前缀，氧分子自旋密度截图使用 `P01-` 前缀。

<a id="mapping"></a>
## 密度表面按 ESP 着色

<a id="step-01"></a>
### 1. 导入水二聚体并查看计算记录

- 点击 **N 侧栏 → 导入与导出（Import and Export） → 导入（Import） → 导入 Gaussian / Cube / XYZ（Import Gaussian / Cube / XYZ）**，选择 [shared/data/public/gaussian-v1/P03/water-dimer.fchk](../../shared/data/public/gaussian-v1/P03/water-dimer.fchk)并完成导入。
- 选中新原子对象，按 `F2` 命名为 **P03-atoms**。应有 **O/H/H/O/H/H** 六个原子；点击 **打开对象属性（Open Object Properties）**，在 **科学记录与振动模式（Scientific Records and Vibration Modes）** 查看电子总能量，应约为 **−152.027859 Eh**。
- 本样本为 Gaussian 16 C.01 的 **RHF/6-31G(d)** 优化构型，FCHK 中保留该构型的波函数。

<details>
<summary>了解电子密度、ESP、计算段与能量单位</summary>

> 电子密度表示空间中电子数的分布。ESP 是静电势，描述单位正试探电荷在该位置的势能。

> Eh（Hartree）是能量单位；RHF 是本例所用计算方法的名称，6-31G(d) 是基组名称，两者说明这份能量的计算条件。

</details>

<a id="step-02"></a>
### 2. 生成电子密度场

- 选 **P03-atoms**，重新打开该对象属性，点击 **对象属性（Object Properties） → 创建视图与工具（Create Views and Tools） → 计算（Compute） → 生成量子化学场（Generate Quantum Field）**。
- 首次使用先等待自动检查，在生成对话框设 **物理量（Quantity）=电子密度（Electron density）**、**网格间距（Grid spacing）=0.2**、**网格边距（Grid margin）=3**、**内存预算（Memory budget）=512**，点击 **确定（OK）** 并等待完成。应生成默认名为 **QC electron_number_density** 的场对象，单位为 **electron/bohr^3**；选中它，按 `F2` 命名为 **P03-density**。

<details>
<summary>了解电子密度、ESP 与自旋通道</summary>

> electron/bohr^3 表示每立方 bohr 的电子数；hartree/e 表示每单位元电荷的势能，用于描述 ESP。网格和内存参数的用途见[主线参数表](../SOP.md#orbital)。

**生成量子化学场（Generate Quantum Field） → 物理量（Quantity）** 决定要从这份计算结果生成哪一种空间场。本节先生成两种场，分别用来确定表面外形和颜色：

> Alpha、Beta 是两个自旋通道。电子总密度是两通道密度之和，自旋密度在这里采用 Alpha 密度减去 Beta 密度的约定。

- **电子密度（Electron density）**：电子总密度，即 Alpha 与 Beta 两个自旋通道密度之和。用于画出分子周围的密度表面。
- **静电势（Electrostatic potential）**：包含核与电子贡献的静电势。本例用它为密度表面着色，观察同一表面上不同位置的 ESP。

其他密度选项的区别与自旋密度案例见本页[选择其他密度](#densities)；轨道选项 **分子轨道（Molecular orbital）** 见[主线轨道案例](../SOP.md#orbital)。

</details>

<a id="step-03"></a>
### 3. 生成静电势场

在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 点击 **P03-atoms** 行最左侧的选择图标，重新打开该对象属性，用相同入口和网格参数生成 **物理量（Quantity）=静电势（Electrostatic potential）**，点击 **确定（OK）** 并等待完成。应生成默认名为 **QC electrostatic_potential** 的场对象，单位为 **hartree/e**；选中它，按 `F2` 命名为 **P03-esp**。

<a id="step-04"></a>
### 4. 用 ESP 为密度表面着色

- 选 **P03-density**，重新点击 **打开对象属性（Open Object Properties）**，在 **几何表示（Geometry Representation）** 设 **正值阈值（Positive Isovalue）=0.004**。
- 点击 **颜色映射（Color Mapping） → 选择／替换着色场（Select / Replace Color Field）**，在 **场（Field）** 选 **P03-esp**，设 **颜色最小值（Color minimum）=−0.05、颜色最大值（Color maximum）=0.05** 并点击 **确定（OK）**。

- 截图保存为 `human/screenshots/P03-density-esp-binding.png`。

![密度几何视图选择ESP着色场和hartree/e颜色范围](../screenshots/P03-density-esp-binding.png)

- 在 Outliner 关闭独立 **P03-esp** 表面的眼睛和相机图标，保留映射后的密度表面与 **P03-atoms**。
- 在 **材质预览（Material Preview）** 中，密度表面应出现随位置变化的颜色。

<details>
<summary>了解密度几何与 ESP 着色</summary>

> 这里用密度确定表面位置，用 ESP 确定颜色。隐藏独立 ESP 表面后，着色仍使用它的场数据。

**选择／替换着色场（Select / Replace Color Field） → 场（Field）** 选择提供颜色数值的场。首次建立映射时，**颜色最小值（Color minimum） / 颜色最大值（Color maximum）** 设置色带范围；以后替换着色场会保留现有范围，需要按新场的单位核对。本例选择 ESP，图例和颜色范围因此采用 **hartree/e**。

</details>

<a id="step-05"></a>
### 5. 设置颜色范围与图例布局

- 保持密度表面活动，在 **颜色映射（Color Mapping）** 设 **颜色最小值（Color Minimum）=−0.05、颜色中心值（Color Center）=0、颜色最大值（Color Maximum）=0.05**。
- 在 **图例排版（Legend Layout）** 开启 **显示图例（Show Legend）**，设 **长度（Length）=2.6、宽度（Width）=0.25、字号（Text Size）=0.2、小数位数（Decimal Places）=3、位置（Position）=(3.5,0,0)、旋转（Rotation）=(1.5707963,0,0) 弧度**；界面按当前精度回显约 **1.571 / 0 / 0**。
- 在三维视图按小键盘 `1` 切到 **前视图（Front）**，观察旋转后的图例；应能读清 **hartree/e** 与上述范围。

- 截图保存为 `human/screenshots/P03-legend-layout.png`。

![ESP色域、图例尺寸与位置，以及实际表面和单位图例](../screenshots/P03-legend-layout.png)

- 在 **属性（Properties） → 材质（Material） → QCBlender · 节点材质（QCBlender · Node Materials）** 把 **反转（0 或 1）（Reverse (0 or 1)）** 设为 **1**，表面和图例应一起反转颜色，再恢复 **0**。

<details>
<summary>了解颜色范围与图例布局</summary>

> 色带把数值范围映射为颜色。颜色范围决定哪些数值对应色带的低端、中点和高端，适合让不同视图使用同一尺度比较；范围外的有效值使用端点颜色。

- **颜色最小值（Color Minimum）**：色带低端对应的值，本例设为 **−0.05 hartree/e**。
- **颜色中心值（Color Center）**：色带中点对应的值，本例设为 **0 hartree/e**，将正负 ESP 分开放在中点两侧。
- **颜色最大值（Color Maximum）**：色带高端对应的值，本例设为 **0.05 hartree/e**。
- **反转（0 或 1）（Reverse (0 or 1)）**：`0` 使用当前颜色顺序，`1` 反转颜色顺序；适合调整配色方向，不改变 ESP 场值。

> 图例标出颜色对应的数值和单位。长度、宽度调整色条尺寸，字号调整文字大小；位置以当前视图对象为参考，尺寸和位置均使用视图局部布局单位。小数位数控制图例标签的显示精度。

</details>

<a id="presets"></a>
## 应用色带预设

本节接续上面的密度/ESP 表面，也可在 [Cube 专题](02-cube.md#mapping)已完成着色的表面或已有标量着色的切片上操作。先选要改变配色的视图，保持它的图例可见。由其他专题跳到本节时，完成步骤 6–8 后返回原专题；继续本页步骤 9 则需要步骤 1–5 的 P03 工程。

<a id="step-06"></a>
### 6. 应用 Viridis 色带预设

- 共享目标材质的视图及图例会一起更新。
- 需要独立配色时，先重新打开目标的对象属性，用 **显示层管理（Display Layer Management） → 复制（Duplicate）** 创建展示副本，再选副本应用预设。

- 打开 **属性（Properties） → 材质（Material） → QCBlender · 节点材质（QCBlender · Node Materials）**，在 **颜色映射（Color map）** 下点击 **应用色带预设…（Apply Color Ramp Preset…）**。
- 查看对话框中的目标材质，将 **色带预设（Color Ramp Preset）** 选为 **Viridis**，点击 **确定（OK）**。
- 表面与图例应一起换色；图例的量名、单位和数值范围保持原样。
- 使用本页密度/ESP 案例时，截图保存为 `human/screenshots/P03-color-presets.png`。

![色带预设入口、使用 Viridis 的 ESP 着色密度表面及 hartree/e 图例](../screenshots/P03-color-presets.png)

<details>
<summary>比较 QC Default、Viridis 与 Cividis</summary>

**色带预设（Color Ramp Preset）** 提供一组颜色与插值设置，适合快速统一图的配色。物理量、单位和数值范围继续由当前视图决定。按当前图的阅读目的选择：

- **QC 默认（QC Default）**：低端红、中点白、高端蓝，适合在本例中区分零点两侧的正负 ESP。
- **Viridis**：从紫色经蓝绿色到黄色连续变化，适合观察数值由低到高的分布；零点的位置仍按图例读取。
- **Cividis**：从深蓝到黄色连续变化，也适合观察数值高低；可与 Viridis 比较，选择更容易辨认细节的一种。

上述颜色顺序以 **反转（Reverse）=0** 为准。本节先应用 Viridis，再比较 Cividis，并练习取消、撤销和重做。

</details>

<a id="step-07"></a>
### 7. 比较 Cividis 并练习撤销与重做

- 再次打开对话框，选择 **Cividis** 后点击 **取消（Cancel）**，应保留刚才的 Viridis；重新打开，选择 **Cividis** 并点击 **确定（OK）**。
- 确认后可用 **编辑（Edit） → 撤销（Undo）** 恢复上一次色带，再用 **编辑（Edit） → 重做（Redo）** 重做。

<a id="step-08"></a>
### 8. 核对颜色反转与预设保留的参数

- 将 **反转（0 或 1）（Reverse (0 or 1)）** 设为 **1**，表面和图例应一起反转颜色。
- 此时再次应用一个预设，反转值应仍为 **1**；最后恢复 **反转（Reverse）=0**。
- 观察 **颜色最小值（Color Minimum） / 颜色中心值（Color Center） / 颜色最大值（Color Maximum）**、透明度和图例位置，应用预设后这些值应保持原样。

<details>
<summary>了解共享材质与图例同步</summary>

> 材质可以被多个视图共享。对话框中所列材质的所有使用者，以及使用它的图例，都会一起更新。

</details>

- 如果提示目标改变、材质只读或无法确认色带，先取消，重新选中可编辑的标准 QC 着色视图，再打开对话框。
- 确认会替换当前的自定义色阶和插值；希望保留手工配色时可先复制显示层。

<a id="charges"></a>
## 原子电荷与偶极

<a id="step-09"></a>
### 9. 按 Mulliken 电荷为原子着色

- 在 Outliner 暂时关闭密度表面的眼睛图标，再在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 选择 **P03-atoms**。
- 重新点击 **打开对象属性（Open Object Properties）**，在 **科学记录与振动模式（Scientific Records and Vibration Modes） → 设置原子电荷着色（Set Atomic Charge Colors）** 选 **Mulliken**，点击 **确定（OK）**。
- 在 **图例排版（Legend Layout）** 开启 **显示图例（Show Legend）**；氧应显示为负电荷一侧的红色，氢为正电荷一侧的蓝色，图例单位为 **e**。
- 在 **颜色映射（Color Mapping）** 将 **电荷最大值（Charge Maximum）** 改为 **0.5 e**，观察颜色范围变化。
- 原子电荷也可按上面的 **应用色带预设…（Apply Color Ramp Preset…）** 更换配色；图例继续使用当前布居方法与 **e**，颜色对应关系以该图例为准。

<details>
<summary>了解 Mulliken 电荷与颜色范围</summary>

> Mulliken 电荷是按一种电子分配方法得到的原子部分电荷，单位 e 为元电荷。电荷最大值（Charge Maximum）设置色带高端对应的电荷值，不改变原子电荷数据。

**设置原子电荷着色（Set Atomic Charge Colors） → 电荷方法（Charge method）** 选择源文件中已有的原子电荷方法；列表随文件内容变化，操作不会重新计算另一种电荷。本例源文件提供 **Mulliken**，选它后可用原子颜色查看各原子的部分电荷。**最小值（e）（Minimum (e)）** 和 **最大值（e）（Maximum (e)）** 设置初始颜色范围，后续在 **颜色映射（Color Mapping）** 调整。

</details>

<a id="step-10"></a>
### 10. 创建偶极箭头并调整显示长度

- 保持 **P03-atoms** 活动，重新打开该对象属性，点击 **对象属性（Object Properties） → 创建视图与工具（Create Views and Tools） → 空间工具（Spatial Tools） → 创建偶极矢量（Create Dipole Vector）**。
- 在 **N 侧栏 → QC 对象导航（QC Object Navigation）** 点击新对象 **QC dipole (Debye; physical direction)** 行最左侧的选择图标，切到 **属性（Properties） → 修改器（Modifiers）**。
- 如果属性编辑器顶部仍显示 **P03-atoms**，点击右上角已启用的图钉解除固定，让面板跟随当前选中的偶极对象；此处再次点击 **打开对象属性（Open Object Properties）** 会固定到来源原子对象。
- 确认顶部显示 **QC dipole**，将 **每 Debye 对应的 Å（Angstrom per Debye）** 从 **0.5** 改为 **1.5**；箭头方向保持不变、长度变为三倍。本例源偶极以 **+Z** 分量为主，并有较小的 **−X** 分量；不要通过修改显示方向把它强行对齐 Z 轴。
- 截图保存为 `human/screenshots/P03-charge-dipole.png`。

![水二聚体的原子电荷颜色和偶极箭头](../screenshots/P03-charge-dipole.png)

<details>
<summary>了解偶极矩与显示长度</summary>

> 偶极矢量用大小和方向描述电荷分布；Debye 是偶极矩单位。修改器（Modifiers）是调节几何处理参数的修改器面板；每 Debye 对应的 Å（Angstrom per Debye）设置每 Debye 对应的箭头显示长度，单位为 Å，不改变源偶极矩。

</details>

- 继续空间观察前，选 **P03-atoms**，重新打开该对象属性，在 **图例排版（Legend Layout）** 关闭原子电荷的 **显示图例（Show Legend）**，避免与密度表面的 ESP 图例重叠。
- 在 Outliner 关闭偶极层的眼睛、相机图标，恢复密度表面；独立 ESP 表面保持隐藏。

<a id="densities"></a>
## 选择其他密度

<a id="step-11"></a>
### 11. 生成氧分子的非零自旋密度

本练习改用开壳层氧分子；完成后恢复水二聚体的显示，再继续其他 P03 专题。

- 若要看非零自旋密度，在同一工程导入 [shared/data/public/gaussian-v1/P01/o2-uhf.fchk](../../shared/data/public/gaussian-v1/P01/o2-uhf.fchk)，选新氧分子原子对象，按 `F2` 命名为 **P01-spin-atoms**，重新打开该对象属性，在 **创建视图与工具（Create Views and Tools） → 计算（Compute） → 生成量子化学场（Generate Quantum Field）** 生成 **物理量（Quantity）=自旋密度（Spin density）**，使用 **0.2 Å / 3 Å / 512 MiB**，点击 **确定（OK）** 并等待完成。
- 选新生成的 **QC spin_density**，按 `F2` 命名为 **P01-spin-density**，点击 **打开对象属性（Open Object Properties）**，设 **正值阈值（Positive Isovalue）=0.002 electron/bohr^3**。
- 在 Outliner 暂时关闭 P03 分子和密度表面的眼睛图标，应看到氧分子周围的自旋密度。
- 截图保存为 `human/screenshots/P01-spin-density.png`。

![氧分子的非零自旋密度](../screenshots/P01-spin-density.png)

- 需要保留本练习时，按[共同保存方法](../SOP.md#save)另存为 `work/human/gaussian-v1/P01/P01-spin-density.blend`，保留同名 `.qcdata/`。

看完后关闭 **P01-spin-atoms** 和 **P01-spin-density** 的眼睛、相机图标，恢复 **P03-atoms** 与按 ESP 着色的密度表面；独立 **P03-esp** 表面和偶极层保持隐藏，便可继续 P03 专题。

<details>
<summary>了解 Alpha、Beta、自旋密度与闭壳层</summary>

当需要区分两个自旋通道，或观察它们的差异时，在 **生成量子化学场（Generate Quantum Field） → 物理量（Quantity）** 选择下面的密度，网格操作与步骤 2 相同。

> 闭壳层指电子成对占据空间轨道，本例水二聚体的两个通道相同。

- **Alpha 密度（Alpha density）**：只看 Alpha 自旋通道的电子密度，适合单独观察该通道的空间分布。
- **Beta 密度（Beta density）**：只看 Beta 自旋通道的电子密度，可与 Alpha 密度比较。
- **自旋密度（Spin density）**：Alpha 密度减去 Beta 密度，适合查看两个通道的差异；正值表示 Alpha 密度较大，负值表示 Beta 密度较大。

本页水二聚体是闭壳层，两个通道相同，自旋密度为零。下面改用开壳层氧分子生成非零自旋密度；完成后恢复水二聚体的显示，继续其他 P03 专题。

</details>
