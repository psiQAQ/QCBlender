# QCBlender

[English](README.md) | 简体中文

QCBlender 让你能在 Blender 中直接加载并可视化量子化学计算结果。它支持由 HF/DFT 波函数即时生成分子轨道、电子密度和静电势空间网格；分子结构、等值面、材质以及分子振动均可通过 Blender 原生几何节点（Geometry Nodes）交互调节，完整保留物理量单位与数据溯源。

**QCBlender 0.1.0 Alpha Preview** 支持 Windows x64 与 Blender 5.1.1。发布包与校验状态详见 [GitHub Releases](https://github.com/psiQAQ/QCBlender/releases/tag/v0.1.0)。

---

## 目录结构

```text
QCBlender/
├── qcblender/              # 插件源码核心包
│   ├── *.py                # 科学求值、文件解析与数据模型模块
│   └── blender/            # 操作符、界面、材质与几何节点集成
├── docs/                   # 开发者文档、接口规范与设计决策（ADR）
│   ├── specs/              # 数据契约与几何节点资产规范
│   ├── research/           # 量化格式调研与物理量语义定义
│   └── adr/                # 关键架构决策记录
├── validation/             # 用户教程、验证脚本与样例数据
│   ├── human/              # 人工实操 SOP 及 12 个专题指南、截图与渲染图
│   ├── agent/              # 自动化验收脚本与执行证据
│   └── shared/data/        # 公开示例、本地测试与回归基准数据集
└── tools/                  # 开发辅助脚本与 CLI 流程工具
```

---

## 核心功能

| 功能分类 | 输入数据 | 输出与呈现效果 |
| --- | --- | --- |
| 分子轨道与电子密度 | 含完整基组/MO 的 Gaussian `.fchk/.fch`，或已有 `.cube/.cub` 网格 | 正负相位等值面、总/Alpha/Beta/自旋密度的等值面与体积雾呈现 |
| 静电势（ESP）分析 | 支持的 FCHK 文件，或密度/ESP Cube 网格 | 密度表面按 ESP 映射着色、固定色阶图例、2D 截面切片、空间探针与沿线取值剖面 |
| 分子性质与振动分析 | Gaussian `.log/.out`，或包含相应性质的 FCHK | 分子结构、指定计算方法的能量、电荷与偶极矩；交互播放简正振动模式，导出原始红外（IR）频率与强度 |
| 几何构型变化与轨迹 | Gaussian 结构优化日志、有序 IRC FCHK 列表或标准 XYZ 文件 | 优化/IRC 逐步几何构型与收敛曲线，多帧 XYZ 结构离散浏览 |
| 外部分析成果展示 | 配对 Cube 文件、点/路径数据或分析结果表 | IGMH/IRI 弱相互作用、ESP 极值点与表面积统计、NBO/E(2)、AIM 拓扑关键点与键径、Mayer 键级及 ETS-NOCV 轨道对（详见 [外部分析导入指南](docs/EXTERNAL_ANALYSIS_IMPORT.md)） |

> [!NOTE]
> 外部分析需要预先由相应专业量化软件完成，QCBlender 负责读取并呈现结果；插件内置计算模块不执行自洽场（SCF）能量迭代。

---

## 兼容环境与安装方法

- **验证环境**：Windows x64、Blender 5.1.1（插件清单最低版本为 5.1.1，最高版本边界为 5.2.0）；其他版本和平台不在本次验证范围内。
- **计算适用范围**：非周期性、实数波函数、全电子 HF 与 DFT 体系。具体支持的基组与泛函见 [验证状态](docs/VALIDATION.md)。
- **运行依赖**：插件已内置必要的科学计算动态库与 Wheels，无需单独配置系统 Python 环境。

### 方式一：从 ZIP 安装（推荐）

1. 从 [GitHub Releases](https://github.com/psiQAQ/QCBlender/releases/tag/v0.1.0) 下载扩展包 `qcblender-0.1.0.zip`，并与同页的 `SHA256SUMS.txt` 核对校验和（切勿直接安装 GitHub 源码归档 ZIP）。
2. 打开 Blender，点击 **编辑（Edit） → 偏好设置（Preferences） → 获取扩展（Get Extensions） → 右上角菜单 → 从磁盘安装（Install from Disk）**，选中下载的 ZIP 文件。
3. 在偏好设置左侧切换至 **插件（Add-ons）**，搜索 **QCBlender** 并勾选启用。展开插件面板，点击 **检查科学运行环境（Check Scientific Runtime）**。各模块均通过后即可开始使用。

### 方式二：配置远程扩展仓库安装

1. 打开 **编辑（Edit） → 偏好设置（Preferences） → 系统（System） → 网络（Network）**，勾选 **允许在线访问（Allow Online Access）**。
2. 进入 **获取扩展（Get Extensions） → 仓库（Repositories） → ＋ → 添加远程仓库（Add Remote Repository）**，填入仓库地址 `https://notes.psiqaq.cn/QCBlender/index.json` 并添加。
3. 同步扩展列表后搜索 **QCBlender** 安装并启用，随后按上述步骤执行 **检查科学运行环境**。

同一 Release 页面还提供配套教程包 `qcblender-tutorial-0.1.0.zip`，内含完整中文 SOP、各专题文档、截图和参考输入文件。解压后请保留原始目录层级。

---

## 快速上手：生成第一张分子轨道图

以教程包中的 [P01 氧分子示例文件](validation/shared/data/public/gaussian-v2/P01/o2-uhf.fchk) 为例。该 FCHK 含完整基组和分子轨道；需要固定 Alpha MO9 的操作与预期结果时，按[轨道主流程](validation/human/SOP.md#orbital)进行。轨道表面的正负表示波函数相位。

1. **导入波函数**：在 3D 视图中按 `N` 呼出侧边栏，打开 **QCBlender → 导入与导出 → 导入 → 导入 Gaussian / Cube / XYZ**，选中 FCHK 文件。
2. **打开对象设置**：选中视口中生成的原子对象，在 **当前 QC 对象** 面板点击 **打开对象属性**。
3. **计算轨道场**：在 **创建视图与工具 → 计算** 区域点击 **生成量子化学场**。等待独立科学预检通过后，在参数对话框中：
   - 物理量选择 **分子轨道（Molecular orbital）**，选择 **Alpha** 自旋通道。
   - 按 HOMO/LUMO 索引或填入源轨道编号选中目标轨道。
   - 确认计算网格（默认间距 0.2 Å、外扩边距 3 Å），点击 **确定（OK）** 开始计算。
4. **调整显示效果**：选中新生成的场对象并打开其属性，在 **几何表示** 中调节等值面阈值（Isovalue）与正负相位开关；在 Blender 原生 **材质属性** 面板中自定义表面颜色与透明度。
5. **保存工程**：在 N 侧栏 **工程与维护 → 保存与归档** 中点击 **保存自包含工程**。系统会生成 `.blend` 文件和同名的 `.qcdata/` 数据缓存目录。
6. **渲染出图**：布置好相机与场景灯光，按 `F12` 调用 Blender 原生渲染引擎出图。

<details>
<summary>查看网格与视图初始默认值</summary>

- 默认计算网格：点间距 **0.2 Å**，边界外扩 **3 Å**，单次内存预算 **512 MiB**。
- 原子视图默认细分等级 `Quality=3`；空间切片视图单轴点数为 **201**。
- 几何节点标准资产均采用工程预设默认参数。

</details>

<details>
<summary>导出计算数据与参数摘要</summary>

选中包含目标记录的 QC 对象，点击 **N 侧栏 → 导入与导出 → 导出 → 导出数据与参数摘要**。可选数据类型随对象已有记录变化：原始 IR、优化能量与收敛记录、IRC、Mayer 键级、采样线剖面、成对场体素及 ESP 面积均可导出为 UTF-8 CSV 和 `metadata.json`；**当前视图参数摘要**则生成 `view-summary.md` 与 `metadata.json`。具体操作见[共同导出步骤](validation/human/SOP.md#export)。

每次导出会自动在工程所在目录（未保存时为用户文档目录）生成独立文件夹，亦可在插件偏好设置中指定全局默认导出路径。

</details>

---

## 工程保存与注意事项

- **数据存放规范**：`.blend` 工程文件记录场景拓扑、材质节点与视口布局；同名 `.qcdata/` 目录存放计算网格二进制数组与溯源信息。迁移或归档时两者必须一同存放，切勿拆分或单独重命名。
- **文件格式要求**：高斯二进制 `.chk` 文件须预先用 Gaussian 自带的 `formchk` 工具转为文本 `.fchk`。普通 Cube 若量名或单位未知，导入后使用 **声明 Cube 物理量与单位**，依据生成条件填写；声明不转换数组数值。
- **功能边界**：当前版本不支持周期性晶体体系（PBC）、有效核心势（ECP）、复数波函数、ORCA 原生格式以及 Multiwfn `.mwfn` 格式。
- **科学呈现须知**：视口中的原子连线仅基于共价半径估算，不代表严谨的量子力学键级；振动动画用于直观查看振动方向，不会将静态波函数转变为含时演化。

标准 XYZ 使用元素符号或原子序数及 Å 单位有限坐标。同原子数、同元素顺序的多帧可离散切换，不支持插值和播放；多帧 XYZ 不能作为静态科学来源关联，单帧关联按真实构型核对。

归档前保存最新工程；归档读取磁盘上的 `.blend` 及配套 `.qcdata/`。原始计算输出另行保留。科研出图应记录方法、基组、来源身份、物理量与单位、网格、等值和色标范围。[当前数据说明](validation/shared/data/public/NOTICE.md)区分自有公开样本和历史受限原件；候选检查与独立人工／科研验收分别记录，见[验证状态](docs/VALIDATION.md)。

---

## 开发者与文档导航

完整文档架构见 [文档索引](docs/README.md)：

| 分类 | 核心入口 |
| --- | --- |
| 编译构建与测试验证 | [开发指南](docs/DEVELOPMENT.md) 与 [验证状态一览](docs/VALIDATION.md) |
| 系统架构与规范契约 | [架构设计](docs/QCBLENDER_V1_DESIGN.md)、[数据契约](docs/specs/qc-data-contract.md)、[几何节点规范](docs/specs/geometry-nodes.md)、[单扩展架构 ADR](docs/adr/0001-self-contained-extension.md) |
| 量化理论与研究依据 | [领域术语模型](CONTEXT.md)、[高斯输入格式调研](docs/research/gaussian-inputs.md)、[高斯能量语义](docs/research/gaussian-energy-semantics.md) |
| 教程指引与验证用例 | [人工实操 SOP](validation/human/SOP.md)、[公共数据集说明](validation/shared/data/README.md)、[复杂案例参数复现](docs/COMPLEX_EXAMPLES.md)、[Agent 自动化流水线](validation/agent/README.md) |
| 协作规则与避坑指南 | [Agent 协作规则](AGENTS.md)、[本地 Issue 规则](docs/agents/issue-tracker.md)、[开发常见问题排查](docs/DEVELOPMENT_PITFALLS.md) |
| 开源许可与更新历史 | [LICENSE](LICENSE)、[第三方软件与引用声明](THIRD_PARTY.md)、[版本变更记录](docs/CHANGELOG.md) |

Alpha 首次操作使用 [P01/MO9 主流程](validation/human/SOP.md)，在“导入与导出 → 导出 → 导出数据与参数摘要”选择“当前视图参数摘要”，保存中文 Markdown 与 JSON。发布方式及门禁见[GitHub 发布研究](docs/research/github-release-workflow.md)。
