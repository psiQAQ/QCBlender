# 03 异步取消收尾

Triage: ready-for-agent
Status: claimed
Blocked by: none

## 范围与验收

遵循spec第一批3。先受控复现terminate失败/wait超时遮盖原错误及中断收尾；普通ESC和真实导出仍通过。保留进程PID/Job目录和原错误，退出未确认不丢失追踪、不删staging；一个任务失败不阻断其余收尾；timer无残留。替身仅隔离进程控制边界，真实集成由主Agent验证。

## Comments

2026-10-05：领取。文件归属为blender/jobs.py、blender/ui.py、blender/data_export.py、qcblender/__init__.py必要收尾及专属测试脚本；不修改外部导入、views/project。

2026-10-05：受控失败复现已执行，初始10项测试全部ERROR：terminate拒绝/wait超时逃逸，modal原错误被取消错误覆盖，批量收尾被中断。替身边界为进程控制和bpy生命周期，不作为真实worker或界面集成成功证据。

2026-10-05：IGMH实际注册operator退出日志`outputs/evidence/2026-10-05/reliability/logs/igmh-native.log`确认RNA cancel契约错误：`expected class QCBLENDER_OT_import_paired_field, function cancel to return None, not dict`。原生取消脚本的纯AsyncOperation实例未覆盖该契约，任务重新claimed。

## Answer

退出追踪与既有原生取消验证通过；注册operator的cancel返回值修复已完成，等待新候选原生复验。实际GUI及综合回归由06记录。

- Passed：`python -B -m unittest discover -s tests -p test_cancel_finalization.py -v`，16项定向测试通过。覆盖退出已确认/未确认、terminate拒绝、wait超时、poll异常、清理失败可重试、原始科学/进程错误与取消错误同时报告、Job释放后的持续追踪、多任务独立收尾与timer移除。日志为本工作树`outputs/tests/cancel-finalization-green.txt`。
- Passed：五个本次Python文件的内存compile检查及`git diff --check`；既有Python文件保持LF、UTF-8无BOM。
- 实现：活动Job使用强引用；`cancel()`返回请求状态、退出状态、PID、任务目录、退出码和错误，保存`cancellation.json`。未确认退出或导出清理未完成时保留Job。收尾先移除timer，原任务错误先报告，取消错误另报告；批量收尾逐个处理并记录异常。导出清理回调捕获路径/token，不引用退出modal后的RNA operator；确认退出才清理staging。
- Passed：主Agent在Blender 5.1.1已安装候选`625f5a32febe2b9db2c7d3b7158adc6ed0d8ccbd`执行原生脚本，宿主PID83488、exit0。真实diagnose worker PID73708和真实P03 CSV导出worker PID57896经脚本分派ESC退出已确认，取消错误为空、清理无待办；子worker退出码1是终止后的记录，不代表科学计算完成。CSV在实际staging出现后取消，脚本核查staging及该token的最终导出目录均未遗留。
- Passed：原生timer创建/移除及操作登记收尾；terminate拒绝与wait超时只在实际自建worker的进程控制返回处注入。退出未确认时Job保留、同批另一个worker独立退出；恢复实际Popen句柄后确认退出。真实缺失FCHK任务错误与受控staging清理错误均保留在报告。最后`remaining_jobs=[]`；这些受控故障不记作自然发生的系统故障。
- 原生证据：主仓`outputs/evidence/2026-10-05/reliability/logs/cancel-native.json`、`cancel-native.log`及`outputs/evidence/2026-10-05/reliability/cancel-native/ec6e3abeb076475087ad9e795c544b9f/cancel-finalization.json`。报告为Passed，明确`gui=Not Run`；日志SHA-256为`3c5550b96f9845748fa277e478ec033d026dfc5f848238947185469bf1c6994c`。
- Not Run：实际GUI按ESC、科学/视觉综合回归、独立人工复做及科研签署；GUI与综合技术验收归06。本任务的脚本分派ESC不作为用户按键或独立人工操作证据。

- Passed：新增产品import/paired-import/export回调契约测试先得到3项断言失败，修复后18项定向测试全部通过。`Operator.cancel`返回None；内部批量收尾从`Job.cancellation`取得结构化报告，`Job.cancel`契约保持。原生脚本新增真实`bpy.ops`创建三类注册operator、取消回调返回None及退出确认检查。
- Not Run：本次修复后注册operator的真实RNA关闭分派及无RNA错误日志。主Agent须用新安装候选执行更新的原生脚本，并检查Blender退出后的host log；脚本内返回None检查不能代替退出日志核查。

原生脚本在已安装本批候选、插件没有既有Job/modal任务的隔离Blender中执行：`--python tools/verify_cancel_finalization_blender.py -- --output-dir <项目内证据目录> --reference-root D:/workspace/QCBlender`。每次生成唯一证据子目录；输出`cancel-finalization.json`。控制故障仅注入Popen控制返回，实际worker句柄恢复后再确认退出；不会按进程名终止其他进程。独立人工复做及科研签署Not Run。
