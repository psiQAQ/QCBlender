# IRC 路径与 Mayer 键级

[返回教程目录](../SOP.md#topics)

路径相对材料根目录。本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。

本页截图使用案例 `P04-` 前缀。

> IRC 是从过渡态沿反应路径得到的一组构型。本例使用 H₂O₂ 路径上靠近过渡态的三个点；原子顺序为 O/O/H/H。

1. 点击 **N 侧栏 → 工作流 → 导入 IRC 路径**，在 **CSV manifest: step,fchk** 选择 [shared/data/public/P04/steps.csv](../../shared/data/public/P04/steps.csv)。该 CSV 与以下三份文件保持在同一目录。完成后选 **IRC path**，在 **对象属性 → IRC Path** 应看到 **Step 1/3**、能量约 **−148.764884 hartree**。

| 步号 | 波函数文件 |
| --- | --- |
| 1 | [shared/data/public/P04/step-001.fchk](../../shared/data/public/P04/step-001.fchk) |
| 2 | [shared/data/public/P04/step-002.fchk](../../shared/data/public/P04/step-002.fchk) |
| 3 | [shared/data/public/P04/step-003.fchk](../../shared/data/public/P04/step-003.fchk) |

2. 保持 **IRC path** 活动，在 **N 侧栏 → 创建视图与检查工具** 创建 **距离标注**，源编号填 **1,2**；再创建 **二面角标注**，填 **3,1,2,4**。两个标注的 **Decimal places** 均设为 **6**。转到能看清标签的视角，必要时在 **局部选择与标注 → Source Atom Annotations** 的设置中调整 **Offset**。

3. 在 **IRC Path** 点击 **Next → Next → Previous**，按 **1→2→3→2** 切换。距离始终约 **1.401928 Å**，二面角应依次约为 **171.760508°、−180.000000°、−171.760508°**；第 2 步能量约 **−148.764883 hartree**。步号与标签应一起更新。截图保存为 `human/screenshots/P04-irc.png`。

![三步 IRC 中的当前构型、能量和随步二面角](../screenshots/P04-irc.png)

4. 保持 **IRC path** 活动，点击 **对象属性 → IRC Path → Import Mayer Results**，在 **CSV manifest: step,mayer_output** 选择 [shared/data/public/P04/mayer-pyscf.csv](../../shared/data/public/P04/mayer-pyscf.csv)。保留其同目录的下列文件；完成后应新增 **QC IRC Mayer orders**。

| 步号 | 分析文件 |
| --- | --- |
| 1 | [shared/data/public/P04/step-001-mayer-pyscf.txt](../../shared/data/public/P04/step-001-mayer-pyscf.txt) |
| 2 | [shared/data/public/P04/step-002-mayer-pyscf.txt](../../shared/data/public/P04/step-002-mayer-pyscf.txt) |
| 3 | [shared/data/public/P04/step-003-mayer-pyscf.txt](../../shared/data/public/P04/step-003-mayer-pyscf.txt) |

> Mayer 键级是由电子结构计算得到的无量纲数值；本例文本由 PySCF 计算并按 Multiwfn 兼容格式保存。

5. 选 **QC IRC Mayer orders**，在 **对象属性 → IRC Path** 填 **Atom A (1-based)=1、Atom B (1-based)=2**，点击 **Read Pair**。第 2 步应显示约 **0.987349**。点击 **Next** 到第 3 步，值应变为约 **0.987331**，构型和标注同步切换；再点击 **Previous** 回第 2 步。截图保存为 `human/screenshots/P04-mayer.png`。

![IRC 当前步与原子对 1、2 的 Mayer 键级](../screenshots/P04-mayer.png)

需要表格时，选择路径根对象后可导出 **Data=IRC**，得到 `irc_steps.csv`；选择 Mayer 表后可导出 **Data=Mayer**，得到 `mayer.csv`。共同导出方法见[剖面 CSV](04-spatial-tools.md#profile)。
