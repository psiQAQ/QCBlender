# 加强节点回归断言

Triage: ready-for-agent
Status: resolved
Type: task

## 目标与验收

- 保留数量断言，比较求值结果实际 qc_atom_id；增加仅选氧原子的同数量案例。
- 非空结果保留 INT / POINT 原子编号；空结果没有顶点。
- 独立固定 qc.atom_selection.v1 的接口名称、方向、类型、默认值及 Socket_0—Socket_4，不从被测节点组生成预期。
- 保留 helper 与接口不变性检查，在原生 Blender 实际执行；图例复用现有专项工具。

## Comments

- 2026-09-30：领取任务，公共接口预期以基线节点快照固定，产品源码保持现状。

## Answer

Passed：原生 Blender 5.1.1 执行 verify_node_helpers.py，核对七种筛选结果的实际原子编号、非空属性类型/域、固定 v1 五个 socket 契约及原有 helper 检查。

两项负向检查 Passed：碳原子预期误写成同数量氧原子编号时身份断言失败；固定 Socket_1 预期误写时接口断言失败。只修改内存中的测试预期，未改产品代码。日志和命令收据见 outputs/cleanup-followup/negative-assertions.json；03 将在同批候选复验正向检查并保存日志。
