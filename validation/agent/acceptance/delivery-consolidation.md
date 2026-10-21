# 教程材料迁入 validation 与交付副本清理（2026-10-22）

按用户要求，将 `checkpoint-rebuild-20261021` 最新版对应材料合并到主仓库 `validation/`，随后清理 `outputs/deliveries/`。入口为[工程索引](../../工程索引.md)和[人工 SOP](../../human/SOP.md)。保留主仓库 README 的导航，合并分发说明；不把 Agent 报告、本地限定输入和回归数据覆盖成分发材料。

| 范围 | 结果 |
| --- | --- |
| 迁移文件 | Passed；91 个相同文件复用、3 个旧 P01 文件覆盖、1,660 个文件补入，另合并 README；1,754 个原字节成员逐项核对 |
| 迁移后工程 | Passed；36 个独立新进程冷重开，按清单指定完整快照严格比较，全部零差异，工程文件未改写 |
| 材料和导航 | Passed；公开输入、安装包、27 张图片和教程检查通过，工程索引及新增入口共 326 个链接/锚点核对通过 |
| 候选身份 | Passed；每个冷读进程核对现有安装全部 123 个成员，安装包与插件源码未变 |
| 既有非对应材料 | Passed；原 `validation/work/human/` 的 23 个额外文件保留；Agent、本地输入、回归数据不在覆盖范围 |
| deliveries 清理 | Not Run；7,055 个文件、2,129,569,652 字节已生成逐文件清单，待最终迁移门禁后执行 |
| 原 P01 窗口恢复 | Not Run；用户已保存关闭，完成清理后打开迁入 `validation/work/human/P01/P01.blend` 的同内容工程 |
| 独立人工/科研验收 | Not Run；本批为材料迁移、真实 CLI 冷读及存储维护 |

原 P01 文件摘要 `e423db84bada5e95385ff71909a20d3b285142c9e932070ef684d421fb2a1294` 与新版交付一致，迁移后仍相同。P01 轨道、P06 标注使用重建批次的真实保存前完整快照，其余 34 个工程使用既有清单明确指定的有效基线；本批重新执行新位置冷读，不把历史执行改记为本批执行。

清理仅覆盖 `outputs/deliveries/`：6,970 个展开文件在 `validation/` 有相同字节对应物，4 份分发 README 合并导航，4 个 ZIP/摘要文件退役，46 个旧检查点文件由重建版替代，31 个旧批次 `.blend1` 自动备份由当前对应工程替代。删除前后均核对迁移成员与候选身份；按清单逐文件删除，任何权限失败原位记录，不修改 ACL。历史报告、清单和归档标签保留，旧 ZIP 摘要只表示原批次身份。

证据：[迁移清单](../reports/2026-10-22/delivery-consolidation/migration-plan.json)、[迁移结果](../reports/2026-10-22/delivery-consolidation/migration-applied.json)、[36 工程冷读](../reports/2026-10-22/delivery-consolidation/cold-summary.json)、[逐文件退役清单](../reports/2026-10-22/delivery-consolidation/cleanup-plan.jsonl.gz)、[清理计划摘要](../reports/2026-10-22/delivery-consolidation/cleanup-plan-summary.json)。编排脚本在主仓库 `outputs/runs/delivery-consolidation-20261022/`。

此后不另存完整教程 ZIP；本地交付需要打包时，从 `validation/` 按[材料打包说明](../../README.md#人工完成后的打包)选择教程、安装包、公开输入、工程索引和对应工程，保持相对目录。包的 ZIP 字节及 README 可能与旧包不同，新包须有自己的材料与解包验证记录。

[Standards](../reports/2026-10-22/delivery-consolidation/standards-review.md) 与 [Spec](../reports/2026-10-22/delivery-consolidation/spec-review.md) 审阅均零发现；清理执行前须将工程索引合入主仓库，再核对全部保留成员。历史分发路径不再作为当前入口，原报告仍保留其实际执行身份。
