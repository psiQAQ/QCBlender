# C10–C13 真实样本与生成依据

核查日期：2026-09-27。本记录对应 Agent 技术复跑，GUI 验收与独立人工签署由主任务分别记录。

| 案例 | 当前材料与状态 |
| --- | --- |
| C10 | **Passed（数据生成及解析）**：真实 H₂O₂ IRC 的相邻三构型，使用现有 PySCF 做 RHF/STO-3G 单点，导出含完整 MO、占据和密度的 FCHK；当前 `import_irc` 读回通过。GUI 操作尚由主任务执行。 |
| C11 | **Passed（数据计算及解析）**：使用已有 PySCF CHK 和标准 Mayer 公式计算三步全部六个原子对，标量交叉核对及 FCHK 身份核对通过；文本明确标注本机脚本生成、Multiwfn-compatible syntax。GUI 由主任务记录。 |
| C12 | **Passed（真实计算及解析）**：用户提供并授权的 Multiwfn 2026.9.20 Win64 以 4 线程运行官方 COBH3 例子，导出最终 ETS-NOCV 表；当前 `import_ets` 读回 9 个显著 pair。GUI 操作由主任务记录。 |
| C13 | **Passed（真实计算及解析）**：同次分析导出的 `Total`、pair 1 signed density Cube 通过原子关联、当前 `import_nocv` 和全部体素的 NOCV 轨道公式核对。GUI、渲染与重开由主任务记录。 |

## 已取得材料与来源锁

本节所有文件位于 `outputs/v1-acceptance/sources/c10-c13/`。归档保留且未运行其中的软件；完整文件摘要在该目录的 `download-and-generation-hashes.json`。本轮不将第三方原件加入发布包。

| 文件 | 直接来源与条件 | 字节数 / SHA-256 |
| --- | --- | --- |
| `source-peroxide_irc.fchk` | 从仓库锁定的 [qc-iodata 1.0.1 官方 wheel](https://files.pythonhosted.org/packages/1c/44/20396e1a1096076a04452db27caf3d97b18fe848a21772b9b439b46bb7af/qc_iodata-1.0.1-py3-none-any.whl) 中原样提取 `iodata/test/data/peroxide_irc.fchk`。wheel 的 SHA 已匹配 `dependencies.lock.json`。源标题 `irc`，RHF/STO-3G，中性单重态，4 原子 `[8,8,1,1]`，18 电子，21 个 IRC 构型；原 Gaussian 精确版本未在此文件给出。 | 97,554 / `a11036281c4a5257f67d29a580126a6153e96cec2a6fd00216aef05f80f3ec6f` |
| `Multiwfn_2026.9.20_bin_Linux_noGUI.zip` | [作者固定版本档案](http://sobereva.com/multiwfn/misc/Multiwfn_2026.9.20_bin_Linux_noGUI.zip)；仅提取示例及许可。 | 30,507,538 / `6347413e5d066508f2b121cfb269a66f8ea9b7247720b1794ad2bafe45b63cc3` |
| `IRCsplit_1.0.3.rar` | [作者固定版本附件](http://sobereva.com/soft/IRCsplit_1.0.3.rar)，入口为[作者教程 /199](http://sobereva.com/199)；只提取文本输入、日志及脚本。 | 776,747 / `c0dbc03a3e1b55cdd19a48e0ad42450ec8baf1679faf25c55e6715a7d4a800e8` |

`source-LICENSE.txt` 是 wheel 随包的 LGPL v3 许可文本，SHA 为 `da7eabb7bafdf7d3ae5e9f223aa5bdc1eece45ac569dc21b3b037520b4464768`；样本无独立许可声明。Multiwfn 档案的 `LICENSE.txt` SHA 为 `0846f4144fd66d07a5b17e340863147a6797bbec871114d804ae620ffd7e8360`，允许免费学术与商业使用，规定引用两篇原始论文，不承诺结果正确性。完整条款见[作者下载页](http://sobereva.com/multiwfn/download.html)。IRCsplit 附件未发现独立许可文件。

Multiwfn 引用：[Lu and Chen, J. Comput. Chem. 33, 580–592 (2012)](https://doi.org/10.1002/jcc.22885)；[Lu, J. Chem. Phys. 161, 082503 (2024)](https://doi.org/10.1063/5.0216272)。

## C10：真实三步单点与核对

可直接导入的清单为 `peroxide-irc-pyscf/steps.csv`。源文件按“TS、正向、反向”存储；本次按照反应坐标递增，选择原文件的第 **12 → 1 → 2** 构型，形成跨 TS 的连续三点。源反应坐标分别为 `-0.105685976, 0, 0.105689581`；源文件未显式声明其单位，报告保留原值、不补写单位。

生成脚本 `generate_irc_pyscf.py` 使用本机已有的 `C:/Users/ustcw/miniforge3/envs/pyscf-win313-test/python.exe`、PySCF 2.13.1 与仓库已有 IOData 1.0.1，不安装依赖。方法与原 IRC 一致：RHF/STO-3G、charge 0、spin 0、Bohr 坐标、不启用对称性、`conv_tol=1e-10`、`max_cycle=100`、2 线程。每步独立执行真实 SCF，然后由 [PySCF Molden 导出器](https://pyscf.org/_modules/pyscf/tools/molden.html)和 [IOData FCHK 写入器](https://iodata.readthedocs.io/en/latest/formats.html#gaussian-fchk-file-format-fchk)转换。没有借用其它构型的轨道、修改源能量或插值制造波函数。

| step / 原构型 | 实算 `mf.e_tot`（Eh） | FCHK 源字段（Eh） | FCHK SHA-256 |
| --- | --- | --- | --- |
| 1 / 12 | `-148.75053390766712` | `-148.750534` | `df38dd4180f7068f6c099eb3b7cfdfae8a585992d1e91b6216af526a005496d4` |
| 2 / 1 | `-148.75043183918416` | `-148.750432` | `a48eed63f663c4025fc39a36e0407a0d467857673c0c289e36dc441346fe748a` |
| 3 / 2 | `-148.75052755326928` | `-148.750528` | `b1005a583c1b73fe770dd3afd874cad0b40561b4a319301c78123653874946c4` |

三份文件均为 7,557 字节。IOData 1.0.1 的实数输出格式为 `16.8E`，此能量数量级的最大舍入误差为 `5e-7 Eh`；本次最大实测为 `4.4674e-7 Eh`。界面须与 FCHK 的已写入字段比较，完整单点精度另见 JSON 和 SCF 日志。

`peroxide-irc-pyscf/generation-report.json` 记录每步源坐标、原步号、程序版本及验证值；`step-NNN-input.json`、`step-NNN-scf.log`、PySCF CHK、Molden 和 FCHK 全部保留。验证结果：

- **Passed**：三步 SCF 均收敛；12×12 MO 系数、12 个轨道能量、9 个双占据轨道和 12×12 SCF 密度矩阵齐全。
- **Passed**：读回原子身份/顺序与 Bohr 坐标；密度积分的最大电子数误差 `7.5e-9`，MO 正交误差小于 `1.8e-9`。
- **Passed**：四个相同空间点上，PySCF 原始密度与 FCHK→GBasis 密度最大绝对差 `1.4e-9 electron/bohr^3`。
- **Passed**：当前 `qcblender.readers.read_fchk` 和 `qcblender.irc.import_irc` 解析三步，得到 `(3,4,3)` 构型数组和三个 FCHK 源能量。

这是三个相邻真实 IRC 构型的演示集，不包含原文件全部 21 个构型。数据解析检查不能替代 SOP 的 GUI、渲染及冷重开检查。

## C11：现有 PySCF 波函数的真实 Mayer 计算

可直接交给当前导入器的清单为 `peroxide-irc-pyscf/mayer-pyscf.csv`，SHA-256 为 `3627fbb0c0e271882dd9852c94efd3f6691f724bb9636465edcfe52d362d65fc`。脚本为同目录上一级的 `generate_mayer_pyscf.py`。运行只使用已有 PySCF 2.13.1、NumPy 2.5.0；IOData 仅用于独立读回 FCHK。没有安装或运行 Multiwfn。

公式依据为 [ORCA 6.1 官方手册 5.1.4、式 5.13](https://www.faccts.de/docs/orca/6.1/manual/contents/spectroscopyproperties/population.html#mayer-population-analysis)，其引用原始 [Mayer, Chem. Phys. Lett. 97, 270–274 (1983)](https://doi.org/10.1016/0009-2614(83)80005-0)。闭壳层 RHF 的自旋密度为零，因此

\[
B_{AB}=\sum_{\mu\in A}\sum_{\nu\in B}(PS)_{\mu\nu}(PS)_{\nu\mu},\qquad
P=C\operatorname{diag}(n_i)C^T,\quad n_i\in\{0,2\}.
\]

`P` 是原始非正交 AO 基下的总电子密度矩阵，`S` 是同一基下的重叠矩阵；`A/B` 按 PySCF 原子 AO 切片划分。数值无量纲。计算输入直接读取 C10 留存的收敛 PySCF CHK；原子顺序、精确坐标、能量和占据与已记录的单点身份一致。每步输出全部六个不同原子对，不作阈值过滤。

| 原子对 | step 1 | step 2（TS） | step 3 |
| --- | --- | --- | --- |
| 1–2（O–O） | 0.973154936561 | 0.973065423000 | 0.973149074227 |
| 1–3（O–H） | 0.952540327299 | 0.952545907723 | 0.952540140340 |
| 1–4（O–H） | 0.015592253218 | 0.015572978922 | 0.015591514611 |
| 2–3（O–H） | 0.015592264429 | 0.015573067416 | 0.015591515295 |
| 2–4（O–H） | 0.952540334356 | 0.952546192344 | 0.952540134839 |
| 3–4（H–H） | 0.000340134409 | 0.000343618912 | 0.000340393358 |

`step-NNN-mayer-pyscf.txt` 是本机计算直接写出的完整逐步日志，文件头写明 PySCF 与脚本版本/摘要、CHK/FCHK 摘要、公式和单位。只为适配现有读取器，数值表采用 `# n: atom(element) atom(element) value` 布局和 `Bond orders with absolute value` 表头；没有冒充 Multiwfn 程序输出。逐步 JSON 还保存原子 AO 切片、完整 `P/S/PS` 矩阵、FCHK 读回矩阵及所有未舍入键级。

| 原始计算日志 | SHA-256 |
| --- | --- |
| `step-001-mayer-pyscf.txt` | `7604ef384afdccd1f6ac23a1e8b62e25da228237c1943dfe116cfbdce4022acc` |
| `step-002-mayer-pyscf.txt` | `5595c1e555f74a0afbfda1223ddbd6f7261138ad5288d86cf3ef2b7f82de149b` |
| `step-003-mayer-pyscf.txt` | `051f4298de40c8287c5344cc0eb6bb6965461851b37e7fcc4600d993740e669f` |

验证见 `mayer-pyscf-report.json` 和三份逐步 JSON：

- **Passed**：矩阵乘法/块求和与逐项标量四重求和分别计算全部键级，最大差 `2.3e-16`；同时验证闭壳层幂等式 `PSP=2P`。
- **Passed**：CHK/FCHK 的 AO 顺序逐项核对，MO 系数差小于 `5e-10`、密度矩阵差小于 `5.9e-9`、重叠矩阵差小于 `1.5e-9`。FCHK 打印舍入产生的 Mayer 最大差 `4.6e-9`，详细原值保留；能量舍入仍按 C10 的 `16.8E` 边界记录。
- **Passed**：`mayer_orders` 与 `import_irc_mayer` 读回三步、每步完整六对；文本只在第 12 位小数舍入，解析值与未舍入结果差不超过 `5.1e-13`。

这些是同一真实波函数的实际外部 Mayer 计算结果，满足 SOP C11 对逐步真实数值、原子对和原始文本的科学来源要求。当前 `import_irc_mayer` 的 `step_sources.format='multiwfn-output'` 表示解析语法，即 Multiwfn-compatible syntax；实际生成器是原始日志明确记录的本机 PySCF 和脚本，该格式标签不是运行 Multiwfn 的证据。本子任务只核查计算与解析，不签署 GUI、冷重开或整体 C11 通过。

已下载的官方 Multiwfn `examples/IRC/out.txt/out2.txt/out3.txt` 仅是部分原子对曲线，不能代替完整逐步分析输出；[作者教程 /200](http://sobereva.com/200)的 Multiwfn 路线仍可用于日后独立程序比对，本次尚未运行该路线。

## C12–C13：Multiwfn 实际计算与核对

目录：`multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/`，来源为上述官方 ZIP；三份 FCH 的条件均是 RB3LYP/6-31G(d)、中性单重态。原子顺序是 C、O、B、H、H、H；整体 22 电子，片段分别 14 和 8 电子。片段拼合后的原子身份完全相同，坐标与整体最大差 `2.3e-7 bohr`，与输入坐标打印精度相符。

| 输入 | 字节数 | SHA-256 |
| --- | --- | --- |
| `COBH3.fch` | 204,322 | `1b6d2fb92be7f8a364a9410764b411837e7762b33ef00d46373aebe63fc45dbc` |
| `CO.fch` | 117,525 | `24a77a144ffef788e2bf4b4f0cc6af91e33d2db9323a94291915fcae7d6158aa` |
| `BH3.fch` | 100,241 | `f7934c013e878d63057de92232a14331cae3a640ba72c4efaa63b22cbb40e9dd` |

参考构型取 `COBH3.fch`，而不是优化输入 GJF 的初始坐标。整体 FCH 电子总能量为 `-139.9711700998564 Eh`。

运行目录为 `outputs/v1-acceptance/sources/c10-c13/multiwfn-cobh3-20260927/`。本次从用户提供的 Windows 包 `examples/ETS-NOCV/COBH3/` 复制三个 FCH；其摘要与上述官方 ZIP 输入逐项一致。2026-09-27 09:57:05（Asia/Shanghai）实际运行 `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/Multiwfn.exe COBH3.fch`，耗时 0.80 秒，退出码 0，stderr 为空，stdout 明确显示版本和 **4 线程**。没有运行量子化学单点，也没有安装依赖。

运行前依据用户提供的[本地手册](../../submodules/Multiwfn/Multiwfn_manual_2026.9.1.pdf)第 3.26.2–3.26.3、4.23.1 节，以及同版本源码 [`ETS_NOCV.f90`](../../submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/ETS_NOCV.f90)、[`sub.f90`](../../submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/sub.f90) 的 `MOene2Fmat` 和 [`grid.f90`](../../submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/grid.f90) 核对菜单、公式和参数；原始网络说明为[作者 ETS-NOCV 教程 /609](http://sobereva.com/609)。本地手册 PDF SHA-256 为 `418871dc13a9c0860f4f5417935ca2848cb2251f42bce9b26e90a15717c6c9fb`。现有 Xpdf `pdftotext` 导出的文字及摘录保存在工作目录，部分 PDF 字体映射不能完整还原公式，因此公式以匹配的 Fortran 源码核对。

`stdin.txt` 是实际交互输入；初始整体 FCH 作为命令行参数传入：

```text
23
2
CO.fch
BH3.fch
-2
-4
COBH3-ETS-NOCV.txt
-5
2
7
1
COBH3-NOCV-pair1.cub
q
6
1
COBH3-NOCV-orb1.cub
6
51
COBH3-NOCV-orb51.cub
-10
q
```

`-2` 从整体实际 MO/轨道能量通过 `F=SCE(C)^-1` 重建 KS 矩阵，在 NOCV 基下求轨道能量；随后 `-4` 导出最终表。手册 3.26.2 明确说明，这是使用实际复合物 KS 矩阵的 Multiwfn 近似，不能称为使用严格过渡态矩阵 `F_TS` 的 ETS 能量；所有 pair 能量之和也不能当作严格 `ΔE_orb`。该方法定义与输入参考态是来源记录的一部分。

完整 stdout 会同时包含未求能量时的零值表和求能量后的表；当前解析器对相同 pair 的冲突能量会拒绝。因此 C12 导入 `-2` 之后由 `-4` 导出的单份最终表，同时另存完整运行日志。C13 必须绑定这份最终表的 `Total`/pair 1。

最终表默认打印阈值为 `|λ| ≥ 0.001`：程序求出 26 对/51 个 NOCV 轨道，表中保留 9 个显著 pair，单位 `kcal/mol`、自旋 `Total`。它不是全部零贡献小 pair 的无阈值表。下面是 C12 应读到的数值：

| pair | pair 能量 | 正/负轨道 | 正特征值 | 正/负轨道能量 |
| --- | --- | --- | --- | --- |
| 1 | -77.88 | 1 / 51 | 0.56514 | -120.88 / 16.93 |
| 2 | -15.83 | 2 / 50 | 0.40205 | -139.60 / -100.22 |
| 3 | -15.84 | 3 / 49 | 0.40204 | -139.62 / -100.23 |
| 4 | -5.53 | 4 / 48 | 0.13007 | -44.60 / -2.06 |
| 5 | -0.41 | 5 / 47 | 0.03704 | -18.25 / -7.19 |
| 6 | -0.41 | 6 / 46 | 0.03703 | -18.19 / -7.13 |
| 7 | -0.65 | 7 / 45 | 0.03419 | 21.33 / 40.48 |
| 8 | -0.06 | 8 / 44 | 0.00834 | -308.53 / -301.42 |
| 9 | -0.02 | 9 / 43 | 0.00273 | -1661.86 / -1655.69 |

负特征值为相应正值的相反数；表内打印的 pair 能量总和为 `-116.63 kcal/mol`。各行的 `λ+ ε+ + λ− ε−` 与已打印 pair 能量均在特征值 5 位小数、能量 2 位小数的舍入界限内。

`7` 输出的是 `λ+ ψ1² + λ− ψ51²` 的 signed pair density；另用 `6` 从同次分析、同一网格导出轨道 1 和 51，仅供独立核对。C13 参数是 **pair 1、Total、electron/bohr^3**，不将轨道振幅当成 pair density。

| C13 网格与核对 | 实测值 |
| --- | --- |
| 网格模式 | 中等 `2`；`ETS_NOCV.f90:329` 将扩展距离设为 **3 bohr**，覆盖主 settings 中的 6 bohr 默认值 |
| 形状 / 体素数 | `74 × 92 × 78` / `531024` |
| 原点（bohr） | `(-5.207033, -6.130225, -4.914148)` |
| 步长向量（bohr） | `(0.127656,0,0)`、`(0,0.127656,0)`、`(0,0,0.127656)` |
| 数值范围（electron/bohr^3） | `-0.409774` 至 `0.0834129` |
| 正 / 负体素数 | `289153` / `241871` |
| 原始 float64 C-order 数组 SHA-256 | `41a25a1f1cd7d8ed0e8f9c64054e60db42136e02c758b1efdb7e93367315351b` |
| 逐体素公式核对 | 最大绝对差 `8.3639085668e-7 electron/bohr^3`；全部体素均小于各自舍入界限，最大误差/局部界限 `0.620673` |

Cube 使用 6 位有效数字输出，表中特征值使用 5 位小数；`verify_cobh3_multiwfn.py` 对每个体素分别传播这两类打印误差，没有以一个任意固定容差替代。三份 Cube 的原子顺序、几何、网格形状、原点和步长完全对应；`import_ets` 与 `import_nocv` 均 **Passed**，关联值原样保存在 `verification.json`。

有限网格积分诊断保留原值：pair 1 净积分 `-0.002055601515 electron`，轨道 1/51 的平方积分为 `0.995710775917` / `0.999348046741`。这些数值反映当前中等网格和有限 3 bohr 扩展范围，未作归一化或修正，也不代表网格收敛性测试通过。

执行文件及证据摘要如下；全部 19 个输出/脚本的实际字节数和摘要见 `sha256-manifest.json`，其 SHA-256 为 `dcca792828b913c42e66ce88717ef4db04efcaffe7171a0004a9dfb3eef4baa0`。`run-report.json` 另记录原始执行脚本快照、当前复跑脚本、EXE、手册及相关源文件摘要。当前复跑脚本只在尚无 stdout 的目录执行，保护既有证据。

| 文件 | SHA-256 |
| --- | --- |
| `Multiwfn.exe` | `64d9660cf859a94882a3df80d840cef8f80493e402b32993cc0cea068ca35421` |
| 原始 `settings.ini` | `243369dd9ace19cd3d1a2b8273ad81bb340fe8f282b1d9d33e98205fc0d06104` |
| 本次 `settings.ini`（4 线程、`isilent=1`） | `bbfc4f49a32a473ca381868d8ac7067667ed91374afdba516c16f9c79cf9cbe0` |
| `stdin.txt` | `ec413bbbe3de391578c3f09976ea2f3360aad73b047a598b08f96b661a1626ae` |
| `stdout.txt` | `0c8c3c844c1b0d1146b64dc595b04c49a66d46982cbb6033ae3aff7d1fe73c10` |
| `COBH3-ETS-NOCV.txt`（1,148 字节） | `59fd8d65aebf2bdfb809fc5d84eba621065398895b4faab1c9a78b470c699c70` |
| `COBH3-NOCV-pair1.cub`（7,611,905 字节） | `bf22e918358bc7353e8d7a7b0e5d00667e6262d83005d21fd9c8879b9c5b5495` |
| `COBH3-NOCV-orb1.cub` | `fd4667a8f6f203d9fe9e5aec5ccf1ff7de3b11f3d15db58c7ff7e74902918031` |
| `COBH3-NOCV-orb51.cub` | `b18f0bf82f2825bffb0e08ac8c13d18430631df5e644abecea5c85fdf7dce0b8` |
| `verification.json` | `83d694665e1aed03407c075cebbd5155609910a78dd10146eeb051f0dde1be94` |

许可与引用遵循本页来源锁内 Multiwfn 条款；本轮第三方原件及生成的 Cube 留在本地 `outputs/`，没有加入候选扩展 ZIP。C12/C13 数据生成和科学解析已通过；本子任务没有操作 Blender，也没有将其替代为 GUI、渲染、冷重开或独立人工签署通过。
