# 两个检查点的保存前验证补齐（2026-10-21）

后续可用性（2026-10-22）：本页保留原 ZIP 身份和当时验证结果。全部最新版材料已迁入 `validation/`，工程从[工程索引](../../工程索引.md)进入；原分发包和重复副本已按授权清理，收据见[迁移与清理](delivery-consolidation.md)。

P01 轨道与 P06 标注检查点已从原始 FCHK/XYZ 重新生成。真实保存前完整快照、保存后同进程比较、新进程冷重开及中文路径解包冷重开均 Passed、差异为空。旧包与旧报告保留原身份；新包中这两个检查点已不再具有“缺少保存前快照”的限制。

| 范围 | 结果 |
| --- | --- |
| P01 重新计算 | Passed；全新 worker 作业根，cache_hit=False，Alpha 源 MO9，间距 0.2 Å、外扩 3 Å、512 MB、31×31×37；所有科学数组与旧有效参考逐项一致 |
| P06 重新生成 | Passed；原始 XYZ，四类标注、来源编号、显示参数、材质和相机；0° 隐藏圆弧的三个 -Infinity 标记完整保留 |
| 保存前状态 | Passed；真实 save_pre 观察器回调，完整快照成功；回调时磁盘 .blend 摘要仍等于空白种子，且没有加载旧检查点 |
| 保存及冷读 | Passed；两例均保存前→保存后→新进程→中文路径解包严格比较，所有差异列表为空 |
| 完整教程包 | Passed；1,755 文件、27 图、36 工程；仅两个检查点及包 README 改动，其余 34 工程和全部配套资源逐字节不变，复用原有效验证 |
| 独立人工/科研验收 | Not Run；本批为 Agent 使用真实 Blender CLI 的生成与持久化验证，未重复 UI 点击 |

完整材料：`outputs/deliveries/checkpoint-rebuild-20261021/QCBlender-tutorial.zip`，296,596,161 字节，SHA-256 `f885589e4e6237cd3ca4dddc6de12ea57a976f9e973fd685556067cdb524f4fb`。展开目录保持原教程结构及工程索引。

保存协议先建立没有科学对象的空白种子工程，固定真实目标路径；随后从原始输入生成案例。调用真实 Save Portable QC Project，插件完成科学侧车复制、核验和路径重绑后，在 Blender 写入场景前由 save_pre 记录完整持久状态。另对调用保存前后的科学数组、对象与节点状态严格比较，确认侧车准备未改变生成结果。快照包括对象、节点、材质、相机、绑定、数组摘要与外部资源；临时选择、窗口尺寸等不作为持久化保证。

P01 生成/冷读/解包进程分别为 9624/16652/32156；P06 为 46648/32336/87080。P06 首次重建脚本假设刚导入对象已有局部选择属性而失败；已按真实教程执行 REPLACE→CLEAR 初始化后重新生成，失败日志及种子原位保留，未跳过检查或手工伪造属性。插件源码与安装候选未变，仍为 `06b46875…`。

证据：[完整工程清单](../reports/2026-10-21/checkpoint-rebuild/delivery-project-manifest.json)、[包清单](../reports/2026-10-21/checkpoint-rebuild/package-manifest.json)、[P01 保存时序](../reports/2026-10-21/checkpoint-rebuild/p01-r1/generation-and-save.json)、[P06 保存时序](../reports/2026-10-21/checkpoint-rebuild/p06-r2/generation-and-save.json)。本批开始前的 P01 原工程已恢复到 PID 15760，未改写，原基线比较[Passed](../reports/2026-10-21/checkpoint-rebuild/restored-P01.json)。

[Standards 审阅](../reports/2026-10-21/checkpoint-rebuild/standards-review.md)首次一项路由建议已修复并复核关闭；[Spec 审阅](../reports/2026-10-21/checkpoint-rebuild/spec-review.md)零发现。实际验证、原工程恢复及材料核对均已完成。

本地提交 `4959619` 已以 ff-only 合入 main。三个本批工作树的 6 个忽略文件已逐项保全、摘要核验后正常移除，任务分支正常删除；注释标签为 `archive/2026-10-21/task/{checkpoint-rebuild-20261021,checkpoint-p01-20261021,checkpoint-p06-20261021}`。逐文件清单、归档 ZIP 和收据位于 `outputs/runs/checkpoint-rebuild-20261021/finish/<工作树名>/`。当前工程、教程 ZIP 及验证证据均保留在主仓库稳定目录，未 push 或发布。
