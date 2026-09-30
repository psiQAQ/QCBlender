# [P2] 重写 README：用户优先，开发者文档分类入口置于末尾

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 05

## 目标

让首次访问仓库的量子化学/计算化学用户能回答：QCBlender 做什么、当前能用哪些输入完成哪些任务、需要什么 Blender/平台、安装包是否已经可取得、如何完成第一个操作、有哪些限制以及工程如何保存。

本任务只重写 README 及必要链接，不为文案新增功能、发布版本、生成演示工程或改变支持范围。遵守 [总规格](../spec.md)。

## 当前问题与事实边界

- [README.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/README.md) 将用户操作、源码借鉴、设计路线、依赖研究和开发工具并列，用户入口不够集中。
- README 使用开发机路径 `outputs/dist/qcblender-0.0.1.zip`；2026-09-30 检查 GitHub Releases API 返回空列表。执行时重新核查实际发布状态，不把本地构建产物写成用户可以直接下载的附件。
- [qcblender/blender_manifest.toml](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender_manifest.toml) 声明版本 `0.0.1`、`windows-x64`，Blender 最低 `5.1.1`、最高边界 `5.2.0`；[docs/VALIDATION.md](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/docs/VALIDATION.md) 的实际验证针对 Blender 5.1.1。清楚区分清单声明和实际验证，不擅自扩大版本范围。
- 技术验收、独立用户验收、公开发布是三种不同状态；最新有效信息由任务 05 整理后的权威文档提供。

## 建议内容顺序

1. 一段定位：在 Blender 中可视化已有量子化学结果，并对支持的波函数进行场求值；避免让用户误认为它是通用 Gaussian 替代计算程序。
2. 用户任务表：轨道、电子/自旋密度、ESP 映射/切片、结构/原子性质/振动，以及经过核查的扩展结果显示；写输入与结果，不堆 Python 模块名。
3. 兼容范围与当前可用状态：操作系统、已测 Blender 版本、输入格式、内置求值边界。
4. 获取与安装：仅指向真实可取得的扩展包；尚未公开发布就明确说明，开发构建指向末尾文档，不能将源码 ZIP 当成可安装扩展。
5. 一个最小工作流，尽量控制在五步：获得合格安装包并启用、导入 FCHK、选择已有入口生成轨道场、调整等值面/材质、保存可迁移工程；具体名称按当前 UI 验证，不重新发明界面操作。
6. 保存与限制：说明 `.blend + .qcdata` 配套；`.chk` 需要已有 Gaussian 的 formchk 导出；不支持/未验证项目清楚列出，详解链接当前指南。
7. 最后才放“开发者文档”，按类别链接现有且已整理的文档。

## 开发者末尾清单

| 类别 | 应指向的内容 |
| --- | --- |
| 构建与验证 | 当前开发构建说明、安装与数值/Blender 验证入口 |
| 架构与数据 | 当前架构、数据契约、Geometry Nodes 契约、有效 ADR |
| 科学依据与支持范围 | 当前验证矩阵、输入/能量语义和必要科学参考 |
| 样本与复现 | 当前样本来源目录、SOP 和可复建示例 |
| 开发约定与问题处理 | AGENTS、有效任务规则、通用开发注意事项 |
| 许可证与变更记录 | LICENSE、THIRD_PARTY、CHANGELOG |

路径以任务 05 的最终文件为准。每个链接给简短用途说明；不把研究报告、候选验收流水账和脚本列表放在 README 用户首屏。

## 验收

- [x] 首屏说明产品定位、用户任务和当前发布/获取状态，而不是开发路线。
- [x] 每项能力与当前实现及验证边界一致；外部分析结果显示不写成插件内置计算，未验证功能不包装成正式支持。
- [x] 安装入口真实可用或明确尚未发布；没有开发机绝对路径、假下载链接或“下载源码 ZIP 即可安装”的误导。
- [x] 已有合格候选可用于验证时，最小工作流在指定 Blender 环境复做；缺少环境/候选时明确 Not Run，不为了完成 README 擅自发版。
- [x] 保存方式与关键科学限制保留，用户不需要先读开发文档理解产品。
- [x] 开发者分类清单位于最后，所有内部链接和锚点有效。
- [x] README 不复制整本用户手册，不保留旧阶段/旧方案的清理过程叙述，不改动运行代码。

## Comments

公开发布状态以实施时的 API 检查为准，并在 README 标明核查日期。

- 2026-09-30：05 已 resolved；领取 README 用户入口整理，实时核查 Releases 并对照本次新包核心操作证据。

- 2026-09-30：README 按定位/任务、兼容与获取、五步轨道操作、保存限制、末尾开发分类导航完成。`gh api repos/psiQAQ/QCBlender/releases` 成功返回 `[]`；原响应保存在 `outputs/repository-cleanup/releases.json`。网页工具不可达与 PowerShell HTTPS 认证失败没有当作“无发布”的证据。
- 验证：工作流按钮逐一核对 `editor_ui.py`、`ui.py`、`project.py`。同一最终 ZIP 的 `verify_extension.py` 实际安装、FCHK worker 导入/MO 求值、阈值/相位、原生渲染、保存与原地/移动冷重开 Passed，见 03 及 final 报告。README 的界面导航静态对照通过；此次未额外执行人工逐次点击，GUI/独立人工复做保留 Not Run。
- 最终链接/空白与保护检查 Passed：115 份 Markdown、277 个内部链接；92 个受保护跟踪文件内容未变，主检出无跟踪改动、三个 gitlink 不变、无暂存或新提交。证据 `outputs/repository-cleanup/final-checks.json`；任务收尾后的检查计数以最终 `links.json` 为准。

## Answer

README 已面向用户重写；不提供本地路径作为公开下载，不扩大平台/科学范围，不把外部分析写成内置计算。安装依赖、五步操作、配套保存及关键限制均有明确说明，开发入口集中在末尾六类。

产品源码与 03 最终候选保持相同摘要，README 与文档修订没有引入功能变化。独立人工验收、完整历史 SOP 与发布不因本次清理变更状态。

## Standards

并行只读评审最初发现 1 项：DEVELOPMENT 固定 QA 目录可能覆盖前批证据。已改为本批短目录 `$batch/qa`，明确新批次使用未占用目录；复核 Passed，剩余 0 项。

## Spec

并行只读评审最初发现 2 项：数据契约的网格层级、历史复跑中的三个有效文档链接。已对齐平铺 fields 元数据并恢复直接相对链接；复核 Passed，剩余 0 项。评审未代替运行检查或人工签署。
