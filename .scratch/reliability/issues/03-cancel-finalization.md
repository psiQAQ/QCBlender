# 03 异步取消收尾

Triage: ready-for-agent
Status: claimed
Blocked by: none

## 范围与验收

遵循spec第一批3。先受控复现terminate失败/wait超时遮盖原错误及中断收尾；普通ESC和真实导出仍通过。保留进程PID/Job目录和原错误，退出未确认不丢失追踪、不删staging；一个任务失败不阻断其余收尾；timer无残留。替身仅隔离进程控制边界，真实集成由主Agent验证。

## Comments

2026-10-05：领取。文件归属为blender/jobs.py、blender/ui.py、blender/data_export.py、qcblender/__init__.py必要收尾及专属测试脚本；不修改外部导入、views/project。

2026-10-05：受控失败复现已执行，初始10项测试全部ERROR：terminate拒绝/wait超时逃逸，modal原错误被取消错误覆盖，批量收尾被中断。替身边界为进程控制和bpy生命周期，不作为真实worker或界面集成成功证据。

## Answer

实现已完成，Status保持claimed，等待主Agent的已安装候选和实际界面验证。

- Passed：`python -B -m unittest discover -s tests -p test_cancel_finalization.py -v`，16项定向测试通过。覆盖退出已确认/未确认、terminate拒绝、wait超时、poll异常、清理失败可重试、原始科学/进程错误与取消错误同时报告、Job释放后的持续追踪、多任务独立收尾与timer移除。日志为本工作树`outputs/tests/cancel-finalization-green.txt`。
- Passed：五个本次Python文件的内存compile检查及`git diff --check`；既有Python文件保持LF、UTF-8无BOM。
- 实现：活动Job使用强引用；`cancel()`返回请求状态、退出状态、PID、任务目录、退出码和错误，保存`cancellation.json`。未确认退出或导出清理未完成时保留Job。收尾先移除timer，原任务错误先报告，取消错误另报告；批量收尾逐个处理并记录异常。导出清理回调捕获路径/token，不引用退出modal后的RNA operator；确认退出才清理staging。
- Not Run：真实Blender worker/CSV导出取消、原生timer及实际GUI ESC。原生脚本`tools/verify_cancel_finalization_blender.py`交主Agent串行执行，包含真实P03 CSV staging取消及进程控制故障注入，并显式区分脚本分派ESC、受控process边界与人工操作。科学/视觉综合回归由主Agent执行。

原生脚本在已安装本批候选、插件没有既有Job/modal任务的隔离Blender中执行：`--python tools/verify_cancel_finalization_blender.py -- --output-dir <项目内证据目录> --reference-root D:/workspace/QCBlender`。每次生成唯一证据子目录；输出`cancel-finalization.json`。控制故障仅注入Popen控制返回，实际worker句柄恢复后再确认退出；不会按进程名终止其他进程。独立人工复做及科研签署Not Run。
