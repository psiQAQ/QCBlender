# 02 表面距离投影真实参照

Triage: ready-for-agent
Status: resolved

## Delivery

取得真实 Multiwfn 未缩放 Å 三列结果、完整扫描设置/日志、生成时静态构型及外部数值参照；确认 XY 坐标模式、偏移、表面定义、首次命中符号和有效域约定。记录版本、来源与哈希，依参照精度确定误差界。

## Comments

2026-10-23：用户在材料盘点后批准“按照建议推进”，本次使用现有 Multiwfn 与官方 Ru 构型生成 vdW 距离投影，并以独立球面求交建立参照。此授权不包含 Gaussian/AICD 计算或依赖安装。

2026-10-23：规划阶段定向检查的可访问输入中尚无完整真实参照包。保持待办；不启动 Multiwfn 或用合成矩阵替代此前置。

2026-10-23：完成[现有材料盘点](../../../docs/research/scientific-display-reference-inventory-20261023.md)。已定位官方 Ru(bpy)₃ 构型、Multiwfn 程序与手册案例、二茂铁输入和上游截图；缺实际未缩放 `distmap.txt`、匹配扫描记录及独立数值/有效域参照。无需再找起始构型；本轮未启动计算，Status 仍为 pending。

## Answer

2026-10-23：按追加授权补齐真实参照。现有 Multiwfn 2026.9.20、官方 Ru 构型、vdW 球面系数 1、61×41 非方网格、0.05 Å 负 Z 扫描；2,501 点全部通过独立解析球面求交和首个离散采样点核对（1,406 命中、1,095 未命中），最大连续表面差 0.049966733 Å。实测原始 XY 从零起算，绝对偏移为 `(-7,-6) Å`；深度为 `z_hit-z_start`，底值 -12 Å 由包围扫描和独立掩码证实为未命中。

原始三列、输入、设置、stdin、日志、执行身份、参数及独立 CSV 已集中到 `validation/shared/data/local/scientific-displays/ru-vdw-20261023/`，哈希和稳定入口验证 Passed。误差界及通用底值歧义见[同一研究记录](../../../docs/research/scientific-display-reference-inventory-20261023.md#本次实际运行及数值验收)；[机器验收](../../../validation/agent/reports/2026-10-23/projection-reference/acceptance.json)。仅完成 vdW 外部结果参照门禁；独立人工科研、适配器、密度表面和 Blender 验收 Not Run。
