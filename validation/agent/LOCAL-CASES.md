# 本机 P02：优化、振动与 NBO

[振动](#vibration) · [优化](#optimization) · [NBO](#nbo)

本页供拥有 P02 原件的维护者操作。P02 原始日志的再分发许可尚未确认；**本页、输入和本页截图均不加入公开教程包**。公开教程本身可以独立完成。

路径相对 `validation/` 材料根目录。输入为 [shared/data/local/log-examples/water_neutral_nbo_opt_freq.out](../shared/data/local/log-examples/water_neutral_nbo_opt_freq.out)。先完成[安装](../human/SOP.md#install)，在材料根目录创建 `agent/screenshots/`，供本页截图使用。

> Gaussian 日志可以包含多个计算段；本例 Job1 是几何优化，Job2 是频率计算。

<a id="vibration"></a>
## 振动

1. 使用 **File → New → General** 新建工程，在 Outliner 删除默认 Cube。点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，选择上述 `.out`。在 **Choose Gaussian Calculation → Calculation** 选择第 **2** 段并确认。将新原子对象命名为 **P02-frequency**；应看到 **O/H/H** 三原子水分子，**科学记录与振动模式** 中目标电子能量约 **−74.9659011806 Eh**。

2. 在 **对象属性 → 科学记录与振动模式** 选择源模式 **3**，应看到 **4392.5759 cm^-1**、IR 强度 **29.9428 km/mol**。在 **高级参数** 开启 **Animate**，设 **Amplitude (angstrom)=0.35、Cycles per second=1**，播放底部 **Timeline**。帧号应持续推进，分子应振动；观察后暂停。截图保存为 `agent/screenshots/local-01-vibration.png`。

![水分子的振动、模式频率和动画参数](screenshots/local-01-vibration.png)

> 振动模式给出原子在平衡构型附近的位移方向和频率；振幅、相位与播放速度是显示设置。

3. 关闭 **Animate**，在 **几何表示** 开启 **Show Displacement Vectors**，拖动 **Phase** 查看位移。切到源模式 **1**，应看到频率 **2169.7613 cm^-1**、IR 强度 **7.2483 km/mol**，位移方向随所选模式改变。

> IR 强度表示这一振动模式的红外吸收强度。

<a id="optimization"></a>
## 优化轨迹

4. 再次点击 **导入 Gaussian / Cube / XYZ**，选择同一完整路径 `shared/data/local/log-examples/water_neutral_nbo_opt_freq.out`，这次选择第 **1** 段。选中新原子对象，点击 **创建视图与检查工具 → 创建优化轨迹视图**。选新轨迹，在 **对象属性 → Optimization Trajectory** 应看到共有 **4 步**。在 **Display Layers** 暂时隐藏频率分子和刚导入的静态分子，只保留轨迹可见。

5. 使用 **Next** 从第 1 步走到第 4 步。步号、构型和能量应同步改变：第 1 步约 **−74.9643287914 Eh**，第 4 步约 **−74.9659011806 Eh**。截图保存为 `agent/screenshots/local-02-optimization.png`。

![水分子的优化步号、当前构型和能量](screenshots/local-02-optimization.png)

> 优化步是计算寻找较低能量构型的过程，步号本身不表示物理时间。

<a id="nbo"></a>
## NBO 与 E(2)

6. 在 **Display Layers** 选回 **P02-frequency**，点击 **N 侧栏 → 导入外部结果 → NBO 记录**。将 **Gaussian Log / Out** 设为 `shared/data/local/log-examples/water_neutral_nbo_opt_freq.out` 的实际文件，先确认以检查日志；检查完成后出现编号对话框，再选 **Gaussian job (1-based)=2、NBO block within job (1-based)=1** 并确认。编号按日志中的实际 Job 和该 Job 的 block 数限制；改选 Job 后，block 的范围同步更新。应生成并选中 **QC NBO: water_neutral_nbo_opt_freq.out**。

> NBO 是自然键轨道，用于按键、孤对等方式分析电子分布。E(2) 是供体与受体轨道之间的二阶微扰相互作用能。

7. 打开 **对象属性 → NBO Records**，应有 **7 orbitals、2 E(2) records**。设 **NBO row (1-based)=1**，应看到 **O1–H2、BD、Occupancy 1.99933、Energy −0.77653 hartree**；设 **E(2) row (1-based)=1**，应看到 **1 → 7、0.59 kcal/mol**。截图保存为 `agent/screenshots/local-03-nbo.png`。

![NBO 第一条轨道和 E(2) 第一条相互作用](screenshots/local-03-nbo.png)

> BD 表示成键轨道；Occupancy 是该轨道的电子占据数。

8. 在 **External Result Browser** 选 **Orbital type=BD、Orbital order=Occupancy, high to low、E(2) order=E(2), high to low**，点击 **应用筛选**。应显示 **Orbitals 2 | E(2) 2**。看完后把 **Orbital type** 恢复 **All**，再次应用。

需要数据表时，选 **P02-frequency** 可导出 **Data=IR**，得到 `ir.csv`；选优化轨迹可导出 **Data=optimization**，得到 `optimization_steps.csv` 与 `optimization_convergence.csv`。共同方法见[科学 CSV 导出](../human/topics/04-spatial-tools.md#profile)。保留本机工程时使用[保存自包含工程](../human/SOP.md#save)，目标目录可用 `work/human/local-P02/`。
