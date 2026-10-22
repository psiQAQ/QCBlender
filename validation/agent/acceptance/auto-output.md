# 自动观察方向与统一出图验收

2026-10-23。新增主轴取景、可选近似减少遮挡，以及在当前场景显式应用、恢复的出图方案。用户批准实施、定向测试、实际 Blender 出图、完整包、SOP 和本地提交；不包含日常配置安装、push 或公开发布。

## 当前交付与身份

- 产品源码：`8d2f83f20c0eb251e10f02c81faae176c636ca46`；后续教程、截图和验收提交不改变产品包。
- 完整包：[qcblender-0.1.0.zip](../../shared/install/qcblender-0.1.0.zip)，50,960,273 字节；SHA-256 `e73797010178657da9b950817f25a79786f2251832c9d04736c56b0dc00fa590`。
- 原构建位置：`outputs/candidates/auto-output/build-4/qcblender-0.1.0.zip`。身份和原始检查收据由[本批机器记录](../reports/2026-10-23/auto-output/acceptance.json)定位，当前入口为 [current-install.json](../current-install.json)。
- Blender 5.1.1，Windows x64；隔离配置 `.tmp/runs/auto-output/build-4/profile/`。完整重建 9 个节点资产，复用已有 11 个锁定 wheels；未新增或更新依赖。
- SOP [第 8 步](../../human/SOP.md#step-08)提供方向、档位、背景与恢复说明；[第 9 步](../../human/SOP.md#step-09)的 1280 × 720 图片已按相同参数重新渲染。

## 行为与结果

| 检查 | 状态 | 实际范围 |
| --- | --- | --- |
| 定向测试 | Passed | 6 个相关模块，去重 61 项；初轮 59 项，动态引擎修复后 7 项、渲染属性上下文修复后 21 项，失败、错误、跳过均为 0。各批源码快照及日志保留，未把重复执行累加为测试数量 |
| 自动方向与取景 | Passed | 原子、双相位 MO、ESP、体积雾四个实际工程；CURRENT/PCA/UNOBSTRUCTED、5% 边距、尺寸与正交投影边界、重复应用不增加相机和灯光；纯算法另覆盖纵横画幅、退化结构、稳定性及有界搜索 |
| 科学数据保护 | Passed | 四个工程应用、恢复、保存及冷读时逐数组 SHA-256、Dataset 身份和对象变换一致 |
| 统一场景设置 | Passed | Standard、曝光 0、Gamma 1、PNG RGB/RGBA、尺寸；三盏归一化 Area 灯随主体尺度和相机方向配置，原相机、World、灯光及相关原生参数可恢复 |
| 跨场景共享 | Passed | MO 案例验证共享 World 保持其他场景引用，共享灯光对象在本场景隔离并可恢复；共享集合中的灯光在修改前明确拒绝 |
| 实际渲染 | Passed | EEVEE 64、Cycles 128/0.02、Cycles 512/0.005；检查 PNG 尺寸、RGB/RGBA 类型、有限像素及透明 Alpha 范围。MO 两相位、ESP 图例及体数据白底图已查看 |
| GUI 新入口 | Passed | 最终包真实点击渲染属性 → QC 出图；取消、PCA、预览/白底/1280×720、减少遮挡/透明/640×480、原生 Undo/Redo、恢复原设置；中文参数和提示布局已查看 |
| 独立相机弹窗 | Passed | F3 搜索并打开“创建取景相机”，确认方向默认 CURRENT、边距可见后取消；该项不宣称 GUI 确认创建已执行 |
| 持久化 | Passed | 最终候选新进程读取 atoms、MO、ESP、fog 和 GUI 工程，核对科学数据与出图状态；GUI 工程冷读后再执行恢复，原参数匹配 |
| 完整包与隔离安装 | Passed | 新源码与生成资产整包构建；128 个安装成员与精确候选核对，最终安装运行实际插件 |
| 本轮全量回归、远端 CI、日常安装 | Not Run | 按已批准范围执行定向验收；日常安装的历史身份另存于 current-install.json，不以本次隔离结果替代 |
| 独立用户及科研验收 | Not Run | Agent 数值检查、点击和图像观察不代表独立人工签署 |

测试实现入口为 [verify_output_settings.py](../../../tools/verify_output_settings.py)。运行时以已有教程工程为只读输入：`validation/work/human/P01/P01.blend`、`P03/P03-density-esp.blend`、`P03/checkpoints/P03-fog.blend`。结果保存到 `outputs/projects/auto-output/`，没有覆盖输入工程。

## 图像与复用边界

MO 和原子的最终渲染使用 build-4。ESP、fog 的基础双引擎渲染保留 build-3 的原候选身份；build-3 到 build-4 的产品变更仅为 `output_ui.py` 的渲染属性上下文，方向、取景、灯光和预设实现未变。最终包对两份工程重新冷读，并另做 fog 精细档白底/透明和 SOP 图片的真实渲染。具体候选 SHA、原报告和新冷读收据在机器记录中逐项关联。

ESP 图例从主体方向采样中排除，但参与最终取景。自动换角度后，图例朝向仍需用已有旋转控制调整；本批在原生 Blender 中设置该控制后复验，`esp-readable-legend.png` 可读，没有新增自动图例排版功能。图例和受光表面的像素颜色不保证相同。

精细体数据透明 PNG 有 30,552 个 Alpha 为 0 但 RGB 非零的像素；仅查看 RGB 会出现本应透明的彩点。按线性 Alpha 合成白底后，与直接白底渲染的逐通道平均绝对差为 0.00445、95 分位为 0.0213；该比较仅说明此案例的合成结果接近，不声称跨引擎或逐像素一致。原始 PNG、[Alpha 分析](../reports/2026-10-23/auto-output/cases/alpha-analysis.json)及精细白底图保留。透明图应在目标背景上检查。

“减少遮挡”是有界几何投影近似，不计算透明表面和体积雾的光学遮挡。纯雾、图表或缺少适合主体点时提示使用当前方向；科学数组与对象坐标不随观察方向改变。已有合成器保持原样，并提示它可能改变最终颜色或 Alpha。

## 实际工具与修复

本批使用真实 Blender CLI 和 Agent Computer Use。现有 MCP 客户端未找到兼容 SDK，因此未运行 MCP，也没有临时安装依赖来绕过这一缺项。

实际运行发现并修复三项问题：Cycles 不在静态 RNA 引擎枚举中；共享灯光链接到 Scene 根集合时不能以普通 PointerProperty 保存 embedded ID；渲染属性上下文的 `context.object` 为空使入口不可用。修复分别补入定向检查和原失败场景复验；早期失败报告仍保留，build-1/2 不作为当前有效候选。

GUI 第一轮撤销返回载入工程的尺寸，因为测试启动脚本对 640×480 的修改没有进入 Undo 栈；“恢复原设置”能精确恢复 640×480。随后第二轮真正 GUI 操作的撤销/重做与记录状态完全匹配。GUI 工程首次沙箱冷读遇到 `WinError 5`，使用原生用户权限重试通过，未修改 ACL、取得所有权或强制删除。

技术截图记录实际点击；[界面观察序列](../reports/2026-10-23/auto-output/runs/gui-2/observations.json)由只读计时器采集，保存与冷读通过 CLI 完成。SOP 插图只展示操作位置，不将它当作独立人工验收。

## 证据及保留

正式记录在 `validation/agent/reports/2026-10-23/auto-output/`。其中 `runs/<相对路径>` 对应原 `.tmp/runs/auto-output/<相对路径>`，保全 138 个执行记录、日志及脚本；原机器记录内的执行时绝对路径未改写。逐文件原路径、当前路径、大小和 SHA-256 见机器记录的 `evidence_files`。

工程、配套 `.qcdata` 与图片在 `outputs/projects/auto-output/`：最终 atoms/MO/GUI 在 `build-4/`，ESP/fog 在 `build-3/{esp-focused,fog-focused}/`，新增精细体图与教程图片分别在 `build-4/{fog-high,sop}/`。失败轮次、旧包和隔离配置均保留。前一有效包 `06b468…ff052` 已核对仍位于 `outputs/candidates/current/sop-completion-20261021/`，无需另建重复备份。

本批拥有的 Blender 进程已正常退出；用户明确要求无需恢复原工程。主检出既有上游引用及调研改动保留，未纳入本批功能提交。本地分支、工作树与归档标签收尾由 [ARTIFACTS](../../../docs/ARTIFACTS.md#auto-output-20261023) 路由；不 push。
