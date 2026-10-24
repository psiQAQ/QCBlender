# 当前 Gaussian 教程样本

Gaussian-v2 是 SOP 的当前数据版本，随 `qcblender-public-tutorial-samples-v4.zip` 分发。全部 270 个输入及许可、SHA-256、真实预期见 [tutorial-samples.json](tutorial-samples.json)。

- P04 使用 Gaussian 16 C.01 原生 GS2 分段续算的 **53 帧**，**TS 位于第 27 帧**。导入 [P04/steps.csv](P04/steps.csv) 和 [P04/mayer.csv](P04/mayer.csv)，并保留全部相对引用。
- P06 的 [三帧 XYZ](P06/p04-three-frames.xyz) 对应 P04 的 **1 / 27 / 53** 帧；[source.json](P06/source.json) 保存精确来源与 SHA-256。
- P01、P02、P03、P05 及 P06 水二聚体坐标复用 Gaussian-v1 的原字节，方法、基组、5D、积分网格和 NOCV KS 能量近似均保持原科学身份。

路径顺序为负二面角端点 → TS → 正二面角端点。Gaussian 的 `Forward` 对应本例负端，`Reverse` 对应正端。每个新接受点均由 Gaussian 积分得到，后续段用 `Downhill` 继续；共 52 个新接受点和一个 TS，边界不重复计数，没有端点优化补帧。逐段输入和日志在 [P04/segments/](P04/segments/)，反应坐标、步长和父步映射在 [P04/energies.csv](P04/energies.csv)。

常规单作业在平坦峰顶附近的早停仍保留为失败诊断；本路径的身份是“Gaussian 原生积分分段续算”，不标为一次单作业完成。原始补充数据及诊断身份见 [gaussian-native-irc-v1](../gaussian-native-irc-v1/README.md)；其 README 和检查状态是初次发布时的历史快照。当前 Blender 证据由[工程索引](../../../../工程索引.md)定位。

旧 Gaussian-v1 的 69 帧、v3 包及旧工程保留，恢复时显式选 `--dataset gaussian-v1`。不要把旧第 35 帧 TS 或旧 GUI 记录用于当前第 27 帧。数据采用 [CC BY 4.0](../LICENSE)，署名 QCBlender contributors；独立人工及科研签署按实际状态记录。
