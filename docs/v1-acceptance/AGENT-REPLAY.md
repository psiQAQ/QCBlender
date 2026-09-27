# Agent 技术复跑记录

2026-09-27。**C01–C13 六栏技术检查、N01–N18：Passed。** 共 26 个独立可见 Blender 进程完成原目录和移动目录冷重开、数组/关联/节点核对及重渲染。独立人工 SOP 结果仍为 Not Run，签名和发布批准均留空。

环境：Windows x64、Blender 5.1.1、独立简体中文配置。固定候选 [qcblender-0.0.1.zip](../../outputs/v1-acceptance/../dist/qcblender-0.0.1.zip)，50,440,466 字节，SHA-256 `03311fdeb0c83a38a546ebddedee1fe05e8dcb7260b53c889dd9fee3fa7ee231`。源码、ZIP 和两套安装目录逐字节一致：[candidate-check.json](../../outputs/v1-acceptance/replay/candidate-check.json)。

Computer Use 实际确认面板按钮与对话框，已确认入口的重复操作优先使用 Blender MCP。MCP 还用于参数预填、原值/单位/数组核对、相机灯光、图例朝向、曲线标签与原生撤销检查。GUI 首次操作见 [gui-actions.jsonl](../../outputs/v1-acceptance/replay/gui-actions.jsonl) 和各例 `gui-confirmation.json`；全部固定包收据见 [evidence-index.json](../../outputs/v1-acceptance/replay/evidence-index.json)。

## C01–C13

| 案例 | 导入 | 源数值/单位 | 节点前后 | PNG | 保存重开 | 移动冷重开 | 工程与证据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Passed | Passed | Passed | Passed | Passed | Passed | [C01.blend](../../outputs/v1-acceptance/cases/C01/C01.blend)、[PNG](../../outputs/v1-acceptance/cases/C01/C01.png)、[数值与节点](../../outputs/v1-acceptance/cases/C01/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C01/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C01/moved-check.json) |
| C02 | Passed | Passed | Passed | Passed | Passed | Passed | [C02.blend](../../outputs/v1-acceptance/cases/C02/C02.blend)、[PNG](../../outputs/v1-acceptance/cases/C02/C02.png)、[数值与节点](../../outputs/v1-acceptance/cases/C02/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C02/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C02/moved-check.json) |
| C03 | Passed | Passed | Passed | Passed | Passed | Passed | [C03.blend](../../outputs/v1-acceptance/cases/C03/C03.blend)、[PNG](../../outputs/v1-acceptance/cases/C03/C03.png)、[数值与节点](../../outputs/v1-acceptance/cases/C03/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C03/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C03/moved-check.json) |
| C04 | Passed | Passed | Passed | Passed | Passed | Passed | [C04.blend](../../outputs/v1-acceptance/cases/C04/C04.blend)、[PNG](../../outputs/v1-acceptance/cases/C04/C04.png)、[数值与节点](../../outputs/v1-acceptance/cases/C04/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C04/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C04/moved-check.json) |
| C05 | Passed | Passed | Passed | Passed | Passed | Passed | [C05.blend](../../outputs/v1-acceptance/cases/C05/C05.blend)、[PNG](../../outputs/v1-acceptance/cases/C05/C05.png)、[数值与节点](../../outputs/v1-acceptance/cases/C05/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C05/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C05/moved-check.json) |
| C06 | Passed | Passed | Passed | Passed | Passed | Passed | [C06.blend](../../outputs/v1-acceptance/cases/C06/C06.blend)、[PNG](../../outputs/v1-acceptance/cases/C06/C06.png)、[数值与节点](../../outputs/v1-acceptance/cases/C06/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C06/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C06/moved-check.json) |
| C07 | Passed | Passed | Passed | Passed | Passed | Passed | [C07.blend](../../outputs/v1-acceptance/cases/C07/C07.blend)、[PNG](../../outputs/v1-acceptance/cases/C07/C07.png)、[数值与节点](../../outputs/v1-acceptance/cases/C07/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C07/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C07/moved-check.json) |
| C08 | Passed | Passed | Passed | Passed | Passed | Passed | [C08.blend](../../outputs/v1-acceptance/cases/C08/C08.blend)、[PNG](../../outputs/v1-acceptance/cases/C08/C08.png)、[数值与节点](../../outputs/v1-acceptance/cases/C08/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C08/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C08/moved-check.json) |
| C09 | Passed | Passed | Passed | Passed | Passed | Passed | [C09.blend](../../outputs/v1-acceptance/cases/C09/C09.blend)、[PNG](../../outputs/v1-acceptance/cases/C09/C09.png)、[数值与节点](../../outputs/v1-acceptance/cases/C09/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C09/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C09/moved-check.json) |
| C10 | Passed | Passed | Passed | Passed | Passed | Passed | [C10.blend](../../outputs/v1-acceptance/cases/C10/C10.blend)、[PNG](../../outputs/v1-acceptance/cases/C10/C10.png)、[数值与节点](../../outputs/v1-acceptance/cases/C10/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C10/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C10/moved-check.json) |
| C11 | Passed | Passed | Passed | Passed | Passed | Passed | [C11.blend](../../outputs/v1-acceptance/cases/C11/C11.blend)、[PNG](../../outputs/v1-acceptance/cases/C11/C11.png)、[数值与节点](../../outputs/v1-acceptance/cases/C11/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C11/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C11/moved-check.json) |
| C12 | Passed | Passed | Passed | Passed | Passed | Passed | [C12.blend](../../outputs/v1-acceptance/cases/C12/C12.blend)、[PNG](../../outputs/v1-acceptance/cases/C12/C12.png)、[数值与节点](../../outputs/v1-acceptance/cases/C12/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C12/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C12/moved-check.json) |
| C13 | Passed | Passed | Passed | Passed | Passed | Passed | [C13.blend](../../outputs/v1-acceptance/cases/C13/C13.blend)、[PNG](../../outputs/v1-acceptance/cases/C13/C13.png)、[数值与节点](../../outputs/v1-acceptance/cases/C13/saved-final.json)、[冷重开](../../outputs/v1-acceptance/cases/C13/reopen-check.json)、[移动](../../outputs/v1-acceptance/cases/C13/moved-check.json) |

每个工程旁均有同名 `.qcdata/`；本轮移动副本在 `moved/final03311/CNN/`。原始外部结果及完整日志另保存在 `sources/`，来源与 SHA 见 [SOURCES.md](../../outputs/v1-acceptance/../../docs/v1-acceptance/SOURCES.md)。[35/35 样本摘要](../../outputs/v1-acceptance/replay/source-check.json)通过。

## 关键数值与边界

- C01：20 原子、69 电子、+1/双重态、UB3LYP/STO-3G；Alpha/Beta HOMO 35/34。总密度=Alpha+Beta、自旋=Alpha−Beta，最大残差 2.49e-14；`.fchk/.fch` 真正分别导入。
- C02：Trp Log/FCHK 最大坐标差 4.986996e-7 Å；DVB 54 模，模式 45 为 3396.4292 cm^-1、98.3271 km/mol。
- C03：NCIPLOT 100×sign(λ₂)ρ 与 RDG 原值保留；`.cube/.cub` 相同数组，标注没有换算数值；RDG 的 100 是过滤哨兵。
- C04：RHF/STO-3G，-673.5905711573 Eh；ESP 为 hartree/e，密度为 electron/bohr^3。源电荷前两项 -0.405349572、0.0192284424 e；偶极约 (-1.207528,0.954743,-2.231571) D。不同网格采样、无效核域、域外及旋转平移源坐标均核对。
- C05：20 原子 → 隐藏氢剩 10 → 保留真实 H6 剩 11；复制层及源原子数组独立保留。
- C06：job 2/block 1，7 NBO、2 E(2)，第一条占据 1.99933、能量 -0.77653 Eh；E(2)=0.59 kcal/mol。原文行号和 `.out/.log` 逐字节别名通过。
- C07：同一真实苯酚二聚体的 IGMH/IRI；26 原子、122×66×66；IGMH 两片段 1–13/14–26，δg 为 electron/bohr^4；IRI a=1.1，保留明确原子单位；着色为 electron/bohr^3。两组各 48312 个真实有限散点，线性全范围，未截断或归一化源数组。
- C08：ρ=0.001 electron/bohr^3、Multiwfn 0.25 Bohr 表面网格，11 最大值+8 最小值；PDB B-factor 为 kcal/mol。40 个面积 bin 总和 228.2405 Å²；高精度极值范围 -44.973471 至 34.841007 kcal/mol。外部表面定义与 C04 显示网格分别记录。
- C09：59 CP=27 个(3,-3)+29 个(3,-1)+3 个(3,+1)，58 条路径；Euler 27−29+3=1。CP 28 的 ρ=0.3219923958、Laplacian=-1.168558420，单位分别 electron/bohr^3、electron/bohr^5；原属性全文保留。
- C10/C11：真实 H2O2 IRC 中三步对应 FCHK，RHF/STO-3G、4 原子、18 电子；Mayer 来自同波函数的 PySCF 2.13.1 计算，每步 6 原子对，数值无量纲。文本采用 Multiwfn 兼容语法，实际计算生产者不是 Multiwfn。
- C12/C13：同次 Multiwfn COBH3 ETS-NOCV，9 对显著记录；pair 1/Total 为 -77.88 kcal/mol，λ=±0.56514、轨道 1/51；配对 Cube 74×92×78，electron/bohr^3，数组逐体素核对。KS/Fock 重建能量属于近似，不能称严格 FTS；有限网格电荷积分不作为收敛声明。

C07–C09 的独立 ESP/密度/Hessian/IRI 复算及 C13 λψ² 差值逐体素核对见 [研究记录一](../../outputs/v1-acceptance/../../docs/research/sop-real-sources-c07-c09.md)、[研究记录二](../../outputs/v1-acceptance/../../docs/research/sop-real-sources-c10-c13.md)。原作者样本的独立再分发许可未明确时仅用于本地验收，不加入 ZIP。

## N01–N18

| 检查 | 结果 | 原值 → 新值 → 可观察变化 / 证据 |
| --- | --- | --- |
| N01 | Passed | 全部 → 无 → 仅 H6，网格和像素改变；C01/node-checks.json |
| N02 | Passed | 球棍 → 空间填充 → 只显示键；半径 0.25/0.07 → 0.4/0.12 Å，轮廓改变；C01 |
| N03 | Passed | 20 → 10 → 11 → 20；真实氢掩码、撤销/重做与复制独立；C05/N03-N15-N16.json |
| N04 | Passed | 双相 → 正相 → 负相；solid → wire → points；C01/node-checks.json |
| N05 | Passed | 联动 0.045 → 独立 0.07/0.025；Opacity 1/1 → 0.15/0.6；两相分别响应；C01 |
| N06 | Passed | C03 同网格、C04 不同网格取 ESP 色；密度等值 0.004 → 0.012，几何变化但原数组不变；C04/node-check.json |
| N07 | Passed | 色域 -0.05/0/0.05 → -0.1/0.01/0.15；图例位置改变，颜色与色标同步；域外紫红；C04 |
| N08 | Passed | 切片中心/旋转/尺寸变化，41² → 61²，像素/截面变化；C04/node-check.json |
| N09 | Passed | 关闭 → 平面 → 盒裁切，预期几何减少、体素数组不变；C01 |
| N10 | Passed | 颜色/透明度范围/阈值/曲线共六图；Opacity Scale → 0 时无可见雾；C01/N10-result.json |
| N11 | Passed | 0.5 → 1.5 Å/D，箭头长度随比例变化，物理偶极不变；C04 |
| N12 | Passed | 模式 45 → 44、帧 0/6/18、振幅/相位/速度变化，位移与 IR 高亮同步；C02/N12-N15.json |
| N13 | Passed | ESP 极值/AIM 类别点与路径显示 → 隐藏；记录 1 → 2 → undo 1 → redo 2，坐标和原文值对应；C08/C09 analysis-check.json |
| N14 | Passed | IGMH/IRI 表面 → 散点显隐；δg/IRI 横轴和 sign(λ₂)ρ 纵轴量名、单位、48312 样本核对；C07/source-node-check.json、C07-scatter-records.png |
| N15 | Passed | Duplicate、排序、隐藏、删除、New Current-Version View；复制节点/材质/IR/氢掩码独立；C01/C02/C05 |
| N16 | Passed | C01/C05/C06/C07–C13 原生撤销/重做返回预期对象、参数和关联；MCP 编辑使用明确 undo checkpoint；各例 N16/analysis/source-node 收据 |
| N17 | Passed | 域内 → 域外 → 核内无效点；后两者明确拒绝，旧读数清除，不当零；平移旋转后源坐标一致；C04/node-check.json |
| N18 | Passed | 13 例原目录 → 另一目录，26 个独立新 PID；数组 SHA、节点、分析记录、VDB 路径及重渲染通过；evidence-index.json |

## 负例、修复与回归

| 项目 | 状态 | 证据 |
| --- | --- | --- |
| 网格不匹配 | Passed | C07/negative-grid-check.json；真实 Cube 原点改 0.1 Bohr，明确拒绝，场景不变 |
| IRC 重复步号/原子身份变化 | Passed | C10/N14-N16-source-check.json；场景完整 |
| Mayer 缺步/原子对冲突 | Passed | C11/N14-source-check.json；已有 Mayer 时重复导入亦被拒绝 |
| NOCV 错误 pair/自旋 | Passed | C13/negative-pair-spin.json；pair 999/Total、pair 1/Alpha 明确拒绝且场景不变 |
| UI-01 侧栏裁切 | Passed | 移除固定 ui_units_x；replay/defects/UI-01-narrow-after.png |
| UI-02 Map Colors 异常 | Passed | 修复 add_legend 局部变量遮蔽；C03/C04 最终包映射与图例复跑通过 |
| PORT-01 VDB 路径 | Passed | 相对路径、缓存刷新、保存失败回滚；最终包全部移动冷重开通过 |
| ESP-01 极值独立编号 | Passed | Multiwfn 最大/最小值分别从1编号；读取器按(kind,serial)查重；同类重复仍拒绝。replay/defects/ESP01/ 原失败与 C08 GUI 复验保留 |
| 科学回归 | Passed | replay/science-reference.json，20/20，0 failures/errors |
| 外部结果读取与持久化 | Passed | tools/verify_external_results.py 的相关已有检查，真实19点重现与修复后复验 |
| 干净配置离线安装和移动冷重开 | Passed | replay/clean-install-03311/evidence/extension.json |
| Check Scientific Runtime | Passed | cases/runtime-final/mcp-operations.json，最终包工作进程实际成功 |
| ZIP/源码/两套安装一致性 | Passed | replay/candidate-check.json |
| 样本 SHA | Passed | replay/source-check.json，35/35 |

原失败收据保留 Failed。旧候选案例完整证据在 `replay/pre-03311/`，更早资料在 `replay/pre-ace35/`；本轮仅以固定 03311… 候选收据汇总。C04 MCP 等待超过300秒后按实际工作进程成功报告继续，未把超时当成计算通过。旧安装测试目录 ACL 冲突后改用全新配置及输出目录，冷重开已复验。

自动审批曾拒绝 ESP 导入报错后写入 Passed 的动作，理由是可能形成不实验收记录；该写入未执行。随后记录 Failed、修复根因并通过实际 GUI 和数值复验。

技术复跑未新增依赖。用户随后授权分批本地提交相关修复及工作流迁移；不推送或发布。已有用户修改保留；人工签名和发布批准由用户填写。

## 提交前复核（2026-09-27）

- 中文材质与图例回归、外部结果读取与持久化回归、20 项科学回归：Passed。
- C01 移动副本的 VDB 相对路径和实际网格加载、真实保存失败回滚：Passed。
- 固定候选与源码及两套安装一致性、35 个来源摘要：Passed；ZIP 未改动。
- 本轮日志位于 `outputs/workflow-migration/`。外部结果检查首次因缺少 Blender 用户数据目录失败，指定独立资源目录后通过。`verify_saved_views.py` 完整脚本面向 water-mode/density-esp，误用于 C01 时在专用着色断言失败；随后仅复用其中的通用体积路径断言，并额外验证真实网格加载及保存回滚。未将该完整脚本记为本轮 Passed。
