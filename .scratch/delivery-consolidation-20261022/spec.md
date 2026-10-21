# 将教程交付合并到 validation 并清理 deliveries

Triage: ready-for-agent
Status: resolved
Baseline: 290a452e5d69e5a32ca30cd0b42ddd57a7117765

用户要求：清理旧版，将新版对应内容覆盖迁入 validation，然后清理 outputs/deliveries。已确认当前 Blender 保存并关闭。

先逐文件核对新版清单与现有 validation；人工教程、资源、工程与索引合并到对应路径，保留 validation/agent、本地输入和回归输入等非交付内容。README 合并当前入口说明，不用分发 README 覆盖仓库导航。旧版原 P01 如出现用户保存的新状态必须保全并验证，不丢失用户内容。

迁移校验原字节、配套资源、文档链接，并串行在新进程核对迁移后的工程。删除前清单记录路径、用途、摘要、保留映射及删除理由；只清理用户指定 deliveries 边界内已核对文件，不修改 ACL、不强制删除未知/占用对象。保存迁移与删除收据，更新当前产物入口及历史可用性，不改写历史执行结果。结束打开 validation 下对应 P01 工程。

遵循本地提交、ff-only 整合与保全归档流程；不 push，不修改插件、安装或依赖。独立人工/科研验收不由本次迁移代替。

## Answer

最新版对应材料已合并到 validation，工程索引和导航已入库。36 个工程迁移后实际新进程冷读全 Passed、零差异；旧 P01 在新位置通过真实 MCP 恢复核对并保留窗口。deliveries 按清单删除 7,055 文件、2,129,569,652 字节，目录已移除，无删除失败；迁移目标再次核对通过，既有非对应材料保留。

详细验收：`validation/agent/acceptance/delivery-consolidation.md`；逐文件映射、冷读和删除收据：`validation/agent/reports/2026-10-22/delivery-consolidation/`。Standards / Spec 均零发现，独立人工/科研验收 Not Run。不 push 或发布。本地归档收据已保存在本批 finish 目录。

本地提交 `3a1fbc7` 已快进合入 main；任务工作树已正常移除、分支正常删除，3 个生成缓存文件经摘要核验保全。注释归档标签为 `archive/2026-10-22/task/delivery-consolidation-20261022`，清单、归档 ZIP 和收据位于 `outputs/runs/delivery-consolidation-20261022/finish/`。当前工程与证据均保留于主仓库，未 push 或发布。
