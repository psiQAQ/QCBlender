# 03 异步取消收尾

Triage: ready-for-agent
Status: claimed
Blocked by: none

## 范围与验收

遵循spec第一批3。先受控复现terminate失败/wait超时遮盖原错误及中断收尾；普通ESC和真实导出仍通过。保留进程PID/Job目录和原错误，退出未确认不丢失追踪、不删staging；一个任务失败不阻断其余收尾；timer无残留。替身仅隔离进程控制边界，真实集成由主Agent验证。

## Comments

2026-10-05：领取。文件归属为blender/jobs.py、blender/ui.py、blender/data_export.py、qcblender/__init__.py必要收尾及专属测试脚本；不修改外部导入、views/project。
