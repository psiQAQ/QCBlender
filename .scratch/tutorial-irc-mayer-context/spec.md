# IRC Mayer 导入自动绘图上下文修复

## 目标与范围

导入 IRC Mayer CSV 后，嵌套绘图 Operator 使用新表对象作为 object 与 active_object，自动创建所选原子对的曲线与当前步游标。保持现有科学数据、公共接口、依赖、教程和样本。

基线：fix/tutorial-aim-records，95cc654bdcc3975064699ad8f46968354719b81b。
工作树：D:/workspace/QCBlender/.worktrees/tutorial-irc-mayer-context。
分支：fix/tutorial-irc-mayer-context；只提交本地，不 push。

## 验收

01：最小上下文修复；现有 verify_irc.py 在固定旧根对象的真实 temp_override 下调用导入，核对自动曲线、游标、四个数组与当前根步；通过静态编译与差异检查。
02：主 Agent 执行 Blender 回归、原生 Properties/Object/QCBlender/IRC Path/Import Mayer Results 导入 P04/mayer-pyscf.csv、科学数组与当前步核对、保存与冷重开。Blender 5.1.1 初始失败证据：outputs/evidence/2026-10-02/tutorial-cu/full/C11/。

## 实施计划

01 修复与回归检查；02 安装和验证依赖 01。Blender 实际操作与最终证据索引由主 Agent 串行维护。
