# 产物查找入口

更新：2026-10-11。本页路由现存产物、历史摘要、重建方法和剩余限制。任务状态在 `.scratch/`，开发步骤见 [DEVELOPMENT](DEVELOPMENT.md)，清理边界见[维护规则](agents/storage-maintenance.md)。

## 当前交付

从 [validation](../validation/README.md) 查找当前教程、输入和校验材料；人工入口为 [SOP](../validation/human/SOP.md)。主线 15 步、9 个按需专题，截图由实际操作者按名称补入。

| 内容 | 当前入口 |
| --- | --- |
| 教程与打包 | `validation/human/`；[材料打包](../validation/README.md#人工完成后的打包) |
| 公开、本地及回归输入 | [shared/data](../validation/shared/data/README.md)；当前位置与旧路径由 `migration-map.json` 定位 |
| 当前安装包 | `validation/shared/install/qcblender-0.1.0.zip`；50,664,814 字节，SHA-256 `60d572186e127e40e1031a75fff325c3038ab7cc44102d3bdf1e79b6763860ee` |
| 完整候选及原报告 | `outputs/candidates/current/upstream-7dc0d11/`；源码 `7dc0d11`；[身份记录](../validation/agent/current-install.json)、[本次验证](../validation/agent/acceptance/upstream-20261011.md) |
| 冻结公开样本 | `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip`；冻结清单位于 `validation/agent/v1-acceptance/tutorial-samples.json` |
| 校验流程与结果 | [Agent 流程](../validation/agent/README.md)、[当前与历史验证](../validation/agent/VALIDATION.md)；主干维护及历史结果见下文 |

独立用户操作、截图补齐、checkpoint 复算和科研签署保持各自的 Not Run 状态。当前产物查找以本页为准；旧文档中的 outputs 路径表示当时身份，其实际可用性由本次删除收据确定。

<a id="upstream-20261011"></a>
## 主干维护、色带和源构型（2026-10-11）

三份上游增量研究、色带预设、真实节点身份/有效域回归和原子样式基准已合入 main。教程补充多 Cube 叠加、色带操作、源属性与求值几何；当前 0.1.0 Alpha ZIP 和日常 Blender 5.1.1 安装使用同一验证候选。181 基础、130 科学、原生专项、实际 GUI 应用/取消/撤销/菜单重做/反转/距离标注、原地和中文移动冷读 Passed；独立用户及科研接受 Not Run。

| 保留对象 | 位置与作用 |
| --- | --- |
| 当前身份及验证 | `validation/agent/reports/2026-10-11/upstream/delivery.json`；[验收说明](../validation/agent/acceptance/upstream-20261011.md)和[机器索引](../validation/agent/acceptance/upstream-20261011.json) |
| 当前构建与上一候选 | `outputs/candidates/current/upstream-7dc0d11/`；上一批 `ui-bounds-50f1f3b/` 原包继续保留 |
| 科学、节点、色带、有效域、视觉及性能报告 | `validation/agent/reports/2026-10-11/upstream/final/`；性能口径见[研究](research/upstream-20261011-atom-performance.md) |
| 实际界面截图与读回记录 | 同批 `gui/`、`daily-gui/`；截图属于 Agent Computer Use |
| 自包含工程与输入副本 | `outputs/runs/up11/gui-project/accepted.blend` 和同名 `.qcdata/`；`daily-gui-project/`、`final-multicube/` 保留日常与公开叠加工程 |
| 日常安装更新前备份 | `outputs/runs/up11/daily-backup.zip`、`daily-backup.json`，包含原扩展和配置文件的逐项摘要 |
| 重建命令及过程证据 | `outputs/runs/up11/` 保留脚本；同批报告根目录的 `*-process.json` 记录实际命令、PID、配置与退出码 |
| 本地归档 | 同批 `closing.json`、`worktree-preservation.json`；注释标签 `archive/2026-10-11/<完整分支名>` 保存七个本批分支提交 |

按[开发说明](DEVELOPMENT.md)从 `7dc0d11` 和现有锁定 wheels 重建；新 ZIP 需记录新摘要。旧候选、早期失败日志与工程继续保留；本批只移除已合并且已保全的工作树和分支，未执行 outputs 批量清理。

## 空场景按钮与编号范围（2026-10-11）

空场景直接 QC 对象菜单和科学预检入口增加前置条件；轨道、步、帧、模式、原子及结果行按实际数据限制。NOCV 保留源 Pair 编号；NBO 先检查日志，再选择有界 Job/block。162 项基础测试、26 项相关科学解析测试、安装后 180 项空场景/默认对象审计、11 项原生 RNA 范围检查及共享对象保存冷读 Passed。Computer Use 实际点击空场景属性入口、轨道边界和 NBO 两步对话框 Passed；独立人工与科研签署 Not Run。详见[本批验证](../validation/agent/acceptance/ui-bounds.md)。

该批 ZIP 由源码 `50f1f3b` 构建，82 个产品文件核验通过，11 个 wheel 与上一候选逐字节相同；当前入口已由上面的主干维护候选接替。报告位于 `validation/agent/reports/2026-10-11/ui-bounds/`，自包含验证工程、独立安装环境和保留脚本位于 `outputs/runs/ui-bounds/`。上一候选 `outputs/candidates/current/empty-properties-2989bd6/` 及其报告继续保留。任务分支按 `archive/2026-10-11/fix/` 本地归档，收尾状态见该批 `closing.json`。

## 空场景属性入口修复（2026-10-10）

没有活动对象时，“查看对象属性”提示选择对象并保留属性编辑器状态。10 项原生窗口回归、安装后窗口及后台回归、152 项基础测试、离线安装/计算/渲染及中文路径冷重开 Passed；Computer Use 点击因 helper 故障 Not Run，独立人工验收 Not Run。来源、命令和证据见[验证记录](../validation/agent/acceptance/empty-properties.md)。

该批安装包已由 2026-10-11 候选接替；旧 CI 候选仍保留在 `outputs/candidates/current/alpha-ci-0.1.0-190e11e/`。11 个 wheel 与旧候选逐字节相同。共用环境、用户输入与工程保留；本次验证工程位于 `outputs/runs/empty-properties/install/qa/`，本批报告位于 `validation/agent/reports/2026-10-10/empty-properties/`。

## outputs 精简结果（2026-10-06）

已按批准清单删除 89,895 个文件、8,545,515,461 字节。逐文件路径、大小和 SHA-256 收据位于 `validation/agent/reports/2026-10-06/outputs-prune/apply/removed.jsonl.gz`；完整审查在 `review/decisions.jsonl.gz`，状态和空间口径在 `final-summary.json`。逻辑文件大小与磁盘可用空间变化分别统计。

用户随后完成5,039个权限受限文件的身份核验和删除，共739,869,148字节；收据为同批 `retry/retry-20261006-212621-2171.json`，全部状态为Deleted，原路径均已不存在。两批累计删除94,934个文件、9,285,384,609字节。原错误、精确清单和重试脚本继续保留；未知、恢复、保护对象和链接未进入清单。

Passed：151 项基础测试、124 项完整科学测试、5 项重建入口测试、根目录 11 个 wheel 身份、离线打包/安装、MO/摘要/保存及中文路径冷重开、受影响的场景工具和用户工程 11 个原数组读回。检查记录在同批 `after-v2/`、`layout/`、`nocv/` 与 `user-after.json`；基础测试复用同源码的 `after/stdlib.json`。本轮 GUI 点击、真实 NOCV 科研样本和独立人工/科研验收为 Not Run；失败尝试保留原日志与后续修正记录。

初次清理后的两个互补只读权限上下文对账 Passed：outputs 当时从100,536个文件、9,776,224,968字节减至10,641个文件、1,230,709,507字节；该统计包含随后已成功重试删除的5,039个文件。junction目标不纳入统计；未知恢复内容保持原位。

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

当前操作进入[人工 SOP](../validation/human/SOP.md)，历史材料见[v1 索引](../validation/agent/v1-acceptance/README.md)。原 SOP 文档整理的范围和验证由[历史摘要](archive/outputs-history/evidence--2026-10-06--sop-user-guide.md)保存。

## 文档整理（2026-10-06）

[文档总索引](README.md)集中当前使用、开发和研究入口。技术验收与 v1 材料共454个文件归入 `validation/agent/acceptance/` 和 `validation/agent/v1-acceptance/`；四份原根目录专项报告见[验收历史](../validation/agent/acceptance/README.md#早期专项验收全文)。419张截图、冻结清单和历史机器记录共436份文件保持迁移前原始字节，历史路径按[对应关系](../validation/agent/acceptance/README.md#历史路径与当前位置)定位。

逐文件基线、引用审查、摘要与链接检查保存在 `validation/agent/reports/2026-10-06/docs-organize/`，最终迁移证据在 `migration/`；48项候选/发布/数据准备测试、138份文档的1,286个本地链接/锚点及主检出的实际冻结包、数据准备和教程材料检查 Passed。本地提交、两个注释归档标签及工作树处置由 `delivery.json` 定位。Blender、科研复算及独立人工验收 Not Run。

## 持续维护

按[维护规则](agents/storage-maintenance.md)先保全工程与来源、完成摘要和重建检查，再使用新的精确清单。需要旧候选功能时，从当前源码与集中输入重建并记录新身份；历史 Passed 不代表新对象通过，也不表示旧二进制仍存在。
