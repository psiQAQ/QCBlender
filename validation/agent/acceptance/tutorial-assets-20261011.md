# 教程素材与工作目录验证（2026-10-11）

本批验证对象为 `02674aa50ef4f9ac0c029f224feaacad5c6618e4` 的教程和检查器，基点为 `7669a07816258c9810ccfd54e17ff0b222b396c9`。主检出使用现有公开输入和当前安装包执行检查；产品源码、科学输入与候选未变。文档入口见 [validation](../../README.md)，现存产物由 [ARTIFACTS](../../../docs/ARTIFACTS.md#tutorial-assets-20261011) 路由。

## 当前布局

| 内容 | 位置 |
| --- | --- |
| 主流程、专题 | `validation/human/SOP.md`、`validation/human/topics/` |
| 两张已提供界面截图 | `validation/human/screenshots/01-install.png`、`02-orbital.png` |
| 已提供渲染成品 | `validation/human/renders/P01-mo.png`；SOP 直接引用 |
| 用户工程及自动备份 | `validation/work/human/P01/未命名.blend`、`未命名.blend1` |
| 人工后续工作目录 | `validation/work/human/P01/`、`P03/`、`exports/`、`移动案例/` |
| 独立公开材料副本 | `validation/work/agent/tutorial-assets-20261011/public-copy/` |

三张 PNG 均在 Git 中；工程、自动备份与工作副本由 Git 忽略。教程保留 31 个图片引用，已有 3 张，其余 28 张由实际操作者补入 `human/screenshots/`。目录已就绪，不用复制同一张渲染图来满足另一个截图名称。

## 实际检查

报告根目录为 `validation/agent/reports/2026-10-11/tutorial-assets/`。

| 检查 | 结果 | 证据与范围 |
| --- | --- | --- |
| 定向回归 | Passed | `unit-tests.log`；9 项测试，覆盖图片统计、工作目录越界、未知文件、空工作目录、占位与严格门禁、复制前拒绝 |
| 主检出材料和独立副本 | Passed | `workspace.json`；30 份公开输入摘要、P04 相对输入、当前 ZIP 摘要/CRC、公开链接与图片路径 |
| 完整图片准备状态 | Failed | `images-required.json`；完整图片门禁准确列出 28 张缺图；这是当前材料的实际未完成状态 |
| 缺图拒绝行为 | Passed | `validation.json`；退出码为 1，错误中的缺图集合与准备报告完全一致 |
| 图片及工程保全 | Passed | `preservation.json`、`project-move.json`、`backup-move.json`、`integration.json`；复制后核对 SHA-256，再移除对应旧位置 |
| Git 跟踪、目录和最终字节检查 | Passed | `final-state.json`；三张 PNG 入库，工程与自动备份仍与保全记录一致 |
| Python 语法及 diff | Passed | `validation.json`、`diff-check.log` |
| Standards 静态评审 | Passed | `review.json`；0 项发现 |
| Spec 静态评审 | Passed | `review.json`；0 项发现 |
| 本批 Blender 操作、工程冷重开 | Not Run | 仅迁移用户确认未使用的工程及其备份；不据此声称工程自包含或运行可用 |
| 网站构建、GitHub Pages 部署 | Not Run | 本批整理仓库内教程源文件和相对资源 |

检查命令和缺图清单见 `validation.json`，重跑方法见 [Agent 流程](../README.md#教程材料与完整图片检查)。公开副本只包含 `human/`、`shared/data/public/`、`shared/install/`；缺少图片的准备检查通过，不代表图片齐全或网站已可发布。

## 保留与本地归档

原始文档修改、三张图片、工程及自动备份保存在 `outputs/runs/tutorial-assets-20261011/before/`。仅移除已验证为空的 `validation/human/P01/`、`validation/human/exports/` 和 `validation/data-export/`。已有 Agent 批次原位保留；新批次使用 `validation/work/agent/<批次>/`。

最终提交、两个注释归档标签和工作树移除状态记录在本批 `closing.json`。任务为 [.scratch/tutorial-assets-20261011](../../../.scratch/tutorial-assets-20261011/spec.md)，本地归档标签为 `archive/2026-10-11/docs/tutorial-assets-20261011` 与 `archive/2026-10-11/test/tutorial-assets-20261011`。
