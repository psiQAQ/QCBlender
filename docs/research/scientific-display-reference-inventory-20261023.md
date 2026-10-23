# 表面距离投影与 AICD：真实样本和参照盘点

核查及补算日期：2026-10-23。对应[规格](../../.scratch/scientific-displays-20261023/spec.md)、[距离投影前置 02](../../.scratch/scientific-displays-20261023/issues/02-projection-reference.md)及 [AICD 前置 04](../../.scratch/scientific-displays-20261023/issues/04-aicd-reference.md)。先只读盘点；用户批准“按照建议推进”后，使用现有 Multiwfn 生成官方 Ru 构型的 vdW 距离投影并独立核算。未运行 Gaussian 或 Blender，未安装依赖或实现适配器。

**当前结论：距离投影的真实参照已补齐，02 resolved；AICD 仍缺原始张量，04 pending。** 真实 Multiwfn 输出的 2,501 点与独立解析球面求交核对 Passed，03 的材料前置已解除。AICD 已有真实 π/σ 计算日志，但日志指向的原始张量转储不在现有材料中，05 仍受前置约束。

## 初次只读盘点的范围与证据边界

- 含忽略文件盘点 `submodules/Multiwfn/`（1,185 个文件）、`submodules/GXNU-MolStudio/`（145 个文件）和 `validation/shared/data/`（338 个文件），按输出名和内容标记检查；同时读取本地输入/迁移索引。没有找到 `distmap.txt`、`mwfn_commands.txt`、`mwfn_log.txt`、`oriented.xyz` 或真实 AICD 张量转储。
- 用现有 Windows `tar -tf` 只读列出 `Multiwfn_2026.9.20_bin_Win64.7z` 的 1,186 个成员：包含下文 Ru 构型及 NICS 苯输入/日志，不含名为 AICD、distmap、tensor 或 `_sdm` 的结果成员。没有解压或执行程序。
- MolStudio 当前检出 `427e6cca72fc43837949d0cee234bfc083279775`，来源为 [上游仓库](https://cnb.cool/chem311/GXNU-MolStudio)。读取的是固定本地检出，不把源码自述当作独立实测。
- Multiwfn 原件来自用户已有材料；身份见末尾 SHA-256。手册内容通过已有 `validation/shared/data/local/sop/c10-c13/multiwfn-cobh3-20260927/manual-utf8.txt` 核对，对应本地 PDF 第 3.300.8、4.300.8 节。未重新下载手册或验证线上最新版。
- 补充检查历史 `outputs/projects/` 时，部分 `.qcdata/datasets/` 返回权限拒绝；没有修改 ACL 或扩大权限扫描。因此结论限定为已核查、可访问的材料，不宣称全盘不存在。MolStudio 的默认临时目录 `%TEMP%/MolStudio_surface_projection` 本次不存在。
- [作者距离投影文章 /589](http://sobereva.com/589) 本次直接访问返回 502；本文不引用未读到的网页正文。官方手册已包含对应案例和步骤。

## 1. 表面距离投影：真实输出与独立参照已补齐

### 本次实际运行及数值验收

八个文件（含原始输入）集中保存在 `validation/shared/data/local/scientific-displays/ru-vdw-20261023/`，沿用本地限定输入的忽略及分发边界；稳定读取 key 为 `scientific-displays/ru-vdw-20261023`。本批[机器验收记录](../../validation/agent/reports/2026-10-23/projection-reference/acceptance.json)绑定逐文件 SHA-256；[独立参照脚本](../../validation/agent/reports/2026-10-23/projection-reference/reference.py)只用 Python 标准库，不导入 QCBlender 或 MolStudio。源文件和计算参数身份位于包内 `parameters.json`。

| 条件或结果 | 本次记录 |
| --- | --- |
| 程序与输入 | Multiwfn 2026.9.20，4 线程；官方 `Ru(bpy3)2+.gjf` 原字节复制为 `input.gjf`，61 原子；坐标不旋转，只读取构型，不执行 Gaussian 路由 |
| 表面 | 原子 vdW 球并集，半径系数 1；H 1.2、C 1.7、N 1.55、Ru 2.0 Å，来自该版本 `define.f90:84–90`。Ru 是程序的默认半径，不能称为单独测定的 Ru 参数 |
| 扫描 | X `[-7,7] Å`，61 点；Y `[-6,7] Å`，41 点；含两端点；沿负 Z，`Zstart=6 Å`、`Zend=-6 Å`、步长 `0.05 Å` |
| 设置与记录 | 原设置只将 `isilent=0` 改为 `1`，`vdwrfile=none`；保留实际 `settings.ini`、`mwfn_commands.txt`、`mwfn_log.txt`、`execution.json`；日志最终参数逐项核对，未使用乘数菜单 |
| 实际导出坐标 | `distmap.txt` 的 XY 为 `[0,14] × [0,13] Å`，X 外循环、Y 内循环；绝对坐标必须加一次 `(-7,-6) Å`。这是本次新进程、未先执行其他平面操作时的实测结果，不能替所有未知来源文件猜偏移 |
| 深度与有效域 | `z_hit-z_start`，负值；1,406 点命中，1,095 点未命中；未命中值为 `-12 Å`。完整独立点表及掩码在 `independent-reference.csv` |
| 坐标与离散深度一致性 | 最大 XY 文本误差 `3.333334e-7 Å`；最大离散深度差 `1.78e-15 Å`（浮点舍入）；分别通过 `5.01e-7 Å` 与 `5.01e-9 Å` 文本精度界 |
| 连续表面与扫描差异 | 连续交点深度减实际离散深度为 `0.00000967164–0.04996673234 Å`，全部在 `[0,0.05 Å]` 内；本格点集没有因薄球弦而漏采的交点 |

独立参照在运行 Multiwfn **之前**生成。对每个原子，解竖直射线与球的二次方程得到开放区间 `(z_low,z_high)`，选择从上方观察的第一个连续交点；再直接解不等式 `z_low < Zstart-k·Δz < z_high`，求首个合格整数 `k`，得到独立离散深度。此算法没有复制 Multiwfn 的逐 Z 层探测循环，也不从实际输出反推预期值。二者共享的是已声明的构型、半径和扫描参数。

本模型所有球面位于 Z `[-4.817364,4.817364] Å`，严格包在起止平面之间，因此本例 `-12 Å` 可由独立几何证明为未命中。**通用文件仍需三态有效性**：若不能证明扫描底值的含义，不能仅凭它等于 `Zend-Zstart` 就判无效。扫描起点已在表面内部时，0 也可为有效命中。本例不验证其他坐标状态、密度表面、不同半径或 AICD。

验收后把八个原始及派生文件逐字节保存到上述集中目录，核对 SHA-256 并通过 `tools.local_inputs.input_path` 重新解析入口。工作副本在 `.tmp/runs/projection-reference/ru-vdw-1/`，没有删除原输入或历史对象。数值一致性为 **Passed**；独立人工科研验收、准分子密度案例、适配器与 Blender GUI/渲染/冷读均为 **Not Run**。

### 初次盘点找到的起始材料

| 已有材料 | 本次确认 | 可用于什么 |
| --- | --- | --- |
| [Ru(bpy3)2+.gjf](<../../submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/excit/Ru(bpy3)2+.gjf>) | 官方手册 4.300.8 指定的 `[Ru(bpy)₃]²⁺` 优化构型；文件标题标明 BP86/SDD+6-31G* optimized；电荷/多重度为 `2 1` | 直接作为真实、固定朝向的投影输入。这里使用构型，不要求执行文件中另列的 TD 计算 |
| [Multiwfn 手册](../../submodules/Multiwfn/Multiwfn_manual_2026.9.1.pdf) 第 3.300.8、4.300.8 节（印刷页 429–430、1053 起） | 定义沿 Z 扫描的相对深度；教程先用 `0.05 a.u.` 准分子密度，再用半径缩放 `1` 的原子 vdW 球叠加 | 物理定义、运行步骤及定性图像对照；手册没有在该节提供逐网格数字参考表 |
| [ferrocene.mwfn](../../submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/ferrocene.mwfn) | 官方包中真实二茂铁波函数存在 | 可选输入；尚无证据证明它与 MolStudio 展示图使用同一朝向或计算条件 |
| [MolStudio 展示图](../../submodules/GXNU-MolStudio/docs/images/sdm_options_pair.png)及[上游文章](../../submodules/GXNU-MolStudio/docs/公众号_感应电流与表面投影更新.md) | 文章说明二茂铁、两种色表和结构叠加 | 仅用于显示效果参考；没有伴随的三列结果、朝向构型或运行日志 |
| [surface_projection.py](../../submodules/GXNU-MolStudio/molstudio/core/surface_projection.py) 与[测试](../../submodules/GXNU-MolStudio/tests/test_surface_projection.py) | `build_commands`/`run_multiwfn`/`project` 会写出命令、日志、`oriented.xyz` 和 `distmap.txt`；测试的 `-(x²+y²)` 是合成场 | 可查外部文件契约与显示边界；合成测试不能替代真实结果 |

源码证据：Multiwfn `otherfunc3.f90:3203–3279,3326–3367` 按 `z_hit-z_start` 记录命中深度，未命中初始化为 `z_end-z_start`，最后转为 Å；密度表面作相邻扫描层插值，vdW 表面按扫描步长命中。`0123dim.f90:3376–3397` 允许缩放当前数据并导出三列，XY 坐标使用 `orgx2D/orgy2D`。MolStudio 面板 `surface_projection_panel.py:538–542` 又将扫描下限作为 XY 偏移。因此仅有三列文件不足以证明绝对坐标、单位、是否缩放及有效域。

### 距离投影参照包的对应文件

| 材料 | 必需内容 | 本次补齐结果 |
| --- | --- | --- |
| 原始 `distmap.txt` | 未缩放的 X、Y、深度三列，保留原始精度；声明 XY 是绝对坐标还是相对扫描起点 | 已由实际 Multiwfn 运行导出；本例为相对坐标 |
| `mwfn_commands.txt`、`mwfn_log.txt` 与必要设置 | 程序版本；表面类型和半径系数；X/Y 范围及 Nx/Ny；Zstart/Zend/Zstep；是否缩放；影响结果的设置文件 | 已保留 stdin、日志、settings、execution 及 parameters 文件，并核对实际日志 |
| 与结果逐字节绑定的输入构型 | 实际用于扫描的 `.gjf`/`.xyz` 等；如有旋转，保留 `oriented.xyz` 或明确变换 | `input.gjf` 与官方原件字节一致；不旋转 |
| 独立数值参照和有效域依据 | 同一网格上的命中深度与明确未命中点，处理端点歧义；参照方法及精度 | `independent-reference.csv` 覆盖全部点；解析球面交点、独立离散采样和掩码均已验证 |

首个基准采用官方 Ru 构型的 **vdW 球叠加**，不需要新量化单点，可独立核算几何交点。误差界区分 Z 步长与文本精度，显示插值后的像素不作为参考数值。手册的准分子密度案例尚未补算；本次外部程序运行不把计算调度加入适配器。

## 2. AICD：π/σ 日志真实，转储缺失且全电子算法不匹配

下表路径位于 `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/`。

| 已有文件 | 核实结果 | 不足之处 |
| --- | --- | --- |
| `benzene.fch`、`benzene.wfn` | 真实苯波函数存在；FCH 为 RB3LYP/6-31G(d)、12 原子、0 电荷、单重态、42 电子，接近 XY 平面 | FCH 基组不同于下列 6-31+G* 响应任务，不能直接作为其配套轨道文件 |
| `ICSS/benzene.gjf` | B3LYP/6-31+G*、0 1；碳顶点 y 为 `1.390788 Å` | 与 NICS 例子的 `1.397000 Å` 构型不同，不能混配 |
| `NICS_scan/benzene-pi_NICS_1D.gjf`、`.out` | 输入 `nmr=csgt iop(10/93=2)`，π轨道 `17,20,21`；Gaussian 16 C.02，正常结束 | 日志宣告生成的 `AICD.txt` 未随现有材料保存 |
| `NICS_scan/benzene-sigma_NICS_1D.gjf`、`.out` | 同结构/方法，σ轨道 `1-16,18-19`；正常结束 | 同样缺少其独立 `AICD.txt` |
| `NICS_scan/benzene_NICS_1D.gjf`、`.out` | 真实全电子 NICS；日志明确使用 GIAO | 不是与上述 CSGT π结果匹配的全电子 AICD 转储 |

可直接定位的证据：

- [π日志](../../submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene-pi_NICS_1D.out) 第 1197–1199 行记录生成 `AICD.txt`、轨道 `17 20 21`、272232 个网格点；第 2873 行正常结束。σ日志第 1197–1199 行有同类记录，第 2837 行正常结束。
- [全电子日志](../../submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene_NICS_1D.out) 第 1194–1195 行为 `GIAO nuclear magnetic shielding tensors`。即使三份日志的 SCF 能量同为 `-232.258890248 Eh`，也不能忽略磁响应算法差异。
- [MolStudio 图像](../../submodules/GXNU-MolStudio/docs/images/aicd_all_vs_pi.png)标注全电子与 π苯结果，但没有附带同源原始张量、生成条件和数值清单。[aicd.py](../../submodules/GXNU-MolStudio/molstudio/core/aicd.py) 第 21–30 行自述用 1470 个块、`AICD-extract.pl` 和苯对称性核对过单位/张量列；本检出未找到对应真实转储或该提取器，不能独立复现此自述。
- `test_aicd_arrows.py:15–28` 使用解析球面与合成矢量，`test_aicd_plane.py:14–21` 使用硬编码苯几何。现有 `validation/shared/data/local/log-examples/benzene_HPfreq.log` 是 AM1 振动任务，均不补足 AICD 门禁。

NICS 的屏蔽张量以及日志中的磁化率 `Anisotropy`，都不是原始采样点上的电流响应张量或 MolStudio `Aniso`；不能借同名字段替代缺件。

### 真正缺少的最小结果包

1. **同构型、同方法/基组、同磁响应设置的全电子及 π原始转储各一份**，包含点坐标、权重和九分量电流响应张量。分别命名/存放，例如 `all/AICD.txt`、`pi/AICD.txt`，避免同名覆盖。σ不是本次最小 all/π门禁的额外必需件；若有，应连同其身份保留。
2. **与上述转储对应的完整输入和正常结束日志**。现有 π输入/日志可在找到其原转储时复用；仍缺全电子 CSGT AICD 的匹配结果。需指定计算段，不能从拼接日志随意取最后构型。
3. **配套轨道身份依据**，包括实际选用的轨道号、自旋、方法/基组和构型；核实 π物理归属时需要对应的选轨道证据或 chk/fchk。现有不同基组的 `benzene.fch` 不能直接顶替。
4. **独立点值参照**：原始点上的 `Aniso` 及单位磁场 `B=(0,0,1)` 下 `Jx/Jy/Jz`，带点对应关系、程序/提取器版本、坐标与响应单位、分量排列、符号约定。不得用待实现解析器自身生成“独立参考”。

原始解析/派生与规则网格重映射的误差应分开验收。得到原始参照后，四近邻反距离网格化的独立核对结果可以另行制作，**不必先向用户索取某个固定格式的现成网格文件**；目前没有执行依据，故不冻结误差阈值。

## 当前结论与下一步

- **Passed**：资料盘点；真实 Multiwfn vdW 扫描；全部 2,501 点的独立数值及有效域核对；扫描日志/设置、源文件身份与八文件集中保全。
- **Not Run**：准分子密度计算、适配器实现、Blender 验证、Gaussian/AICD 计算及独立人工科研验收。
- 02 resolved，03 可按原规格进入实现；04 仍 pending，05 仍受其约束。AICD 继续需要同源 all/π转储和独立点值参照，不能用现有不匹配文件替代。本次追加授权仅补算距离投影参照，未启动新的量化任务。

## 原件身份

下表保留本次读取的原始字节身份。Multiwfn 来源入口为[官网](http://sobereva.com/multiwfn/)，材料由用户此前提供，本次获取方式为本地读取；MolStudio 来源与提交见上文。未下载新原件。

| 原件（相对仓库根目录） | SHA-256 |
| --- | --- |
| `submodules/Multiwfn/Multiwfn_manual_2026.9.1.pdf` | `418871dc13a9c0860f4f5417935ca2848cb2251f42bce9b26e90a15717c6c9fb` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/Multiwfn.exe` | `64d9660cf859a94882a3df80d840cef8f80493e402b32993cc0cea068ca35421` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/excit/Ru(bpy3)2+.gjf` | `14301ca8539eec56dd179a153027ba7b14a7f4628714b049d7340af4c3baea06` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/ferrocene.mwfn` | `f8ebe7c6899bb050ed1f57632878752fe76c1b1cd0884b18e95f88373eae9914` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/otherfunc3.f90` | `80c6d469901bc48d98e71fc8f815352fe1f232478911daaa563ee12d1b5782e2` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/0123dim.f90` | `553ceb8508d4ef78e6f6c717bbb7d9a8916763894d8f8550df6ed2a8006bf989` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/benzene.fch` | `c30d736ada02248b4ec7dba74c21af65fb5ec59d7e87efd854b28c5a4bee057e` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/ICSS/benzene.gjf` | `6aa49794752a04d0226b631e2bd223460cd05de58bd0db4c246da44c564168ea` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene_NICS_1D.gjf` | `b94a60196edf901d1a8231225b05120091f930c9754fbaca95f5b9d12bbcbef0` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene_NICS_1D.out` | `503019781088cc812c9016d9b48e2546dd45943bc2b4d40b8fe25f8bbcbd8499` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene-pi_NICS_1D.gjf` | `05d9c45f9bb1e4cb0daece18926963c1b84edec98e9e1c9274ba269b3e90d047` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene-pi_NICS_1D.out` | `3b22640b08a8b05bdb45db5fcb22b0cbc217f408b3e24ecd55aae25027e893ba` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene-sigma_NICS_1D.gjf` | `3b0e657cf4026e317e1cbeb346430a282ba389b241d3286473938ad65892c90f` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/examples/NICS_scan/benzene-sigma_NICS_1D.out` | `e23774cbb32621728610f90167a10f97b55a1082e00530dd3e12d7788d0df458` |
| `submodules/GXNU-MolStudio/molstudio/core/surface_projection.py` | `be16a86f7783a25ed75a955d6b1aa0b74d882e88af771df8772e72f8df247fc4` |
| `submodules/GXNU-MolStudio/molstudio/core/aicd.py` | `0b755754ea125852d6c1e6ce534c97d89206b4d8d90f8b928842357259ee596c` |
| `submodules/GXNU-MolStudio/docs/images/sdm_options_pair.png` | `caface5984b915987b26ec5d3c341c4088fde8d36b53e73f0aedbfc0a8c80382` |
| `submodules/GXNU-MolStudio/docs/images/aicd_all_vs_pi.png` | `e17d8c1c5d3e5daf169f6c149f996426a43ff961d39337729309bb8bb18a3ba1` |
