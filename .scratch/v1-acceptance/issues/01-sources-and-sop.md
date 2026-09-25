# 01 样本来源与 SOP

Status: needs-info
Type: task
Execution: in_progress

## 工作

固定 `0.0.1` 包摘要、全部输入后缀与分析角色、物理量和节点覆盖；对公开样本逐项记录 URL、版本、许可、SHA-256 与计算条件。找不到成套真实输出的案例保持 `Not Run`。

## 验收

SOP 覆盖 `.fchk/.fch`、`.log/.out`、`.cube/.cub` 和所有专用输入角色、九片功能、节点、渲染及 `.blend + .qcdata`；来源、摘要与科学定义可核验。未找到的真实样本列出缺口，不用合成数据冒充。

## Comments

2026-09-26：Blender 简体中文界面的默认材质节点名导致导入原子时失败，已按节点类型修复。候选 ZIP 更新为 50,440,399 字节、SHA-256 `524ed52f4b71f8ce01ea7d4e702acb7847a956d6b69e40cad28e3b089282951d`；隔离配置离线安装、真实水 FCHK 导入和工程冷重开通过。原人工结果继续 `Not Run`，受影响案例须使用此 ZIP 重做。

2026-09-23：已建立 `docs/v1-acceptance/SOP.md`、`SOURCES.md`，固定当前 ZIP `adf7760c647be303cd69f43b4b928d42411031d1bdfe3f25466bb15aded245fc`。S01–S08 与 `.fch/.cub` 逐字节别名已核对。NBO 来自 cclib-data，但独立许可未确认；不纳入发布包。IGMH/IRI、ESP 表面、AIM、IRC/Mayer、ETS-NOCV、NOCV pair 缺成套真实输出，科学验收 `Not Run`。本任务待补齐来源后完成。

2026-09-23：补充 xyzrender 固定提交 `69a219f` 的 S09–S11 真实 Multiwfn IGMH Cube，三文件 SHA、26 原子和 92×75×77 的共同原子/网格已核对。其原始波函数、片段、Multiwfn 版本和单位未随示例给出，IRI 双场仍缺；C07 保持 `Not Run`。
