# 密度、ESP、电荷与偶极

[返回教程目录](../SOP.md#topics) · [密度与 ESP](#mapping) · [色带预设](#presets) · [电荷与偶极](#charges) · [其他密度](#densities)

路径相对材料根目录。本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。后面的[空间观察](04-spatial-tools.md)和[外部 ESP 与 AIM](06-esp-aim.md)继续使用这里的 P03 对象。

本页水二聚体截图使用 `P03-` 前缀，氧分子自旋密度截图使用 `P01-` 前缀。

> 电子密度表示空间中电子数的分布。ESP 是静电势，描述单位正试探电荷在该位置的势能。

<a id="mapping"></a>
## 密度表面按 ESP 着色

> Eh（Hartree）是能量单位；RHF 是本例所用计算方法的名称，6-31G(d) 是基组名称，两者说明这份能量的计算条件。

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，选择 [shared/data/public/P03/water-dimer.fchk](../../shared/data/public/P03/water-dimer.fchk)。选中新原子对象，命名为 **P03-atoms**。应有 **O/H/H/O/H/H** 六个原子；在 **对象属性 → 科学记录与振动模式** 查看电子总能量，应约为 **−152.013820 Eh**。本样本计算条件为 **RHF/6-31G(d)**。

> electron/bohr^3 表示每立方 bohr 的电子数；hartree/e 表示每单位元电荷的势能，用于描述 ESP。网格和内存参数的用途见[主线参数表](../SOP.md#orbital)。

2. 选 **P03-atoms**，点击 **工作流 → 生成量子化学场**，设 **Quantity=Electron density**、**Grid spacing=0.2**、**Grid margin=3**、**Memory budget=512**，确认。应生成 **QC electron_number_density**，单位为 **electron/bohr^3**。

3. 再选 **P03-atoms**，用相同入口和网格参数生成 **Quantity=Electrostatic potential**。应生成 **QC electrostatic_potential**，单位为 **hartree/e**。

> 这里用密度确定表面位置，用 ESP 确定颜色。隐藏独立 ESP 表面后，着色仍使用它的场数据。

4. 选 **QC electron_number_density**，在 **对象属性 → 几何表示** 设 **正值阈值=0.004**。点击 **颜色映射 → 选择／替换着色场**，选 **QC electrostatic_potential**，设 **Color minimum=−0.05、Color maximum=0.05** 并确认。在 **Display Layers** 关闭独立 **QC electrostatic_potential** 表面的眼睛和相机图标，保留映射后的密度表面与 **P03-atoms**。在 **Material Preview** 中，密度表面应出现随位置变化的颜色。

> Color Minimum、Color Center、Color Maximum 分别指定色带低端、中点和高端对应的数值；Reverse=1 反转颜色顺序，不改变 ESP 场值。

> 图例标出颜色对应的数值和单位。长度、宽度调整色条尺寸，字号调整文字大小；位置以当前视图对象为参考，尺寸和位置均使用视图局部布局单位。小数位数控制图例标签的显示精度。

5. 保持密度表面活动，在 **颜色映射** 设 **Color Minimum=−0.05、Color Center=0、Color Maximum=0.05**。在 **图例排版** 开启 **显示图例**，设 **长度=2.6、宽度=0.25、字号=0.2、小数位数=3、位置=(3.5,0,0)**。转到能读清图例的视角；图例应显示 **hartree/e** 与上述范围。在 **Properties → Material → QCBlender · 节点材质** 把 **Reverse (0 or 1)** 设为 **1**，表面和图例应一起反转颜色，再恢复 **0**。

<a id="presets"></a>
## 应用色带预设

本节接续上面的密度/ESP 表面，也可在 [Cube 专题](02-cube.md#mapping)已完成着色的表面或已有标量着色的切片上操作。先选要改变配色的视图，保持它的图例可见。

> 色带把数值范围映射为颜色。预设提供一组颜色与插值设置；物理量、单位和数值范围继续由当前视图决定。

6. 打开 **Properties → Material → QCBlender · 节点材质**，在 **Color map** 下点击 **应用色带预设…**。查看对话框中的目标材质，将 **色带预设** 选为 **Viridis**，确认应用。表面与图例应一起换色；图例的量名、单位和数值范围保持原样。截图保存为 `human/screenshots/P03-color-presets.png`。

![色带预设入口、使用 Viridis 的 ESP 着色密度表面及 hartree/e 图例](../screenshots/P03-color-presets.png)

| 选项 | 用途 |
| --- | --- |
| QC Default | 使用 QC 原有的红—白—蓝配色 |
| Viridis | 使用紫、蓝绿到黄色的连续配色 |
| Cividis | 使用深蓝到黄色的连续配色 |

7. 再次打开对话框，选择 **Cividis** 后点击取消，应保留刚才的 Viridis；重新打开，选择 **Cividis** 并确认应用。确认后可用 **Edit → Undo** 恢复上一次色带，再用 **Edit → Redo** 重做。

8. 将 **Reverse (0 or 1)** 设为 **1**，表面和图例应一起反转颜色。此时再次应用一个预设，反转值应仍为 **1**；最后恢复 **Reverse=0**。观察 **Color Minimum / Center / Maximum**、透明度和图例位置，应用预设后这些值应保持原样。

> 材质可以被多个视图共享。对话框中所列材质的所有使用者，以及使用它的图例，都会一起更新。需要独立配色时，先用 **N 侧栏 → Display Layers → Duplicate** 创建展示副本，再选副本应用预设。

如果提示目标改变、材质只读或无法确认色带，先取消，重新选中可编辑的标准 QC 着色视图，再打开对话框。确认会替换当前的自定义色阶和插值；希望保留手工配色时可先复制显示层。

<a id="charges"></a>
## 原子电荷与偶极

> Mulliken 电荷是按一种电子分配方法得到的原子部分电荷，单位 e 为元电荷。Charge Maximum 设置色带高端对应的电荷值，不改变原子电荷数据。

9. 在 **Display Layers** 暂时隐藏密度表面，选 **P03-atoms**。点击 **对象属性 → 科学记录与振动模式 → 设置原子电荷着色**，选 **Mulliken** 并确认。在 **图例排版** 开启 **显示图例**；氧应显示为负电荷一侧的红色，氢为正电荷一侧的蓝色，图例单位为 **e**。在 **颜色映射** 将 **Charge Maximum** 改为 **0.5 e**，观察颜色范围变化。原子电荷也可按上面的 **应用色带预设…** 更换配色；图例继续使用当前布居方法与 **e**，颜色对应关系以该图例为准。

> 偶极矢量用大小和方向描述电荷分布；Debye 是偶极矩单位。Modifiers 是调节几何处理参数的修改器面板；Angstrom per Debye 设置每 Debye 对应的箭头显示长度，单位为 Å，不改变源偶极矩。

10. 保持 **P03-atoms** 活动，点击 **N 侧栏 → 创建视图与检查工具 → 创建偶极矢量**，选新对象 **QC dipole (Debye; physical direction)**。在 **Properties → Modifiers** 将 **Angstrom per Debye** 从 **0.5** 改为 **1.5**；箭头应沿 **+Z**，长度变为三倍。截图保存为 `human/screenshots/P03-charge-dipole.png`。继续空间观察前，在 **Display Layers** 隐藏偶极层、恢复密度表面。

![水二聚体的原子电荷颜色和偶极箭头](../screenshots/P03-charge-dipole.png)

<a id="densities"></a>
## 选择其他密度

**生成量子化学场 → Quantity** 还提供以下选项，网格操作与步骤 2 相同。

> Alpha、Beta 是两个自旋通道；自旋密度是 Alpha 密度减去 Beta 密度。闭壳层指电子成对占据空间轨道，本例水二聚体的两个通道相同。

| 选项 | 显示的量 |
| --- | --- |
| Alpha density | Alpha 自旋通道的电子密度 |
| Beta density | Beta 自旋通道的电子密度 |
| Spin density | Alpha 密度减去 Beta 密度 |

11. 若要看非零自旋密度，在同一工程导入 [shared/data/public/P01/o2-uhf.fchk](../../shared/data/public/P01/o2-uhf.fchk)，选新氧分子原子对象，生成 **Quantity=Spin density**，使用 **0.2 Å / 3 Å / 512 MiB**。选 **QC spin_density**，设 **正值阈值=0.002 electron/bohr^3**。在 **Display Layers** 暂时隐藏 P03 的分子和场，应看到氧分子周围的自旋密度。截图保存为 `human/screenshots/P01-spin-density.png`。看完后隐藏本步氧分子和自旋场，恢复 **P03-atoms** 与密度/ESP 表面，便可继续 P03 专题。

![氧分子的非零自旋密度](../screenshots/P01-spin-density.png)
