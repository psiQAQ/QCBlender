# VMD 参数交互技术验收

更新：2026-09-28。基线为 `main` 的 `2fa8096`，开发分支为 `feat/vmd-parameters`。GPT-6 sol/high 子代理在独立工作树实现与复核，主代理按四包顺序合并并执行实际 Blender 验证。规格见 [任务目录](../../.scratch/vmd-parameters/spec.md)。

| 批次 | 代码 | 科学回归 | 独立安装 | MCP 操作与渲染 | 保存、原地与移动冷重开 | Computer Use | 整批 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 分组面板 | Passed | Passed | Passed | Passed | Passed | Not Run | Not Run |
| 02 显式着色场 | Passed | Passed | Passed | Passed | Passed | Not Run | Not Run |
| 03 一次性色标范围 | Passed | Passed | Passed | Passed | Passed | Not Run | Not Run |
| 04 复制显示参数 | Passed | Passed | Passed | Passed | Passed | Not Run | Not Run |

各目录均位于 `outputs/vmd-parameters/`，ZIP 为目录内的 `dist/qcblender-0.0.1.zip`。最终集成候选为 **04-copy-r4**，包含四包功能，版本仍为 `0.0.1`；旧验收基线保留。

| 目录 | 构建提交 | ZIP SHA-256 |
| --- | --- | --- |
| `01-panel` | `2d442e0` | `d2b0457b0c4e6dc3fb7a7a27e8163b179f573c675d0e6f286ed18334af12a0fc` |
| `02-binding` | `9d0617e` | `bab71d8b7214e87cfe0e5e4a64008ae40d9cd747264d18c840935e270c176af7` |
| `03-ranges-r2` | `9922acf` | `bfcffa1e1fe1c16301e7a196dc4c92e9beb353251eeb3bfb42c4d84a55400672` |
| `04-copy-r4` | `1b26f47` | `bcc8bcc564f989aa78eea2bb5c1a170b4fa08a5d67bce1243477b587eee1008e` |

最终 `automated-qualification.json` 核对当前源码、ZIP、安装副本及锁定 wheel 摘要一致；`automated-evidence-index.json` 将通过报告绑定至该 ZIP。它只证明列明的自动技术检查，整体验收以 `acceptance.json` 的 **Not Run** 为准。

## 技术证据

第一包原子三种样式的顶点数为 274 / 210 / 64，轨道实面、线框、点为 2068 / 65920 / 86856；渲染存在相应变化，撤销/重做及冷重开一致。第二包覆盖真实密度/ESP 创建与替换、旧选择顺序入口、切片、映射前后裁剪及歧义图拒绝，范围和图例位置保留。

第三包覆盖零中心对称、原生异步 operator、取消、任务中来源或范围变化、同单位错误字段、常量场和无有效点。真实 ESP 的 73508 个有效格点范围为 `−0.10348012956188413 / 0 / 65.10162445751108 hartree/e`，节点按 float32 容差一致。错误不覆盖当前范围，worker 不创建 Dataset。证据为 `03-ranges-r2/range-checks.json`；最终候选另有 `range-checks.json` 复验实际异步读取。

最终候选的 `features/checks.json` 验证三个复制组、全部目标预检、共享材质拆分、色带独立、源身份与对象变换保留、未知公开输入及被旁路标准节点拒绝。原子电荷着色及旧登记兼容、目标原子选择、切片位置、雾材质裁剪、实际撤销与重做均通过。

`edges/edges.json` 验证真实 C07 IGMH/IRI 的几何/着色角色及各自 Cube 摘要；IGMH worker 读取 `sign_lambda2_rho` 色场范围 `−123.65 / 0 / 0.278699 electron/bohr^3`。解析场经实际 Geometry Nodes 求值，表面和切片的同值映射及端点饱和正确；物理零值、掩码非零值和域外点的有效性不同。`edges/valid-zero.png`、`edges/invalid-outside.png` 验证零值按色标显示、无效值为洋红色。

真实 `water_neutral_nbo_opt_freq.out`（SHA-256 `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519`）的两个计算段分别由已安装候选的 worker 导入。显示层按同一源 SHA 和不同 job 身份分组；从第 1 段向第 2 段复制参数后，目标模式编号、振幅、相位、原子选择、对象位置、源行记录及数组均保留。`real-log-views/checks.json` 的复制和原地/移动冷重开 **Passed**，两个 job 的原文起始行为 1、1091。

同名不同 SHA、同源不同 `selected_job` 的**字段候选**与实际选择，使用明确标注的合成 Dataset 验证。真实 Gaussian 多段字段链路为 **Not Run**：现有 Log reader 导入构型与性质，不提供场求值所需的基组/MO 数组；本轮未扩大输入支持，不能把合成字段身份测试写成真实量化计算。

最终科学回归 **48 项 Passed**、复制策略 **7 项 Passed**；独立配置离线安装、运行库及 worker 检查 Passed。`features/evidence.blend` 和 `evidence.qcdata/` 保存 30 个视图、11 份 Dataset；关闭验收窗口后，两个新进程分别打开原工程和 `features/moved 中文 path/` 副本。来源、科学数组摘要、节点/材质值和对象变换一致，两次重新渲染通过。原生面板/对话框截图记录绘制结果，不能代替 Computer Use 点击。

## 缺陷与待补验收

已修复：范围读取的完整色场身份校验、复制预检的失效常量、电荷着色的节点登记与旧工程兼容、自定义分支旁路标准节点。原子视图叠加电荷和网格两种着色会产生歧义图，现已在修改前拒绝。最终候选对受影响路径复验 Passed。

`04-copy-r2` 的位置断言曾读取未更新的依赖图，修正脚本后确认对象变换保留；`04-copy-r3` 的样本访问受不同进程安全上下文限制，`04-copy-r4` 使用一致用户上下文。各旧目录及复现记录保留，不作为最终通过证据。

Computer Use 未完成的原因是桌面访问失败：`GetCursorPos: Access denied (0x80070005)`；恢复尝试的截取仍返回 `IGraphicsCaptureItemInterop.CreateForMonitor: Could not capture the given monitor (0x80070057)`。待桌面解锁且显示会话可访问后，补验分组控件、着色选择、范围按钮、复制对话框及错误提示。MCP 操作已完成；整批待验，尚未创建通过标签。已合并工作树和分支保留，待最终验收后归档。

续跑再次枚举了实际窗口并尝试恢复已保存的 Blender 窗口，仍报 `GetCursorPos 0x80070005`；刷新后窗口仍最小化，未执行按钮输入。记录在最终候选的 `desktop-recheck.json`。

独立人工复做与签署：**Not Run**。VMD 实际运行及外部视觉对照：**Not Run**。
