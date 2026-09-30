# [P1] 收敛等价重复逻辑：节点构造与数据绑定辅助流程

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 02

## 目标

在任务 02 完成后重新核对仍存在的重复实现，只合并语义等价、能够降低维护成本的部分。保持行为和科学/Blender 分层，不建立通用框架。遵守 [总规格](../spec.md)。

## 已观察到的候选

| 候选 | 远端抽查证据 | 处理前必须证明 |
| --- | --- | --- |
| 数学节点构造 | [views.atom_selection()](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/views.py) 的内嵌 `math_node()` 与 [assets.math()](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/assets.py) 都创建 `ShaderNodeMath`、设置 operation、给数字设默认值或连接 socket | 参数、输出、类型处理与连接结果等价；抽取不会引入循环导入 |
| manifest 摘要/路径读取 | [views.bind()](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/views.py)、[NBO 导入](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/nbo.py)、[NOCV 导入](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/nocv.py) 都出现路径解析及 manifest SHA-256 读取 | 仅底层机械步骤可能共享；对象绑定、父子关系、计算身份和异步期间状态检查并不相同 |
| 工具与测试准备逻辑 | 任务 01 中确认仍被使用的重复 fixture、安装或节点检查准备代码 | 区分重复准备和有意独立的数值参考，后者不能合并成自我验证 |

前两项是已观察到的结构相似，不是“整段都可替换”的结论。NOCV 的指针、父对象和表格身份检查明显比一般摘要读取更丰富，不能以去重名义删掉。

## 执行清单

- [x] 为每个候选列出输入、输出、副作用、异常、单位/坐标约定和调用者；不等价时保留并说明。
- [x] 优先复用现有的小函数；确有需要时提取最小公共函数，不新增基类、注册系统或跨层工具大包。
- [x] 节点辅助逻辑放在合适的依赖位置，核对 `views ↔ assets` 的导入关系，避免循环依赖和 UI 注册副作用。
- [x] 摘要读取可以复用机械步骤，但各操作的身份校验和异步重验仍明确保留在各自调用路径。
- [x] 用相同输入比较修改前后的数值/错误结果；节点检查覆盖 socket 标识、连接、默认值及资产复用。
- [x] 删除合并后确实无用的实现和引用，更新清单；不要保留只有一层转调且无兼容用途的重复包装。

## 验收

- [x] 每处合并都有等价性说明、调用方清单与测试证据。
- [x] 公共标识、默认显示参数、异常/取消/校验语义及旧工程行为不变。
- [x] 不把科学层和 Blender 层的同名模块整体合并。
- [x] 数学节点及受影响场景经原生 Blender 验证；如触及材料查找，保留按节点类型识别而非依赖界面语言名称的行为。
- [x] 科学/非科学测试及相关安装、保存、冷重开检查无新增回归。
- [x] 未能证明等价的项以“保留＋原因”结案，不强求统一所有看起来相似的代码。

## Comments

尚未执行。不要把上述候选数量当成必须完成的重构数量。

- 2026-09-30：02 已 resolved。领取 M01/M02，仅复用已有 `assets.math`，使用函数内导入保持加载顺序。M03/M04 不具备有收益且完整的等价证据，保留。

- 2026-09-30：M01/M02 完成，两份文件 `+16/-33`，净减 17 行。10 组节点图完整对照一致；新包安装、场求值、资产导出重载、原地/移动冷重开和完整图例专项通过。允许 04 领取。
- 图例专项首次在沙箱内替换数组被 WinError 5 拒绝；宿主无法读取该沙箱生成的工程。用同一候选在新宿主隔离配置重建后通过，不修改 ACL 或产品逻辑。初次图例渲染传相对输出路径，Blender 将七张 PNG 写到 `C:/outputs/rc03hl`；已按日志逐文件核对 SHA-256 并移动回本工作树，收据 `final-host/render-paths.json`，后续命令使用绝对路径。此问题属于调用条件，未夹带修改历史脚本。

## Answer

两处重复的数学节点实现已合并到现有 `assets.math`。`views.atom_selection` 和 `scalars.add_legend` 的公开签名、调用顺序、节点操作/默认值/连接、数值和异常处理保持。两个调用点只在函数执行时导入 assets；资产构建与 auto_load 注册均通过，没有新增模块或循环导入失败。`assets`、`fog`、`inspection` 原调用不变。manifest 摘要的三个调用流程及工具准备逻辑按清单 M03/M04 保留。

| 验证 | 结果与证据 |
| --- | --- |
| 等价图和选择行为 | Passed；`outputs/repository-cleanup/final/nodes.json` 与 baseline 完全一致，覆盖 9 类资产和图例测试图；`tools/verify_node_helpers.py` 的数字/socket/错误输入及选择边界 Passed |
| 科学 / 其它单测 | Passed；final 下 `science.json` 69/69、`unit.json` 11/11，0 skipped，科学误差指标不变 |
| 新候选安装、注册注销、求值取消、缓存 | Passed；final 与 final-host 两套独立配置，均使用同一 ZIP；命令日志逐项保留 |
| 资产与工程 | Passed；`outputs/node-assets/report.json` 验证公共节点参数隔离/分支保留/导出重载；新生成 `outputs/rc03/` 与 `rc03h/` 工程原地及中文目录冷重开 Passed |
| 图例与兼容 | Passed；`outputs/rc03hl/checks.json`：真实密度/ESP，横竖/旋转布局、着色替换、独立复制、已知旧图升级、自定义旧图拒绝、原子电荷及 MO 图例、两次冷重开及重渲染。代表渲染已视觉检查 |
| 恢复 / 电荷 / 振动 | Passed；`final/recovery.json`，真实原始输入重建 |
| 包资格 | Passed；`final/qualification.json`、`qualification-host.json`、`evidence-index.json` 核对源码、两套安装和随包 wheel 摘要 |
| 完整历史 SOP、GUI 手动复做、独立人工验收 | Not Run；本次只声明上述受影响范围 |

最终代码候选：`outputs/repository-cleanup/final/dist/qcblender-0.0.1.zip`，50,632,940 字节，SHA-256 `2cd8bd76b22c3ac0d5cecfa519463a3bd01b0df797508f9f9eb730354b1d42fb`。源码文件清单摘要 `52da8fd814067a78e75f1f85872eab271190975e585aa73b2b3f85fd2b590834`。基于 `1b877516` 的未提交工作树；日志与新工程保留，后续 04–06 只改文档，不改变此候选。

Blender 重开日志仍出现既有 `VFont -> Node` 诊断；数值、几何、图例状态与渲染断言通过，不宣称零告警或人工签署。
