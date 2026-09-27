# 本轮源码参考与实现边界

2026-09-27；对应 [实施规格](../../.scratch/source-adoption/spec.md)。来源只读核查 Passed，四项产品行为须以各批安装包验收为准。

| 来源 | 固定版本与具体参考 | 本轮采用 |
| --- | --- | --- |
| Multiwfn | 本地 2026.9.20 Windows 源码；`topology.f90` 1478 行附近 CP 类型/坐标写出，`ETS_NOCV.f90` 的 `showNOCV`（815 行附近） | CP 身份和输出精度；未取得 Fock/KS 矩阵时的未计算声明。作者自定义许可，仅核对输出语义，独立实现 |
| GXNU-MolStudio | `6f3e859020e27d11511b512a7cc47564386b6216`；`aim_panel.py` CP 读取；README_zh GPLv3-only 声明 | 结合类型和坐标理解 CP，未移植代码 |
| MolecularNodes | `999b0b5e8f576c83b3dd854819303fe00c0507a0`；`molecularnodes/framing.py` 正交求解，`scene/camera.py` 视框与裁剪；GPL-3.0-or-later | 固定观察方向、画幅/边距约束，使用 QC 自有相机操作，不引入其运行依赖 |
| VTK | `23f0a095621e91bbdbeace8451e22b950c8e5f46` / v9.7.0；`Filters/Core/vtkProbeFilter.h` Input/Source 角色、沿线采样、有效点掩码 | 复用 QC 三线性采样实现线剖面；不采用 VTK reader/filter 或运行库。文件头 BSD-3-Clause，模块另有 Sandia-USGov 声明 |
| GaussView 6 | 本地 `submodules/GaussianView/gv6.pdf`；SHA-256 `66ea3d5143de282a231e2b87473b71a6d0d63c3447e9a7c10b4497e9f954c847`；印刷页 79–84（分组表、原文、优化/IRC/扫描图） | 结果与对应构型、原文和图形保持可追溯；仅作交互参考，不代表运行验证或移植算法 |

VTK 一手说明：[vtkProbeFilter](https://vtk.org/doc/nightly/html/classvtkProbeFilter.html)。链接为文档入口，实施依据以固定本地源码为准。原始手册及下载材料维持软件目录级忽略；研究结论可进入 Git。

真实 C09 有 59 条 CP，类型一致，最大逐轴 PDB/CPprop 差为 0.000499959833 Å。实现逐项检查已记录的 CP 类型与坐标，并拒绝损坏字段；缺字段保留明确诊断。NOCV 解析按表识别明确的未计算声明，跳过占位表，拒绝不支持或冲突的单位；不会按数值全零推断未计算。正常真实 COBH3 九对的 pair 1 为 -77.88 kcal/mol。实现与安装验证见 [技术验收](../acceptance/source-adoption.md)。

算法性能替换、表面碎片过滤和新科学输入不纳入本轮；已有斜轴、有效域、双相及双场显示保持回归边界。
