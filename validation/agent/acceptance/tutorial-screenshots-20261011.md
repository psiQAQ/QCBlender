# 教程截图与案例命名（2026-10-11）

验证对象：`ff35ad9929aae8ebe32e54cabe25ae95087e07ce`，基点：`9187875d8413342293add5b19265cc18b80b6df1`。当前图片与入口由 [ARTIFACTS](../../../docs/ARTIFACTS.md#tutorial-screenshots-20261011) 路由。

## 当前图片要求

主线与九专题共 26 个图片引用：25 张界面截图和 1 张渲染图。截图均采用 `Pxx-内容.png`，按对应章节的实际案例编号命名；提示与引用一一对应。案例分工见 [validation](../../README.md#目录用途)。79 个操作步骤及原有粗体参数保持一致。

当前 4 张图片均入库，字节与用户原件相同：

- `validation/human/screenshots/P01-install.png`：安装入口及科学环境状态。
- `validation/human/screenshots/P01-orbital.png`：轨道视图与显示参数。
- `validation/human/screenshots/P01-summary.png`：导出对话框；对应主线第 10 步。
- `validation/human/renders/P01-mo.png`：轨道渲染成品，直接引用。

其余 22 张截图由实际操作者按步骤补入 `human/screenshots/`。保留的图片用于呈现独有控件、操作入口或科学视觉结果；重复确认由步骤文字表达。

## 实际检查

证据根目录为 `validation/agent/reports/2026-10-11/tutorial-screenshots/`。

| 检查 | 状态 | 范围与证据 |
| --- | --- | --- |
| 图片要求、命名及操作保留 | Passed | `image-plan.json`：31 个原引用逐项审查，精简 5 个占位要求；剩余 26 个名称唯一、保存提示与引用匹配；79 步及粗体参数不变 |
| 现有图片保全与 Git | Passed | `preservation.json`、`integration.json`、`validation.json`：4 张图片 SHA-256 一致，3 张截图使用 P01 名称；没有丢弃已有图片 |
| 主检出与独立材料副本 | Passed | `workspace.json`：30 份公开输入、P04 相对输入、安装 ZIP、公开链接及图片引用；副本位于 `validation/work/agent/tutorial-screenshots-20261011/public-copy/` |
| 完整图片准备状态 | Failed | `images-required.json`：缺少 22 张截图，完整图片门禁退出码 1；缺图集合与准备报告一致 |
| Standards / Spec 评审 | Passed | `review.json`：两轴均为 0 项发现；另检查了摘要导出图的实际内容 |
| 维护文档链接及 diff | Passed | `final-check.json`，包括产物路由与当前验收入口 |
| 科学测试、Blender 操作 | Not Run | 本次仅修改教程和图片命名 |
| 网站构建、部署 | Not Run | 当前为本地教程源文件整理 |

原始图片保存在 `outputs/runs/tutorial-screenshots-20261011/before/`。逐图决策和新旧名称由本批 `image-plan.json` 记录；演进说明见 [CHANGELOG](../../../docs/CHANGELOG.md)。重跑材料检查采用 [Agent 流程](../README.md#教程材料与完整图片检查)，使用新报告路径。

任务状态见 [.scratch/tutorial-screenshots-20261011](../../../.scratch/tutorial-screenshots-20261011/spec.md)。最终提交、两个注释归档标签及工作树移除状态记录在本批 `closing.json`。
