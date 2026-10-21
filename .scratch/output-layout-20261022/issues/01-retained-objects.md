# 受限对象与未知工程后续核对

Triage: ready-for-human
Status: pending

本次未处理 35 个受限目录、6 个受限文件和 1 个 junction，原错误和准确绝对路径在 `validation/agent/reports/2026-10-22/output-layout/residuals.json`。对应 9 组工程整组保留，已复制部分不作为完整迁移工程；范围在同批 `protected-project-groups.json`。`outputs/1.blend` 身份未明，保持原位。

本机只读核验可使用同批 `inspect-retained.ps1`，不含删除、ACL 或所有权变更。建立准确身份、引用与内容摘要前，不增加删除命令、不按目录名认定缓存；当前项目、恢复文件和链接目标继续保护。需要新授权或其他用户上下文时再处理，原位保留不冒充清理通过。
