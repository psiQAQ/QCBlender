# 公开教程样本版本

当前入口由 [交付索引](../acceptance/tutorial-sample-delivery.json) 选择：v4 包为 Gaussian-v2，270 个输入，P04 原生 53 帧（TS27），P06 取 1/27/53 帧。旧 v3 包与 Gaussian-v1 的 69 帧保持原字节，使用 `--dataset gaussian-v1` 显式恢复。下文为更早 v2 的冻结身份。

`qcblender-public-tutorial-samples-v2.zip` 为既有本地交付包的原始字节，未重新生成或压缩。来源及逐文件记录见 `validation/agent/v1-acceptance/tutorial-samples.json` 和 `validation/agent/acceptance/tutorial-sample-delivery.json`。

文件大小为 12,175,753 字节，SHA-256 为 `b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`。包内保留 LICENSE、NOTICE.md 和来源清单；30 个 included 文件覆盖 P01/P03/P04/P05/P06，采用 CC BY 4.0、署名 QCBlender contributors。P02 的再分发许可未确认，包内没有 P02 文件。

CI 在使用前核对整个 ZIP、清单及每个成员的摘要、许可声明和精确成员集合。该检查证明材料身份与记录一致，不代替组件许可复核或独立科研签署。
