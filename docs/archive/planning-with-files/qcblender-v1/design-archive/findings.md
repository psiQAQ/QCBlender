# Findings

## 当前用户决策

- 单 Blender 扩展，内部通用 QC 数据转换；cbq_core 只参考，不安装外部科学环境。
- 首版内置 MO/密度/自旋/ESP 求值，电荷、偶极、振动/IR 联动；优化/IRC、差分、WFN/WFX 及高级分析后续。
- 数值范围为非周期实值 HF/DFT（含开壳层/常见基组）；MP2、双杂化、CCSD(T)、TD 等已读取能量保留身份，相关密度/多态求值后续。
- 首发 Windows x64 + Blender 5.1.1，必要依赖随 wheels 分发；首版交付离线 ZIP，官方平台发布未在当前请求内。
- setup 已按用户审阅草案完成：AGENTS.md，docs/agents/ 三份配置；本地 .scratch/<feature>/ 任务，五默认标签，single-context。CONTEXT.md 和 docs/adr/0001-self-contained-extension.md 已建立。

## 已核对事实

- MolecularNodes gitlink 为 5ad56c9cf33c4f82ceb3ca507d26d0cab6f7203c，浅克隆且未修改；其当前源码最低 Blender 5.2、Python 3.13，资产使用 nodebpy；许可证 GPL-3.0-or-later。
- ChemBlender 只读核对 HEAD 为 2e94f90419aab186f522fb3b701746839ee8c5c4，既有量化读取能力可参考；其声明不代替本任务运行验收。
- 四份 docs/GPT-Web-Chat 对话与 sobereva 文章已完整读完；内容摘要及哈希见 docs/research/source-review.md。未获得远端会话完整性证明，当前无 read_thread 工具。
- Blender 本机 5.1.1，Python 3.13.9、NumPy 2.3.4、OpenVDB 13.0.0；自带 Python 可直接启动，生产后台任务路径未实现。
- 合成场原生提面、斜轴与平移、正负面、阈值改变、第二场三线性采样 Passed，最大误差 1.79e-6；真实输入、渲染/GUI/安装 Not Run。
- GBasis 0.1.0 Windows NumPy<2 与宿主冲突；固定开发源码支持 NumPy2 但需原生构建。兼容 wheel 构建、离线加载与 AO/MO/密度/ESP 科学验收是 M0 必过条件。
- 原手册、固定 cclib1.8.1 源码及 G16 TD/CCSD(T) 样例证明须按计算段/方法/求值/几何/态选择能量；不能统一取最后 SCF 或直接 zip 数组。

## 交付位置

- docs/QCBLENDER_V1_DESIGN.md：V01–V08，M0–M5，首版与后续边界及验收。
- docs/specs/qc-data-contract.md：内部类型、单位、AO/MO/密度/ESP、持久化与任务。
- docs/specs/geometry-nodes.md：属性、实际 socket、配方与显示边界。
- docs/research/：输入、能量、打包与来源阅读记录。
- tools/probe_volume_nodes.py：可复现的 Blender 合成场行为验证。

外部资料仅作研究数据；任何样例/版本支持必须附对应证据。旧方案的取舍仅在 ADR/进度历史保留。
