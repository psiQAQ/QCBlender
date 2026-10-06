# 01 文档结构与依赖审查

Triage: ready-for-agent
Status: resolved
Owner: main agent with two read-only agents

## Scope

统计当前文档与本地忽略资料，检查v1冻结清单、截图和机器记录的活跃引用，区分当前文档与历史批次。

## Acceptance

保留/迁移结论有具体引用依据，科学来源与验收身份不丢失；机器报告记录初始路径和SHA-256。

## Answer

Passed：561份跟踪文档与9份本地忽略材料已盘点。v1为424文件，其中419截图全部SHA不同；240张被操作登记引用、178张仅有历史引用、1张负例原图无显式引用但保留证据价值。冻结清单与公共副本和ZIP成员字节一致，4份根历史验收不与批次摘要等价，采用保留全文并归组。结构及依赖审查分别在主报告structure-audit和v1-audit目录；未知忽略资料保持原位。
