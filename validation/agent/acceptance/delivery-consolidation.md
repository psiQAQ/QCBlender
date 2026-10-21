# 教程材料迁入 validation 与交付副本清理（2026-10-22）

按用户要求，将 `checkpoint-rebuild-20261021` 最新版对应材料合并到主仓库 `validation/`，随后清理 `outputs/deliveries/`。入口为[工程索引](../../工程索引.md)和[人工 SOP](../../human/SOP.md)。保留主仓库 README 的导航，合并分发说明；不把 Agent 报告、本地限定输入和回归数据覆盖成分发材料。

| 范围 | 结果 |
| --- | --- |
| 迁移文件 | Passed；91 个相同文件复用、3 个旧 P01 文件覆盖、1,660 个文件补入，另合并 README；1,753 个成员保持原字节，工程索引仅按仓库约定规范为 LF 换行 |
| 迁移后工程 | Passed；36 个独立新进程冷重开，按清单指定完整快照严格比较，全部零差异，工程文件未改写 |
| 材料和导航 | Passed；公开输入、安装包、27 张图片和教程检查通过，工程索引及新增入口的链接/锚点核对通过 |
| 候选身份 | Passed；每个冷读进程核对现有安装全部 123 个成员，安装包与插件源码未变 |
| 既有非对应材料 | Passed；原 `validation/work/human/` 的 23 个额外文件保留；Agent、本地输入、回归数据不在覆盖范围 |
| deliveries 清理 | Passed；逐文件删除 7,055 个文件、2,129,569,652 字节，112 项保护摘要通过；无失败或残留，空目录逐层移除，deliveries 已不存在 |
| 原 P01 窗口恢复 | Passed；真实 HTTP MCP 核对 PID 79644、validation 下工程路径、未保存状态为 false，完整基线比较零差异；窗口保留 |
| 独立人工/科研验收 | Not Run；本批为材料迁移、真实 CLI 冷读及存储维护 |

原 P01 文件摘要 `e423db84bada5e95385ff71909a20d3b285142c9e932070ef684d421fb2a1294` 与新版交付一致，迁移后仍相同。P01 轨道、P06 标注使用重建批次的真实保存前完整快照，其余 34 个工程使用既有清单明确指定的有效基线；本批重新执行新位置冷读，不把历史执行改记为本批执行。

清理仅覆盖 `outputs/deliveries/`：6,966 个展开文件在 `validation/` 有相同字节对应物，4 份工程索引内容相同且统一为 LF 换行，4 份分发 README 合并导航，4 个 ZIP/摘要文件退役，46 个旧检查点文件由重建版替代，31 个旧批次 `.blend1` 自动备份由当前对应工程替代。删除前后均核对迁移成员与候选身份；按清单逐文件删除，任何权限失败原位记录，不修改 ACL。历史报告、清单和归档标签保留，旧 ZIP 摘要只表示原批次身份。

证据：[迁移清单](../reports/2026-10-22/delivery-consolidation/migration-plan.json)、[迁移结果](../reports/2026-10-22/delivery-consolidation/migration-applied.json)、[36 工程冷读](../reports/2026-10-22/delivery-consolidation/cold-summary.json)、[逐文件退役清单](../reports/2026-10-22/delivery-consolidation/cleanup-plan-v2.jsonl.gz)、[清理计划摘要](../reports/2026-10-22/delivery-consolidation/cleanup-plan-summary-v2.json)。编排脚本在主仓库 `outputs/runs/delivery-consolidation-20261022/`。

此后不另存完整教程 ZIP；本地交付需要打包时，从 `validation/` 按[材料打包说明](../../README.md#人工完成后的打包)选择教程、安装包、公开输入、工程索引和对应工程，保持相对目录。包的 ZIP 字节及 README 可能与旧包不同，新包须有自己的材料与解包验证记录。

[Standards](../reports/2026-10-22/delivery-consolidation/standards-review.md) 与 [Spec](../reports/2026-10-22/delivery-consolidation/spec-review.md) 审阅均零发现；清理前已将工程索引合入主仓库，并通过全部保留成员门禁；清理后再次核对通过。历史分发路径不再作为当前入口，原报告仍保留其实际执行身份。

工程索引的 CRLF→LF 由仓库 `.gitattributes` 的 Markdown 规则决定，正文、链接及顺序不变；[变换记录](../reports/2026-10-22/delivery-consolidation/index-normalization.json)保留源/目标摘要。原迁移收据对应入库前原字节副本，后续门禁使用该明确变换后的摘要；工程和科学数据未做文本转换。

实际清理：[删除前门禁](../reports/2026-10-22/delivery-consolidation/cleanup-preflight.json)、[逐文件删除收据](../reports/2026-10-22/delivery-consolidation/prune-01/removed.jsonl.gz)、[工具执行收据](../reports/2026-10-22/delivery-consolidation/prune-01/applied.json)、[清理后复核](../reports/2026-10-22/delivery-consolidation/cleanup-finished.json)。逻辑删除量 2,129,569,652 字节，卷可用空间观测增加 2,133,880,832 字节；后者包含同时发生的系统活动，不视为精确净节省量。全 outputs 盘点遇到 36 个范围外不可访问项，均未进入本批删除集合；deliveries 内完整枚举且删除无失败。

当前工程清单见[current-project-manifest.json](../reports/2026-10-22/delivery-consolidation/current-project-manifest.json)，原 P01 的[恢复报告](../reports/2026-10-22/delivery-consolidation/restored-P01.json)与[会话状态](../reports/2026-10-22/delivery-consolidation/restored-state.json)保留。旧报告中 deliveries 路径及旧 ZIP 已退役，依此迁移映射查找当前材料；历史执行结果和源文件身份不改写。

本地提交 `3a1fbc7` 已快进合入 main；任务工作树已正常移除、分支正常删除，3 个生成缓存文件经摘要核验保全。注释归档标签为 `archive/2026-10-22/task/delivery-consolidation-20261022`，清单、归档 ZIP 和收据位于 `outputs/runs/delivery-consolidation-20261022/finish/`。当前工程与证据均保留于主仓库，未 push 或发布。
