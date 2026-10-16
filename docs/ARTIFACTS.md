# 产物查找入口

更新：2026-10-16。本页路由现存产物、历史摘要、重建方法和剩余限制。任务状态在 `.scratch/`，开发步骤见 [DEVELOPMENT](DEVELOPMENT.md)，清理边界见[维护规则](agents/storage-maintenance.md)。

## 当前交付

开发流程工具正在验收：[入口](agents/development-workflow.md)、[当前结果](../validation/agent/acceptance/dev-workflow.md)，日志与全局规则备份在 `outputs/runs/dev-workflow-20261016/`。真实 MCP、构建安装和原工程恢复尚未执行；当前有效插件仍为下列圆弧批候选。

从 [validation](../validation/README.md) 查找当前教程、输入和校验材料；人工入口为 [SOP](../validation/human/SOP.md)。主线 15 步、9 个按需专题，截图由实际操作者按名称补入。

| 内容 | 当前入口 |
| --- | --- |
| 教程与打包 | `validation/human/`；[材料打包](../validation/README.md#人工完成后的打包) |
| 教程图片和人工工程 | `validation/human/screenshots/`、`validation/human/renders/` 随文档入库；工程在 `validation/work/human/`；[当前截图](#tutorial-screenshots-20261011) |
| 公开、本地及回归输入 | [shared/data](../validation/shared/data/README.md)；当前位置与旧路径由 `migration-map.json` 定位 |
| 当前安装包 | `validation/shared/install/qcblender-0.1.0.zip`；50,940,463 字节，SHA-256 `b134cc2f5faaf367a193dbfbc93f801d6b748d27fbdc6b27a186c27530ed6775` |
| 当前候选及验证 | `outputs/candidates/current/annotation-anchor-20261016-r1/`；源码 `b02c9fa`，完整双语资产构建；[身份记录](../validation/agent/current-install.json)、[本次验证](../validation/agent/acceptance/annotation-anchor.md) |
| 冻结公开样本 | `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip`；冻结清单位于 `validation/agent/v1-acceptance/tutorial-samples.json` |
| 校验流程与结果 | [Agent 流程](../validation/agent/README.md)、[当前与历史验证](../validation/agent/VALIDATION.md)；主干维护及历史结果见下文 |

教程现有 27 个图片引用，已提供 4 张；完整图片检查因缺少 23 张截图为 Failed。截图采用 Pxx 案例前缀，当前路径见[截图记录](#tutorial-screenshots-20261011)。完整独立用户操作、checkpoint 复算和科研签署保持各自的 Not Run 状态。当前产物查找以本页为准；旧文档中的 outputs 路径表示当时身份，其实际可用性由本次删除收据确定。

<a id="annotation-anchor-20261016"></a>
## 圆弧中点引线与创建朝向（2026-10-16）

键角和二面角引线从圆弧精确半角顶点出发，四类标注创建时默认一次朝向场景相机。266 标准库、96 公开科学、真实 GUI、原生几何、渲染、冷读和日常安装/原工程恢复 Passed，独立人工接受 Not Run；详见[验收](../validation/agent/acceptance/annotation-anchor.md)。

最终打开原保存工程 `outputs/projects/sidebar-preserved-20261016/user-session.blend`；原件、配套数据与新增保全副本不变，恢复草稿不作为恢复目标。运行脚本、旧插件/偏好/旧当前 ZIP 和 GUI 工程保留于 `outputs/runs/annotation-anchor-20261016/`；报告及渲染工程位于 `validation/agent/reports/2026-10-16/annotation-anchor/`。候选由上表定位，使用 `tools/build_extension.py` 重建。历史对象未清理。

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
