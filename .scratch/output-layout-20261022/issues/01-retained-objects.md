# 受限对象与未知工程后续核对

Triage: ready-for-agent
Status: resolved

初轮未处理 35 个受限目录、6 个受限文件和 1 个 junction，原错误和准确绝对路径在 `validation/agent/reports/2026-10-22/output-layout/residuals.json`。当时对应 9 组工程整组保留，已复制部分不作为完整迁移工程；范围在同批 `protected-project-groups.json`。`outputs/1.blend` 身份未明，保持原位。续办结果见下文。

本机只读核验可使用同批 `inspect-retained.ps1`，不含删除、ACL 或所有权变更。建立准确身份、引用与内容摘要前，不增加删除命令、不按目录名认定缓存；当前项目、恢复文件和链接目标继续保护。需要新授权或其他用户上下文时再处理，原位保留不冒充清理通过。

## Comments

2026-10-22 用户授权继续逐项核对。重试时 35 个目录与 6 个文件均可读取，正按原分类补齐完整工程、迁移有用缓存，并核对旧 wheel；恢复数据继续保护。新证据保存在原报告下 `retained-followup/`，不覆盖首次受限记录。junction 单独核对，未修改权限。

2026-10-22 用户要求先核对剩余未提交改动的任务归属，再将本次续办的四个记录文件提交到本地 Git，不推送。已对照现有逐项结果核对记录，不重新执行迁移、清理或产品验证。

## Answer

42 个对象已逐项复核。30 个目录迁移，5 个恢复目录（155 文件）核对后原位保留；5 个 portable 工程 ZIP 迁移、1 个重复 wheel 去重；空旧运行时的 junction 正常解除，并逐个清理已枚举空目录。9 组工程完整保全，843 个旧位置文件移除，SHA-256、35 Dataset / 1,591 科学数组、VDB 及归档 CRC 检查 Passed，零权限/删除错误。未知 `outputs/1.blend` 摘要不变，当前 P01 未被操作。

准确绝对路径、映射、删除收据、空间口径和可选只读核验命令集中在 `validation/agent/reports/2026-10-22/output-layout/retained-followup/README.md`，权威逐项结果为同目录 `result.json`。没有需要用户手动完成的权限或迁移阻塞。恢复目录及未知工程依然保护，不代表已确定其归属；本轮 Blender 冷读/构建/全量回归 Not Run，复用原字节迁移已有代表证据，实际加载与文件核验独立记录。按用户追加授权提交本地 Git，不推送。
