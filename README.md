# QCBlender

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

实际验证环境为 **Windows x64、Blender 5.1.1**。扩展清单声明最低 5.1.1、最高版本边界 5.2.0；其他版本和平台未经本次验证。内置求值限非周期、实值、全电子 HF/DFT，具体基组、方法及样本边界见 [支持与验证状态](docs/VALIDATION.md)。

目前需使用维护者提供或按下方开发说明构建并验证的扩展 ZIP。取得合格包后，在 Blender **Preferences → Get Extensions → 菜单 → Install from Disk** 安装并启用。扩展包含必要科学库，运行时无需另配 Python 环境；仓库的源码 ZIP 不能直接作为扩展安装包。

## 第一次生成轨道图

1. 安装并启用合格包，在 Add-ons 的 QCBlender 偏好设置中运行 **Check Scientific Runtime**。
2. 在 3D Viewport 按 **N**，打开 **QCBlender → 工作流 → 导入 Gaussian / Cube / XYZ**，选择含基组和轨道的 FCHK。
3. 选中新原子视图，点击 **生成量子化学场**，等待独立科学预检通过并打开参数对话框，再选择 **Molecular orbital**，核对自旋通道和源轨道编号或 HOMO/LUMO，生成场。
4. 在对象属性中调整等值和正负相位，在材质属性中调整颜色；正负表示轨道相位。生成网格初值为0.2 Å、边缘3 Å、预算512 MiB；新建原子外层Quality=3，新切片每轴201点。九个公共节点资产的原有默认值保留。
5. 在 **N 侧栏 → 工程与诊断 → 保存自包含工程** 保存 `.blend` 和同名 `.qcdata/`；两者一起移动。设置相机与灯光后可用 Blender 原生渲染出图。

安装、样本获取和 C01–C13 完整操作按 [跟随教程与独立人工验收 SOP](docs/v1-acceptance/SOP.md) 执行；[用户指南](docs/USER_GUIDE.md) 提供入口索引。[来源目录](docs/v1-acceptance/SOURCES.md) 记录公开与需原站获取的材料。v2样本包的P01/P03/P04/P05/P06数据使用CC BY 4.0；C02/C06的P02日志需按原站条件单独获取、核对SHA，其再分发许可尚未确认。样本包目前本地交付，取得方式见来源目录。独立人工复做状态由 SOP 记录，不从技术报告继承。

原始 IR、优化/收敛、IRC、Mayer、采样线剖面、成对场体素与ESP面积记录可在 **N侧栏 → 工程与诊断 → 导出数据** 显式保存为UTF-8 CSV和metadata.json；每次创建唯一结果子目录。默认目录为已保存.blend的父目录，否则为系统Documents；Addon偏好“数据导出目录”可设置跨工程绝对路径，单次导出可覆盖。详见[SOP 0.5](docs/v1-acceptance/SOP.md#05-显式数据导出)。

## 保存与科学限制

`.blend` 保存节点、材质和布局，`.qcdata/` 保存科学数组、来源和显示缓存。打包前先保存最新工程；只有表面网格无法恢复丢失的科学数组。原始计算输出另行保留。

二进制 `.chk` 须先用已有 Gaussian 的 `formchk` 导出 FCHK。普通 Cube 的物理量和单位可能未知，需依据生成条件显式声明；声明不转换数值。ECP、复轨道、周期体系、ORCA 原生格式和 `.mwfn` 不在当前支持范围内。

标准XYZ支持元素符号/原子序数与三个有限坐标，坐标为Å；同原子数/元素顺序多帧可离散切换。扩展属性、晶胞/PBC、插值和播放不在XYZ范围内；多帧XYZ科学来源关联会明确拒绝，单帧按真实构型核对。

原子间连线由距离推断，不代表计算键级；振动播放速度是展示参数，静态轨道/密度不随之成为时变波函数。科研出图应记录方法、基组、来源摘要、物理量/单位、网格、等值和色标范围。

## 开发者文档

| 类别 | 入口与用途 |
| --- | --- |
| 构建与验证 | [开发说明](docs/DEVELOPMENT.md)：环境、构建与同批复验；[验证状态](docs/VALIDATION.md)：精确候选及 Passed / Not Run |
| 架构与数据 | [架构](docs/QCBLENDER_V1_DESIGN.md)、[数据契约](docs/specs/qc-data-contract.md)、[节点契约](docs/specs/geometry-nodes.md)、[单扩展 ADR](docs/adr/0001-self-contained-extension.md) |
| 科学依据 | [领域词汇](CONTEXT.md)、[输入格式研究](docs/research/gaussian-inputs.md)、[Gaussian 能量语义](docs/research/gaussian-energy-semantics.md) |
| 样本与复现 | [来源与许可目录](docs/v1-acceptance/SOURCES.md)、[跟随教程与独立人工验收 SOP](docs/v1-acceptance/SOP.md)、[复杂案例参数与复建](docs/COMPLEX_EXAMPLES.md) |
| 开发约定与问题 | [AGENTS](AGENTS.md)、[本地任务规则](docs/agents/issue-tracker.md)、[开发问题记录](docs/DEVELOPMENT_PITFALLS.md) |
| 许可证与历史 | [LICENSE](LICENSE)、[第三方材料](THIRD_PARTY.md)、[CHANGELOG](docs/CHANGELOG.md) |

首次公开 Alpha 使用 [P01/MO9 短 SOP](docs/v1-acceptance/SOP.md#alpha-首次出图与短验收)，在“工程与诊断 → 导出数据与参数摘要”选择“当前视图参数摘要”，保存中文 Markdown 与 JSON。发布方式及门禁见[GitHub 发布研究](docs/research/github-release-workflow.md)。
