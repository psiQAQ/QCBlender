# 产物查找入口

更新：2026-10-23。本页路由现存产物、历史摘要、重建方法和剩余限制。任务状态在 `.scratch/`，开发步骤见 [DEVELOPMENT](DEVELOPMENT.md)，清理边界见[维护规则](agents/storage-maintenance.md)。

## 当前交付

本地环境与工作目录现按 [modules](../modules/README.md) 和[维护规则](agents/storage-maintenance.md#当前目录职责)分类：共用依赖在 `modules/`，缓存和临时工作在 `.tmp/`，本机 Blender 配置在 `.local/blender/`。`outputs/` 保留实际输出。2026-10-22 整理的逐文件旧/新路径、SHA-256、用途和清理状态以 `validation/agent/reports/2026-10-22/output-layout/migration.jsonl.gz` 为准；ZIP 成员保全映射在同批 `archive-members.jsonl.gz`。历史记录中的旧路径和 Passed 保持当时身份，当前位置按映射查询；实际验证和残留见[本批验收](../validation/agent/acceptance/output-layout.md)。

开发流程工具已完成技术验收：[入口](agents/development-workflow.md)、[当前结果](../validation/agent/acceptance/dev-workflow.md)，日志与规则备份当前位置由本次迁移映射定位，正式记录在 `validation/agent/reports/2026-10-16/dev-workflow-20261016/legacy-outputs/`。真实 MCP、构建安装和原工程恢复 Passed；当前有效候选见下表。

从 [validation](../validation/README.md) 查找当前教程、输入和校验材料；人工入口为 [SOP](../validation/human/SOP.md)。主线 15 步、10 个按需专题；2026-10-21 完成的 79 步和 27 张截图保留当时身份。后续增补自动出图、Mayer 和表面距离投影，各批实际复验范围见对应验收。

| 内容 | 当前入口 |
| --- | --- |
| 宣传与教程网站 | [维护与预览](../website/README.md)、[本批验收](../validation/agent/acceptance/website.md)；[线上网站](https://notes.psiqaq.cn/QCBlender/)；网站构建、浏览器、Pages 与三组 Blender 新图/冷读 Passed；插件候选 CI 的 3 项失败单独记在验收中；工程在 `outputs/projects/website-showcase/`，图像、会话与归档收据在 `validation/agent/reports/2026-10-23/website/`；本地标签 `archive/2026-10-23/feat/website`、`archive/2026-10-23/feat/website-ui`、`archive/2026-10-23/feat/website-docs`；从 `website/README.md` 重建 |
| 当前完整教程材料 | `validation/`；[工程索引](../validation/工程索引.md)、[迁移与清理](#delivery-consolidation-20261022)；需要分发时按下行打包 |
| 教程与打包 | `validation/human/`；[材料打包](../validation/README.md#人工完成后的打包) |
| 教程图片和人工工程 | `validation/human/screenshots/`、`validation/human/renders/` 随文档入库；当前工程在 `validation/work/human/`；[当前截图与工程](../validation/工程索引.md) |
| 公开、本地及回归输入 | [shared/data](../validation/shared/data/README.md)；当前位置与旧路径由 `migration-map.json` 定位 |
| 当前安装包 | `validation/shared/install/qcblender-0.1.0.zip`；50,984,291 字节，SHA-256 `53b412c62fda4503ad3d1054e949ee2b7238b3aaf78978cb7037d0bd6bc4f3bf` |
| 当前候选及验证 | `outputs/candidates/surface-projection/build-2/`；源码 `368a4ab`，增加表面距离投影；定向检查、实际源码 GUI、完整构建及 134 成员隔离安装、最终包渲染与冷读 Passed；[身份记录](../validation/agent/current-install.json)、[本次验证](../validation/agent/acceptance/surface-projection.md)。日常安装仍为 Mayer `13febd…`，新包日常安装 Not Run |
| 冻结公开样本 | `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip`；冻结清单位于 `validation/agent/v1-acceptance/tutorial-samples.json` |
| 校验流程与结果 | [Agent 流程](../validation/agent/README.md)、[当前与历史验证](../validation/agent/VALIDATION.md)；主干维护及历史结果见下文 |

<a id="surface-projection-20261023"></a>
## 表面距离投影适配器（2026-10-23）

真实 Ru vdW 距离图的二维 Dataset、三态、原子 XY 投影、Viridis/Cividis、等值线、点值及全量 CSV 已实现。[验收](../validation/agent/acceptance/surface-projection.md)与 `validation/agent/reports/2026-10-23/surface-projection/acceptance.json` 是本批结果入口。源码定向 21 项、GUI 导入/设置/撤销重做/取消/点值及保存冷重开、最终完整包构建与 134 成员隔离安装、真实原生运行/渲染/冷读 Passed；当前安装入口已更新为上表最终包。

GUI 便携工程在 `outputs/projects/surface-projection/gui/projection-gui.blend` 及配套 `.qcdata/`；最终安装案例的工程、数据、渲染 `projection.png` 和 CSV 在 `outputs/projects/surface-projection/installed/`。本批原始收据、日志、截图和工作路径的保全映射为同批报告 `evidence-map.json`。源码验证缓存保留在 `.tmp/runs/projection/`；共用 wheels 与输入保留，未执行额外旧包或历史产物清理。复验工具为 `tools/verify_surface_projection.py`；[第 10 专题](../validation/human/topics/10-surface-projection.md)解释真实本机案例与输入契约。AICD 保持原材料阻塞，独立人工/科研、日常安装和远端发布 Not Run。

本地归档入口为 `archive/2026-10-23/feat/surface-distance-projection`（实现）与 `archive/2026-10-23/build/surface-distance-projection`（完整包证据）；工作树保全及正常移除收据在同批报告 `finish/`。主检出原有研究及子模块修改继续保留。

<a id="projection-reference-20261023"></a>
## 表面距离投影真实参照（2026-10-23）

官方 Ru 构型的 Multiwfn 2026.9.20 vdW 实际输出及独立球面求交参照，集中在 `validation/shared/data/local/scientific-displays/ru-vdw-20261023/`，八文件均由 `local-inputs.json` 的同名 key 前缀定位并核对哈希。输入、设置、命令、运行日志、扫描参数及完整 2,501 点参考均保留；原件和工作副本未删除。数值和有效域核对 Passed，02 前置解除；适配器、Blender 与独立人工科研验收 Not Run，当前安装包未改变。详细条件与误差界见[研究记录](research/scientific-display-reference-inventory-20261023.md#本次实际运行及数值验收)，机器验收及标准库复现脚本位于 `validation/agent/reports/2026-10-23/projection-reference/`；脚本的 prepare/run 在新工作目录生成输入与实际结果，verify 更新同批验收 JSON，复验前保全旧记录。AICD 仍缺同源 all/π转储，缺件清单沿用同一研究记录。

<a id="mayer-20261023"></a>
## IRC Mayer 逐键着色（2026-10-23）

产品源码 `4b90967`，当批完整候选在 `outputs/candidates/mayer/build-1/`，仍是已验证的日常安装身份。P04 六原子对、三步联动、阈值/原子筛选、18 个导出数值及原数组保护、关闭恢复、实际 GUI 撤销/菜单重做、渲染和保存冷重开 Passed；[验收](../validation/agent/acceptance/mayer.md)与 `validation/agent/reports/2026-10-23/mayer/acceptance.json` 定位原始证据。复验入口为 `tools/verify_mayer_display.py`。

工程及 `.qcdata` 在 `outputs/projects/irc-mayer/installed/`、`outputs/projects/irc-mayer/gui/`；前者保留最终渲染 `mayer.png`。测试配置及可重建缓存在 `.tmp/runs/mayer/`，早期成图和失败日志保留。日常配置已按追加授权安装同一候选，实际 GUI、便携保存与冷读 Passed；补充工程位于 `outputs/projects/irc-mayer/daily/`，证据在同批报告 `daily/acceptance.json`，旧安装及偏好备份在 `.local/blender/backups/mayer-20261023/`。教程第 6 步及实际截图已更新。本地 ff-only 合入后以 `archive/2026-10-23/feat/irc-mayer-color` 归档，工作树保全及移除记录在同批 `finish/`。原调研修改和无关工作树保留，不推送。

[任务规格](../.scratch/scientific-displays-20261023/spec.md)同时维护表面距离投影和 AICD 的真实参照前置；这两项当前没有交付适配器。

<a id="auto-output-20261023"></a>
## 自动观察方向与统一出图（2026-10-23）

提供当前视角、主轴取景和近似减少遮挡；统一色彩管理、背景、PNG、尺寸、三点柔光及 EEVEE/Cycles 档位，在当前场景应用并可恢复。SOP 的操作、参数截图和实际成图同步更新。去重 61 项定向测试、四类真实工程、GUI 与持久化、完整候选隔离安装 Passed，详见[验收](../validation/agent/acceptance/auto-output.md)。日常配置已按追加授权安装，128 个成员核对、原生自动取景/三档出图和冷读 Passed，未备份旧安装；收据在同批 `daily/`，工程在 `outputs/projects/auto-output/daily/mo/`。随后补做日常 GUI 的两种自动取景、白底/透明渲染、恢复和副本冷读 Passed；[GUI 记录](../validation/agent/reports/2026-10-23/auto-output/daily-gui/acceptance.json)保留首轮观察脚本失败与重试证据，成图和工程在 `outputs/projects/auto-output/daily/gui-2/`。独立人工/科研、全量回归和远端 CI Not Run。

工程、配套数据和渲染保留在 `outputs/projects/auto-output/`，各轮候选在 `outputs/candidates/auto-output/`；该批最终有效包为 build-4，其日常安装已由上节 Mayer 候选接替。前一有效包仍在 `outputs/candidates/current/sop-completion-20261021/`，失败候选和旧包未清理。正式收据、截图及执行脚本在 `validation/agent/reports/2026-10-23/auto-output/`；原 `.tmp/runs/auto-output/` 的记录对应其 `runs/` 子目录。

本地任务分支 `feat/auto-viewpoint`、`feat/output-settings`、`feat/auto-output` 按 ff-only 整合，归档标签采用 `archive/2026-10-23/<完整分支名>`；逐文件保全和实际移除结果由同批 `finish/` 收据确认。主检出原有上游引用、调研文件保留；不 push。用户明确无需恢复原工程，本批 Blender 已退出。

<a id="output-layout-20261022"></a>
## outputs 分类整理（2026-10-22）

已迁移并核验 10,130 个原文件；退役 58,121 个缓存、旧安装副本及本批验证包，共 5,961,811,713 逻辑字节。实际删除源文件总数为 68,251，包含已迁移的旧位置，空间收益不重复计算这部分。详细数量和磁盘空间口径以同批 `cleanup.json` 为准；删除收据为 `removed.jsonl.gz`。当前已验证候选和教程安装入口保持 SHA-256 `06b46875482a4ee377180717551457f9b74019f01c6c3f3221754119f75ff052`。

新位置导入、最终主检出的 272 项标准库和 98 项相关路径检查、5 项科学/持久化回归、离线构建及 11 个 wheel 核验、代表工程删源后独立冷读 Passed。P01 已恢复，科学、对象、材质及节点状态一致，GUI 区域像素尺寸有差异；严格全快照首次失败及后续实际比较均保留。独立人工/科研和远端 CI Not Run。

初轮的 35 个受限目录、6 个受限文件和 1 个 junction 记录保留在 `residuals.json`。继续核对时目录和文件均已可读：9 组完整工程及 5 个 portable 工程归档补齐到 `validation/work/agent/{up11,empty-properties,annotations-20261016}/`，10 个有用 worker 缓存目录归入 `.tmp/cache/blender-jobs/`；逐文件新旧路径和摘要见同批 `retained-followup/mapping.json`，复制核验见 `copy.json` 和 `destination-validation.json`。5 个恢复数据目录、`outputs/1.blend` 和原用户工程保持原位；旧 wheel 与锁定副本完全相同。后续清理结果、junction 处置及任何仍需手动处理的准确路径以 `retained-followup/README.md` 为准。本页各历史日期章节保持当时结论，旧二进制当前可用性以迁移与退役收据为准。

<a id="delivery-consolidation-20261022"></a>
## 教程交付材料统一到 validation（2026-10-22）

最新版 `checkpoint-rebuild-20261021` 的材料已按原目录结构合并到 `validation/`。91 个相同文件复用，3 个旧 P01 文件覆盖，1,660 个文件补入；README 合并导航，新增[工程索引](../validation/工程索引.md)。36 个工程、27 张图片及全部配套材料保持交付内容，原 P01 也位于 `validation/work/human/P01/P01.blend`。原有 Agent 报告、本地输入、回归数据和 23 个不对应的旧工作文件保留。

两批旧分发目录、ZIP、中文路径解包副本和旧批次自动备份已按用户授权逐文件清理：7,055 文件、2,129,569,652 字节，目录已移除，无失败残留。36 个迁移工程新进程比较全部 Passed，原 P01 已在 validation 路径恢复打开；清理范围仅限 `outputs/deliveries/`，收据见[迁移验收](../validation/agent/acceptance/delivery-consolidation.md)。迁移映射、冷读与清理收据位于 `validation/agent/reports/2026-10-22/delivery-consolidation/`，编排脚本位于 `outputs/runs/delivery-consolidation-20261022/`。不另存完整教程 ZIP；需要时从当前材料按[打包说明](../validation/README.md#人工完成后的打包)重建。独立人工/科研验收未由本次迁移替代。

本地提交 `3a1fbc7` 已快进合入 main；任务工作树已正常移除、分支正常删除，3 个生成缓存文件经摘要核验保全。注释归档标签为 `archive/2026-10-22/task/delivery-consolidation-20261022`，清单、归档 ZIP 和收据位于 `outputs/runs/delivery-consolidation-20261022/finish/`。当前工程与证据均保留于主仓库，未 push 或发布。

<a id="checkpoint-rebuild-20261021"></a>
## 两个检查点从原始输入重建并补齐保存前验证（2026-10-21）

后续可用性：本节路径和 ZIP 摘要对应当时交付。2026-10-22 材料迁入 `validation/`，原分发副本已按清单删除，见[本次清理范围](#delivery-consolidation-20261022)；当前材料请使用上方入口。

新完整教程包在 `outputs/deliveries/checkpoint-rebuild-20261021/QCBlender-tutorial.zip`，296,596,161 字节，SHA-256 `f885589e4e6237cd3ca4dddc6de12ea57a976f9e973fd685556067cdb524f4fb`。P01-orbital 与 P06-annotations 从原始输入重建，真实保存前快照、保存后、原位及中文路径解包冷读均 Passed、零差异；旧两个检查点的快照缺口在新交付物中已补齐。

其余 34 个工程及其全部配套文件逐字节未变，复用有效报告；仍为 79 步、27 图、36 工程。完整索引在新展开目录 `工程索引.md`，证据在 `validation/agent/reports/2026-10-21/checkpoint-rebuild/`，详细边界见[补验](../validation/agent/acceptance/checkpoint-rebuild.md)。原 ZIP、工程及失败报告均保留；原 P01 窗口已恢复。独立人工/科研验收 Not Run。脚本及本地归档收据在 `outputs/runs/checkpoint-rebuild-20261021/`。

本地提交 `4959619` 已以 ff-only 合入 main。三个本批工作树的 6 个忽略文件已逐项保全、摘要核验后正常移除，任务分支正常删除；注释标签为 `archive/2026-10-21/task/{checkpoint-rebuild-20261021,checkpoint-p01-20261021,checkpoint-p06-20261021}`。逐文件清单、归档 ZIP 和收据位于 `outputs/runs/checkpoint-rebuild-20261021/finish/<工作树名>/`。当前工程、教程 ZIP 及验证证据均保留在主仓库稳定目录，未 push 或发布。

<a id="sop-completion-20261021"></a>
## SOP 全步骤、截图与工程材料（2026-10-21）

后续可用性：本节保留原批次结果。2026-10-22 旧包及副本已按清单删除，见[本次清理范围](#delivery-consolidation-20261022)，两个旧检查点已由后续重建版本替代，当前材料位于 `validation/`。

79 个编号步骤及章节内演示、27 张教程图已完成；36 个最终工程和检查点原位及中文路径解包新进程比较 Passed。最终教程 ZIP 含 1,755 个文件，296,605,483 字节，SHA-256 `a567d578cf0bfb4940bc2a02b140e8d4af61016440571a84e7b81cbdfa414a9c`。P01 已恢复，原生基线比较 Passed、差异为空，CU 观察相位与相机取景正常。

完整包：`outputs/deliveries/sop-20261021/QCBlender-tutorial.zip`；展开目录中的 `README.md`、`工程索引.md` 可直接导航全部教程与工程。本批使用材料从此入口读取，旧 `validation/work/human/` 工程保持原样。证据在 `validation/agent/reports/2026-10-21/sop-completion/`，详见[验收](../validation/agent/acceptance/sop-completion.md)。

独立人工/科研验收和发布资格 Not Run。P01 轨道、P06 标注缺原保存前完整快照的范围单独记录。历史失败报告、旧安装和偏好、31 个未入包的自动备份原位保留。工作树脚本及忽略文件保全、归档和本地提交收据在 `outputs/runs/sop-20261021/finish/`；不 push。重建沿用统一 build/install 入口，教程打包脚本与工程检查脚本随本批保全。

任务提交 `0ed0fea` 已快进合入 main，主检出材料与候选身份复核 Passed；三个工作树的 202 个忽略文件已保全、核验后正常移除。注释标签为 `archive/2026-10-21/task/{sop-completion-20261021,sop-docs-20261021,sop-project-check-20261021}`，各标签保持原任务最终提交身份。

<a id="annotation-width-20261017"></a>
## 添加和编辑标注窗口宽度减半（2026-10-17）

两个弹窗宽度参数从 760 改为 380，保留横排 XYZ、元素和全局坐标预览。35 项定向测试、完整构建、隔离/日常安装 123 个成员核对、原生标注和保存冷读 Passed；Computer Use 观察原子/二面角添加和原子编辑窗口，编号步进及 X 偏移可操作，四个来源原子行和底部按钮完整可见。[验收](../validation/agent/acceptance/annotation-width.md)区分原生调用、GUI 操作和日常配置覆盖。

稳定候选见当前交付表；旧当前 ZIP、日常旧插件和偏好、工程、失败重试及脚本保存在 `outputs/runs/annotation-width-20261017/`，报告与两张裁剪截图在 `validation/agent/reports/2026-10-17/annotation-width/`。日常 GUI 点击、完整科学套件复跑及独立人工/科研接受 Not Run。工作树忽略文件保全和正常移除收据在本批 `finish/`，注释标签为 `archive/2026-10-17/fix/annotation-dialog-width`。不 push；重建使用统一 build/install 入口和 `tools/verify_annotation_dialog.py`。

<a id="annotation-ui-20261017"></a>
## 标注字号、元素文字与坐标预览（2026-10-17）

四类新建字号 0.5、原子文字纯元素、XYZ 偏移横排及来源编号同行实时全局坐标。266 标准库、100 公开科学、65 定向、完整构建/隔离安装、实际 GUI、原生结果及保存冷读 Passed；Standards/Spec 各 0 发现，详见[验收](../validation/agent/acceptance/annotation-ui.md)。用户随后授权更新日常插件：123 个安装成员逐字节一致，日常配置真实标注及冷读 Passed；[全局安装报告](../validation/agent/reports/2026-10-17/annotation-ui-global/acceptance.json)。日常配置 GUI 点击、独立人工/科研接受及未执行的测量编辑 GUI/渲染范围保留 Not Run。

稳定候选及旧包保全见当前交付表；报告/截图仍在 `validation/agent/reports/2026-10-17/annotation-ui/`。权限重试与保全收据集中于 `outputs/runs/annotation-ui-cleanup-20261017/`：`sandbox-datasets.zip` 保存四个创建账户专属 Dataset 目录的 18 个文件，`finish/annotation-ui-ignored.zip` 保存其余 8,851 个忽略文件，配套 JSON 清单逐文件记录原路径和摘要。三套可直接打开的 `.blend + .qcdata` 副本在该批 `projects/{source-native,native,gui}/`，均经日常配置新进程冷读 Passed。原工作树和 `feat/annotation-ui` 分支已正常移除，原注释标签 `archive/2026-10-17/feat/annotation-ui` 身份不变；没有修改 ACL、取得所有权或强制删除。原 `finish-plan-failed.json`、`delivery.json` 保留当时状态，新的结果见[清理验收](../validation/agent/acceptance/annotation-ui-cleanup.md)及本批 `acceptance.json`。重建调用统一入口及 `tools/verify_annotation_dialog.py`。日常更新的旧插件、偏好备份和验证工程仍在 `outputs/runs/annotation-ui-global-20261017/`，更新记录收尾见该目录 `annotation-ui-global-archive.json`，标签 `archive/2026-10-17/chore/annotation-ui-global`。本次清理记录使用标签 `archive/2026-10-17/chore/annotation-ui-cleanup`，收尾收据位于本批 `records/`。未 push。

<a id="annotation-anchor-20261016"></a>
## 圆弧中点引线与创建朝向（2026-10-16）

键角和二面角引线从圆弧精确半角顶点出发，四类标注创建时默认一次朝向场景相机。266 标准库、96 公开科学、真实 GUI、原生几何、渲染、冷读和日常安装/原工程恢复 Passed，独立人工接受 Not Run；详见[验收](../validation/agent/acceptance/annotation-anchor.md)。

最终打开原保存工程 `outputs/projects/sidebar-preserved-20261016/user-session.blend`；原件、配套数据与新增保全副本不变，恢复草稿不作为恢复目标。运行脚本、旧插件/偏好/旧当前 ZIP 和 GUI 工程保留于 `outputs/runs/annotation-anchor-20261016/`；报告及渲染工程位于 `validation/agent/reports/2026-10-16/annotation-anchor/`。该批历史候选仍在 `outputs/candidates/current/annotation-anchor-20261016-r1/`，使用 `tools/build_extension.py` 重建。历史对象未清理。

本地快进、忽略文件保全、正常移除工作树及标签 `archive/2026-10-16/fix/annotation-anchor` 由本批 `worktree-retention.json`、`archive-local.json`、`delivery.json` 定位。不 push。

<a id="sidebar-20261016"></a>
## Sidebar 摘要与整数标注输入（2026-10-16）

Sidebar 收敛到导入导出、只读对象摘要、详情、选择导航和工程维护；计算、视图、空间工具、采样和相机集中到对象属性。摘要按当前活动对象与来源缓存显示原子总数、构型、数量单位及维度，不随 Properties pin 错位。四类标注改为可键入与左右步进的独立整数输入，越界钳制、重复拒绝、批量原子与显式顺序交换均保留；编辑更新实际几何记录。

266 标准库、94 公开科学、原生摘要/几何/上下文、实际 GUI、最终包安装/渲染/移动冷读、全局原工程恢复 Passed。原生非对象 pin、多视图区比较和独立人工/科研签署 Not Run；详细覆盖与测试脚本失败修订见[验收记录](../validation/agent/acceptance/sidebar.md)。十份教程已同步入口，新增一处摘要截图占位。

当前保全工程为 `outputs/projects/sidebar-preserved-20261016/user-session.blend` 及同名 `.qcdata`，全局 GUI 留在此副本；原文件与内容基线不变。验收工程及旧全局插件、偏好、旧当前 ZIP、运行脚本在 `outputs/runs/sidebar-20261016/`；证据在 `validation/agent/reports/2026-10-16/sidebar/`。R1/R2 候选和失败报告均保留，未清理历史对象。重建入口为 `tools/build_extension.py`、`tools/verify_extension.py`、`tools/verify_annotation_geometry.py` 与 `tools/verify_operator_tooltips.py`。

本地整合及四个工作树的保全/正常移除结果由本批 `worktree-retention.json`、`archive-local.json`、`delivery.json` 记录；注释标签采用 `archive/2026-10-16/{feat/sidebar-main,feat/sidebar-summary,fix/sidebar-context,docs/sidebar-sop}`。不 push。

整合提交 `c915649` 的 266 项标准库、94 项 public-core 和当前安装/教程材料检查 Passed。299 个忽略文件已按逐项摘要保存在 `outputs/runs/sidebar-20261016/worktree-evidence/`；四个工作树与分支均正常移除，四个注释标签可从 main 追溯。本批探针源脚本保存在对应工作树 ZIP 的 `outputs/sidebar-summary/`、`outputs/sidebar-context/`；报告中的旧工作树路径为执行时位置。此前 i18n 空目录残留未动。

<a id="annotations-20261016"></a>
## 标注几何、材质与面板提示（2026-10-16）

四类标注支持固定或自定义前缀、中文字体、距离虚线、键角圆弧、二面角投影弧与原子三角面；新建主材质黑色 Metallic=1，平面另用 Alpha=.2 材质。编辑保留用户材质节点，旧标注仅在显式操作时统一材质。“全部朝向相机”限制当前原子视图，面板按用途分组并补齐中英文工具提示。

221 项标准库、92 项公开科学、原生几何与生命周期、XYZ/优化/IRC 更新、工具提示语言组合、真实 GUI、最终候选安装/渲染/冷重开及全局原工程恢复 Passed。Agent 检查不替代独立人工和科研签署。证据位于 `validation/agent/reports/2026-10-16/annotations/`；[验收记录](../validation/agent/acceptance/annotations.md)区分 r1 与 r2，以及每项实际覆盖范围。

用户最新工程与配套数据保存在 `outputs/projects/annotations-preserved-20261016/user-session.blend` 及同名 `.qcdata`，原件摘要未变。四类标注渲染与自包含示例在本批报告的 `gallery-r2/`；界面测试工程在 `outputs/runs/annotations-20261016/gui-evidence-r1/`、`gui-evidence-r2/`，安装与迁移工程在同目录 `extension-r2/`。旧全局插件、偏好、旧当前 ZIP 和本批维护脚本均留在该 runs 目录；两个候选及失败复现记录保留，不执行历史产物清理。重建入口为 `tools/build_extension.py`、`tools/verify_annotation_geometry.py`、`tools/verify_annotation_motion.py`、`tools/render_annotation_gallery.py` 与 `tools/verify_extension.py`。

本地合并提交 `547865b` 的 221 项标准库、92 项 public-core 与工作区材料检查 Passed。四个注释标签 `archive/2026-10-16/{feat/annotations-main,feat/annotations-core,docs/annotations-sop,feat/panel-tooltips}` 保存任务提交；223 个忽略产物已归入 `outputs/runs/annotations-20261016/worktree-evidence/` 并逐文件验证，四个工作树及分支正常移除。该批报告中的 `worktree-retention.json`、`archive-local.json` 和 `delivery.json` 保存清单与收据。此前 i18n 空目录残留未动，未 push。

<a id="i18n-20261015"></a>
## 全界面双语与全局冷重开（2026-10-15）

界面、提示、原生 QC 自定义属性、节点接口和资产目录随 Blender 偏好切换中英文；用户命名、属性键与科学身份保持。SOP 和九专题使用中文（English）及并集、交集、差集术语。

216 项标准库、67 项公开科学、原生双语与生命周期、资产几何、真实 GUI、渲染、中文路径迁移冷读和全局安装冷重开 Passed。逐弹窗穷尽 GUI、独立人工与科研签署 Not Run。详见[验收](../validation/agent/acceptance/i18n.md)及 validation/agent/reports/2026-10-15/i18n/。

用户原会话在 outputs/projects/i18n-preserved-20261015/user-session.blend 及同名 .qcdata；双语测试副本为 user-session-bilingual.blend。旧全局插件、偏好和旧当前 ZIP 备份位于 outputs/runs/i18n-20261015/；两个候选及原报告保留。最终候选渲染/可迁移工程位于该目录 acceptance-r2/，重建入口 tools/build_extension.py 与 tools/verify_extension.py。源码由 archive/2026-10-15/feat/i18n-main 定位，本地整合，不 push 或发布。

本地合并提交 `707a15c`；四个注释归档标签及工作树登记移除完成。三个目录正常移除，`D:\workspace\QCBlender\.worktrees\i18n-docs` 剩余空目录返回 `Permission denied`，原位保留；未修改 ACL 或强制删除。逐文件保全清单 `worktree-retention.json`、原始移除收据 `archive-local.json` 及最终收据 `delivery.json` 位于本批报告目录；目录残留见[任务 06](../.scratch/i18n-20261015/issues/06-cleanup-residue.md)。合并后的当前安装包和教程完整材料检查见 `workspace-final.json`（Passed；允许既有图片占位）。

本地合并提交 `707a15c`；四个注释归档标签及工作树登记移除完成。三个目录正常移除，`D:\workspace\QCBlender\.worktrees\i18n-docs` 剩余空目录返回 `Permission denied`，原位保留；未修改 ACL 或强制删除。逐文件保全清单 `worktree-retention.json`、原始移除收据 `archive-local.json` 及最终收据 `delivery.json` 位于本批报告目录；目录残留见[任务 06](../.scratch/i18n-20261015/issues/06-cleanup-residue.md)。合并后的当前安装包和教程完整材料检查见 `workspace-final.json`（Passed；允许既有图片占位）。

<a id="local-selection-dialog-20261014"></a>
## 局部选择弹窗与全局安装（2026-10-15）

设置按钮明确指定 Replace，避免继承上次 Clear 等立即执行模式。原 PID 13284、未保存 P06-single 的三种记忆模式点击、七种选项与距离控件、4 项原子选择回归 Passed；83 源码、11 个原有 wheel 和 102 个全局安装文件核对 Passed。当前窗口已生效，原工程数据、偏好与节点布局保留。

[任务](../.scratch/local-selection-dialog-20261014/spec.md)和[验收](../validation/agent/acceptance/local-selection-dialog.md)记录范围；证据在 validation/agent/reports/2026-10-14/local-selection-dialog/。旧 ZIP、全局插件与偏好备份、维护脚本在 outputs/runs/local-selection-dialog-20261014/；没有删除旧候选。验证时源码尚未提交，身份记录保留当时基线及文件摘要；完整后台重建、冷重开与独立人工验收 Not Run。

<a id="tutorial-clarity-20261013"></a>
## 教程用途、选项与步骤目录（2026-10-14）

[SOP](../validation/human/SOP.md) 与九专题已审查并补充用途、选项区别和必要示例；79 个原编号步骤均为有名称的三级标题，各文档开头目录覆盖全部二、三级标题。原编号、参数、输入、截图和显式锚点保留；ESP/AIM 改用实际可见的 Record/Match 操作。材料检查继续统计新形式的步骤。本地提交由归档标签 archive/2026-10-14/docs/tutorial-clarity-main 定位，[任务](../.scratch/tutorial-clarity-20261013/spec.md) 记录范围和验收。

证据在 validation/agent/reports/2026-10-13/tutorial-clarity/：structure.json、sop-example.json、examples.json、checker-tests.json、workspace.json、integration.json。结构和原内容边界、实际输入/函数、10 项检查器回归、材料与独立公开副本 Passed。公开副本位于 validation/work/agent/tutorial-clarity-20261013/public-copy/，保留主线与专题完整相对目录；既有图片缺位保持记录。Blender GUI、渲染、独立人工操作及网站构建/部署 Not Run；用户工程、科学输入和安装包未修改。维护脚本及本轮开始前的文档字节保存在 outputs/runs/tutorial-clarity-20261013/。

<a id="local-selection-modes-20261013"></a>
## 局部选择教程（2026-10-13）

[分子与 XYZ](../validation/human/topics/01-molecule-xyz.md) 包含七种 Mode 的定义与 P06 五步连续演示；[任务](../.scratch/local-selection-modes-20261013/spec.md) 记录范围与验收。实际坐标与当前选择函数、文档边界和材料检查 Passed，Blender GUI 与独立人工操作 Not Run。证据保存在 validation/agent/reports/2026-10-13/local-selection-modes/ 的 examples.json 与 workspace-accepted.json；维护脚本在 outputs/runs/local-selection-modes-20261013/。本次说明与后续教程整合在同一本地提交中，由归档标签 archive/2026-10-14/docs/tutorial-clarity-main 定位；未产生或删除工程及科学输入。

<a id="tutorial-flow-20261011"></a>
## 教程步骤衔接与一致性（2026-10-11）

[SOP](../validation/human/SOP.md) 与九专题集中共用的新工程、对象选择、属性刷新、导出和另存说明；各专题补齐前置对象、可见状态、弹窗确认、筛选定位与节点连线。79 项编号操作保留，科学参数与输入不变。

实现提交 `099a3f0`；原参数表与数字、输入链接、26 个图片引用和 4 张已有图片检查 Passed，主检出实际公开材料检查 Passed。Standards/Spec 各 0 发现。仍有 22 张待补图片；科学测试、Blender 实际操作和网站构建 Not Run。

证据在 `validation/agent/reports/2026-10-11/tutorial-flow/`：`sources.json`、`validation.json`、`workspace.json`、`review.json`、`closing.json`。辅助脚本保留于 `outputs/runs/tutorial-flow-20261011/`；用户工程、现有导出与科学输入未修改。三个本地归档标签为 `archive/2026-10-11/docs/tutorial-flow-20261011`、`archive/2026-10-11/docs/tutorial-flow-a-20261011` 和 `archive/2026-10-11/docs/tutorial-flow-b-20261011`。

<a id="tutorial-terms-20261011"></a>
## 教程术语与控件说明（2026-10-11）

[SOP](../validation/human/SOP.md) 与九专题在正文首次使用处解释初学者可能不熟悉的术语、参数和控件。共用界面说明集中在主线，专题解释独有含义与用途；原操作、输入、参数和图片引用保留。

实现提交 `87da946`；79 项编号操作逐行、表格原值、粗体参数、输入链接、26 个图片引用与 4 张原图检查 Passed，实际公开材料检查 Passed。Standards/Spec 各 0 发现。仍有 22 张待补图片；科学测试、Blender 操作和网站构建 Not Run。

证据在 `validation/agent/reports/2026-10-11/tutorial-terms/`：`sources.json`、`workspace-accepted.json`、`validation-accepted.json`、`review.json`、`closing.json`。辅助脚本保留于 `outputs/runs/tutorial-terms-20261011/`；用户工程、现有导出与科学输入未修改。三个本地归档标签为 `archive/2026-10-11/docs/tutorial-terms-20261011`、`archive/2026-10-11/docs/tutorial-terms-a-20261011` 和 `archive/2026-10-11/docs/tutorial-terms-b-20261011`。

<a id="tutorial-output-purpose-20261011"></a>
## 教程产物用途说明（2026-10-11）

[SOP 导出与保存步骤](../validation/human/SOP.md#export)解释参数摘要、结构化记录、数值表、图片和自包含工程的用途与保留方法。九个专题均已检查，七页补充分析记录对象和文件用途；ESP 面积对象按当前实现使用 `QC ESP area data`。

实现提交 `30046ac`；实际材料检查、79 项操作与科学参数、26 个图片引用和 4 张原图字节核对 Passed。尚缺的 22 张图片由操作者补充；本批未重新执行完整图片门禁。Standards/Spec 各 0 发现，科学测试、Blender 操作及网站构建 Not Run。

证据在 `validation/agent/reports/2026-10-11/tutorial-output-purpose/`：`workspace.json`、`validation.json`、`review.json` 和 `closing.json`。辅助脚本保留于 `outputs/runs/tutorial-output-purpose-20261011/`，用户工程和导出文件未修改。归档标签为 `archive/2026-10-11/docs/tutorial-output-purpose-20261011` 与 `archive/2026-10-11/docs/tutorial-topic-outputs-20261011`。

<a id="tutorial-screenshots-20261011"></a>
## 当前教程截图（2026-10-11）

人工截图采用 `Pxx-内容.png`，前缀沿用章节实际案例编号。主线现有 `P01-install.png`、`P01-orbital.png`、`P01-summary.png` 位于 `validation/human/screenshots/`，渲染成品仍在 `validation/human/renders/P01-mo.png`。共 26 个图片引用，已有 4 张、待补 22 张；保存重开等操作和原参数保留。具体范围见[验证记录](../validation/agent/acceptance/tutorial-screenshots-20261011.md)。

| 保留对象 | 当前入口 |
| --- | --- |
| 逐图决策、名称映射和原件摘要 | `validation/agent/reports/2026-10-11/tutorial-screenshots/image-plan.json`、`preservation.json` |
| 实际材料与图片检查 | 同批 `workspace.json`、`images-required.json`、`validation.json`；30 份公开输入与独立副本 Passed，完整图片状态 Failed |
| 原始图片和操作脚本 | `outputs/runs/tutorial-screenshots-20261011/`；`before/` 保留 4 张原图 |
| 独立教程副本 | `validation/work/agent/tutorial-screenshots-20261011/public-copy/` |
| 评审、最终检查与归档 | 同批 `review.json`、`final-check.json`、`closing.json`；标签 `archive/2026-10-11/docs/tutorial-screenshots-20261011` 和 `archive/2026-10-11/docs/tutorial-topic-images-20261011` |

用户工程、科学输入和历史报告保持原位；旧报告中的图片名按本批 `image-plan.json` 定位。科学测试、Blender 操作及网站构建/部署 Not Run。

<a id="tutorial-assets-20261011"></a>
## 教程图片与工作目录（2026-10-11）

教程文字、两张界面截图和 P01 渲染成品已纳入 Git；SOP 直接引用 `validation/human/renders/P01-mo.png`。用户工程及自动备份现位于 `validation/work/human/P01/未命名.blend`、`未命名.blend1`，原始字节保留。该批目录职责、打包范围、实际检查和限制见[验证记录](../validation/agent/acceptance/tutorial-assets-20261011.md)；当前图片名称与数量以上面的[截图记录](#tutorial-screenshots-20261011)为准。

| 保留对象 | 位置与作用 |
| --- | --- |
| 保全和迁移收据 | `validation/agent/reports/2026-10-11/tutorial-assets/` 下的 `preservation.json`、`project-move.json`、`backup-move.json`、`integration.json` |
| 材料和图片检查 | 同批 `workspace.json`、`images-required.json`、`validation.json`；9 项回归、30 份公开输入及独立材料副本 Passed；完整图片状态 Failed，待补 28 张 |
| 原始文件及迁移脚本 | `outputs/runs/tutorial-assets-20261011/`；`before/` 保留文档、三张图片、工程和自动备份 |
| 独立公开副本 | `validation/work/agent/tutorial-assets-20261011/public-copy/`，用于相对链接和公开资源检查 |
| 最终状态和本地归档 | 同批 `final-state.json`、`closing.json`；两个注释标签 `archive/2026-10-11/docs/tutorial-assets-20261011`、`archive/2026-10-11/test/tutorial-assets-20261011` |

仅移除核实为空的 `validation/human/P01/`、`validation/human/exports/`、`validation/data-export/`。人工后续所需的 P01、P03、exports、移动案例目录已就绪。已有 Agent 工程和历史证据保持原位；新批次使用 `validation/work/agent/<批次>/`。本批 Blender 运行、工程冷重开及网站构建/部署 Not Run。

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
| `modules/build-site/` | 现有锁定构建包；搬移前后的逐文件身份见本次迁移映射 |
| `modules/science/` | 现用科学环境，版本不变 |
| `modules/wheels/`、`modules/backend-wheel.json` | 11 个锁定且逐份核验的 wheel；统一当前打包入口 |
| `modules/sources/gbasis/`、`modules/sources/iodata/`、`modules/sources/qcint/` | GBasis、IOData、历史 qcint 源码 ZIP 各保留一份；原来源记录沿用，本次映射保存原路径与摘要 |
| `modules/licenses/` | 完整历史许可及退役环境、归档中需要保留的许可文本 |
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
