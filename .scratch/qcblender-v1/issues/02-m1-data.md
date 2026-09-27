# M1 数据导入与已有场

Triage: ready-for-agent
Status: resolved
Owner: root
Blocked by: 01

## 工作

实现有来源/单位/身份的数据对象及 Gaussian Log/FCHK/Cube 适配，球棍与电荷基础显示，多文件关联和坏输入诊断。

## 验收

真实输入、Link1、缺字段、非立方/斜轴/多MO Cube 和坐标一致性通过；没有缺失值补零或靠文件名推断科学语义。

## Comments

2026-09-22：本阶段在 docs/VALIDATION.md 声明范围内完成。真实 Log/FCHK 导入、严格 Cube 数据、未知场显式量/单位、刚体坐标关联、源身份与坏输入诊断均有检查。最新 visual-acceptance/result.json 验证坐标配准及 Cube 声明不改数值；科学回归 19/19 Passed。

2026-09-22：Log/FCHK/Cube 数据路径和源快照完成；Link1、MP2/CCSD(T)/TD/双杂化、真实 IR、非立方斜轴多 MO Cube 与坏输入回归 Passed。GUI 后台 FCHK/Log 导入已实测。多文件刚体关联与未知 Cube 显式物理量声明已接入，等待当前构建的交互验收。独立数据与 hash 记录位于 tests/data。

2026-09-22：FCHK 规范化适配与 JSON/NumPy 存储已实现；源身份、坐标、基组约定、Alpha/Beta 轨道、原子电荷/偶极和密度矩阵保留。计算完成状态保持 unknown，不从 FCHK 存在推断收敛。内部数据 roundtrip、哈希与路径逃逸检查 Passed。Log/Cube、关联与 GUI 接入进行中；M0 尚未整体关闭。

2026-09-22：由已确认设计路线建立；实施、启动/安装 Blender 和下载公开样例已获用户授权。未授权提交、推送或发布。
