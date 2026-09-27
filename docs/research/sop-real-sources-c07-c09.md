# C07–C09 真实分析来源核查

核查日期：2026-09-27。C07 已由本研究生成真实 IGMH/IRI 成对 Cube；C08/C09 由主任务生成真实 ESP 表面与 AIM 输出，并在本研究中完成来源、原值、单位和独立数值核查。本文的 `Passed` 只覆盖明确列出的计算与读取检查；Blender GUI、移动后冷重开及独立人工签署由主任务分别记录。

## 已取得的第一手材料

原档、HTTP 响应头、逐文件摘要均保存在 `outputs/v1-acceptance/sources/c07-c09-research/`。其中 `download-manifest.json`、`iri-blog-manifest.json` 和 `extracted-manifest.json` 可复核下载版本和字节数。HTTPS 端点在本机返回 TLS/连接错误，原作者 HTTP 端点可用；以下 SHA-256 固定本轮所用内容。

| 材料 | 作者来源 | 字节数 | SHA-256 |
| --- | --- | ---: | --- |
| IGMH 教程原档 | [IGMH_tutorial.zip](http://sobereva.com/multiwfn/res/IGMH_tutorial.zip)，Last-Modified 2025-11-24 | 7,587,615 | `8b54bf3e4fa34ea9e95eb08b176f0f52dc32f3a907c0dddc97d31094c54ee7e8` |
| IRI 教程原档 | [IRI_tutorial.zip](http://sobereva.com/multiwfn/res/IRI_tutorial.zip)，Last-Modified 2025-06-28 | 1,216,044 | `b40e2dee6d979877c980fb63fe83528a91b76f7e08641bdb1ccb6809e0ce74f5` |
| IRI 博客原始输入 | [file.zip](http://sobereva.com/attach/598/file.zip)，Last-Modified 2021-05-31 | 6,239,048 | `77878e0b602faf3939c80e17c3559f59ea43fc4eee311bb22acefe1870f05f57` |
| `file/PhenolDimer.fchk` | 上述 IRI 博客原档 | 4,694,715 | `3a4b03c8afa4b18ad28820b10d4c40503aa539ada196a33958a633118943b252` |
| `IGMH_tutorial/file/AT.wfn` | 上述 IGMH 教程原档 | 763,438 | `42e50ba8160bb4be8c327277f5818460b33ab67b5ade2dba52595307f3505c6d` |
| `IRI_tutorial/phenol_dimer.wfn` | 上述 IRI 教程原档 | 465,498 | `4147284f300a348a92761081e09efa2dd7bd080993f7c28162fbd51e35b64c53` |

这些原档没有独立的数据再分发许可文件，按作者公开提供的教程材料供本地复跑使用，不纳入扩展发行包。程序许可与数据许可分别记录。作者网站的文章版权声明不授权转载正文；本文仅记录来源、必要操作参数和本地核查结果。[作者教程页](http://sobereva.com/621)、[IRI 教程页](http://sobereva.com/598)

## C07：同一真实波函数的 IGMH 与 IRI

`file/PhenolDimer.fchk` 包含 26 原子、100 电子、中性单重态、324 个基函数；`Gaussian Version` 为 `ES64L-G16RevA.03`，route 为 `#P B3LYP/6-311G** opt freq int=fine em=gd3bj`，源 `Total Energy` 为 `-615.1617590953192 Hartree`。文件标题及作者说明均指向 B3LYP-D3(BJ)/6-311G** 优化构型。它可作为 QCBlender 可直接导入的参考波函数。[官方来源与计算说明](http://sobereva.com/598)

本轮目录为 `outputs/v1-acceptance/sources/c07-c09-research/phenol-2026-09-27/`。IGMH 按两套苯酚的源原子编号划分为 `1–13`、`14–26`；原子顺序及几何成键检查确认两片段不交叉。用户提供的 Multiwfn Windows x64 **2026.9.20** 以 **4 线程**运行，`Multiwfn.exe` SHA-256 为 `64d9660cf859a94882a3df80d840cef8f80493e402b32993cc0cea068ca35421`。两次计算退出码均为 0；源输入、局部 `settings.ini`、完整输入流与 stdout 均保留，未修改程序目录内设置。

已按当前 `visweak.f90`、`otherfunc.f90`、`grid.f90`、`function.f90` 与 2026.9.1 手册核对菜单和定义。IGMH 输入为 `20 → 11 → 2 → 1-13 → 14-26 → -10 → 2 → 2 → 3 → 0 → 0 → q`；IRI 为 `20 → 4 → -10 → 2 → 2 → 3 → 0 → 0 → q`。其中 `-10 → 2` 将分子包围盒各方向延伸设为 **2 Bohr**，随后选择中等网格（名义 512000 点）。两种分析实际同为 **122 × 66 × 66 = 531432 点**，完整精度间距 `0.18859124989632603 Bohr`；Cube 头写为 `0.188591 Bohr`，原点为 `(-11.336526, -6.170854, -6.194976) Bohr`。

设置为 `IGMvdwscl=0`、`IRI_rhocut=0`、`uservar=0`。IGMH 保留完整场，IRI 使用 `a=1.1`，不进行低密度哨兵值替换或共价区显示过滤。IGMH `δg` 是密度梯度差，单位为 `electron/bohr^4`；颜色场 `sign(λ₂)ρ` 为 `electron/bohr^3`。IRI 定义为 `|∇ρ|/ρ^1.1`，单位记录为 `a.u. (electron^-0.1 bohr^-0.7)`，不是无量纲 RDG。单位由当前实现公式和原子单位约定核实。[方法作者说明](http://sobereva.com/621)、[IRI 定义](http://sobereva.com/598)

| 角色 | 计算输出（相对本轮目录） | 范围 | SHA-256 |
| --- | --- | --- | --- |
| IGMH 几何场 | `igmh/dg_inter.cub` | 0 至 0.0500603 | `3d8c044dbbac7a08f18f7bb6a4fa1a71628157c24d3b781bcb0da993bcc99695` |
| IGMH 颜色场 | `igmh/sl2r.cub` | -123.65 至 0.278699 | `ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514` |
| IRI 几何场 | `iri/func2.cub` | 0.0444571 至 149.276 | `a08baaa600115d4321c826be6c1783ecc17649a3b52728f363cbe5faf7e41a1f` |
| IRI 颜色场 | `iri/func1.cub` | -123.65 至 0.278699 | `ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514` |

同时保留 `igmh/dg_intra.cub` 与 `igmh/dg.cub`。六个 Cube 均为 7,618,853 字节。`recipe.json` 记录片段、单位及命令；`run-records.json` 记录实际运行；`provenance.json` 固定程序、许可证、手册和相关源码摘要；`sha256.json` 固定全部本轮文件；`verification.json` 为下列检查证据。

- 六个 Cube 读取、531432 个数值有限性、26 个原子身份及构型对应：`Passed`。Cube 头打印精度引起的坐标最大差为 `2.646e-7 Å`。
- `pair_cubes` 两组配对与 `scatter_points`：`Passed`；各有 48312 个有限散点。IGMH/IRI 的颜色数组逐项完全相同。
- `δg = δg_inter + δg_intra`：`Passed`；导出精度内最大绝对残差 `9.879e-7`。
- 用既有 IOData + GBasis 在 8 个固定网格点独立重算密度、梯度与 Hessian，再构造 IRI 和带符号密度：`Passed`；IRI 最大绝对差 `4.342e-6`，颜色最大绝对差 `4.630e-7`，判据 `rtol=1e-5, atol=1e-7`。核查使用计算时完整精度网格，避免把 Cube 头的六位小数误当计算坐标。

教程原档仅提供输入和说明，没有现成成对 Cube。`AT.wfn` 是官方 IGMH 单独复现实例，30 原子；其官方片段为 `15–29` 和补集，标准网格 `0.15 Bohr`，也可作为另一可追溯输入，但 QCBlender 需要以生成的 Cube 作为参考构型入口。[IGMH 作者教程](http://sobereva.com/multiwfn/res/IGMH_tutorial.zip)

## C08 与 C09：同一 S03 构型的真实分析

主任务的计算目录为 `outputs/v1-acceptance/sources/multiwfn-local/C08/` 与 `C09/`；各自 `run.json`、`input.txt`、`settings.ini`、`stdout.log` 均已保存。两次计算均来自 S03 `outputs/complex-examples/sources/Trp_polar.fchk`，输入 SHA-256 为 `04a1cd071eb66ec4aeeffd0f6a198e2294ad9ef483d3ce3beaf94a839a81e88d`；本研究已逐项复核全部 `run.json` 所列文件摘要，均匹配。输入为 Gaussian 16、RHF/STO-3G，route `#p hf/sto-3g polar symmetry=none`，27 原子、108 电子、中性单重态，能量 `-673.590571157329 Hartree`。原数据来自 [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/FChk/basicGaussian16/Trp_polar.fchk)，许可 BSD-3-Clause。

**C08 ESP 表面。** 主功能 12 使用 `ρ=0.001 electron/bohr^3` 表面、`0.25 Bohr` 网格间距、`91 × 65 × 93` 网格；完整 stdout 给出表面积 **228.24053 Å²**。面积分布选全部原子、`-100 至 100 kcal/mol`、40 个 bin，宽度为 `5 kcal/mol`；40 行打印面积之和为 **228.2405 Å²**、百分比之和 **99.9999%**。表面定义与 C04 的显示等值面分别记录。[作者 ESP 面积教程](http://sobereva.com/196)

`surfanalysis.pdb` 含 11 个最大值（C）和 8 个最小值（O），B-factor 单位由文件开头明确声明为 **kcal/mol**，PDB 坐标为 **Å**。`surfanalysis.txt` 保存同一极值的 a.u./eV/kcal/mol 及较高精度坐标。逐项对比原始 PDB 与 txt，最大坐标差 `0.000499 Å`、最大数值差 `0.004515 kcal/mol`，均在 PDB 的三位/两位小数打印精度内。原生 Multiwfn 的最大/最小值编号分别从 1 开始；当前读取器以类型与编号共同校验身份，原文件 19 点和面积表读取均 `Passed`。这一编号规则由当前 `surfana.f90` 的两个独立输出循环核实。[作者格式说明](http://sobereva.com/443)

用 IOData + GBasis 对 19 个 txt 精度坐标独立重算 ESP，最大绝对差为 **5.948e-7 a.u.**；采用现有 `tests/test_science_reference.py::test_cubegen_density_and_esp` 的 `atol=1.5e-5 a.u.` 判据，`Passed`。极值坐标上的独立密度范围为 `0.000998562 至 0.001002220 electron/bohr^3`，保留原离散表面结果。txt 极值范围为 `-44.973471 至 34.841007 kcal/mol`。

**C09 AIM。** 同一 S03 的密度拓扑得到 27 个 `(3,-3)`、29 个 `(3,-1)`、3 个 `(3,+1)`、0 个 `(3,+3)`，PDB 分别以 C/N/O/F 标记。Euler/Poincaré–Hopf 检查为 **27 − 29 + 3 − 0 = 1**。`CPs.pdb`、`CPprop.txt` 的 59 个编号/类型逐项对应；`paths.pdb` 按 residue 号形成 **58** 条路径。当前源码 `topology.f90` 明确将 CP/路径坐标乘 `b2a` 后写入 PDB，单位为 **Å**；`CPprop.txt` 同时输出 Bohr 与 Å。两套坐标换算一致，PDB 与属性坐标最大差为 `0.000499960 Å`，符合打印精度。[作者 AIM 教程](http://sobereva.com/445)

独立重算全部 59 个 CP 的密度、梯度和 Hessian：密度及 Laplacian 比较使用 `rtol=1e-7`，绝对容差分别 `2e-8`、`2e-7`；均 `Passed`。最大绝对差分别为 `4.841e-7 electron/bohr^3`、`4.063e-4 electron/bohr^5`，后者发生在数值量级很大的核 CP；Hessian 的 59 个符号类型全部匹配，梯度范数最大 `2.245e-8`。本轮 `CPprop.txt` **实际包含**核 ESP、电子 ESP 和总 ESP，按原文保留。

例如 CP 28 连接源原子 `25(H)–1(N)`，类型 `(3,-1)`，位置 `(-0.714365939753, -0.545312022264, 0.686736137747) Bohr`；`ρ=0.3219923958 electron/bohr^3`、`∇²ρ=-1.168558420 electron/bohr^5`、`G=0.08448498215 Hartree/bohr^3`、`H=-0.3766245872 Hartree/bohr^3`、总 ESP `1.011572790 a.u.`。其 RDG 原文值为 100，这是所用默认设置的高密度显示哨兵值，不能解释成未筛选 RDG。全部性质原文和独立检查详见 `outputs/v1-acceptance/sources/c07-c09-research/c08-c09-verification/verification.json`。

Multiwfn 的 Bohr–Å 常数为 `0.529177210903`，当前 QCBlender 为 `0.529177210544`；源坐标换算使用各自明确常数，报告保留两者，避免把常数的微小差异误判为数据关联错误。

## 许可、可复跑证据与状态

- 官方输入身份、源计算参数、教程与字节摘要：`Passed`。
- C07 实际 IGMH/IRI 生成、读取配对、网格与独立数值抽查：`Passed`。
- C08 实际来源、19 个极值原值/单位/坐标、40 个面积 bin、独立 ESP 核查及当前读取器：`Passed`。
- C09 实际来源、59 个 CP、58 条路径、原值/单位/坐标、Euler 与独立密度/Hessian 核查：`Passed`。
- Blender GUI、节点、渲染、保存/移动/冷重开：本研究 `Not Run`；由主任务记录。

本轮使用用户提供且已授权的本地 Multiwfn，不新增依赖。程序本地 `LICENSE.txt` 允许免费学术/商业使用和代码分发，要求引用 Tian Lu, Feiwu Chen, *J. Comput. Chem.* **33**, 580–592 (2012), DOI `10.1002/jcc.22885`；Tian Lu, *J. Chem. Phys.* **161**, 082503 (2024), DOI `10.1063/5.0216272`。ESP 表面 stdout 另要求引用表面算法论文 *J. Mol. Graph. Model.* **38**, 314–323 (2012)。教程输入的独立数据再分发许可未明确，仍只作本地验收材料。[官方版本与许可](http://sobereva.com/multiwfn/download.html)

PDF 文本使用本机已有 Xpdf 4.00 `C:/Program Files/Git/mingw64/bin/pdftotext.exe -layout` 提取（默认 Latin1）。本轮计算、核查阶段只更新本研究文件及独立输出目录；未修改主任务的计算原始输出或人工签署栏。
