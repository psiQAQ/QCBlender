# outputs 深度精简

Triage: ready-for-agent
Status: resolved
Baseline: main@f6a2391
Date: 2026-10-06

## 目标与授权

用户明确要求实施已确认计划：历史批次以 Markdown 摘要、精简压缩文件清单和删除收据留存，删除已结束 Agent 验证工程、数组、渲染、日志、冗余报告、旧环境及构建产物。保留一套现用构建和科学环境及锁定 wheels，不更新依赖版本。计划内类别和本地提交、串行快进合并、归档已获授权；不 push。

清理只在主检出 outputs 内执行，不把整批历史移到其他目录。当前教程、集中科学输入、最新完整候选、明确用户工程、今天人工验收目录、未知恢复对象及不可枚举内容保留。保留项目优先；科学来源与完整许可不能仅由摘要替代。历史技术结果保持执行时身份，不转写为当前人工验收。

## 分工与依赖

| 任务 | 文件归属和完成条件 |
| --- | --- |
| [01 基线](issues/01-baseline.md) | 主 Agent：保护原有三处修改，计划进入 main |
| [02 历史摘要](issues/02-history.md) | 历史子 Agent：docs/archive/outputs-history/、任务02；给出批次和对象映射依据，保留结论/失败/条件/重建入口 |
| [03 环境及重建引用](issues/03-runtime.md) | 环境子 Agent：tools/tests 中除 prune_outputs 与 test_storage_cleanup 外的引用修复、DEVELOPMENT、validation/agent/README、任务03；交接环境/来源原件逐文件退役建议 |
| [04 清理工具](issues/04-tool.md) | 工具子 Agent：tools/prune_outputs.py、tests/test_storage_cleanup.py、任务04；精确清单、保护优先、安全边界及测试 |
| [05 清单与执行](issues/05-inventory-apply.md) | 主 Agent：完成02/03/04后，核对保留对象、摘要和重建，生成准确清单、执行删除、失败命令 |
| [06 整合与交付](issues/06-verify-delivery.md) | 主 Agent：清理后测试、真实离线构建/安装/保存重开、文档路由、工作树保全与本地归档 |

子 Agent 使用 GPT-6.1 Sol / high，在独立工作树自查并提交，等待唯一串行合并轮次；主 Agent 统一操作 Blender 和主检出历史文件。任意子 Agent 不删除主检出文件、不启动 Blender。

## 保留与退役

- 保护 validation 的当前材料、最新完整候选 alpha-ci-0.1.0-190e11e、user-session-20260930、human-acceptance、未知 recovery 工程及用户未提交修改。
- 历史任务报告、生成工程、数组/VDB、渲染、导出、环境副本及备份对象，只有批次摘要完成且输入/来源已核对时才加入逐文件退役集合；内容对象所有有效引用均须已退役或迁移。
- 保留根 wheels 中锁定依赖与当前纯 Python GBasis wheel，统一当前引用后清理 qualified 副本和旧原生 wheel。构建环境按当前锁定五项及文件归属缩减；保留 science、当前记录和必要 GBasis 来源归档。
- 集中目录已有同字节原件的旧输入可删除；独有必要科学文件、原始计算条件、许可和参考资料保存一份并更新入口。
- 未分类、链接/junction、大小/修改时间/内容变化及权限拒绝项保留；没有 ACL、所有权或强制删除操作。

## 检查和交付

清理工具必须拒绝保护项、越界/链接、文件变化和缺失摘要；报告保留原错误且不能覆盖。删除前后核对保护对象、候选和输入，运行基础/完整科学测试及代表性离线打包、安装、生成、保存冷读。当前工具和文档引用已删除材料时必须修复；历史路径由 Markdown 摘要明确标为退役。

新报告和可审查脚本位于 validation/agent/reports/2026-10-06/outputs-prune/。历史摘要位于 docs/archive/outputs-history/，ARTIFACTS 是唯一产物路由。最终分别报告文件数、逻辑字节变化、磁盘可用空间变化和未统计范围。

无法删除的已审查清单项交付准确绝对路径、原错误、对应 PowerShell 命令及重试脚本；重试前复核身份。未知、未枚举和受保护对象不混入删除命令。目录递归命令仅用于已完整枚举且全部属于退役集合的目录。

## 结果

已删除89,895文件、8,545,515,461字节；outputs逐文件对账剩余10,641文件、1,230,709,507字节，其中5,039个权限受限已审查文件保留并交付准确命令。完整当前入口为docs/ARTIFACTS.md；本批final-summary.json汇总验证与统计，delivery.json记录最终main、注释标签和工作树/分支状态。未知、用户及恢复对象均不进入删除集合。
