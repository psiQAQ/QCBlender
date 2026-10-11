# 教程素材与工作目录整理

Triage: ready-for-agent
Status: claimed
Baseline: main@7669a07816258c9810ccfd54e17ff0b222b396c9
Date: 2026-10-11

## 目标

人工 SOP 及其引用图片作为仓库和后续文档网站的教程源文件维护。每张图片只有一个引用位置：界面截图在 `validation/human/screenshots/`，渲染成品在 `validation/human/renders/`；这两类图片均不受 Git 忽略规则排除。工程、配套科学数据和导出文件保存在被忽略的 `validation/work/human/`。

## 范围

- 将用户实际生成的 P01 渲染图迁至 `human/renders/P01-mo.png`，与两张现有界面截图一起入库；同步 SOP、打包说明及目录用途。31 个图片引用中尚未补入的图片继续明确作为占位，不生成替代图片。
- 用户已确认 `human/未命名.blend` 未被使用，允许迁至 `work/human/P01/未命名.blend`。先保全和核对 SHA-256，再迁移；只移除经再次核实为空的 `human/P01/`、`human/exports/`、`validation/data-export/`。
- 保持公开包范围为 `human/`、`shared/data/public/`、`shared/install/`。检查器拒绝教程内的工程、导出和未知文件，拒绝图片引用工作目录；准备阶段允许图片占位，完整图片门禁要求引用的图片全部存在。
- 新 Agent 验证批次使用 `validation/work/agent/<批次>/`；现有工作批次和 `outputs/runs/` 原位保留，通过 ARTIFACTS 查找，不批量迁移历史材料。

## 验收与边界

用户文件迁移前后字节相同；现有三张 PNG 均纳入 Git；准备阶段及独立材料副本的资源、相对链接、图片引用校验通过；缺图时完整图片门禁准确拒绝。只验证本批文件布局和检查工具，不修改产品源码、安装包、依赖或科学输入，不操作用户 Blender 会话，不推送或部署网站。

## 任务

01 文档与素材整理；02 检查器及针对性回归；03 主检出整合、可移植验证、保全与本地归档。
