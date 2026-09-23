# 04 NBO 记录

Status: resolved
Execution: technical_acceptance_passed
Blocked by: none

## Delivery

按指定 Gaussian 计算段读取 NBO Summary 和 E(2)；显示轨道类型、原子、占据与能量/相互作用原始证据，不推断 canonical MO 对应关系。

## Acceptance

- 真实 NBO Log、多个计算段、缺失段和截断段检查；数据关联到正确构型。
- Blender 列表、保存重开及源文件摘要核对。

## Answer

真实 Gaussian 16 水分子 Log 的三个 NBO 块已核对；所选块为 7 条轨道和 2 条 E(2)。缺块、截断、多构型关联拒绝、来源摘要、离线 worker、Blender 列表、冷重开及 GUI 导入撤销/重做通过。独立用户验收另行进行。
