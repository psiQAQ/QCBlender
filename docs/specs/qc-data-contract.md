# 插件内通用量子化学数据契约

数据层由 `qcblender/data.py` 的 `Dataset(metadata, arrays)` 实现。metadata 为字典，arrays 将名称映射到 NumPy 数组；下表描述实际字段，不要求建立同名实体类。科学读取与求值不导入 `bpy`，Blender 层负责对象生命周期。

## 1. 数据与接口

| 内容 | metadata / arrays | 约束 |
| --- | --- | --- |
| 来源 | `source`、`selected_job`（适用时） | 文件名、SHA-256、格式/解析器和计算段，路径不作身份 |
| 结构 | `coordinate_unit`、`atomic_numbers[N]`、`positions[N,3]` | Å；原子顺序固定，缺失信息不补零 |
| 键 | `bonds` 元数据与 `[K,2]` 数组 | 距离/元素半径推断，用于显示，不是键级 |
| 轨道与基组 | `orbitals`、`basis`；`mo_coeffs[nAO,nMO]`、`mo_occs[nMO]`、可用 `mo_energies[nMO]` 及壳层数组 | 保留受限/非受限身份、通道数量、AO 约定、源编号从 1 开始 |
| 密度矩阵 | `density_matrices` 中的 `kind`、`array` 引用 | `[nAO,nAO]`，求值还须核对方法和密度层次 |
| 标量场 | `fields` 中的量名、单位、网格参数与数组引用 | 每场 `[nx,ny,nz]`，可选同形有效掩码；多 Cube 数据集分别保存 |
| 电荷与偶极 | `charges`、`dipole` 中的量名/单位/数组引用 | 电荷 `[N]`，偶极 `[3]`，保持布居方法和原点 |
| 振动 | `modes` 及 `mode_*` 数组 | 频率 `[M]`、位移 `[M,N,3]`；原始记录与归一化显示位移分开 |
| 优化轨迹 | `optimization`、`optimization_positions[S,N,3]` | 每步保留构型、明确关联的能量、收敛表和原文位置；`positions` 仍为最终构型 |
| 标准XYZ多帧 | `trajectory`、`trajectory_positions[F,N,3]`、`xyz_frames` | Å；每帧同原子数/元素顺序，帧号从1起；`positions`为第一帧，无优化/IRC/时间语义 |
| 能量 | `energies` 及日志计算记录 | 方法、目标/参考/校正、状态与源位置；见第 4 节 |

实际入口为 `readers.read_source(path, job_index=0)`、`association.compare_sources(reference, moving, allow_rigid=False, tolerance_angstrom=1e-3)`、`evaluate.evaluate_field(data, grid, quantity, spin='alpha', orbital=1, memory_mb=512, ...)`。Blender 使用 `views.atom_view(directory)`、`views.field_view(directory, parent=None, index=0)` 接入落盘 Dataset。

非法 shape、非有限数据和身份不匹配返回具体诊断；缺字段表现为缺失能力。独立优化视图仅携带该步结构与轨迹记录，不继承最终构型的电荷/偶极/场。旧工程没有逐步数组时不合成步骤。

标准XYZ接收元素符号或1–118原子序数与三个有限坐标；拒绝未知/dummy元素、额外列、截断、NaN/Inf以及扩展Properties/Lattice/PBC。原始UTF-8注释、文件SHA和逐帧SHA、来源行区间保留；IOData列适配器直接读取Å值，帧间空行只在解析副本中规范化。`trajectory`保存`kind='xyz'`、`array='trajectory_positions'`、`coordinate_unit='angstrom'`及`frames`；每帧有`frame/comment/sha256/line_start/line_end/coordinate_line_start/coordinate_line_end`。

`scientific_geometry(data, kind='trajectory', step=frame)`返回当前帧不可写坐标和来源记录；Blender对象用`qc_trajectory_frame/count/record`记录离散选择。切帧保留原子ID/顺序、POINT属性、选择、材质/节点和标注，并按当前科学坐标重新推断连接。不推断能量、轨道或波函数，不插值/播放。科学来源关联对多帧XYZ明确拒绝，单帧仍按真实构型核对。

## 2. 通用场与单位

每个 `metadata['fields'][i]` 平铺保存 `origin[3]`、`steps[3,3]`、`shape[3]` 和 `coordinate_unit`；没有额外的 `grid` 子对象。求值请求通过独立 `grid` 参数传入同一组网格参数。约定步向量为矩阵行：

\[
\mathbf r(i,j,k)=\mathbf o+[i,j,k]A.
\]

数组 `values[i,j,k]` 对应这个采样点。`origin` 指索引零的采样点，不额外加半个 voxel；格式若定义中心/角点差异，由读取器明确转换。非正交、左手/右手变换、各向异性网格保留完整仿射变换。

科学工作坐标使用 Å，长度换算常量集中定义并标明来源/版本；轨道求值时转换为 Bohr。场值单位不会因位置由 Bohr 转 Å 就自动变化。典型量纲：

| 场 | 内部标识 | 源原子单位示例 | 语义限制 |
| --- | --- | --- | --- |
| 实值轨道振幅 | `orbital_amplitude` | `bohr^-3/2` | 正负是波函数相位，不是电荷；不能平方后保留同标签 |
| 电子密度 | `electron_number_density` | `electron/bohr^3` | 区分总/Alpha/Beta，保留密度理论层次 |
| 自旋密度 | `spin_density` | `electron/bohr^3` | 保存具体约定，例如 alpha-minus-beta |
| 静电势 | `electrostatic_potential` | `hartree/e` | 与静电势能区分，场符号约定必须保留 |
| 未知标量 | `unknown_scalar` | 未知 | 可绘制一般标量面，定量积分/比较先补全含义 |

源数据保留 float64；显示体网格采用 float32 时保留转化记录。网格体元由行列式计算，先换成与场值分母一致的长度单位。等值面不能代替电子密度积分。

Cube 的原子行中核电荷信息不直接映射为“原子部分电荷”。文件名不确定 HOMO/LUMO、场类型或电荷方法。负原子数轨道数据与多标量数据分别保留数据集编号；这些数组不自动解释成矢量场。

### 波函数求值契约

求值限于支持的非周期实值全电子 HF/DFT 结果，不执行新的 SCF。输入 Dataset 提供构型、基组、系数和可用密度矩阵；请求指定物理量、自旋、轨道源编号、网格和内存预算。结果记录后端、输入摘要及科学参数；Gaussian 源编号与数组下标分开。

原子轨道基函数（AO）记为 χ，分子轨道（MO）记为 ψ。对实值基组，采用：

\[
\psi_{i\sigma}(\mathbf r)=\sum_\mu C_{\mu i\sigma}\chi_\mu(\mathbf r),\quad
P_\sigma=C_\sigma\operatorname{diag}(n_\sigma)C_\sigma^T,\quad
\rho_\sigma(\mathbf r)=\chi(\mathbf r)^T P_\sigma\chi(\mathbf r).
\]

其中 σ 为 Alpha/Beta，n 为该通道实际占据。总密度为 ρα+ρβ，自旋密度约定为 ρα−ρβ。受限闭壳层可共用空间轨道，但总占据 2 不能再对每个通道乘 2；受限开壳层按已验证电子数/占据拆分，缺证据时报通道信息不足。优先使用具有正确方法/态身份的密度矩阵，不能把 post-SCF 请求悄悄替换成 SCF 密度。

所有系数与密度矩阵必须跟随同一 AO 排序、归一化和坐标变换。覆盖及独立参考以 [VALIDATION](../VALIDATION.md) 为准；超出后端支持的角动量、复数、周期、未知占据/基组约定返回具体原因。HOMO/LUMO 由通道和占据决定，不由文件名或电子总数的一条通用公式决定；分数占据和简并情况展示实际占据及可选集合。

全电子体系的静电势在原子单位下定义为：

\[
\Phi(\mathbf r)=\sum_A\frac{Z_A}{|\mathbf r-\mathbf R_A|}
-\sum_{\mu\nu}P_{\mu\nu}\int\frac{\chi_\mu(\mathbf r')\chi_\nu(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d\mathbf r'.
\]

这里 P 为总电子密度矩阵，零势参考在无穷远；Φ 的单位为 Hartree/e。采用成熟后端的库仑积分，不用有限显示网格上的点电荷求和代替连续密度积分。该计算路线与本次只读核对的 [PySCF cubegen 源码](https://github.com/pyscf/pyscf/blob/c63a953ba603a5ad8c1d65d88da72aaf05ede4d8/pyscf/tools/cubegen.py) 一致；它是独立实现参考，不是本项目已选择或安装的依赖。

核奇点和数值不可靠近核区域用记录了半径/原因的有效域掩码表示。数组存有限占位值，但无效项不得参与定量采样/图例/积分；插值要求所有邻点有效。ECP、幽灵中心、复轨道和超出支持范围的基组组合明确拒绝；不声称重建全电子近核密度。溶剂反应场等额外势需要另有来源，默认分子 ESP 不包含它们。

网格范围与实际步长由用户控制，预览预设只是初值；扩展到包围盒外一定距离不能证明弥散尾部收敛。开始前预估输出、AO 块、积分中间量及显示副本内存，超过预算时报告并允许调整。MO/密度按点分块，ESP 块大小还考虑 AO 对积分开销；取消在块间响应，工作进程退出后不发布未完成数组。

至少用以下数值证据验收：`CᵀSC≈I`（S 为 AO 重叠矩阵）、`Tr(PS)` 与电子数一致、独立参考点及完整小网格比对、总/自旋积分随范围和步长收敛、ESP 的核项/电子项及带电体系远场趋势。MO 比对允许整体反号；简并集合比较对应子空间。网格积分将体元换成 Bohr³；容差结合参考打印精度与收敛实验确定，随验收记录保存。

## 3. 多文件关联与坐标变换

用户显式选择参考和移动 Dataset 后，`compare_sources` 核对原子顺序、已知电荷/多重度与构型；默认坐标容差 1e-3 Å。可选择刚体旋转/平移，不自动搜索原子置换。单中心和线性结构不能唯一确定方向，拒绝自动刚体配准。记录保留变换、坐标误差与各来源摘要，不能据几何相同推断方法相同。

View 的布局变换与科学配准分开：移动对比图中的整个对象只改变展示位置。默认 **1 Å = 1 Blender unit**；所有相关 View 使用同一显示变换。相互关联的体对象存在额外缩放时，采样坐标先转换到被采样网格的局部空间。

## 4. 能量数据与选择

电子总能量、MO 能量、激发能、热校正和 Gibbs 自由能是不同量。对 HF/常规 DFT 可识别目标 SCF 能量；MP2/双杂化/CCSD(T) 必须保留参考 SCF 与目标结果；CASSCF/TD 绑定电子态；组合方法识别专属摘要。

能量语义及完整概念字段表见 [能量设计第 4 节](../research/gaussian-energy-semantics.md#4-插件内部的数据契约)：`kind`、`value_hartree`、`method_ref`、`role`、计算/job/evaluation/几何/态引用、源位置及各项有效性。热力学上下文增加温度、压力、校正方案及对应电子能量；派生量保存已知操作与输入 ID。

规则以方法/任务/态/步骤匹配唯一目标，不按数值大小选择，也不统一取最后一条。规则不覆盖、多个候选或正文/archive 不一致时，列候选和来源，等待用户指定；保留“未识别目标方法能量”。未收敛结果即使能解析也不作为已完成目标数据。

原始 Gaussian 能量通常以 Hartree 输出，但 cclib 的若干公开数组以 eV 输出，适配时按照库契约换算并保留原值。多条能量与几何数组长度相等，也不能据此认定逐项对应。实现与逐方法用例见 [能量设计](../research/gaussian-energy-semantics.md)。

## 5. 原子属性、振动和光谱

原子数组索引在同一结构序列内稳定，显示标签编号与底层数组索引单独记录。推断键包含推断方法、半径表与阈值；片段选择是显示集合，不能据此声称已分解电子密度。

振动位移保存源约定和一次性的规范化结果。节点使用规范化位移做 `R=R0+A*d*sin(phase)`；`A` 与播放速度是展示参数，原始频率保持不变。虚频保留符号；静态电子场保持在对应平衡构型，不随振动原子扭曲成“时变轨道”。

IR保留原始频率/强度列表及源模式身份，可显式导出CSV。振动播放与位移箭头继续使用正常模式；原始IR强度不由动画推断。Raman活性不是Raman强度，当前未提供模拟Raman光谱或温度展宽处理。

分子偶极保存物理矢量、单位和源坐标原点。带净电荷体系的偶极依赖原点；改变显示箭头锚点只改变绘图位置。物理方向箭头作为默认，化学示意方向若提供，应有独立标签。

## 6. 插件内部持久化

采用插件内的版本化 JSON manifest + NumPy 数组，借鉴 CBQ 的可校验数组与来源记录。名称为 `qcblender.project`，初始 schema `0.1`；它是本项目内部工程契约，不宣称是行业统一交换标准，也不直接宣称兼容 `.cbq`。

工程保存为 `<name>.blend` 和 `<name>.qcdata/`。目录根 `manifest.json` 为 `qcblender.scene` schema 0.1，索引 `datasets/<manifest摘要>/manifest.json`；每个 Dataset 内为 `qcblender.project` schema 0.1，包含 `arrays/<hash>.npy` 及字段记录引用的 VDB。这影响的是工程文件组织，安装仍然只有一个扩展。VDB 可从科学网格重建；Blender 节点树和材质仍保存在 `.blend`。

- `.npy` 用 `allow_pickle=False`，限制 dtype、维度、元素数与内存预算，检查有限值及内容摘要。
- manifest 路径为相对路径，拒绝 `..`、绝对路径和逃逸根目录的链接。
- 源文件可以另存原件引用；保存规范化数据后，打开已保存结果无需源程序或源文件仍在线。
- 更新在任务目录生成完整候选、校验后原子替换 manifest；异常/取消不覆盖最后成功状态。
- `.blend` 保存项目 ID、schema、相对位置和内容摘要。缺失时明确显示并支持重定位，不创建空数据替代。
- 项目“打包”将配套目录和 `.blend` 一起归档，不默认把大型数组编码进 Blender 自定义属性。

配套保存、原地/中文移动目录冷重开和缓存恢复的当前证据见 [VALIDATION](../VALIDATION.md)。

### 显式CSV数据导出

工程与诊断的“导出数据”按当前Dataset提供`IR/optimization/IRC/Mayer/profile/paired/ESP_AREA`。UTF-8 CSV逐项保存已有值，metadata.json记录源文件/Dataset摘要、量/单位、原始网格、有效掩码语义、筛选范围和列角色。profile保留端点、距离Å、valid与无效值空白；paired全量/筛选导出逐个有效体素及原索引，筛选后仍保留原数组；ESP_AREA保留完整源bin边界/中心/面积/percent，百分比不归一化。优化/IRC/Mayer按完整源步骤/原子对导出，不用当前面板行替代全表。

跨工程Addon偏好`数据导出目录`使用绝对路径；留空时取已保存.blend父目录，否则取Windows真实系统Documents（包含系统重定向）。对话框`Output directory`可单次覆盖。每次在目标目录创建唯一结果子目录，先写完整暂存结果，成功后提交；取消/失败清理本次暂存，不覆盖已完成结果。导出目录不替代worker缓存或.qcdata。

新建IR、IRC/Mayer、profile、paired和ESP面积记录不生成二维棒图、曲线/游标、剖面坐标轴、散点或柱图；三维构型/振动、场/切片/等值线/图例、AIM空间路径与数据表仍保留。旧工程图形不自动删除，其源Dataset仍可导出。本批界面/截图/保存与冷重开验证状态见[本批验证索引](../acceptance/display-xyz-export-validation.json)。

## 7. 缓存与状态

`worker.py` 的求值缓存身份包括输入 Dataset manifest 摘要、网格、科学参数、后端及求值器源码摘要、NumPy 和 Blender 版本；内存预算不改变场的科学身份。缓存命中后仍校验 Dataset 与 VDB；损坏缓存按实际错误记录后重算。等值、颜色和视图布局不使科学场失效。

计算状态、能力诊断和 worker 执行状态各自保留。worker 最终状态为 `succeeded / failed / cancelled`，执行成功不等于科学正确或独立人工验收通过。后台结果不包含 `bpy` 对象，由主线程校验并接入；取消及过期操作不得覆盖新的选择。

## 8. 数据契约的最小证据

不对每个字段机械建测试；按照会造成科研误解的路径验收：

| 场景 | 必须发现或证明 |
| --- | --- |
| 斜轴/非立方 Cube | 八角点、非中心采样点、符号、axis/dataset 次序正确 |
| 同名不同构型 | 不能自动关联轨道场；有明确不匹配信息 |
| DFT archive HF / 双杂化 / TD | 方法、reference/target 与电子态不混淆 |
| 电荷字段缺失 | 显示不可用，不用核电荷或零填充 |
| 虚频模式 | 原始标签与规范化位移正确，动画振幅不改科学记录 |
| 冷重开/移动/取消 | 有效数据和节点设置保留，失败不损坏上次成功状态 |

数据层已由 `qcblender/data.py`、读取器、求值器和工程模块实现；当前实际覆盖及未验收条件见 [验收记录](../VALIDATION.md)。本契约中的概念实体可由 manifest 字段与数组表达，不要求建立同名 Python 类。
