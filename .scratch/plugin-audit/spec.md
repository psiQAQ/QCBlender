# QCBlender 完成度与参考实现调研

Triage: ready-for-agent
Status: resolved
Type: research

## 目标

以 main `96f9c7ea0c41c63f8b689a766ffafeb14aa3bb48` 为固定基线，按首版可靠交付优先，审计完成度、复现缺陷并全面比较已有参考项目。产品源码、公共 API、数据格式与依赖保持不变。

## 验收

- 核对候选与证据身份，区分实现、技术验证、真实输入、GUI、独立人工验收与发布。
- 重跑科学测试及相关检查；验证动态构型关联、Gaussian 分段、NOCV 冲突、共享 mesh 切步、连续导入、保存与移动冷重开。
- 对 MolecularNodes、GXNU-MolStudio、VTK 及 Multiwfn/VMD/GaussianView 资料按固定版本比较，区分已采用与新增机会。
- 报告提供缺陷触发条件、影响、代码位置、证据与修复方向；功能建议提供场景、成本、依赖和验收。
- Passed / Failed / Not Run 如实记录；不替独立用户或科研人员签署。

## 产物

- `docs/research/qcblender-completion-audit-2026-10-03.md`
- 主仓库 `outputs/evidence/2026-10-03/plugin-audit/`；工作文件位于 `outputs/runs/plugin-audit/1/`。
- `issues/01-research.md` 记录当前执行状态与最终证据。

## Comments

- 用户已批准完整调研计划：测试加关键 Blender 场景，参考软件以固定源码及官方资料比较为主；本任务不实施缺陷修复或新功能。

## Answer

调研交付完成。完成矩阵、四类未修复缺陷、六参考对象十维比较及五项功能建议见 `docs/research/qcblender-completion-audit-2026-10-03.md`；执行及保全证据见主仓 `outputs/evidence/2026-10-03/plugin-audit/`。82科学测试、30相关单测Passed，1项Windows跳过；两类P1实际GUI复现，综合及缺陷工程迁移后冷读Passed。独立科研签署与发布Not Run。任务resolved只表示调研完成，不表示产品缺陷已修复或发布完成。
