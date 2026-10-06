# 04 清理工具与安全检查

Triage: ready-for-agent
Status: pending
Blocked by: 01
Owner: cleanup tool agent

## Scope

扩展 prune_outputs 的明确逐文件退役集合，支持已审查的历史 evidence/projects/text/匿名对象，保护项目优先；允许新报告写入 validation/agent/reports。保留 --plan/--apply 和原安全检查，避免重复全仓哈希和覆盖报告。

## Acceptance

测试保护优先、越界/链接、文件变化、缺少摘要、匿名对象存在有效引用时保留；apply 只处理清单未变更文件，原错误和收据完整保留。只运行隔离测试，不对主检出 apply；本地提交后等待串行合并。
