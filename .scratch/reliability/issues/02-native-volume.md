# 02 原生体场可读性

Triage: ready-for-agent
Status: claimed
Blocked by: none

## 范围与验收

遵循spec第一批2。相同VDB长路径加载失败、短路径成功；原生检查在场景写入/保存发布/重新绑定前运行，验证必要网格，错误保留具体路径与原生原因。覆盖中文/长路径、缺失损坏VDB、无权限/保存失败，失败保留原绑定和工程，临时datablock零泄漏。主Agent运行真实Blender与冷读。

## Comments

2026-10-05：领取。文件归属为原生VDB检查helper、blender/views.py、blender/project.py及专属脚本，不修改科学data.py、jobs/ui和外部导入文件。
