# 随包组件

本文件描述开发构建中的组件；不代表科学功能或发布验收已经通过。

Python 3.13、NumPy 2.3.4 和 OpenVDB 由 Blender 5.1.1 提供。扩展不安装或覆盖这些组件。
其他 Python 组件的固定版本、来源、SHA-256 和声明依赖见 `dependencies.lock.json`；
许可证保留在各 wheel 的 `dist-info` 目录中。

| 组件 | 用途 | 许可证 |
| --- | --- | --- |
| cclib 1.8.1 | Gaussian 日志解析 | BSD-3-Clause |
| IOData 1.0.1 | FCHK 与科学数据解析 | GPL-3.0-or-later |
| GBasis 固定源码的 Python 实现 | 基函数、轨道、密度和库仑积分 | GPL-3.0-or-later，见下述上游声明差异 |
| SciPy 1.16.3 | 科学计算 | BSD-3-Clause 及 wheel 内第三方声明 |
| SymPy / mpmath | GBasis 数学依赖 | BSD-3-Clause 及 SymPy wheel 内第三方声明 |
| attrs / packaging / periodictable / pyparsing / importlib-resources | 解析与运行依赖 | 以各 wheel 自带许可证为准 |

GBasis 源码归档地址、commit 和 SHA-256 见 `science-sources.lock.json`。
IOData 的包元数据及源码头、GBasis 的上游包元数据声明 GPL-3.0-or-later，根 LICENSE 文件却含 LGPLv3 文本；
原样保留这些上游声明，发布前进一步核对，不将其改写为较宽松的统一许可。
`tools/build_science_backend.py` 从已校验源码生成纯 Python wheel；数值代码不修改，
排除可选的 libcint Python 包装器和原生代码。修改说明随 `gbasis/QCBLENDER_BUILD.md` 分发。
GBasis wheel 内保留 Python 源码与原始许可文本；SciPy 二进制及其许可声明原样使用固定上游 wheel。
当前 GBasis wheel 不包含 qcint 或原生编译器运行库。原样使用的 SciPy wheel 则含 OpenBLAS DLL，
其 LICENSE 声明静态链接 GCC runtime，许可为 GPL-3.0-or-later WITH GCC-exception-3.1；相关许可文本保留在该 wheel 中。
`backend-wheel.json` 随扩展保存 GBasis wheel 的版本、文件名和 SHA-256，与 `dependencies.lock.json` 合起来覆盖全部随包 wheels。
构建工具 uv、build、setuptools 只用于开发。
对外发布前须完成所有组件的许可材料复核；当前产物用于本地开发验收。
