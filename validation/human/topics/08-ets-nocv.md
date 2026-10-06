# ETS-NOCV 表与变形密度

[返回教程目录](../SOP.md#topics)

路径相对材料根目录。本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。

> NOCV 将电子密度变化分成配对贡献；ETS-NOCV 表列出各对的数值与能量。本例能量由 Multiwfn 的近似方法计算，详细条件见[样本说明](../../shared/data/public/NOTICE.md)。

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，导入 [shared/data/public/P05/complex.fchk](../../shared/data/public/P05/complex.fchk)。只选新原子对象，点击 **导入外部结果 → ETS-NOCV 表**，选 **ETS-NOCV output text=[shared/data/public/P05/nocv/ets-nocv.txt](../../shared/data/public/P05/nocv/ets-nocv.txt)**、**Pair energy unit=kcal/mol** 并确认。应保留 **C/O/B/H/H/H** 六原子分子，并新增 **QC ETS-NOCV pairs**。

2. 在 **Display Layers** 选 **QC ETS-NOCV pairs**，打开 **对象属性 → External Analysis Records**。应有 **11 条实际打印的记录**；**Record (1-based)=1** 应为 **Pair1 / Total**、**pair_energy=−57.02 kcal/mol**，正负本征值为 **+0.54550/−0.54550**。截图保存为 `human/screenshots/80-nocv-table.png`。

![ETS-NOCV 的 Pair1 数值、单位和源记录](../screenshots/80-nocv-table.png)

> Pair 是一对贡献的编号；Total 表示本例的总自旋通道。Pair energy 是这一对的能量字段。

3. 在表对象的 **External Result Browser** 中选 **Spin=Total**，在 **Pair energy [kcal/mol]** 一行开启两端范围，填 **From=−60、To=−50**，点击 **应用筛选**。应显示 **Matching records: 1**，匹配 **Pair1**。这是表的筛选结果。

4. 保持表对象活动，点击 **N 侧栏 → 导入外部结果 → NOCV pair Cube**，选择 **Signed pair Cube=[shared/data/public/P05/nocv/nocv-pair1.cub](../../shared/data/public/P05/nocv/nocv-pair1.cub)**，设 **Pair number=1、Spin=Total、Deformation density unit=electron/bohr^3**。完成后选 **QC nocv_deformation_density**，其网格应为 **47×50×57**。在 **几何表示** 设 **正值阈值=0.003**，保持 **Link Thresholds、显示正值、显示负值** 开启。切到 **Material Preview**，应看到两种颜色的变形密度。截图保存为 `human/screenshots/81-nocv-density.png`。

![与 Pair1 表记录对应的正负变形密度](../screenshots/81-nocv-density.png)

> 变形密度的正值表示电子密度增加，负值表示电子密度减少；本例表面的单位是 electron/bohr^3。

5. 在 **Display Layers** 选回 **QC ETS-NOCV pairs**，保留步骤 3 的范围，再点击 **应用筛选**。应定位刚才导入的唯一 **Pair1 / Total** 场。然后在 **几何表示** 关闭再开启 **显示负值**，对应部分应消失后恢复，另一符号仍可见。
