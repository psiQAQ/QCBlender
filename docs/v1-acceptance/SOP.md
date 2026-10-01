# QCBlender 0.0.1 跟随教程与独立人工验收 SOP

适用 **Windows x64、Blender 5.1.1**。取得 QCBlender 扩展 ZIP 和本教程指定样本后，即可在 Blender 中完成导入、调整、渲染和保存；安装包包含必要运行库。公开安装包是否可取得见 [README](../../README.md)，来源、许可及获取说明见 [SOURCES](SOURCES.md)。本教程绑定 [冻结样本清单](tutorial-samples.json)；P01/P03/P04/P05 在样本包中，C02/C06 所用 P02 需原站单独获取，其再分发许可未确认。安装包和样本包目前为本地交付，尚无已发布远程下载地址。

本教程保留 **C01–C13** 科学案例和 **N01–N18** 节点/交互检查编号。按钮位置与当前插件界面一致；对话框及部分控件仍使用英文。操作结果只记 **Passed / Failed / Not Run**。用户实际点击、Agent Computer Use 点击、MCP操作与数据核对、独立科研签署分别记录；Agent 不填写使用者签名。维护者按 [交互规则](../agents/blender-interaction.md) 和 [操作登记表](../acceptance/blender-operations.json) 复用已确认且功能未变的操作，MCP/命令行复验单独记录，完整案例结果仍逐项验收。

本文的 Agent 示例截图紧接相应操作展示，原始 JPEG 保存在同级 `screenshot/` 目录。截图记录本批可见 Blender 状态；图注区分 Computer Use 实际点击与 MCP 执行后观察截图，保留你的逐步骤截图占位；各图的候选身份、输入、参数和检查范围见 [点击补验索引](../acceptance/tutorial-cu-validation.json)。C02、密度生成/取样/CSV、氢显隐与首次保存使用90ff9bf候选；IR层显隐复验、最终剖面、相机、渲染及冷重开使用1554ee2候选。候选92d498c的C01雾修复与三路径冷重开、C02能量/振动/优化/连续导入/渲染/三路径冷重开，以及C03双符号/独立着色/保存和MCP三路径冷重开截图同样逐步骤展示，候选e26d22a的C04切片/Gizmo/等值线、ESP几何及绑定色场探针、ESP剖面排版截图亦按步骤展示；其中MCP设置坐标、重放和冷重开单独标明。具体范围见索引 full_batch_progress；完整C/N点击覆盖及独立科研签署仍为Not Run。你复现时，将自己的截图保存到 `screenshot/`，在对应占位下一行填写 `![用户复做：C02-01](screenshot/C02-01-user.png)`；使用独立文件名，保留 Agent 示例便于对照。

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
| 科学运行库检查结果 | Not Run；证据见 0.2 步骤2 |

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

   [用户截图待引用：0.2-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 在 **Preferences → Add-ons** 展开 **QCBlender**，点击 **Check Scientific Runtime**。等待检查完成，记录真实结果；失败时保留错误，不继续场求值。

   [用户截图待引用：0.2-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 回到 **3D Viewport**，选择 **Object Mode（物体模式）**，按 `N` 打开侧栏，选择 **QCBlender** 页。本文简称为“N 侧栏”。

   [用户截图待引用：0.2-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例：QCBlender N 侧栏与工作流入口](screenshot/00-qcblender-sidebar.jpg)

4. **对象属性**指 **Properties 编辑器 → Object → QCBlender · 对象与量子化学**。多数子面板默认折叠，需点击标题展开。可选 QC 对象后点击 **N 侧栏 → 工作流 → 对象属性与显示参数** 打开该位置；此快捷按钮会固定当前对象，换对象后须再次点击按钮或解除图钉。若没有 Properties 编辑器，先将一个编辑器切换为 Properties。

   [用户截图待引用：0.2-04，活动对象、参数与结果同屏；参数变化保留前后画面]

5. Properties 顶部若固定了旧对象，先解除图钉固定再选新对象。每次新建场、优化轨迹、剖面或分析层后，在 Outliner 或 **N 侧栏 → Display Layers** 重新选中步骤指定对象。多选时最后选中的是活动对象，不能只凭画面可见确定活动对象。

   [用户截图待引用：0.2-05，活动对象、参数与结果同屏；参数变化保留前后画面]

6. N 侧栏负责导入、创建、显示层和工程操作；对象属性调整科学记录、几何、颜色、空间和局部选择；**Properties → Material → QCBlender · 节点材质** 调整材质。按钮灰显时读取界面原因，检查活动对象、物体模式和来源是否齐全。观察材质颜色时切换 3D Viewport 为 **Material Preview**；Solid 默认显示灰色，不能据此判断材质丢失。

   [用户截图待引用：0.2-06，活动对象、参数与结果同屏；参数变化保留前后画面]


### 0.3 导入、数值与参数核对

1. 每个独立案例使用新工程；需要承接前例的 C08、C11、C13，分别从 C04、C10、C12 已保存工程继续，并另存新文件。

   [用户截图待引用：0.3-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 在 **N 侧栏 → 工作流 → 导入 Gaussian / Cube** 选择指定 `.fchk/.fch`、`.log/.out`、`.cube/.cub`。Log/Out 会异步打开 **Choose Gaussian Calculation**；在 **Calculation** 中选指定计算段，核对 route、终止状态、原文行范围、能量和 Explicit geometry，再确认。计算段从 1 开始；无显式几何时不自动借用其他段构型。取消预览后应无该次新数据对象。

   [用户截图待引用：0.3-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 等待任务结束后选择新原子/场视图。在 **N 侧栏 → 数据集与数值摘要 → 查看完整来源** 或对象属性 **来源详情** 核对完整摘要、计算段、原子顺序、量名/单位；必要时点击 **刷新来源**。不是所有信息都显示在侧栏，能量和模式见对象属性。

   [用户截图待引用：0.3-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 原子源编号从 1 起，坐标为 Å，1 Blender 单位 = 1 Å。能量为 Hartree/Eh，电荷为 e，偶极为 Debye，振动频率为 cm^-1，IR 强度为 km/mol。MO 振幅为 bohr^-3/2，密度为 electron/bohr^3，ESP 为 hartree/e。外部分析按其实际输出单位核对，不能自行补单位或换算依据。

   [用户截图待引用：0.3-04，活动对象、参数与结果同屏；参数变化保留前后画面]

5. 每个参数变化先记录原值，再改为本例指定值，观察实际显示并记录新值；完成对比后恢复用于最终成图的值。阈值、色标和网格使用清单中的展示参数及实际字段单位；定量结论另需收敛检查。

   [用户截图待引用：0.3-05，活动对象、参数与结果同屏；参数变化保留前后画面]

6. `.chk` 须由持有 Gaussian 的提供者事先用 `formchk` 导出 FCHK。本教程接收已转换的样本，运行教程无需安装 Gaussian、Multiwfn、PySCF 或开发环境。

   [用户截图待引用：0.3-06，活动对象、参数与结果同屏；参数变化保留前后画面]


### 0.4 相机、渲染、保存与移动冷重开（每例执行）

1. 选中具有实际空间几何的 QC 视图；C06 的 NBO 表、C11 的 Mayer 表、C12 的 ETS-NOCV 表只保存记录，先改选其关联原子或实际曲线等可渲染视图取景，面板总览截图时再回选记录表。在 3D Viewport 转到期望观察方向。点击 **N 侧栏 → 创建视图与检查工具 → 创建取景相机**；创建并激活正交相机后，用小键盘 `0` 查看取景，必要时 `F9` 在调整面板改变 **Margin per side**。默认每侧留白 5%。将不希望出图的显示层关闭渲染图标；保持需要的修改器视口/渲染开关一致。

   [用户截图待引用：0.4-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例：选中密度线剖面创建正交相机，每侧留白5%](screenshot/00-04-camera.jpg)

2. 在 Blender 原生 **Render/Output Properties** 设置渲染器、分辨率和色彩管理，按需通过 **Add → Light** 添加灯光。使用 **Render → Render Image**（F12）；在 Render Result 中 **Image → Save As** 保存 `cases/CXX/CXX.png`。记录渲染器、分辨率、色彩管理、光源及参数；需要面板证据时另保存屏幕截图。渲染无法显示来源记录或列表时，`CXX.png` 使用面板总览截图，并另存 `CXX-render.png`。

   [用户截图待引用：0.4-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例：仅渲染密度剖面，EEVEE、1920×1080、100%、AgX；默认点光源与世界背景](screenshot/00-04-render.jpg)

   此图为 C04 的独立密度剖面示例。关闭分子、密度面、IR 谱和默认 Cube 的渲染图标，只保留剖面及其标签；未调整默认照明。渲染颜色随照明变化，曲线数值和单位须以 CSV 核对。

3. 每张图旁记录样本摘要、方法/基组、场量/单位、MO 编号/自旋、网格和等值、颜色范围；振动另记模式频率、显示振幅和播放速度。PNG 是可见结果，数值依据仍为源文件和保存的科学数组。

   [用户截图待引用：0.4-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 若本例在几何节点编辑器中通过“添加”菜单加入公共资产，先点 **文件 → 外部数据 → 打包关联库**，再保存。该步骤把关联的节点库嵌入 `.blend`；普通“打包资源”是另一项菜单，不能据此判断节点库已打包。仅使用插件自动创建的本地节点组时可直接保存。

   [用户截图待引用：0.4-04a，打包关联库菜单；移动后新进程的节点和结果]

   ![Agent原生菜单操作：文件、外部数据、打包关联库；随后MCP核对内嵌库摘要](screenshot/N18-pack-linked-libraries-menu-GUI.jpg)

   在 **N 侧栏 → 工程与诊断 → 保存自包含工程** 选择 `cases/CXX/CXX.blend`，确认同名 `CXX.qcdata/` 已生成。工程包含节点、材质、选择、动画设置和科学数组；原始外部文件、导出的 CSV 另行保留。

   [用户截图待引用：0.4-04，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例：保存自包含工程的文件对话框](screenshot/00-04-portable-save.jpg)

5. 正常关闭本次工程的 Blender，重新启动新进程，用 **File → Open** 打开 `CXX.blend`。重新选择本例对象，核对来源、参数、数值/单位与图例，重新渲染；C04 剖面还须重新导出 CSV。

   [用户截图待引用：0.4-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例：新进程冷重开密度剖面工程；4个Dataset、119个数组和1个体积文件另经MCP核对](screenshot/00-04-cold-final.jpg)

6. 将 `CXX.blend` 和 `CXX.qcdata/` 一起复制到本批 `moved/CXX/`。关闭本次进程，在另一个新进程打开移动副本，再核对与渲染。记录原进程退出、新进程身份及数组摘要核对方式；未实际关闭重开时保存检查仍为 Not Run。

   [用户截图待引用：0.4-06，活动对象、参数与结果同屏；参数变化保留前后画面]

7. 再次保存最新修改后点击 **工程与诊断 → 归档工程**，选择输出 ZIP。解压到新的目录，保持整体结构，再从解压位置打开工程核对。

   [用户截图待引用：0.4-07，活动对象、参数与结果同屏；参数变化保留前后画面]

8. 恢复操作仅在独立副本进行：缺失 VDB 且科学数组完整时，选受影响视图，点击 **重建显示缓存**；数据目录确实移动时，点击 **重新定位数据**，选择同一数据集的 `manifest.json`，其内容摘要必须匹配。保存和新进程重开复核恢复结果。科学数组缺失时记录失败，表面不能重建波函数。

   [用户截图待引用：0.4-08，活动对象、参数与结果同屏；参数变化保留前后画面]



## 1. C01–C13 输入与物理量教程

以下输入均相对本批 `inputs/`。清单的 `archive_path` 是样本包路径；`path` 是开发仓库路径，用户无需将文件放到 `tests/data/`。外部原件为 `P02/water_neutral_nbo_opt_freq.out/.log`。

所有待生成的 MO/密度/ESP 使用 **Grid spacing = 0.7 Å、Grid margin = 3 Å**，Memory budget 使用对话框默认 **512 MiB**，并记录实际网格；0.7 Å 是本批显示测试建议，不证明定量收敛。MO、等值、色域、振幅和其他展示值来自清单 `cases.gui/grid_defaults`，其状态是 **proposed；视觉 Not Run**，按以下值起步后记录实际轮廓和必要调整，不能将建议值称成图验收通过。外部 Cube 的真实网格不重采样为 0.7 Å。

| 案例 | 文件/源身份 | 本例展示设置 |
| --- | --- | --- |
| C01 | P01/o2-uhf.fchk、o2-uhf.fch；UHF/STO-3G O2 | Alpha MO9、Beta MO7（均按源编号选择）；MO阈值0.045 bohr^-3/2；自旋±0.002 electron/bohr^3 |
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

**真实输入预期：** O2 2原子，源顺序 O1/O2，坐标 (0,0,−0.6)/(0,0,+0.6) Å；中性三重态16电子，Alpha9/Beta7，源能量 **−147.633453 Eh**，每通道10个MO。选 Alpha/Source number/9 与 Beta/Source number/7。本样本 Alpha8/9、Beta6/7 各自能量相同；当前自动 HOMO 预览分别选择 Alpha8、Beta6。固定本例轨道须使用 Source number；预览占据/轨道能量以源记录为准，不另填未知值。两FCHK入口 SHA 同为 `ef562c4b210e7c380219282d7684370cca1f0e8349dffa1d4388af5831472e36`。

1. 按 0.3 导入 P01 FCHK，再逐字节别名 `.fch`；选择各自原子对象，核对原子身份/顺序、坐标、方法、基组、电荷、多重度、电子数和电子总能量，两入口记录一致。

   [用户截图待引用：C01-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：FCHK 源记录与原子身份](screenshot/C01-01-source-fchk.jpg)

   ![Agent Computer Use：逐字节 FCH 别名导入](screenshot/C01-01-fch-import.jpg)

2. 保持 FCHK 原子视图活动，点击 **工作流 → 生成量子化学场**；Quantity 选 **Molecular orbital**，分别选 **Alpha/Beta**，按清单选 **Orbital → Source number** 并填 **Orbital number (1-based)**，本例成图固定选 Alpha9/Beta7；另行选择 HOMO/LUMO 时，以预览返回的源编号为准，简并轨道不凭占据最高编号推断。记录预览 Source MO、occupation、Energy；输入清单网格 **Grid spacing (angstrom)**、**Grid margin (angstrom)** 与 **Memory budget (MiB)**，确认等待生成。

   [用户截图待引用：C01-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：Alpha 按源编号选择 MO9](screenshot/C01-02-alpha-mo9-settings.jpg)

   ![Agent Computer Use：Beta 按源编号选择 MO7](screenshot/C01-02-beta-mo7-settings.jpg)

3. 选择新 MO 场，在 **对象属性 → 科学记录与振动模式** 查量名/单位与轨道身份；在 **几何表示** 改正相/负相显隐、阈值、**Link Thresholds**、独立负阈值及实体/线框/点表示。材质属性改变两相颜色、透明度，验证相位与物理电荷不混淆。

   [用户截图待引用：C01-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：独立正负阈值](screenshot/C01-03-independent-thresholds.jpg)

   ![Agent Computer Use：两相颜色与独立透明度](screenshot/C01-03-independent-opacity.jpg)

4. 重新选择源原子对象，依次生成 **Electron density、Alpha density、Beta density、Spin density**，各次使用完全相同网格。分别选择生成场核对单位及自旋约定；数值核对总=Alpha+Beta、自旋=Alpha−Beta需源数组或数据核对证据，不能根据图形断言成立。

   [用户截图待引用：C01-04，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：总电子密度](screenshot/C01-04-total-result.jpg)

   ![Agent Computer Use：自旋密度阈值 0.002](screenshot/C01-04-spin-002.jpg)

5. 选自旋场，点击 **创建视图与检查工具 → 创建体积雾**；选新雾视图，调整颜色、Opacity Range/Scale、Display Threshold 和材质曲线，记录全透明时实际结果。选场/原子视图点击 **添加裁剪控件**，在 **空间观察** 分别开关平面与盒裁剪，原始数组不变。

   [用户截图待引用：C01-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：体积雾的颜色及透明度控件](screenshot/C01-05-fog-restored.jpg)

   ![Agent Computer Use：盒裁剪开启；数组摘要另行核对](screenshot/C01-05-box-on-x0.jpg)

   ![Agent Computer Use：Opacity Scale 为 0 时体积雾消失](screenshot/C01-05-fixed-scale0.jpg)

   ![Agent Computer Use：Opacity Scale 恢复 40 后体积雾即时出现](screenshot/C01-05-fixed-scale40-restored.jpg)

   ![Agent Computer Use：不透明度渐变全黑时体积雾消失](screenshot/C01-05-fixed-ramp-black.jpg)

   ![Agent Computer Use：恢复黑白渐变后体积雾即时出现](screenshot/C01-05-fixed-ramp-white.jpg)

   ![Agent Computer Use：复制层为 0，原层保持 40 且仍可见](screenshot/C01-05-fixed-copy-independent.jpg)

   ![Agent Computer Use：修复候选新建雾层及其材质](screenshot/C01-05-fixed-new-material.jpg)

6. 对应 N01/N02/N04/N05/N09/N10；按 0.4 完成渲染保存。固定证据：`C01.png`、`C01-mo.png`、`C01-total.png`、`C01-alpha.png`、`C01-beta.png`、`C01-spin.png`、`C01.blend` 和配套目录。逐个改参数时另留前后截图。

   [用户截图待引用：C01-06，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：轨道渲染及图像另存](screenshot/C01-06-mo-saved.jpg)

   ![Agent Computer Use：总电子密度原生渲染及保存](screenshot/C01-06-total-saved.jpg)

   ![Agent Computer Use：Alpha 密度原生渲染及保存](screenshot/C01-06-alpha-saved.jpg)

   ![Agent Computer Use：Beta 密度原生渲染及保存](screenshot/C01-06-beta-saved.jpg)

   ![Agent Computer Use：自旋密度原生渲染及保存](screenshot/C01-06-spin-saved.jpg)

   ![Agent Computer Use：密度展示另存自包含工程](screenshot/C01-06-density-portable-saved.jpg)

   ![Agent Computer Use：自包含工程保存完成](screenshot/C01-06-portable-saved.jpg)

   ![Agent Computer Use：新进程通过文件菜单冷重开](screenshot/C01-06-cold-restored.jpg)

   ![Agent Computer Use：冷重开后重新渲染](screenshot/C01-06-cold-render.jpg)

   ![Agent Computer Use：归档工程文件对话框](screenshot/C01-06-archive-dialog.jpg)

   ![Agent Computer Use：工程归档完成](screenshot/C01-06-archive-saved.jpg)

   ![Agent Computer Use：中文移动路径的文件打开对话框](screenshot/C01-06-moved-open-dialog.jpg)

   ![Agent Computer Use：中文移动副本冷重开](screenshot/C01-06-moved-restored.jpg)

   ![Agent Computer Use：移动副本重新渲染](screenshot/C01-06-moved-render.jpg)

   ![Agent Computer Use：归档解包后的新进程冷重开](screenshot/C01-06-unpacked-restored.jpg)

   ![Agent Computer Use：解包工程重新渲染](screenshot/C01-06-unpacked-render.jpg)

   ![Agent Computer Use：修复复验另存自包含工程](screenshot/C01-06-fog-fixed-portable.jpg)

   ![Agent Computer Use：新建雾层原生 F12 渲染](screenshot/C01-06-fog-fixed-render.jpg)

   ![Agent Computer Use：修复工程原路径冷重开（92d498c候选）](screenshot/C01-06-fog-fixed-cold-restored.jpg)

   ![Agent Computer Use：修复工程原路径冷重开后渲染（92d498c候选）](screenshot/C01-06-fog-fixed-cold-render.jpg)

   ![Agent Computer Use：修复工程中文移动副本冷重开（92d498c候选）](screenshot/C01-06-fog-fixed-moved-restored.jpg)

   ![Agent Computer Use：修复工程中文移动副本重新渲染（92d498c候选）](screenshot/C01-06-fog-fixed-moved-render.jpg)

   ![Agent Computer Use：修复工程归档解包副本冷重开（92d498c候选）](screenshot/C01-06-fog-fixed-unpacked-restored.jpg)

   ![Agent Computer Use：修复工程归档解包副本重新渲染（92d498c候选）](screenshot/C01-06-fog-fixed-unpacked-render.jpg)



   密度检查点复核：保存于步骤6的 `C01-density.blend + .qcdata` 已在2eddb6a候选的新原生后台进程冷重开，175配套文件、9 Dataset/221数组、17对象引用及7体积源一致；四密度重新渲染并检查，总密度=Alpha+Beta、自旋密度=Alpha−Beta关系通过。详见[点击补验索引](../acceptance/tutorial-cu-validation.json)的 `C01_density_checkpoint_cold`，原候选/保存身份与本批冷读身份分别记录。此检查点的中文移动/解包及最终统一候选资格另行维护；已有雾工程三路径证据保持原批次。

### C02 Log/Out 能量、振动与优化

**真实输入预期：** Job2 是中性单重态水，3原子 O/H/H，RHF/STO-3G，10电子；目标电子能量 **−74.9659011806 Eh**（与Job1最终优化步一致）。模式1/2/3频率 **2169.7613/4141.3837/4392.5759 cm^-1**，IR **7.2483/44.2724/29.9428 km/mol**；先选模式3。Job1有4优化步，能量依次 **−74.9643287914、−74.9649723283、−74.9659003010、−74.9659011806 Eh**。两扩展名都要完成导入。导入回归的下一文件固定 **P03/water-dimer.fchk**，预期6原子及其SHA；无P02 FCHK。

1. 按 0.3 导入 P02 Log/Out，选清单含频率的计算段。选择导入的**原子对象**，展开 **对象属性 → 科学记录与振动模式**，选择能量记录，核对 Hartree 值、方法、kind/role 和原文位置。参考 SCF、目标方法、ZPE/热校正分别记录，不能把最后一条 SCF 当成唯一目标值。

   [用户截图待引用：C02-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例（候选92d498c）：C02-01-log-alias-job2-preview](screenshot/C02-01-log-alias-job2-preview.jpg)

   ![Agent操作示例（候选92d498c）：C02-01-log-source](screenshot/C02-01-log-source.jpg)

   ![Agent操作示例（候选92d498c）：C02-01-calculation-source](screenshot/C02-01-calculation-source.jpg)

   ![Agent操作示例（候选92d498c）：C02-01-zpe-record](screenshot/C02-01-zpe-record.jpg)

   ![Agent操作示例：选择真实 Log 文件](screenshot/C02-01-log-file.jpg)

   ![Agent操作示例：选择 Job 2 频率计算段](screenshot/C02-01-job2.jpg)

   ![Agent操作示例：能量记录与振动模式](screenshot/C02-01-energy-modes.jpg)

2. 同一面板模式列表选清单指定模式，核对源编号、频率、IR 强度与 IR 棒图高亮。在同级 **高级参数** 勾选 **Animate**，填写指定 **Amplitude (angstrom)** 和 **Cycles per second**，到 Timeline 点击播放，观察实际帧推进，再暂停；改变 Phase 和模式重复。在 **几何表示 → Show Displacement Vectors** 开位移箭头。平衡源坐标不变；播放速度不是物理振动频率。

   [用户截图待引用：C02-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例（候选92d498c）：C02-02-mode3-playback](screenshot/C02-02-mode3-playback.jpg)

   ![Agent操作示例（候选92d498c）：C02-02-mode3-phase-vectors](screenshot/C02-02-mode3-phase-vectors.jpg)

   ![Agent操作示例（候选92d498c）：C02-02-mode1-playback](screenshot/C02-02-mode1-playback.jpg)

   ![Agent操作示例（候选92d498c）：C02-02-mode2-playback](screenshot/C02-02-mode2-playback.jpg)

   ![Agent操作示例（候选92d498c）：C02-02-ir-mode1](screenshot/C02-02-ir-mode1.jpg)

   ![Agent操作示例（候选92d498c）：C02-02-ir-mode2-full](screenshot/C02-02-ir-mode2-full.jpg)

   ![Agent操作示例（候选92d498c）：C02-02-ir-mode3](screenshot/C02-02-ir-mode3.jpg)

   ![Agent操作示例：模式3与振动显示参数](screenshot/C02-02-mode3-parameters.jpg)

   ![Agent操作示例：模式1播放画面](screenshot/C02-02-mode1-playing.jpg)

   ![Agent操作示例：模式2播放画面](screenshot/C02-02-mode2-playing.jpg)

3. 再点 **导入 Gaussian / Cube** 打开新的文件对话框，选同一 Log 的优化计算段。选其原子对象，点 **创建视图与检查工具 → 创建优化轨迹视图**；必须选中新轨迹对象，再展开 **对象属性 → Optimization Trajectory**，逐次点击 **Previous、Next、Choose Step**。核对步号、构型、能量、终止状态、收敛值/阈值及原文行范围。缺失/歧义能量按界面状态记录；优化步不是物理时间。

   [用户截图待引用：C02-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例（候选92d498c）：C02-03-job1-preview](screenshot/C02-03-job1-preview.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-optimization-step1](screenshot/C02-04-optimization-step1.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-optimization-step2](screenshot/C02-04-optimization-step2.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-optimization-step3](screenshot/C02-04-optimization-step3.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-optimization-step4](screenshot/C02-04-optimization-step4.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-choose-step-dialog](screenshot/C02-04-choose-step-dialog.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-ballstick-converged](screenshot/C02-04-ballstick-converged.jpg)

4. 在 Display Layers 复制优化轨迹，分别切到不同步，核对互不影响；原视图仍保留其已核实性质，轨迹不借用最终电荷、偶极或模式。C05 的标注也在 P02/P04 可操作的步序上核对随步更新。

   [用户截图待引用：C02-04，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例（候选92d498c）：C02-04-copy-step2](screenshot/C02-04-copy-step2.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-original-still-step1](screenshot/C02-04-original-still-step1.jpg)

5. **导入状态回归：** 本工程再次导入 Log，明确选 **Job 2** 并完成；随后点击 **导入 Gaussian / Cube** 打开**新文件对话框**导入 **P03/water-dimer.fchk**。核对新的计算段参数从 1 开始，导入成功、来源 SHA 为该 FCHK，未继承 Log 的摘要/job；不得以脚本执行 Operator 代替此项真实点击。

   [用户截图待引用：C02-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例（候选92d498c）：C02-05-new-dialog-reset](screenshot/C02-05-new-dialog-reset.jpg)

   ![Agent操作示例（候选92d498c）：C02-05-fchk-file-selected](screenshot/C02-05-fchk-file-selected.jpg)

   ![Agent操作示例（候选92d498c）：C02-05-fchk-six-atoms](screenshot/C02-05-fchk-six-atoms.jpg)

   ![Agent操作示例：Log Job 2 后打开新的 FCHK 文件对话框](screenshot/C02-05-fchk-new-dialog.jpg)

   ![Agent操作示例：新 FCHK 导入结果](screenshot/C02-05-fchk-success.jpg)

6. 为清楚显示 IR 文字，可在 **世界属性 → 表面 → 颜色** 设为白色（RGBA 1/1/1/1，Strength 1）；在 Outliner 选择 **QC IR labels**，到 **材质属性** 新建材质，设基础色为黑色（RGBA 0/0/0/1）。这是展示设置，不改变科学数组。将原子视图与 IR 棒图一起选中，创建取景相机；若独立渲染窗口无法操作，可在主窗口切换 **图像编辑器 → Render Result → 图像 → 另存为** 导出 F12 结果。对应 N12/N15/N16，按 0.4 保存。证据：`C02.png`、`C02-energy.png`、`C02-vibration.png`、`C02-ir.png`、`C02-optimization.png`、`C02-reimport.png` 及工程。

   [用户截图待引用：C02-06，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-original-restored](screenshot/C02-06-cold-original-restored.jpg)

   ![Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-original-render](screenshot/C02-06-cold-original-render.jpg)

   ![Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-moved-restored](screenshot/C02-06-cold-moved-restored.jpg)

   ![Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-moved-render](screenshot/C02-06-cold-moved-render.jpg)

   ![Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-unpacked-restored](screenshot/C02-06-cold-unpacked-restored.jpg)

   ![Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-unpacked-render](screenshot/C02-06-cold-unpacked-render.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-camera](screenshot/C02-06-camera.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-white-background](screenshot/C02-06-white-background.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-black-label-material](screenshot/C02-06-black-label-material.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-render](screenshot/C02-06-render.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-png-save-dialog](screenshot/C02-06-png-save-dialog.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-portable-saved](screenshot/C02-06-portable-saved.jpg)

   ![Agent操作示例（候选92d498c）：C02-06-archive-saved](screenshot/C02-06-archive-saved.jpg)

   ![Agent操作示例（候选92d498c）：C02-04-portable-saved](screenshot/C02-04-portable-saved.jpg)



### C03 Cube/cub 物理量、网格与双符号

**真实输入预期：** `P03/igmh/sl2r.cub` 与 `P03/color.cube` 字节一致，SHA为 `18a33c308c868c9f7747128f1a23c04fc69df37fd5b9681aa5dd35ef20997958`；6原子，**91×38×156**，origin **(−1.2877770840,−0.5291772105,−0.5291772105) Å**，三轴步长 **0.02874808114 Å**。值域 **−194.599..+0.295371 electron/bohr^3**，量 `sign_lambda2_rho`，倍率 **1**。声明时选 **Other externally computed scalar field**，Physical quantity填 `sign_lambda2_rho`，Unit填 `electron/bohr^3`，该场数值不做额外倍率换算。

1. 分别导入 P03 Cube 和逐字节 `.cub` 别名，选各自场对象核对原子、网格和数值数组；普通 Cube 初始物理量可能为 **unknown_scalar / unknown**。

   [用户截图待引用：C03-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent 实际点击：C03-01-cube-selected](screenshot/C03-01-cube-selected.jpg)

   ![Agent 实际点击：C03-01-cube-imported](screenshot/C03-01-cube-imported.jpg)

   ![Agent 实际点击：C03-01-cub-selected](screenshot/C03-01-cub-selected.jpg)

   ![Agent 实际点击：C03-01-cub-imported](screenshot/C03-01-cub-imported.jpg)

2. 选待声明场，点 **对象属性主面板 → 声明 Cube 物理量与单位**，只选择样本中数值实际已有的物理量/单位；声明不会换算数值。外部标量选择 **Other externally computed scalar field**，填真实量名与单位；来源无法确定时保留 unknown 并记录原始定义。

   [用户截图待引用：C03-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent 实际点击：C03-02-cub-declaration-parameters](screenshot/C03-02-cub-declaration-parameters.jpg)

   ![Agent 实际点击：C03-02-cub-declared](screenshot/C03-02-cub-declared.jpg)

   ![Agent MCP声明；Computer Use仅观察结果：C03-02-cube-declared-MCP](screenshot/C03-02-cube-declared-MCP.jpg)

3. 选已声明场，在 **对象属性 → QCBlender · 对象与量子化学 → 几何表示** 将 **正值阈值** 设为 **0.03 electron/bohr^3**；取消 **Link Thresholds** 后，将出现的 **负值阈值** 设为 **0.01**。分别关闭/恢复 **显示正值** 与 **显示负值**，核对蓝色正值与红色负值单独显示；在 **样式** 依次选择 **实面、线框、点**，最后恢复实面。到 **材质属性 → QCBlender · 节点材质** 将 **Positive Opacity / Negative Opacity** 分别设为 **0.6 / 0.3**，通过 3D Viewport **材质预览** 观察，不能用实面着色判断透明度。核对别名入口一致。

   独立几何场着色：随后导入 **P03/igmh/dg_inter.cub**，声明 `delta_g_inter / electron/bohr^4`，正值阈值设 **0.005**，仅显示正值。保持新几何场活动，在 **对象属性 → QCBlender · 对象与量子化学 → 颜色映射 → 选择／替换着色场** 选择原 `color.cube` 场，确认其源 SHA、`sign_lambda2_rho / electron/bohr^3`，Color minimum/maximum 填 **−0.05 / 0.05**。位置由几何场决定，颜色来自第二场；两个输入须同为 **91×38×156**，origin/steps 及原子身份匹配。在 **N 侧栏 → Display Layers** 隐藏独立着色表面的视口和渲染（眼睛/相机），保留内部体场；只显示一份原子。再次 **选择／替换着色场** 选 `sl2r.cub` 别名，范围和图例位置应保留。本例 Geometry SHA 为 `daf5a7e79c7dcc67b244f3dc1d2d314795c9f318c931e4f25d36e72ea168a28e`；几何原值范围 **1.01735e-10..0.0185476**。

   [用户截图待引用：C03-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent 实际点击：C03-03-unlinked-003-001](screenshot/C03-03-unlinked-003-001.jpg)

   ![Agent 实际点击：C03-03-both-phases](screenshot/C03-03-both-phases.jpg)

   ![Agent 实际点击：C03-03-negative-only](screenshot/C03-03-negative-only.jpg)

   ![Agent 实际点击：C03-03-positive-only](screenshot/C03-03-positive-only.jpg)

   ![Agent 实际点击：C03-03-wire](screenshot/C03-03-wire.jpg)

   ![Agent 实际点击：C03-03-points](screenshot/C03-03-points.jpg)

   ![Agent 实际点击：C03-03-opacity-06-03](screenshot/C03-03-opacity-06-03.jpg)

   ![Agent示例：MCP复验别名阈值/透明度；Computer Use观察](screenshot/C03-03-alias-controls-MCP.jpg)

   ![Agent示例：MCP导入及声明真实几何场，GUI隐藏重复层](screenshot/C03-03-geometry-unmapped-MCP.jpg)

   ![Agent示例：GUI活动几何场与颜色映射入口](screenshot/C03-03-mapping-entry.jpg)

   ![Agent示例：GUI独立着色场来源与范围](screenshot/C03-03-mapping-dialog.jpg)

   ![Agent示例：GUI关联着色结果；MCP取样核对](screenshot/C03-03-mapped-result.jpg)

   ![Agent示例：GUI替换为cub别名](screenshot/C03-03-replace-dialog.jpg)

   ![Agent示例：GUI替换结果，范围和取样属性保留](screenshot/C03-03-replaced-result.jpg)

4. NCIPLOT 的倍率、RDG 过滤哨兵若出现在所选样本中按真实记录解释；普通 RDG 不能称 IGMH/IRI。没有该类样本时不套用旧 NCIPLOT 数值。

   [用户截图待引用：C03-04，活动对象、参数与结果同屏；参数变化保留前后画面]

5. 对应 N04–N07，按 0.4 保存 `C03.png/.blend/.qcdata/`。

   [用户截图待引用：C03-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent示例：GUI双符号阶段取景；Computer Use观察截图](screenshot/C03-05-phase-camera.jpg)

   ![Agent示例：MCP双符号阶段渲染；Computer Use观察截图](screenshot/C03-05-phase-render-MCP.jpg)

   ![Agent示例：MCP双符号阶段保存自包含工程；Computer Use观察截图](screenshot/C03-05-phase-portable-MCP.jpg)

   ![Agent示例：MCP阶段工程冷重开数据核对；Computer Use观察截图](screenshot/C03-05-phase-cold-MCP.jpg)

   ![Agent示例：MCP阶段工程冷重开渲染，像素一致；Computer Use观察截图](screenshot/C03-05-phase-cold-render-MCP.jpg)

   ![Agent示例：MCP保存完整C03工程，3 Dataset/18数组/9引用；Computer Use观察截图](screenshot/C03-05-portable-mapping-MCP.jpg)

   ![Agent示例：MCP完整映射工程渲染；Computer Use观察截图](screenshot/C03-05-mapped-render-MCP.jpg)

   ![Agent示例：新可见进程原路径MCP冷重开及渲染；Computer Use观察截图](screenshot/C03-05-original-cold-render-MCP.jpg)

   ![Agent示例：新可见进程中文移动路径MCP冷重开及渲染；Computer Use观察截图](screenshot/C03-05-moved-cold-render-MCP.jpg)

   ![Agent示例：新可见进程归档解包MCP冷重开及渲染；Computer Use观察截图](screenshot/C03-05-unpacked-cold-render-MCP.jpg)



### C04 ESP、电荷、偶极、切片、探针与剖面

**真实输入预期：** 水二聚体6原子 **[O,H,H,O,H,H]**，中性单重态20电子，RHF/6-31G(d)，能量 **−152.013820 Eh**。源SHA为 `02ffc555ac7bda6e263e8461481914db3a2576582f71b6b9ea97fa05df610d6a`。Mulliken原子1/2/4为 **−0.928340742/+0.461442520/−0.920221916 e**；偶极源向量为约 **(0,0,1.67243888) e·bohr**，界面以Debye展示，核对保留的单位换算记录。切片中心 **(0,0,1.45) Å**；游标剖面起点 **(0,−2,1.45)**、终点 **(0,+2,1.45) Å**，Geometry、101点、距离0..4 Å。源关联使用逐字节别名 **P03/water-dimer.fch**，不能用P02单水Log与水二聚体关联。

1. 导入 P03 FCHK，选原子对象分别 **N 侧栏 → QCBlender → 工作流 → 生成量子化学场**，Quantity 选择 **Electron density / Electrostatic potential**，两次均设置 **Grid spacing=0.7 Å、Grid margin=3 Å、Memory budget=512 MiB**；这是展示网格，定量使用须另做收敛检查。核对密度单位 electron/bohr^3、ESP hartree/e。ESP 核附近无效点不算物理零。

   [用户截图待引用：C04-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent点击：密度/ESP生成参数与密度结果；网格0.7 Å](screenshot/C04-01-density-generation-parameters.jpg)

   ![Agent点击：密度/ESP生成参数与密度结果；网格0.7 Å](screenshot/C04-01-density-generated.jpg)

   ![Agent点击：密度/ESP生成参数与密度结果；网格0.7 Å](screenshot/C04-01-ESP-generation-parameters.jpg)

   ![Agent操作示例：密度生成示例；ESP 须另行操作](screenshot/C04-01-density-dialog.jpg)

2. 选**密度表面**，打开 **对象属性 → 颜色映射 → 选择／替换着色场**，选择 ESP；核对候选源 SHA、job、量名/单位再确认。密度决定几何，ESP 决定颜色。隐藏独立 ESP 表面的显示和渲染，不删除其内部体场。

   [用户截图待引用：C04-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![MCP复用映射操作：密度0.004表面按ESP着色，21点数值核对](screenshot/C04-02-density-ESP-mapped-MCP.jpg)

3. 填 **Color Minimum=−0.05、Color Center=0、Color Maximum=+0.05**，须严格递增；在 **图例排版** 开 **显示图例**（Show Legend），改 长宽/字号/小数/方向/旋转/位置。点击 **零中心对称** 输入 **R=0.05**，再 **读取有效范围** 对照一次读取结果；记录并恢复成图色域。示例排版填长度 **2.6**、宽度 **0.25**、字号 **0.2**（均为本地布局单位），小数位数 **3**，开启竖向排列，旋转 **(0,0,0.3)**（rad），位置 **(3.5,0,0)**。在 **材质属性 → QCBlender · 节点材质** 修改 Color map 中间停靠点 **0.5→0.4**，将 **Reverse (0 or 1)** 从 **0→1**，确认表面和图例颜色方向同时反转；成图前恢复中点 **0.5** 与 Reverse **0**。原生撤销用 **编辑 → 撤销**，重做用 **编辑 → 重做**。范围外用端点颜色，无效采样为洋红；本批1800点均有效，无效域颜色仍须另行验收。

   [用户截图待引用：C04-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent点击：零中心对称与读取有效范围；图例排版和色带操作见下列补验图](screenshot/C04-03-zero-centered-dialog.jpg)

   ![Agent点击：零中心对称与读取有效范围；图例排版和色带操作见下列补验图](screenshot/C04-03-valid-range.jpg)

   ![Agent点击：色域对称、读取范围和图例显隐；排版与色带见下列补验图](screenshot/C04-03-legend-visible-restored-range.jpg)

   ![Agent点击：图例默认排版](screenshot/C04-03-legend-default.jpg)

   ![Agent点击：长度2.6、宽度0.25、字号0.2、小数3](screenshot/C04-03-legend-dimensions.jpg)

   ![Agent点击：切换竖向排列](screenshot/C04-03-legend-vertical.jpg)

   ![Agent点击：图例Z旋转0.3 rad](screenshot/C04-03-legend-rotated.jpg)

   ![Agent点击：图例X位置3.5](screenshot/C04-03-legend-positioned.jpg)

   ![Agent点击：材质属性中的Color map与Reverse入口](screenshot/C04-03-material-before.jpg)

   ![Agent点击：Reverse=1，表面与图例方向同时反转](screenshot/C04-03-material-reversed.jpg)

   ![Agent点击：色带中间停靠点改为0.4](screenshot/C04-03-ramp-middle-changed.jpg)

   ![Agent点击：编辑菜单重做Reverse修改](screenshot/C04-03-material-menu-redo.jpg)

   ![Agent点击：恢复中点0.5与Reverse=0](screenshot/C04-03-material-restored.jpg)

4. 旧多选映射使用新的未映射层独立复核：先选步骤2的密度表面，点 **N 侧栏 → 创建视图与检查工具 → 创建当前版本视图**，保留原层，新标准密度层尚未绑定色场。临时开启 ESP 表面的视口可见性，取消其他选择，在 Outliner 先选 ESP 表面，再 Shift 选新密度表面使其活动，确认恰好选中两个对象；在 **3D Viewport → Object（物体）→ QCBlender → Map Selected Field to Active Surface** 打开映射；也可将鼠标放在3D视口后 F3 搜索同名操作。填 **Color minimum=−0.05、Color maximum=+0.05**，确认后核对与步骤2相同的来源。已有着色的视图会拒绝重复添加，应使用选择／替换着色场。再用 **选择／替换着色场** 替换一次，范围和图例位置保留；恢复独立 ESP 表面隐藏。

   [用户截图待引用：C04-04，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent观察：Object顶部QCBlender菜单中的旧映射入口](screenshot/C04-04-top-object-menu-entry.jpg)

   ![Agent点击新建视图，MCP核对无着色绑定并设置两对象选择](screenshot/C04-04-new-view-before-F3.jpg)

   ![Agent点击：默认配置F3检索旧映射操作](screenshot/C04-04-F3-fresh-map-entry.jpg)

   ![Agent点击：新未映射视图映射参数−0.05至+0.05](screenshot/C04-04-F3-fresh-map-dialog.jpg)

5. 重新选原始原子对象，在 **科学记录与振动模式 → 设置原子电荷着色** 选真实存在的布居方法，核对指定原子电荷 e；已绑定网格着色的原子层需换独立层。点 **创建视图与检查工具 → 创建偶极矢量**，核对源三分量/Debye，改变 **Angstrom per Debye** 只改显示长度。

   [用户截图待引用：C04-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent GUI选择Mulliken电荷；此图为b709096批次](screenshot/C04-05-charge-mulliken-dialog.jpg)

   ![Agent GUI将Charge Maximum设为0.5 e；保留原科学电荷](screenshot/C04-05-charge-range-half.jpg)

   ![Agent GUI创建偶极；默认0.5 Å/Debye](screenshot/C04-05-dipole-created-default.jpg)

   ![Agent GUI将偶极设为1.5 Å/Debye；方向及源向量不变](screenshot/C04-05-dipole-scale-1_5.jpg)

6. 选 ESP 场，点 **创建切片**；选新切片，在 **空间观察** 改 Center/Rotation/Width/Height，在 **几何表示** 改 **显示采样数/轴**（Resolution）。点 **按源网格或三个原子定平面**，选 **Grid ij / Grid jk / Grid ki / Three source atoms**，Associated atom view选水二聚体原子对象，First/Second/Third source atom分别填 **2/1/4**（三点非共线）；使用 3D Viewport 工具栏 **QC Slice Gizmo** 平移/旋转，核对平面记录。在对象属性 **切片等值线 → 开启等值线**，本例ESP切片选 **几何场**；先留 **阈值列表（空白：自动 9 条）** 为空，再填 **−0.02,0,0.02**（hartree/e）并点 **更新等值线**，等待异步曲线/标签更新，变更后无效单元不连线。

   [用户截图待引用：C04-06，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent点击：创建新的ESP切片；候选e26d22a](screenshot/C04-06-fixed-new-slice-dialog.jpg)

   ![Agent点击：Grid ij，101×101采样](screenshot/C04-06-fixed-grid-ij.jpg)

   ![Agent点击：Grid jk；混合绝对与相对绑定路径已通过复验](screenshot/C04-06-fixed-grid-jk.jpg)

   ![Agent点击：Grid ki](screenshot/C04-06-fixed-grid-ki.jpg)

   ![Agent点击：首次三原子平面1/2/3；教程2/1/4另经MCP复验](screenshot/C04-06-fixed-three-atoms-dialog.jpg)

   ![Agent点击：三原子平面；5072个域外采样点以洋红显示](screenshot/C04-06-fixed-three-atoms.jpg)

   ![Agent点击：自由平面Center/Rotation/Width/Height；6×6 Å](screenshot/C04-06-fixed-free-parameters.jpg)

   ![Agent拖动：QC Slice Gizmo平移](screenshot/C04-06-fixed-gizmo-move.jpg)

   ![Agent拖动：QC Slice Gizmo旋转](screenshot/C04-06-fixed-gizmo-rotation.jpg)

   ![Agent拖动：QC Slice Gizmo改变宽度](screenshot/C04-06-fixed-gizmo-width.jpg)

   ![Agent点击显式阈值与标签；MCP取景后观察，−0.02/0/0.02 hartree/e](screenshot/C04-06-fixed-explicit-contours-framed.jpg)

7. 选 ESP 场，在 **3D Viewport → N → View → 3D Cursor** 输入清单坐标，点击 **创建视图与检查工具 → 读取游标处场值**。分别在 **(0,0,1.45)**、核邻近 **(0,0,0)** 和域外 **(20,20,20) Å** 读取。核附近是否无效由实际网格掩码决定，0.7 Å 网格未必命中核的排除区；若核邻近仍有效，如实记录值，并将“无效域读数”保留 Not Run，另由同批数据核对验证真实无效格点，不能凭坐标宣称无效。无效/域外不能记物理0。点 **点击探针 · 几何场** 后在表面点击预览，按 **Enter** 保存取点结果；按 **Escape** 恢复进入探针前的状态。绑定色场的密度表面再用 **点击探针 · 绑定色场**，同样点击后按 Enter 保存，记录采样位置/单位和实际结果。

   [用户截图待引用：C04-07，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent点击：读取游标ESP，0.0085721002 hartree/e](screenshot/C04-07-esp-cursor-valid.jpg)

   ![Agent点击：ESP切片几何场取点预览，Enter保存](screenshot/C04-07-esp-geometry-probe-preview.jpg)

   ![Agent点击：第二取点预览后Escape恢复原记录](screenshot/C04-07-esp-geometry-probe-Escape-preview.jpg)

   ![Agent点击：密度表面绑定色场取点，实际采样ESP](screenshot/C04-07-bound-color-probe-preview.jpg)

   ![Agent点击Enter：保存0.072094069 hartree/e绑定色场读数](screenshot/C04-07-bound-color-probe-saved.jpg)

   ![Agent操作示例：独立密度几何场取点预览，单位 electron/bohr^3；该示例不是 ESP 取点](screenshot/C04-07-click-probe-preview.jpg)

8. 选指定场或切片，输入游标起点，点击 **记录剖面起点**；保持**同一个活动视图**，输入终点，点 **创建线剖面**，先选 **几何数据（Geometry）**、填 **采样（Samples）=101**；绑定色场视图再明确选 **颜色（Color）** 复核。选新剖面，改 **剖面坐标轴与排版 → 应用排版**，点 **导出剖面 CSV** 保存 `C04-profile.csv`；核对距离 Å、字段单位、端点、valid 列及无效值空白。本例图幅宽度从 **4→6** 后点击 **应用排版**；图幅单位与距离单位分别记录，CSV距离仍为 **0–4 Å**。剖面是采样快照，移动排版不改 CSV。

   [用户截图待引用：C04-08，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent点击：Sample field选颜色，采样101点；游标坐标由MCP设置](screenshot/C04-08-color-profile-dialog.jpg)

   ![Agent点击图幅宽度6与应用排版；MCP正面取景，CSV仍覆盖0–4 Å](screenshot/C04-08-color-profile-layout.jpg)

   ![Agent操作示例：独立密度剖面示例的游标起点，场单位 electron/bohr^3](screenshot/C04-08-cursor-start.jpg)

   ![Agent操作示例：独立密度剖面示例的创建参数，场单位 electron/bohr^3](screenshot/C04-08-profile-dialog.jpg)

   ![Agent操作示例：密度剖面结果，距离0–4 Å；隐藏其他图表文字以避免重叠](screenshot/C04-08-profile-final.jpg)

   ![Agent操作示例：导出剖面CSV，101个有效采样点；场单位electron/bohr^3](screenshot/C04-08-profile-csv.jpg)

   上述密度示例沿用步骤1的网格间距0.7 Å、Margin 3 Å，从(0, −2, 1.45)到(0, 2, 1.45)，Samples=101。步骤8的 ESP 检查仍需改选 ESP 场单独执行，两种场的单位分别记录。

9. 源关联复核：导入 **P03/water-dimer.fch** 别名。在 **3D Viewport / Outliner** 先选新导入的原子对象，再按 `Shift` 选原有 FCHK 原子对象，使原对象成为活动参考。转到 **Properties → Object → QCBlender · 对象与量子化学 → 关联选中数据源**。本例逐字节别名保持相同原子顺序和构型，**Align rigid rotation/translation** 不勾选，**Maximum atom deviation (angstrom)** 保持 **0.001 Å**；双击数值框可查看完整精度，未编辑时可能显示为 `0.00`。点击 **确定**，预期提示 **Atom order and geometry matched; each source retains its own properties**，两源 Dataset、理论层次和能量记录分别保留。需要刚体配准的其他输入另行核对；线性/单中心几何不自动唯一配准。

   [用户截图待引用：C04-09，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![MCP设置新源与活动参考；GUI关联按钮可用](screenshot/C04-09-source-selection.jpg)

   ![Agent首次GUI关联：刚体配准关闭，完整容差0.001 Å](screenshot/C04-09-association-tolerance.jpg)

   ![Agent GUI确认成功；MCP核对六原子映射和源数组不变](screenshot/C04-09-association-success.jpg)

10. 对应 N06–N11/N17，按 0.4 保存；冷重开与移动后再次导出 CSV，核对保存数组/摘要。证据：`C04.png`、`C04-esp.png`、`C04-charge.png`、`C04-dipole.png`、`C04-slice.png`、`C04-profile.png`、CSV 和工程。

   [用户截图待引用：C04-10，活动对象、参数与结果同屏；参数变化保留前后画面]

   本例成图：密度/ESP表面与分子从正面观察；图例的 **Legend Rotation** 设为 **X=90°、Y=0°、Z≈17.19°（0.3 rad）**，使刻度朝向相机。自由切片从顶面观察，更新当前平面等值线并等待完成后取景。剖面从正面观察，创建相机后在 **F9 → Margin per side** 设为 **0.20**，切片可用 **0.15**，其余 **0.05**。检查完整单位和刻度处于相机画幅内，再渲染。独立示例工程保存各成图相机；这些排版参数不修改科学数组。

   ![MCP导出并另存工程：7 Dataset、222数组、117配套文件；三路径冷重开报告见验证索引](screenshot/C04-10-association-exports-saved-MCP.jpg)

   ![MCP在新可见进程核对中文移动工程、CSV和渲染；Computer Use观察截图](screenshot/C04-10-completion-cold-moved-MCP.jpg)

   ![MCP在新可见进程核对ZIP解包工程、CSV和渲染；Computer Use观察截图](screenshot/C04-10-completion-cold-unpacked-MCP.jpg)

   ![MCP另存检查点：6 Dataset、172数组；此图尚非最终C04成图](screenshot/C04-10-slice-fixed-checkpoint-saved-MCP.jpg)

   ![新进程MCP冷重开与CSV复导出；单独显示ESP剖面，完整C04成图待验收](screenshot/C04-10-slice-fixed-cold-MCP.jpg)

   ![MCP保存阶段工程；完整C04渲染与冷重开待补验](screenshot/C04-10-mapping-checkpoint-saved-MCP.jpg)

   ![MCP保存图例阶段工程；154数组保持原摘要，完整C04及本工程冷重开待补验](screenshot/C04-10-legend-checkpoint-saved.jpg)

   ![MCP保存F3映射阶段工程；3 Dataset和154数组核对，完整C04与冷重开待补验](screenshot/C04-10-F3-checkpoint-saved-MCP.jpg)



### C05 氢显隐、局部选择、标注与显示层

**真实输入预期：** 同C04水二聚体，氢源编号 **2/3/5/6**，保留 **2**；氧集合 **1,4**。编号标注 **1**；距离 **1,4 = 2.9 Å**；角 **2,1,3 = 112.7698904°**；二面角 **2,1,4,5 = 0.000°**（项目B→C约定）。这些标注预期由已核对FCHK源坐标经项目measure实算，显示可取三位小数。优化/IRC随步更新另用C02/C10，不影响本例静态样本可运行。

本例静态氢、局部选择和全部标注统一使用 **P03水二聚体**；P01 O2不含氢。随步更新另在C02/P02和C10/P04复做。

1. 导入 **P03/water-dimer.fchk**，选原子对象，在 **对象属性 → 局部选择与标注** 依次点击 **隐藏氢 → 保留指定氢 → 显示全部氢**，按清单填一个真实氢的源编号，核对只保留指定氢及全恢复。每步记录前后；撤销/重做核对状态。

   [用户截图待引用：C05-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent操作示例：水二聚体全部6个源原子](screenshot/C05-01-all-hydrogens.jpg)

   ![Agent操作示例：隐藏氢后保留氧，源编号1与4](screenshot/C05-01-hidden-hydrogens.jpg)

   ![Agent操作示例：保留指定氢，源编号2；氧仍保留](screenshot/C05-01-keep-hydrogen-2.jpg)

   ![Agent操作示例：撤销恢复6个原子，再用Edit菜单的Redo重做隐藏氢；返回氧1与4](screenshot/C05-01-redo-menu.jpg)

2. 点 **设置局部选择**，在 **Source atom numbers (1-based)** 先填 **1,4**、**Mode=替换（Replace）**；再填 **2**、**并集（Union）**（得1,2,4），填 **1,2**、**交集（Intersect）**（得1,2），填 **2**、**差值（Difference）**（得1），最后选 **反转（Invert）**（得2–6）。再次点 **设置局部选择**，选 **Replace**、编号 **1**，勾 **Include distance neighborhood**，以源 **1** 为种子、填 **Radius (Å)=1.0** 并勾 Include seed atoms，预期包括1/2/3。局部集合和元素、连续编号、氢筛选共同作用。点 **清除局部限制** 恢复其他筛选控制的范围。

   [用户截图待引用：C05-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：并集后源编号1、2、4](screenshot/C05-02-union-result-GUI.jpg)

   ![Agent Computer Use：源编号1及1.0 Å邻域参数](screenshot/C05-02-radius-dialog-GUI.jpg)

   ![Agent Computer Use：邻域返回源编号1、2、3](screenshot/C05-02-radius-result-GUI.jpg)

3. 保持原子对象，点击 **创建视图与检查工具 → 创建局部显示层**，输入对应编号/半径，新副本独立调整样式/材质。优化/IRC 上局部集合固定源编号，换步不会自动换集合，必要时点 **按当前步重新计算**；IRC 仅在原层选择，不创建局部副本。

   [用户截图待引用：C05-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：编号1、4的独立局部显示层](screenshot/C05-03-local-layer-result-GUI.jpg)

4. 选择 **P03水二聚体原子对象**，在 **3D视图 → N侧栏 → QCBlender → 创建视图与检查工具** 分别点 **创建编号标注／创建距离标注／创建角度标注／创建二面角标注**；也可在 **Properties → Object → QCBlender → 局部选择与标注 → Source Atom Annotations** 点对应 **Atoms／Distance／Angle／Dihedral**，按测量顺序填实际源编号；编号填 **1**，距离填 **1,4**，角度填 **2,1,3**，二面角填 **2,1,4,5**。核对距离 Å、角度度数、带符号二面角范围 (-180°,180°]；退化构型显示 undefined 与原因。

   [用户截图待引用：C05-04，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：按测量顺序输入距离编号1、4](screenshot/C05-04-distance-dialog-GUI.jpg)

   ![Agent Computer Use观察：N侧栏中文按钮与对象属性英文按钮入口](screenshot/C05-04-two-entry-paths-GUI.jpg)

   原生操作示例使用独立显示层 **C05 final annotations**，先恢复全部6个原子，仅选该层。角度输入 **2,1,3**、二面角输入 **2,1,4,5**，**Decimal places=3**；确认后分别为 **112.770°**、**0.000°**。本批 Computer Use 实际创建；独立 NumPy 参考和 MCP 同时核对源编号顺序、单位、锚点、引线及50个科学数组。

   ![Agent Computer Use：当前活动原子层与标注入口](screenshot/C05-final-entrances-GUI.jpg)

   ![Agent Computer Use：角度编号2,1,3及三位小数](screenshot/C05-final-angle-dialog-GUI.jpg)

   ![Agent Computer Use：二面角编号2,1,4,5；B→C约定](screenshot/C05-final-dihedral-dialog-GUI.jpg)

5. 在 **局部选择与标注 → Source Atom Annotations** 用设置图标调整文字大小/颜色/偏移/小数和引线；原子源构型或当前优化/IRC 步决定值，对象缩放与振动位移不改变测量。切步核对文字、锚点、步号同步；相机建好后点 **Face All to Camera**。

   [用户截图待引用：C05-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：距离文字大小调整为0.22](screenshot/C05-05-edit-size-dialog-GUI.jpg)

   ![Agent Computer Use观察：MCP调整颜色、偏移和小数后，科学距离仍为2.900 Å](screenshot/C05-05-edited-result-MCP.jpg)

   ![Agent Computer Use：点击Face All to Camera；MCP核对实际旋转](screenshot/C05-final-face-camera-GUI.jpg)

   可复现排版：保持原子对象位置/旋转为0、缩放为1，球棍 **Atom Radius=0.35 Å、Bond Radius=0.12 Å、Quality=2**。四项文字设 **Size=0.16、Color RGB=(0.03,0.03,0.03)、Decimal places=3、Leader width=0.008、Show leader与可见勾选**；隐藏重复的旧标注及对应引线。分别设置下表 Offset，然后再点 **Face All to Camera**。这些设置只影响显示；本批另用MCP核对父对象缩放(2,0.5,1.5)后科学测量和源数组不变，再恢复缩放。

   | 标注 | 源编号 | Offset X/Y/Z（局部 Å） |
   | --- | --- | --- |
   | 编号 | 1 | −1.2 / −0.5 / −0.6 |
   | 距离 | 1,4 | 1.2 / −0.5 / 0.9 |
   | 角度 | 2,1,3 | 1.2 / −0.5 / −0.35 |
   | 二面角 | 2,1,4,5 | 0.8207 / −0.5 / −0.25215 |

   随优化步更新练习另用 **C02/P02 Job 1** 的四步优化轨迹，保持该轨迹副本为活动对象；添加距离 **1,2** 和角度 **2,1,3**，小数3。在 **对象属性 → Optimization Trajectory → Choose Step** 依次选1、2、3、4；距离/角度由各步源坐标决定，文字中的 **Optimization Step**、锚点和引线同步变化。第1步为 **0.990 Å、106.000°**，第4步为 **0.989 Å、100.037°**。原层保留原步号；不要把P03静态水二聚体的预期数值代入P02优化。

   图中排版使用Size=0.14，距离Offset=(0.3,−0.6,0.95)、角度Offset=(0.3,−0.6,−0.65)，从 **+X** 观察水的 **YZ** 源平面；文字朝向同方向相机。你可用右视图和视图缩放复现画幅。以下为MCP切步、调整排版后由Computer Use观察截图；本批逐步坐标与距离/角度经独立NumPy计算核对。

   ![MCP优化第1步；Computer Use观察：0.990 Å、106.000°及未完成收敛状态](screenshot/C05-followup-optimization-step1-framed-MCP.jpg)

   ![MCP优化第4步；Computer Use观察：0.989 Å、100.037°及收敛状态](screenshot/C05-followup-optimization-step4-framed-MCP.jpg)

   退化角的 **undefined** 与原因另用明确的合成重合原子测试核对，测试后恢复真实源坐标；该测试不代表真实优化步退化，也不要求用户修改输入原件。IRC随步练习仍在C10单独执行。

6. 在 **N 侧栏 → Display Layers** 选择层，用复制图标建立副本，改副本参数/材质确认原层不变；排序、视口/渲染显隐和删除只在副本测试。点击 **创建视图与检查工具 → 创建当前版本视图**，保留原层并核对新层。多选同类层，最后选参数源，在 **3D Viewport → 对象顶部菜单或对象右键菜单 → QCBlender → 复制显示参数到选中视图** 选类别；数值复制需同量/单位/电荷方法，不兼容时取消数值类别。目标位置、选择、裁剪和图例布局保留。

   [用户截图待引用：C05-06，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：复制原子显示层；MCP核对Mesh、外层树和8个标注数据独立](screenshot/C05-display-layer-copy-GUI.jpg)

   ![Agent Computer Use：上移副本；随后下移恢复原顺序，MCP核对次序](screenshot/C05-layer-order-up-GUI.jpg)

   ![Agent Computer Use：对象顶部菜单 → QCBlender → 复制显示参数到选中视图；源最后选中并保持活动](screenshot/C05-copy-parameters-menu-GUI.jpg)

   ![Agent Computer Use：确认几何表示、外观、数值设置三类别](screenshot/C05-copy-parameters-dialog-GUI.jpg)

   ![Computer Use观察MCP选中的目标：球棍/0.35/0.12已复制，氧集合1、4和编号控件保留](screenshot/C05-copy-parameters-result-MCP.jpg)

   ![Agent Computer Use：修复候选隐藏原子层，所属标注与引线同步隐藏](screenshot/C05-06-atom-layer-hidden-GUI.jpg)

   ![Agent Computer Use：恢复原子层及所属标注](screenshot/C05-06-atom-layer-restored-GUI.jpg)

   ![Agent操作示例：关闭IR谱显示层，谱线与所属文字同步隐藏；视口与渲染开关独立](screenshot/C05-06-ir-layer-hidden.jpg)

   当前版本视图示例：仅选上述 **P02第4步优化标注层**，点击 **创建当前版本视图**。新层应保留第4步和两项标注，Mesh、外层节点树、文字、曲线和材质独立；原层仍保留。本批真实点击后MCP核对通过，并在新层遍历四步，不改变原层；临时副本的单项标注和显示层移除另由MCP执行与核对，不记录为GUI删除点击。

   ![Agent Computer Use：创建当前版本优化视图；MCP核对第4步、独立图及标注](screenshot/C05-followup-current-view-after-GUI.jpg)

7. 对应 N01–N03/N15/N16，按 0.4 保存 `C05.png/.blend/.qcdata/`，加 `C05-selection.png`、`C05-annotations.png` 与显示层前后截图。

   [用户截图待引用：C05-07，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Computer Use观察：MCP另存自包含参数工程；原生新进程冷重开核对另记](screenshot/C05-controls-portable-saved-MCP.jpg)



   成图示例使用 **Eevee、1920×1080、Standard**，世界背景白色、Strength=0.7。正交相机位于 **(1.4,−12,1.45) Å**，Euler旋转 **(90°,0°,0°)**、Orthographic Scale=8.7。仅显示目标层：完整6原子、氧1/4局部层、完整6原子加四项标注依次导出三图。两盏Area灯为Disk、Size=5，分别位于 **(4,−5,7)** 与 **(−4,−5,5)**，Power=800/600 W，朝向 **(0,0,1.45)**；其他灯关闭渲染。相机和灯属于显示排版，不改变科学单位。

   ![MCP复用渲染操作：水二聚体全部6原子](screenshot/C05-final-render.png)

   ![MCP复用渲染操作：局部层只显示源氧1、4](screenshot/C05-selection-final-render.png)

   ![MCP实际渲染：O1、2.900 Å、112.770°、0.000°；四项标注与引线](screenshot/C05-annotations-final-render.png)

   本批另存 **C05-final.blend + .qcdata** 和同条目ZIP；关闭可见进程后，原路径、中文移动、解包分别在新原生后台进程冷重开，核对24文件、1 Dataset/50数组、6视图、52标注对象，并各重新渲染三图，像素一致。记录见[当前验证索引](../acceptance/tutorial-cu-validation.json)的 `C05_native_annotations_and_renders`；历史失败报告保留，隐藏对象的保存变换通过完整父级链核对。退化、随优化/IRC步更新、移除与当前版本视图另行验收，不能据此将整个C05或全教程写为Passed。

### C06 NBO 与 E(2)

**真实输入预期：** P02 **Job2/block1**，7条NBO、2条E(2)。NBO1为 O1–H2 的 BD，occupancy **1.99933**、energy **−0.77653 Eh**、原文行 **1444**；E(2)记录1 donor **1**→acceptor **7**、**0.59 kcal/mol**、原文行 **1434**。源SHA同0.1.1，不能把NBO编号当MO编号。

1. 确认已合法取得 P02 的真实 Log/Out 并核对 SHA；公开包不含许可未知原件。按 0.3 选清单指定 job 导入，选其原子对象，点 **3D视图 → N 侧栏 → QCBlender → 导入外部结果 → NBO 记录**。

   [用户截图待引用：C06-01，活动对象、参数与结果同屏；参数变化保留前后画面]

   ![Agent Computer Use：仅选P02 Job2原子对象，在导入外部结果中点击NBO记录](screenshot/C06-entry-GUI.jpg)

2. 对话框 **Gaussian Log / Out** 选同文件，**Gaussian job (1-based)** 与 **NBO block within job (1-based)** 按清单填，确认等待。NBO 几何关联要同段同构型，不能借优化多构型段作最终关联。

   [用户截图待引用：C06-02，活动对象、参数与结果同屏；参数变化保留前后画面]

   本例填 **Gaussian job (1-based)=2、NBO block within job (1-based)=1**。文件为 `water_neutral_nbo_opt_freq.out`；对象保持P02 Job2，不用Job1优化轨迹关联。

   ![Agent Computer Use：Gaussian Log/Out、Job2、block1原生导入对话框](screenshot/C06-dialog-GUI.jpg)

3. 选生成 NBO 记录对象，在 **Properties → 对象属性 → QCBlender · 对象与量子化学 → NBO Records** 选择一条 NBO 和 E(2)，核对条数、占据、能量单位、原子编号、供受体、E(2) kcal/mol 与原文行；NBO 不自动等同 canonical MO。

   [用户截图待引用：C06-03，活动对象、参数与结果同屏；参数变化保留前后画面]

   分别把 **NBO row (1-based)**、**E(2) row (1-based)** 从1改成2，确认选中的是不同源记录。第2条NBO为O1–H3 BD，第2条E(2)为2→6、0.59 kcal/mol。源行按原始文件整行核对，显示末尾空白可省略。

   ![Agent Computer Use：第1条NBO与E(2)，7轨道、2相互作用及原文行](screenshot/C06-record1-GUI.jpg)

   ![Agent Computer Use：分别选择第2条NBO与E(2)，核对源编号与数值](screenshot/C06-record2-GUI.jpg)

4. 在 **External Result Browser** 按编号/类型/占据、供受体/E(2) 筛选排序，点击 **应用筛选**，核对筛选不改源记录。恢复全部，撤销/重做导入核对关联。

   [用户截图待引用：C06-04，活动对象、参数与结果同屏；参数变化保留前后画面]

   本例在 **对象属性 → QCBlender · 对象与量子化学 → External Result Browser** 将 **Orbital type=BD、Orbital order=Occupancy, high to low、E(2) order=E(2), high to low**，点击 **应用筛选**；应显示2条轨道、2条E(2)。复原全部类型与默认范围后再点应用。Agent实际点击了上述组合；编号、范围、空结果和全部排序组合另由MCP用独立预期核对，不冒称逐项点击。

   ![Agent Computer Use：BD筛选和降序，应用后显示2轨道、2条E(2)](screenshot/C06-filter-BD-GUI.jpg)

5. 对同文件逐字节 `.log` 别名重复入口检查，摘要必须一致。别名在自己的 inputs 建立，不改原文件。

   [用户截图待引用：C06-05，活动对象、参数与结果同屏；参数变化保留前后画面]

   用相同字节的 `water_neutral_nbo_opt_freq.log` 再导入Job2/block1，新增记录对象而原记录保持。随后在3D视图执行 **Edit（编辑）→ 撤销**，确认别名对象消失；执行 **Edit（编辑）→ 重做**，确认别名对象及其原子父对象关联恢复。菜单复验Passed；本批快捷键尝试未恢复，失败截图单独留在证据目录，教程使用实际确认的菜单路径。

   ![Agent Computer Use：相同SHA的log别名，Job2/block1](screenshot/C06-cold-native-dialog-GUI.jpg)

   ![Agent Computer Use：撤销后别名对象消失，原out记录保持](screenshot/C06-cold-native-undo-GUI.jpg)

   ![Agent Computer Use：Edit重做菜单恢复log对象；MCP核对完整分析和父对象](screenshot/C06-cold-native-menu-redo-GUI.jpg)

6. 按 0.4 保存 `C06.png/.blend/.qcdata/`；总览必须同时拍到可读 NBO/E(2) 面板和关联分子。

   [用户截图待引用：C06-06，活动对象、参数与结果同屏；参数变化保留前后画面]

   可复现总览：选 `.log` NBO对象，在对象属性展开 **NBO Records** 并将两行索引设为1；把3D视图和属性编辑器分宽，使关联水分子与全部记录同屏。渲染单独选参考原子层，点击 **创建视图与检查工具 → 创建取景相机**，Margin=0.05，Eevee、1920×1080；NBO表本身是属性数据，用界面截图记录。

   ![Agent Computer Use观察：log别名、7条NBO/2条E(2)、单位、源行和关联水分子](screenshot/C06-cold-records-overview-GUI.jpg)

   ![MCP复用相机构图及渲染：P02 Job2水分子，表格数据另见界面图](screenshot/C06-render.png)

   本批保存 **C06-final.blend + .qcdata** 与同条目ZIP；关闭GUI进程后，原地、中文移动、解包三个新原生后台进程分别读取38文件、3 Dataset/33数组、NBO关联和全部元数据，并重渲染核对像素一致。证据见[当前验证索引](../acceptance/tutorial-cu-validation.json)的 `C06_NBO_records_browser_alias_and_cold_chain`。独立人工/科研签署仍为Not Run。



### C07 IGMH、IRI 成对场与散点

**真实输入预期：** P03参考与成对场6原子、片段 **1–3 / 4–6**，各Cube同为 **91×38×156**；Multiwfn **2026.9.20**。IGMH Geometry=`igmh/dg_inter.cub`，electron/bohr^4；Color=`igmh/sl2r.cub`，electron/bohr^3。IRI Geometry=`iri/func2.cub`，`a.u. (electron^-0.1 bohr^-0.7)`；Color=`iri/func1.cub`，electron/bohr^3；**a=1.1**。IGMH几何值域1.01735e-10..0.0185476，IRI几何0.0593502..11.432；颜色−194.599..+0.295371，原值不除100。色域截断只是显示。

1. 按C01的导入入口导入 **P03/water-dimer.fchk**；只选择生成的参考原子对象（本例名为 **QCBlender tutorial; PySCF 2.13.1; water-dimer; CC BY 4.0**），使其为活动对象。在 **3D视图 → N侧栏 → QCBlender → 导入外部结果** 点击 **IGMH / IRI 成对场**。

   [用户截图待引用：C07-01，活动原子对象与实际导入入口同屏]

   ![Agent Computer Use：P03参考原子对象与成对场导入入口](screenshot/C07-entry-GUI.jpg)

2. **Analysis** 选 **IGMH**，**Geometry Cube** 填 `P03/igmh/dg_inter.cub`，**sign(lambda2)rho Cube** 填 `P03/igmh/sl2r.cub`；**Geometry value unit=electron/bohr^4、Color value unit=electron/bohr^3、Color minimum=-0.04、Color maximum=0.04**，确认。完成后重新只选择同一参考原子对象，再次打开对话框，选 **IRI**，Geometry填 `P03/iri/func2.cub`，Color填 `P03/iri/func1.cub`，几何单位填 `a.u. (electron^-0.1 bohr^-0.7)`，颜色单位及色域同上，**IRI density exponent a=1.1**，确认。

   预期分别出现 **QC delta_g** 与 **QC iri_function** 几何场及对应颜色源和散点层。两场各有539,448个原始体素，网格/原子构型匹配；导入显示最多50,000散点。片段、方法/版本、a、网格与单位按生成清单核对；导入不执行IGMH/IRI计算。

   [用户截图待引用：C07-02，分别保留IGMH与IRI对话框、活动参考对象和导入结果]

   ![Agent Computer Use输入并确认：IGMH两文件、单位和色域](screenshot/C07-IGMH-dialog-GUI.jpg)

   ![Agent Computer Use观察：IGMH导入结果；全部数组及关联另由MCP核对](screenshot/C07-IGMH-imported-GUI.jpg)

   ![Agent Computer Use选择IRI并确认：路径和数值由MCP准备，a为1.1](screenshot/C07-IRI-dialog-GUI.jpg)

3. 只选择 **QC delta_g**，在 **Properties → 对象属性 → QCBlender · 对象与量子化学 → 几何表示** 把 **Isovalue** 设为 **0.005**；**QC iri_function** 设为 **1.0**。在各对象的 **颜色映射** 设置 **Color Minimum=-0.04、Color Center=0、Color Maximum=0.04**。位置取自几何场、颜色取自第二场；按N14查看来源，核对两输入摘要与网格，原值不除100。

   本例该阈值下IGMH为4,992顶点/4,906面、IRI为3,150顶点/3,140面（不含图例文字）。成图先只显示参考原子与当前几何场，按N17创建取景相机，**Margin=0.05、Eevee、1920×1080**。本示例视角绕X轴0.9 rad；在 **图例排版** 启用 **Show Legend**，把 **Legend Rotation** 的X角也设为 **0.9 rad（约51.566°）**，使量名、单位和−0.04/0/+0.04可读。初次构图前确认角度字段所用单位。

   [用户截图待引用：C07-03，分别保留两几何场参数、颜色源和可读图例]

   ![MCP复用显示控件与相机构图，真实EEVEE渲染：IGMH 0.005，颜色取自独立sign(lambda2)rho场](screenshot/C07-igmh-v2.png)

   ![MCP复用显示控件与相机构图，真实EEVEE渲染：IRI 1.0、a=1.1](screenshot/C07-iri-v2.png)

4. 只选择 **QC δg–sign(λ₂)ρ distribution** 散点对象，打开 **Properties → 对象属性 → QCBlender · 对象与量子化学 → External Result Browser**。默认横轴为 `sign_lambda2_rho [electron/bohr^3]`，纵轴为 `delta_g [electron/bohr^4]`。启用四个范围开关，填 **X from=-0.04、X to=0.04、Y from=0.001、Y to=0.02**，点击 **更新散点**，预期匹配/显示均为 **36,391**。

   勾选 **Swap scatter axes**，保持这四个数值，再点 **更新散点**，预期为 **28,630**：交换后范围作用于新的轴，表示的筛选区域也随之改变。若要保持物理区域相同，须同时交换X/Y范围。IRI散点用颜色−0.04..0.04、IRI 0.1..2筛选为12,736点；同步交换范围后仍为12,736。恢复全部范围时匹配539,448、显示50,000，显示抽样不删除科学数组。

   [用户截图待引用：C07-04，范围开关、轴量/单位与匹配/显示数；交换前后分别保存]

   ![Agent Computer Use启用范围并更新：36,391点；范围数值由MCP准备](screenshot/C07-IGMH-filter-GUI.jpg)

   ![Agent Computer Use交换轴并更新：相同数字应用于新轴后为28,630点](screenshot/C07-IGMH-swap-GUI.jpg)

   ![MCP恢复IGMH 36,391点范围并真实渲染；量名和单位另见上方面板截图](screenshot/C07-scatter-v2.png)

5. 重新只选择 **P03参考原子对象**，打开成对场导入，选 **IGMH** 并重填对应单位。Geometry用 **P03/igmh/dg_inter.cub**，Color误选 **P05/nocv/nocv-pair1.cub**；预期拒绝并报告 **Atom identities/order differ; an explicit atom mapping is required**，原有对象及数据绑定不变。此例验证原子身份拒绝，网格拒绝需要另一组明确输入。

   恢复正确配对再导入，在3D视图执行 **Edit（编辑）→ 撤销**，新生成五个配对对象消失；执行 **Edit（编辑）→ 重做**，这些对象及科学绑定恢复。保留一个正确显示组，避免重复图层叠加。

   [用户截图待引用：C07-05，错误输入/拒绝信息，以及正确导入的撤销与重做结果]

   ![MCP准备错误配对、Agent Computer Use确认：P03几何与P05颜色](screenshot/C07-wrong-pair-dialog-GUI.jpg)

   ![Agent Computer Use观察拒绝；MCP核对原有对象与绑定不变](screenshot/C07-wrong-pair-refused-GUI.jpg)

   ![Agent Computer Use执行Edit菜单撤销：新增配对对象移除](screenshot/C07-native-undo-GUI.jpg)

   ![Agent Computer Use执行Edit菜单重做：对象与同一科学记录恢复](screenshot/C07-native-redo-GUI.jpg)

6. 对应N06/N07/N14/N16，按0.4导出两表面和散点PNG，保存总览与 **C07.blend + C07.qcdata**，点击 **N侧栏 → QCBlender → 工程与诊断 → 保存自包含工程**。本批效果图文件带 `-v2` 后缀；用户自己的文件可沿用 `C07-igmh.png`、`C07-iri.png`、`C07-scatter.png`。

   [用户截图待引用：C07-06，保存路径、活动对象、图例和保存后的工程；冷重开另留截图]

   ![Computer Use观察与截图：MCP保存后的IGMH总览；保存和控件设置由MCP执行](screenshot/C07-saved-overview-MCP.jpg)

   本批保全44文件、3 Dataset/66数组和4体积文件，关闭GUI后依次在三个新原生后台进程读取原路径、中文移动和ZIP解包工程；九次真实重渲染像素一致。报告、输入/候选摘要及工具身份见[当前验证索引](../acceptance/tutorial-cu-validation.json)的 `C07_paired_fields_scatter_and_cold_chain`。该冷读为命令行技术证据，用户复做及独立科研签署仍为Not Run。


### C08 ESP 极值与面积分布

**真实输入预期：** P03 **rho=0.001 electron/bohr^3** 表面；4最大值/3最小值，PDB B-factor是ESP，**kcal/mol**，坐标Å。例如最大值源1：**36.69 kcal/mol** @ **(−1.740,−0.051,1.026) Å**；最小值源1：**−25.50** @ **(−0.036,−1.400,1.768) Å**。面积各bin见原stdout，合计 **73.1833 Å²**。C04初始0.004密度表面若作为视觉参照，先改成0.001并单独记录；分析导入活动对象仍是ESP场。

1. 打开C04工程，按0.4另存为C08。先只选 **QC electron_number_density** 密度表面，在 **Properties → 对象属性 → QCBlender · 对象与量子化学 → 几何表示** 把 **Isovalue** 从 **0.004** 改为 **0.001 electron/bohr^3**，记录前后画面。然后只选实际ESP场 **QC electrostatic_potential**；在 **3D视图 → N侧栏 → QCBlender → 导入外部结果** 点击 **ESP 表面分析**。密度着色层不能替代实际ESP场参考。

   [用户截图待引用：C08-01，阈值调整前后、活动ESP对象和导入入口]

   ![Agent Computer Use：实际ESP场与ESP表面分析入口；密度阈值另由MCP准备](screenshot/C08-entry-GUI.jpg)

2. **Extrema PDB** 填 `P03/esp/surfanalysis.pdb`，**Area distribution text** 填 `P03/esp/stdout.log`，**Surface definition=rho=0.001 electron/bohr^3**；**Extrema value unit=kcal/mol、Distribution center unit=kcal/mol、Area unit=angstrom^2**，确认。极值和面积单位须与PDB REMARK和原表声明一致；中心单位由使用者明确指定。预期生成 **QC ESP maximum、QC ESP minimum、QC ESP area distribution**，均关联到所选ESP场。

   该外部分析表来自清单中Multiwfn的源表面。Blender本例0.7Å原生网格只用于显示参照，面积数据直接读取源表；导入不在该显示网格重算面积。原log包含非UTF-8进度/横幅字节；核对完整文件SHA-256，保留原始字节，使用原ASCII科学表行核对。

   [用户截图待引用：C08-02，完整路径、表面定义、三单位和确认后的三对象]

   ![MCP准备参数、Agent Computer Use确认：ESP极值与面积导入](screenshot/C08-dialog-GUI.jpg)

3. 只选 **QC ESP maximum**，打开 **Properties → 对象属性 → QCBlender · 对象与量子化学 → External Analysis Records**。**Record (1-based)** 从1改为2；最大值1为 **36.69** @ **(−1.740,−0.051,1.026) Å**，最大值2为 **57.80** @ **(−1.682,−0.042,4.031) Å**，单位均为kcal/mol。选择 **QC ESP minimum** 同样逐条查看；最小值2为 **−50.68** @ **(−0.005,−0.058,−1.769) Å**。PDB的B-factor列明确记录ESP，C/O分别编码maximum/minimum。

   在 **External Result Browser** 保持 **Source number=0**（全部），启用两个 **ESP value [kcal/mol]** 范围开关，填 **从=40、到=60**，保持 **Show source label、Show matching points**，**Match (1-based)=1**，点击 **应用筛选**。预期2条最大值（源2/3），突出源2并显示 **maximum 2 | 57.8 kcal/mol**。**Source number=2**可只查看该源点。换层查看minimum，不能将maximum层误作minimum。

   [用户截图待引用：C08-03，记录1/2、源坐标、范围开关和筛选突出位置]

   ![Agent Computer Use观察：最大值记录1，36.69 kcal/mol](screenshot/C08-maximum-record1-GUI.jpg)

   ![Agent Computer Use选择：最大值记录2，57.80 kcal/mol及源坐标](screenshot/C08-maximum-record2-GUI.jpg)

   ![Agent Computer Use启用范围并应用：2条最大值；40/60由MCP准备](screenshot/C08-maximum-filter-GUI.jpg)

4. 只选 **QC ESP area distribution**，打开同一 **External Result Browser**。**Area bin selection=Center in range**，启用范围 **从=0、到=20 kcal/mol**，点击 **应用筛选**：预期4个中心2.5/7.5/12.5/17.5区间，**displayed=14.4784 Å²、Source percentages shown=19.7838%**。

   改选 **Recorded interval overlaps range**，保留0..20，再点 **应用筛选**：预期保留6个完整源区间，包括与0、20相接的边界区间，**displayed=21.2676 Å²、Source percentages shown=29.0608%**。该模式保留完整bin，不按交集长度分割面积。两模式总面积均 **73.1833 Å²**，百分比不重新归一化。取消范围开关并应用恢复40个bin；原打印百分比合计100.0002%，属于小数舍入，面板可能显示100%。柱形保持原全表中心及面积缩放；准确bin、单位与小计以属性面板和原表为准。

   [用户截图待引用：C08-04，两模式分别保留范围、总面积、小计及源百分比]

   ![Agent Computer Use应用中心范围：4bin、14.4784 Å²、19.7838%](screenshot/C08-area-center-GUI.jpg)

   ![Agent Computer Use切换并应用完整源区间：6bin、21.2676 Å²、29.0608%](screenshot/C08-area-source-interval-GUI.jpg)

5. 对应N13/N16，按0.4导出 **C08-extrema.png、C08-area.png**。极值图先取消数值范围、**Source number=0、Match (1-based)=2**并应用两极值层，显示参考原子、两层及其标签；面积图仅显示恢复全部40bin的面积层。按N17创建相机，**Margin=0.05、Eevee、1920×1080**。本示例沿Y方向取景，标签绕X轴 **90°**面向相机；部分minimum在此投影重叠，可旋转视角并逐条突出核对。源记录和坐标不随观察方向改变。

   为取得下图照明，添加Sun灯，**Energy=2、Angle=0.35 rad（约20.054°）**，灯旋转约 **X=40.107°、Y=−17.189°、Z=−22.918°**；两个原生标签的材质设白色 **Base Color、Emission Color**，**Emission Strength=1**。这些是工程显示设置。恢复极值层后再次点 **应用筛选**，确认标签可见，避免把面积图中临时隐藏的标签状态带入保存工程。

   点击 **3D视图 → N侧栏 → QCBlender → 工程与诊断 → 保存自包含工程**，保存 `.blend + .qcdata`；按N16导出配套ZIP。完成后正常关闭，原路径、中文移动和ZIP解包路径分别在一个新Blender进程打开核对，每次关闭后再开下一处。本批文件名为 **C08-final.blend**，效果图带 `-v2` 后缀。

   [用户截图待引用：C08-05，分别保留极值图、面积图、保存路径和三个冷重开结果]

   ![MCP配置灯光、标签和相机，原生EEVEE渲染：ESP源极值；观察方向会产生投影重叠](screenshot/C08-extrema-v2.png)

   ![MCP配置相机，原生EEVEE渲染：40个源面积bin的原缩放柱形](screenshot/C08-area-v2.png)

   ![Computer Use观察与截图：MCP保存的最终工程、源标签和对象属性](screenshot/C08-saved-GUI.jpg)

   本批35组MCP筛选核对、5项错误输入检查及120文件/8Dataset/224数组/4体积/20引用保全Passed；三个串行原生后台进程冷读和6次重渲染像素一致Passed。报告、输入/候选摘要、失败诊断与工具身份见[当前验证索引](../acceptance/tutorial-cu-validation.json)的 `C08_ESP_records_filters_and_cold_chain`。用户复做和独立科研签署仍为Not Run。


### C09 AIM 临界点、路径与属性

**真实输入预期：** 11临界点属性记录、10路径；源点1类型 **C/(3,−3)**，坐标 **(−0.724,0,3.384) Å**（PDB打印精度），对应源核6(H)，Density of all electrons **0.4316646446**，源属性单位约定按CPprop原文。本样本实际点类型以原文件为准，空类型保持不存在；不要为了C/N/O/F齐全制造记录。

1. 导入 P03 同构型参考 FCHK，选原子对象，点 **导入外部结果 → AIM 拓扑**，分别填 **CPs PDB、Paths PDB、CP properties text (optional)**。有真实属性才填第三项。

   [用户截图待引用：C09-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 选生成 C/N/O/F 点层和路径层，在 **External Analysis Records** 查类型、坐标、路径组、属性值/单位和原子关联；本样本没有的类型不凭空构造。

   [用户截图待引用：C09-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 在 **External Result Browser** 选源编号，按已有数值过滤，点 **应用筛选**；分别开关点/标签/路径，选另一类型须换对应层。筛选恢复后源记录不变。

   [用户截图待引用：C09-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 对应 N13/N16，按 0.4 保存 `C09-points.png`、`C09-paths.png`、总览与工程。

   [用户截图待引用：C09-04，活动对象、参数与结果同屏；参数变化保留前后画面]



### C10 真实 IRC 步序与能量

**真实输入预期：** H2O2四原子 **[O,O,H,H]**，RHF/STO-3G，中性单重态18电子；原生geomeTRIC **1.1.1** 双向IRC，61接受帧，截取0-based **29/30(TS)/31**。CSV中的1/2/3依次对应它们，FCHK打印能量 **−148.764884 / −148.764883 / −148.764884 Eh**；TS唯一虚频 **−48.1434547807 cm^-1**、最大梯度 **1.893862e-8 Eh/bohr**。三点邻近TS，构型变化小，核对坐标/游标而非要求肉眼发生大反应；不能把该短段称为完整61步路径。

1. 按清单保持 P04 CSV 和逐步 FCHK 相对目录。CSV 是 UTF-8，首行为 `step,fchk`，步号从 1 连续，文件顺序与记录的反应方向一致；输入来自真实 IRC 计算。

   [用户截图待引用：C10-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 在 **N 侧栏 → 工作流 → 导入 IRC 路径** 在 **CSV manifest: step,fchk** 指定 steps CSV，等待建立根原子视图与曲线；选**IRC 根原子对象**，打开 **对象属性 → IRC Path**。

   [用户截图待引用：C10-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 点击 **Previous/Next** 遍历每步，核对步号、原子身份/坐标、hartree 能量及曲线游标。确认端点和当前清单；能量须对应该步 FCHK。

   [用户截图待引用：C10-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 在 C05 同入口添加当前步距离/角度/二面角标注，换步核对文字和锚点同步；局部集合保持固定编号，需要时重新计算。

   [用户截图待引用：C10-04，活动对象、参数与结果同屏；参数变化保留前后画面]

5. 在 **inputs/P04/** 复制steps.csv为 **checks-duplicate.csv**，用文本编辑器把第二行数据的step也改为1，保留FCHK相对路径，保存UTF-8；用该副本导入应拒绝重复编号，记录副本摘要和错误。再用完整原CSV导入；原件不改。

   [用户截图待引用：C10-05，活动对象、参数与结果同屏；参数变化保留前后画面]

6. 对应 N15/N16/N18，按 0.4 保存 `C10-curve.png`、`C10-steps.png`、总览与工程。

   [用户截图待引用：C10-06，活动对象、参数与结果同屏；参数变化保留前后画面]



### C11 IRC 逐步 Mayer 键级

**真实输入预期：** 同C10三步、每步六对Mayer；原子对 **1,2** 值 **0.987331413844 / 0.987349305673 / 0.987331413844**，无量纲。可换对1,3：**0.950875651565 / 0.950844120525 / 0.950875651565**，复核独立曲线。结果来自同构型PySCF AO密度/重叠矩阵，文本采用兼容输入语法，其producer不是Multiwfn。

1. 打开 C10 工程另存 C11，选 **IRC 根原子对象**，在 **对象属性 → IRC Path → Import Mayer Results** 在 **CSV manifest: step,mayer_output** 指定清单的 Mayer CSV。

   [用户截图待引用：C11-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 选择新 Mayer 记录对象，在 **IRC Path** 填 **Atom A (1-based)、Atom B (1-based)**，点击实际按钮 **Plot Pair**；核对原子对、每步值/无量纲单位和源文本。

   [用户截图待引用：C11-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 切 IRC 步观察构型、键级曲线游标及显示值同步，再换原子对点 Plot Pair。距离推断显示键不是 Mayer 值。

   [用户截图待引用：C11-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 缺步检查在**尚无Mayer表的IRC根**上执行：重新打开C10工程的独立副本，或从完整steps.csv新建IRC路径，再选根对象。在 **inputs/P04/** 复制Mayer CSV为 **checks-missing-mayer.csv**，删除step3的数据行并保存UTF-8，相对文本路径保留；用副本导入应报 **Mayer step count differs from the IRC path**，且不产生新表。记录副本摘要/实际错误，再导入完整原CSV；已有Mayer表的拒绝不计为缺步检查通过。按 0.4 保存 `C11-curve.png`、`C11-records.png`、总览与工程。

   [用户截图待引用：C11-04，活动对象、参数与结果同屏；参数变化保留前后画面]



### C12 ETS-NOCV 真实结果表

**真实输入预期：** CO–BH3共6原子 **[C,O,B,H,H,H]**，22电子，中性单重态，RB3LYP/6-31G(d)，源能量 **−139.947332 Eh**。pair1 **Total** 对轨道 **1/48**，特征值 **±0.54550**，pair能量 **−57.02 kcal/mol**，原表行7。此能量为真实整体KS矩阵重构的 **Multiwfn近似**，不是F_TS过渡态方法；详情见清单/NOTICE。

1. 导入 P05 参考构型，选原子对象，点 **导入外部结果 → ETS-NOCV 表**。填 **ETS-NOCV output text**，**Pair energy unit** 选文件实际 kcal/mol 或 hartree。

   [用户截图待引用：C12-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 选新表对象，在 **External Analysis Records** 查 pair、spin、特征值、成对轨道编号、能量、原文行号和源 SHA，与同次真实输出核对。

   [用户截图待引用：C12-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 在 **External Result Browser** 按 pair/spin/能量等筛选排序，点击 **应用筛选**。字段缺失按缺失记录，不推断数值。已有唯一关联场时可定位；没有时不表示已生成 pair Cube。

   [用户截图待引用：C12-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 按 0.4 保存 `C12.png/.blend/.qcdata/`，图中同时可读结果表与参考分子。

   [用户截图待引用：C12-04，活动对象、参数与结果同屏；参数变化保留前后画面]



### C13 NOCV pair Cube 与两符号密度

**真实输入预期：** `P05/nocv/nocv-pair1.cub`，pair1/Total，与C12表和构型一致；网格 **47×50×57**，值域 **−0.243093..+0.0494892 electron/bohr^3**，SHA为 `d6d3ec263d5173261791f997eabd78b8112f6685abc3bd851c70deec86a82e33`。正/负阈值从 **0.003** 开始；用不存在pair **999** 或错误Spin **Alpha**观察关联拒绝。

1. 打开 C12 工程另存 C13，选 **ETS-NOCV 表对象**，点 **导入外部结果 → NOCV pair Cube**，在 **Pair number、Spin、Signed pair Cube、Deformation density unit** 填清单 pair 编号、自旋、Cube 路径与数值已有单位，确认等待。

   [用户截图待引用：C13-01，活动对象、参数与结果同屏；参数变化保留前后画面]

2. 选新 pair 场核对表行/pair/spin、参考构型、Cube SHA 和密度单位；不能用 canonical MO Cube 冒充 NOCV 密度。

   [用户截图待引用：C13-02，活动对象、参数与结果同屏；参数变化保留前后画面]

3. 在 **几何表示** 分别显示正/负值，关 Link Thresholds 后各自改阈值，在材质属性改透明度。正负值为形变密度的符号，不能套用 MO 相位解释。

   [用户截图待引用：C13-03，活动对象、参数与结果同屏；参数变化保留前后画面]

4. 先重新选择 **C12的ETS-NOCV表对象**，再打开pair Cube导入，用表中不存在的pair **999** 或错误Spin **Alpha**复核关联拒绝；活动pair场不能作为导入参考。记录错误，随后恢复合法输入。对应 N04/N05/N16，按 0.4 保存 `C13-positive.png`、`C13-negative.png`、总览与工程。

   [用户截图待引用：C13-04，活动对象、参数与结果同屏；参数变化保留前后画面]



## 2. N01–N18 节点与交互检查

以上教程先通过对象/材质属性操作。需查看实际节点时，选指定视图，将一个编辑器切为 **Geometry Node Editor**，取消其图钉固定，选择该视图的 Geometry Nodes 修改器/节点组。修改器输入与对象属性共享参数；内部绑定 Dataset 的节点不作为独立通用资产。**Asset Browser → QCBlender Nodes** 按目录查找九个公共资产，在几何节点编辑器的 **添加** 菜单选择对应目录/资产并单击放置，添加到独立测试副本，核对已有输入/输出并接入真实视图。操作前保存，新增节点或改接线仅在副本进行；记录实际节点名、接线、原值→新值和可见变化，不以节点名称存在计 Passed。

新建视图的外层节点按可见Frame查找：原子 **Atoms: selection and representation**；振动 **Modes: displacement and animation**；等值面 **Field: source and isosurface**；映射 **Scalar: sampling and colors**；电荷 **Charge: attributes and colors**；图例 **Legend: range and labels**；切片 **Slice: plane placement**。Frame用于阅读，不增加物理量或公共节点；实际节点和接线仍以所选视图为准。

1. **N01 QC Select Atoms**：C01/C05 原子；Geometry Nodes 中 Selection、元素号、源编号首末；再局部集合。

   预期/需记录：源编号从1；O2用实际O编号，水再选氢；交集与源数组保持一致。

   [用户截图待引用：N01，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   对象属性控件示例：选 C05 水二聚体原子副本，在 **局部选择与标注 → 清除局部限制** 恢复完整源编号，再展开 **几何表示**。勾选 **选中项**；**Element (0 = all)=8、First Atom (1-based)=1、Last Atom (0 = all)=0** 时只保留氧编号1、4。取消选中项时输出为空。恢复勾选并设 **Element=0、First=2、Last=3**，只保留氢编号2、3；元素与编号范围共同筛选。标注引用源构型，筛选不会删除源数组或标注。此处展示对象属性控件，公共资产的独立添加与接线按本节开头另行执行。

   ![Agent Computer Use（候选2eddb6a）：Element=8；MCP核对源编号1、4](screenshot/N01-element8-GUI.jpg)

   ![Agent Computer Use：取消选中项，MCP核对零顶点；源标注仍可见](screenshot/N01-selection-off-GUI.jpg)

   ![Agent Computer Use：Element=0、First=2、Last=3；MCP核对氢编号2、3](screenshot/N01-first2-last3-GUI.jpg)

   公共资产练习使用 C05 的 P03 水二聚体副本：在 **显示层 → 复制** 后，仅选新副本为活动对象，清除局部限制，保持元素0、First=1、Last=0；副本标注可暂时隐藏。切换 **Geometry Nodes** 工作区，取消图钉，选择副本修改器树。在底部编辑器点 **添加 → 原子选择 → QC Select Atoms**，单击空白处放置。保留原图，按 N02 接入新增显示分支；不要修改公共资产内部节点。

   [用户截图待引用：N01-public，活动副本、添加菜单、选择输入和结果]

   ![Agent Computer Use：从添加菜单选择 QC Select Atoms](screenshot/N01-public-add-menu-GUI.jpg)

   ![Agent Computer Use：在独立副本放置公共选择资产](screenshot/N01-public-added-GUI.jpg)

   N02 分支连好后，在新选择节点勾选 **选中项（Selection）**，设 **Element=8、First=1、Last=0**，只显示氧1、4。取消勾选应为空；恢复勾选并设 Element=0、First=2、Last=3，应显示氢2、3。再测 Element=8、First=1、Last=3，只保留氧1；First=2、Last=3时为空。核对实际源编号，不能只比较显示数量：两个氧和两个氢在本例都求值得到84顶点、160面。恢复全原子参数后继续 N02。

   ![Agent Computer Use：Selection 输出接入表示节点的 Selection](screenshot/N01-public-selection-wire-GUI.jpg)

   ![Agent原生输入Element=8；MCP核对氧编号1、4，科学数组不变](screenshot/N01-public-oxygen-GUI.jpg)

   ![Agent原生关闭Selection；MCP核对零顶点](screenshot/N01-public-selection-off-GUI.jpg)

2. **N02 QC Style Atoms and Bonds**：原子；对象属性→几何表示；球棍/空间填充/键，改原子与键半径。

   预期/需记录：轮廓不同；半径Å，键是距离推断。

   [用户截图待引用：N02，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   在 C05 副本 **几何表示 → 样式** 依次选 **球棍／空间填充／键线**。局部集合仅含氧1、4时，空间填充有两个球，键线为空：两氧相距2.900 Å，没有推断的键。点 **清除局部限制**，并恢复 **Element=0、First=1、Last=0、选中项勾选**，键线显示两个水分子的O–H键。将 **Bond Radius [Å] 0.07→0.12**，键应变粗；回到球棍，将 **Atom Radius [Å] 0.25→0.35**，球应变大。原层保持自己的参数。

   ![Agent Computer Use：局部氧1、4的空间填充](screenshot/N02-space-fill-GUI.jpg)

   ![Agent Computer Use：相同局部氧集合的键线为空](screenshot/N02-bonds-empty-selection-GUI.jpg)

   ![Agent Computer Use：清除局部限制后，六原子的O–H键线](screenshot/N02-bonds-all-atoms-cleared-GUI.jpg)

   ![Agent Computer Use：键半径0.12 Å；源数组不变](screenshot/N02-bond-radius012-GUI.jpg)

   ![Agent Computer Use：球棍原子半径0.35 Å；原层参数不变](screenshot/N02-atom-radius035-GUI.jpg)

   保持 N01 副本活动，在 **添加 → 表示 → 原子与键 → QC Style Atoms and Bonds** 放置资产。连接 **组输入 → 几何数据** 到新表示节点 **几何数据**，N01 节点 **Selection → Selection**；选择副本的元素材质，再将新表示节点 **几何数据** 接 **组输出 → 几何数据**，替换旧显示输出。本批示例为辅助组输入/输出创建、专用材质和布局由 MCP 准备，三条显示分支接线由 Computer Use 实际拖放；你可直接使用副本原有组输入和组输出。

   [用户截图待引用：N02-public，活动副本、显示分支接线与三种样式]

   ![Agent Computer Use：原子与键目录中的公共表示资产](screenshot/N02-public-add-menu-GUI.jpg)

   ![Agent Computer Use：新公共表示节点放置于独立副本](screenshot/N02-public-added-GUI.jpg)

   ![Agent实际拖放选择及几何接线；辅助输入/输出、材质和布局由MCP准备](screenshot/N01-N02-public-route-GUI.jpg)

   全6原子选择时，将新节点 **Style (0 ball-stick, 1 space-fill, 2 bonds)** 依次设 **0、1、2**，球棍、空间填充和键线分别应为300/252/48顶点、512/480/32面；此计数适用于本批Quality=2、Atom Radius=0.25 Å、Bond Radius=0.07 Å、VDW Scale=1。核对4条O–H键及源编号1–6。改 Atom Radius 或 Bond Radius 时，只改变相应显示半径，不改变科学坐标；对象属性的两半径操作示例见上方。最后恢复Style=0，再按 N09 加裁剪。

   ![Agent原生Style=1；MCP核对六原子空间填充252顶点](screenshot/N02-public-spacefill-GUI.jpg)

   ![Agent原生Style=2；MCP核对4条真实O–H推断键及全部源编号](screenshot/N02-public-bonds-GUI.jpg)

3. **N03 氢显隐**：C05含氢原子；局部选择与标注的三个氢按钮、撤销重做。

   预期/需记录：指定氢身份正确，副本不改原层。

   [用户截图待引用：N03，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

4. **N04 QC Style Isosurface / QC Surface Representation**：C01/C13场；几何表示；两符号开关与实体/线框/点。

   预期/需记录：两符号与三样式确实变化；各量符号含义正确。

   [用户截图待引用：N04，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

5. **N05 独立等值与透明度**：C01/C13场；关Link Thresholds、改两阈值；材质改两透明度。

   预期/需记录：分别响应，字段单位正确，源数值不变。

   [用户截图待引用：N05，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

6. **N06 QC Sample Scalar Field**：C04密度表面绑定ESP；C03同网格采样；Geometry Nodes检查接线。

   预期/需记录：几何和颜色分工；域外无效，与来源绑定一致。

   [用户截图待引用：N06，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   选 C04 的密度/ESP 映射视图，在 **N 侧栏 → 显示层** 选该层，点 **复制**；仅选新副本作为活动对象，切换 **Geometry Nodes** 工作区，底部编辑器取消图钉，选择副本的修改器树。原视图保持原参数。示例副本为 `QC electron_number_density.003`。

   ![Agent原生显示层复制；此后节点调整仅作用于副本](screenshot/N15-field-copy-GUI.jpg)

   在几何节点编辑器点 **添加 → 数据 → 采样 → QC Sample Scalar Field** 并放置。找到绑定 ESP 源对象的 **物体信息**，将其 **几何数据** 输出接新节点 **体积（Volume）**；将 **位置（Position）** 节点的输出接新节点 **位置**。将新节点 **值（Value）** 和 **有效（Valid）** 接副本颜色映射节点对应输入，替换旧取样输入；密度等值面几何仍连接颜色节点，不能把 ESP 源体积用作密度等值面输入。

   ![Agent原生添加取样资产；后续Value/Valid接线由MCP完成](screenshot/N06-sample-asset-added-GUI.jpg)

   仅在副本测试：断开新取样节点的位置输入，依次输入 **(0,0,0)**、**(0,−2,0)**、**(0,−2,1.45) Å**。这使表面每个点读取同一位置，颜色应一致；本批粗网格三点ESP约为 **1.224086233、−0.044865982、−0.022647081 hartree/e**。这些是 C04 所记录网格的插值值，换网格时重新核对，不作为所有构型的常数。域外/无效检查另见 N17。

   ![位置默认0/0/0；GUI体积接线、MCP数据核对；表面与图例分别计算](screenshot/N06-sample-origin-linked-GUI.jpg)

   ![Agent原生把取样位置Y改为−2；162个真实表面顶点均与独立插值参考一致](screenshot/N06-sample-Y-negative-two-GUI.jpg)

   ![Agent原生把取样位置Z改为1.45；科学值见同批报告](screenshot/N06-sample-Z-one-point-four-five-GUI.jpg)

   最后重新连接 **位置 → 位置**，恢复表面逐点采样。副本几何、值、有效性和颜色分量应与断开前相同，源视图不变。

   ![Agent原生恢复Position接线；MCP核对副本求值摘要恢复且原视图不变](screenshot/N06-sample-Position-restored-GUI.jpg)

7. **N07 QC Map Scalar Colors v2**：C04映射视图；颜色映射、零中心/有效范围、图例排版、材质色带。

   预期/需记录：色标/量单位同步，范围递增，无效洋红，副本布局独立。

   [用户截图待引用：N07，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   保持 N06 副本活动，在几何节点编辑器 **添加 → 颜色映射 → QC Map Scalar Colors v2** 放置资产。将密度等值面输出接其 **几何数据**，新取样节点 **值/有效** 接对应输入；**材质**选择副本原颜色映射节点的专用材质。新节点输出替换旧颜色节点到 **合并几何** 的连线，不能在多输入合并口同时保留两份表面。

   ![Agent原生放置颜色资产；接线和副本专用材质由MCP设置](screenshot/N07-color-asset-added-GUI.jpg)

   ![MCP连接新颜色节点；同色域下副本几何和颜色分量与原管线相同](screenshot/N07-color-asset-connected-MCP.jpg)

   测试节点独立输入时，先关闭副本 **Show Legend**，暂时断开新节点三个色域输入，填 **Color Minimum=−0.05、Color Center=0、色彩最大值=0.05**；再把最大值改为 **0.1**。正值区的颜色分量应改变，负值区仍按 −0.05..0 映射，零仍为中心。随后将三个色域输入接回 **组输入** 对应输出，并恢复图例；使表面和图例共同使用修改器的 −0.05/0/+0.05 色域。

   ![Agent原生把色彩最大值改为0.1；MCP独立核对零中心分段映射，测试期间图例关闭](screenshot/N07-color-upper-bound-GUI.jpg)

   副本图例可单独设位置 **(−3,0,0)**、长度 **1.5**、宽度 **0.4**、字号 **0.15**；源视图的节点坐标、Frame、材质、色域和求值结果应保留原值。

   ![MCP调整副本图例；Computer Use观察截图，原显示层不变](screenshot/N07-field-copy-legend-independent-MCP.jpg)

8. **N08 QC Planar Slice**：C04切片；空间观察、定平面/Gizmo、切片等值线。

   预期/需记录：平面/分辨率/曲线变化，采样与单位一致。

   [用户截图待引用：N08，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   选 C04 的 ESP 切片层，按 N06 的复制步骤生成独立副本，示例名 `C04 public slice asset test`；仅选副本，编辑其 Geometry Nodes 修改器树。在 **添加 → 空间 → 切片 → QC Planar Slice** 放置新资产。将 **组输入 → 中心/旋转** 接新节点对应输入；**宽度=6、高度=6、分辨率=101**。用新节点输出替换旧平面节点到颜色节点的几何连线，保留原有 ESP Volume/Position 采样及材质。

   ![Agent原生加入平面资产，MCP绑定中心/旋转并连接真实ESP切片](screenshot/N08-slice-asset-connected-MCP.jpg)

   把新节点 **分辨率 101→51**：切片网格顶点应由 **10,201→2,601**，范围仍为 X/Y **−3..3 Å**、Z **1.45 Å**，取样量和单位不变。本项测试新增节点的网格；等值线的重建沿用 C04 步骤，不根据原有曲线宣称已重建为51分辨率。最后将新节点 **宽度/高度/分辨率** 接回组输入，恢复共享参数101，核对副本几何恢复、原层未变。

   ![Agent原生修改新平面节点分辨率；MCP核对2601顶点和21点独立插值参考](screenshot/N08-slice-resolution-51-GUI.jpg)

9. **N09 QC Clip Geometry**：C01原子/场；添加裁剪控件后空间观察。

   预期/需记录：平面/盒分别裁预期区域，原始数据不变。

   [用户截图待引用：N09，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   先用 N01/N02 的 P03 全6原子副本练习；C01 的场显示可使用同一裁剪入口，按其几何另外记录预期。保持副本活动、Style=0，在 **Geometry Nodes → 添加 → 空间 → 裁剪 → QC Clip Geometry** 放置资产。连接 **QC Style Atoms and Bonds → 几何数据 → QC Clip Geometry → 几何数据 → 组输出**，替换之前直通输出；Plane Enabled 与 Box Enabled 均关闭时，应与未裁剪几何完全相同。

   [用户截图待引用：N09-public，活动副本、裁剪分支、边界输入及保留区域]

   ![Agent Computer Use：空间、裁剪目录中的 QC Clip Geometry](screenshot/N09-public-add-menu-GUI.jpg)

   ![Agent Computer Use：放置公共裁剪资产](screenshot/N09-public-added-GUI.jpg)

   ![Agent实际拖放表示到裁剪、裁剪到输出；边界向量由MCP准备](screenshot/N09-public-route-GUI.jpg)

   设置平面 **Origin=(0,0,1.45) Å、法线=(0,0,1)**，方框 **Minimum=(−0.5,−2,−2) Å、Maximum=(0.5,2,5) Å**。仅勾选平面Enabled时保留上方水分子源编号4、5、6；再同时勾选方框Enabled时保留编号4的部分几何；关闭平面、只保留方框时保留氧1、4及与其关联的部分键几何。每次比较裁剪前后位置和源编号，科学数组保持不变。本批依次核对150、50、100顶点与CPU半空间/闭区间盒参考完全一致；这是所记录质量、半径和边界的计数，不能代用于其他视图或场网格。最后关闭两项Enabled，恢复300顶点、512面。

   ![Agent原生开启平面裁剪；MCP逐顶点核对保留4、5、6](screenshot/N09-public-plane-GUI.jpg)

   ![Agent原生同时开启平面和方框；MCP核对交集50顶点、编号4](screenshot/N09-public-intersection-GUI.jpg)

   ![Agent原生仅保留方框裁剪；MCP核对100顶点及源编号1、4](screenshot/N09-public-box-GUI.jpg)

   按0.4先 **打包关联库**，再 **保存自包含工程** 和 **归档工程**；关闭本进程后，分别在新进程读取原工程、中文移动副本、ZIP解包副本。核对公共节点接口、所有输入、源编号和科学数组。Agent本批保存、归档及冷重开使用已登记操作的MCP/命令行复用；三个副本图、几何、50数组和48标注完全一致，移动/解包位置未取得外部节点库仍能求值。完整C05成图与其他案例验收分别记录。

   ![Computer Use观察已保存工程；裁剪恢复及MCP打包保存，完整成图另验收](screenshot/N09-public-restored-saved-MCP-observation.jpg)

10. **N10 QC Style Volume Fog**：C01自旋雾；几何表示/颜色映射/材质控制。

   预期/需记录：颜色/阈值/不透明度变化，全透明无雾。

   [用户截图待引用：N10，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

11. **N11 QC Vector Glyph**：C04偶极；节点或几何控件Angstrom per Debye。

   预期/需记录：显示长度变，物理方向/三分量/原点不变。

   [用户截图待引用：N11，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

12. **N12 振动/ QC IR Sticks v1**：C02频率原子；科学记录模式、Advanced/高级参数、Timeline、位移箭头。

   预期/需记录：切模式/实际帧推进/IR高亮同步，平衡坐标不变。

   [用户截图待引用：N12，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

13. **N13 分析点标注**：C08/C09点/路径层；External Result Browser、应用筛选。

   预期/需记录：显隐/定位/标签随记录选择，源值保留。

   [用户截图待引用：N13，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

14. **N14 QC scatter points**：C07散点；External Result Browser→更新散点、轴交换。

   预期/需记录：两真实字段量单位明确，匹配数/显示数分别记录。

   [用户截图待引用：N14，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

15. **N15 显示层独立性**：C02/C05副本；Display Layers、创建当前版本视图、右键复制显示参数。

   预期/需记录：节点/材质/标注独立，排序/显隐/删除正确，原数组SHA不变。

   [用户截图待引用：N15，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

16. **N16 撤销/重做**：C01/C05/C06/C07–C13；3D视口Ctrl+Z/Ctrl+Shift+Z。

   预期/需记录：对象、节点、数据关联恢复；失败先记缺陷，不吞异常。

   [用户截图待引用：N16，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

17. **N17 游标/无效域/探针/剖面**：C04场/切片；读取游标、点击探针、剖面起点/创建/CSV。

   预期/需记录：量单位与坐标换算正确，无效/域外非零替代；CSV重导一致。

   [用户截图待引用：N17，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

18. **N18 保存/移动/冷重开**：每例执行0.4；保存自包含工程、归档、恢复。

   预期/需记录：新进程和移动副本来源/数组/节点/图例可读，摘要核对。

   [用户截图待引用：N18，活动对象、参数变化前后与实际结果；可引用对应 C 案例步骤证据]

   N06–N08 加入公共资产后，先执行 0.4 的 **打包关联库**，再用 **保存自包含工程** 另存并归档。示例工程 `C04-public-nodes-packed.blend + .qcdata` 含两个内嵌节点库；三次冷重开分别使用新的唯一可见进程，MCP核对17个对象引用、7个Dataset、222数组、4个体积文件和117文件摘要。移动和解包时原相对路径的节点库不存在，内嵌资产仍求值正常。

   ![MCP另存并归档公共节点工程；Computer Use观察截图](screenshot/N18-public-nodes-packed-saved-MCP.jpg)

   ![中文移动副本冷重开，外部节点库不存在；MCP求值核对、Computer Use观察](screenshot/N18-public-nodes-cold-moved-MCP.jpg)

   ![ZIP解包副本冷重开，内嵌节点库和科学数组完整；MCP核对、Computer Use观察](screenshot/N18-public-nodes-cold-unpacked-MCP.jpg)



## 3. 结果记录与独立科研签署

### 3.1 操作证据与身份

每个案例按下表逐步填写，可复制行；未实际执行保持 Not Run。所有路径相对本次批次，用户截图引用填写在相应操作步骤后。本文插图标为 Agent 操作示例，只证明图中所示动作与状态；未展示步骤继续保留待引用，不据此认定全教程 GUI Passed。

| 案例/步骤 | 活动对象/选择顺序 | 编辑器/面板/实际文字 | 参数原值→新值 | 预期→实际 | 结果 | 证据位置 | 执行者/方式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CXX/步骤号 | 待填写 | 待填写 | 待填写 | 待填写 | Not Run | 证据见各步骤 | 待填写 |

| 证据身份 | 可证明的范围 | 本次填写 |
| --- | --- | --- |
| User：用户实际操作 | 用户执行的明确点击与反馈；无反馈步骤不推定完成 | Not Run；截图/反馈待填写 |
| Agent Computer Use | 经授权在可见窗口实际点击；记录安装、进程、活动对象与截图 | Not Run；由根Agent记录 |
| MCP操作与数据核对 | 经授权调用真实 registered operators、原生文件对话框，核对数组/摘要/进程，记录真实窗口截图、渲染与新进程冷重开；写明实际调用及辅助范围 | 本批技术范围 Passed，见验证索引；鼠标点击与用户签署 Not Run |
| 原生脚本数据核对 | 维护者的自动化解析/数组/原生operator检查；独立绑定候选与命令 | Not Run；本表由当前批次执行者填写，维护者本轮结果见验证索引 |
| 独立科研复做与签署 | 独立使用者复做操作，并判断科学记录与成图适用性 | Not Run；姓名/日期留空 |

[cleanup-validation.json](../acceptance/cleanup-validation.json) 记录历史批次技术核查与部分 Agent 点击，以及导入参数错误的历史复验。历史 Passed 不继承到本批；本教程的执行记录须关联本批候选和输入身份；本轮[验证索引](../acceptance/tutorial-validation.json)分别记录历史原生核对和本批 MCP操作与数据核对。按最新授权，本批 C01–C13 核心检查、N01–N18 技术检查、真实窗口截图、C13 渲染、Log Job 2→新 FCHK 对话框回归，以及原路径、移动路径和解包路径的新进程冷重开均为 Passed；这不代表逐例完整渲染、全部鼠标点击或独立科研签署。用户截图占位由实际操作者补入，技术通过不自动填写本表。安装资格、自动测试、真实点击、科研签署是不同结论。

### 3.2 独立使用者案例结果

此表仅由实际独立验收者填写；Agent 技术记录放在 3.1。每项写 Passed / Failed / Not Run，任何必需项 Failed 则该例 Failed；缺输入、未执行或只见测试报告不能填写 Passed。记录缺陷编号和修复后的候选身份，重新执行受影响步骤。

| 案例 | 导入 | 源数值/单位 | 参数/节点前后 | PNG | 保存重开 | 移动冷重开 | 实测/缺陷；证据位置 | 用户签名与日期 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C02 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C03 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C04 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C05 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C06 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C07 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C08 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C09 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C10 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C11 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C12 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |
| C13 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | 证据见各步骤 |  |

| 节点/交互 | 结果 | 实测引用/证据位置 | 缺陷 |
| --- | --- | --- | --- |
| N01 | Not Run | 证据见各步骤 |  |
| N02 | Not Run | 证据见各步骤 |  |
| N03 | Not Run | 证据见各步骤 |  |
| N04 | Not Run | 证据见各步骤 |  |
| N05 | Not Run | 证据见各步骤 |  |
| N06 | Not Run | 证据见各步骤 |  |
| N07 | Not Run | 证据见各步骤 |  |
| N08 | Not Run | 证据见各步骤 |  |
| N09 | Not Run | 证据见各步骤 |  |
| N10 | Not Run | 证据见各步骤 |  |
| N11 | Not Run | 证据见各步骤 |  |
| N12 | Not Run | 证据见各步骤 |  |
| N13 | Not Run | 证据见各步骤 |  |
| N14 | Not Run | 证据见各步骤 |  |
| N15 | Not Run | 证据见各步骤 |  |
| N16 | Not Run | 证据见各步骤 |  |
| N17 | Not Run | 证据见各步骤 |  |
| N18 | Not Run | 证据见各步骤 |  |

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
