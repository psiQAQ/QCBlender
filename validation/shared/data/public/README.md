# 公开案例输入

本目录随人工教程一起保存。各子目录的文件保持原名和相对位置；尤其是 P04 的 CSV 与 FCHK、Mayer 表应一起保留。

| 案例 | 输入路径（相对本目录） | 用途与来源 |
| --- | --- | --- |
| P01 | `P01/o2-uhf.fchk`、`P01/o2-uhf.fch` | PySCF 生成的氧分子波函数；轨道与自旋密度 |
| P03 | `P03/water-dimer.fchk`、`P03/water-dimer.fch` | PySCF 生成的水二聚体；密度、静电势和分子显示 |
| P03 Cube | `P03/color.cube`、`P03/igmh/dg_inter.cub`、`P03/igmh/sl2r.cub`、`P03/iri/func2.cub`、`P03/iri/func1.cub` | Multiwfn 生成的空间场；Cube、IGMH 和 IRI 显示 |
| P03 ESP | `P03/esp/surfanalysis.pdb`、`P03/esp/stdout.log` | Multiwfn 静电势表面极值和面积分布 |
| P03 AIM | `P03/aim/CPs.pdb`、`P03/aim/paths.pdb`、`P03/aim/CPprop.txt` | Multiwfn 临界点、路径和属性 |
| P04 | `P04/steps.csv`、`P04/step-001.fchk`、`P04/step-002.fchk`、`P04/step-003.fchk` | PySCF/geomeTRIC 生成的三步 IRC 路径 |
| P04 Mayer | `P04/mayer-pyscf.csv`、`P04/step-001-mayer-pyscf.txt`、`P04/step-002-mayer-pyscf.txt`、`P04/step-003-mayer-pyscf.txt` | 各步构型的 Mayer 键级 |
| P05 | `P05/complex.fchk`、`P05/co.fchk`、`P05/bh3.fchk`、`P05/nocv/ets-nocv.txt`、`P05/nocv/nocv-pair1.cub` | CO–BH3 示例的 ETS-NOCV 分析记录与空间分布 |
| P06 | `P06/water-dimer.xyz`、`P06/p04-three-frames.xyz`、`P06/source.json` | 从 P03/P04 构型提取的单帧与三帧 XYZ；坐标单位 Å |

> FCHK 是包含分子构型和波函数数据的格式化检查点文件。

> Cube 是保存三维网格数值的文本文件。

> IRC 是沿反应路径排列的一组构型；本案例保留三个代表步骤。

这 30 个输入按 [LICENSE](LICENSE) 使用 CC BY 4.0，署名 QCBlender contributors；计算来源、软件引用和科学适用范围见 [NOTICE.md](NOTICE.md)。P01/P03/P05 使用说明性的未优化构型；P04 来源于已收敛的双向 IRC。NOCV 能量重建是指定近似，不包含网格收敛结论。

[tutorial-samples.json](tutorial-samples.json) 保留原始来源与计算条件；其中 `archive_path` 对应本目录内的文件位置，其他来源路径为生成时的记录。P06 的来源构型可直接在本目录的 `P03/` 和 `P04/` 找到。
