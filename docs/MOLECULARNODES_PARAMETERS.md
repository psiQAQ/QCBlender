# MolecularNodes 参数交互技术验收

本记录属于 Agent 技术验收。独立人工验收与外部视觉对照继续后置；固定 SOP、结果浏览、优化轨迹和 VMD 候选不被覆盖。

| 工作包 | 状态 | 证据 |
| --- | --- | --- |
| A 固定局部选择 | Passed | `outputs/molecularnodes-parameters/01-selection-r2/qualification.json` |
| B 源编号和真实步测量标注 | Passed | `outputs/molecularnodes-parameters/02-annotations/qualification.json` |
| C 图例排版 | Not Run | 待主代理集成验收 |
| 最终候选 C01–C13 / N01–N18 | Not Run | 待全部功能集成 |

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

## 验收修复记录

A 对话框加宽并分列显示。验收工具复用现有 Windows 长路径函数，修复便携目录复制和数组摘要遍历；实际安装、GUI 和工程生成使用同一普通用户权限，避免沙箱生成资料无法被桌面进程读取。修复后全部相关检查重新执行。
