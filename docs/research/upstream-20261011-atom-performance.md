# 原子样式性能测量：2026-10-11

本批单原子载体基准总体 **Passed**。结果来自最终 main `7042b56c12eae9cea4522ea02fa41aa3ac28b4e0` 的实际安装环境，原始证据为 [report.json](../../validation/agent/reports/2026-10-11/upstream/final/benchmark/report.json)，SHA-256 为 `970849aaf392f9ab4c430a728f8abf586207937dd02b75ebaa54ca4c01341308`。报告属于本地批次证据；本文件归档测量结论，不改变 GUI 或独立科研接受的验收状态。

## 矩阵与测量定义

矩阵包含 32/128/512 原子，对应 25/102/409 条键，ball-stick、space-fill、bonds 三种样式及 Quality 1/3，共 18 个组合。每组合预热 1 对、正式重复 3 对冷/热试验，即 **108 次正式载体测量、36 次预热测量**；预热不进入统计摘要。核对所有记录均完整，耗时有限且低于 900 s，同一组合的求值网格计数重复一致。报告没有逐试验 `status` 字段；通过状态来自顶层 `status`，结合记录完整性及基准中的输入、原子身份、位置、键和网格检查。

数据出处：`parameters`、`generated_datasets.<原子数>.bonds`、`trials`、`warmups`。每对试验对应数组中的一条记录，包含 `cold` 和 `warm`；所有测量使用同一个 Blender 进程，PID 为 207280。

| 阶段或条件 | 定义 |
| --- | --- |
| 创建 | `atom_view` 的 Dataset 读取、载体属性、节点和材质构建及 Style/Quality 写入；不包含显式 depsgraph 更新 |
| 求值 | `view_layer.update`、depsgraph 更新、`evaluated_get` 及求值网格计数，实际完成 Geometry Nodes 工作 |
| 提取 | 对已求值对象执行 `to_mesh`、计数及 `to_mesh_clear`，期间不修改节点 |
| 冷条件 | 新建载体并重建本批节点资产；进程保持运行，不清理操作系统缓存 |
| 热条件 | 新建载体并复用配对冷轮的节点资产；仍重新读取 Dataset，不清理操作系统缓存 |
| 验证 | 文件摘要、载体原子 ID/元素/位置/键及网格重复性检查在计时之外执行 |

出处：`timing_definition.creation/evaluation/extraction/cold/warm/validation`。原生阻塞调用的 900 s 限制在返回后检查，不等同于硬进程截止时间。

## 512 原子结果

以下为正式 3 次试验的中位数。时间单位为 ms，“创建/求值/提取”分别统计；当前内存单位为 MiB，取提取完成时的工作集中位数。全部条件均为 1 个载体和 1 个求值网格。

| 样式、Quality | 冷：创建/求值/提取 | 热：创建/求值/提取 | 当前内存：冷/热 | 求值顶点/面 |
| --- | ---: | ---: | ---: | ---: |
| ball-stick，Q1 | 11.958 / 2.140 / 0.872 | 4.573 / 1.568 / 0.968 | 278.86 / 278.89 | 12,688 / 13,512 |
| ball-stick，Q3 | 11.855 / 2.502 / 1.579 | 4.721 / 2.293 / 1.850 | 324.05 / 324.11 | 89,488 / 167,112 |
| space-fill，Q1 | 12.067 / 1.482 / 0.552 | 4.984 / 1.489 / 0.641 | 319.03 / 318.98 | 6,144 / 10,240 |
| space-fill，Q3 | 11.936 / 1.849 / 1.020 | 4.694 / 1.636 / 1.067 | 314.16 / 314.16 | 82,944 / 163,840 |
| bonds，Q1 | 12.491 / 1.286 / 0.363 | 4.825 / 0.899 / 0.304 | 314.31 / 314.35 | 6,544 / 3,272 |
| bonds，Q3 | 12.117 / 1.359 / 0.375 | 4.558 / 1.043 / 0.379 | 314.51 / 314.51 | 6,544 / 3,272 |

时间出处：`summary["512/<style>/quality-<Q>/<cold|warm>/<stage>"].seconds.median`；当前内存出处：同键下提取阶段的 `current_working_set_mib.median`；网格出处：`trials[36..53].<cold|warm>.evaluated_mesh`。

以每次试验三个阶段耗时相加后再取中位数，最快组合为 **32 原子 bonds Q1 热条件：4.827 ms**，正式范围 4.794–4.956 ms；最慢组合为 **512 原子 ball-stick Q3 冷条件：16.102 ms**，正式范围 15.811–16.690 ms。原始记录分别为 `trials[12..14].warm`、`trials[39..41].cold`。总时间由各次原始数据计算，不是三个阶段中位数直接相加；它不包含场景清理、输入生成或计时之外的验证。

## 内存、热点与推断边界

正式测量的阶段末当前工作集范围为 **238.52–324.11 MiB**；进程生命周期峰值最高 **324.13 MiB**。两者使用 Windows `GetProcessMemoryInfo`。生命周期峰值包含此前阶段、此前组合及预热的高水位，不能解释为某个样式或阶段独立需要的内存。出处：`trials[*].<condition>.<stage>.current_working_set_mib/process_lifetime_peak_working_set_mib`、`timing_definition.memory`。

在本批规模内，创建阶段占三个阶段中位数之和的 **53.3%–89.8%**，冷条件创建耗时是热条件的 **2.42–2.96 倍**。这是从 `summary` 计算的同批条件差异，支持优先进一步剖析节点资产构建与复用路径，尚不能确定 Python 列表转换、逐原子颜色映射或某个具体函数是主导热点。

Quality 从 1 提升到 3 明显增加球体网格；bonds 的顶点和面数保持不变，因为当前键截面固定为 8 段。全部正式条件的图结构均为 3 个 Geometry Nodes 组、44 个节点、1 个材质及 3 个材质节点。出处：`timing_definition.quality_bonds`、`parameters.bond_profile_resolution`、`trials[*].<condition>.graph`。

本结果的适用边界：

- 未测量视口 FPS、渲染、用户交互延迟或完整应用启动时间。
- 没有旧版本对照，不能声称版本加速或无性能回归；冷/热差异属于资产复用条件差异。
- 原子数与键数按同一重复规则共同变化，不能推断独立的键复杂度规律；每条件只有 3 次正式样本，不外推至超过 512 原子、更密集拓扑或其他硬件。
- 合成 CH4 负载属于工程性能证据，不构成新的计算科学体系或独立科研接受证据。

## 环境与来源身份

| 身份 | 固定值及 JSON 出处 |
| --- | --- |
| 环境 | Windows 11，i5-13600KF，20 个逻辑 CPU；Blender 5.1.1、Python 3.13.9、NumPy 2.3.4、QCBlender 0.1.0；`environment` |
| Blender 二进制 SHA-256 | `b952b58cafe44050ae016bda94c91de0968b028b1c7082a824d7087985619642`；`environment.binary_sha256` |
| 源码 commit | `7042b56c12eae9cea4522ea02fa41aa3ac28b4e0`；`provenance.source_commit` |
| 产品树 | `24acf92e290ede3ec0fcef37d5a01a4e7cb44d93`；`provenance.product_tree` |
| 安装一致性 | Python 与源码一致，锁和 11 个 wheel 一致性检查通过；`provenance.checkout_python_match/installed_lock_and_wheel_match/installed_dependencies` |
| 候选 ZIP SHA-256 | `60d572186e127e40e1031a75fff325c3038ab7cc44102d3bdf1e79b6763860ee`；`candidate.sha256` |
| 基准工具 SHA-256 | `5a359fea1afeaefd4d7bdf12f07ac90cb9adf0d567c49e37b536b510585a8fa5`；`provenance.tool_sha256.benchmark_atom_styles.py` |
| 源 CH4 FCHK SHA-256 | `3f93c52df5ef5adda00eff89bc5c9bb0bc10182722193d87e72f3b710d7c2c40`；`source.sha256` |

源文件为 [ch4_uhf_ccpvdz.fchk](../../validation/shared/data/regression/chemtools/ch4_uhf_ccpvdz.fchk)。工程负载采用 `repeat-seed-cubic-lattice-v1`，以 8 Å 间距按源原子顺序重复构型，只复制构型内键，末尾允许截断至精确目标数；32/128/512 原子分别需要 7/26/103 个副本。生成参数和 Dataset 文件摘要保存在 `generated_datasets.<原子数>.generation/files`，源输入和生成数据在测量期间保持不变。
