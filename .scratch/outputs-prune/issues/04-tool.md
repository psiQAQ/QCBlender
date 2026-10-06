# 04 清理工具与安全检查

Triage: ready-for-agent
Status: resolved
Blocked by: 01
Owner: cleanup tool agent

## Scope

扩展 prune_outputs 的明确逐文件退役集合，支持已审查的历史 evidence/projects/text/匿名对象，保护项目优先；允许新报告写入 validation/agent/reports。保留 --plan/--apply 和原安全检查，避免重复全仓哈希和覆盖报告。

## Acceptance

测试保护优先、越界/链接、文件变化、缺少摘要、匿名对象存在有效引用时保留；apply 只处理清单未变更文件，原错误和收据完整保留。只运行隔离测试，不对主检出 apply；本地提交后等待串行合并。

## Answer

- 新增 `retired_files` 与 `retained_references`，均为 outputs 相对精确文件路径；原四个策略字段保持兼容。明确保护、有效引用、当前报告、recovery 工程与 Git 跟踪项优先；匿名保全目录需要逐文件退役，不通过任务或环境根范围自动删除。
- `--report-dir` 允许 outputs 或 validation/agent/reports 下的普通子目录，核对祖先链接和实际路径。plan、apply 及成功收据独占创建，已有报告不能覆盖；安全检查在 Python 优化模式下仍有效。
- 启用策略时，plan 只为删除候选、明确保护项、有效引用和 Git 跟踪项计算输出摘要。未知保留对象和未知 recovery 的扫描失败记录在 summary.skipped，保持原位；apply 对这些扫描失败路径只核对绝对路径与 outputs 词法边界，不解析未知 junction 或拒绝访问目录。明确保护范围或包含 Git 跟踪项的范围无法枚举则阻塞整批删除。集中科学输入与索引保存 stat/SHA-256 并在 apply 前复核。
- apply 全量预检保护项目和删除授权，通过后才逐文件复核 stat/SHA-256 与路径并删除。任何保护失败零删除；内容变化、缺少摘要和权限失败保留文件及原错误。
- `applied.json` 记录 status、protection_preflight、removed.files/bytes、protected_hashes_verified、removed_receipt 和 skipped 的 path/reason/phase。成功逐文件收据为 `removed.jsonl.gz`，每行 path/bytes/sha256；删除失败的 phase 为 delete，可据此生成精确重试命令。保护或收据故障不混入删除重试集合。

验证：`python -m unittest tests.test_storage_cleanup` — Passed，26 项隔离测试；同套测试在 `python -O` 下 — Passed。`python -m compileall -q tools/prune_outputs.py tests/test_storage_cleanup.py` 和 `git diff --check` — Passed。实际主检出清理、Blender 和全仓科学验证 — Not Run，由任务05/06执行。工作树和分支保留，等待主 Agent 唯一串行合并。
