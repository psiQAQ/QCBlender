# 将教程交付合并到 validation 并清理 deliveries

Triage: ready-for-agent
Status: claimed
Baseline: 290a452e5d69e5a32ca30cd0b42ddd57a7117765

用户要求：清理旧版，将新版对应内容覆盖迁入 validation，然后清理 outputs/deliveries。已确认当前 Blender 保存并关闭。

先逐文件核对新版清单与现有 validation；人工教程、资源、工程与索引合并到对应路径，保留 validation/agent、本地输入和回归输入等非交付内容。README 合并当前入口说明，不用分发 README 覆盖仓库导航。旧版原 P01 如出现用户保存的新状态必须保全并验证，不丢失用户内容。

迁移校验原字节、配套资源、文档链接，并串行在新进程核对迁移后的工程。删除前清单记录路径、用途、摘要、保留映射及删除理由；只清理用户指定 deliveries 边界内已核对文件，不修改 ACL、不强制删除未知/占用对象。保存迁移与删除收据，更新当前产物入口及历史可用性，不改写历史执行结果。结束打开 validation 下对应 P01 工程。

遵循本地提交、ff-only 整合与保全归档流程；不 push，不修改插件、安装或依赖。独立人工/科研验收不由本次迁移代替。
