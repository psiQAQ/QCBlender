# ETS-NOCV 表与变形密度

[返回教程目录](../SOP.md#topics)

路径相对材料根目录。先按[准备新工程](../SOP.md#new-scene)准备场景并打开 QCBlender 侧栏。

本页截图使用案例 `P05-` 前缀。

> NOCV（自然化学价轨道）将片段组合时的电子密度变化分成配对贡献；ETS-NOCV 将这些贡献与相互作用能量分析结合，表中列出各对的数值与能量。本例能量由 Multiwfn 的近似方法计算，详细条件见[样本说明](../../shared/data/public/NOTICE.md)。

> Pair energy unit 声明表中每对贡献的能量单位；kcal/mol 表示千卡每摩尔。这里导入源表数值，单位选项不执行换算。

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，导入 [shared/data/public/P05/complex.fchk](../../shared/data/public/P05/complex.fchk)。只选新原子对象，点击 **导入外部结果 → ETS-NOCV 表**，选 **ETS-NOCV output text=[shared/data/public/P05/nocv/ets-nocv.txt](../../shared/data/public/P05/nocv/ets-nocv.txt)**、**Pair energy unit=kcal/mol** 并确认。应保留 **C/O/B/H/H/H** 六原子分子，并新增 **QC ETS-NOCV pairs**。

> **QC ETS-NOCV pairs** 是分析表的记录对象，用于查看各 Pair 的能量和本征值，并筛选对应的成对贡献。

> External Analysis Records 查看源记录，Record 选择源记录表中的行位置；External Result Browser 则用于按条件筛选这些记录。

> Pair 是源分析中一对贡献的编号；Spin 区分自旋记录，Total 表示总通道，Alpha、Beta 表示分别列出的两种自旋通道。Pair energy 是该对贡献的能量，正负本征值描述该对电子密度重排的大小；它们用于比较各对贡献。

2. 在 **Display Layers** 点击 **QC ETS-NOCV pairs** 行最左侧的选择图标，点击 **工作流 → 对象属性与显示参数**，展开 **External Analysis Records**。应有 **11 条实际打印的记录**；**Record (1-based)=1** 应为 **Pair1 / Total**、**pair_energy=−57.02 kcal/mol**，正负本征值为 **+0.54550/−0.54550**。截图保存为 `human/screenshots/P05-nocv-table.png`。

![ETS-NOCV 的 Pair1 数值、单位和源记录](../screenshots/P05-nocv-table.png)

> Pair energy 范围筛选选出能量落在 From 到 To 之间的记录，包含两端；Spin 进一步限定自旋通道。Matching records 是满足条件的源记录数。

3. 在表对象的 **External Result Browser** 中选 **Spin=Total**，在 **Pair energy [kcal/mol]** 一行开启两端范围，填 **From=−60、To=−50**，设 **Match (1-based)=1**，点击 **应用筛选**。应显示 **Matching records: 1**，匹配 **Pair1**。此时尚未导入该 Pair 的场，视口中还没有对应变形密度表面。

> Signed pair Cube 保存一对贡献的带正负号变形密度场；Pair number 与 Spin 声明它对应的源表记录。Deformation density unit 声明该场的密度单位，供图例与导出使用。

4. 保持表对象活动，点击 **N 侧栏 → 导入外部结果 → NOCV pair Cube**，选择 **Signed pair Cube=[shared/data/public/P05/nocv/nocv-pair1.cub](../../shared/data/public/P05/nocv/nocv-pair1.cub)**，设 **Spin=Total**，从 **Pair number** 的实际源编号列表选择 **1**，并设 **Deformation density unit=electron/bohr^3**。完成后在 **Display Layers** 选 **QC nocv_deformation_density**，重新点击 **工作流 → 对象属性与显示参数**，其网格应为 **47×50×57**。在 **几何表示** 设 **正值阈值=0.003**，保持 **Link Thresholds、显示正值、显示负值** 开启。应看到两种颜色的变形密度。截图保存为 `human/screenshots/P05-nocv-density.png`。

![与 Pair1 表记录对应的正负变形密度](../screenshots/P05-nocv-density.png)

> 变形密度的正值表示电子密度增加，负值表示电子密度减少；本例表面的单位是 electron/bohr^3，用于观察对应 Pair 的电子密度重排发生在哪些区域。

5. 在 **Display Layers** 选回 **QC ETS-NOCV pairs**，重新点击 **工作流 → 对象属性与显示参数**，保留步骤 3 的筛选条件与 **Match=1**，再点击 **应用筛选**。活动对象应切换到刚才导入的唯一 **Pair1 / Total** 场 **QC nocv_deformation_density**。再次点击 **工作流 → 对象属性与显示参数**，将原先固定在表对象上的属性区切到场对象；然后在 **几何表示** 关闭再开启 **显示负值**，对应部分应消失后恢复，另一符号仍可见。
