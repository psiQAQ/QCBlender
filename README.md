# QCBlender

面向量子化学与计算化学结果的单个 Blender 扩展，以几何节点控制结构、轨道、空间场与振动。首版设计支持 Gaussian Log/FCHK/Cube，内置 HF/DFT 波函数求值；必要科学库随包分发，用户无需配置外部 Python。首发目标为 Windows x64 + Blender 5.1.1，后续扩展 ORCA 和其它平台。

当前为 `0.0.1` 开发验收候选：已接通 Gaussian 导入、内置场求值、几何节点、ESP 映射/切片、电荷/偶极、振动/IR 和可迁移工程。随包科学运行库已通过全新 Blender 配置离线安装；独立用户验收及对外发布尚未完成。

本地安装包：`outputs/dist/qcblender-0.0.1.zip`。在 Blender 的 Preferences → Get Extensions → 菜单 → Install from Disk 选择该 ZIP 并启用，进入 3D Viewport 的 QCBlender 侧栏。用户不需要安装 Python、pip 或 Gaussian；从二进制 CHK 导出 FCHK 时才需要自己已有的 Gaussian `formchk`。

- [安装与操作指南](docs/USER_GUIDE.md)
- [当前支持范围与验收结果](docs/VALIDATION.md)
- [开发构建和复现命令](docs/DEVELOPMENT.md)

- [首版范围、架构与开发路线](docs/QCBLENDER_V1_DESIGN.md)
- [插件内数据与求值契约](docs/specs/qc-data-contract.md)
- [几何节点接口与配方](docs/specs/geometry-nodes.md)
- [Gaussian 方法特定能量](docs/research/gaussian-energy-semantics.md)
- [Blender 运行时与 wheels 打包研究](docs/research/blender-extension-packaging.md)
- [Gaussian 输入与解析依赖研究](docs/research/gaussian-inputs.md)
- [用户资料阅读与设计依据](docs/research/source-review.md)
- [体数据节点可行性检查](tools/probe_volume_nodes.py)

`submodules/MolecularNodes` 是固定版本的参考源码。该子模块已采用深度 1 的浅克隆；其完整依赖与运行环境不属于 QCBlender 当前运行环境。
