# SOP 安装包与样本

本页列出可用于 [SOP](SOP.md) 的材料身份。2026-10-06 已核对下列本机文件的大小和 SHA-256。开始新批次时仍需核对实际取得的文件；使用提供者更新的安装包时，填写其清单及实际摘要。

## 扩展安装包

适用 Windows x64 / Blender 5.1.1，QCBlender 0.1.0。

- 仓库相对路径：`outputs/candidates/current/alpha-ci-0.1.0-f8b1115/qcblender-0.1.0.zip`。
- 大小：50,656,040 字节。
- SHA-256：`6f25cbaf2df9a41137bfef74abbb7c3b365905370bd70bc77327a9cabeb0dfd8`。
- 源码提交：`f8b111549e34b7ad995139d09042ca912661d352`。
- 同目录的 `release-manifest.json`、`SHA256SUMS.txt` 记录材料身份。

安装包与保留工程的查找入口为 [ARTIFACTS](../ARTIFACTS.md)。取得他人提供的 ZIP 时，向提供者一并取得身份清单；源码 ZIP 不能直接作为 Blender 扩展安装。

## 公开教程样本

- 仓库相对路径：`tests/data/distribution/qcblender-public-tutorial-samples-v2.zip`；上述候选目录也包含相同样本包。
- 大小：12,175,753 字节。
- SHA-256：`b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`。
- 包含 P01、P03、P04、P05、P06；保留解压后的 `LICENSE`、`NOTICE` 和 `tutorial-samples.json`。数据使用 CC BY 4.0，署名 QCBlender contributors。
- 每个文件的身份和计算条件见[样本清单](tutorial-samples.json)；来源与取得方式见 [SOURCES](SOURCES.md#公开教程样本与独立获取2026-09-30)。

| 目录 | 内容 | 使用章节 |
| --- | --- | --- |
| P01 | 开壳层 O₂ FCHK | A02–A09、C01 |
| P03 | 水二聚体 FCHK、Cube、IGMH/IRI、ESP、AIM 输出 | C03–C05、C07–C09 |
| P04 | 三步 IRC 波函数、steps.csv、Mayer 输出 | P1-A/P1-B、C10/C11 |
| P05 | 复合物波函数、ETS-NOCV 表和 pair Cube | C12/C13 |
| P06 | 单帧水二聚体、多帧 XYZ | 入门流程、X01 |

## P02 优化与频率日志

P02 未包含在公开样本包中。其独立再分发许可未确认，保留为本地使用输入，不加入公开附件。已有原件可直接复制；需要取得原件时，按 [SOURCES](SOURCES.md#公开教程样本与独立获取2026-09-30) 的固定来源与使用条件办理。

- 本机路径：`tests/data/local/log-examples/water_neutral_nbo_opt_freq.out`。
- 输入身份：Gaussian 16 A.03 / NBO 3.1，水优化与频率日志。
- 大小：92,872 字节。
- SHA-256：`9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519`。
- 将 `.out` 复制为同名 `.log` 后，两份摘要应相同。操作见 [SOP 0.1.1](SOP.md#011-单独取得-p02c02c06-前置条件)。

读取这些现成结果无需安装 Gaussian、Multiwfn 或 PySCF。
