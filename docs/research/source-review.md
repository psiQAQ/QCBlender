# 用户资料阅读与设计依据

核对日期：2026-09-22。以下五份本地 Markdown 已完整阅读；原件位于用户既有忽略目录，保持原样，不随设计文档复制。此记录保存采用的需求与证据边界，使设计不依赖读者持有这些原件。

## 1. 本地资料

| 文件（相对仓库根目录） | 本次采用的内容 | 验证与决策 |
| --- | --- | --- |
| `docs/GPT-Web-Chat/20260922-1.md` | MolecularNodes 的分子数据与节点展示思路 | 实际结构以子模块源码为准，介绍中的能力描述不是本项目验收 |
| `docs/GPT-Web-Chat/20260922-2.md` | 标量场、科学语义与节点映射之间的分工 | 用 Blender 5.1.1 合成场验证坐标、提面及采样 |
| `docs/GPT-Web-Chat/20260922-3.md` | 独立量子化学插件定位、Gaussian 优先及后续 ORCA | 用户当前明确要求独立单扩展，cbq_core 只作参考 |
| `docs/GPT-Web-Chat/20260922-4.md` | MO、密度、ESP、电荷、偶极、振动/IR 的工作流，字段与节点的区别 | 用户确认这些首版工作流，并明确首版必须内置波函数求值；Cube 是并列入口 |
| `docs/sobereva/谈谈该从Gaussian输出文件中的什么地方读电子能量.md` | 方法特定能量、正文/archive、参考/目标与热校正的区别 | 按原手册、固定解析器源码与真实输出交叉核对；未验证别名保留为候选规则 |

对话中的助手回答作为需求讨论资料。软件支持、格式含义、依赖与版本结论需独立来源；本地文件不证明已经取得远端 ChatGPT 会话的完整导出。当前没有可用的 `read_thread` 接口，原引用 `6ab207d7-5b68-83e8-98b1-cd894bf8bc14` 的完整性仍未远端核对。

读取版本的 SHA-256：

| 文件简称 | SHA-256 |
| --- | --- |
| 20260922-1.md | `ba9ac235267d73b3e0271296d945e3855c877452b83e78c5bb4cbfe2c9632096` |
| 20260922-2.md | `54c99a10e76b805662dabc6b3f0e64eed7e1a11223982ec19fc2974ccc14ef2f` |
| 20260922-3.md | `c4898fe6f771385476dc6e5f4faeefebf31761d12569aad01f7bd6d818dab738` |
| 20260922-4.md | `3241e6fa2bcd587827c405fae5883ba2b7e31da118416dd1dfcf7de7a5a6f4d6` |
| sobereva 能量文章 | `5c2a4e77f226ff4383ef2fe8dbd8ae1697f4490a0d9c688d8abb821e2c06c56c` |

## 2. 设计采用的证据

- MolecularNodes 子模块固定在 `5ad56c9cf33c4f82ceb3ca507d26d0cab6f7203c`，浅克隆；参考数据/节点资产组织。当前源码要求 Blender 5.2，不能整套搬入首发 5.1.1。QCBlender 的体节点路径另做本机实验。
- 本机 ChemBlender 源码核对版本为 `2e94f90419aab186f522fb3b701746839ee8c5c4`；参考 `cbq_core` 的网格、单位、来源、校验与缓存思路。用户选择的交付边界见 [单扩展 ADR](../adr/0001-self-contained-extension.md)。本次未复制或安装其代码。
- Gaussian 格式与 ORCA 后续路径见 [输入研究](gaussian-inputs.md)。Gaussian 官网部分请求失败，实际可读依据是原手册镜像与读取器源码，不宣称完成当前 G16 全部官方资料核查。
- 能量证据见 [方法特定能量](gaussian-energy-semantics.md)：真实 G16 TDDFT 与 CCSD(T) 输出的原始标签已核对；尚未执行 QCBlender 解析。
- Blender 运行时与发布元数据见 [打包研究](blender-extension-packaging.md)：5.1.1 / Python 3.13.9 / NumPy 2.3.4 / OpenVDB 13.0.0 已本机核对。GBasis 0.1.0 的 Windows NumPy 约束不满足基线，兼容源码构建尚待验证。
- [体数据实验](../../tools/probe_volume_nodes.py) 已通过合成正负场、轴序、仿射剪切、等值阈值与第二场三线性采样；最大绝对采样误差约 1.79e-6。它不验证 Gaussian 数值后端或完整科研图像。

## 3. 已确认边界与剩余验证

用户确认单插件、必要依赖 wheels、首版内置求值、非周期实值 HF/DFT（含开壳层/常见基组）、更广方法能量保留，以及 Windows x64 + Blender 5.1.1。优化/IRC、差分、WFN/WFX、相关密度/多态求值及高级分析分期，ORCA 后续。

剩余工作是 [主设计](../QCBLENDER_V1_DESIGN.md) M0–M5 的实施与验收，包含真实样例、后端兼容构建、离线安装、节点/界面、冷重开、性能及独立用户确认。具体库版本、基组组合和每条能量规则只在通过相应证据后声明支持。
