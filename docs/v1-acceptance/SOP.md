# QCBlender 0.0.1 独立人工验收 SOP

适用 **Windows x64 + Blender 5.1.1**。候选 ZIP：`outputs/dist/qcblender-0.0.1.zip`，50,440,285 字节，SHA-256 `adf7760c647be303cd69f43b4b928d42411031d1bdfe3f25466bb15aded245fc`。这是当前技术候选的固定快照；ZIP 摘要变化时停止并重建本清单。全部案例当前状态为 **Not Run**，只有实际操作和复核的使用者填写结果、日期和签名。Agent 已有的技术报告不构成人工签署。

[样本清单](SOURCES.md)列出 S01–S08 的 URL、版本、许可、摘要和计算条件。先在仓库根目录 PowerShell 检查 ZIP 和本次所用的每个样本：`Get-FileHash <路径> -Algorithm SHA256`。摘要不符则停在该例。`outputs/v1-acceptance/` 是本地忽略目录；每例在 `outputs/v1-acceptance/cases/CNN/` 留存同名 `CNN.png`、`CNN.blend`、`CNN.qcdata/`。记录型案例的 `CNN.png` 须拍到可读的 QCBlender 面板和关联分子，不假造三维数值场。可另加 PNG，但不能替代这些固定文件。

## 0. 安装与通用操作

1. 在 Blender 5.1.1 的 **Preferences → Get Extensions → Install from Disk** 选择上述 ZIP，启用 QCBlender；在 3D Viewport 按 `N`，打开 **QCBlender** 页，点击 **Check Scientific Runtime**。记录操作系统、Blender 精确版本、ZIP 摘要及检查结果。
2. 每例开始前打开新场景。进入 **QCBlender → Import** 选择案例文件。`.log/.out` 还要选择从 1 开始的 **Gaussian Log job number**。等待完成，选择新原子或场视图。原子编号从 1 开始，坐标是 Å，1 Blender 单位 = 1 Å。
3. 在 QCBlender 面板和源文件核对原子数、顺序、元素、坐标、计算方法/基组、源摘要、量名、单位及具体数值。FCHK/Log 的源总能量用 Hartree；电荷用 `e`；偶极用 Debye；频率用 `cm^-1`，IR 强度用 `km/mol`。数值按源文件输出精度比较，不凭颜色或轮廓判断数值正确。
4. 选中视图，在 **Geometry Nodes 修改器** 或侧栏编辑下面指定节点输入；截图或记下修改前后数值与视觉变化。用 Blender 原生相机/灯光和 **Render → Render Image**，`Image → Save As` 保存指定 PNG。图注或旁注写源文件 SHA、量名/单位、阈值、网格、颜色范围和色彩管理。
5. 点击 **Save Portable QC Project** 指定 `CNN.blend`。检查同名 `CNN.qcdata/`。关闭 Blender，重新启动后打开该 `.blend`，确认视图、数值、图例/参数和 PNG 对应；再将 `.blend` 与 `.qcdata/` 一起复制到另一目录，用新 Blender 进程冷重开并再次渲染。原始外部结果文件需另存，`.qcdata` 只保存其来源摘要和导入记录。
6. 每例依次记 **导入、源数值、节点变化、渲染、保存重开、移动冷重开** 六栏的 `Passed / Failed / Not Run`、实测值/截图路径、缺陷编号、本人签名和日期。任一栏失败则全例 `Failed`；修复后须用新的候选 ZIP 重做受影响例。未找到真实样本的例子保留步骤，状态 `Not Run`，不得签署。

`.chk` 不是输入格式；在持有 Gaussian 的机器上先执行 `formchk calculation.chk calculation.fchk`，再将 `.fchk` 纳入来源和摘要核对。不要把 `.chk` 导入失败算作受支持功能失败。

## 1. 输入与物理量案例

下表每行的路径相对仓库根。`A` 表示来源清单中已在本地且摘要匹配；`M` 表示缺真实成套样本，执行前必须先补齐 [样本清单](SOURCES.md) 的来源字段。每个案例按第 0 节六步操作，并执行本表的附加点击步骤。所有 `CXX.png/.blend/.qcdata` 均放在 `outputs/v1-acceptance/cases/CXX/`。别名只复用科学/成图案例，仍须逐一通过导入和保存检查。

| 例 / 输入 / 状态 | 点击步骤和须核对的物理量、单位 | 节点参数、预期变化与固定证据路径 |
| --- | --- | --- |
| **C01 FCHK + `.fch` 别名**；S01、S05 和 `outputs/v1-acceptance/aliases/water_dimer.fch`；A | 分别 **Import** S01、S05 和别名；S05/别名均应为 6 原子且身份、坐标、源能量一致；S01 应为 20 原子、+1/双重态、69 电子，UB3LYP/STO-3G，总能量约 `-382.0813927197 Eh`。在 S01 原子视图分别 **Generate Field** Alpha MO 35、Beta HOMO 34、总/Alpha/Beta/自旋密度；核对 MO 的源编号、占据、能量和 `bohr^-3/2`，密度为 `electron/bohr^3`，同网格上总=Alpha+Beta、自旋=Alpha−Beta。 | MO35 用 `Isovalue=0.045`、正负相均开；自旋密度从 `±0.002 electron/bohr^3` 开始。正负相显隐、独立阈值、透明度和三种表面样式都应改变显示而不改源数组。分别保存 `C01-mo.png`、`C01-total.png`、`C01-alpha.png`、`C01-beta.png`、`C01-spin.png`；总览 `C01.png`，工程 `C01.blend` + `C01.qcdata/`。 |
| **C02 `.log` 与 `.out`**；S04、S02；A | **Import** S04（`.log`）与 S02（`.out`）；S04 与 S03 同为 27 原子、原子顺序一致，最大坐标差约 `4.99e-7 Å`；查能量记录方法、来源行及 `Eh`。S02 是中性 DVB、B3LYP/STO-3G、54 个振动模式；选模式 45，核对 `3396.4292 cm^-1`、IR 强度源值 `km/mol` 及 IR 棒图高亮。 | 开 **Animate**、`Amplitude=0.35 Å`、`Cycles per second=1`，切模式、调 Phase，振动方向/IR 高亮应变化；播放速度不是物理频率。保存 `C02-vibration.png`、`C02-ir.png`、总览 `C02.png/.blend/.qcdata/`。 |
| **C03 `.cube` + `.cub` 别名**；S05–S07 与 `outputs/v1-acceptance/aliases/water_dimer_density.cub`；A | 分别 **Import** S06 `.cube` 和别名 `.cub`，核对 6 原子、同一网格及原值，初始应为 `unknown_scalar/unknown`；S06 是 NCIPLOT 的 **100×sign(λ₂)ρ**，不得点选普通电子密度并误称未缩放。再导入 S07，核对 RDG 过滤哨兵和原始量定义。`Identify Cube` 仅在填入实际物理量和**数值已有的单位/倍率**时使用；标注不执行数值换算。 | 调正负等值与颜色映射，显示 S06 双符号区域；S07 可作表面几何场但不能宣称 IGMH/IRI。`.cube` 和 `.cub` 值、网格、场形应一致。保存 `C03.png/.blend/.qcdata/`，并记录源值、倍率和标注文本。 |
| **C04 ESP / 电荷 / 偶极**；S03 + S04；A | **Import** S03；在原子对象 **Generate Field → Electrostatic potential** 和 **Electron density**。核对 27 原子、RHF/STO-3G、总能量约 `-673.5905711573 Eh`；ESP 是 `hartree/e`，密度 `electron/bohr^3`；**Charge** 只选源中确有的方法，核对至少两原子电荷和 `e`；**Dipole** 核对三分量及 Debye，检查 S04 对应偶极（换算后）。核附近无效 ESP 不当零值。 | 密度表面 `Isovalue=0.004 electron/bohr^3`；选 ESP 表面再 Shift 选密度为活动对象，点 **Map Colors**，色域 `-0.05/0/+0.05 hartree/e`，开图例；偶极显示比例可用 `1.5 Å/D`。另 **Slice** ESP，保存 `C04-esp.png`、`C04-charge.png`、`C04-dipole.png`、`C04-slice.png` 与总览 `C04.png/.blend/.qcdata/`。 |
| **C05 显示快捷控制**；S01；A | 选 S01 原子视图，在 **Display Layers** 依次点 **Hide H → Keep H...**（填一个真实氢的源编号）→ **Show all**；核对被保留原子确为氢且其他氢隐藏。 | 原子数和 `.qcdata` 原始原子数组始终不变；撤销/重做各一次，保存前后画面 `C05.png/.blend/.qcdata/`。 |
| **C06 NBO `.out`**；S08；A，许可待核 | **Import** S08、job 2，选其原子视图，再 **Import NBO Records** 同一文件、job 2、block 1。核对 7 条 NBO、2 条 E(2)，占据、NBO 能量、原子编号、E(2) 的 `kcal/mol` 及原文行；NBO 不与 canonical MO 自动映射。job 1 的优化段有多构型，不作为最终几何关联。 | 在 **NBO Records** 面板逐条选择，证据 PNG 中至少一条 NBO 和一条 E(2) 可读；保存 `C06.png/.blend/.qcdata/`。再次用 `.log` 逐字节别名导入 NBO 只验证扩展名入口，记录其摘要仍为 S08；按本表后的命令创建别名。 |
| **C07 IGMH 与 IRI 双 Cube**；同构型几何场 + `sign(λ₂)ρ` 场各一套；M | 选参考原子视图，点 **Import IGMH / IRI**；对 IGMH、IRI 各自指定两 Cube、方法、两个场的已有单位、色域。核对原子顺序、坐标、网格、片段定义、δg/IRI 原值及 `sign(λ₂)ρ` 值；故意交换不匹配网格，应拒绝。 | 改几何等值、色域及散点节点；表面位置由几何场决定，颜色由第二场决定，散点横纵轴有量名/单位。分别保存 `C07-igmh.png`、`C07-iri.png`、`C07-scatter.png`、总览 `C07.png/.blend/.qcdata/`；目前 **Not Run**。 |
| **C08 ESP 表面极值/面积**；同构型极值 PDB + 面积分布文本；M | 先创建 C04 ESP 场，保持其场视图为活动对象，点 **ESP Surface**，填表面定义、极值单位、分布中心单位、面积单位。核对每个最大/最小值、坐标、面积各 bin、总面积及 PDB B-factor 约定；与场单位不同要明确换算依据。 | 点/面积分布应与所选 ESP 场关联；选点在 **External Analysis Records** 查询数值。保存 `C08-extrema.png`、`C08-area.png`、总览 `C08.png/.blend/.qcdata/`；目前 **Not Run**。 |
| **C09 AIM 点/路径/属性**；`CPs.pdb` + `paths.pdb` + 可选 `CPprop.txt`；M | 选同构型原子视图，点 **AIM**，逐项指定文件。核对 C/N/O/F 临界点类型、坐标、路径组、可用属性原值/单位和原子关联；不含属性时只验点/路径，不补造值。 | 显隐各类点和路径，选点在 **External Analysis Records** 查询；保存 `C09-points.png`、`C09-paths.png`、总览 `C09.png/.blend/.qcdata/`；目前 **Not Run**。 |
| **C10 IRC 步序 CSV/FCHK**；同一路径多步 FCHK + `step,fchk` CSV；M | CSV 必须 UTF-8、首行 `step,fchk`、从 1 连续且按预期反应方向排序。点 **IRC FCHK Path** 选择清单，逐步点 **IRC Path → Previous/Next**；核对每步原子身份/坐标、`Eh` 能量与源 FCHK、曲线游标及端点。故意重复编号/换原子应拒绝。 | 切步后原子构型和能量游标同步移动；保存 `C10-curve.png`、`C10-steps.png`、总览 `C10.png/.blend/.qcdata/`；目前 **Not Run**。 |
| **C11 逐步 Mayer**；C10 路径 + `step,mayer_output` CSV 与逐步真实文本；M | 选 IRC 根原子对象，点 **IRC Path → Import Mayer Results**，填 CSV。核对步数、原子对源编号、每步 Mayer 值（无量纲）与原文；在记录对象改原子对并点 **Plot Selected Mayer Pair**。缺步/原子对集合冲突应拒绝。 | 选步游标与键级曲线同步；保存 `C11-curve.png`、`C11-records.png`、总览 `C11.png/.blend/.qcdata/`；目前 **Not Run**。 |
| **C12 ETS-NOCV 表**；真实原始输出文本 + 参考构型；M | 选参考原子视图，点 **ETS-NOCV Table**，指定文本和文件**实际使用**的 `kcal/mol` 或 `hartree`；核对 pair 编号、自旋、成对轨道编号、能量、原文行号及来源 SHA。 | **External Analysis Records** 表可逐行查询；仅展示记录与关联分子。保存 `C12.png/.blend/.qcdata/`；目前 **Not Run**。 |
| **C13 NOCV pair Cube**；C12 表 + 对应 pair 的带符号 Cube；M | 选 C12 表对象，点 **NOCV Pair Cube**，填 pair 号、自旋、Cube 和已有单位；与 C12 行及参考构型逐项核对，选不存在的 pair/错误自旋应拒绝。 | 正负形变密度相分别显隐、独立阈值，源数值保留；保存 `C13-positive.png`、`C13-negative.png`、总览 `C13.png/.blend/.qcdata/`；目前 **Not Run**。 |

为 C06 检查 `.log` 别名时，在仓库根目录 PowerShell 执行：

```powershell
Copy-Item outputs/log-examples/water_neutral_nbo_opt_freq.out outputs/v1-acceptance/aliases/water_neutral_nbo_opt_freq.log
Get-FileHash outputs/v1-acceptance/aliases/water_neutral_nbo_opt_freq.log -Algorithm SHA256
```

摘要仍须为 S08。C01、C02、C03、C06 合起来覆盖 `.fchk/.fch`、`.log/.out`、`.cube/.cub` 的每一个入口；外部 CSV/PDB/text 的角色由专用对话框指定，不能仅靠文件扩展名代替角色检查。

## 2. 可用 Geometry Nodes 与交互覆盖表

在相应案例的 **Geometry Nodes 修改器输入**和节点编辑器中逐个记录“原值 → 新值 → 可见变化”；改完恢复用于成图的参数。节点组能否独立接入现有视图也要检查，不以资产名称存在作为通过。每行均有 `结果 / 截图 / 缺陷` 留白，可在下方结果表写 `N01…N18`。不存在的概念节点不纳入通过计数。

| 检查 | 对应案例和操作 | 预期变化 / 物理边界 |
| --- | --- | --- |
| N01 `QC Select Atoms` | C01：`Selection`、元素号、源编号首末值；选单个 H、再选全部 | 只改变选中原子的显示；编号以源顺序从 1 起，源数组不变 |
| N02 `QC Style Atoms and Bonds` | C01：样式 0 球棍、1 空间填充、2 只显示键；调原子/键半径 | 三样式轮廓确实不同；键为距离推断而非 Mayer 键级 |
| N03 氢显隐 | C05：Hide H、Keep H、Show all | 三步和撤销/重做正确，复制显示层互不影响 |
| N04 `QC Style Isosurface` + `QC Surface Representation` | C01：正/负相分别开关，0 solid / 1 wire / 2 points | 同一数值场显示两符号和三种样式；相位不表示电子电荷正负 |
| N05 独立等值与透明度 | C01：关 `Link Thresholds`、调 `Isovalue`/`Negative Isovalue` 与正/负 Opacity | 两相轮廓与透明度分别响应；阈值使用字段原单位 |
| N06 `QC Sample Scalar Field` | C04：密度网格取 ESP 颜色；C03：同网格采样 | 改几何场阈值不改变颜色场原值；域外采样标无效 |
| N07 `QC Map Scalar Colors v2` | C04：改 Color Minimum/Center/Maximum，开 Show Legend、改位置 | 色标与表面同步；范围严格递增，域外为紫红而非物理零 |
| N08 `QC Planar Slice` | C04：调中心、旋转、尺寸和分辨率 | 截面位置、像素尺寸变化，颜色按场值/单位解释 |
| N09 `QC Clip Geometry` | C01：Plane Enabled/Origin/Normal；Box Enabled/Minimum/Maximum | 平面/盒分别裁掉预期区域；原始体素和数值不变 |
| N10 `QC Style Volume Fog` | C01 自旋场：Fog、调 Color Minimum/Maximum、Opacity Range/Scale、Display Threshold 和曲线 | 体积颜色/不透明度变化，0 不透明度应不见雾；记录所用场量/单位 |
| N11 `QC Vector Glyph` | C04：Dipole、调 `Å/D` 显示比例 | 箭头长度变，物理三分量及方向/原点不变 |
| N12 振动位移与 `QC IR Sticks v1` | C02：换模式，调振幅/相位/播放速度、开位移箭头 | 原子显示位移、箭头与 IR 选中峰同步；平衡坐标不变 |
| N13 分析点标注 | C08/C09：显隐 ESP 极值、AIM 临界点/路径，选择不同点 | 点位和可查询记录随选择变化，不生成无依据的物理量 |
| N14 `QC scatter points` | C07：显隐、查询 δg–sign(λ₂)ρ 分布轴 | 散点来源于同网格两个真实场，轴值与场定义一致 |
| N15 显示层独立性 | C01/C02：Duplicate、排序、隐藏、删除、New Current-Version View | 改复制层节点/材质不改原层；源数组 SHA 不变 |
| N16 撤销/重做 | C01/C05/C06/C07–C13 有可用界面操作时 `Ctrl+Z/Ctrl+Shift+Z` | 对象、节点和科学数据关联回到预期状态；遇失败先记缺陷 |
| N17 域外与游标 | C04：在网格内、无效域、网格外各点一次 **Read at Cursor** | 显示数值及单位；无效/域外不作为 0，坐标换算正确 |
| N18 移动后冷重开 | 每例复制 `.blend` + `.qcdata/` 到另一目录、新进程打开、重渲染 | 来源/数值/节点/图例仍可用，原始数组摘要不变 |

可组合节点参考 [现有用户指南](../USER_GUIDE.md)；上述输入以当前 [`assets.py`](../../qcblender/blender/assets.py)、[`views.py`](../../qcblender/blender/views.py) 及操作入口为准。实际侧栏只显示适用于所选对象的输入。若某节点未暴露为按钮，在 Geometry Nodes 编辑器里找到对应 `QC …` 节点组并记录它的接线及修改器输入。

## 3. 结果与用户签署

下表只由实际验收者填写。每格写 `Passed / Failed / Not Run`，并在 `实测/证据` 填核心数值、PNG/场景文件、截图或缺陷编号。**缺真实样本的 C07–C13 目前必须保留 Not Run 且签名为空**；即使用户已操作别的案例，也不能把整体状态改为通过。

| 案例 | 导入 | 源数值/单位 | 节点前后 | PNG | 保存重开 | 移动冷重开 | 实测/证据/缺陷 | 用户签名与日期 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |  |  |
| C02 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |  |  |
| C03 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |  |  |
| C04 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |  |  |
| C05 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |  |  |
| C06 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |  |  |
| C07 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺 IGMH/IRI 真实输出 |  |
| C08 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺 ESP 表面真实输出 |  |
| C09 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺 AIM 真实输出 |  |
| C10 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺 IRC 真实逐步 FCHK |  |
| C11 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺逐步 Mayer 真实输出 |  |
| C12 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺 ETS-NOCV 真实输出 |  |
| C13 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 缺 NOCV pair 真实 Cube |  |

| 节点检查 | 结果 | 修改前 → 修改后 / 截图 / 缺陷 | 验收者签名与日期 |
| --- | --- | --- | --- |
| N01 | Not Run |  |  |
| N02 | Not Run |  |  |
| N03 | Not Run |  |  |
| N04 | Not Run |  |  |
| N05 | Not Run |  |  |
| N06 | Not Run |  |  |
| N07 | Not Run |  |  |
| N08 | Not Run |  |  |
| N09 | Not Run |  |  |
| N10 | Not Run |  |  |
| N11 | Not Run |  |  |
| N12 | Not Run |  |  |
| N13 | Not Run |  |  |
| N14 | Not Run |  |  |
| N15 | Not Run |  |  |
| N16 | Not Run |  |  |
| N17 | Not Run |  |  |
| N18 | Not Run |  |  |

最终签署仅在 **C01–C13 全部 Passed、N01–N18 逐项 Passed、九片真实样本齐全且修复后重做、科学回归/干净环境离线安装/移动冷重开/包摘要均 Passed** 时填写：

- 使用者对成品图和科学解释的总体结论：`Not Run`
- 候选 ZIP SHA-256：`________________`
- 验收者签名、日期、Blender 版本：`________________`
- 对 `v1.0.0` 公开发布的明确批准（单独填写；空白表示未批准）：`________________`

任一 `Failed` 或 `Not Run` 均保留候选状态，不推送发布标签、不公开 GitHub Release、不上传 Blender Extensions。首次平台上架仍需 Blender ID 上传与审核；平台审核状态须单独记录。
