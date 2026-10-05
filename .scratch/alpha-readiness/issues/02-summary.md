# 02 当前视图参数摘要

Triage: ready-for-agent
Status: resolved

## 工作与验收

实施spec第4项，复用现有导出事务，提供SUMMARY与Markdown/JSON。覆盖实时输入、科学身份、缺字段/自定义图partial、重复导出及取消；不运行或连接Blender进程，主Agent串行集成验证。

## Comments

- 2026-10-05：在独立分支 `feat/alpha-summary` 领取；修改仅涉及导出、摘要、相关测试和导出入口。Blender GUI、冷重开及共享 SOP 由主 Agent 集成验证。

## Answer

- 现有导出提供 `SUMMARY`；同一事务生成 `view-summary.md` 与 `metadata.json`。`metadata.json` 的导出 schema 仍为 1，科学 metadata 和旧 CSV 列/单位保持；摘要新增独立 `view_summary`。
- 确认导出时从实时 modifier、socket、材质节点与色带读取配置输入。外层显示连接复用现有预检；自定义或断开的显示图标记 `unverified`，缺少存储输入或未记录科学字段标记 `partial`，不补默认数值。摘要只陈述已读取配置，内部节点组和完整渲染等效性未验证。
- 科学字段及来源必须匹配绑定 Dataset；保留计算段、方法/基组、源构型/当前构型身份、字段/单位/轨道/自旋/网格与有效域计数。生成摘要前及发布前复核 manifest，变化则失败并清理暂存。目录优先级、唯一结果目录、取消、文件 SHA-256 沿用原导出流程。
- `Passed`：28 项相关测试（实时状态边界 5、真实 Dataset 摘要导出 7、旧科学 CSV 导出 7、显示参数复制 9）、compileall、`git diff --check`。解释器为 Blender 5.1 随附 Python 3.13.9，科学依赖只读复用主仓库 `outputs/science`；旧 CSV 真实输入通过 `QCBLENDER_REFERENCE_ROOT` 使用主仓库既有样本。
- 证据：本工作树 `outputs/evidence/2026-10-05/alpha-summary/validation.json` 与逐项日志；报告包含源码及日志 SHA-256。复跑入口：`outputs/runs/alpha-summary/validate.py`。
- `Not Run`：本轮 Blender 进程交互、GUI、原生撤销/重做、保存与冷重开、独立人工签署。状态边界使用明确隔离的替身测试，实际 Dataset 加载及文件事务均真实运行；原生界面和工程验证归主 Agent 的集成任务。
