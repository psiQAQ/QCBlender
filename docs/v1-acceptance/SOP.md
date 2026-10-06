# QCBlender 用户验证 SOP

适用 **Windows x64、Blender 5.1.1、QCBlender 0.1.0**。按本文导入样本、调整显示、核对科学记录、导出数据，并验证工程保存和重新打开后的结果。

先完成准备和 XYZ 入门流程，再检查关联与共享对象；需要验证出图时完成 A01–A09，需要完整验收时继续 C01–C13、X01 和 N01–N18。每步记录实际结果：**Passed** 表示已执行且符合预期，**Failed** 表示已执行但不符合预期，**Not Run** 表示未执行或尚无法判断。正确拒绝无效操作、且场景保持不变的测试可以记 Passed。

| 要做的事 | 入口 |
| --- | --- |
| 核对安装包、准备样本并安装 | [0.1–0.3](#0-准备安装与通用操作)，材料身份见[安装包与样本](MATERIALS.md) |
| 第一次导入、查看来源和保存重开 | [XYZ 入门流程](#第一次操作xyz-小流程) |
| 检查关联失效、共享对象及 Undo/Redo | [P1-A/P1-B](#当前构型关联与共享对象检查) |
| 生成轨道并完成首次出图 | [A00–A09](#alpha-首次出图与短验收) |
| 完整功能验证 | [C01–C13/X01](#1-c01c13-输入与物理量教程)、[N01–N18](#2-n01n18-节点与交互检查) |
| 每例出图、保存、迁移和导出 | [0.4](#04-相机渲染保存与移动冷重开每例执行)、[0.5](#05-显式数据导出) |
| 填写结果及科研适用性 | [第 3 节](#3-结果记录与独立科研签署)，复制[记录模板](RECORD-TEMPLATE.md)到本次目录填写 |

## 0. 准备、安装与通用操作

### 0.1 取得材料并建立本次目录

1. 取得扩展 ZIP、v2 教程样本包及身份清单，按[安装包与样本](MATERIALS.md)核对大小与 SHA-256。把实际版本、文件路径、摘要、操作者和日期填入记录模板。不同安装包即使版本号相同也分别记录。
2. 新建自己的验证目录，保存本次输入、截图、导出和工程。下面使用仓库所在位置；在其他电脑上可修改路径为实际材料与保存位置。
3. 在 PowerShell 中执行以下准备命令。后续命令沿用同一个窗口中的变量。

```powershell
$sopRepository = 'D:\workspace\QCBlender'
$sopCandidateRoot = Join-Path $sopRepository `
    'outputs\candidates\current\alpha-ci-0.1.0-f8b1115'
$sopCandidate = Join-Path $sopCandidateRoot 'qcblender-0.1.0.zip'
$sopSamples = Join-Path $sopRepository `
    'tests\data\distribution\qcblender-public-tutorial-samples-v2.zip'

Get-Item -LiteralPath $sopCandidate, $sopSamples |
    Select-Object FullName, Length
Get-FileHash -LiteralPath $sopCandidate, $sopSamples -Algorithm SHA256
```

核对成功后创建批次并解压样本；摘要不符时先重新取得正确文件。

```powershell
$sopBatchName = Get-Date -Format 'yyyy-MM-dd-HHmmss'
$sopBatch = Join-Path $sopRepository `
    "outputs\projects\human-acceptance\$sopBatchName"
if (Test-Path -LiteralPath $sopBatch) { throw '请使用未占用的批次目录' }
$sopFolders = @(
    'inputs', 'cases', 'screenshots', 'records', 'exports', 'moved', 'unpacked',
    'profile\config', 'profile\extensions', 'profile\datafiles', 'profile\cache'
)
foreach ($sopFolder in $sopFolders) {
    New-Item -ItemType Directory -Path (Join-Path $sopBatch $sopFolder) |
        Out-Null
}
Expand-Archive -LiteralPath $sopSamples `
    -DestinationPath (Join-Path $sopBatch 'inputs')
$sopBatch
```

保持 P01/P03/P04/P05/P06 目录结构和许可证文件；P04 的 CSV 通过相对路径引用 FCHK 和分析表，不要单独搬走其中一个文件。本文 `inputs/`、`cases/` 等路径均相对本次批次目录。

### 0.1.1 单独取得 P02（C02/C06 前置条件）

已有本机原件时，在上述 PowerShell 窗口执行：

```powershell
$sopP02Source = Join-Path $sopRepository `
    'tests\data\local\log-examples\water_neutral_nbo_opt_freq.out'
$sopP02Directory = Join-Path $sopBatch 'inputs\P02'
New-Item -ItemType Directory -Path $sopP02Directory | Out-Null
Copy-Item -LiteralPath $sopP02Source -Destination $sopP02Directory
$sopP02Out = Join-Path $sopP02Directory 'water_neutral_nbo_opt_freq.out'
$sopP02Log = Join-Path $sopP02Directory 'water_neutral_nbo_opt_freq.log'
Copy-Item -LiteralPath $sopP02Out -Destination $sopP02Log
Get-FileHash -LiteralPath $sopP02Out, $sopP02Log -Algorithm SHA256
```

两份摘要应与[材料清单中的 P02](MATERIALS.md#p02-优化与频率日志)一致。没有本机原件时，先按该页的来源入口取得文件，再填写实际路径。缺少 P02 时将 C02、C06 和 P1-B 的优化部分记为 Not Run，其他案例可继续。

### 0.2 安装与编辑器定位

先保存并正常关闭原有 Blender 工程。使用本批独立配置启动 Blender，之后的冷重开也从这个 PowerShell 窗口启动。

```powershell
$sopBlender = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
$env:BLENDER_USER_RESOURCES = Join-Path $sopBatch 'profile'
$env:BLENDER_USER_CONFIG = Join-Path $sopBatch 'profile\config'
$env:BLENDER_USER_EXTENSIONS = Join-Path $sopBatch 'profile\extensions'
$env:BLENDER_USER_DATAFILES = Join-Path $sopBatch 'profile\datafiles'
$env:BLENDER_USER_CACHE = Join-Path $sopBatch 'profile\cache'
& $sopBlender --offline-mode --disable-autoexec
```

1. 打开 **Edit → Preferences → Get Extensions → 菜单 → Install from Disk**，选择本次扩展 ZIP，安装并启用 QCBlender。
2. 在 **Preferences → Add-ons → QCBlender** 点击 **Check Scientific Runtime**，等待结果。也可从 **N 侧栏 → QCBlender → 工程与诊断 → 检查科学运行环境** 进入。记录版本与检查截图；失败时保留完整错误，相关场生成步骤暂不继续。
3. 回到 **3D Viewport**，切换 **Object Mode**，按 `N` 打开 **QCBlender** 页。本文简称“N 侧栏”。
4. **对象属性**指 **Properties → Object → QCBlender · 对象与量子化学**。子面板默认折叠时先展开。可选中 QC 对象，再点 **N 侧栏 → 工作流 → 对象属性与显示参数**；该快捷入口会固定对象，换对象后再次点击或解除 Properties 顶部图钉。
5. 每次创建场、轨迹或分析记录后，在 Outliner 或 **Display Layers** 选中新对象。多选时，最后选中的是活动对象。按钮灰显时检查活动对象、Object Mode 及界面给出的原因。
6. 查看材质时切换 **Material Preview**；材质参数位于 **Properties → Material → QCBlender · 节点材质**。Solid 模式下的灰色显示不用于判断材质效果。

### 0.3 导入、数值与参数核对

1. 独立案例用 **File → New → General** 新建工程；在 Outliner 选中新工程自带的 **Cube**，按 **Delete** 删除，避免遮挡分子和渲染。C08 从 C04、C11 从 C10、C13 从 C12 的已保存工程继续；先另存本例工程。
2. 普通输入使用 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**。Log/Out 导入后等待 **Choose Gaussian Calculation**，在 **Calculation** 选择指定计算段，核对 route、终止状态、原文行范围、能量及 Explicit geometry。段号从 1 开始；无显式几何的段不借用其他段构型。取消预览后应没有该次新数据对象。
3. 选中新对象，打开 **数据集与数值摘要 → 查看完整来源**，或对象属性中的 **来源详情**；必要时点 **刷新来源**。核对源摘要、生成程序、方法/基组、电荷/多重度、选中段、原子顺序及单位。能量和振动模式还需在 **科学记录与振动模式** 中核对。
4. 原子源编号从 1 起，显示坐标为 Å，1 Blender 单位 = 1 Å。常用单位：能量 Eh、电荷 e、偶极 Debye、频率 cm^-1、IR 强度 km/mol、MO 振幅 bohr^-3/2、密度 electron/bohr^3、ESP hartree/e。外部分析按源输出的实际单位填写。
5. 每次改变参数，记录“原值 → 新值”、前后画面和预期。检查当前步骤/帧、构型及标注是否一致；MO 正负代表相位，振动振幅与速度是显示设置，XYZ 帧序不自动代表物理时间。
6. 核对数值时同时查看原始记录及界面/CSV；显示位数不足时以导出数据比较。教程的比较容差见第 1 节，仅适用于指定量和参考。网格、等值和配色是展示参数，科研定量用途另记收敛依据。

读取现成样本无需安装计算软件；自己的 Gaussian `.chk` 需由提供者用 `formchk` 转成 FCHK 后再导入。

### 0.4 相机、渲染、保存与移动冷重开（每例执行）

1. 选中需要成图的分子、表面或路径，转到合适观察方向，点 **N 侧栏 → 创建视图与检查工具 → 创建取景相机**。按小键盘 `0` 查看取景，`F9` 可调整 **Margin per side**（默认 5%）。通过 Display Layers 关闭不需要的视口和渲染层。
2. 在 **Render/Output Properties** 设置渲染器、分辨率、采样和色彩管理，按需 **Add → Light**。点 **Render → Render Image（F12）**，在结果窗口 **Image → Save As** 保存到 `cases/CXX/CXX-render.png`。科学记录、NBO/Mayer/ETS-NOCV 表和采样记录另留属性面板截图或 CSV。
3. 记录样本摘要、方法/基组、量与单位、轨道/自旋、网格、等值和颜色范围；振动另记模式频率、振幅与播放速度。灯光、相机和渲染参数与图片一起保留。
4. 手动加入公共节点资产后，先执行 **File → External Data → Pack Linked Libraries（打包关联库）**。仅用自动创建的本地节点组可直接继续。
5. 点 **N 侧栏 → 工程与诊断 → 保存自包含工程**，保存为 `cases/CXX/CXX.blend`，确认同目录生成 `CXX.qcdata/`。PNG、原始输入、CSV 和参数摘要分别保留。
6. 用 **File → Quit** 正常关闭 Blender；确认进程退出后，用 0.2 的命令重新启动，从 **File → Open** 打开原位置工程。重新选对象，核对来源、步骤、单位、参数、材质和图例，重新渲染并再次导出适用的 CSV/摘要。
7. 再次正常退出，将 `.blend` 与整个同名 `.qcdata/` 一起复制到本批 `moved/CXX 中文路径/`。打开副本前核对文件完整性，再启动新进程打开副本，重复上一步核对。科学数据路径应指向副本的 `.qcdata/`。
8. 在重开的工程中保存最新状态，点 **工程与诊断 → 归档工程** 输出 ZIP。关闭 Blender，将 ZIP 解压到本批 `unpacked/CXX/`，启动新进程打开解包工程，再核对一次。

分别填写“保存、原地冷重开、移动冷重开、归档解包冷重开”的结果。冷重开需要实际退出并启动新进程。异常时保留原件和错误信息；恢复操作见 N18。

复制后可用下面的 PowerShell 核对全部文件摘要。把 `CXX` 改成实际案例编号；在打开或保存副本之前执行。

```powershell
$sopCase = 'CXX'
$sopOriginal = Join-Path $sopBatch "cases\$sopCase"
$sopMoved = Join-Path $sopBatch "moved\$sopCase 中文路径"
$sopFiles = @((Get-Item -LiteralPath "$sopOriginal\$sopCase.blend")) +
    @(Get-ChildItem -LiteralPath "$sopOriginal\$sopCase.qcdata" -Recurse -File -ErrorAction Stop)
$sopHashRows = foreach ($sopFile in $sopFiles) {
    $sopRelative = $sopFile.FullName.Substring($sopOriginal.Length + 1)
    $sopDestination = Join-Path $sopMoved $sopRelative
    $sopBefore = (Get-FileHash -LiteralPath $sopFile.FullName -Algorithm SHA256).Hash
    $sopAfter = (Get-FileHash -LiteralPath $sopDestination -Algorithm SHA256 -ErrorAction Stop).Hash
    if ($sopBefore -ne $sopAfter) { throw "SHA-256 不一致：$sopRelative" }
    [pscustomobject]@{ Path = $sopRelative; SHA256 = $sopBefore; Result = 'Passed' }
}
$sopHashRows | Export-Csv -LiteralPath "$sopBatch\records\$sopCase-move-hashes.csv" `
    -Encoding UTF8 -NoTypeInformation
```

### 0.5 显式数据导出

1. 在 **Preferences → Add-ons → QCBlender → 数据导出目录** 检查默认位置。可填跨工程绝对目录；留空时，已保存工程使用 `.blend` 父目录，未保存工程使用系统 Documents。分别查看这两种情况下的导出对话框，记录实际默认路径。
2. 选择含所需科学记录的对象，点 **N 侧栏 → 工程与诊断 → 导出数据与参数摘要**，在 **Data** 选择种类：

   | 数据 | 选择对象 | 导出后核对 |
   | --- | --- | --- |
   | 当前视图参数摘要 | 当前 QC 视图 | view-summary.md、metadata.json；来源、单位、实时参数、网格、有效域与材质 |
   | IR | 含模式的原子对象 | 模式编号、频率、IR 强度 |
   | optimization | 优化原子或轨迹 | 步骤、能量、收敛记录 |
   | IRC | 路径根对象 | 步序、能量、源 FCHK 身份 |
   | Mayer | IRC Mayer 表 | 步骤、源原子对、键级 |
   | profile | 采样线记录 | 距离、场值、valid |
   | paired | 成对场记录 | 原体素索引、双值、有效域 |
   | ESP_AREA | ESP 面积表 | 原 bin、面积、percent |

3. 将 **Output directory** 改为本批 `exports/` 的实际绝对路径。paired 与 ESP_AREA 分别导出 **Rows=All source records** 和 **Current filter**；筛选条件须先在 **External Result Browser** 中设置并应用。
4. 确认并等待完成消息，打开新建的唯一结果目录。科学数据应有 UTF-8 CSV 和 `metadata.json`；摘要应有 `view-summary.md` 和 `metadata.json`。核对表中内容及来源、单位、筛选和缺值。摘要的 `partial/unverified` 项应列出原因，按实际可核验范围记录。
5. 重复导出一次，应产生另一目录，原结果不变。重开对话框时应恢复偏好中的目录，单次覆盖不改变偏好。在确认前取消对话框，不应产生新完整结果。
6. 对较大的 paired 全量导出，在任务仍运行时按 **Esc**。等待取消完成，确认原有结果保留、本次没有可误认成功的最终目录。若按键前已经完成，取消检查记 Not Run；若报错，保存完整错误和任务路径。清除筛选，再导出 All source records，确认完整记录仍可取得。
7. 按 0.4 保存并重开后，重新选相同记录和筛选条件导出，逐值比较 CSV、原索引、单位与来源。导出目录单独保留。

## 第一次操作：XYZ 小流程

使用 `inputs/P06/water-dimer.xyz`，先完成一组不需要生成场的操作。

1. 按 0.3 新建工程并移除默认 Cube，点 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，选择该文件。
2. 等待完成，在 Outliner 选中新原子对象。打开 **对象属性 → 来源详情**，核对源文件、摘要、原子顺序与坐标单位。
3. 预期为 **6 个原子，O/H/H/O/H/H，坐标单位 Å**。切换 Material Preview 查看分子，保存活动对象、分子及来源信息截图。
4. 点 **工程与诊断 → 保存自包含工程**，保存 `cases/X01-start/X01-start.blend`，确认旁边有 `X01-start.qcdata/`。
5. 正常退出 Blender，按 0.2 重新启动并打开工程，核对分子、来源和显示。

记录本次已做步骤；完整 XYZ 多帧、标注、独立副本和错误边界继续见 X01。

## 当前构型关联与共享对象检查

两个检查各使用独立新工程。P04 的 `steps.csv` 与三份 FCHK 保持相对位置。每次保存按 0.4 完成原地、移动和归档解包冷重开。

### P1-A 当前步骤关联、失效与重新关联

1. 点 **N 侧栏 → 工作流 → 导入 IRC 路径**，选择 `inputs/P04/steps.csv`。选中 IRC 根原子对象，确认 **对象属性 → IRC Path** 显示 **Step 1/3**。
2. 使用普通导入入口单独导入 `inputs/P04/step-001.fchk`。可将两对象命名为 `IRC-current`、`FCHK-step1`。
3. 先选 IRC，再按住 Shift 选 FCHK，使 **FCHK 最后选中并成为活动参考对象**。点 **对象属性 → 关联选中数据源**，保持容差 **0.001 Å**，不启用刚体对齐，确认。预期第 1 步与静态第 1 步关联成功。
4. 仅选 IRC 根对象，点 **IRC Path → Next** 到第 2 步。打开 **来源详情 → Source record → Geometry association**，预期 `status: stale` 并提示重新关联。
5. 按步骤 3 的顺序再次关联当前第 2 步和静态第 1 步。预期拒绝，最大原子偏差约 **0.0354167 Å**，超过容差。记录完整错误；拒绝前后步号、构型、对象位置与现有记录应保持一致。
6. 仅选 IRC，点 **Previous** 回第 1 步，再看关联记录，预期仍为 `stale`。明确重新执行步骤 3，才恢复有效关联。
7. 从刚关联成功的第 1 步开始，点 **Next**，确认第 2 步且关联失效；再用 **Edit → Undo**，预期恢复第 1 步及有效关联；用 **Edit → Redo**，预期恢复第 2 步及失效状态。

保留成功、换步失效、不同步拒绝、返回原步仍失效、重新关联及 Undo/Redo 的截图和记录。保存为 `cases/P1-A/P1-A.blend`，重开时核对当前步骤、参考对象和关联状态。

### P1-B 共享 mesh 拒绝换步与单用户恢复

1. 在新工程导入 P04 IRC，选中根原子对象。鼠标放在 3D Viewport，按 **Alt+D**，再按 **Esc** 取消位移；副本已经创建，通常与原件重叠。
2. 在 Outliner 区分原件与副本，只选副本，点 **IRC Path → Next**。预期拒绝，并提示先使 **Object Data** 单用户。分别选中两者检查步号、构型和标注均未变化。
3. 保持只选副本，使用 **3D Viewport → Object → Relations → Make Single User → Object & Data**。
4. 再点 **IRC Path → Next**。预期副本正常换步、原件保持原步。分别选择并核对，不能仅凭重叠画面判断。
5. 用 **Edit → Undo / Redo** 检查副本换步恢复和重做，原件始终不受影响。再 Undo 换步和单用户操作，回到共享状态时换步仍应拒绝；Redo 单用户操作后可再次换步。
6. 在另一工程导入 P02 并选择 **Job 1**，选原子对象，点 **N 侧栏 → 创建视图与检查工具 → 创建优化轨迹视图**。
7. 选中新轨迹对象，在 **Optimization Trajectory** 中完整重复步骤 1–5：Alt+D、取消位移、Next 拒绝、Object & Data 单用户、Next 成功、Undo/Redo。

IRC 与优化分别保存为 `cases/P1-B-IRC/`、`cases/P1-B-opt/` 下的同名自包含工程。两种入口分别记录结果；保留拒绝提示、单用户操作、独立换步及 Undo/Redo 的前后状态。

## Alpha 首次出图与短验收

本流程用 P01 的 O₂ 波函数生成一张轨道图，导出参数并保存可移动工程。每一步均记录结果；完成 A01–A09 后可填写短验收记录。

### A00 建立本次目录并启动干净配置

先完成 0.1、0.2。本例输入为 `inputs/P01/o2-uhf.fchk`，UHF/STO-3G，8,880 字节，SHA-256 为 `ef562c4b210e7c380219282d7684370cca1f0e8349dffa1d4388af5831472e36`。在本批 `cases/A/` 保存图片、工程，在 `exports/` 保存摘要。

### A01 安装扩展并检查运行库

按 0.2 安装本次 ZIP、启用扩展并点击 **Check Scientific Runtime**。预期检查成功且 N 侧栏可见；保存安装版本与结果截图。若已在本批完成，引用该次记录。

### A02 从原始 P01 导入并核对来源

按 0.3 新建工程并移除默认 Cube，点 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ** 选择 P01。选中新原子对象，解除旧图钉，在 **数据集与数值摘要 → 查看完整来源** 核对 **UHF、STO-3G、两个 O 原子**及源摘要。

### A03 自动预检并生成 Alpha 源 MO9

选 P01 原子对象，点 **工作流 → 生成量子化学场**。等待首次科学预检完成；通过后在 **Generate Quantum Field** 填写：

| 控件 | 值 |
| --- | --- |
| Quantity | Molecular orbital |
| Spin | Alpha |
| Orbital | Source number |
| Orbital number (1-based) | 9 |
| Grid spacing (angstrom) | 0.2 |
| Grid margin (angstrom) | 3 |
| Memory budget (MiB) | 512 |

资源预览参考：**31 × 31 × 37、35,557 体素、Dataset 约 0.31 MiB、求值估算约 0.59 MiB**。有差异时先核对输入、量、自旋、编号和网格，记录实际值。无拒绝原因后点 **OK**；预期生成双符号场，来源为 Alpha 源 MO9。

预检失败时保留诊断；取消对话框不应创建结果。内存预算和 Dataset 大小分别核对；Dataset 上限为 1 GiB，预算预览不代表进程峰值。重新绑定来源或新进程重开后，生成前需重新预检。

### A04 修改等值并观察两符号

选中新 MO9 场视图，在 **Properties → Modifiers → QC Isosurface** 将 **Isovalue** 从实际原值改为 **0.045 bohr^-3/2**，保持 **Link Thresholds** 和正负两符号开启。切换 Material Preview，记录表面形状与两种相位材质的前后变化。用 **Edit → Undo / Redo** 检查恢复，最终回到 0.045。

### A05 创建取景并保存首次图片

选最终 MO9 场视图，按 0.4 创建取景相机、设置灯光与渲染参数。确认两符号未被裁切，保存 `cases/A/A-render.png`，同时记录网格、等值、材质和渲染参数。

### A06 导出当前视图参数摘要

保持 MO9 活动，点 **工程与诊断 → 导出数据与参数摘要**，**Data=当前视图参数摘要**，**Output directory** 选择本批 `exports/` 的实际绝对路径。

打开生成的 `view-summary.md` 与 `metadata.json`，核对 Alpha/源 MO9、bohr^-3/2、0.2 Å 网格、有效域、实时等值 0.045 和材质。按实际精度比较浮点数。`partial/unverified` 项按其原因记录。重复导出应创建另一目录；取消对话框应不生成新完整结果。

### A07 保存自包含工程并正常退出

按 0.4 保存为 `cases/A/A.blend`，确认 `A.qcdata/`，再正常关闭 Blender。PNG 与参数摘要分别保留。

### A08 将工程放到中文目录并核对摘要

将 `A.blend` 与整个 `A.qcdata/` 复制到 `moved/A 中文路径/`。按 0.4 的摘要命令核对，把 `$sopCase` 改为 `A`，保留逐文件比较记录。

### A09 新进程重开、再导出并记录完成

在原 PowerShell 窗口按 0.2 启动新 Blender，打开中文目录副本。选择 MO9，确认两符号、等值 0.045、材质和来源；数据应指向副本的 `A.qcdata/`。重新渲染并导出摘要，比较来源、参数、网格和有效域。将 A01–A09 结果填入记录模板；完整验收继续执行以下案例。

## 完整 SOP 执行顺序与完成标准

按 C01–C13、X01 逐例操作；C08 从 C04、C11 从 C10、C13 从 C12 的保存工程另存后继续，其余新建工程。每例完成数据核对及 0.4/0.5，再在独立副本执行适用的 N 项。

| 范围 | 需要完成的检查 |
| --- | --- |
| C01–C05 | 波函数、能量、振动、Cube、ESP、标注与显示 |
| C06–C09 | NBO、IGMH/IRI、ESP 分析、AIM 的来源、数值、单位与显示 |
| C10–C13 | IRC/Mayer、ETS-NOCV 及 pair Cube；当前步和记录对应 |
| X01 | XYZ 单帧、多帧、标注、独立副本与错误边界 |
| N01–N18 | 节点、材质、筛选、交互、撤销、拒绝与恢复 |
| 每例留存 | 图片/面板、参数、适用 CSV/摘要、`.blend + .qcdata/`、三种冷重开结果 |

遇到问题，保存出错前工程、输入摘要、选择顺序、参数、完整错误与最短复现步骤。更换修复包后记录新摘要，并重做受影响步骤与保存重开检查。第 3 节汇总实际完成范围。

## 1. C01–C13 输入与物理量教程

以下文件路径均相对本批 `inputs/`。[样本清单](tutorial-samples.json) 的 `archive_path` 对应包内路径，`path` 是仓库路径。每例先核对输入，完成编号步骤后执行 0.4/0.5，并在记录模板填写结果。

生成 MO、密度和 ESP 默认使用 **Grid spacing=0.2 Å、Grid margin=3 Å、Memory budget=512 MiB**，记录实际网格。新建原子视图外层 **Quality=3**，新切片 **201 点/轴**；公共资产在 N02/N08 分别检查自身的 Quality=2、Resolution=101。输入 Cube 保留其源网格。显示参数不代表科学收敛。

本教程的源值比较容差：坐标 **3×10^-6 Å**、FCHK 标量能量 **6×10^-7 Eh**、Log 打印能量 **10^-9 Eh**、Cube 公式值 **3×10^-6**（源字段单位）。这些容差仅用于相应样本与比较对象；保存和改变显示时仍需保持科学数组摘要一致。

### C01 FCHK、开壳层轨道与密度

**输入与目标：** 使用 `P01/o2-uhf.fchk` 及其逐字节 `.fch` 别名，验证波函数导入、开壳层轨道选择、密度、体积雾与裁剪。两份文件的 SHA-256 均为 `ef562c4b210e7c380219282d7684370cca1f0e8349dffa1d4388af5831472e36`。

| 核对项 | 本例预期 |
| --- | --- |
| 原子与坐标 | O1/O2，坐标 `(0,0,−0.6)` / `(0,0,+0.6) Å` |
| 计算条件 | UHF/STO-3G，中性三重态，16 电子，Alpha 9 / Beta 7 |
| 电子总能量 | `−147.633453 Eh` |
| 轨道 | 每个自旋通道 10 个 MO；本例固定选择 Alpha 9、Beta 7 |
| 场生成参数 | Grid spacing `0.2 Å`，Grid margin `3 Å`，Memory budget `512 MiB` |

1. **导入并核对来源。** 按 0.3 分别导入 FCHK 和 FCH，选择各自原子对象，查看来源与科学记录。核对原子源编号、顺序、坐标、方法、基组、电荷、多重度、电子数和能量；两入口应一致。

2. **生成 Alpha 与 Beta 轨道。** 选 FCHK 原子对象，点击 **N 侧栏 → QCBlender → 工作流 → 生成量子化学场**。Quantity 选 **Molecular orbital**，Spin 选 **Alpha**，Orbital 选 **Source number**，Orbital number (1-based) 填 **9**。记录预览中的 Source MO、occupation、Energy，输入上表网格参数后确认。重新选择原子对象，以 **Beta / Source number / 7** 再生成一次。

   本样本 Alpha 8/9、Beta 6/7 分别能量简并；选择自动 **HOMO** 时，预览分别为 Alpha 8、Beta 6。另试 HOMO/LUMO 时按预览源编号记录；固定本例成图仍使用 Alpha 9、Beta 7。

3. **检查轨道正负相与显示参数。** 选 MO 场，在 **对象属性 → 科学记录与振动模式** 核对量、单位、自旋通道和源轨道编号。在 **几何表示** 将阈值设为 **0.045 bohr^-3/2**，逐一关闭、恢复正相和负相；取消 **Link Thresholds** 后单独改变负阈值，确认两相能独立调整，再恢复联动。依次切换实面、线框和点表示。到 **材质属性** 修改两相颜色和透明度，在 **材质预览** 中观察。正负相表示轨道相位。

4. **生成四种密度。** 每次重新选择原始 FCHK 原子对象，依次生成 **Electron density、Alpha density、Beta density、Spin density**，均使用上表相同网格。选择各场，核对量名、`electron/bohr^3` 单位和网格；自旋密度阈值可设 **0.002**。数值核对采用同网格源数组：总密度 = Alpha + Beta，自旋密度 = Alpha − Beta。图形只能用于检查显示，不能代替这两项数值比较。

5. **检查体积雾的可见性。** 选自旋场，点击 **创建视图与检查工具 → 创建体积雾**，再选新雾视图。逐项改变颜色、**Opacity Range、Opacity Scale、Display Threshold** 和材质不透明度曲线。将 **Opacity Scale** 设为 **0**，雾应消失；恢复 **40**，雾应重新出现。把不透明度渐变设为全黑，雾应消失；恢复黑白渐变，雾应出现。在 **Display Layers** 复制雾层，把副本 Opacity Scale 设为 0，原层保持 40，确认二者独立。

6. **检查裁剪。** 选择场或原子视图，点击 **添加裁剪控件**，在 **空间观察** 分别开启、调整和关闭平面裁剪、盒裁剪。预期只改变可见区域；关闭后恢复完整显示，科学源数组不变。

7. **保存并重新打开。** 按 0.4 分别渲染轨道及四种密度，保存自包含工程，完成原位置、移动位置和归档解包后的冷重开。重新检查轨道身份、单位、阈值、雾层和裁剪状态。节点参数复核对应 N01/N02/N04/N05/N09/N10。

**需留存结果：** 来源与生成参数截图；两相、透明度、雾层及裁剪的操作前后截图；四密度数值比较记录；`C01.png`、`C01-mo.png`、`C01-total.png`、`C01-alpha.png`、`C01-beta.png`、`C01-spin.png`；`C01.blend + C01.qcdata/` 及冷重开记录。密度单独保存时使用 `C01-density.blend + C01-density.qcdata/`。

### C02 Log/Out 能量、振动与优化

**输入与目标：** 使用 `P02/water_neutral_nbo_opt_freq.out` 及逐字节 `.log` 别名，验证计算段选择、能量记录、振动播放、优化步进和再次导入。两扩展名都需完成导入；后续 FCHK 导入使用 `P03/water-dimer.fchk`。

| 核对项 | 本例预期 |
| --- | --- |
| Job 2 | 中性单重态水，O/H/H，RHF/STO-3G，10 电子 |
| 目标电子能量 | `−74.9659011806 Eh` |
| 模式 1 / 2 / 3 频率 | `2169.7613 / 4141.3837 / 4392.5759 cm^-1` |
| 模式 1 / 2 / 3 IR 强度 | `7.2483 / 44.2724 / 29.9428 km/mol` |
| Job 1 优化能量，步 1 → 4 | `−74.9643287914`、`−74.9649723283`、`−74.9659003010`、`−74.9659011806 Eh` |

1. **选择频率计算段。** 按 0.3 导入 Out，选择 **Job 2**。选中新原子对象，展开 **对象属性 → 科学记录与振动模式**，逐项查看能量记录。核对 Hartree 值、方法、kind/role 和原文位置；分别记录参考 SCF、目标方法能量、ZPE 与热校正。再导入 Log 别名的 Job 2，核对记录一致。

2. **播放振动。** 选择 **模式 3**，核对源编号、频率和 IR 强度。在 **高级参数** 勾选 **Animate**，设 **Amplitude = 0.35 Å、Cycles per second = 1**，在 Timeline 播放，确认帧号实际推进后暂停。改变 Phase，切到模式 1、模式 2 重复观察；在 **几何表示 → Show Displacement Vectors** 开启位移箭头。平衡坐标应保持不变，振幅与播放速度属于展示参数。

3. **导出 IR 数据。** 保持含振动模式的原子对象活动，按 0.5 选择 **Data = IR**，导出 CSV 和 metadata。逐行核对三组频率、强度和源编号。IR 数据通过科学记录和导出表检查。

4. **创建优化轨迹。** 再次点击 **导入 Gaussian / Cube / XYZ**，在新文件对话框中选同一日志的 **Job 1**。导入后选原子对象，点击 **创建视图与检查工具 → 创建优化轨迹视图**。选择新轨迹对象，展开 **对象属性 → Optimization Trajectory**，使用 **Previous、Next、Choose Step** 遍历 4 步，核对每步构型、能量、步号、终止状态、收敛值与阈值、原文行范围。能量缺失或歧义按界面状态记录；优化步不代表物理时间。

5. **验证独立轨迹。** 在 **Display Layers** 复制优化轨迹，把原层和副本切到不同步。分别选中两层核对步号与构型，原层不应随副本改变。轨迹应使用对应步骤的性质，不借用最终电荷、偶极或振动模式。按 C05 的随步标注练习检查距离与角度同步；共享 mesh 的拒绝与恢复按 P1-B 操作。

6. **验证动态数据的外部分析限制。** 选择含优化轨迹的对象，包括初始步，展开 **导入外部结果**，检查适用入口提示使用独立静态文件。外部分析需要的参考构型应从该步对应的独立 Log/FCHK/Cube 导入。

7. **检查再次导入的计算段。** 在当前工程中再次导入 Log，明确选择 **Job 2** 并完成。然后重新点击 **导入 Gaussian / Cube / XYZ** 打开新文件对话框，选 **P03/water-dimer.fchk**。预期计算段参数从 1 开始；导入成功后为 6 原子，SHA-256 为 `02ffc555ac7bda6e263e8461481914db3a2576582f71b6b9ea97fa05df610d6a`，来源属于该 FCHK。

8. **导出、保存并重开。** 按 0.5 导出 **Data = optimization** 的 CSV 和 metadata；按 0.4 对实际振动与优化原子视图创建相机、渲染并保存工程，完成三种位置的冷重开。重开后复核能量、模式、轨迹步号与导出数据。节点参数复核对应 N12/N15/N16。

**需留存结果：** `C02-energy`、`C02-vibration`、`C02-optimization`、`C02-reimport` 截图；振动播放与不同优化步记录；IR 和 optimization 的 CSV/metadata；`C02.png`、`C02.blend + C02.qcdata/` 及冷重开记录。

### C03 Cube/cub 物理量、网格与双符号

**输入与目标：** 使用 `P03/color.cube` 与逐字节别名 `P03/igmh/sl2r.cub` 验证导入、物理量声明和双符号显示；再用 `P03/igmh/dg_inter.cub` 验证独立几何场着色。

| 核对项 | 本例预期 |
| --- | --- |
| color.cube / sl2r.cub SHA-256 | `18a33c308c868c9f7747128f1a23c04fc69df37fd5b9681aa5dd35ef20997958` |
| 原子和网格 | 6 原子，`91×38×156` |
| 网格原点 | `(−1.2877770840,−0.5291772105,−0.5291772105) Å` |
| 三轴步长 | `0.02874808114 Å` |
| 着色场量与值域 | `sign_lambda2_rho`，`−194.599..+0.295371 electron/bohr^3`，倍率 1 |
| dg_inter.cub SHA-256 | `daf5a7e79c7dcc67b244f3dc1d2d314795c9f318c931e4f25d36e72ea168a28e` |
| 几何场量与值域 | `delta_g_inter`，`1.01735e-10..0.0185476 electron/bohr^4` |

1. **导入两个扩展名。** 按 0.3 分别导入 color.cube、sl2r.cub，选择各自场对象，核对原子、网格原点、轴步长、形状和数值范围。普通 Cube 初始量名/单位可能为 **unknown_scalar / unknown**。

2. **声明物理量。** 选待声明场，点击 **对象属性主面板 → 声明 Cube 物理量与单位**。选择 **Other externally computed scalar field**，Physical quantity 填 **sign_lambda2_rho**，Unit 填 **electron/bohr^3**。对另一扩展名重复。声明应保留源数值，倍率为 1；来源无法确定的其他输入保留 unknown，并记录原始定义。

3. **调整双符号表面。** 在 **对象属性 → QCBlender · 对象与量子化学 → 几何表示** 将正值阈值设 **0.03 electron/bohr^3**；取消 **Link Thresholds**，把出现的负值阈值设 **0.01**。分别关闭、恢复 **显示正值** 和 **显示负值**，确认蓝色正值与红色负值可以单独显示。依次选择 **实面、线框、点**，最后恢复实面。

4. **检查两相透明度。** 到 **材质属性 → QCBlender · 节点材质**，将 **Positive Opacity / Negative Opacity** 分别设 **0.6 / 0.3**。切换 **材质预览** 观察两相透明度，再对别名场重复相同设置，核对结果一致。

5. **导入独立几何场。** 导入 dg_inter.cub，声明 **delta_g_inter / electron/bohr^4**，正值阈值设 **0.005**，只显示正值。核对其网格、原子身份与着色场相匹配。

6. **绑定与替换着色场。** 保持新几何场活动，打开 **颜色映射 → 选择／替换着色场**，选 color.cube。确认来源摘要、`sign_lambda2_rho / electron/bohr^3`，Color minimum/maximum 填 **−0.05 / 0.05**。预期表面位置由 delta_g_inter 决定，颜色来自 sign_lambda2_rho。在 **N 侧栏 → Display Layers** 隐藏独立着色表面的视口与渲染，保留内部体场，只显示一份原子。再次选择／替换着色场，改选 sl2r.cub 别名，范围和图例位置应保留。

7. **核对输入定义并保存。** 本例使用上表物理量和倍率。若另验 NCIPLOT 样本，按其真实记录核对倍率与 RDG 过滤哨兵；普通 RDG 不解释为 IGMH 或 IRI。按 0.4 保存双符号与映射后的图像、自包含工程，并完成三种位置的冷重开。节点参数复核对应 N04–N07。

**需留存结果：** 两扩展名导入与量/单位声明截图；双符号、阈值、样式和透明度前后截图；两个场的来源与映射参数；`C03.png`、`C03.blend + C03.qcdata/` 及冷重开记录。

### C04 ESP、电荷、偶极、切片、探针与剖面

**输入与目标：** 使用 `P03/water-dimer.fchk`，验证密度表面按 ESP 着色、原子电荷、偶极、切片、取点、剖面和源关联。SHA-256 为 `02ffc555ac7bda6e263e8461481914db3a2576582f71b6b9ea97fa05df610d6a`；源关联使用逐字节别名 `P03/water-dimer.fch`。

| 核对项 | 本例预期 |
| --- | --- |
| 构型与计算条件 | 6 原子 `[O,H,H,O,H,H]`，中性单重态，20 电子，RHF/6-31G(d) |
| 电子能量 | `−152.013820 Eh` |
| Mulliken 电荷，原子 1 / 2 / 4 | `−0.928340742 / +0.461442520 / −0.920221916 e` |
| 源偶极向量 | 约 `(0,0,1.67243888) e·bohr`；界面以 Debye 显示 |
| 两场生成参数 | Grid spacing `0.2 Å`，Grid margin `3 Å`，Memory budget `512 MiB` |
| 密度等值面 / ESP 色域 | `0.004 electron/bohr^3` / `−0.05, 0, +0.05 hartree/e` |

1. **生成密度和 ESP。** 导入 FCHK，选原子对象，点击 **N 侧栏 → QCBlender → 工作流 → 生成量子化学场**，Quantity 选 **Electron density**，按表填网格参数并生成。重新选择原子对象，以同样参数生成 **Electrostatic potential**。核对实际网格、密度 `electron/bohr^3`、ESP `hartree/e` 和有效掩码；无效点不能作为物理零。

2. **将 ESP 映射到密度表面。** 选择密度表面，在 **几何表示** 设置等值 **0.004 electron/bohr^3**。打开 **对象属性 → 颜色映射 → 选择／替换着色场**，选择 ESP，核对所选场的来源摘要、计算段、量与单位后确认。预期密度决定几何、ESP 决定颜色。隐藏独立 ESP 表面的视口与渲染，保留其内部体场。

3. **设置色域与图例。** 将 **Color Minimum、Color Center、Color Maximum** 分别设 **−0.05、0、+0.05**，三值须严格递增。在 **图例排版** 开启 **显示图例（Show Legend）**，依次调整长宽、字号、小数、方向、旋转和位置。可用长度 **2.6**、宽度 **0.25**、字号 **0.2**（本地布局单位）、小数 **3**、竖向排列、旋转 **(0,0,0.3) rad**、位置 **(3.5,0,0)**。点击 **零中心对称**，输入 **R=0.05**；再点 **读取有效范围**，记录读数后恢复本例色域。

4. **检查色带与撤销。** 在 **材质属性 → QCBlender · 节点材质**，把 Color map 中间停靠点从 **0.5** 改为 **0.4**，将 **Reverse (0 or 1)** 从 **0** 改为 **1**。表面与图例颜色方向应同时反转。使用 **编辑 → 撤销 / 重做** 检查恢复，最终把中点恢复为 0.5、Reverse 恢复为 0。范围外使用端点颜色，无效采样显示洋红；根据本次实际掩码核对。

5. **检查多选映射入口。** 选择密度表面，点击 **创建视图与检查工具 → 创建当前版本视图**，使用新建、尚未绑定色场的标准密度层。临时显示独立 ESP 表面，取消其他选择，在 Outliner 先选 ESP，再按 Shift 选新密度表面，使密度表面活动，确认只选两个对象。在 **3D Viewport → Object → QCBlender → Map Selected Field to Active Surface** 打开映射，也可在视口按 F3 搜索同名操作。填色域 **−0.05 / +0.05** 并确认。已有着色的视图应拒绝重复添加；改用 **选择／替换着色场**，检查替换后范围与图例位置保留。恢复独立 ESP 表面隐藏。

6. **显示原子电荷与偶极。** 选原始原子对象，在 **科学记录与振动模式 → 设置原子电荷着色** 选择 **Mulliken**，核对表中电荷。已绑定网格着色时使用独立原子层。改变 **Charge Maximum** 至 **0.5 e**，源电荷应保持不变。点击 **创建视图与检查工具 → 创建偶极矢量**，核对源三分量及 Debye 换算记录；将 **Angstrom per Debye** 从 **0.5** 改为 **1.5**，预期只改箭头长度，方向与源向量不变。

7. **创建与调整切片。** 选 ESP 场，点击 **创建切片**，再选新切片。在 **空间观察** 设置中心 **(0,0,1.45) Å**，调整 Rotation、Width、Height，可用 **6×6 Å**。在 **几何表示** 检查 **显示采样数/轴（Resolution）**：新切片初值为 **201/轴**，即 **40,401** 个显示采样点；源场网格间距仍为 0.2 Å。已有工程按其保存值核对。

8. **检查定平面与等值线。** 点击 **按源网格或三个原子定平面**，依次试 **Grid ij、Grid jk、Grid ki**；再选 **Three source atoms**，Associated atom view 选水二聚体原子对象，First/Second/Third source atom 填 **2/1/4**。这三个源原子非共线。使用视口工具栏 **QC Slice Gizmo** 平移、旋转并调整宽度，核对平面记录。在 **切片等值线** 开启等值线，ESP 切片选 **几何场**；先把阈值列表留空，检查自动 9 条，再填 **−0.02,0,0.02 hartree/e** 并点 **更新等值线**，等待曲线与标签更新。无效单元不应连线。

9. **读取游标处场值。** 选 ESP 场，在 **3D Viewport → N → View → 3D Cursor** 依次输入 **(0,0,1.45)**、**(0,0,0)**、**(20,20,20) Å**，每次点击 **创建视图与检查工具 → 读取游标处场值**。最后一点应在域外；核附近 `(0,0,0)` 是否无效取决于实际网格掩码。若它仍有效，记录实际读数；未找到真实无效点时，“无效域读数”记 Not Run。无效与域外均不能记作物理零。

10. **检查交互探针。** 在 ESP 视图点击 **点击探针 · 几何场**，在表面点击预览，按 **Enter** 保存取点结果；再次取点后按 **Escape**，应恢复进入探针前的记录。选已绑定 ESP 的密度表面，使用 **点击探针 · 绑定色场**，点击后按 Enter 保存。分别核对采样位置、场身份、量/单位和数值。

11. **采样线剖面。** 选 ESP 场或切片，把游标设为 **(0,−2,1.45) Å**，点击 **记录剖面起点**。保持同一活动视图与绑定，把游标设为 **(0,+2,1.45) Å**，点击 **采样线剖面数据**，Sample field 选 **Geometry**，Samples 设 **101**。绑定色场的视图可再选择 **Color** 采样。选择新建的 **QC line profile data** 记录，按 0.5 以 **Data = profile** 导出 CSV/metadata，核对 **101 行、距离 0..4 Å、端点坐标、量/单位、valid 和无效值空白**，以及 metadata 中的源网格和绑定。每次结果为数据快照，记录对象在视口中没有可见图形，通过记录面板与 CSV 查看。

12. **关联同构型数据源。** 导入 water-dimer.fch。在视口或 Outliner 先选新 FCH 原子对象，再 Shift 选原 FCHK 原子对象，使 FCHK 成为活动参考。点击 **Properties → Object → QCBlender · 对象与量子化学 → 关联选中数据源**。不勾 **Align rigid rotation/translation**，保持 **Maximum atom deviation (angstrom) = 0.001 Å**；数值框若显示 `0.00`，双击查看完整精度。确认后应提示 **Atom order and geometry matched; each source retains its own properties**。两源数据集、理论层次和能量记录分别保留。其他输入如需刚体配准须另行核对；线性或单中心构型不能自动得到唯一配准。

13. **成图、保存并复导出。** 密度/ESP 表面与分子可从正面取景，将图例旋转设为 **X=90°、Y=0°、Z≈17.19°**，使量与单位朝向相机。自由切片从顶面取景，更新等值线后渲染；相机 Margin 可用切片 **0.15**、其他空间视图 **0.05**。按 0.4 保存并完成三种位置的冷重开，再次导出 CSV 比较。节点参数复核对应 N06–N11/N17。

**需留存结果：** 当前网格与场生成参数、色域/图例/色带、电荷与偶极、切片/等值线、探针和关联操作截图；`C04.png`、`C04-esp.png`、`C04-charge.png`、`C04-dipole.png`、`C04-slice.png`；剖面记录与 CSV/metadata；`C04.blend + C04.qcdata/` 及冷重开、复导出比较记录。

### C05 氢显隐、局部选择、标注与显示层

**输入与目标：** 静态操作使用 `P03/water-dimer.fchk`，验证氢筛选、局部集合、源原子标注和显示层独立性；随优化步更新使用 C02 的 P02 Job 1，IRC 随步检查在 C10 完成。

| 核对项 | 本例预期 |
| --- | --- |
| 氢源编号 / 保留的氢 | `2,3,5,6` / `2` |
| 氧源编号 | `1,4` |
| 编号标注 | 原子 1 |
| 距离 `1,4` | `2.900 Å` |
| 角度 `2,1,3` | `112.7698904°`，三位小数显示 `112.770°` |
| 二面角 `2,1,4,5` | `0.000°`，采用 B→C 约定 |

1. **验证氢筛选。** 导入 FCHK，选原子对象，在 **对象属性 → 局部选择与标注** 点击 **隐藏氢**，预期只剩氧 1、4。点击 **保留指定氢**，填源编号 **2**，预期显示 1、2、4；点击 **显示全部氢** 恢复 6 原子。使用 **编辑 → 撤销 / 重做** 核对对应状态。

2. **验证局部集合运算。** 点击 **设置局部选择**，在 **Source atom numbers (1-based)** 填 **1,4**、Mode 选 **替换（Replace）**。然后依次输入 **2 + 并集（Union）**，预期集合为 1,2,4；**1,2 + 交集（Intersect）**，预期为 1,2；**2 + 差值（Difference）**，预期为 1；最后选 **反转（Invert）**，预期为 2–6。

3. **验证距离邻域。** 再次设置局部选择：**Replace、编号 1**，勾选 **Include distance neighborhood**，Radius 设 **1.0 Å**，勾选 **Include seed atoms**。预期为 1、2、3。局部集合与元素、连续编号、氢筛选共同作用。点击 **清除局部限制**，应恢复到其他筛选控制的范围。

4. **创建独立局部层。** 保持原子对象活动，点击 **创建视图与检查工具 → 创建局部显示层**，输入 **1,4**，在新层独立调整样式与材质，核对原层不变。优化或 IRC 的局部集合按源编号保留，切步后如需重新按距离筛选，点击 **按当前步重新计算**。IRC 在原层做选择，不创建局部副本。

5. **创建四种标注。** 恢复完整 6 原子，选择 P03 原子层，在 **N 侧栏 → QCBlender → 创建视图与检查工具** 依次点击 **创建编号标注、创建距离标注、创建角度标注、创建二面角标注**。也可在 **对象属性 → 局部选择与标注 → Source Atom Annotations** 使用 **Atoms、Distance、Angle、Dihedral**。按表中顺序填源编号，设 **Decimal places=3**，核对值与单位。二面角范围为 **(−180°,180°]**；退化构型应显示 **undefined** 及原因，使用真实样本时无需改动输入来制造退化。

6. **调整标注排版。** 在 **Source Atom Annotations** 使用设置图标改变文字大小、颜色、偏移、小数和引线。可使用球棍 **Atom Radius=0.35 Å、Bond Radius=0.12 Å、Quality=2**，文字 **Size=0.16、Color RGB=(0.03,0.03,0.03)、Decimal places=3、Leader width=0.008**，勾选 **Show leader** 与可见。下表为不遮挡主要构型的一组 Offset（局部 Å）；创建相机后点击 **Face All to Camera**。

   | 标注 | 源编号 | Offset X / Y / Z |
   | --- | --- | --- |
   | 编号 | 1 | −1.2 / −0.5 / −0.6 |
   | 距离 | 1,4 | 1.2 / −0.5 / 0.9 |
   | 角度 | 2,1,3 | 1.2 / −0.5 / −0.35 |
   | 二面角 | 2,1,4,5 | 0.8207 / −0.5 / −0.25215 |

   测量取自原子源构型或当前轨迹步。临时将父对象缩放改为 **(2,0.5,1.5)**，核对科学距离、角度及源数组不变后恢复 **(1,1,1)**；振动显示位移也不改变测量值。

7. **检查标注随优化步更新。** 选 C02/P02 Job 1 的优化轨迹副本，创建距离 **1,2**、角度 **2,1,3** 标注，小数设 3。在 **Optimization Trajectory → Choose Step** 依次选 1、2、3、4，核对文字中的 **Optimization Step**、测量值、锚点与引线同步。第 1 步预期 **0.990 Å、106.000°**，第 4 步预期 **0.989 Å、100.037°**；原层保持原步号。取景可从 **+X** 观察 YZ 平面，文字 Size 用 **0.14**，距离 Offset 用 **(0.3,−0.6,0.95)**，角度用 **(0.3,−0.6,−0.65)**。

8. **验证显示层副本与显隐。** 在 **N 侧栏 → Display Layers** 选择层，用复制图标创建独立副本，改变副本参数和材质，确认原层不变。上移、下移副本，核对排序。分别切换视口与渲染显隐；隐藏原子层时，所属标注与引线应一同隐藏，恢复后应重新出现。

9. **检查当前版本视图。** 仅选 P02 第 4 步优化标注层，点击 **创建视图与检查工具 → 创建当前版本视图**。新层应保留第 4 步及两项标注，原层仍在。遍历新层四步并调整标注、材质，核对原层不变。

10. **复制显示参数。** 多选同类层，最后选参数源，使其成为活动对象。在 **3D Viewport → Object 顶部菜单或对象右键菜单 → QCBlender → 复制显示参数到选中视图** 选择类别。数值设置要求量、单位和电荷方法兼容；不兼容时取消数值类别。检查几何表示与外观复制结果，以及目标位置、选择、裁剪、图例布局仍保留。

11. **移除临时副本。** 仅选刚创建的临时独立副本，点击 **Display Layers → 移除**。预期副本及所属标注消失，原层和科学源数据保留。列表中下一层会自动激活并显示；如该层之前隐藏，使用其视口显隐图标恢复原状态。

12. **分别成图并保存。** 依次显示完整 6 原子、氧 1/4 局部层、完整 6 原子加四项标注，保存三张图。可使用 **Eevee、1920×1080、Standard**，白色世界背景，Strength=0.7；正交相机位置 **(1.4,−12,1.45) Å**，Euler 旋转 **(90°,0°,0°)**，Orthographic Scale=8.7。两盏 Area 灯可设 Disk、Size=5，位置 **(4,−5,7)** 与 **(−4,−5,5)**，Power=800/600 W，朝向 **(0,0,1.45)**。按 0.4 保存自包含工程并完成三种位置冷重开，复核筛选、标注、步号、显示层和渲染。节点参数复核对应 N01–N03/N15/N16。

**需留存结果：** 氢筛选、集合运算、距离邻域、四种标注、优化随步更新与显示层操作前后截图；`C05.png`、`C05-selection.png`、`C05-annotations.png`；`C05.blend + C05.qcdata/` 及冷重开记录。

### C06 NBO 与 E(2)

**输入与目标：** 使用 P02 的 `water_neutral_nbo_opt_freq.out`，选择 **Job2 / block1**，查看 7 条 NBO 和 2 条 E(2) 记录。P02 原件需按 0.1.1 合法取得并核对 SHA-256；公开样本包不含该原件。NBO 编号与 MO 编号分别核对。

1. 按 0.3 导入 P02 的 **Job2**，只选择该段的原子对象。在 **3D 视图 → N 侧栏 → QCBlender → 导入外部结果 → NBO 记录** 打开对话框。
2. **Gaussian Log / Out** 选择同一 `.out` 文件，填 **Gaussian job (1-based)=2、NBO block within job (1-based)=1**，点击确定。预期生成关联到 Job2 原子对象的 NBO 记录对象；本例不用 Job1 优化轨迹作为关联构型。
3. 选择生成的记录对象，打开 **Properties → 对象属性 → QCBlender · 对象与量子化学 → NBO Records**。分别把 **NBO row (1-based)**、**E(2) row (1-based)** 从 1 改为 2，核对下表及原文行。行号以完整原文件为准，显示时可省略行末空白。

   | 记录 | 应看到的源数据 |
   | --- | --- |
   | NBO 1 | O1–H2 的 BD；occupancy **1.99933**；energy **−0.77653 Eh**；原文行 **1444** |
   | NBO 2 | O1–H3 的 BD |
   | E(2) 1 | donor **1** → acceptor **7**；**0.59 kcal/mol**；原文行 **1434** |
   | E(2) 2 | donor **2** → acceptor **6**；**0.59 kcal/mol** |

4. 打开同一对象的 **External Result Browser**，设 **Orbital type=BD、Orbital order=Occupancy, high to low、E(2) order=E(2), high to low**，点击 **应用筛选**。预期显示 **2 条轨道、2 条 E(2)**。再按源编号、占据范围、供受体编号和 E(2) 范围检查筛选；每次修改后都点击应用，并与源表核对。筛选只影响显示，最后恢复全部类型、默认范围和源顺序。
5. 在自己的 `inputs` 中建立同字节的 `water_neutral_nbo_opt_freq.log` 副本，核对两文件 SHA-256 相同，再按步骤 1–2 导入 Job2 / block1。预期新增记录对象，原 `.out` 记录保留，两者摘要及记录一致。在 3D 视图执行 **Edit（编辑）→ 撤销**，新增对象应消失；执行 **Edit（编辑）→ 重做**，对象及原子父对象关联应恢复。
6. 按 0.4 保存 **C06.blend + C06.qcdata**。将两行索引恢复为 1，调整 3D 视图与属性编辑器宽度，截图同时记录关联水分子、7 条 NBO / 2 条 E(2)、单位和源行。需要分子效果图时只选参考原子，使用 **创建视图与检查工具 → 创建取景相机**，可设 **Margin=0.05、EEVEE、1920×1080**；表记录以面板截图留存。按 0.4 完成原路径、移动副本和解包副本的重新打开检查，复核记录与关联。

### C07 IGMH、IRI 成对场与数据导出

**输入与目标：** P03 水二聚体，6 原子，片段 **1–3 / 4–6**。使用 Multiwfn **2026.9.20** 生成的成对场，网格均为 **91×38×156**，每场 **539,448** 个原始体素。导入时声明量、单位与参数，检查三维表面、颜色来源及完整 CSV 数据。

| 分析 | Geometry Cube / 单位 | sign(lambda2)rho Cube / 单位 | 样本参数与原始值域 |
| --- | --- | --- | --- |
| IGMH | `P03/igmh/dg_inter.cub`；**electron/bohr^4** | `P03/igmh/sl2r.cub`；**electron/bohr^3** | component **inter**；几何值域 **1.01735e-10..0.0185476** |
| IRI | `P03/iri/func2.cub`；**a.u. (electron^-0.1 bohr^-0.7)** | `P03/iri/func1.cub`；**electron/bohr^3** | **a=1.1**；几何值域 **0.0593502..11.432** |

两组颜色场的原始值域均为 **−194.599..+0.295371 electron/bohr^3**。原值不除以 100；显示色域截断不改变数据。

1. 按 0.3 导入 `P03/water-dimer.fchk`。只选择生成的参考原子对象，在 **N 侧栏 → QCBlender → 导入外部结果 → IGMH / IRI 成对场** 打开对话框。
2. 先选 **Analysis=IGMH**，按上表填写两个文件与单位，填 **Color minimum=−0.04、Color maximum=0.04、IGMH component=inter、Fragment atoms (JSON)=[[1,2,3],[4,5,6]]、Declaration source (optional)=P03 Multiwfn fragment setup**，点击确定。预期生成 **QC delta_g** 几何场、颜色源与 **QC paired field data** 数据记录对象。

   选几何场或 paired 记录，在 **对象属性 → QCBlender · 对象与量子化学 → IGMH 来源声明** 核对 inter、两组片段、声明来源及 **user_assigned**。这些是使用者依据源计算作出的声明，导入不会重新计算 IGMH。片段按源 Cube 的 1 基原子顺序填写：可覆盖部分原子；片段内重复、越界或非整数应拒绝；跨片段交叠应保留并提示。未声明分量显示 **unknown/unverified**。
3. 重新只选择同一参考原子，打开相同入口，选 **Analysis=IRI**，按上表填写两文件与单位，填 **IRI density exponent a=1.1**，色域仍用 **−0.04..0.04**，确认。预期生成 **QC iri_function**、颜色源及对应 paired 数据记录。核对两输入的原子、网格、来源摘要和单位；本样本每组全量有效体素均为 **539,448**。
4. 选择 **QC delta_g**，在 **对象属性 → QCBlender · 对象与量子化学 → 几何表示** 设 **Isovalue=0.005**；选择 **QC iri_function** 设 **Isovalue=1.0**。在各对象的 **颜色映射** 设 **Color Minimum=−0.04、Color Center=0、Color Maximum=0.04**。按 N14 核对位置来自 Geometry 场、颜色来自独立 sign(lambda2)rho 场。

   分别只显示参考原子与当前几何场，按 0.4 创建取景相机，可用 **Margin=0.05、EEVEE、1920×1080**。在 **图例排版** 勾选 **Show Legend**，让量名、单位和 **−0.04 / 0 / +0.04** 可读。若视角绕 X 轴 **0.9 rad**，将 **Legend Rotation** 的 X 角也设为 **0.9 rad（约 51.566°）**；输入前确认角度字段单位。
5. 选择 IGMH 的 **QC paired field data**，在 **对象属性 → QCBlender → External Result Browser** 核对 **X=sign_lambda2_rho [electron/bohr^3]、Y=delta_g [electron/bohr^4]**。启用四个范围开关，填 **X from=−0.04、X to=0.04、Y from=0.001、Y to=0.02**，点击 **Apply Filter**。按 0.5 选择 **Data=paired、Rows=Current filter** 导出 CSV 与 metadata，核对源索引、范围、单位与实际行数；本样本参考行数为 **36,391**。

   勾选 **Swap value columns**，先保持四个数值不变，再应用、另行导出。范围现在作用于交换后的量列，需记录实际行数（参考 **28,630**）。随后同步交换 X / Y 的范围再导出，应与最初筛选保留同一体素集合。IRI 可用颜色范围 **−0.04..0.04**、IRI 范围 **0.1..2** 检查同样流程，参考行数为 **12,736**；这些行数均需以本轮 CSV 核实。

   再分别导出 **Rows=All source records**，核对每组 **539,448** 个有效体素及原索引。全量导出逐个写出有效体素。metadata 中的 **scientific_metadata** 应保留 IGMH 分量与片段声明。
6. 重新只选择 P03 参考原子，打开成对场导入，选 **IGMH**，Geometry 填 `P03/igmh/dg_inter.cub`，Color 故意选 `P05/nocv/nocv-pair1.cub`，单位照 IGMH 填写。预期拒绝并提示 **Atom identities/order differ; an explicit atom mapping is required**，既有对象与绑定保留。此输入检查的是原子身份不匹配。

   恢复正确文件再导入一次，执行 **Edit → 撤销**，新增的五个配对对象应消失；执行 **Edit → 重做**，对象与科学绑定应恢复。只保留需要显示的一组，避免重叠。
7. 按 0.4 分别保留 IGMH、IRI 三维表面和可读图例，按 0.5 保留全量、筛选及交换列后的 CSV + metadata，保存 **C07.blend + C07.qcdata**。在原路径、移动副本及解包副本重新打开后，复核表面绑定、来源声明与再次导出的体素集合。paired 记录通过表面和 CSV 检查，paired 数据的筛选结果在 CSV 中核对。

### C08 ESP 极值与面积分布

**输入与目标：** 使用 P03 在 **rho=0.001 electron/bohr^3** 表面上的外部 ESP 分析。应有 **4 个最大值、3 个最小值**；PDB 的 B-factor 表示 **ESP [kcal/mol]**，坐标为 **Å**，C/O 分别编码 maximum/minimum。源面积分布有 **40 个 bin**，合计 **73.1833 Å²**。

1. 打开 C04 工程，按 0.4 另存为 C08。只选 **QC electron_number_density** 密度表面，在 **对象属性 → QCBlender · 对象与量子化学 → 几何表示** 将 **Isovalue** 从 **0.004** 改为 **0.001 electron/bohr^3**，保留前后画面。然后只选实际 ESP 场 **QC electrostatic_potential**，打开 **N 侧栏 → QCBlender → 导入外部结果 → ESP 表面分析**；导入参考应为实际 ESP 场。
2. 填 **Extrema PDB=P03/esp/surfanalysis.pdb、Area distribution text=P03/esp/stdout.log、Surface definition=rho=0.001 electron/bohr^3、Extrema value unit=kcal/mol、Distribution center unit=kcal/mol、Area unit=angstrom^2**，确认。预期生成 **QC ESP maximum、QC ESP minimum、QC ESP area distribution**，均关联到所选 ESP 场。单位与 PDB REMARK、原表声明逐项核对。

   原 `stdout.log` 含非 UTF-8 的进度或横幅字节，核对时保留原始字节与 SHA-256，按其中的 ASCII 科学表行读取。面积直接来自源表；当前 **0.2 Å** 生成网格只作为三维显示参照。
3. 选择 **QC ESP maximum**，打开 **对象属性 → QCBlender · 对象与量子化学 → External Analysis Records**，将 **Record (1-based)** 从 1 改为 2。再选择 **QC ESP minimum** 查看两条记录，按下表核对。

   | 类型 / 源编号 | ESP [kcal/mol] | 位置 [Å] |
   | --- | --- | --- |
   | maximum 1 | **36.69** | **(−1.740,−0.051,1.026)** |
   | maximum 2 | **57.80** | **(−1.682,−0.042,4.031)** |
   | minimum 1 | **−25.50** | **(−0.036,−1.400,1.768)** |
   | minimum 2 | **−50.68** | **(−0.005,−0.058,−1.769)** |

4. 在 maximum 对象的 **External Result Browser** 设 **Source number=0**（全部），启用 **ESP value [kcal/mol]** 的两个范围开关，填 **从=40、到=60**，勾选 **Show source label、Show matching points**，设 **Match (1-based)=1**，点击 **应用筛选**。预期匹配 **2 条最大值（源 2 / 3）**，突出源 2，显示 **maximum 2 | 57.8 kcal/mol**。再设 **Source number=2**，应只保留该源点。查看最小值时切换到 minimum 对象。
5. 选择 **QC ESP area distribution**，打开 **External Result Browser**，依次检查下表，每次改动后点击 **应用筛选**，按 0.5 以 **Data=ESP_AREA、Rows=Current filter** 单独导出 CSV + metadata。

   | Area bin selection | 范围 [kcal/mol] | 预期结果 |
   | --- | --- | --- |
   | **Center in range** | **0..20** | 4 个 bin，中心 **2.5 / 7.5 / 12.5 / 17.5**；**displayed=14.4784 Å²、Source percentages shown=19.7838%** |
   | **Recorded interval overlaps range** | **0..20** | 6 个完整源 bin，含与 0、20 相接的边界区间；**displayed=21.2676 Å²、Source percentages shown=29.0608%** |

   区间模式保留完整 bin，不按相交长度拆分；总面积保持 **73.1833 Å²**，源百分比不重新归一化。取消范围恢复 **40 个 bin**，以 **Rows=All source records** 再导出，核对中心、边界、面积与 percent；原表打印百分比之和为 **100.0002%**（舍入）。面积记录以属性与 CSV 查看，不生成柱图。
6. 按 0.4 保存三维极值图 **C08-extrema.png**、面积属性截图与所有 CSV + metadata。极值层恢复 **Source number=0、Match=2** 并应用，面积恢复全部 40 个 bin。取景包含真实极值点和关联分子，可用 **Margin=0.05、EEVEE、1920×1080**；标签绕 X **90°**。重叠点可旋转视角检查，源坐标应保持不变。

   需要增强可读性时可添加 Sun，设 **Energy=2、Angle=0.35 rad（约 20.054°）**，旋转 **X=40.107°、Y=−17.189°、Z=−22.918°**；标签材质使用白色 **Base Color / Emission Color、Emission Strength=1**。保存前再次应用极值筛选并确认标签可见。
7. 使用 **N 侧栏 → QCBlender → 工程与诊断 → 保存自包含工程** 保存 **C08.blend + C08.qcdata**，按 0.4 归档与重新打开检查。在原路径、移动副本和解包副本分别核对极值坐标、单位、面积源表、筛选状态及再次导出的 CSV。

### C09 AIM 临界点、路径与属性

**输入与目标：** P03 水二聚体，6 原子。临界点源编号 **1–6 为 C/(3,−3)**，**7–11 为 N/(3,−1)**，共 **11 条**；本样本没有 O/F 层。路径共 **10 条、408 点**。属性单位以 `CPprop.txt` 原文为准。

1. 导入 `P03/water-dimer.fchk`，只选择原子对象，保持 **Object Mode**。打开 **N 侧栏 → QCBlender → 导入外部结果 → AIM 拓扑**，填 **CPs PDB=P03/aim/CPs.pdb、Paths PDB=P03/aim/paths.pdb、CP properties text (optional)=P03/aim/CPprop.txt**，点击确定。预期生成 **QC AIM CP C、QC AIM CP N、QC AIM bond paths**，父级关联参考原子，来源保留三份输入摘要。属性文件虽为可选，本例应填写。
2. 选择 **QC AIM CP C**，打开 **对象属性 → QCBlender · 对象与量子化学 → External Analysis Records**。首次导入即可查看 **Record (1-based)=1**：源点 **1**、**C/(3,−3)**、对应核 **6(H)**、PDB 位置 **(−0.724,0,3.384) Å**、**Density of all electrons=0.4316646446**。改为记录 **2**：对应核 **5(H)**、位置 **(0.724,0,3.384) Å**、密度相同。属性文本中更高精度的 Bohr / Å 坐标与 PDB 的打印精度分别核对；源编号不随排序改变。
3. 选择 **QC AIM bond paths**，在对象属性的 **External Result Browser** 核对 **10 recorded AIM paths**。设 **Path (1-based)=1** 应显示 **Source residue 1 | 9 points**；设为 **2** 应显示 **Source residue 2 | 47 points**。使用原生对象与曲线控件调整路径显隐、线宽。路径组编号与临界点源编号分别核对。
4. 选择 **QC AIM CP C**，打开 **External Result Browser**，设 **Source number=0、Numeric CP property=Density of all electrons**。启用 **Selected CP property value** 的两个范围开关，填 **从=0.432、到=0.433**，勾选 **Show source label、Show matching points**，保留首条匹配并点击 **应用筛选**。预期匹配源 **4、5**，位置分别为 **(−0.724,0,0.484)、(0.724,0,0.484) Å**；突出源 4，标签值 **0.432922**。若失焦后只显示两位小数，重新激活输入框核对完整数值。

   切换到 **QC AIM CP N**，同一属性键设范围 **0..0.02** 并应用。预期只匹配源 **9**，位置 **(0,0,1.451) Å**、密度 **0.01088848625**，标签以六位有效数字显示 **0.0108885**。分别开关 **Show matching points / Show source label**，点与标签应独立显隐。**Source number** 指源编号，**Record / Match (1-based)** 指相应列表位置；取消范围、恢复 Source number=0 并应用，应恢复全部点，原属性不变。
5. 按 0.4 保存点图、路径图与总览：点图只显示参考原子、筛选出的 C4/5 与 N9 及标签；路径图只显示参考原子和完整路径；总览显示二者。核点可能被原子球遮挡，O–H 路径也可能与显示键投影重叠；旋转观察或临时隐藏参考原子检查，之后恢复。

   可用 **EEVEE、1920×1080、正交相机 Scale=9、位置 (1,−12,1.65)、绕 X 轴 90°**。标签字号 **0.11**、绕 X **90°**、局部 Y 偏移 **−0.6**；C 标签局部 Z 偏移 **−1.05**，N 标签 **0.15**。照明与白色发光标签可沿用 C08，另加能量 **0.35** 的 Sun。这些参数只改变显示。
6. 保存 **C09.blend + C09.qcdata**，按 0.4 归档并在原路径、移动副本及解包副本重新打开，核对源属性、标签、筛选和全部路径；每次正常关闭后再打开下一份。

### C10 真实 IRC 步序、能量与随步标注

**输入与目标：** P04 的 H2O2，原子顺序 **[O,O,H,H]**，RHF/STO-3G，中性单重态，18 电子。源为 geomeTRIC **1.1.1** 的双向 IRC，共 61 个接受帧；本例只使用 0 基编号 **29 / 30(TS) / 31**，对应 CSV 步号 **1 / 2 / 3**。TS 唯一虚频 **−48.1434547807 cm^-1**、最大梯度 **1.893862e-8 Eh/bohr**。三步接近 TS，需通过坐标与数值检查微小变化。

1. 新建工程，保留 `P04/steps.csv` 与 `step-001.fchk`、`step-002.fchk`、`step-003.fchk` 的相对位置。CSV 为 UTF-8，表头 **step,fchk**，步号从 1 连续。在自己的 `inputs/P04/` 中复制为 `checks-duplicate.csv`，将第二条数据的步号改成 **1**，其余路径保持不变。

   打开 **N 侧栏 → QCBlender → 工作流 → 导入 IRC 路径**，在 **CSV manifest: step,fchk** 选择此副本并确认。预期提示 **Step numbers must be explicit, unique and contiguous from 1**，场景不新增 IRC 对象。记录错误，保留原 `steps.csv`。
2. 同一入口选择完整 `P04/steps.csv` 并确认。选择生成的 **IRC path** 根原子，在 **对象属性 → QCBlender → IRC Path** 核对 **Step 1/3、Energy: −148.7648840000 hartree**。源原子 **1/2/3/4** 对应固定 `qc_atom_id` **0/1/2/3**。按 0.5 以 **Data=IRC** 导出三步记录，核对步号、能量与来源；新建结果通过面板和 CSV 查看能量。
3. 保持根原子活动，在 **对象属性 → 几何表示** 设球棍 **Style=0、Atom Radius=0.25、Bond Radius=0.07**。按 C05 的 **N 侧栏 → QCBlender → 创建视图与检查工具**，依次创建距离、角度、二面角标注；源编号分别填 **1,2**、**3,1,2**、**3,1,2,4**，小数位 **6**、字号 **0.14**，保留引线。

   可将三标签偏移分别设为 **(1.7,−0.4,−0.9)、(1.7,−0.4,−0.2)、(1.7,−0.4,0.8)**，颜色 **(1,0.8,0.2,1)**，绕 X **90°**；也可通过 C05 的设置图标与 **Face All to Camera** 调整可读位置。
4. 选择 **IRC path**，在 **IRC Path** 面板点击 **Next → Next → Previous**，走 **1→2→3→2**。逐步核对原子身份、坐标、面板能量与标签中的 **IRC Step**，数值与下表一致。测量值由源坐标计算。

   | 步号 | FCHK 打印能量 [Eh] | 距离 1,2 [Å] | 角 3,1,2 [°] | 二面角 3,1,2,4 [°] |
   | --- | --- | --- | --- | --- |
   | 1 | **−148.764884** | **1.401927844** | **99.818649** | **171.760508** |
   | 2（TS） | **−148.764883** | **1.401928051** | **99.818565** | **−179.999999984** |
   | 3 | **−148.764884** | **1.401927844** | **99.818650** | **−171.760508** |

   第二步的二面角以六位小数显示 **−180.000000°**。
5. 步 3 再点 **Next**，步 1 再点 **Previous**，均应提示 **IRC step is outside the imported path**，步号、几何与标注保留。回到步 2，只选根原子，点击 **N 侧栏 → QCBlender → 创建视图与检查工具 → 创建当前版本视图**。预期拒绝并提示 **Creating a current-version IRC view cannot preserve the full path; keep the current view**，完整原路径保留。IRC 局部选择使用原层固定源编号；切步后如需按当前几何重新选择，应重新计算集合。
6. 按 0.4 为三步保存分子与三种标注的效果图，并按 0.5 保存 **IRC CSV + metadata**，源能量单位为 hartree。可用 **EEVEE、1920×1080、Standard、正交相机 (2.8,−20,0)、绕 X 90°、Scale=11**。标签黄色材质 **Emission Strength=1**；世界背景 **(0.12,0.12,0.12)、Strength=0.8**；两盏 Sun 的能量 **2 / 0.35**、角宽 **0.35 rad**、Euler XYZ 旋转分别 **(0.7,−0.3,−0.4) / (−0.4,0.4,2.5) rad**。
7. 保存 **C10.blend + C10.qcdata**，按 0.4 归档和重新打开检查。原路径、移动副本和解包副本分别重放 **1→2→3→2**，核对三步数据、标注和再次导出的 CSV。C11 从这份尚未导入 Mayer 表的工程继续，另存结果。

### C11 IRC 逐步 Mayer 键级

**输入与目标：** 承接 C10 的三步 H2O2，每步有六对 Mayer 键级，单位 **dimensionless**。源结果由同构型 **PySCF 2.13.1** 的收敛 RHF/STO-3G AO 密度与重叠矩阵计算；文本使用 Multiwfn 兼容语法，producer 为 PySCF。距离推断的显示键与 Mayer 键级分别核对。

| 原子对 | 步 1 | 步 2 | 步 3 |
| --- | --- | --- | --- |
| **1,2** | **0.987331413844** | **0.987349305673** | **0.987331413844** |
| **1,3** | **0.950875651565** | **0.950844120525** | **0.950875651565** |

1. 打开已保存且 **尚无 Mayer 表** 的 C10 工程。保持 `P04/mayer-pyscf.csv` 与 `step-001-mayer-pyscf.txt`、`step-002-mayer-pyscf.txt`、`step-003-mayer-pyscf.txt` 的相对位置。在自己的 `inputs/P04/` 中复制清单为 `checks-missing-mayer.csv`，删除 step3 数据行，保存为 UTF-8。

   只选 **IRC path** 根原子，打开 **对象属性 → QCBlender · 对象与量子化学 → IRC Path → Import Mayer Results**，在 **CSV manifest: step,mayer_output** 选择缺步副本并确认。预期提示 **Mayer step count differs from the IRC path**，不新增 Mayer 表与数据，当前步号保留。此检查应在尚未导入 Mayer 的工程进行。
2. 同一入口选择完整 `P04/mayer-pyscf.csv` 并确认。预期新增并选中 **QC IRC Mayer orders** 子表，在 **对象属性 → IRC Path** 设 **Atom A=1、Atom B=2**，点击 **Read Pair**。C10 停在步 2 时应显示 **Step 2/3、Mayer order: 0.987349**。完整数值与上表和源文本核对；结果通过面板与 CSV 查看。
3. 保持子表活动，将 B 改为 **3**、A 保持 **1**，点击 **Read Pair**。步 2 应显示 **Mayer order: 0.950844**。按 0.5 选 **Data=Mayer** 导出三步的全部六对记录，核对上表两对的完整数值、单位和摘要。**Read Pair** 选择只影响面板读取，不裁减导出数组。
4. 保持表活动，用 **Previous / Next** 走 **2→1→2→3→2**，逐步核对根构型、能量、当前对的 Mayer 值与 C10 三种标注。把 **B=2** 后点击 Read Pair，再重放一次；完成后恢复 **B=3、Read Pair、步 2**。
5. 将 B 临时设为 **999** 并点击 **Read Pair**，预期提示 **Selected atom pair is absent from Mayer results**，原数组和步号保留；恢复 B=3 并读取。再选 **IRC path** 根原子导入同一完整 CSV，预期提示 **This IRC path already has a Mayer import**，不新增重复子表。按 0.5 检查取消导出，已有结果应完整保留。
6. 沿用 C10 的构图与照明，按 0.4 保存实际分子和标注效果图，截图记录 Read Pair 面板，保留 **Mayer CSV + metadata**。标注 **Visible / show_leader** 会在切步时重新应用；若为出图临时改过对象渲染开关，切步后再次核对当前图的可见对象。
7. 保存 **C11.blend + C11.qcdata**，按 0.4 归档并在原路径、移动副本、解包副本重新打开。每处逐步读取 **1,2** 和 **1,3** 两对，核对源构型、能量与标注，再次导出并核对三步六对的完整源值。

### C12 ETS-NOCV 真实结果表

**输入与目标：** `P05/complex.fchk` 为 CO–BH3，六原子 **[C,O,B,H,H,H]**，22 电子，中性单重态，RB3LYP/6-31G(d)，源能量 **−139.947332 Eh**。`P05/nocv/ets-nocv.txt` 声明 **24 pair、48 orbital**，阈值 **1e−3** 下实际打印 **11 行**；插件展示这些源行。该结果为整体 KS 矩阵重构的 **Multiwfn 近似**，方法不是 F_TS 过渡态方法。来源与许可见样本清单和 NOTICE。

| pair / Spin | 轨道编号 | 特征值 | Pair energy [kcal/mol] | 原文行 |
| --- | --- | --- | --- | --- |
| **1 / Total** | **1 / 48** | **+0.54550 / −0.54550** | **−57.02** | **7** |
| **2 / Total** | **2 / 47** | **+0.33615 / −0.33615** | **−11.91** | **8** |

Pair energy 与两个轨道各自的 energy 是不同字段，核对时保留字段身份。

1. 新建工程，使用 **N 侧栏 → QCBlender → 工作流 → 导入 Gaussian / Cube / XYZ** 导入 `P05/complex.fchk`。只选择根原子对象，打开 **导入外部结果 → ETS-NOCV 表**，填 **ETS-NOCV output text=P05/nocv/ets-nocv.txt、Pair energy unit=kcal/mol**，点击确定。预期新增 **QC ETS-NOCV pairs** 子表，根对象仍为活动对象。
2. 在 **N 侧栏 → Display Layers** 点击 **QC ETS-NOCV pairs** 行左侧选择箭头，或在 Outliner 选中该子表。打开 **对象属性 → QCBlender · 对象与量子化学 → External Analysis Records**，以 **Record (1-based)=1 / 2** 分别核对上表、两个轨道的能量及源行；再逐条核对全部 **11 行**。在 **来源详情** 查看摘要。关联标记 **user_assigned** 表示使用者将表分配给参考构型，导入未重新计算 ETS-NOCV。
3. 在表对象的 **External Result Browser** 设 **Pair number=1、Spin=总数（Total）**，关闭全部范围开关并点击 **应用筛选**。预期 **Matching records: 1**，对应 pair1 / 行7。再设 **Pair number=0**（全部）、**Spin=Total、Eigenvalue=Negative orbital**，启用本征值两范围，填 **从=−0.6、到=−0.5** 后应用，仍应只匹配 pair1。本征值保留源符号。
4. 关闭两本征值与两 pair 能量范围，设 **Pair=0、Spin=Total、排序=Positive eigenvalue**，应用后应有 **11 条**，顺序为 **11,10,9,8,6,7,5,4,2,3,1**；首条 **pair11、positive_eigenvalue=0.00147、source_line=17**。相同值按 pair 顺序稳定排列。

   分别检查以下边界，每次改动后应用：pair 能量范围 **−60..−50 kcal/mol** 只匹配 pair1；**pair999** 或 **Alpha / Beta** 筛选为空；倒置范围应拒绝。通过导入对话框将声明能量单位改成与源文件不符的单位，应拒绝并保留原记录。完成后恢复 **Pair1、Spin=Total、范围关闭、排序=Pair、Record1**。

   筛选改变匹配记录与显示顺序；存在唯一关联 pair 场时可定位该场。本阶段尚未导入 pair Cube，筛选不会生成密度场；缺失源字段按缺失核对。
5. 按 0.4 渲染关联的六原子根分子，用属性面板截图保存表记录。需要图内说明时，可用 Blender **Add → Text** 手动排版，明确标为源记录说明并保留单位、原文行、打印范围和来源；表对象本身没有可渲染网格。

   可用 **EEVEE、1920×1080、Standard、正交相机 (1.1,−20,0.1)、绕 X 90°、Scale=12**。根显示位置 **X=−3、绕 Z 45°**；文字放在 **Y=−1** 朝向相机，默认 Font、字号 **0.15–0.33**，浅黄色、**Emission Strength=1**。照明沿用 C10 两盏 Sun，世界背景 **0.06 灰、Strength=0.8**。这些设置只改变显示变换。
6. 保存 **C12.blend + C12.qcdata**，按 0.4 归档和重新打开检查。在原路径、移动副本、解包副本分别核对 **11 条源记录**、构型与表的来源关联、筛选参数和效果图。C13 从此工程继续并另存。

### C13 NOCV pair Cube 与两符号密度

**输入与目标：** 承接 C12，使用 `P05/nocv/nocv-pair1.cub`，**Pair 1 / Total**。网格 **47×50×57**，**133,950** 个值，值域 **−0.243093..+0.0494892 electron/bohr^3**，SHA-256 为 `d6d3ec263d5173261791f997eabd78b8112f6685abc3bd851c70deec86a82e33`。正负表示形变密度的符号；参考构型和单位由使用者依据源计算明确指定。

1. 打开已保存的 **C12.blend**，最后另存 C13。只选择 **QC ETS-NOCV pairs** 表对象，在 **N 侧栏 → QCBlender → 导入外部结果 → NOCV pair Cube** 打开对话框，填 **Signed pair Cube=P05/nocv/nocv-pair1.cub、Pair number=1、Spin=总数（Total）、Deformation density unit=electron/bohr^3**，点击确定并等待完成。预期新增并选中 **QC nocv_deformation_density** 场和配套体积源，表与六原子根保留。
2. 保持新场活动，在 **对象属性 → QCBlender · 对象与量子化学** 核对网格与单位；点击 **来源详情**，核对 **Geometry / data source** 的 Cube 摘要与 **Geometry field** 的量名、单位和 Spin。选择 ETS 表，按 C12 查看 **Record=1** 的 Pair1 / Total / 源行7；在 **External Result Browser** 设 Pair1 / Total 并应用，应定位已有的唯一 pair 场。分别记录 Cube、表和参考构型摘要。六原子源顺序为 **[C,O,B,H,H,H]**；Cube 源坐标使用 bohr，界面几何坐标使用 Å。
3. 在场对象的 **几何表示** 设 **正值阈值 [electron/bohr^3]=0.003**，勾选 **Link Thresholds**。分别勾选 **显示正值 / 显示负值**：实体模式下默认蓝色为正、红色为负；同时打开应显示两符号密度，同时关闭只剩根分子。分别保存 **C13-positive.png、C13-negative.png**。
4. 恢复两符号显示，取消 **Link Thresholds**，设正值阈值 **0.004**、负值阈值 **0.006**，单独改变其中一个并检查另一侧保持。分别切换 **样式=实面 / 线框 / 点**，线框或点半径只影响展示。

   在 **Properties → 材质属性 → QCBlender · 节点材质** 设 **Positive Opacity=0.35、Negative Opacity=0.65**，观察两侧透明度独立变化。这些控件控制已链接的 Alpha。完成后恢复 **实面、Link Thresholds、两阈值 0.003、两 Opacity=1**。
5. 重新只选择 **QC ETS-NOCV pairs** 表对象，使用同一导入入口与 Cube，设 **Pair number=999、Spin=Total** 并确认。预期提示 **Selected pair and spin do not identify one ETS-NOCV table row**，不新增场，现有科学数据保留。再用 **Pair number=1、Spin=Alpha** 检查同一拒绝。记录实际错误后取消对话框，重新选择合法的 Pair1 / Total 场。
6. 按 N16 检查显示层复制：活动 pair 场，在 **N 侧栏 → Display Layers → 复制** 创建副本，只将副本正值阈值改为 **0.009**，原场应保持 **0.003**。执行 **Edit → 撤销 / 重做**，核对副本状态、阈值、独立的 Mesh / 节点树 / 材质与源绑定；只移除本次临时显示副本，源数据保留。
7. 按 0.4 保存两符号总览 **C13-overview.png**。可沿用 C12 的根显示变换 **X=−3、Z 旋转 45°**，用正交相机 **(−3,−20,0.65)、X 旋转 90°、Scale=11**，**EEVEE、1920×1080、Standard**，照明沿用 C12，隐藏手动说明文字。构图应完整包围两符号密度。
8. 保存 **C13.blend + C13.qcdata**，按 0.4 归档和重新打开检查。原路径、移动副本、解包副本分别核对 **Pair / Spin / 表关联**、体积数据、显示控件及重新渲染的正值、负值、透明度和总览效果；每份关闭后再打开下一份。

### X01 标准XYZ与离散帧

**输入与目标：** 使用样本包中的 `P06/water-dimer.xyz`（单帧，6 原子）与 `P06/p04-three-frames.xyz`（三帧，每帧 4 原子），来源及 CC BY 4.0 归属见 [SOURCES](SOURCES.md)，SHA-256 按样本清单核对。坐标单位为 **Å**；多帧必须保持原子数与元素顺序。XYZ 的帧号和注释只表示源帧身份，文件自身不提供能量、波函数或正常模式。

1. 新建工程，打开 **N 侧栏 → QCBlender → 工作流 → 导入 Gaussian / Cube / XYZ**，选择 `P06/water-dimer.xyz`。选新原子对象，按 0.3 核对 **O/H/H/O/H/H** 六原子、Å 坐标、UTF-8 原注释、源摘要与固定原子 ID。显示连接为距离推断，新建外层 **Quality=3**；改变显示参数应保留源坐标。
2. 再导入 `P06/p04-three-frames.xyz`，选择其四原子对象，展开 **Properties → 对象属性 → QCBlender → XYZ Frames**，核对 **Frame 1/3**、原注释和 **Source lines**。点击 **Next → Next → Previous**，走 **1→2→3→2**；核对 **O/O/H/H** 顺序和 ID 保持，坐标来自当前源帧。点击 **Choose XYZ Frame**，输入 **2** 并确认，再次核对来源。多帧 XYZ 以离散帧查看，不提供插值或 Timeline 播放。
3. 按 C05 为多帧根建立距离 **1,2**、角 **3,1,2**、二面角 **3,1,2,4** 标注。切帧时核对标签中的 **XYZ Frame**、测量值、锚点与引线同步；这些构型与 P04 同源 FCHK 对应，可使用 C10 的逐步测量表核对。帧 2 距离显示约 **1.401928 Å**、二面角约 **−180°**。

   在帧 1 点 Previous、帧 3 点 Next 检查端点拒绝。若检查非法文件，只编辑独立输入副本：未知或 dummy 元素、额外列、截断、NaN / Inf，以及含 **Properties / Lattice / PBC** 声明的扩展 XYZ 均应明确失败，合法视图保留。
4. 在 **N 侧栏 → 显示层 → 复制** 创建独立副本，并检查 **创建当前版本视图**。原层停在帧 2，让副本切到另一帧；检查原层帧号与参数保持，Mesh、节点、材质与标注分别独立。局部选择继续使用固定源 ID，切帧不重编号。改变副本参数并执行 **Edit → 撤销 / 重做**，原层和源数组应保持。
5. 按 C04 步骤 12 的选择顺序与 0.001 Å 容差，将单帧 `water-dimer.xyz` 关联到同原子顺序、同构型的 `P03/water-dimer.fchk`（FCHK 最后选中作为活动参考），核对关联来源与真实 FCHK 构型。再以多帧 XYZ 尝试科学来源关联，应明确拒绝，已有对象及绑定保留；当前显示帧不构成独立静态科学参考。
6. 按 0.4 保存构型与标注效果图及 **X01.blend + X01.qcdata**。正常退出后重新打开，核对两个来源、多帧数据、当前帧、注释、原子 ID 与独立副本。再按 0.4 检查中文移动目录和 ZIP 解包副本，确认帧选择与随帧标注仍可操作。

## 2. N01–N18 节点与交互检查

本节接着各 C 案例检查参数、节点和保存恢复。每项记录活动对象、实际入口、参数原值与新值、预期与实际结果；已有对应 C 案例的操作记录可直接引用。

开始节点练习前保存工程。在 **N 侧栏 → QCBlender → 显示层 → 复制** 建立测试副本，仅选副本为活动对象。切换 **Geometry Nodes** 工作区，取消节点编辑器图钉，选择副本的 Geometry Nodes 修改器/节点组。记录原接线，保留原节点；新增节点和改线只在副本进行。修改器输入与对象属性共享参数，修改公共资产内部节点会影响其使用者，因此本节只操作资产的外部输入和接线。

在 **Asset Browser → QCBlender Nodes** 可查找九个公共资产。实际添加时，在几何节点编辑器的 **添加** 菜单中按下文目录选择资产，再单击空白处放置。新节点连入视图、参数改变并出现预期结果后，才记录该项结果。内部绑定 Dataset 的节点由对应视图提供。

节点较多时，可按外层 Frame 查找：原子 **Atoms: selection and representation**；振动 **Modes: displacement and animation**；等值面 **Field: source and isosurface**；映射 **Scalar: sampling and colors**；电荷 **Charge: attributes and colors**；图例 **Legend: range and labels**；切片 **Slice: plane placement**。

### N01 QC Select Atoms：元素与源编号选择

1. 使用 C05 的 **P03 水二聚体原子副本**。在 **对象属性 → QCBlender → 局部选择与标注** 点击 **清除局部限制**，并点击 **显示全部氢**；在 **几何表示** 恢复 **Element=0、First Atom=1、Last Atom=0、选中项勾选**。应显示源编号 1–6，O/H/H/O/H/H；标注可暂时隐藏。
2. 在副本节点树选择 **添加 → 原子选择 → QC Select Atoms**。接着完成 N02 的表示节点接线，使本节点的 **Selection → 表示节点 Selection**。源原子编号从 1 开始，`Last Atom=0` 表示不限制末尾。
3. 在新选择节点设 **Selection 开启、Element=8、First=1、Last=0**，应只显示氧 1、4；关闭 Selection，应无原子显示。重新开启，设 **Element=0、First=2、Last=3**，应只显示氢 2、3。
4. 设 **Element=8、First=1、Last=3**，应只保留氧 1；再把 First 改为 2，应为空。元素与编号范围取交集。逐一核对源编号，筛选不得重编号或改动源坐标，已有标注仍引用源构型。
5. 恢复 **Selection 开启、Element=0、First=1、Last=0**。将原显示分支临时接回组输出，使用对象属性中的同名控件按上述组合检查一次并恢复；然后接回新公共分支。保留副本供 N02、N09 使用。

### N02 QC Style Atoms and Bonds：原子与键表示

1. 保持 N01 副本活动，选择 **添加 → 表示 → 原子与键 → QC Style Atoms and Bonds**。将 **组输入 Geometry → 新表示节点 Geometry**、**N01 Selection → 新表示节点 Selection**，为 **Material** 选择副本已有的元素材质。最后将 **新表示节点 Geometry → 组输出 Geometry**，替换旧显示输出。
2. 全选六个原子，在新节点将 **Style (0 ball-stick, 1 space-fill, 2 bonds)** 依次设为 **0、1、2**。应分别出现球棍、空间填充和键线；全原子键线应有两个水分子的四条 O–H 键。键由距离推断，不能作为键级结论。
3. 在 N01 设 **Element=8**，只保留氧 1、4。空间填充应有两个氧球；键线应为空，因为两氧相距 **2.900 Å**，没有推断键。随后恢复全原子。
4. 设 **Style=2、Bond Radius=0.07 Å**，将半径改为 **0.12 Å**，键应变粗；设 **Style=0、Atom Radius=0.25 Å**，改为 **0.35 Å**，原子球应变大。源坐标、源编号及原显示层不变。临时接回原显示分支后，对象属性 **几何表示 → 样式** 的球棍/空间填充/键线也按此检查；完成后恢复参数并接回新公共分支。
5. 将测试分支恢复 **Style=0、Atom Radius=0.25 Å、Bond Radius=0.07 Å、VDW Scale=1**；其他已修改参数按记录恢复。继续 N09，或将原输出连线接回。

### N03 氢显隐

1. 选 C05 的 P03 原子副本，清除局部限制，恢复全元素与全编号范围。在 **对象属性 → QCBlender → 局部选择与标注** 点击 **隐藏氢**，应只显示氧 **1、4**。
2. 点击 **保留指定氢**，输入源编号 **2** 并确认，应显示氧 1、4 和氢 2；源氢 3、5、6 隐藏。点击 **显示全部氢**，应恢复全部六个原子。
3. 对一次氢显隐操作执行 N16 的撤销/重做，逐一核对源编号及原显示层。完成后恢复显示全部氢及原来的局部选择。

### N04 QC Style Isosurface / QC Surface Representation：符号与表面样式

1. 使用 C13 的 **P05 Pair 1 / Total 变形密度场副本**。在副本节点树中，通过 **添加 → 表示 → 表面** 分别添加 **QC Style Isosurface v3** 和 **QC Surface Representation**。
2. 找到指向该场 Volume 源的 **Object Info**，连接 **Object Info Geometry → 等值面 Volume → 等值面 Geometry → 表面表示 Geometry → 组输出 Geometry**。保留原节点，替换其输出连线。新等值面组 **Style=0**，由后接的表面表示节点控制样式。
3. 在等值面节点设 **Isovalue=0.003 electron/bohr³**，开启 **Positive Phase、Negative Phase**，分别选择副本已有的 **Positive Material、Negative Material**。依次关闭再开启两符号开关，核对相应区域消失及恢复。此处正负是变形密度的增加/减少；C01 的 MO 正负则是轨道相位。
4. 将表面表示 **Style (0 solid, 1 wire, 2 points)** 依次设为 **0、1、2**，应分别显示实体、线框、点。记录每种样式、阈值和单位；显示形式变化不得改变源场值。
5. 恢复 **Style=0** 和两个符号开关，或按原记录恢复；需要保留该分支时按 N18 打包保存。

### N05 正负等值与透明度独立调整

1. 另选 C13 的普通场显示副本，在 **对象属性 → QCBlender → 几何表示** 开启两个符号，记下阈值。关闭 **Link Thresholds**，设正阈值 **0.003**、负阈值幅度 **0.003 electron/bohr³**。
2. 只把正阈值改为 **0.004**，再恢复；只把负阈值幅度改为 **0.004**，再恢复。每次应仅相应符号的等值面改变，另一符号保持原阈值。
3. 打开 **材质属性 → QCBlender · 节点材质**，将 **Positive Opacity** 从原值改为 **0** 再恢复，再对 **Negative Opacity** 做相同操作。分别核对对应表面透明、另一表面保留。使用 Material Preview 或渲染检查透明度。
4. 恢复两透明度、阈值和 Link Thresholds 原值。记录量与单位；阈值和透明度只改变显示，源场数值不变。若在 N04 的独立分支操作，直接修改新节点上的对应输入并记录实际接线。

### N06 QC Sample Scalar Field：绑定色场采样

1. 复制 C04 的 **密度/ESP 映射视图**，仅选副本，在 **添加 → 数据 → 采样 → QC Sample Scalar Field** 放置新资产。
2. 找到绑定 ESP 源对象的 **Object Info**，连接其 **Geometry → 新采样节点 Volume**；连接 **Position → 新采样节点 Position**。再将新节点 **Value、Valid → 副本颜色映射节点的对应输入**，替换旧采样输入。密度等值面仍提供表面几何，ESP 提供颜色值。
3. 记录原效果后，暂时断开新采样节点的 Position 连线，依次输入 **(0,0,0)、(0,−2,0)、(0,−2,1.45) Å**。每个位置使表面使用同一采样值；按 N17 在相同源场和坐标读取数值，记录本批实际 ESP 值，单位 **hartree/e**。域外或掩码无效时，应传递无效状态。
4. 重新连接 **Position → Position**，应恢复表面逐点采样，副本几何、有效性及颜色恢复，原视图保持不变。C03 的同网格映射也按相同原则核对几何源与颜色源。

### N07 QC Map Scalar Colors v2：颜色与图例

1. 保持 N06 副本活动，通过 **添加 → 颜色映射 → QC Map Scalar Colors v2** 放置资产。连接 **密度等值面 Geometry → 新颜色节点 Geometry**、**N06 Value/Valid → 新颜色节点 Value/Valid**；Material 选择副本已有的映射材质。
2. 将新颜色节点输出接到旧颜色节点原来连接的 **Join Geometry（合并几何）** 输入，删除旧的这条连线，确保只有一份表面进入合并节点。记录原来三个色域输入的接线和图例状态。
3. 暂时关闭副本 **Show Legend**，断开新颜色节点三个色域输入，填 **Color Minimum=−0.05、Color Center=0、Color Maximum=0.05 hartree/e**；再将最大值改为 **0.1**。正值区的颜色映射应改变，负值区仍按 −0.05..0 映射，零保持中心；无效位置应显示洋红。色域必须满足最小值 < 中心 < 最大值。
4. 将三个色域输入接回 **组输入** 对应输出，将修改器色域恢复为 **−0.05/0/+0.05 hartree/e**，恢复图例。确认表面与图例的量名、单位、范围一致。
5. 在副本 **图例排版** 试设位置 **(−3,0,0)**、长度 **1.5**、宽度 **0.4**、字号 **0.15**；在材质控件调整一端色带颜色并恢复。应只影响副本，原视图的材质、色域和图例布局不变。完成后恢复所改布局或记录最终保留值。

### N08 QC Planar Slice：平面与采样数

1. 复制 C04 的 **ESP 切片层**。记下副本原 Center/Rotation/Width/Height/Resolution，再在 **空间观察** 设 **Center=(0,0,1.45) Å、Rotation=(0,0,0)**。
2. 在副本节点树选择 **添加 → 空间 → 切片 → QC Planar Slice**。将 **组输入 Center/Rotation → 新平面节点对应输入**，设 **Width=6 Å、Height=6 Å、Resolution=101**。新节点输出替换旧平面节点到颜色节点的几何连线，保留 ESP Volume/Position 采样及材质。
3. 将 **Resolution 101→51**。平面采样点数应由 **10,201→2,601**，范围仍为 X/Y **−3..3 Å**、Z **1.45 Å**，量与单位不变。需要核对等值线时，按 C04 在 **切片等值线 → 更新等值线** 重新生成，再检查曲线与有效区域。
4. 将 Width/Height/Resolution 接回组输入，恢复原平面参数。新建切片若原值为 **201/轴**，应恢复 **40,401** 个采样点；已有工程按其保存值恢复。
5. 按 C04 再检查 **按源网格或三个原子定平面** 与 **QC Slice Gizmo** 平移/旋转，记录实际平面和曲线变化，再恢复起始平面。源网格及原切片层应保持不变。

### N09 QC Clip Geometry：平面与盒裁剪

1. 使用 N01/N02 的 P03 全六原子副本，保持 **Style=0**。通过 **添加 → 空间 → 裁剪 → QC Clip Geometry** 放置资产，连接 **原子表示 Geometry → 裁剪 Geometry → 组输出 Geometry**，替换原先的直通输出。
2. **Plane Enabled、Box Enabled** 均关闭时，应与未裁剪视图相同。设 **Plane Origin=(0,0,1.45) Å、Plane Normal=(0,0,1)**；设 **Box Minimum=(−0.5,−2,−2) Å、Box Maximum=(0.5,2,5) Å**。法线无量纲，边界使用视图局部 Å 坐标。
3. 仅开启平面裁剪，应保留上方水分子源编号 **4、5、6**；再同时开启盒裁剪，应保留编号 **4** 的部分显示几何；关闭平面、仅保留盒裁剪，应保留氧 **1、4** 及相关的部分键几何。对照源编号和空间位置，原始原子/场数组应保持不变。
4. 关闭两个 Enabled，恢复全部分子显示。C01 的场可使用同一裁剪节点，按场几何另行记录边界与结果。保留公共分支时按 N18 完成打包、保存和冷重开。

### N10 QC Style Volume Fog：体积雾

1. 复制 C01 已创建的自旋雾，在副本节点树通过 **添加 → 表示 → 体积 → QC Style Volume Fog v1** 添加资产。连接 **指向自旋场的 Object Info Geometry → 公共组 Volume**、**公共组 Geometry → 组输出 Geometry**，Material 选择副本已有的雾材质。
2. 打开 **材质属性 → QCBlender · 节点材质**，记录色域、Display Threshold 和 Opacity Scale 原值。将 **Opacity Scale** 设为 **0**，渲染应无雾；设为 **40**，在有非零有效场值的区域应出现雾。Opacity Scale 是显示不透明度缩放。
3. 按 C01 使用的场单位调整颜色上下限，并将 **Display Threshold** 从 **0** 改为该场一个已知的非零有效幅值，记录对应区域变化；再恢复。确认正负色义、单位及源场绑定保持一致，原显示层不变。
4. 恢复全部原材质参数和必要接线，保留前后图像。该公共组负责赋材质，颜色、阈值和光学不透明度由雾材质控制。

### N11 QC Vector Glyph：偶极显示比例

1. 选 C04 的偶极对象 **QC dipole (Debye; physical direction)**，在 Geometry Nodes 修改器输入找到 **Angstrom per Debye**。同时在原子来源记录中核对偶极三分量、单位和坐标原点。
2. 将比例 **0.5→1.5 Å/Debye**，箭头长度应变为三倍；物理方向、三分量及源坐标原点保持不变。该节点组绑定当前偶极数据，由 **创建偶极矢量** 生成。
3. 恢复 **0.5 Å/Debye** 或记录的原值，核对箭头恢复。源偶极为零时应无非零长度箭头。

### N12 振动与 IR CSV

1. 选 C02 的 **P02 Job 2 频率原子对象**，打开 **对象属性 → QCBlender → 科学记录与振动模式**，依次选择模式 **1、2、3**，核对源编号、频率与 IR 强度。对应三频率为 **2169.7613、4141.3837、4392.5759 cm⁻¹**，强度为 **7.2483、44.2724、29.9428 km/mol**。
2. 记录原动画参数，在 **高级参数** 开启 **Animate**，设 **Amplitude=0.35 Å、Cycles per second=1**。在 Timeline 播放，确认实际帧号推进和分子振动，再暂停；换模式后复做。
3. 关闭 Animate 后改变 **Phase**，并在 **几何表示 → Show Displacement Vectors** 开启位移箭头，检查箭头与所选模式对应。振幅、相位和播放速度属于显示参数，源平衡坐标不变。
4. 按 0.5 选择 **Data=IR** 导出 CSV 与 metadata，逐行对照源日志的三频率和强度。完成后恢复模式、帧号、Animate、Amplitude、Phase、播放速度及箭头开关原值。

### N13 分析点、源标签与路径

1. 选 C08 的 **QC ESP maximum**，打开 **对象属性 → QCBlender → External Result Browser**。保持 **Source number=0**，开启 ESP 值的两个范围开关，设 **40..60 kcal/mol**，开启 **Show source label、Show matching points**，点击 **应用筛选**。
2. 应保留最大值源 **2、3**；**Match (1-based)=1** 应突出源 2，标签显示 **maximum 2 | 57.8 kcal/mol**。改变 Match、切换点与标签开关，核对位置和读数分别响应。Source number 是源编号，Record/Match 是列表位置。取消范围、恢复 Source number=0 并应用，恢复全部点。
3. 选 C09 的 **QC AIM CP C**，将 **Numeric CP property** 填为 **Density of all electrons**，范围设 **0.432..0.433**，应用后应保留源 **4、5**。选 **QC AIM CP N**，同一属性范围 **0..0.02** 应保留源 **9**，密度 **0.01088848625 electron/bohr³**。核对原始属性、坐标及标签，取消范围后恢复全部点。
4. 选 **QC AIM bond paths**，将 **Path (1-based)** 从 **1→2**，分别核对 **Source residue 1 | 9 points** 和 **Source residue 2 | 47 points**。用原生对象/曲线控件检查路径显隐与线宽，随后恢复原值；路径组编号与临界点源编号分别记录。

### N14 成对场全量与筛选 CSV

1. 选 C07 的 IGMH **QC paired field data**，在 **对象属性 → QCBlender → External Result Browser** 核对两列身份：**X=sign_lambda2_rho [electron/bohr³]、Y=delta_g [electron/bohr⁴]**。
2. 开启 X/Y 的四个范围，填 **X from=−0.04、X to=0.04、Y from=0.001、Y to=0.02**，点击 **Apply Filter**。按 0.5 设 **Data=paired、Rows=Current filter**，导出后核对所有匹配有效体素、原体素索引、列单位及 metadata 的筛选条件，记录实际行数。
3. 开启 **Swap value columns**，保持四个数值并重新应用/导出。范围应作用于交换后的量列，结果可能改变。随后同步交换 X/Y 范围再应用/导出，应与步骤 2 保留同一体素集合。
4. 对 C07 的 IRI 记录，使用 **sign_lambda2_rho=−0.04..0.04 electron/bohr³、IRI=0.1..2** 重复筛选与同步交换；IRI 的定义及单位按本批导入记录核对。
5. 分别导出 **Rows=All source records**。本教程对应原网格应有 **539,448** 个有效体素，核对完整有效体素与原索引。恢复未交换列和原筛选状态，并保存各次 CSV/metadata；移动冷重开后重新导出比较。

### N15 显示层独立性与参数复制

1. 在 C02 频率原子或 C05 静态原子工程中，选目标层，在 **N 侧栏 → QCBlender → 显示层 → 复制** 创建副本。将副本原子半径 **0.25→0.35 Å**，改变副本材质颜色和一个标注位置，分别检查原层的节点、材质、标注和参数保持原值。
2. 在显示层列表对副本执行排序、视口显隐、渲染显隐，再恢复；另建一个临时副本测试删除，核对原层和源数据保留。选原层，点击 **创建视图与检查工具 → 创建当前版本视图**，应新增一层并保留原层。
3. 多选同类层，最后选择参数源使其活动。在 **3D Viewport → 对象菜单或对象右键菜单 → QCBlender → 复制显示参数到选中视图** 选择所需类别并确认。核对所选参数被复制，而目标位置、局部选择、裁剪和图例布局保留。
4. 数值类别要求同物理量、同单位及适用的同电荷方法；不兼容时应明确拒绝且目标保留原状态。按 N16 撤销/重做一次复制操作，再恢复测试参数。源科学数组及摘要不得变化。IRC 层的复制与换步边界按 P1-B、C10 单独检查。

### N16 撤销与重做

1. 在 C01、C05、C06、C07–C13 中，每次选定一个明确操作，先记录活动对象、原参数/筛选/步骤、节点、标注和科学绑定；再执行该操作并记录变化后的状态。
2. 将鼠标移入 3D Viewport，使用顶部 **Edit（编辑）→ Undo（撤销）**，核对恢复操作前的对象、几何、节点、数据关联、标注与显示参数；再点 **Edit → Redo（重做）**，核对恢复操作后的状态。同一视口也可使用 **Ctrl+Z / Ctrl+Shift+Z**，记录实际入口。
3. 覆盖氢显隐、局部选择、显示参数复制、外部结果筛选及可操作的步进。C08 检查 ESP 源记录，C09 检查 AIM 源记录，C10 检查 IRC 当前步，C11 检查 Mayer 配对显示，C12 检查 ETS-NOCV Pair 筛选；P1-A/P1-B 的关联及共享 mesh 边界按专项步骤复做。
4. 最后选择需要保留的状态，再按 0.4 保存。若撤销或重做不一致，记录原错误、最短操作顺序和工程副本，保留该项 Failed。

### N17 游标、探针与采样线剖面

1. 选 C04 的 ESP 场，在 **3D Viewport → N → View → 3D Cursor** 依次设 **(0,0,1.45)、(0,0,0)、(20,20,20) Å**，每次点 **QCBlender → 创建视图与检查工具 → 读取游标处场值**。记录采样位置、量、单位及有效性。域外或无效值不得记为物理零；核附近是否无效由实际网格掩码决定，若仍有效则记录真实值，内部无效域项保持 Not Run。
2. 点 **点击探针 · 几何场**，在表面点击预览，按 **Enter** 保存；再次进入并取另一点，按 **Escape**，应恢复进入探针前的记录。选绑定 ESP 色场的密度表面，再用 **点击探针 · 绑定色场** 重复，确认采样的是 ESP，单位为 hartree/e。
3. 选 ESP 场或切片，将游标设为 **(0,−2,1.45) Å**，点 **记录剖面起点**；保持同一活动视图和绑定，将游标设为 **(0,+2,1.45) Å**，点 **采样线剖面数据**。设 **Sample field=Geometry、Samples=101**；若检查绑定色场，另行明确选择 **Color**。
4. 选新建的 **QC line profile data** 数据记录，按 0.5 设 **Data=profile** 导出。应有 **101 行、距离 0..4 Å**，端点、单位、valid 和源网格/绑定正确，无效值留空。该记录保存本次采样快照。保存、冷重开后重新导出，比较源值与 metadata。
5. 将游标和探针记录恢复到需要保留的状态，记录恢复动作；保留各采样记录与其导出文件的对应关系。

### N18 保存、移动、冷重开与恢复

1. 每例按 0.4 保存完整 **`.blend + .qcdata`**、输入与摘要。手动添加公共节点的工程先执行 **文件 → 外部数据 → 打包关联库**，再 **保存自包含工程** 和 **归档工程**。
2. 正常关闭并确认 Blender 进程退出，再以新进程依次检查原位置、中文/空格移动目录和 ZIP 解包目录；每处检查后关闭再开下一处。核对来源、单位、步骤/帧号、数组、体积、公共节点接口、接线、材质、标注和渲染；有 CSV 的重新导出比较。
3. 若显示缓存丢失，先复制工程与完整配套数据作为恢复副本，只打开此副本。选需要恢复的 **QC 标量场视图**，点击 **3D Viewport → N → QCBlender → 工程与诊断 → 重建显示缓存**，等待作业完成。核对原科学数组、来源、单位、体积绑定和显示结果；该操作需要已保存的科学数组。
4. 若同一 Dataset 目录已移动，保持对应 QC 场对象活动，点 **工程与诊断 → 重新定位数据**。在文件浏览器中进入保留的同一 Dataset 目录，选择 **manifest.json**；编辑文件名后按 Enter，再确认。应更新关联对象与体积路径，并保持科学身份和数组摘要一致。
5. 缺科学数组、不同 Dataset 的 manifest 或 Blender 无法读取的 VDB 应明确失败，保留原对象和绑定。记录完整路径、原生错误和日志；缺数组时恢复原配套数据，Windows 路径问题可用较短位置的完整工程副本重试。正常工程无需人为破坏数据。
6. 恢复完成后 **保存自包含工程** 另存，核对配套数据后正常关闭；在新进程重新打开并按步骤 2 复核。将保存、原位置冷重开、移动冷重开、解包冷重开及实际发生的恢复分别记录。

## 3. 结果记录与独立科研签署

### 3.1 操作证据与身份

把[记录模板](RECORD-TEMPLATE.md)复制到本批 `records/`，逐步填写活动对象、选择顺序、实际入口、参数前后、预期与实际、状态和证据文件。截图放在本批目录，能看清对象、控件和结果；数值检查同时保留原始记录或 CSV。每个案例注明实际操作者及身份。

### 3.2 独立使用者案例结果

按 C01–C13、X01、P1-A/P1-B、N01–N18 分别汇总。任何必需步骤失败，该例记 Failed；缺输入、未执行或无法判断的项目记 Not Run。每例分别填写保存、原地重开、移动重开、归档解包重开和适用导出结果。

科研核对至少包含以下内容：

| 检查 | 需要写下的内容 |
| --- | --- |
| 输入身份 | 摘要、生成程序/版本、方法/基组、电荷/多重度、计算段 |
| 原子与构型 | 元素顺序、源编号、坐标单位、步骤/帧号 |
| 数值与单位 | 原始记录位置、界面或 CSV 实测值、比较容差及结果 |
| 显示参数 | 等值、颜色范围、网格、振幅、筛选及前后变化 |
| 科研用途 | 图中颜色/符号的含义、已核对的具体用途、尚未验证的范围 |

若要用于自己的课题，再加入一个熟悉的真实计算案例，按同样步骤核对并说明适用范围。完整版本验收还需 **VMD/VESTA 同输入、同参数的外部视觉对照**：记录软件版本、输入摘要、量/单位、网格与等值、方向和配色，对照图及差异判断单独保存；条件未齐或未执行时记 Not Run。

### 3.3 最终签署

可以先签署已完成的专项范围，例如 P1-A 与 P1-B；在记录中明确列出已执行项和未覆盖项。A01–A09 全部通过且图片、参数摘要、自包含工程与中文移动重开证据齐全，可填写 Alpha 短验收。

完整验收需 **C01–C13、X01、P1-A/P1-B、N01–N18、0.5 导出检查及各例 0.4 保存重开均通过**，外部视觉对照完成，必要输入及许可记录齐全，缺陷在实际安装包上复验。再核对提供者交付的同批科学回归、离线安装、保存/移动冷读及安装包摘要记录。

在模板中填写操作者、日期、实际安装包与输入摘要、证据目录、科研适用性和剩余限制，由实际操作者与科研审阅者签名。参与开发者如实注明身份。完整版本的独立验收须由未参与开发的使用者复做；科研适用性由能够核对相应计算条件与物理含义的审阅者判断并签署。
