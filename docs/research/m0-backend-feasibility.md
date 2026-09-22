# M0：GBasis 构建可行性与独立参考样本

核对日期：2026-09-22。目标运行时：Windows x64、Blender 5.1.1、CPython 3.13.9、NumPy 2.3.4。本次下载并审阅固定源码和样本，未安装构建依赖、未生成 wheel，未运行科学求值测试。

## 结论

推荐继续验证 GBasis 固定提交 `071969c900d6d7a9fbbdfe193c65ba3be177fbdf` 的原生 wheel。未找到一个可直接认定为 Windows / NumPy 2 合格、且仍采用纯 Python 发布流程的固定上游版本。旧提交没有 NumPy 上界，不构成兼容证据；它们缺少后来的 Windows 修复。当前源码保留 Python 实现的 AO、密度和 ESP API，但官方构建过程仍构建 C 扩展，不能直接把源码目录包装成声称等价的官方 wheel。[当前构建元数据](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/pyproject.toml)、[ESP 实现](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/gbasis/evals/electrostatic_potential.py)

构建需要开发用 CPython 3.13 的头文件和链接库：本机 Blender 自带 Python 下 `include/Python.h`、`libs/python313.lib` 两个路径均不存在，而 GBasis 明确要求 `Python Development.Module`。开发工具仅用于维护者构建，不进入插件用户安装流程。[GBasis CMake](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/CMakeLists.txt)

## 历史提交核对

| 固定来源 | 查到的事实 | 对本项目的意义 |
| --- | --- | --- |
| `126f558b82957c6f0724f247a90d6b6c99469b69` | 2024-08 Windows 限制引入之前的父提交；当时 `numpy>=1.16`，运行依赖还含 pytest | 元数据不排除 NumPy 2，但没有目标平台运行证据，不选作捷径 |
| `1dcc4f6cdbda76607d53ba0d21635329f6a910b6` | 明确加入 Windows `numpy>=1.22,<2.0.0` | 限制来自上游，不能通过删除它宣称兼容 |
| `9d379c47486e29262e9fbe58a4e4a24c75982ac5` | 发布时期的 setuptools 构建仍保留相同 Windows 限制 | 对应 0.1.0 发布路线不可直接使用 |
| `0fb4fce416184220094639f07988550f4370f431` | 2026-06 迁移 scikit-build-core | 后续 NumPy 2 路线伴随新的原生构建流程 |
| `07c417cc8ce4115f2c44d2b9fad6dde041f27495` | Windows MinGW CI、`eval_hermite` 的 int32/float64 转换、libcint 数组连续性修复 | 目标平台问题涉及实际计算代码，不能只改依赖声明 |
| `071969c900d6d7a9fbbdfe193c65ba3be177fbdf` | 固定候选包含上述修复，声明 NumPy≥2.0 | 适合开始构建和验收；不是已通过的发布包 |

证据：[引入 NumPy 上界的完整变更](https://github.com/theochem/gbasis/commit/1dcc4f6cdbda76607d53ba0d21635329f6a910b6)、[发布时期元数据](https://github.com/theochem/gbasis/blob/9d379c47486e29262e9fbe58a4e4a24c75982ac5/pyproject.toml)、[构建迁移](https://github.com/theochem/gbasis/commit/0fb4fce416184220094639f07988550f4370f431)、[Windows 修复](https://github.com/theochem/gbasis/commit/07c417cc8ce4115f2c44d2b9fad6dde041f27495)。

## 最短构建路线

1. 建立仓库内的构建工具目录。使用匹配的 CPython 3.13 x64 开发解释器及其头文件、链接库；固定 NumPy 2.3.4。构建端另需 `scikit-build-core>=0.9`、`setuptools-scm>=8`、构建前端、CMake、Ninja 和 MinGW gcc/g++。实际版本在下载前锁定；不改 Blender 安装目录。[上游构建要求](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/pyproject.toml)
2. 下载固定 GBasis 源码。用完整 Git checkout 保留版本身份，或显式为源码归档提供 setuptools-scm 构建版本并记录提交；不要把开发 wheel 标作未修改的 PyPI 0.1.0。上游版本由 setuptools-scm 动态生成。[版本提供器](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/pyproject.toml)
3. 固定子依赖。GBasis 在 x86/SSE3 选择 qcint v6.1.2；该 tag 本次解析为 `48f138c28bb72cf7b4350224152e407fe9e88b39`。先取得此源码，用 CMake `FETCHCONTENT_SOURCE_DIR_CINT` 指向固定目录可避免构建时临时拉取 tag；目录内容的哈希需留存。[GBasis 获取逻辑](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/CMakeLists.txt)、[qcint 固定源码](https://github.com/sunqm/qcint/tree/48f138c28bb72cf7b4350224152e407fe9e88b39)
4. 显式设置 `BUILD_MARCH_NATIVE=OFF`。qcint 默认 `-march=native`；关闭后使用 SSE3，避免发布 wheel 意外依赖构建机额外的 CPU 指令。上游还使用 `-ffast-math`，应保留在构建记录中，并用实际数值测试确定误差。[qcint CMake](https://github.com/sunqm/qcint/blob/48f138c28bb72cf7b4350224152e407fe9e88b39/CMakeLists.txt)
5. 用 CPython 3.13、NumPy 2.3.4 构建 `cp313-cp313-win_amd64` wheel；不装入系统 Python。上游 Windows 强制 gcc/g++，CMake 最低 3.18。选择 CMake 3.x 可避免第三方旧 policy 与较新 CMake 的额外变数。[GBasis CMake](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/CMakeLists.txt)
6. 检查 wheel 中 `.pyd` 和所有 DLL 的实际依赖。上游给出静态 libgcc/libstdc++/pthread 链接选项，但 qcint 检测到 QUADMATH 后仍链接 `quadmath`；不能仅凭这些选项认定没有 DLL 依赖。清理测试进程 PATH 中的 MinGW 后，在 Blender 中导入并执行积分。[GBasis 链接选项](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/CMakeLists.txt)、[qcint QUADMATH 链接](https://github.com/sunqm/qcint/blob/48f138c28bb72cf7b4350224152e407fe9e88b39/CMakeLists.txt)
7. 随扩展携带固定 SciPy、IOData、GBasis 及传递依赖；继续复用 Blender NumPy/OpenVDB。开发构建成功后仍要通过干净用户目录下的离线安装、后台计算、科学参考测试。

这里的构建步骤是待执行方案。当前上游 Windows CI 使用 Python 3.9–3.12，不能据此推断 CPython 3.13 已被覆盖。其测试配置还会向 PATH 加 MinGW，并复制运行时 DLL；本项目需要额外证明最终用户不依赖这些路径。[固定 CI](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/.github/workflows/pytest.yaml)、[测试启动配置](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/tests/conftest.py)

针对 CPython 3.13 / NumPy 2 的有限源码检查未发现 `np.float_`、`np.complex_`、`np.math` 等已删除接口；C 包装器通过 `Python.h`、`numpy/arrayobject.h` 和 `PyModuleDef` 初始化，采用 CINT 函数前向声明，没有直接包含 `cint.h`。这些检查不能证明二进制兼容，但目前没有证据要求先改科学计算源码。先构建未修改提交；若发生真实错误，再记录最小补丁、原始源码哈希和复现检查。不要为了构建方便直接删除 native 模块或放宽依赖元数据。[C 包装器](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/gbasis/integrals/src/libcint_wrap.c)、[Windows 导数修复](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/gbasis/evals/_deriv.py)

## 可用的真实输入与数值参考

IOData v1.0.1 tag 本次解析为 `adab5813713ba64641565eb2a8c11803a4e9bba6`。以下均来自固定上游测试数据；具体文件版权和许可证随来源保留，不只保存裸数据。

| 数据 | 用途与边界 | 固定来源 |
| --- | --- | --- |
| `water_sto3g_hf_g03.fchk` | 小型 RHF / STO-3G；检查 SP 壳拆分、7 AO、10 电子和 FCHK→IOData→GBasis 接入 | [IOData 文件](https://github.com/theochem/iodata/blob/adab5813713ba64641565eb2a8c11803a4e9bba6/iodata/test/data/water_sto3g_hf_g03.fchk)、[GBasis wrapper 验证](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/tests/test_wrappers.py) |
| `ch3_hf_sto3g.fchk`、`ch3_rohf_sto3g_g03.fchk` | 开壳层输入候选，分别检查 unrestricted 与 restricted open-shell 轨道/占据语义；实际适配还未运行 | [IOData 测试目录](https://github.com/theochem/iodata/tree/adab5813713ba64641565eb2a8c11803a4e9bba6/iodata/test/data) |
| `o2_cc_pvtz_pure.fchk`、`o2_cc_pvtz_cart.fchk` | 高角动量纯球谐和 Cartesian 顺序/归一化候选 | [IOData FCHK 测试](https://github.com/theochem/iodata/blob/adab5813713ba64641565eb2a8c11803a4e9bba6/iodata/test/test_fchk.py) |
| `h2o_hf_ccpv5z_sph.fchk`、`h2o_hf_ccpv5z_cart.fchk` | 更大基组和高角动量覆盖候选；不宜作为首次性能样本 | [GBasis 测试目录](https://github.com/theochem/gbasis/tree/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/tests) |
| `cubegen_h2o_5points.cube` | Gaussian cubegen 电子密度网格：标题为 UB3LYP/cc-pVTZ、Total SCF Density；可用于 Cube 轴序/单位测试 | [IOData Cube 文件](https://github.com/theochem/iodata/blob/adab5813713ba64641565eb2a8c11803a4e9bba6/iodata/test/data/cubegen_h2o_5points.cube) |

**不能把最后一行 Cube 与 STO-3G 水 FCHK 组成一对独立参考。** 方法、基组与几何均需一致；本次在上述有限数据集中没有确认到同一计算的 FCHK + MO Cube + density Cube + ESP Cube 完整组合。

GBasis 提供可先使用的独立 HORTON 数值数组：

| 参考 | 输入条件 | 验证内容 |
| --- | --- | --- |
| `data_horton_hhe_cart_eval.npy`、`data_horton_hhe_sph_eval.npy` | ANO-RCC，H/He 相距 **0.8 bohr**，`linspace(-2,2,5)` 的 125 点，numpy 默认 meshgrid 顺序 | Cartesian/球谐 AO 值、归一化、排列；这是 AO 而非真实 Gaussian MO 参考 |
| `data_horton_hhe_sph_density.npy` | H/He 相距 **0.8 Å**，换算常数 `0.5291772083 Å/bohr`，88×88 单位密度矩阵，10³ 点 | 二次型密度计算；人为矩阵不代表实际分子密度 |
| `data_horton_hhe_cart_esp.npy`、`data_horton_hhe_sph_esp.npy` | H/He 相距 **0.8 Å**，同一旧换算常数，单位密度矩阵 103/88 维，125 点，核电荷 1/2 | 电子势积分与核项；人为密度可验证数学实现，不证明 FCHK 端到端正确 |

精确条件由上游测试给出：[AO 测试](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/tests/test_eval.py)、[密度测试](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/tests/test_density.py)、[ESP 测试](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/tests/test_electrostatic_potential.py)。读取数组时 `allow_pickle=False`。上游 ESP 包含原点核位置，比较时须显式核对非有限值位置，不能把核奇点数值删去后宣称全域一致。

MO 验收可先把 HORTON AO 参考与同一已知系数矩阵相乘，检验变换维度、转置与轨道排列，但这仍是组合测试。发布前需要匹配真实 FCHK 的独立 MO/密度/ESP 参考，或使用独立计算程序离线生成固定参考并保存程序版本、生成脚本、方法/基组/几何、采样点和误差。不能用 GBasis 自己生成的文件回测 GBasis 后声称独立验证。

## 下载记录与状态

本次下载物只在忽略目录 `outputs/m0-research/`，没有修改第三方源码或系统环境。

| 归档 | SHA-256 |
| --- | --- |
| GBasis `071969c900d6d7a9fbbdfe193c65ba3be177fbdf` GitHub ZIP | `42c80656a3a744ad528d69c6cb5a7c805c1278ce3d560f822f8a3ca3848e43d4` |
| IOData `v1.0.1` GitHub ZIP | `ff3631dbab960738449f5d3ce2c8689f541e2076f7aaa058639242c24e43d307` |

来源：[GBasis 固定 ZIP](https://codeload.github.com/theochem/gbasis/zip/071969c900d6d7a9fbbdfe193c65ba3be177fbdf)、[IOData 发布 ZIP](https://codeload.github.com/theochem/iodata/zip/refs/tags/v1.0.1)。归档在本机由 Blender 自带 Python `urllib.request` 下载，TLS 验证保持启用；PowerShell / curl 的 Schannel 出现本机凭据错误，未以禁用证书验证绕过。

| 检查 | 状态 |
| --- | --- |
| 固定源码、历史约束、Windows 修复、真实样本取得 | Passed |
| 未修改的 qc-gbasis 0.1.0 对 Windows NumPy 2 的元数据兼容 | Failed |
| Blender bundled Python 可直接满足 GBasis Development.Module 构建要求 | Failed：缺开发头/链接库 |
| CPython 3.13 原生 wheel 构建、DLL 闭包、离线 Blender 导入 | Not Run |
| 真实 FCHK→MO/密度/ESP 与独立参考数值比较 | Not Run |

本研究没有改变单扩展交付决策；M0 先解除构建与数值验收门槛，插件使用者仍只安装一个扩展 ZIP。
