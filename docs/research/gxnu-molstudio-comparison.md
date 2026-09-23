# GXNU MolStudio 与 QCBlender 对照（2026-09-23）

## 比较基准与证据边界

- QCBlender：本地 `1007375` 的 M7 技术候选。现有[验证记录](../VALIDATION.md#L1)报告科学回归、离线安装、节点、图像、工程保存等技术检查通过；独立用户验收、外部视觉对照和对外发布仍为 `Not Run`，不能把技术候选称作正式发布。[M5 任务记录](../../.scratch/qcblender-v1/issues/06-m5-release.md#L14)和[M7 任务记录](../../.scratch/qcblender-v1/issues/08-m7-composable-views.md#L3)另存分阶段证据。
- GXNU MolStudio：子模块固定在 `6f3e859020e27d11511b512a7cc47564386b6216`。下文“声明”表示其 [README](../../submodules/GXNU-MolStudio/README_zh.md#L50) 描述，“源码入口”表示此提交存在相关代码；**本次未安装或运行 MolStudio，也未复验其 GUI、数值结果、打包或图片**。源码入口不能自动证明功能正确或可分发。
- 两者定位不同：QCBlender 是使用 Blender 原生节点与 `.blend + .qcdata` 的单扩展，首发环境为 Blender 5.1.1 / Windows x64；MolStudio 是 PyQt5 桌面程序，使用自有 OpenGL 画布，并可调用外部 Multiwfn、VMD、Tachyon。[QCBlender README](../../README.md#L1)、[单扩展 ADR](../adr/0001-self-contained-extension.md#L1)、[MolStudio 主窗口](../../submodules/GXNU-MolStudio/main_window.py#L13)、[MolStudio README 环境表](../../submodules/GXNU-MolStudio/README_zh.md#L101)。

## 当前能力对照

| 方面 | QCBlender 当前开发状态 | GXNU MolStudio 声明及源码入口 | 核查结论 |
| --- | --- | --- | --- |
| 输入与来源 | Gaussian Log/FCHK/Cube 已有读取入口，源摘要、网格/单位、数组摘要与显式关联属于现有数据路径；实际范围见[验证记录](../VALIDATION.md#L5)、[读取器](../../qcblender/readers.py#L124)、[数据保存](../../qcblender/data.py#L124)。 | README 以 FCHK、Cube、日志为主要输入；[主程序](../../submodules/GXNU-MolStudio/main.py#L20)有 FCHK 命令行批处理，[FCHK 解析器](../../submodules/GXNU-MolStudio/fchk_parser.py)、[Cube 读取器](../../submodules/GXNU-MolStudio/marching_cubes.py)、[NBO Log 解析器](../../submodules/GXNU-MolStudio/nbo_parser.py#L50)存在。 | 两者均有文件入口；MolStudio 的跨文件身份、单位与持久化不能从 README 推定。 |
| 内置科学计算 | 非周期实值 HF/DFT 的 MO、电子/自旋密度、ESP 求值由插件和随包库执行；适用组合受[求值入口](../../qcblender/evaluate.py#L35)限制，代表样本数值比较见[验证记录](../VALIDATION.md#L25)。 | README 声称双击轨道生成 Cube、IGMH/IRI、ESP、AIM 等；[IGMH worker](../../submodules/GXNU-MolStudio/igmh_panel.py#L223)、[ESP worker](../../submodules/GXNU-MolStudio/esp_panel.py#L244)、[AIM worker](../../submodules/GXNU-MolStudio/aim_panel.py#L365)实际调用 Multiwfn；[ETS-NOCV 面板](../../submodules/GXNU-MolStudio/etsnocv_panel.py#L3)也依赖该程序。 | MolStudio 主要是外部计算与本机可视化工作流；本次未验证其输出数值。 |
| 分析数据 | 现有电荷、偶极、振动/IR、双场/切片/图例及体积场显示已通过对应技术检查；IGMH、AIM、NBO、IRC 键级和 ETS-NOCV 尚不属于该基准的已验收能力。[验证矩阵](../VALIDATION.md#L31)。 | [IGMH 复合场及散点图](../../submodules/GXNU-MolStudio/igmh_panel.py#L105)、[ESP 极值和面积分布](../../submodules/GXNU-MolStudio/esp_panel.py#L116)、[AIM CP/路径文本](../../submodules/GXNU-MolStudio/aim_panel.py#L265)、[NBO 与 E(2) Log 解析](../../submodules/GXNU-MolStudio/nbo_parser.py#L50)、[IRC 逐步 FCHK/Mayer](../../submodules/GXNU-MolStudio/irc_panel.py#L102)、[NOCV 对表](../../submodules/GXNU-MolStudio/etsnocv/nocv_analyzer.py#L18)均有源码入口。 | 这些入口提供可借鉴的**结果类型和交互流程**，不等于 QCBlender 已完成移植。MolStudio 的 NBO 解析器还有按能量找最近 canonical MO 的逻辑，QCBlender 不采用这种身份推断。[源码](../../submodules/GXNU-MolStudio/nbo_parser.py#L235)。 |
| 显示 | Blender 原生可组合几何节点、公共等值面/体积雾、独立显示层、裁剪与游标采样已有技术证据。[验证矩阵](../VALIDATION.md#L32)、[视图入口](../../qcblender/blender/views.py#L46)、[图层入口](../../qcblender/blender/layers.py#L6)。 | README 声称深度剥离、样式和灯光控制；自有 [`QOpenGLWidget` 画布](../../submodules/GXNU-MolStudio/ovcanvas/_glwidget.py#L1669)、深度剥离目标类及样式表确有入口。[画布源码](../../submodules/GXNU-MolStudio/ovcanvas/_glwidget.py#L1293)。传统渲染模式另有 VMD/Tachyon 路径。[主窗口](../../submodules/GXNU-MolStudio/main_window.py#L2720)。 | 渲染架构不同，不以复制画布替换 Blender 节点。 |
| 交互 | Blender 侧栏导入、异步任务、节点编辑、图层管理、撤销/重做和工程重开有技术验收；GUI 证据仅属开发实例。[界面入口](../../qcblender/blender/ui.py#L118)、[验证矩阵](../VALIDATION.md#L35)。 | PyQt5 多面板主窗口集成 ESP、IGMH、AIM、NBO、IRC、ETS-NOCV；主入口还提供 CLI 批处理。[主窗口](../../submodules/GXNU-MolStudio/main_window.py#L641)、[CLI](../../submodules/GXNU-MolStudio/main.py#L20)。隐藏全部 H、保留指定 H、恢复显示在窗口源码中有状态与动作入口。[快捷控制](../../submodules/GXNU-MolStudio/main_window.py#L3974)。 | 借鉴分析面板的信息组织和原子显示快捷控制；保留 Blender 现有交互体系。 |
| 依赖与打包 | 扩展目标是离线安装；必要 Python wheels 随包，NumPy/OpenVDB 来自 Blender，运行时不执行 pip。[第三方清单](../../THIRD_PARTY.md#L1)、[验证记录](../VALIDATION.md#L18)。 | README 列 PyQt5、PyOpenGL、NumPy、PyMCubes、matplotlib 和外部 Multiwfn；VMD/Tachyon 用于传统渲染。[环境表](../../submodules/GXNU-MolStudio/README_zh.md#L101)。有 [PyInstaller spec](../../submodules/GXNU-MolStudio/OrbitalViewer.spec#L1)，但含机器特定路径/系统 DLL 配置。 | MolStudio README 的 `pip install` 和打包命令是使用说明，本次未执行；不把其 EXE 可分发性记为已验证。 |
| 测试与发布 | 当前候选的平台、测试结果、`Passed`/`Not Run` 已明确列出；独立用户及发布仍待人工流程。[验证记录](../VALIDATION.md#L20)。 | README 展示 1.0、截图、CLI 与打包说明；当前源码树未见自动化测试目录或可核对的运行报告。本次也未运行其程序。[README](../../submodules/GXNU-MolStudio/README_zh.md#L1)、[打包说明](../../submodules/GXNU-MolStudio/README_zh.md#L193)。 | 无法据版本徽章或截图断言其功能、数值和发行质量通过本地复验。 |

## README 与源码需要分开的地方

- MolStudio README 把 DI、ESM 列为功能，并在结构树写出 `di_analysis_panel.py`、`energy_span_panel.py`，但固定提交的源码树及主窗口集成入口未见这些模块；本比较不列为已实现能力。[README 功能表](../../submodules/GXNU-MolStudio/README_zh.md#L85)、[README 结构树](../../submodules/GXNU-MolStudio/README_zh.md#L180)、[主窗口分析面板导入区](../../submodules/GXNU-MolStudio/main_window.py#L70)。
- MolStudio README 引用 `THIRD-PARTY-NOTICES.md`，但该文件不在此固定提交的源码树。其根 [LICENSE](../../submodules/GXNU-MolStudio/LICENSE#L1)是 GPLv3 文本；README 自称 GPLv3-only，第三方组件许可清单的完整性需在分发前另核。本项目自身许可和随包归属以 [LICENSE](../../LICENSE#L1)与[第三方清单](../../THIRD_PARTY.md#L1)为准，借鉴时不直接复制 MolStudio 源码。[MolStudio README 许可段](../../submodules/GXNU-MolStudio/README_zh.md#L243)。

## 本轮已确认的功能取舍

在现有科学数据存储与 Blender 节点上，分成九个独立验收片：①隐藏全部氢/保留指定氢/恢复显示，②IGMH/IRI 几何场、着色场与散点图，③ESP 极值点和面积分布，④指定 Gaussian Log 计算段的 NBO/E(2)，⑤AIM 临界点/键路径/可选属性，⑥用户明确排列的 IRC FCHK 构型与能量路径，⑦按 IRC 步序与原子编号关联的 Mayer 键级，⑧ETS-NOCV 成对能量表，⑨与表格 pair 明确关联的 NOCV 形变密度 Cube。全部仅导入**用户已有的外部分析结果**，逐文件确认角色、单位、计算/构型关系并保存来源摘要；功能通过各自真实样本、错误输入、Blender 显示与冷重开验证后才能记为完成。[QCBlender 数据契约](../specs/qc-data-contract.md#L9)、[节点设计](../QCBLENDER_V1_DESIGN.md#L155)。

本轮不引入运行时 Multiwfn/VMD/Tachyon、不移植 Qt/OpenGL 画布、不直接复制 MolStudio 源码；灯光/相机预设、自动出图、DI/ESM 也不纳入九片。这样保持[单扩展 ADR](../adr/0001-self-contained-extension.md#L1)已确认的安装与显示边界。独立用户验收和对外发布仍由 M5 流程处理。
