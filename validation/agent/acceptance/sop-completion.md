# SOP 实操与完整材料交付（2026-10-21）

后续可用性（2026-10-22）：本页保留原批次身份和结果。当前材料统一在 `validation/`，其中两个检查点采用后续重建版本；旧包、展开副本及自动备份已按授权清理，收据见[迁移与清理](delivery-consolidation.md)。

79 个编号步骤及章节内演示、27 张教程图已完成；36 个最终工程和检查点原位及中文路径解包新进程比较 Passed。最终教程 ZIP 含 1,755 个文件，296,605,483 字节，SHA-256 `a567d578cf0bfb4940bc2a02b140e8d4af61016440571a84e7b81cbdfa414a9c`。P01 已恢复，原生基线比较 Passed、差异为空，CU 观察相位与相机取景正常。

| 范围 | 结果与证据 |
| --- | --- |
| 主线与九专题 | Passed；[79 步与 27 图索引](../reports/2026-10-21/sop-completion/step-image-index.json)，MCP 执行、CU 点击和观察分别记录 |
| 最终候选 | Passed；完整构建、隔离和日常安装，123 个安装成员匹配；[候选身份](../current-install.json)、[选择记录](../reports/2026-10-21/sop-completion/final-candidate/selection.json) |
| 原位工程 | Passed；[36 份工程清单](../reports/2026-10-21/sop-completion/final-projects/delivery-project-manifest.md) |
| 解包可迁移性 | Passed；全部 36 份中文路径工程分别由新 Blender 进程读取，科学数组、资源与持久显示状态零差异；[汇总](../reports/2026-10-21/sop-completion/unpacked-projects/summary.json) |
| 图片、链接、公开材料 | Passed；[文档检查](../reports/2026-10-21/sop-completion/final-docs.json)及[包清单](../reports/2026-10-21/sop-completion/package-manifest.json) |
| P01 恢复 | Passed；[只读比较](../reports/2026-10-21/sop-completion/projects/P01-final-restored.json)，PID 1308；CU 观察主窗口可用，未改写工程 |
| 独立用户与科研验收 | Not Run；Agent 实操与数值检查不代签 |
| 完整发布资格、许可审查、远端 CI | Not Run；本批为本地教程交付，不 push 或公开发布 |

本批修复冷重开时生成节点树碰撞后缀重新编号，源码 `1f7d537`，15 项定向测试 Passed。检查工具另修复 Windows 长路径、Blender 5.1 状态等价表示与 RNA 正负 Infinity，保留科学数组非有限值失败；相关定向结果及旧失败报告均保留。新候选 SHA-256 为 `06b46875482a4ee377180717551457f9b74019f01c6c3f3221754119f75ff052`，50,941,014 字节。

P01 轨道检查点和 P06 标注检查点缺少有效的原保存前完整快照：两次冷读严格比较、原始执行记录与科学数据独立核对已通过，但不声称补回缺失快照。节点外部库的 Pack 操作失败，原错误保留；实际改为三组节点“转为本地项”，几何和科学数据不变，保存及解包冷读通过。较早步骤绑定旧候选 `8c23eaff…`，本批记录保留各自身份；最终所有工程的解包比较绑定新候选。

材料在主仓库 `outputs/deliveries/sop-20261021/QCBlender-tutorial.zip`，同级目录提供 README、工程索引和完整展开内容。31 个自动 `.blend1` 备份只排除出 ZIP，仍留原位。既有用户工程、旧安装/偏好备份及历史报告未删除。执行脚本和工作树忽略产物按收尾清单保全；本地整合与归档收据见主仓库 `outputs/runs/sop-20261021/finish/`。

收尾评审修正当前截图/工程路由，并使统一操作查询支持登记关键词、展示本批复验条目，历史 GUI 状态仍独立。查询回归先复现 `Make Local` 无匹配，修复后 4 项测试 Passed；[实际结果](../reports/2026-10-21/sop-completion/query-alias-final/checks-tests.json)。产品源码及候选未因该工具变更改变。

本地任务提交 `0ed0fea` 已快进合入 main；[主检出材料检查](../reports/2026-10-21/sop-completion/main-docs.json)与[当前安装同步](../reports/2026-10-21/sop-completion/final-candidate/main-sync.json) Passed。[Standards](../reports/2026-10-21/sop-completion/final-standards-review.md) 首次两项发现修复后无剩余，[Spec](../reports/2026-10-21/sop-completion/final-spec-review.md) 无发现。三个本批工作树共 202 个忽略文件已保全、核验后正常移除，分支以 `git branch -d` 删除；注释标签为 `archive/2026-10-21/task/{sop-completion-20261021,sop-docs-20261021,sop-project-check-20261021}`。逐文件清单与归档 ZIP 位于 `outputs/runs/sop-20261021/finish/<工作树名>/`。所有工程及当前候选留在主仓库稳定位置。

后续补验：两个检查点已从原始输入重新生成并建立真实保存前完整快照；新交付物及全部比较结果见[检查点重建](checkpoint-rebuild.md)。本页原批次缺口描述仍对应旧工程，未改写旧报告。
