# v1 人工验收样本清单

本清单固定当前 `0.0.1` 候选的本地输入。SHA-256 是原始文件字节摘要；验收前用 `Get-FileHash <路径> -Algorithm SHA256` 复核。样本不得随扩展 ZIP 分发。已找到的文件位于忽略目录 `outputs/`；S01–S08 的已有来源锁见 [`tests/data/complex-example-sources.json`](../../tests/data/complex-example-sources.json) 和 [`tests/data/local-log-downloads.json`](../../tests/data/local-log-downloads.json)。

| ID | 本地路径（相对仓库根） | 固定公开来源、版本和许可 | SHA-256 | 计算条件 / 用途 |
| --- | --- | --- | --- | --- |
| S01 | `outputs/complex-examples/sources/dvb_un_sp.fchk` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/FChk/basicGaussian16/dvb_un_sp.fchk)，BSD-3-Clause | `32ed4471dc01913f1a6d5e7b5238745ea4489d98fd19a989fe56c254b7c05972` | Gaussian 16；UB3LYP/STO-3G；DVB 自由基阳离子，20 原子，+1、双重态；MO 和自旋密度 |
| S02 | `outputs/complex-examples/sources/dvb_ir.out` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/Gaussian/basicGaussian16/dvb_ir.out)，BSD-3-Clause | `bc1a21de15ada135d5188b11d44226389022d92488ddfa8163ba7d4d713e5061` | Gaussian 16；B3LYP/STO-3G；中性 DVB，20 原子；54 个振动模式及 IR |
| S03 | `outputs/complex-examples/sources/Trp_polar.fchk` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/FChk/basicGaussian16/Trp_polar.fchk)，BSD-3-Clause | `04a1cd071eb66ec4aeeffd0f6a198e2294ad9ef483d3ce3beaf94a839a81e88d` | Gaussian 16；RHF/STO-3G；色氨酸，27 原子；密度、ESP、电荷和偶极 |
| S04 | `outputs/complex-examples/sources/Trp_polar.log` | [cclib f90be37](https://github.com/cclib/cclib/blob/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data/Gaussian/basicGaussian16/Trp_polar.log)，BSD-3-Clause | `42bf0641a49d6944847b0368ca35d3ff5367e31abd22f3821bb1d009ae3ca82b` | 同 S03；核对 Log 计算段、能量、原子顺序及偶极 |
| S05 | `outputs/complex-examples/sources/chemtools-h2o_dimer_pbe_sto3g.fchk` | [ChemTools 47c9fe2](https://github.com/theochem/chemtools/blob/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data/h2o_dimer_pbe_sto3g.fchk)，仓库 GPL-3.0-or-later | `d3801a7a8b13c1a5b106440e5eefab2e6e76b0f1e47181a33270406154efe03e` | Gaussian 格式；PBE/STO-3G；水二聚体，6 原子；Cube 对照构型 |
| S06 | `outputs/complex-examples/sources/chemtools-h2o_dimer_pbe_sto3g-dens.cube` | [ChemTools 47c9fe2](https://github.com/theochem/chemtools/blob/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data/h2o_dimer_pbe_sto3g-dens.cube)，仓库 GPL-3.0-or-later | `c033795323068422872bb65d221f72e30e83e3d3d4b18dc41fd20ee2d6a6aefc` | 与 S05 同构型；NCIPLOT 输出，数值为 **100 × sign(λ₂)ρ**，不能直接标成普通电子密度 |
| S07 | `outputs/complex-examples/sources/chemtools-h2o_dimer_pbe_sto3g-grad.cube` | [ChemTools 47c9fe2](https://github.com/theochem/chemtools/blob/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data/h2o_dimer_pbe_sto3g-grad.cube)，仓库 GPL-3.0-or-later | `33ff13185dc4d97e70788c344049b55422a403100c88836c238f802df26a577d` | 同构型的 NCIPLOT RDG 场，部分点为过滤哨兵；不能当作 IGMH/IRI |
| S08 | `outputs/log-examples/water_neutral_nbo_opt_freq.out` | [cclib-data a16cc80](https://github.com/cclib/cclib-data/blob/a16cc80ea29e8baec60abd0df346ce6862f52531/Gaussian/Gaussian16/water_neutral_nbo_opt_freq.out)；该数据仓库未找到可确认的独立许可，**发布许可待核** | `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519` | Gaussian 16 A.03、Gaussian NBO 3.1；HF/STO-3G opt/freq/pop=nbo；选 job 2、NBO 块 1，7 个 NBO 与 2 个 E(2) |
| S09 | `outputs/v1-acceptance/sources/igmh-phenol/phenol_di-dg_inter.cub` | [xyzrender 69a219f](https://github.com/aligfellow/xyzrender/blob/69a219f6474eae20886726c2270806e27de98e77/examples/structures/phenol_di-dg_inter.cub)，仓库 MIT；该数据更早的生成来源未说明 | `c2e200ac5783698d260056a24a193daaa06f46f5a3e156cd5250fd224ce5d0de` | 苯酚二聚体、26 原子；Multiwfn 生成的 IGMH `δg_inter`；92×75×77 网格，原值范围 `0–0.0357952`；理论级别、片段和 Multiwfn 版本待核 |
| S10 | `outputs/v1-acceptance/sources/igmh-phenol/phenol_di-dg_intra.cub` | [xyzrender 69a219f](https://github.com/aligfellow/xyzrender/blob/69a219f6474eae20886726c2270806e27de98e77/examples/structures/phenol_di-dg_intra.cub)，仓库 MIT；更早来源待核 | `160c93255985ecd8c3790e0d8988fa869c912f7f1c3a8609a0b3c8da38a5622e` | 同构型/同网格的 IGMH `δg_intra`，原值范围约 `1.12507e-10–0.733392`；计算条件待核 |
| S11 | `outputs/v1-acceptance/sources/igmh-phenol/phenol_di-sl2r.cub` | [xyzrender 69a219f](https://github.com/aligfellow/xyzrender/blob/69a219f6474eae20886726c2270806e27de98e77/examples/structures/phenol_di-sl2r.cub)，仓库 MIT；更早来源待核 | `ed2fc856d75eee59268304cadd05cbba0827aaf2abe52eff7f2c88837d886911` | 同构型/同网格 `sign(λ₂)ρ` 着色场，原值范围 `-146.966–0.282149`；色域应取局部范围而非全局极值，单位约定待核 |

别名检查只改变扩展名，不改变内容：`outputs/v1-acceptance/aliases/water_dimer.fch` 是 S05 的逐字节副本，摘要同 S05；`outputs/v1-acceptance/aliases/water_dimer_density.cub` 是 S06 的逐字节副本，摘要同 S06；`outputs/v1-acceptance/aliases/water_neutral_nbo_opt_freq.log` 是 S08 的逐字节副本，摘要同 S08。缺失时在仓库根目录 PowerShell 执行：

```powershell
New-Item -ItemType Directory -Force outputs/v1-acceptance/aliases | Out-Null
Copy-Item outputs/complex-examples/sources/chemtools-h2o_dimer_pbe_sto3g.fchk outputs/v1-acceptance/aliases/water_dimer.fch
Copy-Item outputs/complex-examples/sources/chemtools-h2o_dimer_pbe_sto3g-dens.cube outputs/v1-acceptance/aliases/water_dimer_density.cub
Copy-Item outputs/log-examples/water_neutral_nbo_opt_freq.out outputs/v1-acceptance/aliases/water_neutral_nbo_opt_freq.log
```

S09–S11 如在本机缺失，可从固定提交重新取得；在仓库根目录 PowerShell 执行后，逐个核对上表摘要：

```powershell
$igmhDir = 'outputs/v1-acceptance/sources/igmh-phenol'
$igmhRevision = '69a219f6474eae20886726c2270806e27de98e77'
New-Item -ItemType Directory -Force $igmhDir | Out-Null
foreach ($name in @('phenol_di-dg_inter.cub', 'phenol_di-dg_intra.cub', 'phenol_di-sl2r.cub')) {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/aligfellow/xyzrender/$igmhRevision/examples/structures/$name" -OutFile "$igmhDir/$name"
    Get-FileHash "$igmhDir/$name" -Algorithm SHA256
}
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/aligfellow/xyzrender/$igmhRevision/LICENSE" -OutFile "$igmhDir/LICENSE"
```

## 尚缺的真实分析结果

下列项目**没有完整的**可供本轮科学验收的真实结果集。检索过 MolStudio 子模块、IGMH_Toolbox 源码与公开资料；方法说明、文件名示例、构造格式样本及本仓库生成的 RDG 均不能替代该分析的原始输出。S09–S11 是真实 Multiwfn Cube，已用当前 Cube 解析器确认 26 原子、相同原子顺序/坐标与 92×75×77 网格；[上游示例文档](https://xyzrender.readthedocs.io/en/latest/examples/nci_surf.html)将其用于 IGMH 画面，但没有给出原始波函数、片段划分、版本和单位证据。它们可做真实场的导入预检，**不能单独完成科学签署**。取得新样本后，在此表增补直接 URL、不可变版本、许可、每个文件的 SHA-256、程序版本、方法/基组、构型、片段或表面定义以及输出单位，再按 [SOP](SOP.md) 操作。没有这些材料时维持 `Not Run`。

| 功能 | 需要成套取得的真实输出 | 当前状态 |
| --- | --- | --- |
| IGMH 与 IRI | IGMH 有 S09–S11 真场，但缺原始波函数/理论级别、片段、程序版本及单位证据；IRI 仍缺几何场 + 同网格着色 Cube | Not Run |
| ESP 表面 | 同一参考构型的 `surfanalysis.pdb` 类极值文件 + 面积分布文本；记录等密度面定义和两种单位 | Not Run |
| AIM | 同一参考构型的 `CPs.pdb` + `paths.pdb`，如有则加 `CPprop.txt` | Not Run |
| IRC | 同一路径每步完整 FCHK + `step,fchk` 清单；逐步能量必须来自对应 FCHK | Not Run |
| Mayer | 与已验收 IRC 每步对应的真实 Mayer 输出 + `step,mayer_output` 清单 | Not Run |
| ETS-NOCV | 含 pair、自旋、轨道号、成对能量的原始分析输出及对应参考构型 | Not Run |
| NOCV 场 | 与已验收 ETS 行明确对应的带符号 pair Cube | Not Run |

S08 的许可未核清前，验收可在本地使用；不得把该数据文件加入发布包或公开案例附件。`S01–S07` 的仓库许可与文件来源是可审查线索，公开再分发仍须按各许可处理。检索线索：[IGMH_Toolbox 源码](https://github.com/houcheng-gxnu/IGMH_Toolbox)、[Multiwfn 手册中的 ESP 文件定义](https://mgcf.cchem.berkeley.edu/mgcf/Multiwfn_3.8_dev.pdf)。
