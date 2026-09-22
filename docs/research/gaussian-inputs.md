# Gaussian 输入能力、数值边界与 ORCA 迁移依据

核对日期：2026-09-22。本文是 QCBlender 的设计研究，不代表插件已经实现或通过下述验收。首版目标是用 Blender Geometry Nodes 控制量子化学结果的展示；Gaussian 是首个数据来源，ORCA 是后续来源。

## 结论与建议

首版以三条入口组织 Gaussian 工作流：计算日志提供结构和已输出性质；FCHK 提供可供后处理的波函数或密度信息；Cube 提供已采样的空间场。WFN/WFX 与优化/IRC 播放在后续接入。`.chk` 通过用户已有 Gaussian 的 `formchk` 转换进入 FCHK 路径。解析文件、由波函数计算空间场、在 Blender 中展示空间场分别验收。

**格式支持必须写成“来源版本 × 文件内容 × 可用物理量 × 展示行为”，不能只列后缀。** 例如，能够从 FCHK 读取坐标不证明能够计算轨道；能够读取单标量 Cube 不证明支持多轨道 Cube；读取 MO 能级不证明拥有完整基组和 MO 系数。

用户已确认首版完整验收结构/电荷/偶极、振动与 IR 联动、MO 正负等值面、总电子密度/自旋密度、ESP 映射及场切片。FCHK 内置求值为首版要求，科学范围为非周期实值 HF/DFT，含开壳层及常见基组；更广方法的能量读取与其密度求值分开。具体阶段以 [主设计](../QCBLENDER_V1_DESIGN.md) 为准。

## 证据可用性

- 本次实际请求 [Gaussian formchk](https://gaussian.com/formchk/)、[cubegen](https://gaussian.com/cubegen/)、[Output](https://gaussian.com/output/)、[Units](https://gaussian.com/units/) 均未成功取得正文，工具返回 502 或内部抓取错误。因此下文明确标注 Gaussian 09 原手册镜像，并用读取器源码交叉核对；不能据此宣称已完整复核 Gaussian 16 的当前官方网页。
- ORCA 依据可读取的 [ORCA 6.1 官方手册](https://www.faccts.de/docs/orca/6.1/manual/contents/utilitiesvisualization/utilities.html)。Python 库区分 cclib 1.8.1 文档、IOData 在线文档和本次所见开发分支源码；开发分支事实不等同于已发布 wheel 的行为。
- 必需科学库以扩展内 wheels 提供，版本与平台验证见 [打包研究](blender-extension-packaging.md)；本研究未安装依赖、调用 Gaussian/ORCA 或执行这些库。

## Gaussian 格式能力矩阵

| 文件族 | 文件可能提供的内容 | 首版入口建议 | 必须保留的边界 | 依据 |
| --- | --- | --- | --- | --- |
| `.log` / `.out` | 单点/优化几何、能量、原子电荷、振动频率与位移、偶极等已打印结果；部分任务打印 MO 数据 | 以日志解析器识别内容和任务，建立结构/轨迹/性质对象 | 输出关键字、计算类型、正常/异常终止、多个任务段会改变可用数据；不能从普通后缀推定完整波函数 | [cclib 数据表](https://cclib.github.io/data.html)、[Gaussian parser](https://github.com/cclib/cclib/blob/master/cclib/parser/gaussianparser.py) |
| `.fchk` / `.fch` | 元素、坐标、有效核电荷、基组壳层/指数/收缩、alpha/beta MO、若干密度矩阵和性质；部分文件有轨迹字段 | 波函数主入口；按字段逐项授予结构、轨道、密度等能力 | 球谐/笛卡尔、SP 壳、归一化、系数顺序、ECP、电子数都参与含义；有字段名不代表任务曾正确计算该性质 | [Gaussian 09 FCHK 原手册镜像](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/f_formchk.htm)、[IOData FCHK 源码](https://github.com/theochem/iodata/blob/main/iodata/formats/fchk.py) |
| `.chk` | Gaussian 二进制 checkpoint | 显示转换流程；可选调用用户配置的 `formchk`，再读 FCHK | 不通过文本解码尝试直接解析；转换程序、版本和结果另行验证 | [Gaussian 09 FCHK 原手册镜像](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/f_formchk.htm) |
| `.cube` / `.cub` | 原子、网格原点、三个步进向量、网格值；可含多个 MO 或不同输出布局 | 已计算场的主要入口，按数据集选择等值面、切片、颜色映射 | 数值可能是轨道、电子密度、自旋密度、ESP、梯度等；网格不是晶胞；头信息不足时物理量保持未知 | [Gaussian 09 cubegen 原手册镜像](https://theochem.mercer.edu/chm295/g09ur/u_cubegen.htm)、[VMD Cube 插件](https://www.ks.uiuc.edu/Research/vmd/plugins/molfile/cubeplugin.html) |
| `.wfn` | primitive Gaussian 展开、轨道占据和系数、坐标等 AIM 后处理数据 | 与 FCHK 共用波函数/空间场后端，采用已验证的读取器 | 固定字段和变体存在；自旋分类可能依赖推断；不能保证有 LUMO/完整虚轨道 | [Gaussian Output 原手册镜像](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_output.htm)、[IOData WFN 源码](https://iodata.readthedocs.io/en/latest/_modules/iodata/formats/wfn.html) |
| `.wfx` | 扩展 AIM 波函数、自旋和占据等标签；可带 ECP 的额外电子密度函数 EDF | 与 WFN/FCHK 共用后端；按实际支持的标签给出能力 | WFX 不是合法 XML；一阶密度信息不等于任意相关波函数的完整多电子信息；EDF/磁场扰动需单独验收 | [WFX 作者规范 1.0.4c](https://aim.tkgristmill.com/wfxformat.html)、[IOData WFX 源码](https://iodata.readthedocs.io/en/latest/_modules/iodata/formats/wfx.html) |

以上是文件语义和实现建议，全部插件功能状态为 **Not Run**。

## 数据与数值条件

### 日志：任务、单位和坐标系是数据的一部分

cclib 的公开数据单位包括：`atomcoords` 为 Å，`scfenergies` / `moenergies` 为 eV，`vibfreqs` 为 cm⁻¹，`vibdisps` 文档记为 delta Å。它们不是全量统一原子单位。适配层需要逐字段转换并保存原始单位，不能把 cclib 返回值直接套入 FCHK 的单位规则。[cclib 1.8.1 数据说明](https://cclib.github.io/data.html)

Gaussian parser 优先处理 Standard orientation，也维护 Input orientation；源码会旋转输入方向的力以匹配标准方向。日志、FCHK、Cube 联合显示前，必须核对原子顺序、几何帧和坐标系。仅因为文件同名而叠合是不充分的。[cclib Gaussian parser](https://github.com/cclib/cclib/blob/master/cclib/parser/gaussianparser.py)

`gbasis` 需要日志实际打印基组；cclib 文档建议 Gaussian 的 `GFINPUT`。MO 系数也必须确实存在并完整。日志不含所需数据时，界面应给出缺失项和可用入口，而不是用零填充制造“可计算”。优化轨迹并不自动拥有分子动力学的时间间隔，振动动画的显示幅度也不等于实验振幅。[cclib 数据注解](https://cclib.github.io/data_notes.html)

实现建议：一个日志中保留任务段、每帧身份、收敛/终止状态、对应能量类型和性质来源；未收敛几何可以显示，但不得标记为成功优化结果。振动模式需保留负频率，区分频率值与用于展示的周期/幅度。

### FCHK：读到系数之后还缺什么

Gaussian 09 原手册规定 FCHK 采用原子单位，并在计算已确定 Standard orientation 时采用该方向。坐标以 Bohr 解释；不能把输入文件的 `Units` 直接套到 FCHK。原手册还区分有效核电荷与原子序数，并提醒非频率任务的力常数字段可能不能用于振动分析。[FCHK 原手册镜像](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/f_formchk.htm)

读取器至少应保留 `Shell types`、`Shell to atom map`、每壳 primitive 数、指数、收缩系数及 SP 的 p 系数。IOData 显式处理 SP、球谐和笛卡尔约定，并将文件顺序的 MO 系数重排为基函数 × 轨道矩阵。由此可见，`nbasis × nmo` 大小正确仍不足以证明系数语义正确。[IOData FCHK 源码](https://github.com/theochem/iodata/blob/main/iodata/formats/fchk.py)

用于核对数值后端的数学关系为：

\[
\psi_i(\mathbf r)=\sum_\mu C_{\mu i}\chi_\mu(\mathbf r),\qquad
\rho(\mathbf r)=\sum_{\mu\nu}P_{\mu\nu}\chi_\mu(\mathbf r)\chi_\nu(\mathbf r)
\]

这里采用实基函数，`C` 的第一维是基函数，`P` 是对应基函数约定下的一阶密度矩阵。这些公式要求基函数顺序、归一化、坐标系和密度定义一致；对于复轨道需保留共轭，不能继续使用实数路径。电子密度、轨道振幅和 ESP 应作为不同类型的物理量。

建议首个数值后端对支持的 RHF/RKS、UHF/UKS、ROHF 等情形逐项验收；不要把所有密度都重新从整数占据的 SCF 轨道构造。文件内的 SCF 与 post-SCF 密度来源需要保留，未找到目标密度时直接报告缺失。独立求值应核对 `CᵀSC ≈ I`；电子数检验需考虑 ECP、密度定义和有限积分域。

### Cube：先确定网格布局，再做表面

Gaussian `cubegen` 输出使用原子单位。自定义网格输入中 `N1` 的单位约定属于工具输入语法，不能与输出文件的原子数符号混用。VMD 的格式说明也明确原子坐标和步进向量为原子单位。[VMD Cube 插件](https://www.ks.uiuc.edu/Research/vmd/plugins/molfile/cubeplugin.html)

建议内部使用显式 affine 网格：

\[
\mathbf r(i,j,k)=\mathbf o+i\mathbf a+j\mathbf b+k\mathbf c,
\quad 0\le i<n_1,\;0\le j<n_2,\;0\le k<n_3.
\]

Gaussian 的三个向量可非正交；文件第三个网格索引变化最快。负 `NAtoms` 表示后续带 MO 编号记录；多个 MO 的值按每个采样点成组保存。转换为 Blender volume 或 mesh 时要验证完整变换，不能只取三个对角步长。[cubegen 原手册镜像](https://theochem.mercer.edu/chm295/g09ur/u_cubegen.htm)

建议 Cube 输入至少区分下列情况：

| 内容 | 处理要求 |
| --- | --- |
| 普通单标量网格 | 数据数目必须等于 `n1*n2*n3`，保留原点和三个向量 |
| 负原子数、一个或多个 MO | 正确读取跨行 MO 编号，解交错全部数据集；显示用户选择的轨道 |
| 正原子数且有 `NVal` | 解析器必须理解实际多值布局；不能悄悄只读取第一份数据 |
| density + gradient / laplacian | 按生成器布局解释，禁止仅 flatten 后当作多个标量 MO |
| 缺头、二进制或未支持的生成器变体 | 清晰拒绝并给出支持的导出路径 |
| 不明物理量 | 以“未知标量场”导入，要求明确量纲才能用于定量图例或运算 |

支持范围应包含上述常用多轨道输入；尚未实现的组合输出需要公开标记。`.cube` 本身不能证明场是 density，也不能恢复已丢失的基组或所有轨道。建议记录生成程序/版本、原始注释、物理量、单位、数据集编号和源文件摘要。以上是由文件布局推导的 QCBlender 数据要求。

ESP 映射使用两个不同的场：一个定义表面，一个在该表面取样用于颜色。差分密度至少需要相同几何参考、相同物理量/单位和一致网格；不同网格需要显式插值。不得用包围盒相似作为可以逐元素相减的依据。

### WFN/WFX：保留实际存在的波函数信息

WFX 作者规范使用原子单位和未归一化 primitive Cartesian Gaussian 的展开系数，含占据及自旋信息；它不是合法 XML。其一阶密度信息足以描述相应一电子性质，不等于完整的相关多电子波函数。规范还为 ECP 的 EDF 留出结构。因此不能把 WFX 交给标准 XML parser 后认为工作已完成，也不能丢弃 EDF 后宣称重建了全电子密度。[WFX 作者规范](https://aim.tkgristmill.com/wfxformat.html)

IOData 的 WFN reader 会转换 primitive 归一化；缺少扩展自旋标签时存在自旋分类启发式。因此对 Gaussian WFN 的受限/非受限、分数占据以及高角动量输入要用真实文件核对，模糊情况应保留“不确定”。读取到占据轨道不能推出存在完整虚轨道目录。[IOData WFN 源码](https://iodata.readthedocs.io/en/latest/_modules/iodata/formats/wfn.html)

本次检查的 IOData WFX 源码没有找到 EDF 字段处理；这不足以证明所有版本都不支持 EDF，但足以阻止在未做固定版本测试前宣称具备此能力。磁场扰动、复数和 EDF 均需单独做数据保真与数值测试。[IOData WFX 源码](https://iodata.readthedocs.io/en/latest/_modules/iodata/formats/wfx.html)

## ORCA 的可迁移部分

ORCA 官方路径已经提供 Cube、Molden/MKL、WFN/WFX 和 JSON 导出。建议后续优先接入 ORCA 日志及这些公开导出，不依赖自建 `.gbw` 二进制读取器。几何、振动、空间场、表面与材质节点可以共用，生产者特有的单位、轨道编号和基组约定留在适配层。[ORCA 6.1 utilities](https://www.faccts.de/docs/orca/6.1/manual/contents/utilitiesvisualization/utilities.html)

| 来源路径 | 可共用内容 | 新增验收点 |
| --- | --- | --- |
| `orca_plot` / `%plots` → Cube | 网格、等值面、切片、颜色映射 | ORCA 生成器信息、实际 MO 编号/自旋通道、不同版本导出 |
| `orca_2mkl` → Molden/MKL | 原子、基组和轨道后处理对象 | 球谐符号、primitive 归一化、高角动量；不能沿用 Gaussian 的 AO 顺序 |
| `orca_2aim` → WFN/WFX | 已验证的波函数读取和求值链 | alpha/beta、自然轨道、有效核电荷及 EDF 的保真 |
| ORCA `.out` | 结构、能量、振动与已打印性质 | ORCA parser 覆盖和单位；日志需要额外输出的字段 |
| `orca_2json` → JSON | 未来结构化入口候选 | 先核对具体 schema/版本；不能把它默认视为 QCSchema |

上述官方工具和导出角色见 [ORCA 6.1 utilities](https://www.faccts.de/docs/orca/6.1/manual/contents/utilitiesvisualization/utilities.html)。ORCA 的图示说明直接支持 Cube MO 双符号等值面，并区分 UHF 的 spin-up/spin-down 选择。[ORCA orbital and density plots](https://www.faccts.de/docs/orca/6.1/manual/contents/utilitiesvisualization/plots.html)

IOData Molden reader 专门处理 ORCA 的 primitive 归一化及部分球谐符号约定，并用轨道范数判断纠正结果。这个已有实现证明“增加一个 `.molden` 后缀”不是完成 ORCA 波函数迁移的充分条件。[IOData Molden 源码](https://github.com/theochem/iodata/blob/main/iodata/formats/molden.py)

ORCA 6.1 手册新增 `orca_plot` 对可用 state density 的 ESP 生成路径；该能力需按版本表达，不宜反推旧版行为。[ORCA 6.1 ESP plots](https://www.faccts.de/docs/orca/6.1/manual/contents/utilitiesvisualization/utilities.html#perform-electrostatic-potential-plots)

## 解析库与依赖决策

| 组件 | 已核对能力 | 实际限制及采用建议 |
| --- | --- | --- |
| cclib | Gaussian/ORCA 日志的结构与性质；也有 FCHK reader | 建议作为日志解析首选；按照属性和任务逐项验收，不把支持程序列表当作全量保证。它不是首版通用波函数求值引擎 |
| IOData (`qc-iodata`) | FCHK、WFN、WFX、Molden 等的基组和轨道读取 | 波函数解析首选候选；先解决版本/许可证元数据不一致，再核对受支持字段。Cube reader 不能未经扩展直接承担全部 Gaussian Cube 变体 |
| GBasis (`qc-gbasis`) | Gaussian 型基函数的求值、微分及积分库 | 可供独立数值后端评估；本次所见源码已涉及编译构建，不按“纯 Python 无打包成本”处理 |
| Open Babel | 官方 FCHK 页面明示分子几何读取 | 不以其 FCHK 格式标签推定能够提供完整 QC 波函数；首版无需仅为此引入 |
| Gaussian `formchk` / `cubegen` | checkpoint 转文本，波函数后处理得到空间场 | 适合作为用户配置的外部工具和独立数值参照；是否存在、版本、退出码、输出内容全部显式检查；不得自动下载或分发 |

能力来源：[cclib 数据表](https://cclib.github.io/data.html)、[IOData 支持格式](https://iodata.readthedocs.io/en/latest/formats.html)、[GBasis 仓库](https://github.com/theochem/gbasis)、[Open Babel FCHK 文档](https://openbabel.org/docs/FileFormats/Gaussian_formatted_checkpoint_file_format.html)、[Gaussian 原手册](https://theochem.mercer.edu/chm295/g09ur/u_cubegen.htm)。

必须记录的源码审查结果：

1. **cclib FCHK 读取范围。** 本次所见 `fchkparser.py` 读取 MO 系数，`Shell types` 路径建立 AO 名称；没有 `Primitive exponents`、`Contraction coefficients` 或 `gbasis` 的解析实现。不能把该返回对象视为完整可求值基组。[cclib FCHK 源码](https://github.com/cclib/cclib/blob/master/cclib/parser/fchkparser.py)
2. **cclib 体求值范围。** `volume.py` 的实现依赖 PyQuante/pyquante2 分支，显式的 S/P/D/F 笛卡尔幂表不构成通用球谐/高角动量后端的证明。[cclib volume 源码](https://github.com/cclib/cclib/blob/master/cclib/method/volume.py)
3. **IOData Cube 范围。** 在线源码按原样 `natom` 分配原子数组，并读取 `shape` 个标量，未见负原子数的 MO 编号和多值拆分。适配前需独立验证该版本；这个短而明确的格式边界可以做专用解析，但不能复写整套波函数解析库。[IOData Cube 源码](https://iodata.readthedocs.io/en/latest/_modules/iodata/formats/cube.html)

许可证与打包事实（记录元数据，不替代发布时的许可证核验）：

| 候选 | 本次核对到的元数据 | 对 QCBlender 的决策 |
| --- | --- | --- |
| cclib 开发分支 | `BSD-3-Clause`；Python ≥3.10；依赖 NumPy、SciPy、packaging、periodictable | 固定所采用的发布版本，验证 Blender 自带 Python ABI 与随包 wheels，携带相应许可证材料。[pyproject.toml](https://github.com/cclib/cclib/blob/master/pyproject.toml) |
| IOData 开发分支 | 根 `LICENSE.txt` 为 LGPLv3；`pyproject.toml` 声明 `GPL-3.0-or-later`，FCHK/Cube 文件头为 GPLv3+；依赖 NumPy、SciPy、attrs | 记录许可证材料不一致，不能只采用 GitHub 自动识别的标签。固定目标版本并核对所打包文件后再批准集成。[LICENSE.txt](https://github.com/theochem/iodata/blob/main/LICENSE.txt)、[pyproject.toml](https://github.com/theochem/iodata/blob/main/pyproject.toml)、[FCHK 文件头](https://github.com/theochem/iodata/blob/main/iodata/formats/fchk.py) |
| GBasis 开发分支 | 元数据为 GPLv3+；NumPy ≥2.0、SciPy、importlib_resources、SymPy；scikit-build/CMake 构建配置 | 固定源码构建 Blender 兼容 wheel；PyPI 0.1.0 的 Windows NumPy<2 约束不适用目标运行时，详见打包研究。[pyproject.toml](https://github.com/theochem/gbasis/blob/master/pyproject.toml) |

主路径是扩展内 **cclib 日志适配 + 经核验的波函数解析/求值后端 + 有明确变体边界的 Cube 导入**。`formchk`/`cubegen` 是可选外部转换和比较路径。用户安装一个 Windows x64 / Blender 5.1.1 扩展包；构建环境由维护者管理，运行时不补装依赖。

## 建议验收矩阵

下表覆盖首版与后续路线，当前产品状态全部为 **Not Run**。G03、G12、O01 在后续验收；G06 的相关密度数值求值、G11 的场差也在后续，首版保留识别与具体不支持诊断。其它行只针对声明支持的内容验收。文件读取、数值正确、Blender 行为、视觉确认分别记录。

| 编号 | 输入或场景 | 可观察通过条件 |
| --- | --- | --- |
| G01 | Gaussian 单点、优化、IRC、频率日志；完整与异常终止各一例 | 原子顺序、任务段、帧、性质与原始输出一致；异常终止不标为成功 |
| G02 | 同一体系的日志/FCHK/Cube | 转换后坐标重合；方向不同时存在可核查的变换；属性绑定到正确几何帧 |
| G03 | 优化或 IRC 轨迹 | 时间线切换正确原子/帧；能量类型和进度值明确；不虚构 MD 时间 |
| G04 | 含实频和虚频的频率结果 | 位移原子顺序、方向和模式编号正确；频率保留符号；显示幅度可调 |
| G05 | FCHK：闭壳层、非受限、受限开壳层，SP、5D/6D、7F/10F、一个更高角动量体系 | 所有受支持基组约定通过独立参考；不支持的具体类型明确失败，不产生近似冒充结果 |
| G06 | FCHK：SCF 与相关密度、ECP、线性相关删除基函数 | MO 维度不强制等于原始 AO 数；有效核电荷正确；选中密度来源未被悄悄换成 SCF |
| G07 | Cube：偏移原点、各向异性、旋转/斜轴，非立方 shape | 八个角点、特定 voxel 数值和分子位置正确；数据不换轴、不镜像、不误缩放 |
| G08 | Cube：一个/多个 MO、跨行 MO 编号、正原子数多值/组合输出 | 每个声明支持的数据集均逐点正确；不支持的布局清晰拒绝；截断与多余数据可检测 |
| G09 | MO 正负等值面 | 使用同一绝对阈值；正负两组几何和颜色可通过节点控制；改变阈值确实改变表面 |
| G10 | density、spin density、ESP、未知标量场 | 标签/单位/色标与数据语义对应；未知场不会自动标为电子密度 |
| G11 | 密度表面映射 ESP；同网格/异网格场差 | 采样位置和坐标系正确，异网格显式插值；保存后可恢复场绑定和参数 |
| G12 | WFN/WFX：Gaussian 实际文件，开闭壳层、分数占据、ECP/EDF | 轨道/密度求值可独立对照；缺自旋信息、缺虚轨道、未实现 EDF 均准确报告 |
| G13 | `.chk` 外部转换 | 工具未配置、版本不匹配、非零退出码、空/坏 FCHK、包含空格/中文路径分别给出真实结果 |
| G14 | Blender 安装、导入、节点编辑、保存/重开、渲染 | 干净 Blender 环境可用；数值缓存、科学单位、节点值和外部文件定位保真 |
| O01 | ORCA 的日志、Cube、Molden/WFX 样例 | 能复用展示链；新来源的单位、轨道索引、spin 与基组约定通过对应验收 |

数值验收建议采用两层证据：先用可解析的人工小网格验证索引/单位/插值，再用有来源和生成条件的真实计算结果验证科学含义。MO 求值对比 Gaussian `cubegen` 时允许整个轨道统一反号，不能允许局部任意反号；简并轨道需注意轨道子空间旋转。误差容限应从输出精度、网格间距和独立参照推导，不能用“看起来相似”的截图替代。

真实文件候选可从 [cclib-data](https://github.com/cclib/cclib-data) 和 [IOData 测试数据](https://github.com/theochem/iodata/tree/main/iodata/test/data) 挑选；纳入本仓库前逐个记录来源版本、许可、计算方法/基组/电荷/多重度、预期字段和 SHA-256。合成网格负责边界测试，真实文件负责端到端科学验证。

## 仍需取得的证据

- Gaussian 16 当前官方原文或用户本地手册，用于补足本次官方站点抓取失败；特别是新增密度类型和输出变体。
- 被采用依赖的确切版本、许可材料、随包 wheels 的真实离线安装结果及 Blender 集成结果。
- 经允许使用的 Gaussian 配套样例（同一次计算的 log/fchk/cube/wfn/wfx）及独立 `cubegen` 数值参照。
- WFX EDF、磁场扰动、复杂相关密度和高角动量的实际覆盖；未验收前只能给出具体能力状态。
- 与 VMD/VESTA 对照的具体展示任务、节点交互和导出图像证据。
