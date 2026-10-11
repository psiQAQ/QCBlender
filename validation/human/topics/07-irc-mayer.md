# IRC 路径与 Mayer 键级

[返回教程目录](../SOP.md#topics)

路径相对材料根目录。先按[准备新工程](../SOP.md#new-scene)准备场景并打开 QCBlender 侧栏。

本页截图使用案例 `P04-` 前缀。

> 过渡态是反应路径上能量势垒处的构型。IRC（内禀反应坐标）用于跟随过渡态两侧的反应路径；这里导入沿路径计算的一组构型。本例使用 H₂O₂ 路径上靠近过渡态的三个点；原子顺序为 O/O/H/H。

> CSV manifest 是文件清单；step、fchk 两列把步号与对应的波函数文件配对。IRC path 是管理整条路径的根对象，Step 1/3 表示当前为三份构型中的第一份；步号表示构型顺序。

1. 点击 **N 侧栏 → 工作流 → 导入 IRC 路径**，在 **CSV manifest: step,fchk** 选择 [shared/data/public/P04/steps.csv](../../shared/data/public/P04/steps.csv)。该 CSV 与以下三份文件保持在同一目录。完成后在 **Display Layers** 点击 **IRC path** 行最左侧的选择图标，点击 **工作流 → 对象属性与显示参数**，在 **IRC Path** 应看到 **Step 1/3**、能量约 **−148.764884 hartree**。

| 步号 | 波函数文件 |
| --- | --- |
| 1 | [shared/data/public/P04/step-001.fchk](../../shared/data/public/P04/step-001.fchk) |
| 2 | [shared/data/public/P04/step-002.fchk](../../shared/data/public/P04/step-002.fchk) |
| 3 | [shared/data/public/P04/step-003.fchk](../../shared/data/public/P04/step-003.fchk) |

> Decimal places 控制标签保留的小数位数；Offset 移动标签相对测量位置的显示位置，便于避开分子。它们不改变构型或测量值。

2. 保持 **IRC path** 活动，在 **N 侧栏 → 创建视图与检查工具** 创建 **距离标注**，源编号填 **1,2**；再创建 **二面角标注**，填 **3,1,2,4**。两个标注的 **Decimal places** 均设为 **6**。创建后仍选 **IRC path**，转到能看清标签的视角，必要时在 **局部选择与标注 → Source Atom Annotations** 的设置中调整 **Offset**。

> Next 与 Previous 切换根对象的当前构型；能量、原子位置和绑定的测量标注随当前步更新。

3. 在 **IRC Path** 点击 **Next → Next → Previous**，按 **1→2→3→2** 切换。距离始终约 **1.401928 Å**，二面角应依次约为 **171.760508°、−180.000000°、−171.760508°**；第 2 步能量约 **−148.764883 hartree**。步号与标签应一起更新。截图保存为 `human/screenshots/P04-irc.png`。

![三步 IRC 中的当前构型、能量和随步二面角](../screenshots/P04-irc.png)

> Mayer 键级是由电子结构计算得到的无量纲数值，用于比较指定原子对沿路径的成键变化；本例文本由 PySCF 计算并按 Multiwfn 兼容格式保存。step、mayer_output 清单把各步与相应的键级分析文件配对。

4. 保持 **IRC path** 活动，点击 **对象属性 → IRC Path → Import Mayer Results**，在 **CSV manifest: step,mayer_output** 选择 [shared/data/public/P04/mayer-pyscf.csv](../../shared/data/public/P04/mayer-pyscf.csv)。保留其同目录的下列文件；完成后应新增 **QC IRC Mayer orders**。

| 步号 | 分析文件 |
| --- | --- |
| 1 | [shared/data/public/P04/step-001-mayer-pyscf.txt](../../shared/data/public/P04/step-001-mayer-pyscf.txt) |
| 2 | [shared/data/public/P04/step-002-mayer-pyscf.txt](../../shared/data/public/P04/step-002-mayer-pyscf.txt) |
| 3 | [shared/data/public/P04/step-003-mayer-pyscf.txt](../../shared/data/public/P04/step-003-mayer-pyscf.txt) |

> Atom A、Atom B 指定要查看的两个源原子编号；Read Pair 读取这一原子对的随步键级，面板显示当前步的值。

5. 在 **Display Layers** 选 **QC IRC Mayer orders**，点击 **工作流 → 对象属性与显示参数**，在 **IRC Path** 填 **Atom A (1-based)=1、Atom B (1-based)=2**，点击 **Read Pair**。第 2 步应显示约 **0.987349**。点击 **Next** 到第 3 步，值应变为约 **0.987331**，构型和标注同步切换；再点击 **Previous** 回第 2 步。截图保存为 `human/screenshots/P04-mayer.png`。

![IRC 当前步与原子对 1、2 的 Mayer 键级](../screenshots/P04-mayer.png)

需要表格时，在 **Display Layers** 选 **IRC path**，按[数据导出](../SOP.md#export)选择 **Data=IRC** 并设置输出目录，得到 `irc_steps.csv`；再选 **QC IRC Mayer orders**，用同一入口选择 **Data=Mayer**，得到 `mayer.csv`。两次导出各有一个新子目录，各自的 `metadata.json` 与 CSV 一起保留。

> `irc_steps.csv` 保存各步的能量与来源文件信息，供整理路径能量变化；`mayer.csv` 保存所有源步、原子对及其键级，供比较成键变化。绘图时可用步号作横轴，能量（hartree）或无量纲键级作纵轴；步号不是时间。两份表可在表格或绘图软件中按步号对应查看。
