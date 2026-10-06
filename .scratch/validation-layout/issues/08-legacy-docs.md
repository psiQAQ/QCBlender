# 08 清理历史教程重复入口

Triage: ready-for-agent
Status: resolved
Blocked by: 05
Owner: legacy-docs agent
Baseline: main@8f686c2

## Scope

核对并清理 `docs/v1-acceptance/` 内已被统一校验目录取代的操作包装页，修复现行文档链接，明确历史材料用途。保留独有来源、科学条件、验证证据、全部历史截图及冻结 `tutorial-samples.json` 的原始字节。产品源码、依赖、数据和压缩包保持现状；主检出的已有修改由主 Agent 维护。

## Acceptance

人工操作统一进入 `validation/human/SOP.md`；删除页面的有效链接均已更新；历史记录与冻结清单可追溯并保持身份。按 Passed / Failed / Not Run 记录检查结果，完成本地提交并等待主 Agent 串行合并。

## Comments

2026-10-06：用户授权清理旧验收目录中可删除的重复内容。任务 05 已 resolved；在独立工作树和 `docs/validation-legacy-docs` 分支领取。三处现有主检出修改不纳入本任务。

## Answer

删除已由统一入口取代的 `SOP.md`、`MATERIALS.md`、`RECORD-TEMPLATE.md` 三个转发页，增加历史目录 README，明确人工教程、技术检查和历史资料的入口。SOURCES 的历史结果链接改为 HISTORY/AGENT-REPLAY 和独立人工任务；发布研究的完整验收链接改为现行 v1 规格和任务 02。历史任务中的旧文件路径继续作为当时的记录保留。

- Passed：423 个保护对象逐文件大小及 SHA-256 不变，覆盖全部 419 张截图（393 张早期截图及 26 张后续专项截图）、HISTORY、AGENT-REPLAY、冻结样本清单和操作登记表。
- Passed：三个重复页面已删除；README 的 10 个本地链接存在；子 Agent 扫描其负责的受跟踪 Markdown 未见指向删除页面的有效链接，`git diff --check` 通过。主 Agent 已在 main 的 `cabef24` 更新 ARTIFACTS 五处链接。
- Not Run：Blender、GUI、独立人工及科研验收。本任务仅清理文档，不转写历史验证状态。

子任务提交 `61acdb2` 已快进合入 main，主检出三处原有修改在合并前后保持原字节。本批摘要清单和检查脚本位于 `validation/agent/reports/2026-10-06/legacy-docs/`。主分支链接复核由 `closing/verification.json` 记录，归档身份由 `delivery/followup-worktrees.json` 记录。
