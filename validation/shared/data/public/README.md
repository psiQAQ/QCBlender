# 公开案例输入

当前教程使用 `gaussian-v2/` 中的 Gaussian 自有计算数据；各组文件及相对引用应一起保留。

| 案例 | 当前输入路径 | 用途 |
| --- | --- | --- |
| P01 | [gaussian-v2/P01/o2-uhf.fchk](gaussian-v2/P01/o2-uhf.fchk) | 优化氧分子的轨道和自旋密度 |
| P02 | [gaussian-v2/P02/water_neutral_nbo_opt_freq.out](gaussian-v2/P02/water_neutral_nbo_opt_freq.out) | 自有水分子的优化、频率、NBO |
| P03 | [gaussian-v2/P03/water-dimer.fchk](gaussian-v2/P03/water-dimer.fchk) | 优化水二聚体及 IGMH/IRI、ESP、AIM 外部结果 |
| P04 | [gaussian-v2/P04/steps.csv](gaussian-v2/P04/steps.csv)、[gaussian-v2/P04/mayer.csv](gaussian-v2/P04/mayer.csv) | 原生 GS2 双向 53 帧（TS27）与逐点 Mayer 键级 |
| P05 | [gaussian-v2/P05/complex.fchk](gaussian-v2/P05/complex.fchk) | 优化 CO–BH3 及冻结片段 NOCV 分析 |
| P06 | [gaussian-v2/P06/source.json](gaussian-v2/P06/source.json) | 新 P03 单帧、新 P04 首/TS/末三帧 XYZ |

所有当前样本的身份、实际数值和计算条件见 [当前清单](gaussian-v2/tutorial-samples.json)。数据按 [LICENSE](LICENSE) 使用 CC BY 4.0，署名 QCBlender contributors。科学适用范围、软件引用及 NOCV 能量近似见 [NOTICE.md](NOTICE.md)。

当前版本从原生 GS2 补充数据复制 P04 原字节；P06 三帧取自第 1/27/53 帧。P01/P02/P03/P05 和水二聚体 XYZ 保持上个版本的科学身份。旧 `gaussian-v1/` 的 69 帧和 v3 包、`gaussian-native-irc-v1/` 的补充原件均保留；它们是独立历史/来源材料，当前独立分发材料只含活动版本。

根目录旧 P01–P06 及根 `tutorial-samples.json` 保留为 legacy-v2 历史输入；旧验证结论不代表当前 Gaussian 数据已通过界面或独立科研验收。
