# 02 安装与原生 GUI 验证

Triage: ready-for-agent
Status: resolved
Blocked by: 01

## Comments

2026-10-02：由主 Agent 领取，串行维护 Blender、原生 GUI 与最终证据。先执行 verify_irc.py 及 --reopen；再从已保存 C10 IRC 根对象原生导入 P04/mayer-pyscf.csv，核对 6 对/3 步、四数组、当前根步与自动曲线/游标、保存和冷重开。必要时在 Properties 编辑器对象上下文内复验；不得将静态检查写成 Blender Passed。

## Answer

Passed：固定源码deb9416及候选c736bb9，锁定后端/wheels核对、安装68 Python源码摘要、显式旧root上下文verify_irc及冷重开通过。新可见PID40356从真实C10根原生导入P04 Mayer，自动表/曲线/步2游标、原生Atom B=3/Plot Pair及18源值通过；两对逐步源坐标、数组、标注和游标MCP通过。13文件/2Dataset/9数组/6引用保存归档通过，31332/15732/54032原路径/中文移动/解包三次冷读和9渲染像素一致通过，所有进程退出。

证据：outputs/evidence/2026-10-02/tutorial-irc-mayer-context/与outputs/evidence/2026-10-02/tutorial-cu/full/C11/fixed/cold-chain-v2.json。修复前GUI poll失败与保全工程、首次临时渲染mask断言失败保留，未改写原批次。当前教程02仍claimed、03 pending；全教程/统一资格/合并归档和用户复做及独立科研签署Not Run。
