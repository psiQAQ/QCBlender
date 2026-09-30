# 07 Blender 验证配置隔离

Triage: ready-for-agent
Status: resolved
Blocked by: none

## 验收

开发说明显式创建本批 CONFIG/EXTENSIONS 目录；安装检查在写入前核对实际目录与环境变量，缺少隔离时失败。本批原生检查不会写入用户默认配置。记录首轮意外配置写入及保护核对；无原始备份时不以其他配置覆盖。

## Comments

- 2026-09-30：节点首轮临时安装脚本调用 save_userpref，将偏好写入默认 config；日志位于 outputs/runs/public-tutorial/nodes/install.stdout.log。补充本轮验证所需隔离修正，产品行为和依赖保持现状。
- 2026-09-30：主 Agent 领取；先修正命令前置与安装 guard，再验证缺少隔离的拒绝路径及本批安装路径。

## Answer

Passed：原生 Blender 负向检查在缺少隔离变量时安装前退出；正向检查确认 CONFIG/EXTENSIONS/DATAFILES 位于本批目录，前后默认偏好 SHA-256 一致。证据：outputs/evidence/2026-09-30/public-tutorial/isolation/{negative,positive}.json 与对应日志。同批候选安装继续由05验证。

首轮节点临时脚本曾写入默认 userpref.blend；原始备份未找到，未自动恢复。用户活动工程的独立旧配置目录未被改动。完整偏好副本因自动审批隐私风险拒绝，改为只记录摘要核对。
