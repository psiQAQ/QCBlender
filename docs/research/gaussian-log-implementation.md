# Gaussian Log 最小解析入口与验收样本

核对日期：2026-09-22。目标：M1 的构型/属性导入与 M4 的能量来源、振动/IR。已在 Blender 5.1.1 自带 CPython 3.13.9 中加载仓库 `outputs/science/` 的 cclib 1.8.1，实际解析 8 个真实 Gaussian 输出。研究脚本/结果位于 `outputs/log-fixtures/`；本文不表示产品适配器已实现。

## 1. 最小实现建议

采用一层小型 Gaussian 适配：**带全局行号的分段扫描 → 每段调用 `cclib.parser.Gaussian(StringIO(...)).parse()` → 单位/完整性验证 → 结果对象**。cclib 负责成熟格式区块；适配层扫描明确的 job 边界、route、终止标记和能量事件，保留原始来源。不要依赖最后一个 `ccData` 重建多任务事件账本。[Gaussian parser v1.8.1](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py)、[多任务清理逻辑](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/logfileparser.py)

首个验收入口只承诺：选择一个明确计算段，显示该段末个已解析构型及其状态，读取该段可用电荷/偶极/模式/IR，并展示带源行的能量。优化动画、每步性质映射仍按既定后续范围处理。

## 2. 可直接复用的字段与必须修正的语义

| 字段 | cclib 实际内容 | QCBlender 接入要求 |
| --- | --- | --- |
| `atomnos`, `atomcoords` | 原子序数；`(nframe,natom,3)`，Å。Gaussian 通常取 Standard orientation，缺失时可能用 inputcoords | 读取选定段的 `atomcoords[-1]` 仅表示末个已解析构型，不宣称优化成功；记录 orientation。与 FCHK 关联时不能只靠原子数相同 |
| `charge`, `mult`, `atommasses` | 电荷、多重度、质量 | 缺失显式 unavailable，不能默认中性单重态；同位素质量进入振动上下文 |
| `atomcharges` | scheme→长度 N 数组；可见 `mulliken`、`lowdin`、`apt`、`natural`、`hirshfeld`、`cm5` 等 | 保留 scheme；`*_sum` 是把 H 合并到重原子的另一种量，不能作为普通逐原子电荷默认项。所有字段验证 shape 与 finite |
| `atomspins` | scheme→逐原子自旋布居 | 与空间自旋密度区分；源未给出时不从电荷推测 |
| `moments[0]`, `moments[1]` | Gaussian reader 将原点设为 `[0,0,0]`；偶极直接读取标题注明 **Debye** 的 X/Y/Z | **不能使用数据总表中的笼统 a.u. 标签。** 保留 Debye 或用固定常数转 e·bohr；源坐标系、原点和带电分子平移效应必须保留 |
| `vibfreqs` | `(nmode,)`，cm⁻¹；保留负频率 | 负值作为虚频标记，不取绝对值冒充稳定振动 |
| `vibdisps` | `(nmode,natom,3)`；Gaussian 标准/高精度模式区块 | 保存 Gaussian 原始归一化约定。cclib 数据表称 delta Å，但展示振幅由用户控制，不把该向量当某温度下实际振幅。与同段构型保持坐标系一致 |
| `vibirs`, `vibrmasses`, `vibfconsts` | km/mol、Da、mDyne/Å | IR 与 frequency/displacement 按模式索引共同验证。NaN 或缺失强度不画成强度 0 |
| `metadata`, `optstatus`, `optdone` | 方法提示、版本、basis、终止及优化信息 | 正常终止、SCF 收敛、优化收敛分别记录；方法不能仅取 metadata['methods'][-1] |

字段/单位参考：[cclib 1.8.1 数据表](https://cclib.github.io/data.html)。其中 `moments` 单位需以特定 reader 和原输出核对：Gaussian reader 第 441–455 行直接保存 Debye，未做转为原子单位的转换。实际水 HF 文件解析得 `moments[1]=[-0.0,-0.0,-1.7093]`，与日志 Debye 值相同。[固定实现](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L441)

其它影响结果归属的实际行为：

- `Natural Population` 只在 `natural` key 尚不存在时读取，因此同一段重复 NPA 结果可能保留第一次，不能概括为“所有电荷均是最终构型电荷”。首版若一个段出现多次 NPA，应标记归属不明确，或另做有来源位置的窄区块提取。[NPA 分支](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L2264)
- 高频精度区块优先提供位移；普通频率区块再提供频率和 IR，最后 high-precision displacement 覆盖普通 displacement。手写扫描不能把两套区块拼成两倍模式。[频率分支](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L1384)
- IR 中无法转换的字段被 cclib 转成 NaN。适配层必须显式报告，不能默默吞掉。[IR 读取](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L1454)
- Gaussian 的 forces 与 moments/vibdisps 可能不同 orientation；cclib 对 gradients 做旋转不意味着任意用户坐标都已适配。FCHK/Log 跨文件坐标关联必须依据原子序和已验证刚体变换。[解析后处理](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L169)

## 3. Link1 与终止标记

明确的内部 job 分段标记为 `Link1:  Proceeding to internal job step number  N.`，这是 cclib 自身调用 `new_internal_job()` 的条件。`Entering Link 1`、`Leave Link 1`、l101/l502 等是程序内部执行链，不等于新的用户计算段。新拼接进来的完整 Gaussian 启动头 `Entering Gaussian System, Link 0=...` 可作为另一种边界，但应另设拼接文件测试，不将它与 Link1 当同一格式。[分段条件](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L216)

实际验证 `water_neutral_nbo_opt_freq.out`：

- 第 1–1090 行为优化段，1090 行正常终止；独立解析得到 `(4,3,3)` 构型数组，无振动模式。
- 第 1091 行开始 Link1；第 1093 行 route 为 `RHF/STO-3G Freq`，末尾 1726 行正常终止；独立 `Gaussian(StringIO(...))` 解析得到 `(1,3,3)` 构型和三种模式。
- 第二段没有程序版本头，独立解析不会得到 `package_version`。适配层可从同一原文件的全局头继承程序版本，并记录证据来自文件头；不要伪造重复源行。
- 该文件整个解析得到 5 帧，与分段 4+1 一致只是这个样例的事实。一般情况下 cclib 会裁剪重复 orientation，不能用数组长度给事件硬配对。

`Normal termination of Gaussian` 应结束当前段；`Error termination` 表示当前段失败；缺少终止为 incomplete/unknown，保留已有数据。cclib 全文件 `metadata['success']` 在看见一次 Normal termination 后即设 True，不能代表后续段成功；`new_internal_job()` 只删除 mpenergies，不完整重置属性。先分段能够避免大部分串段，但没有独立输出构型的 `Geom=Check` 段仍需明确继承关系，不能直接套用最后一帧。[success 分支](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L2535)、[new_internal_job](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/logfileparser.py#L247)

## 4. 能量行的最小语义扫描

已有 [能量契约](gaussian-energy-semantics.md) 是选择规则依据。以下目标条目均需保留原文、全局行号、段号、量类型、方法和角色；每次匹配能量都追加，不按浮点值去重。

| 样例 | 真实源行及数值（Hartree） | 最小验收 |
| --- | --- | --- |
| `water_mp2.log` | 306: SCF `-74.9643287914`；342: E2 `-0.03795333610`、EUMP2 `-75.002282127454` | reference / correlation_correction / MP2 target 三者分开，D 指数正确 |
| `water_ccsdt.log` | 305: SCF；342: EUMP2；381–429: 七次 E(CORR)；437: CCSD(T) `-75.017760422` | 迭代记录不制造构型；CCSD(T) 是请求目标，不能取末个 SCF |
| `dvb_td.out` | 446: B3LYP ground `-382.308266602`；643: root1 excitation `5.3351 eV`；655: TD target total `-382.112205281` | excitation 与 electronic_total 分开；同时保存 root 和 spin/symmetry；不用舍入激发能替换直接总值 |
| issue746 DSDPBEP86 | 380: SCF `-851.035605442`；404: E2(DSDPBEP86) `-1.398086059`、E(DSDPBEP86) `-852.43369150131` | cclib 实测只返回 SCF，适配层补 final double-hybrid label；保持方法为 DSDPBEP86。文件含 SMD，额外修正不能擅自重复相加 |

SCF/MP/CC 的 cclib 数组为 eV，原始正文为 Hartree；为了保留打印精度，能量事件直接从原行取值，cclib 数组用于交叉检查。CC 的最终数组只保留最高层结果；TD 列表可能被新求值覆盖，不能作为完整事件来源。[能量读取实现](https://github.com/cclib/cclib/blob/v1.8.1/cclib/parser/gaussianparser.py#L977)

双杂化附件来自 [cclib issue 746](https://github.com/cclib/cclib/issues/746)，报告者提供的实际标签与下载文件一致。它验证 **DSDPBEP86 此文件**，不等于 B2PLYP 及所有双杂化变体已验收；B2PLYP 真实样本仍是缺口。

## 5. 已下载清单

`outputs/log-fixtures/manifest.json` 保存完整固定 raw URL、SHA-256、字节数；`inspection.json` 保存本次 cclib 的 shapes、属性名和 metadata。

| 文件 | 固定来源 | SHA-256 | 实测 |
| --- | --- | --- | --- |
| water_mp2.log | cclib `07260dd0394cb1a2381d4d897746d727a12ad6ce`，data/Gaussian/basicGaussian16 | `9a93eac63dba161d4973494df296ff4e62bd1f3c97da6e519df97df172bade74` | 3 原子、SCF/MP2、Mulliken、dipole |
| water_ccsdt.log | 同上 | `b0b99ae2c142931cbcdc76a035ce719e4fc068a83c8d9cb610105eaae9527b2c` | 3 原子、CCSD(T)及中间方法 |
| dvb_td.out | 同上 | `c9255c92b829a4d2072ffca262be4dd9212f35a9c75d84c1fe8eb5969c166eef` | 20 原子、5 激发态 |
| dvb_ir.out | 同上 | `bc1a21de15ada135d5188b11d44226389022d92488ddfa8163ba7d4d713e5061` | B3LYP/STO-3G、54 模式，含高精度位移 |
| water_neutral_nbo_opt_freq.out | cclib-data `a16cc80ea29e8baec60abd0df346ce6862f52531`，Gaussian/Gaussian16 | `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519` | RHF/STO-3G，2 段；频率 2169.7613/4141.3837/4392.5759 cm⁻¹ |
| water.log | 同一 cclib-data，Gaussian/Gaussian16 | `3c5aa038823d5b84b9c314286a7a3d8f13a68bacea3a0028b1a4d21202693f3d` | PBE1PBE/6-31G(d,p)、IEFPCM/toluene，2 段；3 模式 |
| benzene_HPfreq.log | 同一 cclib-data，Gaussian/Gaussian09 | `38397a99e6b92295fe4ad5fd6cca3f3a4363439ae09d302f78daeae20db7bdc9` | 30 模式，高精度与普通区块去重；方法实际是 AM1，不能当 DFT 能量基准 |
| issue746-dsdpbep86.log | https://github.com/cclib/cclib/files/3231956/g16.log | `a43082b35aa8ea3c91a9ca242450bb6585a9c187dcef369d81c081499a7b7768` | Gaussian16 B.01、30 原子；缺失双杂化目标解析已复现 |

固定目录入口：[cclib basicGaussian16](https://github.com/cclib/cclib/tree/07260dd0394cb1a2381d4d897746d727a12ad6ce/data/Gaussian/basicGaussian16)、[cclib-data G16](https://github.com/cclib/cclib-data/tree/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian16)、[cclib-data G09](https://github.com/cclib/cclib-data/tree/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian09)。

许可证边界：cclib 主仓库提供 BSD-3-Clause [LICENSE](https://github.com/cclib/cclib/blob/07260dd0394cb1a2381d4d897746d727a12ad6ce/LICENSE)，可随主仓库来源的回归样本保留该许可证与归属。此次 cclib-data 树未发现 LICENSE/COPYING，README 只描述回归数据用途；issue 附件也没有单独许可声明。后两类可用于用户授权的本地下载验收，本次不把它们默认为主仓库 BSD 授权并提交原文件；在明确许可前保留 URL/hash/下载步骤即可。

## 6. 实施检查顺序

1. HF 小水 Link1：独立解析两个段；选中频率段有 3 个 mode、3 个 IR 值、`(3,3,3)` 位移，偶极 Debye 正确。保存重新读取后段身份与源行不变。
2. DFT `dvb_ir.out`：高精度/普通区块最终只有 54 模式；频率、IR、displacement 索引一致，实际属性单位明确。
3. MP2、CCSD(T)、TD、DSDPBEP86：核对表中的正文行数值/角色；缺失目标不得提升参考 SCF 为 target。
4. 对真实文件建立明确标识的截断变体：前段成功、后段未结束；确认整文件不能显示全部成功，已有数据仍可浏览。变体与原始下载样本分别记录。

本次状态：固定下载与哈希 **Passed**；8 个文件 cclib 解析 **Passed**；水 Link1 两段独立 StringIO 解析 **Passed**；DSDPBEP86 的 cclib 目标能量覆盖 **Failed（已复现缺口）**；QCBlender Log 适配、UI、保存和振动联动 **Not Run**。
