# QCBlender 安装与操作教程


## 目录

- [安装并找到插件](#install)
  - [1. 安装并启用 QCBlender](#step-01)
  - [2. 检查科学运行环境](#step-02)
  - [3. 准备新工程和操作界面](#step-03)
- [生成第一张轨道图](#orbital)
  - [4. 导入氧分子并查看来源](#step-04)
  - [5. 选择轨道并设置计算网格](#step-05)
  - [6. 调整轨道表面阈值](#step-06)
  - [7. 切换相位显示和透明度](#step-07)
- [渲染图片](#render)
  - [8. 设置输出尺寸并创建取景相机](#step-08)
  - [9. 渲染并保存图片](#step-09)
- [导出当前参数](#export)
  - [10. 选择参数摘要并导出](#step-10)
  - [11. 打开摘要并核对参数](#step-11)
- [保存、重新打开和归档工程](#save)
  - [12. 保存自包含工程](#step-12)
  - [13. 关闭并重新打开工程](#step-13)
  - [14. 检查重开后的显示和取景](#step-14)
  - [15. 归档工程及配套数据](#step-15)
- [按需选择功能专题](#topics)


适用 Windows x64、Blender 5.1.1、QCBlender 0.1.0。本文共 15 步；完成后可继续选择专题。

界面名称写作“中文名称（English name）”，便于对照简体中文与英文界面。文件名、科学数据字段、`qc_*` 内部标识和单位保持原样；如 `filename`、`coordinate_unit`、`electron/bohr^3`，不要将它们译成中文后填入文件或节点。

本文的文件路径均相对**材料根目录**，即解压后同时含有 `human/` 和 `shared/` 的文件夹。保留这两个目录的相对位置；无需安装 Gaussian、Multiwfn 或 PySCF。

教程截图保存在 `human/screenshots/`，以案例编号和内容命名，如 `P01-orbital.png`；本页使用 P01 前缀。渲染图保存在 `human/renders/`，工程和导出文件保存在 `work/human/`。按步骤保存图片后，下方引用便会显示对应图片。

<a id="install"></a>
## 安装并找到插件

<a id="step-01"></a>
### 1. 安装并启用 QCBlender

打开 Blender，选择 **编辑（Edit） → 偏好设置（Preferences） → 获取扩展（Get Extensions） → 右上角菜单 → 从磁盘安装（Install from Disk）**，选择 [shared/install/qcblender-0.1.0.zip](../shared/install/qcblender-0.1.0.zip)，完成安装。在 **插件（Add-ons）** 中搜索 **QCBlender**，确认已经启用。

需要切换语言时，打开 **编辑（Edit） → 偏好设置（Preferences） → 界面（Interface） → 语言（Language）**，选择简体中文或 English。使用简体中文时，开启 **界面（Interface）** 和 **工具提示（Tooltips）**；English 使用英文原文。QCBlender 的面板、操作、参数、节点、插口及资产目录随界面语言显示。切换语言不会改变科学数据；节点或资产显示名更新可能使工程出现“已修改”状态，按后面的保存步骤保存即可。自行改过的名称会保留。

> 偏好设置（Preferences）是偏好设置窗口；获取扩展（Get Extensions）用于管理扩展，从磁盘安装（Install from Disk）从本地 ZIP 安装，插件（Add-ons）用于启用或停用插件。

<a id="step-02"></a>
### 2. 检查科学运行环境

> 检查科学运行环境（Check Scientific Runtime）检查插件执行量子化学数值计算所需的运行环境是否可用。

展开 QCBlender，点击 **检查科学运行环境（Check Scientific Runtime）**。等待检查完成，应显示科学运行环境可用。截图保存为 `human/screenshots/P01-install.png`。

![插件已启用，科学运行环境检查完成](screenshots/P01-install.png)

<a id="new-scene"></a>
<a id="step-03"></a>
### 3. 准备新工程和操作界面

关闭偏好设置；如果已有需要保留的工程，先保存，再选择 **文件（File） → 新建（New） → 常规（General）**。在右上角 **大纲视图（Outliner）** 选中默认**立方体（Cube）** 并删除，保留摄像机（Camera）和灯光（Light）。鼠标移入 **3D 视图（3D Viewport）**，切到 **物体模式（Object Mode）**，按 `N`，打开 **QCBlender** 页；点击视口右上角的 **材质预览（Material Preview）**。之后文中的“N 侧栏”均指这里。

> 大纲视图（Outliner）是场景对象列表；3D 视图（3D Viewport）是观察和选择三维对象的视口，物体模式（Object Mode）用于操作整个对象。材质预览（Material Preview）是材质预览，可直接看到分子和表面的颜色。

> 立方体（Cube）是默认立方体，摄像机（Camera）是决定出图取景的相机，灯光（Light）是灯光；本教程导入的原子和场表面也都是场景对象。

> 属性（Properties）是属性编辑区，用于查看和修改所选对象及场景的设置。“对象属性”指右侧 **属性（Properties） → 物体（Object） → QCBlender · 对象与量子化学（QCBlender · Object and Quantum Chemistry）**。本教程使用 **N 侧栏 → 工作流（Workflow） → 对象属性与显示参数（Object Properties and Display Parameters）** 打开它；该入口会固定当前对象，每次换对象后再次点击，以便后续参数作用于新对象。

> 自定义属性（Custom Properties）是附在 Blender 对象或数据上的额外记录。选中 QCBlender 对象，在 **属性（Properties） → 物体（Object） → 自定义属性（Custom Properties）** 展开对应记录；将鼠标停在属性名称上，可查看内部键和用途。界面显示的友好名称可随语言切换，内部 `qc_*` 键保持原样，用于插件和脚本读取。日常调整优先使用教程指定的面板，不手动改科学记录。节点几何上的命名属性另见[节点专题](topics/09-nodes.md#attributes)。

文中的“选中对象”可在大纲视图（Outliner）点击对应名称。也可在 **N 侧栏 → 显示层（Display Layers）** 点击该对象行最左侧的选择图标；它会取消其他对象的选择，并在视口显示当前对象。眼睛图标控制视口可见性，相机图标控制是否参与渲染。

观察模型时，在 3D 视图（3D Viewport）中按住鼠标中键拖动可旋转视角，滚轮可缩放；也可拖动视口右上角的坐标轴导航控件。

N 侧栏按任务分组，先选当前案例对象，再展开需要的一组；不适用于该对象的操作不会显示空组。按钮的悬停说明会解释用途、作用对象、结果和必要前提。

| 面板 | 分组与用途 |
| --- | --- |
| 工作流（Workflow） | **导入（Import）** 读取文件；**计算（Compute）** 生成量子化学场。**对象属性与显示参数（Object Properties and Display Parameters）** 仍是直接入口。 |
| 创建视图与检查工具（Create Views and Inspection Tools） | **显示视图（Display Views）** 创建等值面、体积雾、局部层及其他显示视图；**空间工具（Spatial Tools）** 创建切片、裁剪和偶极；**场值采样（Field Sampling）** 取点与采样剖面；**原子与几何标注（Atom and Geometry Annotations）** 创建四类标注；**相机（Camera）** 设置取景。 |
| 导入外部结果（Import External Results） | **空间场分析（Spatial Field Analysis）** 导入 IGMH/IRI 与 ESP；**原子与键分析（Atom and Bond Analysis）** 导入 NBO 与 AIM；**能量分解（Energy Decomposition）** 导入 ETS-NOCV 表和配对场。 |
| 工程与诊断（Project and Diagnostics） | **保存与导出（Save and Export）** 保存、归档和导出；**恢复与维护（Recovery and Maintenance）** 重新定位数据、重建显示缓存及整理旧节点资产；**诊断信息（Diagnostics）** 检查科学运行环境。 |

标注的黑色文字、引线和测量几何，以及二面角的半透明三角面，见[分子与标注案例](topics/01-molecule-xyz.md#step-05)。标注属于对应的原子显示层，显示设置和材质随工程保存；它们的颜色、尺寸与朝向不改变源构型或测量值。

<a id="orbital"></a>
## 生成第一张轨道图

<a id="step-04"></a>
### 4. 导入氧分子并查看来源

点击 **N 侧栏 → 工作流（Workflow） → 导入（Import） → 导入 Gaussian / Cube / XYZ（Import Gaussian / Cube / XYZ）**，选择 [shared/data/public/P01/o2-uhf.fchk](../shared/data/public/P01/o2-uhf.fchk)。应出现两个氧原子，它们属于同一个原子对象。在大纲视图（Outliner）选中这个原子对象，按 `F2` 命名为 **P01-atoms**；点击 **数据集与数值摘要（Dataset and Numerical Summary） → 查看完整来源（View Full Source）**，应看到 **filename: o2-uhf.fchk**、**coordinate_unit: angstrom**。关闭来源窗口。

> FCHK 是格式化的量子化学计算结果文件，提供分子构型和波函数。构型是原子的空间位置；波函数提供计算轨道等物理量所需的信息。本例的计算条件见[样本说明](../shared/data/public/NOTICE.md)。

> 数据集是导入的科学数据及其来源记录；`filename` 是源文件名，`coordinate_unit` 是坐标单位。`angstrom` 即 Å（埃），1 Å = 0.1 nm。

<a id="step-05"></a>
### 5. 选择轨道并设置计算网格

> 活动对象是本次操作针对的对象；只选一个对象时就是它，多选时通常为最后选中的对象。生成量子化学场（Generate Quantum Field）会在空间网格上计算所选物理量，网格是规则排列的采样点。

> MO 是分子轨道；Alpha 和 Beta 是两种自旋通道的标记。轨道振幅的正负表示波函数的相位。

> 物理量（Quantity）决定生成哪一种场；先按要观察的内容选择，再设置计算网格。网格是数值计算的采样位置，与表面的配色和透明度分开设置。

- **分子轨道（Molecular orbital）**：生成一个轨道的振幅，用正负相位表面观察轨道形状；需要继续选择自旋通道和轨道。
- **电子密度（Electron density）**：生成 Alpha 与 Beta 通道相加的总电子密度，用于观察整体电子分布。
- **Alpha 密度（Alpha density） / Beta 密度（Beta density）**：分别生成一个自旋通道的电子密度。
- **自旋密度（Spin density）**：生成 Alpha 密度减 Beta 密度，用于观察两个自旋通道分布的差别。
- **静电势（Electrostatic potential）**：生成静电势，可给密度表面着色；操作见[密度与 ESP](topics/03-density-esp.md)。

> 选择分子轨道（Molecular orbital）后，自旋（Spin）指定 Alpha 或 Beta 通道；轨道（Orbital）决定如何在该通道中找到轨道。

- **HOMO**：自动选择该通道中能量最高的已占据轨道。
- **LUMO**：自动选择该通道中能量最低的未占据轨道。
- **源编号（Source number）**：使用源文件里的轨道编号，需要填写从 1 开始的轨道编号（从 1 开始）（Orbital number）。本例固定使用 Alpha 轨道 9，便于核对同一结果。

保持 **P01-atoms** 活动，点击 **工作流（Workflow） → 计算（Compute） → 生成量子化学场（Generate Quantum Field）**。首次使用时先等待自动检查。在 **生成量子化学场（Generate Quantum Field）** 对话框中，先选 **物理量（Quantity）=分子轨道（Molecular orbital）、自旋（Spin）=Alpha**，将 **轨道（Orbital）** 依次切到 **HOMO** 和 **LUMO**，观察预览中的 **源轨道（Source MO）**、占据数和能量；本例应分别显示源轨道 **8（占据数 1）** 和 **10（占据数 0）**，即一个已占据轨道和一个未占据轨道。此时还没有生成场。再切到 **源编号（Source number）**，输入 **9**，按下表补齐网格参数并点击 **确定（OK）**。

| 控件 | 输入值 | 用途 |
| --- | --- | --- |
| 物理量（Quantity） | 分子轨道（Molecular orbital） | 选择计算的物理量；本例为分子轨道振幅 |
| 自旋（Spin） | Alpha | 选择 Alpha 自旋通道 |
| 轨道（Orbital） | 源编号（Source number） | 按源文件编号选择轨道 |
| 轨道编号（从1开始）（Orbital number (1-based)） | 9 | 指定轨道编号；1-based 表示从 1 开始编号 |
| 网格间距（Å）（Grid spacing (angstrom)） | 0.2 | 相邻采样点的间距；越小采样越密，计算量也越大 |
| 网格边距（Å）（Grid margin (angstrom)） | 3 | 在分子外围扩展计算区域的距离 |
| 内存预算（MiB）（Memory budget (MiB)） | 512 | 供计算程序估算内存需求并安排分批计算的预算 |

> MiB 是内存容量单位，1 MiB = 1024² 字节；这里的预算用于本次数值计算，不是 Blender 总内存的硬限制。本文参数用于学习显示操作。

<a id="step-06"></a>
### 6. 调整轨道表面阈值

> 等值面连接场值达到某个阈值的位置；调整阈值会改变轨道表面的形状和大小。联动正负阈值（Link Thresholds）用于决定正、负相位是否采用相同的阈值幅度，显示开关则决定对应表面是否可见。

- **联动正负阈值（Link Thresholds）开启**：负相位沿用正相位的阈值幅度，适合用相同尺度观察两种相位。
- **联动正负阈值（Link Thresholds）关闭**：可以分别设置正、负相位的阈值幅度。
- **显示正相位（Show Positive Phase） / 显示负相位（Show Negative Phase）**：分别控制两种表面的可见性；只想暂时隐藏一种相位时，操作它的显示开关。

> `orbital_amplitude` 表示轨道振幅；bohr 是原子尺度的长度单位，约等于 0.529 Å，轨道振幅的单位 `bohr^-3/2` 表示 bohr 的 −3/2 次方。

完成后选中 **QC orbital_amplitude**。在 **对象属性（Object Properties） → 几何表示（Geometry Representation）** 将 **正值阈值（Positive Isovalue）** 设为 **0.045**，保持 **联动正负阈值（Link Thresholds）**、**显示正相位（Show Positive Phase）**、**显示负相位（Show Negative Phase）** 开启。应看到两种颜色的轨道表面；在 **科学记录与振动模式（Scientific Records and Vibration Modes）** 中应看到 `spin: alpha`、`source_number: 9`，单位为 `bohr^-3/2`。截图保存为 `human/screenshots/P01-orbital.png`。

![两个氧原子周围的 Alpha MO9 双相位表面及阈值](screenshots/P01-orbital.png)

> `spin` 记录自旋通道，`source_number` 记录源轨道编号。科学记录用于核对当前表面对应哪份计算数据。

<a id="step-07"></a>
### 7. 切换相位显示和透明度

> 材质（Material）是材质设置区，节点材质通过相连的计算单元控制颜色和透明度。正值不透明度（Positive Opacity）调整正相位表面的不透明度；0 为全透明，1 为不透明。

关闭再开启 **显示负相位（Show Negative Phase）**，应只有一种相位的表面消失后恢复。打开 **属性（Properties） → 材质（Material） → QCBlender · 节点材质（QCBlender · Node Materials）**，将 **正值不透明度（Positive Opacity）** 设为 **0.4**，正相位应变透明；最后恢复 **1**，保留两种相位。

<a id="render"></a>
## 渲染图片

> 渲染是按相机、灯光和材质生成图片；创建取景相机（Create Framed Camera）用于把当前观察对象纳入出图范围。渲染属性（Render Properties）是渲染设置区，EEVEE 是本例使用的渲染引擎；输出属性（Output Properties）控制输出尺寸，1280 × 720 是图片的宽、高像素数，100% 表示按此尺寸输出。

<a id="step-08"></a>
### 8. 设置输出尺寸并创建取景相机

在文件管理器中，在材料根目录创建 `work/human/P01/` 和 `work/human/exports/`。回到 Blender，在 **渲染属性（Render Properties）** 选择 **EEVEE**，在 **输出属性（Output Properties）** 设分辨率 **1280 × 720、100%**。选中 **QC orbital_amplitude**，转到能看清两种相位的角度，点击 **N 侧栏 → 创建视图与检查工具（Create Views and Inspection Tools） → 相机（Camera） → 创建取景相机（Create Framed Camera）**。在 3D 视图（3D Viewport）按小键盘 `0` 查看相机范围，整个轨道应在画面内；没有小键盘时选择 **视图（View） → 摄像机（Cameras） → 活动摄像机（Active Camera）**。

<a id="step-09"></a>
### 9. 渲染并保存图片

按 `F12` 渲染，在结果窗口选择 **图像（Image） → 另存为（Save As）**，保存到 `human/renders/P01-mo.png`。应看到完整的两种相位表面，构图与相机视图一致。

![第一张轨道渲染图](renders/P01-mo.png)

这张 PNG 是可直接用于教程、报告或演示的静态图片。需要调整视角、表面或材质时，使用后面保存的工程继续编辑，再重新渲染。

<a id="export"></a>
## 导出当前参数

<a id="step-10"></a>
### 10. 选择参数摘要并导出

> 导出数据与参数摘要（Export Data and Parameter Summary）用于把当前视图的说明或已有科学记录保存成文件。数据（Data）选择输出内容，可用选项随活动对象的数据变化；先选要导出的对象，再打开对话框。输出目录（Output directory）选择保存目录，文件浏览器会填入从盘符开始的实际绝对路径。

- **当前视图参数摘要（Current View Parameter Summary）**：导出供人阅读的 view-summary.md 与配套 metadata.json，用于核对图中的来源和显示参数。本主线使用这一项。
- **线剖面（profile）、成对场（paired）、ESP_AREA 等科学数据项**：导出对应对象已有的数值记录及 metadata.json，供表格或绘图软件使用；各专题说明应选哪一项。

> paired 与 ESP_AREA 还提供行（Rows），用于决定导出完整记录还是选中的部分。

- **全部来源记录（All source records）**：导出该类数据的全部记录。
- **当前筛选（Current filter）**：按当前筛选条件导出成对场的有效网格点或 ESP 面积区间。先在专题中设置筛选条件，再选这一项。

在渲染结果窗口按 `F11` 返回主窗口，选中 **QC orbital_amplitude**，点击 **N 侧栏 → 工程与诊断（Project and Diagnostics） → 保存与导出（Save and Export） → 导出数据与参数摘要（Export Data and Parameter Summary）**。将 **数据（Data）** 设为 **当前视图参数摘要（Current View Parameter Summary）**；在 **输出目录（Output directory）** 选择材料根目录下的 `work/human/exports/`，让文件浏览器填入它的实际绝对路径。截图保存为 `human/screenshots/P01-summary.png`，然后确认导出。

![当前视图参数摘要的导出选项与保存目录](screenshots/P01-summary.png)

<a id="step-11"></a>
### 11. 打开摘要并核对参数

按 **数据已导出：（Data exported:）** 提示中的完整路径打开新生成的子目录；若提示已消失，到 `work/human/exports/` 查找刚生成的目录。应有 **view-summary.md** 和 **metadata.json**；打开前者，检查其中有 **Alpha、源轨道 9、0.2 Å 网格、0.045 阈值**。插件每次自动创建一个不同名称的子目录。

这两个文件记录图中数据的来源和导出时读取的参数，方便以后核对与追溯。

> 计算方法规定采用的量子化学近似，基组是表达轨道的一组基础函数；它们帮助区分计算条件。色带把数值映射为颜色。

> `.md` 是 Markdown 文本，可用文本编辑器阅读；JSON 是便于程序读取的结构化文本。

| 文件 | 用途与内容 |
| --- | --- |
| `view-summary.md` | 供人阅读的参数说明：来源、已记录的计算方法与基组、轨道与自旋、网格、表面阈值、材质和色带，以及未记录或未验证的项目。 |
| `metadata.json` | 供程序读取的结构化记录：数据来源、科学参数、导出类型、数据身份和文件校验信息；本次参数摘要导出还包含当前视图参数，便于自动检查和比较。 |

日常主要查看 `view-summary.md`，将 `metadata.json` 一起保留即可，通常不需要手动编辑。这是导出时的快照；修改参数后需要重新导出，并将需要留存的图片和对应摘要一起保存。摘要中的未记录或未验证项说明本次记录的边界，它不保证完整记录节点内部效果或渲染结果。继续编辑工程仍需保留后面介绍的 `.blend` 与配套 `.qcdata/`。

> CSV 是以逗号分隔各列的数值表格，可用表格或绘图软件打开。[剖面专题](topics/04-spatial-tools.md#profile)会练习一次科学数据 CSV 导出。

专题中导出 CSV 时，先选专题指定的记录对象，再使用步骤 10 的入口，将 **数据（Data）** 改为该专题指定的类型。若尚未创建 `work/human/exports/`，先在文件管理器中创建它；只有支持筛选的类型才显示 **行（Rows）**，按专题要求选择导出范围。同目录的 `metadata.json` 用于说明数据来源、列名、单位和适用的筛选条件。需要分析或分享数据时，将 CSV 和该文件一起保留。

<a id="save"></a>
## 保存、重新打开和归档工程

> 自包含工程把场景及它引用的科学数据保存到配套位置，便于重新打开和移动。

下面的文件名用于 P01 主线。保存专题工程时，先创建对应案例目录，并换成有区别的名称，例如 `work/human/P03/P03-density-esp.blend`；重新打开和归档时沿用自己的工程名。

<a id="step-12"></a>
### 12. 保存自包含工程

点击 **N 侧栏 → 工程与诊断（Project and Diagnostics） → 保存与导出（Save and Export） → 保存自包含工程（Save Self-Contained Project）**，保存为 `work/human/P01/P01.blend`。在文件管理器中应同时看到 `work/human/P01/P01.qcdata/`。

> `.blend` 是 Blender 工程，保存场景对象、显示设置、材质、节点和相机等内容；同名 `.qcdata/` 保存工程需要的科学数据和场缓存。继续编辑或重新出图需要保留两者；移动时保持它们同处一个目录，不单独改名或手动修改配套数据。

<a id="step-13"></a>
### 13. 关闭并重新打开工程

选择 **文件（File） → 退出（Quit）** 正常关闭 Blender，再启动 Blender，用 **文件（File） → 打开（Open）** 打开 `work/human/P01/P01.blend`。

<a id="step-14"></a>
### 14. 检查重开后的显示和取景

选中 **QC orbital_amplitude**，切到 **材质预览（Material Preview）**。两种相位仍应完整显示，阈值仍为 **0.045**；按小键盘 `0`（或 **视图（View） → 摄像机（Cameras） → 活动摄像机（Active Camera）**）应能恢复刚才的取景。

<a id="step-15"></a>
### 15. 归档工程及配套数据

> 归档把已保存的工程及配套数据打包成一个 ZIP 压缩文件，便于备份或传递。

点击 **工程与诊断（Project and Diagnostics） → 保存与导出（Save and Export） → 归档工程（Archive Project）**，保存为 `work/human/P01/P01-project.zip`。在文件管理器中打开 ZIP，应能找到 `.blend` 与配套科学数据目录。接收者解压后保持目录结构，再打开其中的 `.blend`。

归档使用磁盘上已保存的工程。若归档前又修改了场景，先再次执行 **保存自包含工程（Save Self-Contained Project）**。独立导出的 PNG、CSV 和参数摘要仍在各自保存目录，需要一起分享时另行附上。

<a id="topics"></a>
## 按需选择功能专题

后续专题可按需要选择。标明“接续”的专题使用指定前置步骤生成的对象，不必完成前页所有可选练习；其余按[准备新工程](#new-scene)开始。出图、导出和保存按需使用上面的共同方法：选中当前案例的目标对象，替换主线中的 P01 对象名与文件名，为图片和工程使用不同名称。

| 想学习的功能 | 专题 |
| --- | --- |
| 球棍（Ball and Stick）、氢显隐、局部选择、测量标注、显示层、XYZ 帧 | [分子显示与 XYZ](topics/01-molecule-xyz.md) |
| 导入 Cube，声明量与单位，调整两符号表面，多场叠加与跨场着色 | [Cube 场](topics/02-cube.md) |
| 密度表面按 ESP 着色、图例、色带预设（Color Ramp Preset）、原子电荷、偶极和自旋密度 | [密度与 ESP](topics/03-density-esp.md) |
| 切片、等值线、探针、剖面 CSV、裁剪和体积雾 | [空间观察与数据导出](topics/04-spatial-tools.md) |
| IGMH、IRI 表面与成对场筛选 | [IGMH 与 IRI](topics/05-igmh-iri.md) |
| ESP 极值和面积、AIM 临界点与路径 | [外部 ESP 与 AIM 分析](topics/06-esp-aim.md) |
| IRC 路径、随步标注和 Mayer 键级 | [IRC 与 Mayer](topics/07-irc-mayer.md) |
| ETS-NOCV 表（ETS-NOCV Table）和正负变形密度 | [ETS-NOCV](topics/08-ets-nocv.md) |
| 用公共节点组合自己的显示流程 | [几何节点](topics/09-nodes.md) |

公开样本的计算条件和许可见 [shared/data/public/NOTICE.md](../shared/data/public/NOTICE.md) 与 [LICENSE](../shared/data/public/LICENSE)。
