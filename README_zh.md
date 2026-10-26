# QCBlender

[English](README.md) | 简体中文
QCBlender 在 Blender 中显示已有量子化学结果，并对支持的 HF/DFT 波函数生成轨道、密度和静电势网格。结构、等值面、材质与振动可通过原生几何节点调整；科学数据保留来源、单位和计算条件。

当前 manifest 版本为 **0.1.0 Alpha 候选**。公开安装包以 [GitHub Releases](https://github.com/psiQAQ/QCBlender/releases) 实际批准的 prerelease 为准；候选技术检查、组件许可复核和独立试装分别记录，准备状态不代表已公开发布。

## 可以做什么

| 用户任务 | 输入 | 可得到的结果 |
| --- | --- | --- |
| 轨道与电子分布成图 | 含完整基组/MO 的 Gaussian `.fchk/.fch`，或已有 `.cube/.cub` | MO 正负相位、总/Alpha/Beta/自旋密度的等值面和体积显示 |
| 查看静电势分布 | 支持的 FCHK，或已有密度/ESP Cube | 密度表面按 ESP 着色、固定色标、切片、取值及线剖面 |
| 查看分子性质与振动 | Gaussian `.log/.out`、含相应性质的 FCHK | 结构、方法特定能量、电荷、偶极；有正常模式时显示振动，导出原始 IR 频率/强度 |
| 浏览构型变化 | Gaussian 优化日志、有序 IRC FCHK 清单或标准 XYZ | 优化/IRC 逐步构型与记录，XYZ 同原子顺序多帧离散查看 |
| 展示已有外部分析 | 配对 Cube、点/路径文件或结果表 | IGMH/IRI、ESP 极值/面积、NBO/E(2)、AIM、Mayer、ETS-NOCV/NOCV 结果；文件要求见 [导入说明](docs/EXTERNAL_ANALYSIS_IMPORT.md) |

外部分析由相应软件事先完成，QCBlender 读取和显示其结果。插件内置求值不执行新的 SCF 计算。

## 兼容范围与安装

本次实际验证环境为 **Windows x64、Blender 5.1.1**。扩展清单声明的最低 Blender 版本为 5.1.1，最高版本边界为 5.2.0；其他版本和平台未经本次验证。

内置求值限于非周期、实值、全电子 HF/DFT。具体基组、方法及样本边界见 [支持与验证状态](docs/VALIDATION.md)。扩展包含必要的科学库，运行时无需另配 Python 环境。

1. **准备安装包**：使用维护者提供的合格扩展 ZIP，或按 [开发说明](docs/DEVELOPMENT.md) 构建并验证。仓库的源码 ZIP 不能直接作为扩展安装包。
2. **安装扩展**：在 Blender 打开 **编辑（Edit） → 偏好设置（Preferences） → 获取扩展（Get Extensions） → 右上角菜单 → 从磁盘安装（Install from Disk）**，选择扩展 ZIP。
3. **启用并检查运行环境**：在偏好设置左侧切换到 **插件（Add-ons）**，搜索 **QCBlender** 并确认已启用。展开插件偏好设置，点击 **检查科学运行环境（Check Scientific Runtime）**。确认各模块检查通过后，再继续生成轨道。

## 第一次生成轨道图

完成安装和运行环境检查后，准备一份含完整基组和分子轨道（MO）的 FCHK，例如 [P01 氧分子示例](validation/shared/data/public/gaussian-v2/P01/o2-uhf.fchk)。需要逐项核对参数和预期结果时，按 [用户教程的轨道主流程](validation/human/SOP.md#orbital) 操作。

1. **导入 FCHK**：在 **3D 视图（3D Viewport）** 按 **N**，打开 **QCBlender → 导入与导出 → 导入 → 导入 Gaussian / Cube / XYZ**，选择 FCHK。
2. **打开原子视图的设置**：选中导入后生成的原子对象，在 **N 侧栏 → 当前 QC 对象 → 打开对象属性** 核对目标对象名并打开设置。
3. **生成轨道场**：在 **对象属性 → 创建视图与工具 → 计算** 点击 **生成量子化学场**。等待独立科学预检通过后，在弹出的参数对话框中选择 **分子轨道（Molecular orbital）**，核对自旋通道，并按源轨道编号或 HOMO/LUMO 选择轨道。确认网格参数后点击 **确定（OK）**，等待生成完成。
4. **调整轨道显示**：选中新生成的场对象，重新点击 **打开对象属性**，在 **几何表示** 中调整等值和正负相位显示，在属性编辑器的 **材质属性** 中调整颜色。

   > 轨道表面的正负表示轨道相位。

5. **保存工程**：通过 **N 侧栏 → 工程与维护 → 保存与归档 → 保存自包含工程** 保存。应同时得到 `.blend` 和同名 `.qcdata/`；移动工程时两者一起移动。
6. **渲染图片**：设置相机与灯光后，使用 Blender 原生渲染出图。

<details>
<summary>查看默认网格参数与新建视图默认值</summary>

- 生成网格的初值：间距 **0.2 Å**、边距 **3 Å**、内存预算 **512 MiB**。
- 新建原子视图的外层参数 `Quality=3`；新建切片每轴 **201** 点。
- 九个公共节点资产保留原有默认值。

</details>

<details>
<summary>导出数据、参数摘要与设置输出目录</summary>

需要导出数据时，选中包含目标记录的 QC 对象，通过 **N 侧栏 → 导入与导出 → 导出 → 导出数据与参数摘要**，将原始 IR、优化/收敛、IRC、Mayer、采样线剖面、成对场体素与 ESP 面积记录显式保存为 UTF-8 CSV 和 `metadata.json`。操作见 [参数摘要](validation/human/SOP.md#export) 和 [剖面 CSV](validation/human/topics/04-spatial-tools.md)。

每次导出会创建一个名称唯一的结果子目录。未设置导出目录时，已保存的工程使用 `.blend` 所在目录，未保存的工程使用系统 Documents 目录。可在插件偏好设置的 **数据导出目录** 中设置跨工程使用的绝对路径，也可在单次导出时覆盖。

</details>

完整操作按 [用户教程](validation/human/SOP.md) 从安装开始，再按需选择专题。[校验目录](validation/README.md) 集中教程、截图、安装包和数据，并说明人工完成后的打包方法；技术检查见 [Agent 流程](validation/agent/README.md)。

[数据目录](validation/shared/data/README.md) 管理公开、本地限定及回归输入。公开 P01/P03/P04/P05/P06 使用 CC BY 4.0；P02 仅供本机限定案例使用，再分发许可未确认。

## 保存与科学限制

`.blend` 保存节点、材质和布局，`.qcdata/` 保存科学数组、来源和显示缓存。打包前先保存最新工程；只有表面网格无法恢复丢失的科学数组。原始计算输出另行保留。

二进制 `.chk` 须先用已有 Gaussian 的 `formchk` 导出 FCHK。普通 Cube 的物理量和单位可能未知，需依据生成条件显式声明；声明不转换数值。ECP、复轨道、周期体系、ORCA 原生格式和 `.mwfn` 不在当前支持范围内。

标准XYZ支持元素符号/原子序数与三个有限坐标，坐标为Å；同原子数/元素顺序多帧可离散切换。扩展属性、晶胞/PBC、插值和播放不在XYZ范围内；多帧XYZ科学来源关联会明确拒绝，单帧按真实构型核对。

原子间连线由距离推断，不代表计算键级；振动播放速度是展示参数，静态轨道/密度不随之成为时变波函数。科研出图应记录方法、基组、来源摘要、物理量/单位、网格、等值和色标范围。

## 开发者文档

完整分类见[文档索引](docs/README.md)，当前说明、研究依据与历史验收各有独立入口。

| 类别 | 入口与用途 |
| --- | --- |
| 构建与验证 | [开发说明](docs/DEVELOPMENT.md)：环境、构建与同批复验；[验证状态](docs/VALIDATION.md)：精确候选及 Passed / Not Run |
| 架构与数据 | [架构](docs/QCBLENDER_V1_DESIGN.md)、[数据契约](docs/specs/qc-data-contract.md)、[节点契约](docs/specs/geometry-nodes.md)、[单扩展 ADR](docs/adr/0001-self-contained-extension.md) |
| 科学依据 | [领域词汇](CONTEXT.md)、[输入格式研究](docs/research/gaussian-inputs.md)、[Gaussian 能量语义](docs/research/gaussian-energy-semantics.md) |
| 样本与复现 | [数据目录](validation/shared/data/README.md)、[用户教程](validation/human/SOP.md)、[复杂案例参数与复建](docs/COMPLEX_EXAMPLES.md) |
| 开发约定与问题 | [AGENTS](AGENTS.md)、[本地任务规则](docs/agents/issue-tracker.md)、[开发问题记录](docs/DEVELOPMENT_PITFALLS.md) |
| 许可证与历史 | [LICENSE](LICENSE)、[第三方材料](THIRD_PARTY.md)、[CHANGELOG](docs/CHANGELOG.md) |

Alpha 首次操作使用 [P01/MO9 主流程](validation/human/SOP.md)，在“导入与导出 → 导出 → 导出数据与参数摘要”选择“当前视图参数摘要”，保存中文 Markdown 与 JSON。发布方式及门禁见[GitHub 发布研究](docs/research/github-release-workflow.md)。
