# 密度、ESP、电荷与偶极

[返回教程目录](../SOP.md#topics) · [密度与 ESP](#mapping) · [电荷与偶极](#charges) · [其他密度](#densities)

路径相对材料根目录。本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。后面的[空间观察](04-spatial-tools.md)和[外部 ESP 与 AIM](06-esp-aim.md)继续使用这里的 P03 对象。

> 电子密度表示空间中电子数的分布。ESP 是静电势，描述单位正试探电荷在该位置的势能。

<a id="mapping"></a>
## 密度表面按 ESP 着色

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，选择 [shared/data/public/P03/water-dimer.fchk](../../shared/data/public/P03/water-dimer.fchk)。选中新原子对象，命名为 **P03-atoms**。应有 **O/H/H/O/H/H** 六个原子；在 **对象属性 → 科学记录与振动模式** 查看电子总能量，应约为 **−152.013820 Eh**。本样本计算条件为 **RHF/6-31G(d)**。

> Eh（Hartree）是能量单位；方法和基组说明这份能量来自什么计算条件。

2. 选 **P03-atoms**，点击 **工作流 → 生成量子化学场**，设 **Quantity=Electron density**、**Grid spacing=0.2**、**Grid margin=3**、**Memory budget=512**，确认。应生成 **QC electron_number_density**，单位为 **electron/bohr^3**。

3. 再选 **P03-atoms**，用相同入口和网格参数生成 **Quantity=Electrostatic potential**。应生成 **QC electrostatic_potential**，单位为 **hartree/e**。

4. 选 **QC electron_number_density**，在 **对象属性 → 几何表示** 设 **正值阈值=0.004**。点击 **颜色映射 → 选择／替换着色场**，选 **QC electrostatic_potential**，设 **Color minimum=−0.05、Color maximum=0.05** 并确认。在 **Display Layers** 关闭独立 **QC electrostatic_potential** 表面的眼睛和相机图标，保留映射后的密度表面与 **P03-atoms**。在 **Material Preview** 中，密度表面应出现随位置变化的颜色。

> 这里用密度确定表面位置，用 ESP 确定颜色。隐藏独立 ESP 表面后，着色仍使用它的场数据。

5. 保持密度表面活动，在 **颜色映射** 设 **Color Minimum=−0.05、Color Center=0、Color Maximum=0.05**。在 **图例排版** 开启 **显示图例**，设 **长度=2.6、宽度=0.25、字号=0.2、小数位数=3、位置=(3.5,0,0)**。转到能读清图例的视角；图例应显示 **hartree/e** 与上述范围。在 **Properties → Material → QCBlender · 节点材质** 把 **Reverse (0 or 1)** 设为 **1**，表面和图例应一起反转颜色，再恢复 **0**。截图保存为 `human/screenshots/30-density-esp.png`。

![密度表面的 ESP 颜色与相同范围的图例](../screenshots/30-density-esp.png)

<a id="charges"></a>
## 原子电荷与偶极

6. 在 **Display Layers** 暂时隐藏密度表面，选 **P03-atoms**。点击 **对象属性 → 科学记录与振动模式 → 设置原子电荷着色**，选 **Mulliken** 并确认。在 **图例排版** 开启 **显示图例**；氧应显示为负电荷一侧的红色，氢为正电荷一侧的蓝色，图例单位为 **e**。在 **颜色映射** 将 **Charge Maximum** 改为 **0.5 e**，观察颜色范围变化。

> Mulliken 电荷是按一种电子分配方法得到的原子部分电荷，单位 e 为元电荷。

7. 保持 **P03-atoms** 活动，点击 **N 侧栏 → 创建视图与检查工具 → 创建偶极矢量**，选新对象 **QC dipole (Debye; physical direction)**。在 **Properties → Modifiers** 将 **Angstrom per Debye** 从 **0.5** 改为 **1.5**；箭头应沿 **+Z**，长度变为三倍。截图保存为 `human/screenshots/31-charge-dipole.png`。继续空间观察前，在 **Display Layers** 隐藏偶极层、恢复密度表面。

![水二聚体的原子电荷颜色和偶极箭头](../screenshots/31-charge-dipole.png)

> 偶极矢量描述正负电荷分布的偏离；Debye 是偶极矩单位。Angstrom per Debye 只设置箭头显示比例。

<a id="densities"></a>
## 选择其他密度

**生成量子化学场 → Quantity** 还提供以下选项，网格操作与步骤 2 相同。

| 选项 | 显示的量 |
| --- | --- |
| Alpha density | Alpha 自旋通道的电子密度 |
| Beta density | Beta 自旋通道的电子密度 |
| Spin density | Alpha 密度减去 Beta 密度 |

> 自旋密度描述两个自旋通道的密度差；本例闭壳层水二聚体的两个通道相同。

8. 若要看非零自旋密度，在同一工程导入 [shared/data/public/P01/o2-uhf.fchk](../../shared/data/public/P01/o2-uhf.fchk)，选新氧分子原子对象，生成 **Quantity=Spin density**，使用 **0.2 Å / 3 Å / 512 MiB**。选 **QC spin_density**，设 **正值阈值=0.002 electron/bohr^3**。在 **Display Layers** 暂时隐藏 P03 的分子和场，应看到氧分子周围的自旋密度。截图保存为 `human/screenshots/32-spin-density.png`。看完后隐藏本步氧分子和自旋场，恢复 **P03-atoms** 与密度/ESP 表面，便可继续 P03 专题。

![氧分子的非零自旋密度](../screenshots/32-spin-density.png)
