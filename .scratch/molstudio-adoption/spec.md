# MolStudio 对照与外部分析结果导入

Status: claimed

## Problem Statement

QCBlender 已完成首版 M7 技术验收，但尚未提供 MolStudio 所展示的若干分析结果浏览工作流。用户需要一份以当前开发状态为基准的源码对照，并在 QCBlender 中逐期导入和显示自己已经计算好的结果。

## Solution

以 `docs/research/gxnu-molstudio-comparison.md` 固定对照基准：QCBlender HEAD `1007375f0b3c2704a5acdd696c0322ae381b2f09`，MolStudio 子模块 `6f3e859020e27d11511b512a7cc47564386b6216`。复用当前单个 Blender 扩展的数据、节点、显示层和工程存储。通过逐文件指定角色导入外部结果，校验来源、单位和构型关联，保存到 `.qcdata`；不运行或打包 Multiwfn、VMD、Tachyon，不复制 MolStudio 代码。

## User Stories

1. 使用者能隐藏氢、保留指定氢并恢复显示，同时保留原始分子数据。
2. 使用者能将 IGMH/IRI 的几何场与着色场组合，并查看 δg 与 sign(λ₂)ρ 的分布。
3. 使用者能将 ESP 表面极值与面积分布关联到已导入的静电势视图。
4. 使用者能从指定 Gaussian 计算段查看 NBO 和 E(2) 原始记录。
5. 使用者能查看 AIM 临界点、键路径和可用属性。
6. 使用者能明确排列 IRC 构型并查看每步能量与结构。
7. 使用者能将外部 Mayer 键级结果关联到 IRC 的相同步与原子对。
8. 使用者能查看带自旋和单位的 ETS-NOCV 成对能量表。
9. 使用者能将某个 NOCV pair 的 Cube 关联到表格行并显示带符号形变密度。

## Implementation Decisions

- 每项分析沿用现有纯 Python 读取层、`Dataset`、Blender 操作入口、场映射和 `.qcdata` 持久化；只有具体分析需要的解析与视图才新增。
- Blender 对话框让使用者逐文件指定角色、源计算/构型和没有可靠自动判定的单位。文件名不决定科学语义，缺失与冲突要明确报错。
- 记录源文件摘要、原始单位、计算/几何关联及导入器版本。外部分析结果不标成 QCBlender 内置计算。
- IGMH/IRI、ESP、AIM 和 NOCV 复用原生 Blender 场、点/线或图像视图；NBO、IRC、ETS-NOCV 展示记录及原始证据。
- NBO 轨道不通过能量相近与 canonical MO 自动等同；IRC 顺序由使用者明确提供。
- README 所列但 MolStudio 当前源码未见模块的 DI/ESM 只进入比较文档，不作为已实现能力。

## Testing Decisions

- 每片在读取接口使用真实有来源的外部结果，验证有效输入、截断/损坏、单位和关联冲突。
- 每片在 Blender 5.1.1 验证实际导入、显示和保存重开；修改界面的片同时验证撤销/重做。
- 复跑相关科学回归、重建离线包并核对包资格。没有真实样本时标记 `Not Run`，不得宣布该片 Passed。
- 用户独立使用及发布验收不由 Agent 签署。

## Out of Scope

灯光/相机预设、自动出图、Qt/OpenGL 画布、直接调用外部分析程序、DI/ESM 及对外推送/发布。

## Issues

01–09 实现已落地，真实样本及 Agent 技术验收 Passed。来源、参数、逐例 GUI/数值/节点/渲染及冷重开证据见 [SOP 复跑任务](../v1-acceptance/issues/04-agent-replay.md)。独立用户验收及发布验收仍由用户完成。

- [01 显示快捷控制](issues/01-atom-visibility.md)
- [02 IGMH/IRI 结果](issues/02-igmh-iri.md)
- [03 ESP 表面结果](issues/03-esp-surface.md)
- [04 NBO 记录](issues/04-nbo.md)
- [05 AIM 拓扑结果](issues/05-aim.md)
- [06 IRC 能量路径](issues/06-irc-path.md)
- [07 IRC 键级](issues/07-irc-bond-order.md)
- [08 ETS-NOCV 表格](issues/08-ets-nocv-table.md)
- [09 NOCV 场](issues/09-nocv-field.md)
