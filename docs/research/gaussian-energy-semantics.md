# Gaussian 能量语义与 QCBlender 结果选择设计

核对日期：2026-09-22。本文定义单个 Blender 插件内部的结果数据契约与验收要求；当前已实现的规则和样本证据见 [验收记录](../VALIDATION.md)，未验证方法仍属于候选。`cbq_core` 仅作为代码与设计参考；数据转换、能量识别与展示在 QCBlender 内完成。解析库版本在锁文件中固定，必要依赖以扩展内 wheels 交付，不要求用户建立外部 Python 环境。

## 1. 结论与证据边界

能量必须同时回答“什么量、什么方法、哪个任务、哪一步、哪个态、是否收敛”。首版数据层应保存一组带来源的 `EnergyRecord`，结果面板再按用户选定的目标筛选。`SCF Done`、archive 中的 `HF=`、某个数组的最后一个数，都不能单独作为“最终电子能量”的定义。

本次完整阅读用户提供的 `docs/sobereva/谈谈该从Gaussian输出文件中的什么地方读电子能量.md`，原文链接为 [Sobereva 文章](http://sobereva.com/488)，本地文中最后更新时间为 2023-09-16。下文只采用可核对的输出语义；文章对方法和软件的价值判断不构成产品行为。

本次 Gaussian 官网 `mp`、`casscf`、`td`、`g4` 页面未能取得正文。可读取的一手资料是 Gaussian 09 原手册镜像，不能当作已经核对所有 Gaussian 16 版本。另核对了 cclib **v1.8.1** 的公开源码与数据表，以及本地 cclib checkout 中的 Gaussian 16 A.03 原始输出。证据区分如下：

| 证据 | 可支持的结论 | 不能证明的内容 |
| --- | --- | --- |
| 用户文章 | 待核对的标签、易混情形和研究线索 | 每个 Gaussian 版本、全部方法变体均适用 |
| Gaussian 原手册镜像 | 文档中明确的物理量、选项和输出示例 | 当前读取器已正确实现这些规则 |
| 固定版本 cclib 源码 | 该版本怎样抽取、转换或丢弃信息 | 全部真实日志都能解析、UI 的默认选择正确 |
| 实际 Gaussian 输出 | 该文件中确实出现的值、顺序、任务与标签 | QCBlender 已完成导入或科学验收 |

本文的 `EnergyRecord`、选择规则、状态与 UI 行为是 **QCBlender 设计提案**。方法覆盖的发布优先级由主设计确认；语义明确不等于该方法已经纳入首版。

## 2. 方法特定的选择规则

“电子总能量”在通常的 HF/DFT 语境下包括核间排斥项，不是仅有电子部分，也不包含振动零点能。Gaussian 原手册明确写出了 HF/KS 能量中的核间排斥项。[Gaussian 09 DFT 原手册镜像](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_dft.htm)

| 任务/方法 | 目标记录与参考记录 | 来源与未决边界 |
| --- | --- | --- |
| HF、普通 DFT | 经方法识别和收敛核对后，`SCF Done` 的值可以是目标电子总能量。记录完整方法/泛函与自旋限制形式 | [cclib Gaussian parser v1.8.1](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py) 有该值的读取路径；下文真实 B3LYP 文件也包含此行 |
| MP2 | 同一步 HF 值是参考；目标为完整 MP2 总能量，不能将二阶相关校正 `E2` 当总能量 | [Gaussian MP 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_mp.htm) 明示 `EUMP2`；不能根据标签里的 U 就自行改写文件已确定的受限/非受限方法 |
| 双杂化 DFT | 同一步 SCF 值是参考；B2PLYP 目标为 `E(B2PLYP)`，同时可保留相关校正。不要依据出现 MP2 类中间项把方法改名为 MP2 | [Gaussian MP 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_mp.htm) 明示双杂化的组成及 B2PLYP 最终标签；archive `MP2=` 别名目前由用户文章提供，仍需具体泛函/版本真实文件 |
| CCSD、CCSD(T) | 保留 SCF、MP2 等参考或中间值；以请求方法实际收敛的总能量作为目标。迭代中多次 `E(CORR)` 不等于多帧轨迹 | cclib 有 CC 路径；下文真实 CCSD(T) 文件同时出现多层能量。其它 CC 变体应逐条建规则 |
| CASSCF | 每个态各有记录；保存 active space、`NRoot` 和态平均权重。态平均目标与各态本征能量分开 | [CASSCF 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_casscf.htm) 规定 `NRoot=1` 是基态，`#P` 控制最终本征值/本征向量输出。文章给出的 CI 区块标签及 archive 中最高序号态的映射仍待真实样例，不能直接普遍采用 |
| TD-HF、TDDFT、TDA | 基态总能量、各激发能和选中态总能量是不同记录。保存源 root 编号、spin/symmetry；同一 root 在不同几何处不是已经证明的连续态身份 | [TD 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_td.htm) 规定 `Root=1` 为第一激发态。下文真实输出核对了目标态总能量与基态 archive 值 |
| AM1/PM3/PM6/PDDG 等半经验方法 | 匹配到已验证模型时按 `heat_of_formation` 记录，UI 展示“模型生成焓”；不能沿用通常的电子总能量标签 | [Semi-Empirical 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_semiempirical.htm) 明示所打印值的含义。旧实现可能使用不同输出标签，具体版本需真实用例；不能据此推广到一切半经验 Hamiltonian |
| AMBER/UFF 等 MM | 总值按 `force_field_potential` 保存，另记力场与参数来源，不自动与 ab initio 绝对能量合并比较 | [MM 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_mm.htm) 描述力场及分项。文章所述 `Energy=`/archive `HF=` 对应仍需具体日志；单独匹配 `Energy=` 无法确定物理类型 |
| G4/G4MP2/CBS 等完整组合任务 | 同时保存组合方法总结果、0 K 含 ZPE 的量、温度下内能/焓/Gibbs 能和中间计算。电子能可在已验证语义下由同一组合摘要的 `E0 - ZPE` 推导 | [G1–G4 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_g1.htm)、[CBS 原手册](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_cbs.htm) 区分这些量；精确 G16 输出变体仍待验收 |
| 组合方法的单点选项 | 只有识别实际 job mode 与该模式的标签含义后，才能赋予 `electronic_total` | 用户文章的 `G4MP2=SP` 及其能量标签是待验证规则；本次原手册页面没有核实该选项，不按字符串 `Energy` 通用推断 |

**archive 标签是文件字段名，不能代替方法。** 本次真实 TDDFT 输出中 `HF=` 对应 B3LYP 基态值；文章对 CASSCF、MM 和双杂化的 archive 映射应列为待验证的具体规则。归档值通常保留较少小数位，和正文不应要求浮点精确相等；比较容限来自两处打印精度。archive 只绑定其所属任务的末态摘要，不用于补齐前面每一步的轨迹。[真实 TDDFT 文件](https://github.com/cclib/cclib/blob/07260dd0394cb1a2381d4d897746d727a12ad6ce/data/Gaussian/basicGaussian16/dvb_td.out)

特别注意：完整 CBS-QB3 任务中的 `CBS-QB3 Energy` 是指定温度下的热校正能量；`CBS-QB3 (0 K)` 已含 ZPE。因此按“标签包含 Energy”挑选电子能会选错量。[CBS 原手册标签说明](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_cbs.htm)

## 3. cclib 的正确使用边界

本次核对的是固定发布标签 v1.8.1，采用它与否仍是依赖决策。其数据表中 SCF/MP/CC 能量为 eV，激发能为 cm⁻¹，热力学总值及 ZPE 为 Hartree/particle；内部单位转换必须逐属性指定。[cclib 1.8.1 数据表](https://cclib.github.io/data.html)

源码审查发现：

- Gaussian reader 分别抽取 SCF、MP、CC 结果；CC 路径会覆盖中间能量，只向结果追加最高层记录。
- 新一轮激发态输出会重置激发态列表；优化后重复打印的坐标会被裁剪。
- `SCF Done` 的方法分类逻辑不能直接作为 QCBlender 的完整方法识别器；在所查版本中，仅 `E(RHF)` 被该分支显式分入 HF，其余走另一分支。
- 在该文件中未找到 B2PLYP、CASSCF CI 本征值、G4 组合结果及 TD 总能量标签的专用读取路径。这是该文件的静态审查结果，不是对所有版本能力的断言。

这些行为见 [Gaussian parser v1.8.1](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py)。另外，Link1 的 `new_internal_job()` 会清除已有 MP 能量列表；这进一步说明一个最终 `ccData` 不能充当完整计算事件账本。[Logfile parser v1.8.1](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/logfileparser.py)

由此提出的 QCBlender 设计是：复用成熟读取器取得其确实提供的结果，同时由 Gaussian 适配层保留任务、事件和源位置，补充缺失的语义。不能对两个长度看似相同的数组直接 `zip`，也不能把某个库没有返回该属性解释为源文件没有该属性。具体实现采用局部扩展还是独立语义扫描，M0 用真实样例选择；不为此建立通用插件解析框架。

## 4. 插件内部的数据契约

`Calculation` 拥有原始来源、任务列表、几何帧、状态与结果。`EnergyRecord` 是其中的小型记录结构，不需要独立服务、数据库或另一个 Python 包。Blender 节点读取已经确定的值和单位，不能负责猜测 Gaussian 标签含义。

| 字段组 | 最小内容 | 约束 |
| --- | --- | --- |
| 身份 | `id`, `calculation_id`, `job_id`, 可选 `subjob_id`, `evaluation_id` | Link1 或组合子任务改变计算上下文；SCF 重试、CC 迭代与一个几何步内的附加求值不能混为一条 |
| 几何绑定 | `geometry_id`, 可选 `step_id`, `coordinate_frame_id` | 绑定不明确时允许空值并给出原因，禁止最近坐标或数组下标自动顶替证据 |
| 数值 | `value_hartree`, `raw_value_text`, `raw_unit`, `printed_precision` | 统一计算单位保留原值文本；`D` 指数按数值语法读取。缺失不是 0；NaN/Inf/截断数字不成为有效结果 |
| 物理类型 | `kind` | 至少区分 `electronic_total`, `excitation`, `zpe_correction`, `zero_point_total`, `thermal_correction`, `internal_energy`, `enthalpy`, `gibbs_energy`, `heat_of_formation`, `force_field_potential`, `correlation_correction`, `unknown` |
| 方法与角色 | `method_ref`, `role` | 方法指向完整 route/基组/ECP/溶剂/色散等上下文；角色区分 `target`, `reference`, `intermediate`, `iteration`，不依赖文件顺序确定 |
| 电子态 | `state_ref` | 保存源编号及编号规则、spin、symmetry、选中态；CASSCF 的 state average 另记所含态与权重，不冒充某一单态 |
| 修正与条件 | 可选 `correction_of`, `thermochemistry_ref` | 热校正明确修正哪个总值；温度、压力、同位素质量、频率缩放、模型与虚频情况位于共享热化学上下文 |
| 来源 | `source_id`, `line_start`, `line_end`, `raw_label`, `reader_version`, `rule_id` | 来源文件有 SHA-256、程序版本；显示能回到原始区块，避免把所有性质归到一个文件末尾 |
| 推导 | `derivation`, `operand_ids` | 原始直接值与计算值分开。推导用有限的已知操作，例如差值、单位转换；不执行来自文件的表达式 |
| 有效性 | `parse_status`, `association_status`, `calculation_status`, `validation_basis` | 语法成功、归属明确、计算收敛、科学规则已验收是不同事实 |

`method_ref` 应保留源 route 原文与能识别的规范化字段；例如 `CCSD(T)`、frozen-core/all-electron、限制形式和溶剂条件不能只压成 `CC`。未知部分保留为未知。用户给记录加备注可以补充语义，但不能覆写其原始方法与收敛状态。

熵不是能量，放在 `Thermochemistry` 中并带能量/温度单位，不塞进 `EnergyRecord.value_hartree`。频率计算的质量、温度、压力和近似处理也属于该上下文，不能只保留一个 Gibbs 数值。

## 5. 选择、推导与跨任务比较

结果面板的默认选择按以下顺序执行：

1. 明确用户当前选中的计算、job、结构步和电子态。未指定时可定位最近一个完整目标结果，并同时显示其任务身份与后续失败任务；不能把文件末尾失败隐藏掉。
2. 根据已验证的方法规则确定所需 `kind` 与 `role`。MP2、双杂化和 CCSD(T) 目标缺失时，保留可用参考值但不将其提升为目标。
3. 在同一 `evaluation_id` 下选择收敛目标，核对任务是否完成。电子 SCF 收敛与优化收敛分别展示；部分结果可浏览，但明确标为部分/失败任务数据。
4. 正文与 archive 均有同义结果时，核对上下文和打印精度，保留多个证据位置。冲突标为 `conflicting`；不能以“越晚越可信”掩盖冲突。
5. 只有派生关系经过该方法/任务规则验证后才建立派生记录。找不到唯一目标时返回原因和候选，不填 0、不取最低值、不跨任务回退。

Gaussian 的 Link1 job、内部 link 执行号、优化步、扫描点、IRC 点和电子迭代是不同层级。适配层先建立 job/evaluation 归属，再建立几何轨迹；相同坐标重复打印可以合并坐标内容，但不能合并两个不同计算事件。组合方法包含不同方法/基组的子计算，最终组合结果绑定到整体任务，不默认附属于“最后一个 SCF”。

建议支持的明确派生关系：

| 派生值 | 允许条件 | 禁止的默认行为 |
| --- | --- | --- |
| TD 目标态总能量 | 已确认同一几何/求值、相同响应/溶剂规则的基态与激发能；优先使用完整直接输出，再用关系核对 | 不能将任意前一个 SCF 加任意激发能；不把四位小数 eV 的激发能合成值冒充更高精度直接值 |
| 组合电子能量 `E0 - ZPE` | 同一组合摘要、ZPE 约定/缩放明确，保留两个操作数与方法规则 | 不用其它频率任务的 ZPE，不把温度下内能减 ZPE 当电子能 |
| 相对能量 | 用户明确参考记录，比较物理类型一致、方法与环境条件明确 | 不把不同方法/基组、不同热化学条件自动放到同一条可比曲线上 |
| 反应能/电离能等跨体系组合 | 用户显式定义反应、计量系数和各物种记录；检查物理量类型、方法与可用条件 | 不要求参与物种原子数相等，也不能只按文件名自动组成反应 |

溶剂、色散、counterpoise 和 ONIOM 会引入额外能量语义。首版若尚无对应规则，保存原始字段并标为具体语义未支持；不要把已经包含在目标总值中的修正再加一次。是否支持这些结果的自动比较，应作为单独产品边界确认。

动画与图表保存 `energy_record_id` 或明确的系列筛选条件。优化能量曲线的横轴是优化步，IRC 是源反应坐标，只有真正有物理时间的数据才能使用时间轴。几何节点可以显示当前步对应的数值或驱动颜色；科学值仍存于内部数据层，节点上的显示倍率和颜色范围不改变能量。

## 6. 状态与界面表达

不使用没有统计校准的“置信度 95%”。采用可解释的状态与理由：

| 维度 | 示例状态 | 行为 |
| --- | --- | --- |
| 读取 | `parsed`, `missing`, `unsupported`, `parse_error` | 区分源文件未给出、读取器暂不支持和坏记录 |
| 归属 | `matched`, `ambiguous`, `conflicting` | `ambiguous` 不自动进入轨迹或比较；用户可显式关联并留下依据 |
| 计算 | 电子/相关迭代 `converged/failed/unknown`；几何优化独立状态；job `normal/error/incomplete/unknown` | 正常终止不自动证明所有中间任务/波函数符合目标 |
| 规则依据 | `fixture_verified`, `documented`, `article_candidate`, `user_assigned` | 与数据本身分开；规则已做真实回归才能成为发布能力 |
| 可用能力 | `available`, `partial`, `unavailable`，附具体原因 | 目标能量缺失时可以展示坐标和参考能量，不虚报整个文件全部失败或全部支持 |

面板示例为“Job 2 / Step 5 / CCSD(T) 电子总能量 / Hartree / 来源第 n 行”，展开后显示参考 HF/MP2 值、方法条件和收敛证据。TD 面板同时显示基态能量、激发能和所选态总能量；热化学面板显示 E、E+ZPE、U、H、G，并附 T/P。默认标题不用含义不明的“能量”。

## 7. 本次真实输出核对

核对文件来自本机 `D:/workspace/ChemBlender_2_x` 的既有资料，仅只读检查，未复制到本仓库或执行解析器。源 cclib checkout 为 `07260dd0394cb1a2381d4d897746d727a12ad6ce`；此数据版本与上文静态检查的 parser v1.8.1 分开记录。

| 样例 | 实际观察 | 本次状态 |
| --- | --- | --- |
| [G16 A.03 dvb_td.out](https://github.com/cclib/cclib/blob/07260dd0394cb1a2381d4d897746d727a12ad6ce/data/Gaussian/basicGaussian16/dvb_td.out) | 第 85 行为 B3LYP/STO-3G TD 五态任务；第 446 行基态为 `-382.308266602` Hartree；第 643 行第一激发能 `5.3351` eV；第 655 行所选态总值 `-382.112205281` Hartree；第 946 行 archive HF 字段为基态舍入值；第 954 行正常终止 | 原始标签与归属逐行核对 **Passed**；QCBlender 导入 **Not Run** |
| [G16 A.03 water_ccsdt.log](https://github.com/cclib/cclib/blob/07260dd0394cb1a2381d4d897746d727a12ad6ce/data/Gaussian/basicGaussian16/water_ccsdt.log) | 第 82 行 CCSD(T)/STO-3G；第 305 行 HF `-74.9643287914`；第 342 行 MP2 `-75.002282127453`；第 381–429 行为多次 CC 迭代；第 437 行 CCSD(T) `-75.017760422` Hartree；第 497–499 行 archive 保存多层舍入值 | 原始标签与顺序逐行核对 **Passed**；QCBlender 导入 **Not Run** |

TD 文件本地 SHA-256 为 `c9255c92b829a4d2072ffca262be4dd9212f35a9c75d84c1fe8eb5969c166eef`，与既有 `examples/scientific-visualization/input-manifest.json` 一致。该清单记录上游路径、commit 与 BSD-3-Clause；正式复制测试数据时仍须附许可证并重新核对。网页工具未能抓取对应 raw URL，本次文件内容证据来自可读本地原件及清单，不声称远程下载验证成功。

## 8. 验收用例与实施顺序

下面是拟定验收用例，产品状态全部 **Not Run**。一个用例应同时核对原始输出、内部记录、UI 选择和持久化后的结果；库测试通过不替代插件测试。

| 编号 | 输入/边界 | 必须观察到的结果 |
| --- | --- | --- |
| E01 | HF 与普通 DFT，各有正文/archive | 方法来自上下文；目标值正确；archive 别名与打印精度正确 |
| E02 | MP2 含 SCF、E2、EUMP2 | 三者按 reference/correction/target 保存；默认目标为 MP2 总值 |
| E03 | B2PLYP 及一个带色散双杂化变体 | 最终目标不取 SCF；方法名、修正包含关系与 archive 别名逐变体验证 |
| E04 | CCSD(T) 含 MP2/CCSD 迭代 | 保留需要的参考值，目标为收敛 CCSD(T)；迭代数不改变几何帧数 |
| E05 | CASSCF 单态、多态、态平均；有/无 #P | root 约定、态/权重、缺失本征值均正确；不把最后一个态当所有态 |
| E06 | TD 两个 root、多个几何求值 | 每步激发态不被最终列表覆盖；所选态总值、基态与激发能区分；编号不暗示已完成跨步态追踪 |
| E07 | AM1/PM6 及 MM | 各自物理量标签正确；`Energy=` 不造成跨模型误分类 |
| E08 | G4MP2 与 CBS-QB3 完整任务、单点模式 | E0、ZPE、U/H/G 和目标电子能分开；未验证 SP 模式不能套完整任务规则 |
| E09 | Opt→Freq→更高水平 SP 的 Link1 | 每段方法/能量/几何独立；热校正的转用必须显式创建派生关系 |
| E10 | SCF 已收敛但 MP2/CC 阶段失败；优化未收敛；文件截断 | 已有结果可读，目标结果缺失原因准确，不能回退冒充完成 |
| E11 | 扫描/IRC、重复 orientation、一次几何多个能量 | 曲线逐点绑定正确，源步骤/方向保留，不按数组长度配对 |
| E12 | Fortran D 指数、相同量的不同打印精度、正文/archive 冲突 | 数值语法严格；舍入差异允许，真实冲突可见；错误不得填零 |
| E13 | 两个温度/压力的热化学摘要、同位素/缩放变化 | 热化学上下文不串段；不同条件默认分组，不能只保留最后一组 |
| E14 | 导入后保存、重开、源文件移动 | 保留已选记录、原始标签、单位、来源定位与推导操作数 |

M0 固定 E01/E02/E03/E04/E06/E09/E10 的真实样例与期望语义；缺少双杂化等样例时明确列入缺口。M1 建立任务/几何归属，M4 完成方法特定能量选择。E06 的跨几何态追踪、E11 轨迹曲线，以及复合方法推导和跨计算比较属于后续路线；保存源任务/步/态身份仍是首版要求。

用户已确认首版 HF/DFT 求值并保留区分 MP2、双杂化、CCSD(T)、TD 等已读取能量。所有读取结果保留来源/单位/身份；未经真实样例验收的方法规则不自动选择目标，具体诊断为未支持。热化学原始量可保留，反应能组合、跨任务修正、态追踪及 ONIOM/counterpoise 等自动分析作为后续能力，见 [主设计](../QCBLENDER_V1_DESIGN.md)。
