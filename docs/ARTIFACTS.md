# 产物查找入口

更新：2026-10-06。本页路由现存产物、历史摘要、重建方法和剩余限制。任务状态在 `.scratch/`，开发步骤见 [DEVELOPMENT](DEVELOPMENT.md)，清理边界见[维护规则](agents/storage-maintenance.md)。

## 当前交付

从 [validation](../validation/README.md) 查找当前教程、输入和校验材料；人工入口为 [SOP](../validation/human/SOP.md)。主线 15 步、9 个按需专题，截图由实际操作者按名称补入。

| 内容 | 当前入口 |
| --- | --- |
| 教程与打包 | `validation/human/`；[材料打包](../validation/README.md#人工完成后的打包) |
| 公开、本地及回归输入 | [shared/data](../validation/shared/data/README.md)；当前位置与旧路径由 `migration-map.json` 定位 |
| 当前安装包 | `validation/shared/install/qcblender-0.1.0.zip`；50,656,021 字节，SHA-256 `56dd541da291173f35758df3146832b51eeaa8547796cfd3b5578e37ddf95ad2` |
| 完整候选及原报告 | `outputs/candidates/current/alpha-ci-0.1.0-190e11e/`；源码 `190e11e`、run `37415371574`；[身份记录](../validation/agent/current-install.json) |
| 冻结公开样本 | `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip`；冻结清单位于 `docs/v1-acceptance/tutorial-samples.json` |
| 校验流程与结果 | [Agent 流程](../validation/agent/README.md)、[教程整合验证](../validation/agent/VALIDATION.md)；本次精简结果见下节 |

独立用户操作、截图补齐、checkpoint 复算和科研签署保持各自的 Not Run 状态。当前产物查找以本页为准；旧文档中的 outputs 路径表示当时身份，其实际可用性由本次删除收据确定。

## outputs 精简结果（2026-10-06）

已按批准清单删除 89,895 个文件、8,545,515,461 字节。逐文件路径、大小和 SHA-256 收据位于 `validation/agent/reports/2026-10-06/outputs-prune/apply/removed.jsonl.gz`；完整审查在 `review/decisions.jsonl.gz`，状态和空间口径在 `final-summary.json`。逻辑文件大小与磁盘可用空间变化分别统计。

5,039 个已审查文件、739,869,148 字节保留原位。准确路径、原错误和逐文件 PowerShell 命令见同批 `retry/commands.md`；`retry/retry-reviewed-files.ps1` 默认只核对，添加 `-Apply` 才处理身份未变的清单文件。未知、恢复、保护对象和链接不进入重试清单，未修改 ACL 或所有权。

Passed：151 项基础测试、124 项完整科学测试、5 项重建入口测试、根目录 11 个 wheel 身份、离线打包/安装、MO/摘要/保存及中文路径冷重开、受影响的场景工具和用户工程 11 个原数组读回。检查记录在同批 `after-v2/`、`layout/`、`nocv/` 与 `user-after.json`；基础测试复用同源码的 `after/stdlib.json`。本轮 GUI 点击、真实 NOCV 科研样本和独立人工/科研验收为 Not Run；失败尝试保留原日志与后续修正记录。

两个互补只读权限上下文的逐文件对账 Passed：outputs 从 100,536 个文件、9,776,224,968 字节减至 10,641 个文件、1,230,709,507 字节，其中包含上述待重试文件。junction 目标不纳入统计；未知恢复内容保持原位。

本轮工具改为显式候选、集中输入及新目录重建；保留一套构建/科学环境。GBasis 两份同版本 wheel 的解压成员相同，但 ZIP 摘要不同；根目录已统一为后端记录要求的合格字节，依赖版本与锁文件不变。具体记录为 `wheel-normalization.json`。

## 共用环境与保全项目

| 位置 | 用途与保留范围 |
| --- | --- |
| `outputs/build-site/` | 五个锁定构建包所需的 429 个文件；离线构建验证通过 |
| `outputs/science/` | 现用科学环境，版本不变 |
| `outputs/wheels/`、`outputs/backend-wheel.json` | 11 个锁定且逐份核验的 wheel；统一当前打包入口 |
| `outputs/build-sources/`、`outputs/m0-research/iodata.zip` | GBasis、IOData、历史 qcint 源码 ZIP 各保留一份；来源、版本与 SHA 见同批 `runtime/final-v2/runtime-plan.json` |
| `outputs/native-backend-licenses/` | 六份完整历史许可文本 |
| `outputs/projects/user-session-20260930/` | 用户 `.blend + .qcdata`；新进程冷读 11 数组与原记录一致，未改写工程 |
| `outputs/projects/human-acceptance/` | 本日人工验收工作目录 |
| `outputs/projects/cleanup-followup-original/`、`outputs/projects/recovery/`、`outputs/recovery/` | 未知或需保留恢复对象；按原位保护，不推断可删除 |
| `validation/work/2026-10-06-validation-layout/` | 前批教程整合的代表工程；按该批交付收据定位 |

独有科学原件、Cube、旧计算文件及下载归档按同批 `history/source-review-v2.json` 保留；匿名科学/许可对象由 `objects/review-v2/objects.jsonl.gz` 反查原始路径。早期失败或未完成的计算修订由 `extra-science-review.json` 对应到集中保留的完整版本、条件和原始日志。原始科学文件及完整许可没有被 Markdown 摘要替代。

## 历史任务路由

[历史批次索引](archive/outputs-history/README.md) 保存 67 份 Markdown，覆盖原日期、源码/标签、候选身份、参数、Passed / Failed / Not Run、限制和重建入口。原始日志、历史 Agent 工程、数组、渲染、重复环境及保全 ZIP 以精确退役清单为准；不再承诺这些旧路径可读。压缩逐文件记录和对象 aliases 在本批报告目录，不整批搬移历史二进制。

| 历史主题 | 摘要入口 |
| --- | --- |
| 2026-09-30 整理与迁移 | [output-maintenance](archive/outputs-history/evidence--2026-09-30--output-maintenance.md) |
| 2026-10-01 公开教程 | [public-tutorial-mcp](archive/outputs-history/evidence--2026-10-01--public-tutorial-mcp.md) |
| 2026-10-02 教程与显示/导出 | [tutorial-cu](archive/outputs-history/evidence--2026-10-02--tutorial-cu.md)、[display-xyz-export](archive/outputs-history/evidence--2026-10-02--display-xyz-export.md) |
| 2026-10-03 完成度调研 | [plugin-audit](archive/outputs-history/evidence--2026-10-03--plugin-audit.md) |
| 2026-10-04 P1/P2 与旧工作树 | [audit-p1](archive/outputs-history/evidence--2026-10-04--audit-p1.md)、[audit-p2](archive/outputs-history/evidence--2026-10-04--audit-p2.md)、[legacy-worktree-retry](archive/outputs-history/evidence--2026-10-04--legacy-worktree-retry.md) |
| 2026-10-05 Alpha 与可靠性 | [alpha-readiness](archive/outputs-history/evidence--2026-10-05--alpha-readiness.md)、[reliability](archive/outputs-history/evidence--2026-10-05--reliability.md) |
| 2026-10-06 CI 与 alpha-core 残余 | [actions-fix](archive/outputs-history/evidence--2026-10-06--actions-fix.md)、[alpha-core-cleanup](archive/outputs-history/evidence--2026-10-06--alpha-core-cleanup.md) |

## 遗留清理状态

2026-10-06：重试 `.worktrees/alpha-core` 普通清理。归档标签 `archive/2026-10-05/feat/alpha-core` 仍指向 `9cc9a005` 且可达 main；Git 工作树登记及任务分支已移除。按逐文件 SHA-256 清单删除 30,455 文件/2,671,377,950 字节，补存 7 文件/520,691,210 字节；7,503 份保全内容清理后摘要复核 Passed。现存仅 outputs，79 个扫描路径拒绝访问，目录完整移除 Failed，11 保持 pending；未修改 ACL/所有权或强制删除。清单、两批删除收据及最终复核在 `outputs/evidence/2026-10-06/alpha-core-cleanup/`，入口为 `final-verification.json`。产品测试及 Blender 复做 Not Run。

2026-10-04重试：f458工作树Git登记和已合并`chore/repository-cleanup`分支已正常移除；该次收尾仅保留main工作树/分支，原注释归档标签`archive/2026-09-30/chore/repository-cleanup`仍指向`47fd82c`且可达main。b48c目录已不存在。f458磁盘残留因访问拒绝保留，06继续pending。

以上旧批次的路径与结论按当时身份保留；历史原件可用性改由[摘要索引](archive/outputs-history/README.md)及本次精确删除收据定位。仓库 outputs 之外的旧 f458、alpha-core 磁盘残余不在本次清理范围内，未更新其权限或未完成状态。

## 教程整合与本地归档（2026-10-06）

前批教程整合的报告和保全记录位于 `validation/agent/reports/2026-10-06/integration/`、`subagents/`、`delivery/` 与 `closing/`。原 257 文件清理见 [CLEANUP](../validation/agent/CLEANUP.md)。当前教程、集中输入、冻结材料及 419 张历史截图继续保留。

本轮任务见 [.scratch/outputs-prune](../.scratch/outputs-prune/spec.md)。子任务及整合工作使用本地快进合并和注释标签 `archive/2026-10-06/`；分支为 `docs/outputs-history`、`chore/outputs-runtime`、`chore/outputs-prune-tool`、`chore/outputs-prune`。实际提交、工作树与分支移除状态见本批 `delivery.json`；没有 push。

<a id="用户验证-sop2026-10-06"></a>
## 2026-10-06 旧 SOP 整理记录

当前操作进入[人工 SOP](../validation/human/SOP.md)，历史材料见[v1 索引](v1-acceptance/README.md)。原 SOP 文档整理的范围和验证由[历史摘要](archive/outputs-history/evidence--2026-10-06--sop-user-guide.md)保存。

## 持续维护

按[维护规则](agents/storage-maintenance.md)先保全工程与来源、完成摘要和重建检查，再使用新的精确清单。需要旧候选功能时，从当前源码与集中输入重建并记录新身份；历史 Passed 不代表新对象通过，也不表示旧二进制仍存在。
