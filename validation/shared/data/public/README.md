# 公开案例输入

当前教程使用 `gaussian-v1/` 中的 Gaussian 自有计算数据；各组文件及相对引用应一起保留。

| 案例 | 当前输入路径 | 用途 |
| --- | --- | --- |
| P01 | [gaussian-v1/P01/o2-uhf.fchk](gaussian-v1/P01/o2-uhf.fchk) | 优化氧分子的轨道和自旋密度 |
| P02 | [gaussian-v1/P02/water_neutral_nbo_opt_freq.out](gaussian-v1/P02/water_neutral_nbo_opt_freq.out) | 自有水分子的优化、频率、NBO |
| P03 | [gaussian-v1/P03/water-dimer.fchk](gaussian-v1/P03/water-dimer.fchk) | 优化水二聚体及 IGMH/IRI、ESP、AIM 外部结果 |
| P04 | [gaussian-v1/P04/steps.csv](gaussian-v1/P04/steps.csv)、[gaussian-v1/P04/mayer.csv](gaussian-v1/P04/mayer.csv) | 完整双向 IRC 和逐点 Mayer 键级 |
| P05 | [gaussian-v1/P05/complex.fchk](gaussian-v1/P05/complex.fchk) | 优化 CO–BH3 及冻结片段 NOCV 分析 |
| P06 | [gaussian-v1/P06/source.json](gaussian-v1/P06/source.json) | 新 P03 单帧、新 P04 首/TS/末三帧 XYZ |

所有当前样本的身份、实际数值和计算条件见 [当前清单](gaussian-v1/tutorial-samples.json)。数据按 [LICENSE](LICENSE) 使用 CC BY 4.0，署名 QCBlender contributors。科学适用范围、软件引用及 NOCV 能量近似见 [NOTICE.md](NOTICE.md)。

另有 [Gaussian 原生 GS2 分段续算补充数据](gaussian-native-irc-v1/README.md)：53 帧双向路径、全部原生接受点的 FCHK、逐段输入/日志及 Mayer 清单。它具有独立清单，默认教程的 Gaussian-v1、v3 包和历史输入保持原身份。

根目录旧 P01–P06 及根 `tutorial-samples.json` 保留为 legacy-v2 历史输入；旧验证结论不代表当前 Gaussian 数据已通过界面或独立科研验收。
