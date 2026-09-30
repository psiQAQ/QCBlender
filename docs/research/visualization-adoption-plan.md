# QCBlender 可视化借鉴与近期落地路线

核查日期：2026-09-27。研究输入为 Multiwfn 调研（本地原件：`docs/GPT-Web-Chat/multiwfn.md`）与可视化软件调研（本地原件：`docs/GPT-Web-Chat/visualization-sw.md`），原文仅保存在本地忽略目录，不纳入提交历史。

**近期顺序：文档状态同步（完成）→ Gaussian 优化轨迹及四项源码借鉴（技术 Passed）→ 独立人工验收及外部视觉对照（Not Run）。** 现有 IOData/cclib、GBasis、OpenVDB 和 Geometry Nodes 已承担核心功能；新参考项目的价值需要落实到具体缺口。VTK 保留为固定版本的源码参考，未引入 VTK 产品代码或运行依赖。

## 1. 比较基准与证据边界

- **固定 SOP 基准**：技术复跑基线 `ce56c50`，固定 SOP 候选 SHA-256 为 `03311fdeb0c83a38a546ebddedee1fe05e8dcb7260b53c889dd9fee3fa7ee231`。C01–C13 六栏技术检查、N01–N18、35 个真实样本摘要和 26 次冷重开均 Passed，见 [技术复跑记录](../v1-acceptance/AGENT-REPLAY.md)。
- **结果浏览基准**：`065a444`、`2402bc9`、`5496f67` 已完成计算段选择、来源浏览及技术验证，见 [结果浏览记录](../RESULT_BROWSER.md)。
- **验收边界**：独立人工 SOP 仍为 Not Run；发布前置条件不变。技术复跑与后续功能开发分别记录。
- **架构**：[ADR 0001](../adr/0001-self-contained-extension.md)的单扩展和科学数据/显示分离保持不变。VTK、MolecularNodes 仅作固定源码参考，不进入产品运行依赖。
- **来源**：两份调研原文保留在本地 `docs/GPT-Web-Chat/`，研究验证记录在忽略的 `outputs/visualization-adoption/`。

## 2. 原稿建议与当前实现的对应

| 能力 | 当前代码与证据 | 实际缺口及处理 |
| --- | --- | --- |
| Gaussian Log/FCHK/Cube 入口 | [read_source](../../qcblender/readers.py#L124)已分派 IOData、cclib 和有界 Cube 读取器；[read_log](../../qcblender/gaussian_log.py#L179)保留计算段、方法、终止状态、能量及原文行号。 | `.mwfn`、Molden、ORCA 尚非当前入口；新增格式须有实际输入需求和可验收字段，暂不改内部模型。 |
| 内置 MO、密度和 ESP | [prepare/evaluate_field](../../qcblender/evaluate.py#L35)检查方法、占据、密度矩阵和基组，分块求值并支持取消；[轨道选择](../../qcblender/data.py#L53)使用自旋、占据和能量。 | 能力限于明确的方法集合和已验证组合；ECP、ghost、最高 g 以上角动量及受限分数占据等仍被拒绝。补数值对照，不引入新的 SCF 引擎。 |
| 科学数据与显示分离 | [Dataset 与保存](../../qcblender/data.py#L87)已有 metadata、float64 数组、来源哈希、形状/单位/有效域及内容寻址存储；[worker](../../qcblender/worker.py#L136)已有求值缓存。 | 可迁移工程和来源浏览已通过技术验证；只读详情按需读取 metadata，不加载科学数组。 |
| 双场着色、切片和多视图 | [add_mapping](../../qcblender/blender/scalars.py#L164)独立绑定几何与色场；[采样节点](../../qcblender/blender/assets.py#L34)、[显示层](../../qcblender/blender/layers.py#L8)和[等值面](../../qcblender/blender/views.py#L198)均已存在。 | 按来源分组和字段角色详情已完成；复制、坐标变换、无效域和冷重开保持为回归检查。 |
| 计算结果浏览 | [导入入口](../../qcblender/blender/ui.py)已提供异步计算段摘要和确认导入，来源详情可查看计算身份与原文位置。 | 选中 Gaussian 段内的离散优化轨迹已完成；范围与证据见 [技术记录](../OPTIMIZATION_TRAJECTORY.md)。 |
| IGMH/IRI、ESP、AIM、IRC/Mayer、ETS-NOCV/NOCV | [双场导入](../../qcblender/external_fields.py#L11)、[离散分析数据](../../qcblender/analysis_data.py#L12)、[IRC](../../qcblender/irc.py#L39)与[NOCV](../../qcblender/nocv.py#L8)已有显式关联、单位和来源记录。 | C07–C13 真实输出已通过本轮技术验收；新增变体仍须分别验证解析、显示与科学值。 |
| 周期体系 | 当前 [Grid](../../qcblender/evaluate.py#L13)能保存完整仿射网格，原子构型与显示变换已有约束。 | 仿射网格不等于周期物理能力。晶胞、周期镜像和跨边界连接按后续需求开展。 |

## 3. 各项目的借鉴结论

### Multiwfn：优先补外部结果的语义与验收

参数交互首批已完成：原生界面分工、单位/区间语义、点击探针与切片、等值线与剖面排版、外部记录过滤和定位。2026-09-28 最终候选的 69 项科学回归和 C01–C13、N01–N18 技术复跑 Passed，见 [参数研究](multiwfn-parameters.md)和[验收记录](../MULTIWFN_PARAMETERS.md)。下表保留各来源的科学约束与后续变体验证边界。

作者[官方下载页](http://sobereva.com/multiwfn/download.html)列出日期版 `2026.9.20` 和源码归档包，采用自定义许可；本轮未确认官方 Git 入口。参考版本、输入波函数、分析参数和实际输出需要共同记录。已有 `analysis.sources`、`reference_source`、用户关联和原文行号可复用，生成程序的版本和参数不能从文件后缀推断。[现有记录入口](../../qcblender/analysis_data.py#L12)

| 入口 | 官方输出中的具体约定 | 应补的验收场景 |
| --- | --- | --- |
| IGMH / IRI | [IGMH 教程](http://sobereva.com/621)示例使用 `dg_inter.cub` 与 `sl2r.cub`，需要片段定义；[IRI 教程](http://sobereva.com/598)的 `func1.cub` 是 sign(λ₂)ρ，`func2.cub` 才是 IRI。 | 保留显式角色选择，核对片段、构型、单位、网格、过滤条件和散点轴量名；用真实配对场验证互换输入造成的语义错误。 |
| ESP 极值与面积 | [官方教程](http://sobereva.com/443)说明 PDB 默认单位可能因字段容量改为 eV，单位写在头部；PQR 又使用不同字段。 | 对照文件头和生成记录确认单位；覆盖 eV 与默认值不一致的输入。当前 PDB 入口不扩张成通用 PQR 支持。 |
| AIM | [作者教程](http://sobereva.com/445)将 C/N/O/F 用作四类临界点标签，属性通过 CP 源编号关联；示例 CPprop 标题由等号分隔。 | 已验证真实 59 条 CP 的标题、类型、坐标及路径关联；CPprop 与 PDB 逐轴容差为 0.0005001 Å，冲突或损坏字段拒绝，缺字段显示未核验。见[源码借鉴验收](../acceptance/source-adoption.md)。 |
| IRC / Mayer | [作者批处理教程](http://sobereva.com/612)逐帧读取波函数并提取指定原子对的键级。 | 复用现有显式步序 CSV，核对原子身份、步数及逐步完整输出；教程的普通轨迹不能替代真实 IRC 验收。 |
| ETS-NOCV / NOCV | [作者教程](http://sobereva.com/609)中的初始全零能量表可能表示尚未计算；pair 形变密度、单轨道振幅和 Alpha/Beta 输出有各自身份。 | 已按表识别明确未计算声明，跳过占位表并保留后续已计算表；合法零值不据此拒绝，单位缺失由必填用户单位声明，冲突单位拒绝。真实九对及错误 pair/自旋见[源码借鉴验收](../acceptance/source-adoption.md)；更多开壳层变体仍需对应真实样本。 |

IGMH/IRI 当前要求两场同网格，这是该导入器的合同；一般表面着色可以从另一网格采样，不能把同网格要求泛化为所有双场显示的物理条件。[成对场校验](../../qcblender/external_fields.py#L11)、[原生表面采样](../../qcblender/blender/scalars.py#L164)

### GaussView、Chemcraft：优先改善结果选择

[Chemcraft 官方说明](https://www.chemcraftprog.com/help/ccbasicinfo.html)按构型、振动等结果组织树节点，并提供摘要、原文、坐标和图像；[Cube 操作说明](https://www.chemcraftprog.com/help/workwithcubes.html)分别控制正负表面、着色来源和切片。这直接支持“先选择科学结果，再添加视图”的近期改进。复用现有 jobs、能量、模式及场记录，先提供计算段摘要选择和来源查看。

[GaussView 6 官方手册](https://gaussian.com/wp-content/uploads/dl/gv6.pdf)的本地副本位于忽略的 `submodules/GaussianView/gv6.pdf`。源码借鉴阶段实际查阅印刷页 79–84 的分组表、原文及优化/IRC/扫描图，版本摘要及具体用途见[研究记录](source-adoption.md)。实际 GaussView GUI 对照仍为 Not Run。GaussView 的[安装说明](https://gaussian.com/g16/gv6win_install.pdf)包含 Gaussian/Utilities 前置条件，因此产品交互参考与运行组件获取分别评估。

### VMD Molfile：借鉴边界检查，保留现有 Cube 读取器

[VMD 表示方式](https://www.ks.uiuc.edu/Research/vmd/current/ug/node45.html)把选择范围、显示方式、着色和材质分开，适合核查现有显示层的可理解性。[Molfile](https://www.ks.uiuc.edu/Research/vmd/plugins/molfile/)可单独调用，但[插件许可](https://www.ks.uiuc.edu/Research/vmd/plugins/pluginlicense.html)与主程序不同，且存在逐文件例外。

已读[官方 Cube 源码页](https://www.ks.uiuc.edu/Research/vmd/plugins/doxygen/cubeplugin_8C-source.html)标注 Revision 1.32、2016-11-28；它是确定的历史源码快照。该实现为显示约束旋转坐标与网格、缓存多轨道 float 数据，正原子数路径按一个 dataset 处理。[插件说明](https://www.ks.uiuc.edu/Research/vmd/plugins/molfile/cubeplugin.html)也记录了旋转和多轨道内存限制。可据此补兼容性案例；当前读取器已有斜轴、多 dataset、预算和损坏数据检查，暂无直接替换收益。官方[源码获取说明](https://www.ks.uiuc.edu/Research/vmd/doxygen/cvsget.html)使用需申请账户的 CVS，本轮未确认可用的官方 Git 子模块入口。

### VTK：固定源码用于算法审查和后续对照

参考子模块为 submodules/VTK（本地原件：`submodules/VTK`），来源采用[官方仓库入口](https://vtk.org/download/)，固定 `v9.7.0` / `23f0a095621e91bbdbeace8451e22b950c8e5f46`。本地为 depth 1、`blob:none` 部分克隆和指定文件的 sparse checkout；检出了许可、模块声明及下列源码，未初始化嵌套子模块、编译 VTK 或安装 wheel。Git 记录固定 gitlink，`.gitmodules` 保存官方 URL 和 `shallow = true`；局部检出范围属于本地读取配置。

| 固定版本源码 | 核查结果 | 对 QCBlender 的取舍 |
| --- | --- | --- |
| vtkGaussianCubeReader.cxx（本地原件：`submodules/VTK/IO/Chemistry/vtkGaussianCubeReader.cxx#L119`） | 原子行读取四项；轨道编号被跳过；grid 分配一个 float32 标量；origin 为零、spacing 为一，另持有 Transform。读值循环没有按多轨道数量拆出多个数组。 | 不能直接替换当前 float64、多轨道源编号、完整步向量和显式单位合同。这是源码观察，未运行该 reader 验证全部变体。 |
| vtkProbeFilter.h（本地原件：`submodules/VTK/Filters/Core/vtkProbeFilter.h#L80`） | Input 提供几何，Source 提供插值数据，并输出有效点掩码。 | 线剖面复用 QC 三线性采样，保存源坐标距离、字段来源和有效掩码；曲线在无效区断开，CSV 留空。未引入 VTK 运行依赖，见[源码借鉴验收](../acceptance/source-adoption.md)。 |
| vtkFlyingEdges3D.h（本地原件：`submodules/VTK/Filters/Core/vtkFlyingEdges3D.h#L18`） | 四遍处理、预分配和并行能力明确；文档同时提示可能产生零面积三角形。 | 作为性能对照候选。先测原生等值面瓶颈、内存及输出质量，再决定是否值得增加编译/打包成本。 |
| vtkImageData.h（本地原件：`submodules/VTK/Common/DataModel/vtkImageData.h#L304`）、VTK XML writer（本地原件：`submodules/VTK/IO/XML/vtkXMLImageDataWriter.h#L4`） | 数据模型有方向矩阵和索引到物理空间变换，writer 提供 VTI 文件输出。 | 后续有场交换需求时审查坐标、数组顺序、点/单元属性、有效域和科学元数据；不能只导出数值数组就声称完整互操作。 |

所查 reader/filter 文件头为 BSD-3-Clause；项目许可（本地原件：`submodules/VTK/Copyright.txt`）与模块材料都需保留。尤其 FiltersCore 模块声明（本地原件：`submodules/VTK/Filters/Core/vtk.module`）另列 `LicenseRef-BSD-3-Clause-Sandia-USGov` 和对应附加声明（本地原件：`submodules/VTK/Filters/Core/LICENSE`），完整模块不能仅凭单文件头概括。IOChemistry（本地原件：`submodules/VTK/IO/Chemistry/vtk.module`）还依赖多个 Common/IO/Rendering 等模块，“选一个 reader”并不等于只增加一个无依赖源文件。本轮仅登记参考源码，未改变现有发行材料和包内容。

### VESTA：保留结构与场共同变换的验收思路

[官方手册](https://jp-minerals.org/vesta/en/doc/VESTAch2.html)描述结构、多等值面、第二物理量着色和切片；[数据编辑章节](https://jp-minerals.org/vesta/en/doc/VESTAch6.html)区分晶胞、结构和体数据。近期可用这些概念审查当前关联和显示变换；周期晶胞、超胞、跨边界连接待实际需求再进入实现。[官方许可页](https://jp-minerals.org/vesta/en/download.html)对再分发有明确限制，本轮采用公开资料作为参考。

## 4. 当前落地路线

| 顺序 | 状态 | 范围与证据 |
| --- | --- | --- |
| 固定 SOP 技术复跑 | Passed | C01–C13、N01–N18 与真实样本，见 [技术记录](../v1-acceptance/AGENT-REPLAY.md) |
| 计算段选择、来源浏览 | Passed | 三项任务均 resolved，见 [结果浏览记录](../RESULT_BROWSER.md) |
| Gaussian 优化轨迹浏览 | Passed | 独立视图逐步构型、能量、收敛与来源；25/25 科学回归、GUI/MCP、独立候选和移动冷重开，见 [技术记录](../OPTIMIZATION_TRAJECTORY.md) |
| AIM/NOCV 校验、自动取景、场值线剖面 | Passed | 四项独立开发、逐批安装验收；最终候选 45/45 科学回归与完整技术 SOP 通过，见[技术记录](../acceptance/source-adoption.md) |
| VMD 参数交互首批 | Passed | 四包实现、48 项科学回归、安装、MCP、Computer Use 与双冷重开通过，见[技术记录](../acceptance/vmd-parameters.md) |
| MolecularNodes 参数交互首批 | Passed | 固定局部选择、真实步测量标注、图例排版及最终 C01–C13 / N01–N18 技术 SOP 通过，见[技术记录](../MOLECULARNODES_PARAMETERS.md) |
| 独立人工验收、外部视觉对照 | Not Run | 在本轮功能开发及技术验证之后执行，记录确切候选；人工签名由用户完成 |
| 发布机制 | Not Run | 继续受人工验收和候选资格门槛约束 |

ORCA、`.mwfn`、周期体系及新的分析类型按后续实际需求另行立项。Molden、VTK 交换和算法性能替换也不自动进入本轮任务；只有真实输入或测量结果证明缺口时再评估。

## 5. 研究阶段验证与复核方法

| 检查 | 状态 | 证据与限制 |
| --- | --- | --- |
| 两份原文保全 | Passed | 两份本地原文已保全；研究阶段副本与本地原文的差异仅为一处尾空白，不覆盖本地原文。 |
| VTK 来源、版本与浅克隆 | Passed | 官方 tag 对应上述 commit；`rev-parse --is-shallow-repository` 为 true，`rev-list --count HEAD` 为 1；所查源码已检出，子模块无修改。 |
| 当前 Cube 边界测试 | Passed | 研究工作树 `tests/test_science_cube.py` 的 2 项测试；斜轴非立方多轨道、交错排列/源编号、负网格计数单位、未知量、少值/多值/NaN 均覆盖。 |
| 文档与 Git 范围检查 | Passed | 41 条仓库内链接及代码行号有效；报告为 UTF-8 无 BOM、LF，无尾空白；原件哈希、研究文件清单、已有子模块 gitlink 和 VTK 深度核对通过，`git diff --check` 无错误。 |
| 官方资料与指定源码阅读 | Passed | 各结论旁链接限定到实际查阅来源；GaussView 只使用官方索引页段。版本、许可和字段语义各自核查。 |
| GaussView 手册全文直连 | Failed | 本次环境未成功获取全文；未将官方索引片段扩大解释为全手册或实际运行验证。 |
| VTK/VMD/Multiwfn 构建、运行与性能比较 | Not Run | 本轮只获取参考源码、阅读资料并执行现有 Cube 测试。 |
| C01–C13 科学与 GUI 完整复跑、独立人工复做 | Not Run（本轮） | 研究阶段未执行；后续主分支技术复跑已 Passed，独立人工仍 Not Run，见第 1 节。 |

重跑 Cube 科学检查使用 [DEVELOPMENT](../DEVELOPMENT.md) 中已有环境与当前测试入口。本研究当时的检查保存于忽略的 `outputs/visualization-adoption/cube-check.json`；它不构成当前候选复验结果。
