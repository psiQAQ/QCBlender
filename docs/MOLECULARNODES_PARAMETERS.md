# MolecularNodes 参数交互技术验收

> 产物状态更新（2026-09-29）：本页是历史技术验收记录。候选 ZIP、生成工程及图像已纳入用户批准的清理范围；日志、摘要和历史 Passed 保留，二进制可用性以 [清理记录](acceptance/storage-cleanup.md) 为准。本文中“可重开”“保留候选”等描述只代表验收当时状态。当前可用的用户工程单独保存，后续演示从集中输入重建。

本记录属于 Agent 技术验收。独立人工验收与外部视觉对照继续后置；固定 SOP、结果浏览、优化轨迹和 VMD 候选不被覆盖。

| 工作包 | 状态 | 证据 |
| --- | --- | --- |
| A 固定局部选择 | Passed | `outputs/molecularnodes-parameters/01-selection-r2/qualification.json` |
| B 源编号和真实步测量标注 | Passed | `outputs/molecularnodes-parameters/02-annotations/qualification.json` |
| C 图例排版 | Passed | `outputs/molecularnodes-parameters/03-legend/qualification.json` |
| 最终候选 C01–C13 / N01–N18 | Passed | `outputs/molecularnodes-parameters/03-legend/final-sop/final-sop-summary.json` |

## A 候选

- 源码：`a333721b93f8b61defc6ee482f75c1f38de7d6e6`。
- ZIP：`outputs/molecularnodes-parameters/01-selection-r2/dist/qcblender-0.0.1.zip`。
- SHA-256：`39f40814fb55fee7474269f5278053b5bdfd6774ee5a644f0196ac96201921bb`。
- Blender 5.1.1，独立简体中文配置；源码、ZIP、安装副本和 wheel 摘要一致。
- Passed：53 项科学回归，非连续编号、邻域、集合运算、氢掩码求交、独立局部层、真实优化第 4 步和 IRC 第 2 步的固定成员、显式重新计算、错误拒绝、当前版本视图保留优化步。
- Computer Use 确认新增对话框、选择、撤销/重做和空结果提示；MCP 核对成员、节点和数组摘要。原工程及移动后的工程分别由新进程重开并渲染。
- 既有参数复制及 Gaussian 多计算段/振动检查 Passed，均绑定本次候选。
- 可重开工程：`outputs/molecularnodes-parameters/01-selection-r2/features/evidence.blend`；关联 `.qcdata` 与移动副本位于同一证据目录。

## B 候选

- 产品源码：`fc78c2f`；后续验收脚本提交不改变产品源码，资格报告在 `9b9a701` 核对源码与候选一致。
- ZIP：`outputs/molecularnodes-parameters/02-annotations/dist/qcblender-0.0.1.zip`。
- SHA-256：`3d50144f62ea2dfaf59bc924326bedd5f667654e64defd0c93f4b55f04982365`。
- Passed：58 项科学回归、A 包回归、参数复制、Gaussian 两段/振动、标注四类和默认精度、真实优化/IRC 换步、源身份和锚点、非均匀缩放与真实振动不改变测量。
- 原子标注使用独立 FONT/CURVE 和材质。标注损坏时，换步在修改网格前拒绝；计算退化时显示 undefined 和原因。复制、编辑、删除及当前版本视图保留计算步和选择的检查 Passed。
- Computer Use 确认距离对话框、创建、朝向相机、撤销与重复编号错误；MCP 检查撤销/重做后的对象和距离 `1.087830245524686 Å`。
- `annotations/evidence.blend` 及对应 `.qcdata` 可重开，原地和移动副本的新进程重开、渲染及数组摘要检查 Passed。

## C 候选

- 产品源码：`082d81e`；验收脚本在 `faeab84` 更新，资格检查确认产品源码与候选一致。
- ZIP：`outputs/molecularnodes-parameters/03-legend/dist/qcblender-0.0.1.zip`。
- SHA-256：`662ca041ca01fd128da82a476d480de5b9ae02191ac8741b1bb5e3c0309622a5`。
- Passed：58 项科学回归、2 项纯图例布局测试、A/B 功能回归、参数复制、Gaussian 多段/振动、干净配置安装及源码/ZIP/安装副本一致性。
- `legend/checks.json` 核对默认布局、长度/宽度/字号/精度、横竖方向和旋转；ESP、Mulliken 电荷与带符号 MO 的标题、单位、三点范围和色带保持一致。替换着色场保留布局，复制显示参数保留目标布局。
- Computer Use 确认竖向控件、标准旧图升级及自定义旧图拒绝提示；MCP 核对新输入和原图保留。`legend/evidence.blend` 与关联 `.qcdata` 原地及移动冷重开、渲染、数组摘要检查 Passed。

## 最终 SOP

最终 ZIP 使用上列 C 候选。35 个固定样本摘要一致；所有工程及移动副本由各自的新 Blender 进程重开、重新渲染，核对关联目录、节点输入和科学数组摘要。记录型案例保留 Computer Use 原生面板实拍；重复操作、源值与节点检查通过 MCP 执行。完整证据矩阵见 [技术汇总](../outputs/molecularnodes-parameters/03-legend/final-sop/final-sop-summary.md)。

| 案例 | 导入 | 源数值与单位 | 节点前后 | PNG | 保存重开 | 移动冷重开 |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | Passed | Passed | Passed | Passed | Passed | Passed |
| C02 | Passed | Passed | Passed | Passed | Passed | Passed |
| C03 | Passed | Passed | Passed | Passed | Passed | Passed |
| C04 | Passed | Passed | Passed | Passed | Passed | Passed |
| C05 | Passed | Passed | Passed | Passed | Passed | Passed |
| C06 | Passed | Passed | Passed | Passed | Passed | Passed |
| C07 | Passed | Passed | Passed | Passed | Passed | Passed |
| C08 | Passed | Passed | Passed | Passed | Passed | Passed |
| C09 | Passed | Passed | Passed | Passed | Passed | Passed |
| C10 | Passed | Passed | Passed | Passed | Passed | Passed |
| C11 | Passed | Passed | Passed | Passed | Passed | Passed |
| C12 | Passed | Passed | Passed | Passed | Passed | Passed |
| C13 | Passed | Passed | Passed | Passed | Passed | Passed |

N01–N18 全部 Passed；逐项“原值 → 新值 → 可见变化”及证据路径保存在同一汇总中。C07 错配网格、C13 错误 pair/自旋均拒绝且场景不变。图例布局撤销/重做另见 `03-legend/legend/undo-redo.json`。

本地技术标签：`qa/mn-parameters-20260928-01`、`02`、`03`；独立人工签署和外部软件视觉对照均为 Not Run，不构成发布批准。

## 验收修复记录

A 对话框加宽并分列显示。验收工具复用现有 Windows 长路径函数，修复便携目录复制和数组摘要遍历；实际安装、GUI 和工程生成使用同一普通用户权限，避免沙箱生成资料无法被桌面进程读取。修复后全部相关检查重新执行。

最终 SOP 适配新的图例布局输入，补齐原先由 GUI 执行的着色场绑定和记录导入；清理 C04 复跑场景残留文字后重新渲染并执行双冷重开。C04 ESP 超过 MCP 300 秒等待上限时，核对持续运行的原任务并读取其成功结果，未重复计算。Computer Use 的 JPEG 原图保留，PNG 由 Windows 原生编解码器转存；截图格式和文件名缺项修正后，严格汇总为 13/13 案例、18/18 参数检查 Passed。
