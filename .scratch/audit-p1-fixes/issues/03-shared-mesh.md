# 共享 mesh 切步保护

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 01

共享mesh Agent独占IRC和optimization切步守卫及专用原生回归脚本。不接入关联失效helper、不改其他产品模块、不启动Blender；交接脚本由主Agent串行执行。

## Comments

- 2026-10-04集成验收：旧候选原生脚本RED；`a4baaaf`候选P04/P02根及IRC子入口、NEXT/PREV/GOTO拒绝、单用户化后的独立导航、标注保护与XYZ对照Passed。原地及中文移动冷读Passed，证据`outputs/runs/audit-p1/1/final/shared/`及`logs/final-shared*`。GUI与Undo/Redo由04继续执行。

- 2026-10-04：在 `fix/shared-mesh-steps` 领取；原生 Blender 验证由主 Agent 串行执行。

## Answer

IRC 根对象及子对象入口、优化切步均在 `current_geometry` 校验后检查 atom mesh 用户数；共享 mesh 报错并提示先使 Object Data 独立，检查位于所有步骤、坐标和标注写入前。公共只读构型、复制和标注模块不变。

专用脚本 `tools/verify_audit_p1_shared_mesh.py` 使用已安装扩展、真实 P04/P02、原生 linked duplicate 和 single-user 操作，覆盖拒绝时全部记录状态不变、独立切步不污染原件、IRC 子对象、优化 NEXT/PREV/GOTO、共享标注数据/材质拒绝、优化显示层独立复制和 XYZ 对照。保存包含拒绝后的共享对象对与成功的独立对象，提供 `--output-dir <目录>` 及 `--reopen <blend>`；输入根目录通过 `QCBLENDER_REFERENCE_ROOT` 指定。冷读比较使用原生数据名称/共享关系、步骤、平衡坐标、标注和科学数组摘要，不保存进程指针。

- Passed：三个 Python 文件 AST 解析、UTF-8 无 BOM/LF 检查、`git diff --check`。
- Not Run：已安装候选原生验证、GUI 单用户路径、Undo/Redo、自包含工程及移动冷读；主 Agent 取得实际报告后更新验收状态。
