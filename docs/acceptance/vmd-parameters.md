# VMD 参数交互技术验收

更新：2026-09-28。基线为 `main` 的 `2fa8096`，开发分支为 `feat/vmd-parameters`。GPT-6 sol/high 子代理在独立工作树实现与复核，主代理按四包顺序合并并执行实际 Blender 验证。规格见 [任务目录](../../.scratch/vmd-parameters/spec.md)。

| 批次 | 代码 | 科学回归 | 独立安装 | MCP 操作与渲染 | 保存、原地与移动冷重开 | Computer Use | 整批 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 分组面板 | Passed | Passed | Passed | Passed | Passed | Passed | Passed |
| 02 显式着色场 | Passed | Passed | Passed | Passed | Passed | Passed | Passed |
| 03 一次性色标范围 | Passed | Passed | Passed | Passed | Passed | Passed | Passed |
| 04 复制显示参数 | Passed | Passed | Passed | Passed | Passed | Passed | Passed |

Computer Use 四项均在最终集成候选 **04-copy-r4** 上执行；表中通过范围是首批四项技术验收。旧候选的单独 GUI 状态不追记为通过，独立人工签署与外部视觉对照继续后置。

各目录均位于 `outputs/vmd-parameters/`，ZIP 为目录内的 `dist/qcblender-0.0.1.zip`。最终集成候选为 **04-copy-r4**，包含四包功能，版本仍为 `0.0.1`；旧验收基线保留。

| 目录 | 构建提交 | ZIP SHA-256 |
| --- | --- | --- |
| `01-panel` | `2d442e0` | `d2b0457b0c4e6dc3fb7a7a27e8163b179f573c675d0e6f286ed18334af12a0fc` |
| `02-binding` | `9d0617e` | `bab71d8b7214e87cfe0e5e4a64008ae40d9cd747264d18c840935e270c176af7` |
| `03-ranges-r2` | `9922acf` | `bfcffa1e1fe1c16301e7a196dc4c92e9beb353251eeb3bfb42c4d84a55400672` |
| `04-copy-r4` | `1b26f47` | `bcc8bcc564f989aa78eea2bb5c1a170b4fa08a5d67bce1243477b587eee1008e` |

最终 `qualification.json` 核对源码、ZIP、安装副本及锁定 wheel 摘要一致；`evidence-index.json` 将自动检查、GUI 点击和 GUI 工程双冷重开报告绑定至该 ZIP。首批技术验收汇总 `acceptance.json` 为 **Passed**。原有 `automated-qualification.json` 及其索引保留，继续只证明其中列明的自动技术检查。

## 技术证据

第一包原子三种样式的顶点数为 274 / 210 / 64，轨道实面、线框、点为 2068 / 65920 / 86856；渲染存在相应变化，撤销/重做及冷重开一致。第二包覆盖真实密度/ESP 创建与替换、旧选择顺序入口、切片、映射前后裁剪及歧义图拒绝，范围和图例位置保留。

第三包覆盖零中心对称、原生异步 operator、取消、任务中来源或范围变化、同单位错误字段、常量场和无有效点。真实 ESP 的 73508 个有效格点范围为 `−0.10348012956188413 / 0 / 65.10162445751108 hartree/e`，节点按 float32 容差一致。错误不覆盖当前范围，worker 不创建 Dataset。证据为 `03-ranges-r2/range-checks.json`；最终候选另有 `range-checks.json` 复验实际异步读取。

最终候选的 `features/checks.json` 验证三个复制组、全部目标预检、共享材质拆分、色带独立、源身份与对象变换保留、未知公开输入及被旁路标准节点拒绝。原子电荷着色及旧登记兼容、目标原子选择、切片位置、雾材质裁剪、实际撤销与重做均通过。

`edges/edges.json` 验证真实 C07 IGMH/IRI 的几何/着色角色及各自 Cube 摘要；IGMH worker 读取 `sign_lambda2_rho` 色场范围 `−123.65 / 0 / 0.278699 electron/bohr^3`。解析场经实际 Geometry Nodes 求值，表面和切片的同值映射及端点饱和正确；物理零值、掩码非零值和域外点的有效性不同。`edges/valid-zero.png`、`edges/invalid-outside.png` 验证零值按色标显示、无效值为洋红色。

真实 `water_neutral_nbo_opt_freq.out`（SHA-256 `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519`）的两个计算段分别由已安装候选的 worker 导入。显示层按同一源 SHA 和不同 job 身份分组；从第 1 段向第 2 段复制参数后，目标模式编号、振幅、相位、原子选择、对象位置、源行记录及数组均保留。`real-log-views/checks.json` 的复制和原地/移动冷重开 **Passed**，两个 job 的原文起始行为 1、1091。

同名不同 SHA、同源不同 `selected_job` 的**字段候选**与实际选择，使用明确标注的合成 Dataset 验证。真实 Gaussian 多段字段链路为 **Not Run**：现有 Log reader 导入构型与性质，不提供场求值所需的基组/MO 数组；本轮未扩大输入支持，不能把合成字段身份测试写成真实量化计算。

最终科学回归 **48 项 Passed**、复制策略 **7 项 Passed**；独立配置离线安装、运行库及 worker 检查 Passed。`features/evidence.blend` 和 `evidence.qcdata/` 保存 30 个视图、11 份 Dataset；关闭验收窗口后，两个新进程分别打开原工程和 `features/moved 中文 path/` 副本。来源、科学数组摘要、节点/材质值和对象变换一致，两次重新渲染通过。

## GUI 验收

在 Blender 5.1.1 简体中文独立配置中，通过 Computer Use 实际点击新增入口；MCP 只负责场景准备、数值核对及证据保存。记录为 `gui-checks.json`，PNG 和可重开工程位于 `gui/`。

| 操作 | 观察与核对 | 结果 |
| --- | --- | --- |
| 分组参数与命名样式 | 密度表面从线框切为实体，节点样式 1 → 0，求值网格 2370 顶点；密度使用正值标签，轨道显示正相位/负相位。 | Passed |
| 显式选择着色场 | 选择器显示文件、完整 SHA、字段单位及轨道信息；同构型 ESP 绑定成功且原范围保留。不同分子的 MO 字段被拒绝，原映射与对象数不变。 | Passed |
| 一次性色标范围 | 输入 R=0.08 得到 −0.08/0/+0.08；点击有效范围读取后得到上述真实 ESP 全网格范围。 | Passed |
| 显示参数复制 | 三个组选项默认选中；目标样式与色标跟随源，来源和对象变换保留。撤销恢复原值，编辑菜单重做恢复复制结果。不兼容目标报错且双方保持原状。 | Passed |

GUI 操作结束后科学数组摘要与操作前完全一致。另存 `gui/evidence.blend + evidence.qcdata/` 后关闭本次验收进程，再由两个新进程打开原工程和 `gui/moved 中文 path/` 副本：30 个视图、11 份 Dataset 的来源、节点、材质、变换与数组均一致，重新渲染 **Passed**；见 `gui/checks.json`。既有用户 Blender 窗口保留。

四个已合并工作树已归档至 `outputs/vmd-parameters/worktree-archives/`，逐文件摘要记录于 `manifest.json`，对应开发分支保留。主目录继续位于 `feat/vmd-parameters`。

## 验收演进记录

已修复：范围读取的完整色场身份校验、复制预检的失效常量、电荷着色的节点登记与旧工程兼容、自定义分支旁路标准节点。原子视图叠加电荷和网格两种着色会产生歧义图，现已在修改前拒绝。最终候选对受影响路径复验 Passed。

`04-copy-r2` 的位置断言曾读取未更新的依赖图，修正脚本后确认对象变换保留；`04-copy-r3` 的样本访问受不同进程安全上下文限制，`04-copy-r4` 使用一致用户上下文。各旧目录及复现记录保留，不作为最终通过证据。

桌面访问曾返回 `GetCursorPos 0x80070005` 和监视器捕获 `0x80070057`，当时未执行按钮输入；历史记录保留于 `desktop-recheck.json`。2026-09-28 桌面访问恢复后完成上述 GUI 点击与双冷重开，不再构成技术验收阻塞。

Computer Use 的 `Control_L+Shift_L+z` 输入在本次会话中产生了额外撤销，随后通过 Blender 的“编辑 → 重做”逐步恢复，并由 MCP 比较完整显示状态。重做验收依据菜单操作，不将该工具快捷键结果归因于插件。

## 后置检查

独立人工复做与签署：**Not Run**。VMD 实际运行及外部视觉对照：**Not Run**。
