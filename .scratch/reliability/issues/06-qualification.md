# 06 综合验收与本地交付

Triage: ready-for-agent
Status: claimed
Blocked by: 01, 02, 03, 04, 05

## 范围与验收

科学回归、相关原生operator及真实GUI、Undo/Redo、六视觉基准、保存/移动冷读、Standards/Spec审查。候选/证据绑定固定提交、产品树、SHA-256；更新相关用户说明、ARTIFACTS和CHANGELOG。按项目本地流程归档，独立人工签署Not Run；不push/发布/强制清理。

## Comments

2026-10-05：01至05技术前置已resolved；性能增益未达门槛，按规格停止扩大优化。开始以固定a3ed826产品及最终候选运行科学回归、相关单测、原生operator、六视觉、实际GUI与保存/移动冷读；独立人工/科研签署继续Not Run。

2026-10-05技术资格：固定a3ed826候选完成105科学测试、40单测、15项原生体场检查、15项IGMH/静态参考及六视觉场景；36份最终候选报告绑定源码/产品树/ZIP/安装副本和11wheels通过。GUI声明导入、Undo/Redo、动态参考禁用、运行中ESP取消、损坏VDB拒绝、保存及原地/中文移动冷读Passed。GUI CSV在Esc前完成，运行中CSV GUI取消Not Run；原生worker取消另有报告。自然权限拒绝、独立使用者/科研签署Not Run。当前等待本地ff-only、归档与清理收据，技术入口为docs/acceptance/reliability-validation.json。
