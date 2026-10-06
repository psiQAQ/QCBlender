# 人工教程与技术检查覆盖

本表保留旧 SOP 的 **44 个 A/C/N/X/P1 编号**。人工入口只承担可观察的正常操作；重复输入、数值恒等式、错误边界、取消、完整撤销矩阵和多位置冷重开由 Agent 按需执行。表中的工具是复验入口，不是本批通过记录。

人工目录见 [SOP](../human/SOP.md#topics)，可运行技术命令见 [README](README.md)。脚本路径均相对仓库根目录；输入统一从 `validation/shared/data/{public,local,regression}/` 取得。当前候选与历史证据通过 [ARTIFACTS](../../docs/ARTIFACTS.md) 分别定位。

## 首次安装与出图

| 旧编号 | 人工入口 | Agent 保留的技术检查 |
| --- | --- | --- |
| A00 | [安装](../human/SOP.md#install) | 本批独立配置、实际源码/安装包身份；`tools/verify_extension.py` |
| A01 | [安装](../human/SOP.md#install) | 离线安装、科学运行库、注册/注销；`tools/verify_extension.py` |
| A02 | [轨道](../human/SOP.md#orbital) | P01 原始文件、O₂ 电子数/自旋和来源；`tools/verify_tutorial_samples.py` |
| A03 | [轨道](../human/SOP.md#orbital) | 预检、Alpha 源 MO9、资源上限和缓存；`tools/verify_alpha_workflow.py` |
| A04 | [轨道](../human/SOP.md#orbital) | 等值变化、正负相位、网格原值保持；`tools/verify_alpha_workflow.py` |
| A05 | [渲染图片](../human/SOP.md#render) | 实际 PNG、对象和材料绑定；`tools/verify_alpha_workflow.py`、`tools/render_visual_baseline.py` |
| A06 | [导出参数](../human/SOP.md#export) | 当前视图摘要、重复导出、失效绑定和自定义节点状态；`tools/verify_alpha_workflow.py`、`tests/test_view_summary.py` |
| A07 | [保存工程](../human/SOP.md#save) | `.blend + .qcdata` 保存与数据完整性；`tools/verify_alpha_workflow.py`、`tests/test_science_project.py` |
| A08 | 由 Agent 执行中文路径迁移核对 | 科学数组、VDB 与文件身份不变；`tools/verify_alpha_workflow.py --reopen` |
| A09 | [保存重开](../human/SOP.md#save) | 新 PID 重开、摘要复导出和显示参数；`tools/verify_alpha_workflow.py --reopen` |

## 文件与物理量

| 旧编号 | 人工入口 | Agent 保留的技术检查 |
| --- | --- | --- |
| C01 | [轨道主流程](../human/SOP.md#orbital)、[密度与 ESP](../human/topics/03-density-esp.md)、[空间工具](../human/topics/04-spatial-tools.md) | FCHK/FCH 别名、MO 来源编号、总密度=Alpha+Beta、自旋密度=Alpha−Beta；`tools/verify_tutorial_samples.py`、`tools/verify_alpha_workflow.py`、`tests/test_science_reference.py` |
| C02 | [本地限定案例](LOCAL-CASES.md) | 多计算段能量、优化步、振动频率/位移与 IR；`tests/test_science_log.py`、`tests/test_science_optimization.py`、`tools/verify_optimization.py`、`tools/verify_animation.py` |
| C03 | [Cube](../human/topics/02-cube.md) | Cube/CUB 别名、源网格/倍率、符号与数组；`tests/test_science_cube.py`、`tools/verify_paired_fields.py`、`tools/verify_tutorial_samples.py` |
| C04 | [密度与 ESP](../human/topics/03-density-esp.md)、[空间工具](../human/topics/04-spatial-tools.md) | 电荷/偶极原值、不同网格采样、核内/域外无效、旋转平移、CSV 单位；`tests/test_science_reference.py`、`tests/test_science_profile.py`、`tools/verify_line_profile.py`、`tools/verify_xyz_export_blender.py` |
| C05 | [分子与 XYZ](../human/topics/01-molecule-xyz.md) | 原子源编号、氢显隐、局部选择、标注、复制独立性与 Undo/Redo；`tools/verify_mn_parameters.py`、`tools/verify_mn_annotations.py`、`tests/test_science_atom_selection.py`、`tests/test_copy_display.py` |
| C06 | [本地限定案例](LOCAL-CASES.md) | NBO/E(2) 计算段、轨道与原文行号、OUT/LOG 别名；`tools/verify_tutorial_samples.py`、`tools/verify_nbo.py`、`tools/verify_nbo_gui_undo.py` |
| C07 | [IGMH 与 IRI](../human/topics/05-igmh-iri.md) | 成对网格、片段和分量声明、全量/筛选散点、取消与错误网格不破坏原场；`tools/verify_igmh_provenance.py`、`tests/test_science_igmh_declaration.py`、`tools/verify_xyz_export_blender.py`、`tools/verify_multi_field_accept.py` |
| C08 | [ESP 与 AIM](../human/topics/06-esp-aim.md) | 极值/面积分布、单位、表面定义、记录编号与重复拒绝；`tools/verify_tutorial_samples.py`、`tools/verify_external_results.py`、`tools/verify_external_results_gui.py` |
| C09 | [ESP 与 AIM](../human/topics/06-esp-aim.md) | CP 类型、路径、原文属性与同构型关联；`tests/test_science_aim_association.py`、`tools/verify_aim_association.py`、`tools/verify_tutorial_samples.py` |
| C10 | [IRC 与 Mayer](../human/topics/07-irc-mayer.md) | 逐步波函数、能量、原子身份、重复步拒绝和随步标注；`tools/verify_irc.py`、`tools/verify_tutorial_samples.py`、`tools/verify_audit_p1_shared_mesh.py` |
| C11 | [IRC 与 Mayer](../human/topics/07-irc-mayer.md) | Mayer 原子对/步号、来源、缺步和冲突拒绝；`tools/verify_irc.py`、`tools/verify_tutorial_samples.py`、`tools/verify_xyz_export_blender.py` |
| C12 | [ETS-NOCV](../human/topics/08-ets-nocv.md) | 能量分解、近似身份、原文和单位；`tools/verify_nocv.py`、`tools/verify_nocv_status.py`、`tools/verify_tutorial_samples.py` |
| C13 | [ETS-NOCV](../human/topics/08-ets-nocv.md) | pair/自旋匹配、两符号密度、数组、错误 pair 拒绝、复制与撤销；`tools/verify_nocv.py`、`tools/verify_tutorial_samples.py`、`tests/test_science_nocv_status.py` |
| X01 | [分子与 XYZ](../human/topics/01-molecule-xyz.md) | 单帧/多帧、注释/帧号、格式错误拒绝、复制和导出；`tests/test_science_xyz.py`、`tools/verify_xyz_export_blender.py`、`tools/verify_audit_p1_shared_mesh.py` |

## 节点与交互

| 旧编号 | 人工入口 | Agent 保留的技术检查 |
| --- | --- | --- |
| N01 | [分子与 XYZ](../human/topics/01-molecule-xyz.md)、[公共节点](../human/topics/09-nodes.md) | Selection、元素/源编号组合、空集和界面/公共节点对应；`tools/verify_mn_parameters.py`、`tools/verify_composable.py`、`tests/test_science_atom_selection.py` |
| N02 | [分子与 XYZ](../human/topics/01-molecule-xyz.md)、[公共节点](../human/topics/09-nodes.md) | 球棍/空间填充/键线、半径/质量与真实键；`tools/verify_composable.py`、`tools/verify_composable_render.py`、`tools/verify_node_assets.py` |
| N03 | [分子与 XYZ](../human/topics/01-molecule-xyz.md) | 全部/无/所选氢、源编号、复制及撤销；`tools/verify_mn_parameters.py`、`tools/verify_layers.py` |
| N04 | [Cube](../human/topics/02-cube.md) | 双相/正相/负相、实体/线框/点、公共节点分支；`tools/verify_node_assets.py`、`tools/verify_composable.py`、`tools/render_visual_baseline.py` |
| N05 | [Cube](../human/topics/02-cube.md) | 联动/独立阈值与透明度，源场不变；`tools/verify_alpha_workflow.py`、`tools/verify_composable.py` |
| N06 | [Cube](../human/topics/02-cube.md)、[密度与 ESP](../human/topics/03-density-esp.md) | 绑定色场、Position/Value/Valid、不同网格与无效传播；`tools/verify_vmd_parameters.py --check binding`、`tools/verify_vmd_scalar_edges.py` |
| N07 | [密度与 ESP](../human/topics/03-density-esp.md) | 色域、单位、图例同步和无效颜色；`tools/verify_mn_legend.py`、`tools/verify_vmd_scalar_edges.py`、`tests/test_legend_layout.py` |
| N08 | [空间工具](../human/topics/04-spatial-tools.md) | 切片位置/旋转/采样数、有效掩码和数据导出；`tests/test_science_planes.py`、`tools/verify_composable.py`、`tools/verify_xyz_export_blender.py` |
| N09 | [空间工具](../human/topics/04-spatial-tools.md)、[公共节点](../human/topics/09-nodes.md) | 平面/盒裁剪只改可见几何、源数组不变；`tools/verify_composable.py`、`tools/verify_visual_features.py` |
| N10 | [空间工具](../human/topics/04-spatial-tools.md) | 雾颜色、阈值、透明度曲线、透明度零与体积有效路径；`tests/test_fog_materials.py`、`tools/verify_fog.py`、`tools/render_visual_baseline.py` |
| N11 | [密度与 ESP](../human/topics/03-density-esp.md) | 偶极箭头比例改变，物理偶极值不变；`tools/verify_visual_features.py`、`tools/verify_composable.py` |
| N12 | [本地限定案例](LOCAL-CASES.md) | 模式/帧/幅度/相位/速度、IR 高亮与 CSV；`tools/verify_animation.py`、`tools/verify_xyz_export_blender.py` |
| N13 | [ESP 与 AIM](../human/topics/06-esp-aim.md) 的记录浏览 | 分析点/路径显隐、记录切换、原文值和 Undo/Redo；`tools/verify_external_results_gui.py`、`tools/verify_aim_association.py`；各控件的实际 GUI 可达性须单独核对 |
| N14 | [IGMH 与 IRI](../human/topics/05-igmh-iri.md) | 几何/着色场角色、全量与筛选 CSV、数据量与单位；`tools/verify_xyz_export_blender.py`、`tools/verify_igmh_provenance.py`、`tests/test_science_data_export.py` |
| N15 | [分子与 XYZ](../human/topics/01-molecule-xyz.md) | 图层复制/排序/隐藏/删除、参数兼容拒绝、材质与节点独立；`tests/test_copy_display.py`、`tools/verify_vmd_parameters.py --check copy`、`tools/verify_audit_p1_shared_mesh.py` |
| N16 | 由 Agent 完成完整撤销矩阵 | 原生 GUI 的撤销/重做及科学数据不变；`tools/verify_nbo_gui_undo.py` 为局部入口，其余对象按下表补充实际 GUI 证据 |
| N17 | [空间工具](../human/topics/04-spatial-tools.md) | 游标/探针/采样线、域外和核内无效、旧读数清除、源坐标一致；`tools/verify_line_profile.py`、`tools/verify_vmd_scalar_edges.py`、`tests/test_science_profile.py` |
| N18 | [一次保存重开](../human/SOP.md#save)，其余由 Agent 执行 | 原位置、中文移动位置和归档解包后的新进程读回、丢文件/恢复/保存失败；`tools/verify_extension.py`、`tools/verify_project_recovery.py`、`tools/verify_failed_save.py`、`tests/test_science_project.py` |
| P1-A | 由 Agent 检查，正常 IRC 操作见 [IRC 与 Mayer](../human/topics/07-irc-mayer.md) | 当前构型关联、换步失效、重新关联、旧绑定拒绝；`tools/verify_audit_p1_association.py`、`tests/test_science_current_association.py` |
| P1-B | 由 Agent 检查，独立副本见 [分子与 XYZ](../human/topics/01-molecule-xyz.md) | 共享 mesh 拒绝换步、单用户恢复、IRC/优化/XYZ 控制；`tools/verify_audit_p1_shared_mesh.py` |

## 技术检查的补充边界

现有工具覆盖表中所列能力的一部分或多个方面；执行前检查脚本参数与断言，不把文件名当作覆盖证明。以下矩阵有历史人工操作成分，现有自动脚本未完整实现时，应在本批补最小原生检查或真实 GUI 操作；未做的格子保留 `Not Run`。

| 范围 | 本批要实际观察的行为 |
| --- | --- |
| 文件别名 | 同一原件另存 `.fch`、`.cub`、`.log` 后分别走真实读取入口，核对量、单位、数组与源身份；不把成功读取一个后缀当作另一个后缀通过 |
| N16 原子/轨道/显示层 | 选择、氢显隐、阈值、复制/排序/隐藏/删除各完成一次 Undo 和 Redo，核对原对象与副本独立 |
| N16 外部分析 | NBO、IGMH/IRI、ESP/AIM、IRC/Mayer、ETS/NOCV 的活动记录或显示变化回到预期状态，数据关联仍有效 |
| N16 共享对象 | 关联、失效、恢复与换步拒绝的原生撤销行为单独执行；脚本返回 `undo_redo: Not Run` 时不能改写为通过 |
| N18 三位置 | 原位置、移动位置、归档解包位置分别启动新 PID，检查 Dataset 身份、数组、节点、VDB 和必要重渲染；人工主流程只练习一次保存重开 |
| 取消和失败 | `tools/verify_cancel_finalization_blender.py` 的 ESC 是脚本派发；实际 GUI 取消另记录。`tools/verify_multi_field_accept.py` 的首/次字段失败、`tools/verify_native_volume.py` 的原生体积失败不破坏现有场景 |
| 科学有效性 | 展示阈值、网格和相机选择不能证明计算收敛；外部结果保留生产者、方法、单位、片段/分量及近似说明 |

当前人工 ESP/AIM 专题使用可见的记录浏览与可用筛选入口。源编号、CP 属性值范围、点/路径显隐和 ETS Pair number 等底层属性是否具有实际可操作的面板入口，仍需对照当前界面确认；属性定义或脚本可写不代表人工教程已覆盖该控件。

旧 C01–C13 每例重复的渲染、保存、三位置重开和多轮导出比较转入这里按受影响能力选择执行。历史结果入口保持 [ARTIFACTS](../../docs/ARTIFACTS.md) 中对应批次的候选身份；本目录不将旧结果重新标成当前候选通过。
