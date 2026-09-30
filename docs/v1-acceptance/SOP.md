# QCBlender 0.0.1 跟随教程与独立人工验收 SOP

适用 **Windows x64、Blender 5.1.1**。取得 QCBlender 扩展 ZIP 和本教程指定样本后，即可在 Blender 中完成导入、调整、渲染和保存；安装包包含必要运行库。公开安装包是否可取得见 [README](../../README.md)，来源、许可及获取说明见 [SOURCES](SOURCES.md)。本教程绑定 [冻结样本清单](tutorial-samples.json)；P01/P03/P04/P05 在样本包中，C02/C06 所用 P02 需原站单独获取，其再分发许可未确认。安装包和样本包目前为本地交付，尚无已发布远程下载地址。

本教程保留 **C01–C13** 科学案例和 **N01–N18** 节点/交互检查编号。按钮位置与当前插件界面一致；对话框及部分控件仍使用英文。操作结果只记 **Passed / Failed / Not Run**。用户实际点击、Agent Computer Use 点击、MCP 数据核对、独立科研签署分别记录；Agent 不填写使用者签名。

## 0. 准备、安装与通用操作

### 0.1 取得材料并建立本次目录

1. 取得实际扩展安装 ZIP，核对提供者记录的版本、文件大小和 SHA-256；源码仓库 ZIP 不能直接安装为扩展。使用公开包时记录下载地址；维护者提供候选时记录候选身份。
2. 向提供者取得 **qcblender-public-tutorial-samples-v1.zip**，SHA-256 为 `a4ccfc3ef91921817d17284196ba23ccfb7cce7b1643cdfa41af8e8a6103f85b`。核对后解压到本次 `inputs/`，保留包内 P01/P03/P04/P05 目录、LICENSE、NOTICE 和 `tutorial-samples.json`，署名 **QCBlender contributors**。按 [SOURCES 的公开教程获取说明](SOURCES.md#公开教程样本与独立获取2026-09-30) 单独取得 P02。新计算数据使用 CC BY 4.0；第三方材料保留原许可。公开包只收录允许分发的文件。受限或许可未知的材料按原站获取步骤取得并核对摘要，不能因其可下载便视为可再分发。取得不了必要文件时，在相应案例记录阻塞和 Not Run，其他案例可以继续。
3. 在自己的工作目录新建一个独立批次目录，例如 `QCBlender-tutorial/2026-09-30-run01/`，下面建立 `inputs/`、`cases/C01/` 至 `cases/C13/` 和 `moved/`。输入保持样本包的相对目录结构，尤其 IRC 的 CSV 与逐步 FCHK/Mayer 文本不能分离。不要覆盖上一批工程或用户已有文件。
4. Windows PowerShell 中逐一核对安装 ZIP 和本次所用文件：

   ```powershell
   Get-FileHash -LiteralPath '实际文件的完整路径' -Algorithm SHA256
   ```

   与清单不符时停止该文件相关案例，重新取得原件；不编辑原文件以迎合预期。本文后续的 `cases/CXX/` 均指本次目录，无需源码仓库。开发者在仓库内执行时可将本批放在被忽略的 `outputs/runs/<批次>/`。

填写批次身份，不沿用历史候选的通过状态：

| 字段 | 本次填写 |
| --- | --- |
| 批次目录、操作者和日期 | 待填写 |
| Windows 与 Blender 精确版本 | 待填写 |
| 扩展 ZIP 下载/提供路径、字节数、SHA-256 | 待填写 |
| 扩展版本、源码身份或提供者资格报告 | 待填写 |
| 样本清单版本/摘要、所用文件 SHA-256 | 待填写 |
| 科学运行库检查结果及截图 | Not Run；[用户截图待引用] |

### 0.1.1 单独取得 P02（C02/C06 前置条件）

在 **本批 inputs/ 目录**打开 PowerShell。P02 使用 Gaussian 16 A.03 / NBO 3.1 的真实水优化/频率日志；下载定位与本地读取说明不授予再分发权限。先自行确认原站使用条件；不具备使用权或下载失败时，C02/C06 保持 Not Run 并记录原因，不需要安装计算软件补造结果。

```powershell
New-Item -ItemType Directory -Force P02 | Out-Null
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/cclib/cclib-data/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian16/water_neutral_nbo_opt_freq.out' -OutFile P02/water_neutral_nbo_opt_freq.out
Get-FileHash -LiteralPath P02/water_neutral_nbo_opt_freq.out -Algorithm SHA256
```

SHA 必须为 `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519`，字节数 **92,872**。核对成功后创建另一扩展名入口的逐字节副本：

```powershell
Copy-Item -LiteralPath P02/water_neutral_nbo_opt_freq.out -Destination P02/water_neutral_nbo_opt_freq.log
Get-FileHash -LiteralPath P02/water_neutral_nbo_opt_freq.log -Algorithm SHA256
```

两者摘要相同。该原站本轮取得与摘要核对 Passed，仅证明提供者检查时可取得；每位使用者仍需核对实际下载。不把 P02 文件放进公开附件或归档分发。

### 0.2 安装与编辑器定位

1. 打开 Blender 5.1.1，在 **Edit → Preferences → Get Extensions → 菜单 → Install from Disk** 选择扩展 ZIP，确认安装并启用 QCBlender。
2. 在 **Preferences → Add-ons** 展开 **QCBlender**，点击 **Check Scientific Runtime**。等待检查完成，记录真实结果；失败时保留错误，不继续场求值。
3. 回到 **3D Viewport**，选择 **Object Mode（物体模式）**，按 `N` 打开侧栏，选择 **QCBlender** 页。本文简称为“N 侧栏”。
4. **对象属性**指 **Properties 编辑器 → Object → QCBlender · 对象与量子化学**。多数子面板默认折叠，需点击标题展开。可选 QC 对象后点击 **N 侧栏 → 工作流 → 对象属性与显示参数** 打开该位置；若没有 Properties 编辑器，先将一个编辑器切换为 Properties。
5. Properties 顶部若固定了旧对象，先解除图钉固定再选新对象。每次新建场、优化轨迹、剖面或分析层后，在 Outliner 或 **N 侧栏 → Display Layers** 重新选中步骤指定对象。多选时最后选中的是活动对象，不能只凭画面可见确定活动对象。
6. N 侧栏负责导入、创建、显示层和工程操作；对象属性调整科学记录、几何、颜色、空间和局部选择；**Properties → Material → QCBlender · 节点材质** 调整材质。按钮灰显时读取界面原因，检查活动对象、物体模式和来源是否齐全。

### 0.3 导入、数值与参数核对

1. 每个独立案例使用新工程；需要承接前例的 C08、C11、C13，分别从 C04、C10、C12 已保存工程继续，并另存新文件。
2. 在 **N 侧栏 → 工作流 → 导入 Gaussian / Cube** 选择指定 `.fchk/.fch`、`.log/.out`、`.cube/.cub`。Log/Out 会异步打开 **Choose Gaussian Calculation**；在 **Calculation** 中选指定计算段，核对 route、终止状态、原文行范围、能量和 Explicit geometry，再确认。计算段从 1 开始；无显式几何时不自动借用其他段构型。取消预览后应无该次新数据对象。
3. 等待任务结束后选择新原子/场视图。在 **N 侧栏 → 数据集与数值摘要 → 查看完整来源** 或对象属性 **来源详情** 核对完整摘要、计算段、原子顺序、量名/单位；必要时点击 **刷新来源**。不是所有信息都显示在侧栏，能量和模式见对象属性。
4. 原子源编号从 1 起，坐标为 Å，1 Blender 单位 = 1 Å。能量为 Hartree/Eh，电荷为 e，偶极为 Debye，振动频率为 cm^-1，IR 强度为 km/mol。MO 振幅为 bohr^-3/2，密度为 electron/bohr^3，ESP 为 hartree/e。外部分析按其实际输出单位核对，不能自行补单位或换算依据。
5. 每个参数变化先记录原值，再改为本例指定值，观察实际显示并记录新值；完成对比后恢复用于最终成图的值。阈值、色标和网格使用清单中的展示参数及实际字段单位；定量结论另需收敛检查。
6. `.chk` 须由持有 Gaussian 的提供者事先用 `formchk` 导出 FCHK。本教程接收已转换的样本，运行教程无需安装 Gaussian、Multiwfn、PySCF 或开发环境。

### 0.4 相机、渲染、保存与移动冷重开（每例执行）

1. 选中具有实际空间几何的 QC 视图；C06 的 NBO 表、C11 的 Mayer 表、C12 的 ETS-NOCV 表只保存记录，先改选其关联原子或实际曲线等可渲染视图取景，面板总览截图时再回选记录表。在 3D Viewport 转到期望观察方向。点击 **N 侧栏 → 创建视图与检查工具 → 创建取景相机**；创建并激活正交相机后，用小键盘 `0` 查看取景，必要时 `F9` 在调整面板改变 **Margin per side**。默认每侧留白 5%。将不希望出图的显示层关闭渲染图标；保持需要的修改器视口/渲染开关一致。
2. 在 Blender 原生 **Render/Output Properties** 设置渲染器、分辨率和色彩管理，按需通过 **Add → Light** 添加灯光。使用 **Render → Render Image**（F12）；在 Render Result 中 **Image → Save As** 保存 `cases/CXX/CXX.png`。记录渲染器、分辨率、色彩管理、光源及参数；需要面板证据时另保存屏幕截图。渲染无法显示来源记录或列表时，`CXX.png` 使用面板总览截图，并另存 `CXX-render.png`。
3. 每张图旁记录样本摘要、方法/基组、场量/单位、MO 编号/自旋、网格和等值、颜色范围；振动另记模式频率、显示振幅和播放速度。PNG 是可见结果，数值依据仍为源文件和保存的科学数组。
4. 在 **N 侧栏 → 工程与诊断 → 保存自包含工程** 选择 `cases/CXX/CXX.blend`，确认同名 `CXX.qcdata/` 已生成。工程包含节点、材质、选择、动画设置和科学数组；原始外部文件、导出的 CSV 另行保留。
5. 正常关闭本次工程的 Blender，重新启动新进程，用 **File → Open** 打开 `CXX.blend`。重新选择本例对象，核对来源、参数、数值/单位与图例，重新渲染；C04 剖面还须重新导出 CSV。
6. 将 `CXX.blend` 和 `CXX.qcdata/` 一起复制到本批 `moved/CXX/`。关闭本次进程，在另一个新进程打开移动副本，再核对与渲染。记录原进程退出、新进程身份及数组摘要核对方式；未实际关闭重开时保存检查仍为 Not Run。
7. 再次保存最新修改后点击 **工程与诊断 → 归档工程**，选择输出 ZIP。解压到新的目录，保持整体结构，再从解压位置打开工程核对。
8. 恢复操作仅在独立副本进行：缺失 VDB 且科学数组完整时，选受影响视图，点击 **重建显示缓存**；数据目录确实移动时，点击 **重新定位数据**，选择同一数据集的 `manifest.json`，其内容摘要必须匹配。保存和新进程重开复核恢复结果。科学数组缺失时记录失败，表面不能重建波函数。

**通用截图槽：** 安装/运行检查 [用户截图待引用]；渲染设置 [用户截图待引用]；保存对话框与文件 [用户截图待引用]；新进程重开 [用户截图待引用]；移动重开/归档/恢复 [用户截图待引用]。每例记录各自路径，可引用同一批次公共安装截图。

## 1. C01–C13 输入与物理量教程

以下输入均相对本批 `inputs/`。清单的 `archive_path` 是样本包路径；`path` 是开发仓库路径，用户无需将文件放到 `tests/data/`。外部原件为 `P02/water_neutral_nbo_opt_freq.out/.log`。

所有待生成的 MO/密度/ESP 使用 **Grid spacing = 0.7 Å、Grid margin = 3 Å**，Memory budget 使用对话框默认 **512 MiB**，并记录实际网格；0.7 Å 是本批显示测试建议，不证明定量收敛。MO、等值、色域、振幅和其他展示值来自清单 `cases.gui/grid_defaults`，其状态是 **proposed；视觉 Not Run**，按以下值起步后记录实际轮廓和必要调整，不能将建议值称成图验收通过。外部 Cube 的真实网格不重采样为 0.7 Å。

| 案例 | 文件/源身份 | 本例展示设置 |
| --- | --- | --- |
| C01 | P01/o2-uhf.fchk、o2-uhf.fch；UHF/STO-3G O2 | Alpha MO9、Beta HOMO7；MO阈值0.045 bohr^-3/2；自旋±0.002 electron/bohr^3 |
| C02 | P02/water_neutral_nbo_opt_freq.out/.log；Job2频率、Job1优化 | 模式3；Amplitude 0.35 Å；Cycles per second 1 |
| C03 | P03/igmh/sl2r.cub、P03/color.cube | sign_lambda2_rho，electron/bohr^3，倍率1；正负阈值0.02 |
| C04 | P03/water-dimer.fchk | 密度等值0.004 electron/bohr^3；ESP色域−0.05/0/+0.05 hartree/e；Mulliken；偶极1.5 Å/D |
| C05 | P03/water-dimer.fchk/.fch | 保留氢源编号2；氧编号1、4；距离1,4；角2,1,3 |
| C06 | P02同C02 | Job2/block1；NBO1、E(2)记录1 |
| C07 | P03参考FCHK；igmh/dg_inter.cub、sl2r.cub；iri/func2.cub、func1.cub | 片段1–3/4–6；IGMH0.005 electron/bohr^4；IRI1，a=1.1；颜色−0.04/0/+0.04 electron/bohr^3 |
| C08 | P03参考/ESP场；esp/surfanalysis.pdb、esp/stdout.log | rho=0.001 electron/bohr^3；极值/分布中心kcal/mol；面积angstrom^2 |
| C09 | P03参考；aim/CPs.pdb、paths.pdb、CPprop.txt | 坐标Å；选源点1 |
| C10 | P04/steps.csv、step-001/002/003.fchk | 三步连续跨TS，按CSV顺序1→2→3 |
| C11 | P04/mayer-pyscf.csv、step-001/002/003-mayer-pyscf.txt | Mayer原子对1,2，无量纲 |
| C12 | P05/complex.fchk、nocv/ets-nocv.txt | kcal/mol，pair1，Spin Total |
| C13 | C12表与P05/nocv/nocv-pair1.cub | pair1/Total；electron/bohr^3；两符号阈值0.003 |

数值核对按源打印精度：坐标容差 **3e-6 Å**，FCHK 标量能量 **6e-7 Eh**，Log打印能量 **1e-9 Eh**，Cube公式核对 **3e-6**（原字段单位）。保存或改显示时数组应保留，不能用这些数值容差代替数组 SHA 一致性检查。

### C01 FCHK、开壳层轨道与密度

**真实输入预期：** O2 2原子，源顺序 O1/O2，坐标 (0,0,−0.6)/(0,0,+0.6) Å；中性三重态16电子，Alpha9/Beta7，源能量 **−147.633453 Eh**，每通道10个MO。选 Alpha/Source number/9 与 Beta/HOMO（应解析为7）；预览占据/轨道能量以源记录为准，不另填未知值。两FCHK入口 SHA 同为 `ef562c4b210e7c380219282d7684370cca1f0e8349dffa1d4388af5831472e36`。

1. 按 0.3 导入 P01 FCHK，再逐字节别名 `.fch`；选择各自原子对象，核对原子身份/顺序、坐标、方法、基组、电荷、多重度、电子数和电子总能量，两入口记录一致。
2. 保持 FCHK 原子视图活动，点击 **工作流 → 生成量子化学场**；Quantity 选 **Molecular orbital**，分别选 **Alpha/Beta**，按清单选 **Orbital → Source number** 并填 **Orbital number (1-based)**，或按已核对身份选 HOMO/LUMO。记录预览 Source MO、occupation、Energy；输入清单网格 **Grid spacing (angstrom)**、**Grid margin (angstrom)** 与 **Memory budget (MiB)**，确认等待生成。
3. 选择新 MO 场，在 **对象属性 → 科学记录与振动模式** 查量名/单位与轨道身份；在 **几何表示** 改正相/负相显隐、阈值、**Link Thresholds**、独立负阈值及实体/线框/点表示。材质属性改变两相颜色、透明度，验证相位与物理电荷不混淆。
4. 重新选择源原子对象，依次生成 **Electron density、Alpha density、Beta density、Spin density**，各次使用完全相同网格。分别选择生成场核对单位及自旋约定；数值核对总=Alpha+Beta、自旋=Alpha−Beta需源数组或数据核对证据，不能根据图形断言成立。
5. 选自旋场，点击 **创建视图与检查工具 → 创建体积雾**；选新雾视图，调整颜色、Opacity Range/Scale、Display Threshold 和材质曲线，记录全透明时实际结果。选场/原子视图点击 **添加裁剪控件**，在 **空间观察** 分别开关平面与盒裁剪，原始数组不变。
6. 对应 N01/N02/N04/N05/N09/N10；按 0.4 完成渲染保存。固定证据：`C01.png`、`C01-mo.png`、`C01-total.png`、`C01-alpha.png`、`C01-beta.png`、`C01-spin.png`、`C01.blend` 和配套目录。逐个改参数时另留前后截图。

**截图槽：** 轨道身份/两相/样式 [用户截图待引用]；五种场 [用户截图待引用]；裁剪/雾前后 [用户截图待引用]。

### C02 Log/Out 能量、振动与优化

**真实输入预期：** Job2 是中性单重态水，3原子 O/H/H，RHF/STO-3G，10电子；目标电子能量 **−74.9659011806 Eh**（与Job1最终优化步一致）。模式1/2/3频率 **2169.7613/4141.3837/4392.5759 cm^-1**，IR **7.2483/44.2724/29.9428 km/mol**；先选模式3。Job1有4优化步，能量依次 **−74.9643287914、−74.9649723283、−74.9659003010、−74.9659011806 Eh**。两扩展名都要完成导入。导入回归的下一文件固定 **P03/water-dimer.fchk**，预期6原子及其SHA；无P02 FCHK。

1. 按 0.3 导入 P02 Log/Out，选清单含频率的计算段。选择导入的**原子对象**，展开 **对象属性 → 科学记录与振动模式**，选择能量记录，核对 Hartree 值、方法、kind/role 和原文位置。参考 SCF、目标方法、ZPE/热校正分别记录，不能把最后一条 SCF 当成唯一目标值。
2. 同一面板模式列表选清单指定模式，核对源编号、频率、IR 强度与 IR 棒图高亮。在同级 **高级参数** 勾选 **Animate**，填写指定 **Amplitude (angstrom)** 和 **Cycles per second**，到 Timeline 点击播放，观察实际帧推进，再暂停；改变 Phase 和模式重复。在 **几何表示 → Show Displacement Vectors** 开位移箭头。平衡源坐标不变；播放速度不是物理振动频率。
3. 再点 **导入 Gaussian / Cube** 打开新的文件对话框，选同一 Log 的优化计算段。选其原子对象，点 **创建视图与检查工具 → 创建优化轨迹视图**；必须选中新轨迹对象，再展开 **对象属性 → Optimization Trajectory**，逐次点击 **Previous、Next、Choose Step**。核对步号、构型、能量、终止状态、收敛值/阈值及原文行范围。缺失/歧义能量按界面状态记录；优化步不是物理时间。
4. 在 Display Layers 复制优化轨迹，分别切到不同步，核对互不影响；原视图仍保留其已核实性质，轨迹不借用最终电荷、偶极或模式。C05 的标注也在 P02/P04 可操作的步序上核对随步更新。
5. **导入状态回归：** 本工程再次导入 Log，明确选 **Job 2** 并完成；随后点击 **导入 Gaussian / Cube** 打开**新文件对话框**导入 **P03/water-dimer.fchk**。核对新的计算段参数从 1 开始，导入成功、来源 SHA 为该 FCHK，未继承 Log 的摘要/job；不得以脚本执行 Operator 代替此项真实点击。
6. 对应 N12/N15/N16，按 0.4 保存。证据：`C02.png`、`C02-energy.png`、`C02-vibration.png`、`C02-ir.png`、`C02-optimization.png`、`C02-reimport.png` 及工程。

**截图槽：** Job预览 [用户截图待引用]；能量/模式 [用户截图待引用]；播放/IR [用户截图待引用]；优化两步 [用户截图待引用]；Log→Job2→FCHK [用户截图待引用]。

### C03 Cube/cub 物理量、网格与双符号

**真实输入预期：** `P03/igmh/sl2r.cub` 与 `P03/color.cube` 字节一致，SHA为 `18a33c308c868c9f7747128f1a23c04fc69df37fd5b9681aa5dd35ef20997958`；6原子，**91×38×156**，origin **(−1.2877770840,−0.5291772105,−0.5291772105) Å**，三轴步长 **0.02874808114 Å**。值域 **−194.599..+0.295371 electron/bohr^3**，量 `sign_lambda2_rho`，倍率 **1**。声明时选 **Other externally computed scalar field**，Physical quantity填 `sign_lambda2_rho`，Unit填 `electron/bohr^3`，该场数值不做额外倍率换算。

1. 分别导入 P03 Cube 和逐字节 `.cub` 别名，选各自场对象核对原子、网格和数值数组；普通 Cube 初始物理量可能为 **unknown_scalar / unknown**。
2. 选待声明场，点 **对象属性主面板 → 声明 Cube 物理量与单位**，只选择样本中数值实际已有的物理量/单位；声明不会换算数值。不匹配提供的选项时保留 unknown 并记录原始定义，不能冒选密度。
3. 在 **几何表示** 改两符号阈值与显隐，核对别名入口一致；按 C04 将一个真实几何场按另一个场着色，来源和网格必须匹配。
4. NCIPLOT 的倍率、RDG 过滤哨兵若出现在所选样本中按真实记录解释；普通 RDG 不能称 IGMH/IRI。没有该类样本时不套用旧 NCIPLOT 数值。
5. 对应 N04–N07，按 0.4 保存 `C03.png/.blend/.qcdata/`。

**截图槽：** Cube身份/单位声明 [用户截图待引用]；正负/别名前后 [用户截图待引用]。

### C04 ESP、电荷、偶极、切片、探针与剖面

**真实输入预期：** 水二聚体6原子 **[O,H,H,O,H,H]**，中性单重态20电子，RHF/6-31G(d)，能量 **−152.013820 Eh**。源SHA为 `02ffc555ac7bda6e263e8461481914db3a2576582f71b6b9ea97fa05df610d6a`。Mulliken原子1/2/4为 **−0.928340742/+0.461442520/−0.920221916 e**；偶极源向量为约 **(0,0,1.67243888) e·bohr**，界面以Debye展示，核对保留的单位换算记录。切片中心 **(0,0,1.45) Å**；游标剖面起点 **(0,−2,1.45)**、终点 **(0,+2,1.45) Å**，Geometry、101点、距离0..4 Å。源关联使用逐字节别名 **P03/water-dimer.fch**，不能用P02单水Log与水二聚体关联。

1. 导入 P03 FCHK，选原子对象分别 **生成量子化学场 → Electron density / Electrostatic potential**，使用同一指定网格；核对密度单位 electron/bohr^3、ESP hartree/e。ESP 核附近无效点不算物理零。
2. 选**密度表面**，打开 **对象属性 → 颜色映射 → 选择／替换着色场**，选择 ESP；核对候选源 SHA、job、量名/单位再确认。密度决定几何，ESP 决定颜色。隐藏独立 ESP 表面的显示和渲染，不删除其内部体场。
3. 填 **Color Minimum=−0.05、Color Center=0、Color Maximum=+0.05**，须严格递增；在 **图例排版** 开 **显示图例**（Show Legend），改 长宽/字号/小数/方向/旋转/位置。点击 **零中心对称** 输入 **R=0.05**，再 **读取有效范围** 对照一次读取结果；记录并恢复成图色域。材质属性改色带/Reverse，范围外用端点颜色，无效采样为洋红。
4. 旧多选映射使用新的未映射层独立复核：先选步骤2的密度表面，点 **N 侧栏 → 创建视图与检查工具 → 创建当前版本视图**，保留原层，新标准密度层尚未绑定色场。临时开启 ESP 表面的视口可见性，取消其他选择，在 Outliner 先选 ESP 表面，再 Shift 选新密度表面使其活动，确认恰好选中两个对象；F3 搜索 **Map Selected Field to Active Surface**，确认后核对与步骤2相同的来源。再用 **选择／替换着色场** 替换一次，范围和图例位置保留；恢复独立 ESP 表面隐藏。
5. 重新选原始原子对象，在 **科学记录与振动模式 → 设置原子电荷着色** 选真实存在的布居方法，核对指定原子电荷 e；已绑定网格着色的原子层需换独立层。点 **创建视图与检查工具 → 创建偶极矢量**，核对源三分量/Debye，改变 **Angstrom per Debye** 只改显示长度。
6. 选 ESP 场，点 **创建切片**；选新切片，在 **空间观察** 改 Center/Rotation/Width/Height，在 **几何表示** 改 **显示采样数/轴**（Resolution）。点 **按源网格或三个原子定平面**，选 **Grid ij / Grid jk / Grid ki / Three source atoms**，Associated atom view选水二聚体原子对象，First/Second/Third source atom分别填 **2/1/4**（三点非共线）；使用 3D Viewport 工具栏 **QC Slice Gizmo** 平移/旋转，核对平面记录。在对象属性 **切片等值线 → 开启等值线**，本例ESP切片选 **几何场**；先留 **阈值列表（空白：自动 9 条）** 为空，再填 **−0.02,0,0.02**（hartree/e）并点 **更新等值线**，等待异步曲线/标签更新，变更后无效单元不连线。
7. 选 ESP 场，在 **3D Viewport → N → View → 3D Cursor** 输入清单坐标，点击 **创建视图与检查工具 → 读取游标处场值**。分别在 **(0,0,1.45)**、核邻近 **(0,0,0)** 和域外 **(20,20,20) Å** 读取。核附近是否无效由实际网格掩码决定，0.7 Å 网格未必命中核的排除区；若核邻近仍有效，如实记录值，并将“无效域读数”保留 Not Run，另由同批数据核对验证真实无效格点，不能凭坐标宣称无效。无效/域外不能记物理0。点 **点击探针 · 几何场** 后在表面点击，退出探针；绑定色场的密度表面再用 **点击探针 · 绑定色场**，记录采样位置/单位和实际结果。
8. 选指定场或切片，输入游标起点，点击 **记录剖面起点**；保持**同一个活动视图**，输入终点，点 **创建线剖面**，先选 **Geometry**、填 **Samples=101**；绑定色场视图再明确选 Color复核。选新剖面，改 **剖面坐标轴与排版 → 应用排版**，点 **导出剖面 CSV** 保存 `C04-profile.csv`；核对距离 Å、字段单位、端点、valid 列及无效值空白。剖面是采样快照，移动排版不改 CSV。
9. 源关联复核：导入 **P03/water-dimer.fch** 别名，选两个同构型原子对象，最后选参考对象，点 **对象属性主面板 → 关联选中数据源**。检查原子顺序和构型，按实际需要开启刚体配准；线性/单中心几何不自动唯一配准。两个理论层次/能量各自保留。
10. 对应 N06–N11/N17，按 0.4 保存；冷重开与移动后再次导出 CSV，核对保存数组/摘要。证据：`C04.png`、`C04-esp.png`、`C04-charge.png`、`C04-dipole.png`、`C04-slice.png`、`C04-profile.png`、CSV 和工程。

**截图槽：** 映射/图例 [用户截图待引用]；电荷/偶极 [用户截图待引用]；切片/等值线 [用户截图待引用]；探针三类结果 [用户截图待引用]；剖面/CSV [用户截图待引用]；来源关联 [用户截图待引用]。

### C05 氢显隐、局部选择、标注与显示层

**真实输入预期：** 同C04水二聚体，氢源编号 **2/3/5/6**，保留 **2**；氧集合 **1,4**。编号标注 **1**；距离 **1,4 = 2.9 Å**；角 **2,1,3 = 112.7698904°**；二面角 **2,1,4,5 = 0.000°**（项目B→C约定）。这些标注预期由已核对FCHK源坐标经项目measure实算，显示可取三位小数。优化/IRC随步更新另用C02/C10，不影响本例静态样本可运行。

本例静态氢、局部选择和全部标注统一使用 **P03水二聚体**；P01 O2不含氢。随步更新另在C02/P02和C10/P04复做。

1. 导入 **P03/water-dimer.fchk**，选原子对象，在 **对象属性 → 局部选择与标注** 依次点击 **隐藏氢 → 保留指定氢 → 显示全部氢**，按清单填一个真实氢的源编号，核对只保留指定氢及全恢复。每步记录前后；撤销/重做核对状态。
2. 点 **设置局部选择**，在 **Source atom numbers (1-based)** 先填 **1,4**、Mode=**Replace**；再填 **2**、Mode=**Union**（得1,2,4），填 **1,2**、Mode=**Intersect**（得1,2），填 **2**、Mode=**Difference**（得1），最后Mode=**Invert**（得2–6）。再次点 **设置局部选择**，选 **Replace**、编号 **1**，勾 **Include distance neighborhood**，以源 **1** 为种子、填 **Radius (Å)=1.0** 并勾 Include seed atoms，预期包括1/2/3。局部集合和元素、连续编号、氢筛选共同作用。点 **清除局部限制** 恢复其他筛选控制的范围。
3. 保持原子对象，点击 **创建视图与检查工具 → 创建局部显示层**，输入对应编号/半径，新副本独立调整样式/材质。优化/IRC 上局部集合固定源编号，换步不会自动换集合，必要时点 **按当前步重新计算**；IRC 仅在原层选择，不创建局部副本。
4. 选择 **P03水二聚体原子对象**，分别点 **创建编号标注／创建距离标注／创建角度标注／创建二面角标注**，按测量顺序填实际源编号；编号填 **1**，距离填 **1,4**，角度填 **2,1,3**，二面角填 **2,1,4,5**。核对距离 Å、角度度数、带符号二面角范围 (-180°,180°]；退化构型显示 undefined 与原因。
5. 在 **局部选择与标注 → Source Atom Annotations** 用设置图标调整文字大小/颜色/偏移/小数和引线；原子源构型或当前优化/IRC 步决定值，对象缩放与振动位移不改变测量。切步核对文字、锚点、步号同步；相机建好后点 **Face All to Camera**。
6. 在 **N 侧栏 → Display Layers** 选择层，用复制图标建立副本，改副本参数/材质确认原层不变；排序、视口/渲染显隐和删除只在副本测试。点击 **创建视图与检查工具 → 创建当前版本视图**，保留原层并核对新层。多选同类层，最后选参数源，在 **3D Viewport → 对象右键菜单 → QCBlender → 复制显示参数到选中视图** 选类别；数值复制需同量/单位/电荷方法，不兼容时取消数值类别。目标位置、选择、裁剪和图例布局保留。
7. 对应 N01–N03/N15/N16，按 0.4 保存 `C05.png/.blend/.qcdata/`，加 `C05-selection.png`、`C05-annotations.png` 与显示层前后截图。

**截图槽：** 三步氢显隐 [用户截图待引用]；集合/邻域 [用户截图待引用]；四类标注/换步 [用户截图待引用]；复制/排序/参数复制前后 [用户截图待引用]。

### C06 NBO 与 E(2)

**真实输入预期：** P02 **Job2/block1**，7条NBO、2条E(2)。NBO1为 O1–H2 的 BD，occupancy **1.99933**、energy **−0.77653 Eh**、原文行 **1444**；E(2)记录1 donor **1**→acceptor **7**、**0.59 kcal/mol**、原文行 **1434**。源SHA同0.1.1，不能把NBO编号当MO编号。

1. 确认已合法取得 P02 的真实 Log/Out 并核对 SHA；公开包不含许可未知原件。按 0.3 选清单指定 job 导入，选其原子对象，点 **N 侧栏 → 导入外部结果 → NBO 记录**。
2. 对话框 **Gaussian Log / Out** 选同文件，**Gaussian job (1-based)** 与 **NBO block within job (1-based)** 按清单填，确认等待。NBO 几何关联要同段同构型，不能借优化多构型段作最终关联。
3. 选生成 NBO 记录对象，在 **对象属性 → NBO Records** 选择一条 NBO 和 E(2)，核对条数、占据、能量单位、原子编号、供受体、E(2) kcal/mol 与原文行；NBO 不自动等同 canonical MO。
4. 在 **External Result Browser** 按编号/类型/占据、供受体/E(2) 筛选排序，点击 **应用筛选**，核对筛选不改源记录。恢复全部，撤销/重做导入核对关联。
5. 对同文件逐字节 `.log` 别名重复入口检查，摘要必须一致。别名在自己的 inputs 建立，不改原文件。
6. 按 0.4 保存 `C06.png/.blend/.qcdata/`；总览必须同时拍到可读 NBO/E(2) 面板和关联分子。

**截图槽：** 输入job/block [用户截图待引用]；NBO与E(2) [用户截图待引用]；筛选/恢复 [用户截图待引用]。

### C07 IGMH、IRI 成对场与散点

**真实输入预期：** P03参考与成对场6原子、片段 **1–3 / 4–6**，各Cube同为 **91×38×156**；Multiwfn **2026.9.20**。IGMH Geometry=`igmh/dg_inter.cub`，electron/bohr^4；Color=`igmh/sl2r.cub`，electron/bohr^3。IRI Geometry=`iri/func2.cub`，`a.u. (electron^-0.1 bohr^-0.7)`；Color=`iri/func1.cub`，electron/bohr^3；**a=1.1**。IGMH几何值域1.01735e-10..0.0185476，IRI几何0.0593502..11.432；颜色−194.599..+0.295371，原值不除100。色域截断只是显示。

1. 导入 P03 参考 FCHK，选择同构型原子对象，点 **导入外部结果 → IGMH / IRI 成对场**。
2. **Analysis** 选 IGMH，分别在 **Geometry Cube** 与 **sign(lambda2)rho Cube** 填清单文件，填 **Geometry value unit、Color value unit、Color minimum/maximum**，确认。再次以 IRI 输入其成对文件和 **IRI density exponent a**；片段、方法/版本、a、网格与单位按真实生成记录核对，不能用另一类几何场替代。
3. 选几何场改等值与色域：位置由几何场、颜色由第二场决定；查看来源核对两输入 SHA 与完全相同网格。
4. 选散点对象，打开 **对象属性 → External Result Browser**，核对横/纵轴量名/单位，改上下界并点 **更新散点**，交换轴重复。核对匹配总数/显示数；最多显示 50,000 点是显示抽样，不是删除科学数组。
5. 错误输入检查前重新选择 **P03参考原子对象**，重新打开配对导入，选 **IGMH** 并重填对应单位。Geometry使用 **P03/igmh/dg_inter.cub**，Color误选 **P05/nocv/nocv-pair1.cub**，应先因原子身份/构型不匹配拒绝；记录实际错误，这个组合不单独证明网格检查通过。然后恢复正确配对；不修改原Cube。
6. 对应 N06/N07/N14/N16，按 0.4 保存 `C07-igmh.png`、`C07-iri.png`、`C07-scatter.png`、总览与工程。

**截图槽：** 成对场对话框 [用户截图待引用]；IGMH/IRI [用户截图待引用]；散点轴/筛选 [用户截图待引用]；错误拒绝 [用户截图待引用]。

### C08 ESP 极值与面积分布

**真实输入预期：** P03 **rho=0.001 electron/bohr^3** 表面；4最大值/3最小值，PDB B-factor是ESP，**kcal/mol**，坐标Å。例如最大值源1：**36.69 kcal/mol** @ **(−1.740,−0.051,1.026) Å**；最小值源1：**−25.50** @ **(−0.036,−1.400,1.768) Å**。面积各bin见原stdout，合计 **73.1833 Å²**。C04初始0.004密度表面若作为视觉参照，先改成0.001并单独记录；分析导入活动对象仍是ESP场。

1. 打开C04工程另存为C08。先选**密度表面对象**，在 **对象属性 → 几何表示 → 正值阈值**（Isovalue）从 **0.004** 改为 **0.001 electron/bohr^3**，记录新旧画面；也可创建独立密度等值面层并设0.001。然后重新选**实际ESP场对象**，点 **导入外部结果 → ESP 表面分析**。密度表面即使按 ESP 着色，也不能替代这个活动参考对象。
2. 填 **Extrema PDB、Area distribution text、Surface definition、Extrema value unit、Distribution center unit、Area unit**，均用清单所记真实表面定义/单位；PDB REMARK/table 声明与用户指定须一致。
3. 选择生成的 maximum/minimum 层，在 **External Analysis Records** 逐项读极值/坐标；在 **External Result Browser** 按源编号/数值筛选并 **应用筛选**，显示标签和点，核对选择突出位置。值源于 PDB B-factor 时记录该约定。
4. 选择面积层，按中心或完整区间筛选，核对原始总面积、所选小计、各 bin 百分比和原表，筛选不重新归一化。
5. 对应 N13/N16，按 0.4 保存 `C08-extrema.png`、`C08-area.png`、总览与工程；不同单位时仅采用有证据的换算。

**截图槽：** 表面定义/单位 [用户截图待引用]；极值/筛选 [用户截图待引用]；面积/小计 [用户截图待引用]。

### C09 AIM 临界点、路径与属性

**真实输入预期：** 11临界点属性记录、10路径；源点1类型 **C/(3,−3)**，坐标 **(−0.724,0,3.384) Å**（PDB打印精度），对应源核6(H)，Density of all electrons **0.4316646446**，源属性单位约定按CPprop原文。本样本实际点类型以原文件为准，空类型保持不存在；不要为了C/N/O/F齐全制造记录。

1. 导入 P03 同构型参考 FCHK，选原子对象，点 **导入外部结果 → AIM 拓扑**，分别填 **CPs PDB、Paths PDB、CP properties text (optional)**。有真实属性才填第三项。
2. 选生成 C/N/O/F 点层和路径层，在 **External Analysis Records** 查类型、坐标、路径组、属性值/单位和原子关联；本样本没有的类型不凭空构造。
3. 在 **External Result Browser** 选源编号，按已有数值过滤，点 **应用筛选**；分别开关点/标签/路径，选另一类型须换对应层。筛选恢复后源记录不变。
4. 对应 N13/N16，按 0.4 保存 `C09-points.png`、`C09-paths.png`、总览与工程。

**截图槽：** 三文件角色 [用户截图待引用]；点/属性 [用户截图待引用]；路径/过滤 [用户截图待引用]。

### C10 真实 IRC 步序与能量

**真实输入预期：** H2O2四原子 **[O,O,H,H]**，RHF/STO-3G，中性单重态18电子；原生geomeTRIC **1.1.1** 双向IRC，61接受帧，截取0-based **29/30(TS)/31**。CSV中的1/2/3依次对应它们，FCHK打印能量 **−148.764884 / −148.764883 / −148.764884 Eh**；TS唯一虚频 **−48.1434547807 cm^-1**、最大梯度 **1.893862e-8 Eh/bohr**。三点邻近TS，构型变化小，核对坐标/游标而非要求肉眼发生大反应；不能把该短段称为完整61步路径。

1. 按清单保持 P04 CSV 和逐步 FCHK 相对目录。CSV 是 UTF-8，首行为 `step,fchk`，步号从 1 连续，文件顺序与记录的反应方向一致；输入来自真实 IRC 计算。
2. 在 **N 侧栏 → 工作流 → 导入 IRC 路径** 在 **CSV manifest: step,fchk** 指定 steps CSV，等待建立根原子视图与曲线；选**IRC 根原子对象**，打开 **对象属性 → IRC Path**。
3. 点击 **Previous/Next** 遍历每步，核对步号、原子身份/坐标、hartree 能量及曲线游标。确认端点和当前清单；能量须对应该步 FCHK。
4. 在 C05 同入口添加当前步距离/角度/二面角标注，换步核对文字和锚点同步；局部集合保持固定编号，需要时重新计算。
5. 在 **inputs/P04/** 复制steps.csv为 **checks-duplicate.csv**，用文本编辑器把第二行数据的step也改为1，保留FCHK相对路径，保存UTF-8；用该副本导入应拒绝重复编号，记录副本摘要和错误。再用完整原CSV导入；原件不改。
6. 对应 N15/N16/N18，按 0.4 保存 `C10-curve.png`、`C10-steps.png`、总览与工程。

**截图槽：** CSV输入 [用户截图待引用]；两步构型/游标 [用户截图待引用]；端点/错误拒绝 [用户截图待引用]。

### C11 IRC 逐步 Mayer 键级

**真实输入预期：** 同C10三步、每步六对Mayer；原子对 **1,2** 值 **0.987331413844 / 0.987349305673 / 0.987331413844**，无量纲。可换对1,3：**0.950875651565 / 0.950844120525 / 0.950875651565**，复核独立曲线。结果来自同构型PySCF AO密度/重叠矩阵，文本采用兼容输入语法，其producer不是Multiwfn。

1. 打开 C10 工程另存 C11，选 **IRC 根原子对象**，在 **对象属性 → IRC Path → Import Mayer Results** 在 **CSV manifest: step,mayer_output** 指定清单的 Mayer CSV。
2. 选择新 Mayer 记录对象，在 **IRC Path** 填 **Atom A (1-based)、Atom B (1-based)**，点击实际按钮 **Plot Pair**；核对原子对、每步值/无量纲单位和源文本。
3. 切 IRC 步观察构型、键级曲线游标及显示值同步，再换原子对点 Plot Pair。距离推断显示键不是 Mayer 值。
4. 缺步检查在**尚无Mayer表的IRC根**上执行：重新打开C10工程的独立副本，或从完整steps.csv新建IRC路径，再选根对象。在 **inputs/P04/** 复制Mayer CSV为 **checks-missing-mayer.csv**，删除step3的数据行并保存UTF-8，相对文本路径保留；用副本导入应报 **Mayer step count differs from the IRC path**，且不产生新表。记录副本摘要/实际错误，再导入完整原CSV；已有Mayer表的拒绝不计为缺步检查通过。按 0.4 保存 `C11-curve.png`、`C11-records.png`、总览与工程。

**截图槽：** Mayer CSV [用户截图待引用]；原子对/数值 [用户截图待引用]；切步曲线 [用户截图待引用]。

### C12 ETS-NOCV 真实结果表

**真实输入预期：** CO–BH3共6原子 **[C,O,B,H,H,H]**，22电子，中性单重态，RB3LYP/6-31G(d)，源能量 **−139.947332 Eh**。pair1 **Total** 对轨道 **1/48**，特征值 **±0.54550**，pair能量 **−57.02 kcal/mol**，原表行7。此能量为真实整体KS矩阵重构的 **Multiwfn近似**，不是F_TS过渡态方法；详情见清单/NOTICE。

1. 导入 P05 参考构型，选原子对象，点 **导入外部结果 → ETS-NOCV 表**。填 **ETS-NOCV output text**，**Pair energy unit** 选文件实际 kcal/mol 或 hartree。
2. 选新表对象，在 **External Analysis Records** 查 pair、spin、特征值、成对轨道编号、能量、原文行号和源 SHA，与同次真实输出核对。
3. 在 **External Result Browser** 按 pair/spin/能量等筛选排序，点击 **应用筛选**。字段缺失按缺失记录，不推断数值。已有唯一关联场时可定位；没有时不表示已生成 pair Cube。
4. 按 0.4 保存 `C12.png/.blend/.qcdata/`，图中同时可读结果表与参考分子。

**截图槽：** 文件/单位 [用户截图待引用]；表记录/来源 [用户截图待引用]；筛选 [用户截图待引用]。

### C13 NOCV pair Cube 与两符号密度

**真实输入预期：** `P05/nocv/nocv-pair1.cub`，pair1/Total，与C12表和构型一致；网格 **47×50×57**，值域 **−0.243093..+0.0494892 electron/bohr^3**，SHA为 `d6d3ec263d5173261791f997eabd78b8112f6685abc3bd851c70deec86a82e33`。正/负阈值从 **0.003** 开始；用不存在pair **999** 或错误Spin **Alpha**观察关联拒绝。

1. 打开 C12 工程另存 C13，选 **ETS-NOCV 表对象**，点 **导入外部结果 → NOCV pair Cube**，在 **Pair number、Spin、Signed pair Cube、Deformation density unit** 填清单 pair 编号、自旋、Cube 路径与数值已有单位，确认等待。
2. 选新 pair 场核对表行/pair/spin、参考构型、Cube SHA 和密度单位；不能用 canonical MO Cube 冒充 NOCV 密度。
3. 在 **几何表示** 分别显示正/负值，关 Link Thresholds 后各自改阈值，在材质属性改透明度。正负值为形变密度的符号，不能套用 MO 相位解释。
4. 先重新选择 **C12的ETS-NOCV表对象**，再打开pair Cube导入，用表中不存在的pair **999** 或错误Spin **Alpha**复核关联拒绝；活动pair场不能作为导入参考。记录错误，随后恢复合法输入。对应 N04/N05/N16，按 0.4 保存 `C13-positive.png`、`C13-negative.png`、总览与工程。

**截图槽：** pair/spin关联 [用户截图待引用]；两符号前后 [用户截图待引用]；错误拒绝 [用户截图待引用]。

## 2. N01–N18 节点与交互检查

以上教程先通过对象/材质属性操作。需查看实际节点时，选指定视图，将一个编辑器切为 **Geometry Node Editor**，取消其图钉固定，选择该视图的 Geometry Nodes 修改器/节点组。修改器输入与对象属性共享参数；内部绑定 Dataset 的节点不作为独立通用资产。**Asset Browser → QCBlender Nodes** 按目录查找九个公共资产，添加到独立测试副本，核对已有输入/输出并接入真实视图。操作前保存，新增节点或改接线仅在副本进行；记录实际节点名、接线、原值→新值和可见变化，不以节点名称存在计 Passed。

新建视图的外层节点按可见Frame查找：原子 **Atoms: selection and representation**；振动 **Modes: displacement and animation**；等值面 **Field: source and isosurface**；映射 **Scalar: sampling and colors**；电荷 **Charge: attributes and colors**；图例 **Legend: range and labels**；切片 **Slice: plane placement**。Frame用于阅读，不增加物理量或公共节点；实际节点和接线仍以所选视图为准。

| 检查 | 活动对象、入口和操作 | 预期/需记录 |
| --- | --- | --- |
| N01 QC Select Atoms | C01/C05 原子；Geometry Nodes 中 Selection、元素号、源编号首末；再局部集合 | 源编号从1；O2用实际O编号，水再选氢；交集与源数组保持一致 |
| N02 QC Style Atoms and Bonds | 原子；对象属性→几何表示；球棍/空间填充/键，改原子与键半径 | 轮廓不同；半径Å，键是距离推断 |
| N03 氢显隐 | C05含氢原子；局部选择与标注的三个氢按钮、撤销重做 | 指定氢身份正确，副本不改原层 |
| N04 QC Style Isosurface / QC Surface Representation | C01/C13场；几何表示；两符号开关与实体/线框/点 | 两符号与三样式确实变化；各量符号含义正确 |
| N05 独立等值与透明度 | C01/C13场；关Link Thresholds、改两阈值；材质改两透明度 | 分别响应，字段单位正确，源数值不变 |
| N06 QC Sample Scalar Field | C04密度表面绑定ESP；C03同网格采样；Geometry Nodes检查接线 | 几何和颜色分工；域外无效，与来源绑定一致 |
| N07 QC Map Scalar Colors v2 | C04映射视图；颜色映射、零中心/有效范围、图例排版、材质色带 | 色标/量单位同步，范围递增，无效洋红，副本布局独立 |
| N08 QC Planar Slice | C04切片；空间观察、定平面/Gizmo、切片等值线 | 平面/分辨率/曲线变化，采样与单位一致 |
| N09 QC Clip Geometry | C01原子/场；添加裁剪控件后空间观察 | 平面/盒分别裁预期区域，原始数据不变 |
| N10 QC Style Volume Fog | C01自旋雾；几何表示/颜色映射/材质控制 | 颜色/阈值/不透明度变化，全透明无雾 |
| N11 QC Vector Glyph | C04偶极；节点或几何控件Angstrom per Debye | 显示长度变，物理方向/三分量/原点不变 |
| N12 振动/ QC IR Sticks v1 | C02频率原子；科学记录模式、Advanced/高级参数、Timeline、位移箭头 | 切模式/实际帧推进/IR高亮同步，平衡坐标不变 |
| N13 分析点标注 | C08/C09点/路径层；External Result Browser、应用筛选 | 显隐/定位/标签随记录选择，源值保留 |
| N14 QC scatter points | C07散点；External Result Browser→更新散点、轴交换 | 两真实字段量单位明确，匹配数/显示数分别记录 |
| N15 显示层独立性 | C02/C05副本；Display Layers、创建当前版本视图、右键复制显示参数 | 节点/材质/标注独立，排序/显隐/删除正确，原数组SHA不变 |
| N16 撤销/重做 | C01/C05/C06/C07–C13；3D视口Ctrl+Z/Ctrl+Shift+Z | 对象、节点、数据关联恢复；失败先记缺陷，不吞异常 |
| N17 游标/无效域/探针/剖面 | C04场/切片；读取游标、点击探针、剖面起点/创建/CSV | 量单位与坐标换算正确，无效/域外非零替代；CSV重导一致 |
| N18 保存/移动/冷重开 | 每例执行0.4；保存自包含工程、归档、恢复 | 新进程和移动副本来源/数组/节点/图例可读，摘要核对 |

**节点截图槽：** N01–N18 各项 [用户截图待引用]，在下表引用对应 C 案例前后截图即可；不能用一个最终渲染证明全部参数变化。

## 3. 结果记录与独立科研签署

### 3.1 操作证据与身份

每个案例按下表逐步填写，可复制行；未实际执行保持 Not Run。所有路径相对本次批次，截图槽由用户在实际复做后填写。

| 案例/步骤 | 活动对象/选择顺序 | 编辑器/面板/实际文字 | 参数原值→新值 | 预期→实际 | 结果 | 证据/用户截图 | 执行者/方式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CXX/步骤号 | 待填写 | 待填写 | 待填写 | 待填写 | Not Run | [用户截图待引用] | 待填写 |

| 证据身份 | 可证明的范围 | 本次填写 |
| --- | --- | --- |
| User：用户实际操作 | 用户执行的明确点击与反馈；无反馈步骤不推定完成 | Not Run；截图/反馈待填写 |
| Agent Computer Use | 经授权在可见窗口实际点击；记录安装、进程、活动对象与截图 | Not Run；由根Agent记录 |
| MCP 数据核对 | 读取候选实例的数组/摘要/进程；准备对象/游标时记录辅助范围 | Not Run；不能作为点击或用户签署 |
| 原生脚本数据核对 | 维护者的自动化解析/数组/原生operator检查；独立绑定候选与命令 | Not Run；本表由当前批次执行者填写，维护者本轮结果见验证索引 |
| 独立科研复做与签署 | 独立使用者复做操作，并判断科学记录与成图适用性 | Not Run；姓名/日期留空 |

[cleanup-validation.json](../acceptance/cleanup-validation.json) 记录历史批次技术核查与部分 Agent 点击，以及导入参数错误的历史复验。历史 Passed 不继承到本批；本教程的执行记录须关联本批候选和输入身份；本轮[验证索引](../acceptance/tutorial-validation.json)记录原生技术核对及未完成的实际点击。截图占位由实际操作者补入，技术通过不自动填写本表。安装资格、自动测试、真实点击、科研签署是不同结论。

### 3.2 独立使用者案例结果

此表仅由实际独立验收者填写；Agent 技术记录放在 3.1。每项写 Passed / Failed / Not Run，任何必需项 Failed 则该例 Failed；缺输入、未执行或只见测试报告不能填写 Passed。记录缺陷编号和修复后的候选身份，重新执行受影响步骤。

| 案例 | 导入 | 源数值/单位 | 参数/节点前后 | PNG | 保存重开 | 移动冷重开 | 实测/证据/缺陷 | 用户签名与日期 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C02 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C03 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C04 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C05 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C06 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C07 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C08 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C09 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C10 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C11 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C12 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |
| C13 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | [用户截图待引用] |  |

| 节点/交互 | 结果 | 前后截图/实测引用 | 缺陷 |
| --- | --- | --- | --- |
| N01 | Not Run | [用户截图待引用] |  |
| N02 | Not Run | [用户截图待引用] |  |
| N03 | Not Run | [用户截图待引用] |  |
| N04 | Not Run | [用户截图待引用] |  |
| N05 | Not Run | [用户截图待引用] |  |
| N06 | Not Run | [用户截图待引用] |  |
| N07 | Not Run | [用户截图待引用] |  |
| N08 | Not Run | [用户截图待引用] |  |
| N09 | Not Run | [用户截图待引用] |  |
| N10 | Not Run | [用户截图待引用] |  |
| N11 | Not Run | [用户截图待引用] |  |
| N12 | Not Run | [用户截图待引用] |  |
| N13 | Not Run | [用户截图待引用] |  |
| N14 | Not Run | [用户截图待引用] |  |
| N15 | Not Run | [用户截图待引用] |  |
| N16 | Not Run | [用户截图待引用] |  |
| N17 | Not Run | [用户截图待引用] |  |
| N18 | Not Run | [用户截图待引用] |  |

### 3.3 最终签署

仅在 C01–C13 必需项全部 Passed、N01–N18 逐项 Passed、真实必要样本与许可/获取记录齐全、同批科学回归/离线安装/保存和移动冷重开及包摘要核对全部 Passed、缺陷修复后已重做时，由独立使用者填写：

- 独立使用者姓名：________
- 日期：________
- 本批候选 ZIP SHA-256：________
- 本批样本清单身份及输入摘要记录：________
- 复做工程、截图和数值记录目录：________
- 科研适用性与剩余限制：________
- 签署：________

独立人工验收当前 **Not Run**。Agent 不代签，不将已编写教程、已生成样本或技术检查作为独立科研接受证据。
