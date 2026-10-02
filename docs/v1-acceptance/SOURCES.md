# SOP 与科学回归输入目录

本清单固定当前 `0.0.1` 候选的本地输入。SHA-256 是原始文件字节摘要；验收前用 `Get-FileHash <路径> -Algorithm SHA256` 复核。样本不得随扩展 ZIP 分发。本地大样本位于忽略目录 `tests/data/local/`；S01–S08 的已有来源锁见 [`tests/data/complex-example-sources.json`](../../tests/data/complex-example-sources.json) 和 [`tests/data/local-log-downloads.json`](../../tests/data/local-log-downloads.json)。

| ID | 本地路径（相对仓库根） | 固定公开来源、版本和许可 | SHA-256 | 计算条件 / 用途 |
| --- | --- | --- | --- | --- |
| S01 | `tests/data/local/complex-examples/dvb_un_sp.fchk` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/FChk/basicGaussian16/dvb_un_sp.fchk)，程序仓库 BSD-3-Clause；数据文件许可未单列确认 | `32ed4471dc01913f1a6d5e7b5238745ea4489d98fd19a989fe56c254b7c05972` | Gaussian 16；UB3LYP/STO-3G；DVB 自由基阳离子，20 原子，+1、双重态；MO 和自旋密度 |
| S02 | `tests/data/local/complex-examples/dvb_ir.out` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/Gaussian/basicGaussian16/dvb_ir.out)，程序仓库 BSD-3-Clause；数据文件许可未单列确认 | `bc1a21de15ada135d5188b11d44226389022d92488ddfa8163ba7d4d713e5061` | Gaussian 16；B3LYP/STO-3G；中性 DVB，20 原子；54 个振动模式及 IR |
| S03 | `tests/data/local/complex-examples/Trp_polar.fchk` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/FChk/basicGaussian16/Trp_polar.fchk)，程序仓库 BSD-3-Clause；数据文件许可未单列确认 | `04a1cd071eb66ec4aeeffd0f6a198e2294ad9ef483d3ce3beaf94a839a81e88d` | Gaussian 16；RHF/STO-3G；色氨酸，27 原子；密度、ESP、电荷和偶极 |
| S04 | `tests/data/local/complex-examples/Trp_polar.log` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/Gaussian/basicGaussian16/Trp_polar.log)，程序仓库 BSD-3-Clause；数据文件许可未单列确认 | `42bf0641a49d6944847b0368ca35d3ff5367e31abd22f3821bb1d009ae3ca82b` | 同 S03；核对 Log 计算段、能量、原子顺序及偶极 |
| S05 | `tests/data/local/complex-examples/chemtools-h2o_dimer_pbe_sto3g.fchk` | [ChemTools 47c9fe2](https://github.com/theochem/chemtools/blob/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data/h2o_dimer_pbe_sto3g.fchk)，仓库 GPL-3.0-or-later | `d3801a7a8b13c1a5b106440e5eefab2e6e76b0f1e47181a33270406154efe03e` | Gaussian 格式；PBE/STO-3G；水二聚体，6 原子；Cube 对照构型 |
| S06 | `tests/data/local/complex-examples/chemtools-h2o_dimer_pbe_sto3g-dens.cube` | [ChemTools 47c9fe2](https://github.com/theochem/chemtools/blob/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data/h2o_dimer_pbe_sto3g-dens.cube)，仓库 GPL-3.0-or-later | `c033795323068422872bb65d221f72e30e83e3d3d4b18dc41fd20ee2d6a6aefc` | 与 S05 同构型；NCIPLOT 输出，数值为 **100 × sign(λ₂)ρ**，不能直接标成普通电子密度 |
| S07 | `tests/data/local/complex-examples/chemtools-h2o_dimer_pbe_sto3g-grad.cube` | [ChemTools 47c9fe2](https://github.com/theochem/chemtools/blob/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data/h2o_dimer_pbe_sto3g-grad.cube)，仓库 GPL-3.0-or-later | `33ff13185dc4d97e70788c344049b55422a403100c88836c238f802df26a577d` | 同构型的 NCIPLOT RDG 场，部分点为过滤哨兵；不能当作 IGMH/IRI |
| S08 | `tests/data/local/log-examples/water_neutral_nbo_opt_freq.out` | [cclib-data a16cc80](https://github.com/cclib/cclib-data/blob/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian16/water_neutral_nbo_opt_freq.out)；该数据仓库未找到可确认的独立许可，**发布许可待核** | `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519` | Gaussian 16 A.03、Gaussian NBO 3.1；HF/STO-3G opt/freq/pop=nbo；选 job 2、NBO 块 1，7 个 NBO 与 2 个 E(2) |
| S09 | `tests/data/local/sop/igmh-phenol/phenol_di-dg_inter.cub` | [xyzrender 69a219f](https://github.com/aligfellow/xyzrender/blob/69a219f6474eae20886726c2270806e27de98e77/examples/structures/phenol_di-dg_inter.cub)，仓库 MIT；该数据更早的生成来源未说明 | `c2e200ac5783698d260056a24a193daaa06f46f5a3e156cd5250fd224ce5d0de` | 苯酚二聚体、26 原子；Multiwfn 生成的 IGMH `δg_inter`；92×75×77 网格，原值范围 `0–0.0357952`；理论级别、片段和 Multiwfn 版本待核 |
| S10 | `tests/data/local/sop/igmh-phenol/phenol_di-dg_intra.cub` | [xyzrender 69a219f](https://github.com/aligfellow/xyzrender/blob/69a219f6474eae20886726c2270806e27de98e77/examples/structures/phenol_di-dg_intra.cub)，仓库 MIT；更早来源待核 | `160c93255985ecd8c3790e0d8988fa869c912f7f1c3a8609a0b3c8da38a5622e` | 同构型/同网格的 IGMH `δg_intra`，原值范围约 `1.12507e-10–0.733392`；计算条件待核 |
| S11 | `tests/data/local/sop/igmh-phenol/phenol_di-sl2r.cub` | [xyzrender 69a219f](https://github.com/aligfellow/xyzrender/blob/69a219f6474eae20886726c2270806e27de98e77/examples/structures/phenol_di-sl2r.cub)，仓库 MIT；更早来源待核 | `ed2fc856d75eee59268304cadd05cbba0827aaf2abe52eff7f2c88837d886911` | 同构型/同网格 `sign(λ₂)ρ` 着色场，原值范围 `-146.966–0.282149`；色域应取局部范围而非全局极值，单位约定待核 |

别名检查只改变扩展名，不改变内容：`tests/data/local/aliases/water_dimer.fch` 是 S05 的逐字节副本，摘要同 S05；`tests/data/local/aliases/water_dimer_density.cub` 是 S06 的逐字节副本，摘要同 S06；`tests/data/local/aliases/water_neutral_nbo_opt_freq.log` 是 S08 的逐字节副本，摘要同 S08。缺失时在仓库根目录 PowerShell 执行：

```powershell
New-Item -ItemType Directory -Force tests/data/local/aliases | Out-Null
Copy-Item tests/data/local/complex-examples/chemtools-h2o_dimer_pbe_sto3g.fchk tests/data/local/aliases/water_dimer.fch
Copy-Item tests/data/local/complex-examples/chemtools-h2o_dimer_pbe_sto3g-dens.cube tests/data/local/aliases/water_dimer_density.cub
Copy-Item tests/data/local/log-examples/water_neutral_nbo_opt_freq.out tests/data/local/aliases/water_neutral_nbo_opt_freq.log
```

S09–S11 如在本机缺失，可从固定提交重新取得；在仓库根目录 PowerShell 执行后，逐个核对上表摘要：

```powershell
$igmhDir = 'tests/data/local/sop/igmh-phenol'
$igmhRevision = '69a219f6474eae20886726c2270806e27de98e77'
New-Item -ItemType Directory -Force $igmhDir | Out-Null
foreach ($name in @('phenol_di-dg_inter.cub', 'phenol_di-dg_intra.cub', 'phenol_di-sl2r.cub')) {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/aligfellow/xyzrender/$igmhRevision/examples/structures/$name" -OutFile "$igmhDir/$name"
    Get-FileHash "$igmhDir/$name" -Algorithm SHA256
}
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/aligfellow/xyzrender/$igmhRevision/LICENSE" -OutFile "$igmhDir/LICENSE"
```

## 本轮补充的真实波函数与 IRC 输入

以下是本轮已下载或真实计算生成的输入，原件位于忽略目录。核查依据见 [C07–C09 来源研究](../research/sop-real-sources-c07-c09.md)和 [C10–C13 来源与生成记录](../research/sop-real-sources-c10-c13.md)。波函数齐全不等于外部分析输出已经生成，也不替代 GUI、渲染、冷重开或人工签署。

| ID | 本地路径（相对仓库根） | 固定公开来源、版本和许可 | SHA-256 | 计算条件 / 用途 |
| --- | --- | --- | --- | --- |
| S12 | `tests/data/local/sop/c07-c09-research/file/PhenolDimer.fchk` | [作者 IRI 教程输入档](http://sobereva.com/attach/598/file.zip)，Last-Modified 2021-05-31；未附独立数据许可，仅供本地验收 | `3a4b03c8afa4b18ad28820b10d4c40503aa539ada196a33958a633118943b252` | Gaussian 16 A.03；B3LYP-D3(BJ)/6-311G**；26 原子、中性单重态、100 电子、324 基函数；`Total Energy=-615.1617590953192 Eh`，FCHK 坐标为 Bohr；C07 IGMH/IRI 后处理输入，生成场见 S25–S28 |
| S13 | `tests/data/local/sop/c07-c09-research/IGMH_tutorial/file/AT.wfn` | [作者 IGMH 教程](http://sobereva.com/multiwfn/res/IGMH_tutorial.zip)，Last-Modified 2025-11-24；未附独立数据许可，仅供本地验收 | `42e50ba8160bb4be8c327277f5818460b33ab67b5ade2dba52595307f3505c6d` | 30 原子 AT 碱基对、68 占据轨道；WFN 不含完整计算 route，方法/基组需结合随包教程和原始计算记录核实；教程片段为 `15–29` 与补集，坐标为 Bohr；备用后处理输入 |
| S14 | `tests/data/local/sop/c07-c09-research/IRI_tutorial/phenol_dimer.wfn` | [作者 IRI 教程](http://sobereva.com/multiwfn/res/IRI_tutorial.zip)，Last-Modified 2025-06-28；未附独立数据许可，仅供本地验收 | `4147284f300a348a92761081e09efa2dd7bd080993f7c28162fbd51e35b64c53` | 26 原子、50 占据轨道，坐标为 Bohr；WFN 未声明方法/基组，尚未与 S12 建立逐数组计算身份核对；备用后处理输入 |
| S15 | `tests/data/local/sop/c10-c13/source-peroxide_irc.fchk` | [qc-iodata 1.0.1 官方 wheel](https://files.pythonhosted.org/packages/1c/44/20396e1a1096076a04452db27caf3d97b18fe848a21772b9b439b46bb7af/qc_iodata-1.0.1-py3-none-any.whl) 内 `iodata/test/data/peroxide_irc.fchk`；wheel 匹配项目依赖锁，随包 LGPL v3，样本未单列许可 | `a11036281c4a5257f67d29a580126a6153e96cec2a6fd00216aef05f80f3ec6f` | H₂O₂ IRC，RHF/STO-3G，中性单重态，4 原子 `[8,8,1,1]`、18 电子、21 构型；原 Gaussian 精确版本未给出；坐标为 Bohr、能量为 Eh，反应坐标单位未声明 |
| S16 | `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/step-001.fchk` | S15 的原构型 12；本机 PySCF 2.13.1 真实单点，IOData 1.0.1 导出；源数据许可同 S15，本地产物不随扩展分发 | `df38dd4180f7068f6c099eb3b7cfdfae8a585992d1e91b6216af526a005496d4` | RHF/STO-3G，4 原子、中性单重态；SCF 收敛；FCHK 能量 `-148.750534 Eh`，坐标为 Bohr；C10 step 1、C11 对应波函数 |
| S17 | `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/step-002.fchk` | S15 的原构型 1（TS）；生成程序、许可边界同 S16 | `a48eed63f663c4025fc39a36e0407a0d467857673c0c289e36dc441346fe748a` | 同 S16 理论条件；SCF 收敛；FCHK 能量 `-148.750432 Eh`，坐标为 Bohr；C10 step 2、C11 对应波函数 |
| S18 | `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/step-003.fchk` | S15 的原构型 2；生成程序、许可边界同 S16 | `b1005a583c1b73fe770dd3afd874cad0b40561b4a319301c78123653874946c4` | 同 S16 理论条件；SCF 收敛；FCHK 能量 `-148.750528 Eh`，坐标为 Bohr；C10 step 3、C11 对应波函数 |
| S19 | `tests/data/local/sop/c10-c13/multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/COBH3.fch` | [Multiwfn 2026.9.20 官方包](http://sobereva.com/multiwfn/misc/Multiwfn_2026.9.20_bin_Linux_noGUI.zip)内示例；仅提取数据，Linux 程序未运行；自定义程序许可、示例未单列许可，仅供本地验收 | `1b6d2fb92be7f8a364a9410764b411837e7762b33ef00d46373aebe63fc45dbc` | RB3LYP/6-31G(d)，中性单重态；6 原子 C/O/B/H/H/H、22 电子；总能量 `-139.9711700998564 Eh`，坐标为 Bohr；C12/C13 参考构型及整体波函数 |
| S20 | `tests/data/local/sop/c10-c13/multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/CO.fch` | 同 S19 官方版本和许可边界 | `24a77a144ffef788e2bf4b4f0cc6af91e33d2db9323a94291915fcae7d6158aa` | RB3LYP/6-31G(d)，中性单重态；CO 片段、14 电子；坐标为 Bohr；与 S19 关联的 ETS-NOCV 片段输入 |
| S21 | `tests/data/local/sop/c10-c13/multiwfn-data/Multiwfn_2026.9.20_bin_Linux_noGUI/examples/ETS-NOCV/COBH3/BH3.fch` | 同 S19 官方版本和许可边界 | `f7934c013e878d63057de92232a14331cae3a640ba72c4efaa63b22cbb40e9dd` | RB3LYP/6-31G(d)，中性单重态；BH₃ 片段、8 电子；坐标为 Bohr；S20/S21 拼合与 S19 原子顺序一致，最大坐标差 `2.3e-7 Bohr` |

S12–S14 的原始 Gaussian 运行日志未随所用归档提供；S12 本轮 Multiwfn 后处理日志已保存，见下文 C07 证据。S12 的 Gaussian 版本、route 与能量直接取自 FCHK，不据此补写优化收敛过程。其余下载的研究备用波函数及每个归档成员的摘要保存在 `c07-c09-research/extracted-manifest.json`，未选为本轮案例输入。

源归档也固定摘要：`c07-c09-research/iri-blog-files.zip` 为 `77878e0b602faf3939c80e17c3559f59ea43fc4eee311bb22acefe1870f05f57`，`IGMH_tutorial.zip` 为 `8b54bf3e4fa34ea9e95eb08b176f0f52dc32f3a907c0dddc97d31094c54ee7e8`，`IRI_tutorial.zip` 为 `b40e2dee6d979877c980fb63fe83528a91b76f7e08641bdb1ccb6809e0ce74f5`；`c10-c13/Multiwfn_2026.9.20_bin_Linux_noGUI.zip` 为 `6347413e5d066508f2b121cfb269a66f8ea9b7247720b1794ad2bafe45b63cc3`。这里的目录均相对 `tests/data/local/sop/`。下载版本与响应头见两份来源研究链接的本地 manifest。

C10 的导入入口为 `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/steps.csv`，SHA-256 为 `e364c78eb296bb63048f6ce6b64226b4ada40bce553e7bc2e05c70d8b198f1ba`。清单按原反应坐标递增排列 `12 → 1 → 2`，对应 `-0.105685976 → 0 → 0.105689581`；保留原值且不补写未声明的反应坐标单位。这是原 21 构型中跨 TS 的三个相邻点，三份完整波函数均由对应构型重新计算。

S16–S18 的共同生成设置为 RHF/STO-3G、charge 0、spin 0、`conv_tol=1e-10`、`max_cycle=100`、2 线程、关闭对称性。完整精度电子总能量依次为 `-148.75053390766712`、`-148.75043183918416`、`-148.75052755326928 Eh`；FCHK 写入精度造成最大 `4.4674e-7 Eh` 舍入差，界面以表中 FCHK 源值为比较基准。脚本 `c10-c13/generate_irc_pyscf.py`、每步 `step-NNN-input.json`、`step-NNN-scf.log`、CHK、Molden 和最终 FCHK 均保留；生成及读回证据为 `peroxide-irc-pyscf/generation-report.json`，SHA-256 `c7949ca9ecfebbee00adc4fa359f1de59dc678231115ea44eb9606a48e60f0fc`，全部日志摘要见 `c10-c13/download-and-generation-hashes.json`。三步 SCF、波函数完整性及当前 IRC 解析检查为 **Passed**；这项记录不覆盖 GUI 等验收项。

本轮 C11 已使用对应 S16–S18 的收敛 PySCF CHK 计算真实 Mayer 键级，生成器是 **PySCF 2.13.1 + NumPy 2.5.0 + 本机 `generate_mayer_pyscf.py`**，解释器为 Python 3.13.14，沿用上述 RHF/STO-3G、中性闭壳层条件。每步输出四个原子的全部六个不同原子对，阈值为 `0.0`，单位为 **dimensionless（无量纲）**，数值打印至小数点后 12 位。文本使用 **Multiwfn-compatible syntax**；当前 `step_sources.format='multiwfn-output'` 表示解析语法，实际 producer 以文件头和本清单为准，**C11 Mayer 数值由 PySCF 与本机脚本生成**。

| ID | 本地路径（相对仓库根） | 来源、生成器与许可边界 | SHA-256 | 计算条件 / 用途 |
| --- | --- | --- | --- | --- |
| S22 | `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/step-001-mayer-pyscf.txt` | 对应 S16 的真实 PySCF CHK，由上述本机脚本直接计算并记录；本地产物，输入来源与许可边界同 S15–S18，不随扩展分发 | `7604ef384afdccd1f6ac23a1e8b62e25da228237c1943dfe116cfbdce4022acc` | C11 step 1，原 IRC 构型 12；6 对 Mayer 值；1–2（O–O）为 `0.973154936561`；1,337 字节 |
| S23 | `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/step-002-mayer-pyscf.txt` | 对应 S17 的真实 PySCF CHK；生成器和许可边界同 S22 | `5595c1e555f74a0afbfda1223ddbd6f7261138ad5288d86cf3ef2b7f82de149b` | C11 step 2，原 IRC 构型 1（TS）；6 对 Mayer 值；1–2 为 `0.973065423000`；1,336 字节 |
| S24 | `tests/data/local/sop/c10-c13/peroxide-irc-pyscf/step-003-mayer-pyscf.txt` | 对应 S18 的真实 PySCF CHK；生成器和许可边界同 S22 | `051f4298de40c8287c5344cc0eb6bb6965461851b37e7fcc4600d993740e669f` | C11 step 3，原 IRC 构型 2；6 对 Mayer 值；1–2 为 `0.973149074227`；1,336 字节 |

闭壳层 Mayer 公式为 `B_AB = Σ_(μ∈A) Σ_(ν∈B) (PS)_μν (PS)_νμ`，其中 `P = C diag(n) Cᵀ` 是占据数为 2/0 的总电子 AO 密度，`S` 是同一非正交 AO 基的重叠矩阵；RHF 自旋密度为零。公式核对依据为 [ORCA 6.1 官方手册 5.1.4、式 5.13](https://www.faccts.de/docs/orca/6.1/manual/contents/spectroscopyproperties/population.html#mayer-population-analysis)及其引用的 [Mayer 原始论文](https://doi.org/10.1016/0009-2614(83)80005-0)。原子编号与 C10 相同：1/2 为 O，3/4 为 H；每步顺序固定为 `1–2, 1–3, 1–4, 2–3, 2–4, 3–4`。

C11 清单、逐步完整矩阵记录和汇总报告的实际摘要已于 2026-09-27 复核。下表路径相对 `tests/data/local/sop/c10-c13/`；S22–S24 的文件头和逐步 JSON 另记录输入 CHK、对应 FCHK、SCF 日志、生成输入及脚本 SHA。

| 文件 | 字节数 | SHA-256 |
| --- | --- | --- |
| `peroxide-irc-pyscf/mayer-pyscf.csv` | 103 | `3627fbb0c0e271882dd9852c94efd3f6691f724bb9636465edcfe52d362d65fc` |
| `generate_mayer_pyscf.py` | 10,200 | `9816f0ddd877c909c88d3c50ae44aaf5b81cb3dcf1741e36b555d5800fea4fb0` |
| `peroxide-irc-pyscf/step-001-mayer-pyscf.json` | 22,734 | `d7b4a4eb15fbc6aa21a56a844ce21b4f311266b132e1cb6636aa86fdfe4b5936` |
| `peroxide-irc-pyscf/step-002-mayer-pyscf.json` | 22,906 | `1efdee43dfc4d839b6fcf445fbcbf5cb78ef5942e7f032a04ae1c781000a0631` |
| `peroxide-irc-pyscf/step-003-mayer-pyscf.json` | 22,836 | `637d3e664cfca82d6c183c1350df99d9d1f240d636781916774e2b589b6195e4` |
| `peroxide-irc-pyscf/mayer-pyscf-report.json` | 1,285 | `2a29ad17150b07023085fd9340695bcbe7583a9d6b9b952fa40dfecfa234027a` |

三步共 18 个 Mayer 值的矩阵运算与逐项标量求和交叉核对为 **Passed**，最大差 `2.220446049250313e-16`。对应 CHK/FCHK 的原子、坐标、AO 顺序、占据和波函数身份核对为 **Passed**；FCHK 输出舍入引起的 MO 系数最大差小于 `5e-10`、密度矩阵差小于 `5.9e-9`、重叠矩阵差小于 `1.5e-9`，Mayer 最大差为 `4.537944020555074e-9`；能量舍入界限仍采用上述 C10 记录。完整矩阵与未舍入数值保存在三份 JSON。当前 `mayer_orders` 和 `import_irc_mayer` 读回三步、每步六对为 **Passed**，文本舍入误差不超过 `5.1e-13`。这些检查覆盖真实数值与解析，不代替 SOP GUI、渲染、冷重开和人工验收。

## 本轮 Multiwfn 真实分析输出

以下 **11 个实际分析导入文件**于 2026-09-27 用用户提供并授权的 `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/Multiwfn.exe` 生成，版本为 **2026.9.20、Windows x64、4 线程**；EXE SHA-256 为 `64d9660cf859a94882a3df80d840cef8f80493e402b32993cc0cea068ca35421`。程序及相关源码、2026.9.1 手册的摘要保存在各生成目录的 provenance/run 报告中。[Multiwfn 许可](http://sobereva.com/multiwfn/download.html)允许免费学术/商业使用，规定引用 [Lu and Chen (2012)](https://doi.org/10.1002/jcc.22885)与 [Lu (2024)](https://doi.org/10.1063/5.0216272)；程序许可不代替 S12、S19–S21 示例数据的独立再分发许可。下列本地产物均不随扩展分发。

| ID | 本地路径（相对仓库根） | 来源、生成器与许可边界 | SHA-256 | 计算条件 / 用途 |
| --- | --- | --- | --- | --- |
| S25 | `tests/data/local/sop/c07-c09-research/phenol-2026-09-27/igmh/dg_inter.cub` | S12 的真实波函数；上述 Multiwfn；[作者 IGMH 方法与教程](http://sobereva.com/621)，数据许可边界同 S12 | `3d8c044dbbac7a08f18f7bb6a4fa1a71628157c24d3b781bcb0da993bcc99695` | C07 IGMH 几何场；片段 `1–13 / 14–26`，`δg_inter`、`electron/bohr^4`；122×66×66 同网格；范围 `0–0.0500603` |
| S26 | `tests/data/local/sop/c07-c09-research/phenol-2026-09-27/igmh/sl2r.cub` | 同 S25 输入、生成器与许可边界，同次 IGMH 运行 | `ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514` | C07 IGMH 颜色场；`sign(λ₂)ρ`、`electron/bohr^3`；网格与 S25 相同，范围 `-123.65–0.278699` |
| S27 | `tests/data/local/sop/c07-c09-research/phenol-2026-09-27/iri/func2.cub` | S12 的真实波函数；上述 Multiwfn；[作者 IRI 定义与输入](http://sobereva.com/598)，数据许可边界同 S12 | `a08baaa600115d4321c826be6c1783ecc17649a3b52728f363cbe5faf7e41a1f` | C07 IRI 几何场；`a=1.1`，`a.u. (electron^-0.1 bohr^-0.7)`；122×66×66 网格；范围 `0.0444571–149.276` |
| S28 | `tests/data/local/sop/c07-c09-research/phenol-2026-09-27/iri/func1.cub` | 同 S27 输入、生成器与许可边界，同次 IRI 运行 | `ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514` | C07 IRI 颜色场；`sign(λ₂)ρ`、`electron/bohr^3`；与 S27 同网格；与 S26 字节及数组相同 |
| S29 | `tests/data/local/sop/multiwfn-local/C08/surfanalysis.pdb` | S03（cclib f90be37、BSD-3-Clause）；上述 Multiwfn；[作者 ESP 表面说明](http://sobereva.com/443)，本地产物 | `ac23f9279c968f9e89cdc8069fb060c0dabfbf3a3aeab74a3f437b6d22c6057d` | C08 极值；RHF/STO-3G、S03 原构型；11 最大值/8 最小值，B-factor 为 `kcal/mol`、坐标 Å；表面 `ρ=0.001 electron/bohr^3` |
| S30 | `tests/data/local/sop/multiwfn-local/C08/stdout.log` | 同 S29 的完整原始 stdout；[作者面积统计说明](http://sobereva.com/196)，输入许可边界同 S03 | `5c16de7d68ab340f673efbb7808a3748b35af8e05cdd9fb1dac942cc7614f85e` | C08 面积分布导入；40 bins、`-100–100 kcal/mol`、宽度 5；中心为 `kcal/mol`、面积为 `Å²`、百分比为 `%`；打印面积之和 `228.2405 Å²` |
| S31 | `tests/data/local/sop/multiwfn-local/C09/CPs.pdb` | S03（cclib f90be37、BSD-3-Clause）；上述 Multiwfn；[作者 AIM 拓扑说明](http://sobereva.com/445)，本地产物 | `b268ee3391a647ee4efe5c833aca2abe2705c037b21bccd358488c3b136f9c80` | C09 密度 CP；27 个 `(3,-3)`、29 个 `(3,-1)`、3 个 `(3,+1)`、0 个 `(3,+3)`；C/N/O/F 为类型标记；坐标 Å |
| S32 | `tests/data/local/sop/multiwfn-local/C09/paths.pdb` | 同 S31 波函数与运行，输入许可边界同 S03 | `4f4e33b008055a24f59f8b359db033ed817efba8618a2aca963402212715f79b` | C09 路径；58 条，按 PDB residue 号分组；坐标 Å，与 S31 对应 |
| S33 | `tests/data/local/sop/multiwfn-local/C09/CPprop.txt` | 同 S31 波函数与运行，输入许可边界同 S03 | `130a93c85feb8bbc059d93ea1c4ed3cc6c9f443b1f1695faa8ed1d67b84e8bc8` | C09 原始性质表；59 CP、类型/编号与 S31 对应；密度 `electron/bohr^3`、Laplacian `electron/bohr^5`、能量密度 `Hartree/bohr^3`；位置同时给 Bohr/Å，含原始 ESP |
| S34 | `tests/data/local/sop/c10-c13/multiwfn-cobh3-20260927/COBH3-ETS-NOCV.txt` | S19 整体与 S20/S21 片段；上述 Multiwfn；[作者 ETS-NOCV 教程](http://sobereva.com/609)，数据许可边界同 S19–S21 | `59fd8d65aebf2bdfb809fc5d84eba621065398895b4faab1c9a78b470c699c70` | C12 最终能量表；RB3LYP/6-31G(d)；9 个显著 pair，`abs(λ)≥0.001`，自旋 Total，能量 `kcal/mol`；pair 1 为 `-77.88`、轨道 1/51、特征值 ±0.56514；使用实际复合物 KS 矩阵近似 |
| S35 | `tests/data/local/sop/c10-c13/multiwfn-cobh3-20260927/COBH3-NOCV-pair1.cub` | 同 S34 的同次分析、同一 Total/pair 1；数据许可边界同 S19–S21 | `bf22e918358bc7353e8d7a7b0e5d00667e6262d83005d21fd9c8879b9c5b5495` | C13 signed pair density；`λ+ψ1²+λ−ψ51²`、`electron/bohr^3`；74×92×78 网格；范围 `-0.409774–0.0834129`；与 S19 原构型对应 |

C07 的四个 Cube 均为 7,618,853 字节。IGMH 菜单为 `20 → 11`，IRI 为 `20 → 4`；两组均选择中等网格（名义 512000 点）、分子包围盒各方向延伸 `2 Bohr`，实际 531432 点，计算间距 `0.18859124989632603 Bohr`（Cube 头打印 `0.188591`），原点 `(-11.336526, -6.170854, -6.194976) Bohr`。局部设置为 `nthreads=4`、`IGMvdwscl=0`、`IRI_rhocut=0`、`uservar=0`，保留完整 IGMH 和 `a=1.1` 的未屏蔽 IRI 场。原值单位从本地同版本源码及手册定义核对。生成目录内 `recipe.json`、`run-records.json`、`provenance.json`、各分析的 `stdin.txt/settings.ini/stdout.log`、`verification.json` 与 `sha256.json` 固定本轮条件；`dg.cub`、`dg_intra.cub` 作为加和核查证据保留。两组读取/配对及 8 个固定点的 IOData+GBasis 独立 IRI/带符号密度核查 **Passed**。

C08/C09 沿用 S03 原始 RHF/STO-3G 波函数、中性单重态、27 原子/108 电子，无构型变换。C08 表面网格间距 `0.25 Bohr`、形状 `91×65×93`；表面整体面积原值 `228.24053 Å²`。同目录 `surfanalysis.txt` 保存更高精度极值（范围 `-44.973471–34.841007 kcal/mol`），S29 与其逐项符合 PDB 打印精度。原生 Multiwfn 的最大/最小值编号分别从 1 开始，身份键为 `(kind, serial)`。C09 密度拓扑的 Euler 检查为 `27−29+3−0=1`；S33 原始 RDG 在高密度点可为默认 `RDG_maxrho=0.05` 设置产生的 100 哨兵值，按原值保留。两个生成目录均保存 `input.txt/settings.ini/stdout.log/run.json`；各输出字节摘要在 `run.json`。19 点 ESP、59 CP 的密度/Hessian 独立核查及当前解析均 **Passed**，证据为 `c07-c09-research/c08-c09-verification/verification.json`。

C12/C13 使用 S19–S21 的字节相同 Windows 示例副本：`c10-c13/multiwfn-cobh3-20260927/COBH3.fch`、`CO.fch`、`BH3.fch`。片段拼合与参考构型最大坐标差 `1.2172e-7 Å`。主功能 23 载入两个片段后，`-2` 根据实际复合物 KS 矩阵求能量，`-4` 导出 S34；它是手册 3.26.2 所述近似，不能将 pair 能量总和当作严格过渡态矩阵 `F_TS` 的 `ΔE_orb`。C12 导入单份最终 S34，完整 stdout 中同时保留求能量前后的表，不直接作为最终表导入。C13 通过同次运行的 `7 → 1` 导出 Total/pair 1，使用中等网格、3 Bohr 延伸、531024 点，步长 `0.127656 Bohr`、原点 `(-5.207033, -6.130225, -4.914148) Bohr`。同网格轨道 1/51 Cube 仅作逐体素公式核查，全部体素在打印误差界限内 **Passed**；实际 pair 净积分 `-0.002055601515 electron`，保留有限网格误差，不声称网格收敛或重新归一化。S34 的 9 行能量和 S35 的导入/关联检查均 **Passed**。

原始日志与来源摘要如下，路径相对 `tests/data/local/sop/`；完整命令流、设置、原值和科学核查见两份来源研究。

| 证据 | 本地路径 | SHA-256 |
| --- | --- | --- |
| C07 IGMH 原始日志 | `c07-c09-research/phenol-2026-09-27/igmh/stdout.log` | `746a7d1eb82a9b2438240ac56ffe28a2efb1fd32b8e2a43cd07a1f207702b553` |
| C07 IRI 原始日志 | `c07-c09-research/phenol-2026-09-27/iri/stdout.log` | `ea47aaa7d21a17031fc11638fd154093139308dda00e737e16760fc146a98bc0` |
| C07 全文件摘要 | `c07-c09-research/phenol-2026-09-27/sha256.json` | `57ed1d93e479082a90bfc49432e09440a0da8270fbd31d4a2939a37520fee9be` |
| C08 原始日志 | `multiwfn-local/C08/stdout.log`（S30） | `5c16de7d68ab340f673efbb7808a3748b35af8e05cdd9fb1dac942cc7614f85e` |
| C09 原始日志 | `multiwfn-local/C09/stdout.log` | `d060c6b3c5ae7628be91ee593d3134cc5573a3a0866e42c359f7f3268390a60f` |
| C12/C13 原始日志 | `c10-c13/multiwfn-cobh3-20260927/stdout.txt` | `0c8c3c844c1b0d1146b64dc595b04c49a66d46982cbb6033ae3aff7d1fe73c10` |
| C12/C13 全文件摘要 | `c10-c13/multiwfn-cobh3-20260927/sha256-manifest.json` | `dcca792828b913c42e66ce88717ef4db04efcaffe7171a0004a9dfb3eef4baa0` |

## 外部分析结果与验收状态

C07–C13 的本轮真实输入与分析结果现已取得，固定清单共 **35 项（S01–S35）**。下表只汇总样本及科学解析状态；Blender GUI、节点、PNG、保存/移动/冷重开和独立人工签署继续按 [SOP](SOP.md) 分别记录。S09–S11 保留为早期预检材料：其生成参数仍不全，也未与 S12 建立计算身份关联；本轮 C07 科学核对使用 S25–S28。[上游示例说明](https://xyzrender.readthedocs.io/en/latest/examples/nci_surf.html)

| 功能 | 本轮导入文件与参考构型 | 样本及科学解析状态 |
| --- | --- | --- |
| IGMH 与 IRI（C07） | S12 参考波函数；IGMH 几何/颜色为 S25/S26，IRI 几何/颜色为 S27/S28。生成目录两份 `PhenolDimer.fchk` 均与 S12 字节相同 | Passed |
| ESP 表面（C08） | S03 参考；S29 `surfanalysis.pdb` 为极值，S30 `stdout.log` 为面积分布；单位及表面定义见上文 | Passed |
| AIM（C09） | S03 参考；S31 `CPs.pdb`、S32 `paths.pdb`、S33 `CPprop.txt`，59 CP/58 路径，原值及实际单位见上文 | Passed |
| IRC（C10） | `c10-c13/peroxide-irc-pyscf/steps.csv` 导入 S16–S18；原 S15 的三个相邻构型，逐步能量取自各 FCHK | Passed |
| Mayer（C11） | `c10-c13/peroxide-irc-pyscf/mayer-pyscf.csv` 导入 S22–S24，对应 S16–S18；PySCF 与本机脚本生成，每步六对、无量纲 | Passed |
| ETS-NOCV（C12） | S19 参考（计算目录 `COBH3.fch` 字节相同）；S34 单份最终表，输入片段为 S20/S21 的字节相同副本；9 个显著 Total pair | Passed |
| NOCV 场（C13） | 绑定 S34 的 Total/pair 1，导入 S35 带符号 pair density Cube，参考构型同 S19 | Passed |

S08 的许可未核清前，验收可在本地使用；不得把该数据文件加入发布包或公开案例附件。`S01–S07` 的仓库许可与文件来源是可审查线索，公开再分发仍须按各许可处理。检索线索：[IGMH_Toolbox 源码](https://github.com/houcheng-gxnu/IGMH_Toolbox)、[Multiwfn 手册中的 ESP 文件定义](https://mgcf.cchem.berkeley.edu/mgcf/Multiwfn_3.8_dev.pdf)。

## 集中输入与重建（2026-09-29）

本文件是输入的人工阅读目录；机器入口为 [`tests/data/local-inputs.json`](../../tests/data/local-inputs.json)。索引记录稳定 ID、相对路径、SHA-256、用途及使用者。`tools/local_inputs.py` 在读取前检查必需文件及摘要，缺失或变更直接失败；没有输出目录回退或自动跳过。已有受 Git 跟踪的 `tests/data/` 小样本及其来源清单保持原位。

| 输入组（相对 `tests/data/local/`） | 数据、单位、关联与用途 | 来源和限制 |
| --- | --- | --- |
| `complex-examples/` | S01–S07 的波函数、Gaussian Log、Cube；构型统一读取为 Å，源计算能量 Hartree；密度、ESP、MO 的单位按量名记录。ELF Cube 是无量纲局域函数，不能当电子密度。用于导入、场求值、振动和双场检查 | 固定 URL、许可和 SHA 见 S01–S07 与 `tests/data/complex-example-sources.json`。NCIPLOT 的缩放仍按 S06 解释 |
| `log-examples/` | S08 水优化＋频率＋NBO；`water.log` 为多构型/片段结构检查，`benzene_HPfreq.log` 核对高精度频率，`issue746-dsdpbep86.log` 核对双杂化相关能。坐标 Å、能量 Hartree、频率 cm⁻¹、IR km/mol；按所选计算段读取，不能自动跨段继承 | 逐文件 URL 和摘要见 `tests/data/local-log-downloads.json`。除 S08 已列条件外，以各原文 route 和解析器记录为准，不补猜方法/版本；本地使用，许可未确认前不再分发 |
| `sop/c07-c09-research/`、`sop/multiwfn-local/` | S12/S25–S33，真实 IGMH/IRI、ESP、AIM；`stdin.txt`、`settings.ini`、计算日志、生成/核查脚本和 provenance 随同保存。单位和计算条件见上文，显示筛选不改变原值 | Multiwfn 版本、菜单、参数和原文位置保留；历史日志中的绝对路径是当时运行记录，不改写为新执行记录 |
| `sop/c10-c13/` | S15–S24/S34–S35、逐步 FCHK/Mayer CSV、生成脚本及 SCF 日志。`steps.csv` 和 `mayer-pyscf.csv` 使用相对路径，迁移后字节摘要不变 | CSV 每步身份和同构型关联保持；生成脚本记录当时环境，重新计算仍需明确指定可用计算工具 |
| `aliases/` | `.fch/.cub/.log` 入口别名，字节与相应原始样本一致 | 用于扩展名兼容验证，不构成新的计算来源 |

迁移逐文件映射和摘要核对在 `outputs/storage-cleanup/input-migration.json`。S01–S35 原始字节不变。生成日志中列出的冗余波函数、加和核对 Cube、轨道 Cube 等辅助原件仍作为参考资料保留在原目录；集中索引覆盖当前 SOP/回归读取和来源追溯所需输入。日志中的历史摘要不代表这些计算在本次重新执行。

输入索引可用 Blender Python 执行 `tools/local_inputs.py` 完整核对；受影响场景由 `tools/prepare_sop_fixture.py` 通过已安装扩展重新读取/求值。重建密度与 ESP 使用 0.7 Å 的显示测试网格，原始波函数及外部分析条件不变，该网格不替代科学收敛检查。验证报告与科学量的源数组分别记录。

## 公开教程样本与独立获取（2026-09-30）

当前教程固定使用 [机器清单](tutorial-samples.json) 的 P01–P05，而非把 S01–S35 原件整体装入附件。逐文件 `archive_path` 是公开包解压根相对路径，`path` 是仓库规范路径，SHA-256/字节数、真实 producer、方法/基组/电荷/自旋、原子顺序、单位及实测期待值均在清单内。C01–C13 与 N01–N18 的映射、Job/block/pair 号及 Log Job 2 → 新 FCHK 的检查身份也由清单固定。显示阈值、色域、切片/剖线和网格默认值属于建议设置，GUI、渲染及人工签署保持 Not Run，由教程/综合验证分别更新。

| 能力组 | 真实来源与计算条件 | 教程入口及分发状态 |
| --- | --- | --- |
| P01 | 自定义 O₂ 构型，PySCF 2.13.1 UHF/STO-3G，中性三重态，16 电子；完整 Alpha/Beta MO，自旋与电子密度。FCHK 能量 `-147.633453 Eh` | 包内 `P01/o2-uhf.fchk` 与逐字节 `.fch`；CC BY 4.0，署名 QCBlender contributors；C01 |
| P02 | 原 S08 Gaussian 16 A.03/NBO 3.1 真实水多计算段，RHF/STO-3G；job 1 优化 4 步，job 2 有 3 模式、7 NBO/2 E(2) | **包外单独取得**：下述固定原站与 SHA 实际下载核验 Passed。数据许可未确认，不把 cclib 程序许可当作数据许可；C02/C06 |
| P03 | 自定义水二聚体，PySCF RHF/6-31G(d)，中性单重态，20 电子，源原子 `[8,1,1,8,1,1]`；Multiwfn 2026.9.20 真实 IGMH/IRI、ESP 表面极值/面积、AIM CP/路径/属性。片段 `1–3`、`4–6`；IRI a=1.1；双场同为 `91×38×156` | 包内 `P03/water-dimer.fchk/.fch`、`igmh/`、`iri/`、`esp/`、`aim/`；CC BY 4.0；C03–C05/C07–C09。独立 Cube 初始 unknown；按 manifest 识别量名与已有单位，倍率 1 |
| P04 | 自定义 H₂O₂ 初始构型；PySCF RHF/STO-3G + geomeTRIC 1.1.1 原生 TS/双向 IRC，18 电子。TS 唯一虚频 `-48.1434547807 cm^-1`，最大梯度 `1.893862e-8 Eh/Bohr`；61 个接受帧，选 0-based 帧 29/30(TS)/31 三个连续点。每点重新真实 SCF，完整 FCHK 与同一 AO 密度/重叠矩阵 Mayer | 包内 `P04/steps.csv`、`mayer-pyscf.csv`、3 份 FCHK/3 份 Mayer；CC BY 4.0；C10/C11。三步 FCHK 能量 `-148.764884/-148.764883/-148.764884 Eh`。这是当前原生 IRC，不使用旧 S15 构型，也不是三点扫描；Mayer 文本明确 producer 为 PySCF，语法兼容 Multiwfn |
| P05 | 自定义 CO/BH₃ 及整体几何，PySCF RB3LYP/6-31G(d)，整体 22 电子；同几何片段真实 SCF，Multiwfn 真实 ETS-NOCV。pair 1/Total 为轨道 1/48、特征值 ±0.54550、pair 能量 `-57.02 kcal/mol`；场 `47×50×57` | 包内 `P05/complex.fchk`、`co.fchk`、`bh3.fchk`、`nocv/ets-nocv.txt`、`nocv-pair1.cub`；CC BY 4.0；C12/C13。能量是整体 KS 轨道重构矩阵的 Multiwfn 近似，不是 F_TS 过渡态方法 |

P01/P03/P05 是自行定义的示意构型，未声称优化结构；本次场网格用于导入/显示检查，不声称科学网格收敛。Multiwfn 引用保存在样本 `NOTICE.md`。ETS-NOCV 逐体素公式、真实空间密度、构型/电子数/自旋与源值互校均 Passed，视觉表现另验。

公开 ZIP 当前本地交付位置为 `outputs/evidence/2026-10-02/tutorial-cu/final-samples/qcblender-public-tutorial-samples-v1.zip`，身份见[样本交付索引](../acceptance/tutorial-sample-delivery.json)。C01固定Alpha MO9/Beta MO7与自动HOMO Alpha8/Beta6分别记录；27份科学输入与旧包逐字节相同，旧批次报告继续绑定原包。当前包仅 27 份许可合格数据加清单/LICENSE/NOTICE；没有原站未知许可文件或程序二进制。尚未发布远程下载地址。小文件 Git 跟踪于 `tests/data/tutorial/`，较大 Cube 只保留主检出 `tests/data/local/public-tutorial/` 并进入集中索引；工作树读取大文件时显式 `--reference-root D:/workspace/QCBlender`。不要复制整套历史样本到工作树。

P02 的独立获取适用 PowerShell，在公开样本解压根新建 `P02/` 后执行。该原站定位和本地读取说明**不授予再分发权限**；许可不明日志不得加入公开包，且未承诺下载者在其环境下拥有额外使用权。cclib 官方 [安装说明](https://cclib.readthedocs.io/en/stable/how_to_install.html)说明测试日志数据存在非自由许可问题，不能由代码仓库许可证替代逐文件许可核查。

```powershell
New-Item -ItemType Directory -Force P02 | Out-Null
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/cclib/cclib-data/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian16/water_neutral_nbo_opt_freq.out' -OutFile P02/water_neutral_nbo_opt_freq.out
Get-FileHash P02/water_neutral_nbo_opt_freq.out -Algorithm SHA256
Copy-Item P02/water_neutral_nbo_opt_freq.out P02/water_neutral_nbo_opt_freq.log
```

摘要须为 `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519`，字节数 92,872；不符则停止该例。job 2/block 1 的 NBO 与 E(2) 原文、频率和 IR 强度见清单。公共包的 C02/C06 不会自动可运行：须先取得并核对该外部日志；其分发许可仍是剩余限制。

生成与验证脚本为 `tools/generate_tutorial_samples.py`、`tools/generate_tutorial_irc.py`、`tools/finalize_tutorial_samples.py`、`tools/verify_tutorial_samples.py`。根目录通过 `Path(__file__).resolve().parents[1]` 固定，外部工具/科学依赖取显式 reference-root；不依赖搬移旧生成脚本的 parents 层级。每次生成选新的不存在任务输出目录，保留真实输入/SCF CHK/Molden/FCHK、Multiwfn stdin/settings/stdout、TS Hessian/虚频/梯度和两方向 IRC 接受轨迹，避免覆盖原输入。

完整本次证据为 `outputs/evidence/2026-09-30/public-tutorial/samples/`，科学/包验收 `final-validation.json`；GUI、独立冷重开、移动重开、科研签署为 Not Run。

维护者核查：`tools/verify_tutorial_samples.py` 的常规模式使用插件科学环境，不要求 PySCF。原始 PySCF CHK 与 FCHK 密度互校须在既有计算环境中显式加 `--checkpoints`；报告单列 `original_checkpoint_density`，未运行时为 Not Run。该环境仅用于材料生成和来源互校，用户安装与教程不需要它。
