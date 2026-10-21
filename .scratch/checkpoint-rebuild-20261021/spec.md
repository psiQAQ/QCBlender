# 重建两个教程检查点并补齐保存前验证

Triage: ready-for-agent
Status: resolved
Baseline: main@20d137057b842e99ac064121eabfbdc3878adf84
Date: 2026-10-21

用户要求解释原保存前完整快照缺口，并重新生成 P01-orbital 与 P06-annotations 补齐验证；已确认保存并关闭当前 Blender。沿本轮已授权本地提交、快进、保全归档流程，不 push 或发布。

从原始 FCHK/XYZ 输入和真实插件操作重新建立科学数据、轨道或标注，不从旧工程复制对象。父 Agent 独占 Blender，两个离线 helper 由独立工作树准备。

保存协议：先建立不含科学对象的空白种子工程，使相对路径拥有真实目标；生成完整案例状态后调用真实 Save Portable QC Project。注册临时 save_pre 观察器，在插件已复制和核对科学侧车、重绑路径后且 Blender 写入新场景前捕获完整快照。记录种子文件摘要、回调时文件摘要和快照成功状态，必须确认回调发生且旧文件尚未改变；随后退出并新进程严格比较。原始生成数组与保存前/后状态另做核对，不能把保存后的快照改名为保存前。

新教程材料及 ZIP 保存在 `outputs/deliveries/checkpoint-rebuild-20261021/`，保留旧材料和失败报告。全部未变工程复用已核对相同字节的有效冷读；两个新检查点必须原位及中文路径解包冷读 Passed。更新现有验收、工程索引、当前交付路由及任务记录；独立人工/科研验收仍 Not Run。

结束恢复用户已保存的原 P01 工程，核对本批启动前身份，保留窗口；源码与安装包无需变更。

## Answer

两例从原始输入重建，保存前、保存后、冷读及中文路径解包比较均 Passed、零差异；完整教程 36 工程中 2 个新检查点、34 个逐字节未变工程复用有效验证。原 P01 恢复 Passed；独立人工/科研验收 Not Run。详见 `validation/agent/acceptance/checkpoint-rebuild.md`。

本地提交 `4959619` 已以 ff-only 合入 main。三个本批工作树的 6 个忽略文件已逐项保全、摘要核验后正常移除，任务分支正常删除；注释标签为 `archive/2026-10-21/task/{checkpoint-rebuild-20261021,checkpoint-p01-20261021,checkpoint-p06-20261021}`。逐文件清单、归档 ZIP 和收据位于 `outputs/runs/checkpoint-rebuild-20261021/finish/<工作树名>/`。当前工程、教程 ZIP 及验证证据均保留在主仓库稳定目录，未 push 或发布。
