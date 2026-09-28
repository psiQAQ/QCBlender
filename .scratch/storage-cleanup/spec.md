Triage: ready-for-agent
Status: resolved

# 阶段产物清理与必要输入集中

保全 PID 3144 的当前便携工程并关闭；集中 SOP 和科学回归必要输入到 tests/data，原件保持字节摘要；维护输入索引和 SOURCES.md。保留安装环境、配置、共享构建依赖、日志与历史验证报告，删除明确不再需要的候选、生成工程、运行数据和缓存。按用户批准的新保留政策更新 AGENTS、维护流程和现有 CHANGELOG。

## 验收

- 保全工程在清理前后独立冷重开 Passed。
- 输入摘要和关联 CSV Passed；科学回归无新增跳过。
- 相关 Blender 检查从集中输入重新构建场景 Passed。
- 软件环境非缓存内容和既有 Git 标签不变；清理清单和空间报告保留。
- 本地提交合回 main，工作分支归档后移除；不推送、不发布、不代签人工验收。

## Comments

已完成便携保存和首次冷重开：4 个 Dataset、3 个体文件、19 个对象。保存目录 outputs/recovery/pid3144-preserved，作为清理保护对象。

2026-09-29：104 个输入及 CSV 核对 Passed；69 项科学回归前后均 Passed、0 skipped；相关 Blender 重建/冷重开 Passed。清理 9.39 GB，实测约 22.85 → 13.43 GB。用户工程清理后仍可重开。软件环境、来源资料、Git 既有标签与子模块保留；权限受限和归属不明项按计划跳过。详情见 docs/acceptance/storage-cleanup.md，操作与例外记录位于 outputs/storage-cleanup/。
