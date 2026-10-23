# 子模块主干更新与 QCBlender 采用建议（2026-10-23）

三个参考子模块已更新到本批核实的默认主干提交。优先建议是在既有取景相机上增加自动观察方向、集中出图设置；其次是让已经导入的 IRC Mayer 数值驱动逐键着色。表面距离投影图与 AICD 保留为后续专题，尚未实施任何插件功能。

产品对照基线：`6c3545dd72bce8d897d5826b22ca0ac973b0763e`。本批规格和授权边界见[任务规格](../../.scratch/upstream-20261023/spec.md)。本次只更新参考检出及研究记录，未提交、推送、发布、构建安装包或操作 Blender；既有安装和历史验收身份不变。

后续进展（2026-10-23）：上文及以下比较保留研究时的产品基线。自动观察方向与出图、Mayer、表面距离投影及 AICD 已在后续独立任务实施，当前能力和验收以 [ARTIFACTS](../ARTIFACTS.md) 为准。用户随后要求提交全部未提交内容并推送，本研究与固定子模块指针一并纳入，不重写原研究结论。

## 1. 固定来源与完整增量

2026-10-23 实施前分别执行 `git ls-remote --symref origin HEAD refs/heads/main`（MolecularNodes、MolStudio）及 `refs/heads/master`（VTK），HEAD 与对应分支指向下表目标。均与同日规划快照一致。

| 参考仓库与原件 | 比较基线 | 本批目标 | 完整增量 | 目标提交时间 |
| --- | --- | --- | ---: | --- |
| [MolecularNodes](https://github.com/BradyAJohnston/MolecularNodes)，[本地参考](../../submodules/MolecularNodes) | `f88961b28828dfb32697748b575298dec20af3af` | `6cc280ff7002e46e6977cc2ab337cf9a34adac7a` | 23 | 2026-10-22T11:05:36Z |
| [GXNU-MolStudio](https://cnb.cool/chem311/GXNU-MolStudio)，[本地参考](../../submodules/GXNU-MolStudio) | `a030398b75e62bd10905c52d04c3f884e0b07fb6` | `427e6cca72fc43837949d0cee234bfc083279775` | 4 | 2026-10-18T09:38:20+08:00 |
| [VTK](https://gitlab.kitware.com/vtk/vtk)，[本地参考](../../submodules/VTK) | `4b0325a981d1f5cfad9d4da4909a8230881b2bf4` | `be385f1c26ca5699f5b17578c690a0d83eed9ec5` | 188 | 2026-10-22T16:21:25Z |

完整提交范围包括已合入的分支提交及合并提交，不等于功能数量。三份完整 SHA 清单保存在本文附录，不另建重复研究报告。

- MolecularNodes：使用[官方 compare API](https://api.github.com/repos/BradyAJohnston/MolecularNodes/compare/f88961b28828dfb32697748b575298dec20af3af...6cc280ff7002e46e6977cc2ab337cf9a34adac7a?per_page=100)；`status=ahead`，`ahead_by=total_commits=23`，返回 23 个唯一提交，末项为目标。
- MolStudio：CNB 官方提交页已核对四项父子链；更新后用完整本地历史 `git log --reverse --format='%H %P %cI %s' a030398b75e62bd10905c52d04c3f884e0b07fb6..427e6cca72fc43837949d0cee234bfc083279775` 复核。第一项父提交是基线，末项是目标。其 README 列出的 GitHub 镜像未能提供本范围的 compare（404），未用镜像旧版本代替 CNB 结果。
- VTK：官方 GitLab 远端与 Kitware 官方 GitHub 镜像核得同一目标。使用镜像 compare 的[第 1 页](https://api.github.com/repos/Kitware/VTK/compare/4b0325a981d1f5cfad9d4da4909a8230881b2bf4...be385f1c26ca5699f5b17578c690a0d83eed9ec5?per_page=100&page=1)和[第 2 页](https://api.github.com/repos/Kitware/VTK/compare/4b0325a981d1f5cfad9d4da4909a8230881b2bf4...be385f1c26ca5699f5b17578c690a0d83eed9ec5?per_page=100&page=2)，分别返回 100、88 项；`status=ahead`，`ahead_by=total_commits=188`，去重后仍为 188，末项为目标。

本批对 MolecularNodes 和 VTK 使用 `fetch --no-tags --depth=1` 获取固定目标；两者更新后 `git rev-list --count old..new` 的本地可见结果均为 1，不能用它代替上面的完整范围。VTK 的 compare `files` 数组仅返回前 300 项；本地两端树的 `git diff --no-renames --name-only old new` 列出 397 个变更路径。MolecularNodes 同口径为 242 个路径，API 开启重命名识别时为 241；这是路径统计口径差异。MolStudio 为 33 个变更路径。

## 2. 本轮变化及已有能力对照

### MolecularNodes

- [自动观察方向](https://github.com/BradyAJohnston/MolecularNodes/blob/6cc280ff7002e46e6977cc2ab337cf9a34adac7a/molecularnodes/viewpoint.py)：新增 PCA、减少遮挡、可见面积、视点熵等方法；Canvas 还可对实际网格做 raycast。相关接口明确标注 Experimental。QC 的[取景相机](../../qcblender/blender/camera.py)已经能框住选中对象，但沿用当前 3D 视图方向，因此新价值是选择方向而非重复实现包围框取景。
- [Canvas 设置](https://github.com/BradyAJohnston/MolecularNodes/commit/6cc280ff7002e46e6977cc2ab337cf9a34adac7a)：本轮新增构造参数 `view_transform`、`background`，在预设载入后按显式输入应用；透明背景参数此前已有。本插件可借鉴统一设置入口，不能把上游已有透明功能描述为本轮新算法。
- [合成器节点](https://github.com/BradyAJohnston/MolecularNodes/commit/a5c96d6e19a8dceeae913317b31c28c58091fe59)：新增描边、插画风格及 AOV 掩码。`Outline` 保留图像 alpha，并使透明背景上的描边可见；接入 QC 需要自己的渲染与图例核验。
- [Align Molecules](https://github.com/BradyAJohnston/MolecularNodes/commit/d5b0a29309c8345c9e61031703f187dc75317aec)侧重蛋白序列/结构配准。QC 已有按源原子顺序、几何和显式刚体变换的[关联操作](../../qcblender/blender/association.py)，不重复新增同名入口，也不把同源蛋白配准当成严格科学数据对应。
- 其余增量包括 Evaluate on Atoms 输出、CellPack 导入集合隔离、PubChem 结构获取、CIF 多数据块及缩进标签读取、矩阵属性约定、依赖和 CI 更新。它们分别服务上游的数据模型、导入器及渲染后端；本轮没有证实 QC 具有相同缺陷，不直接移植，也不引入联网获取或新的格式承诺。完整标题及 SHA 见附录。

当前 [QC manifest](../../qcblender/blender_manifest.toml) 的最低 Blender 为 5.1.1、最高边界为 5.2.0；上游 [pyproject](../../submodules/MolecularNodes/pyproject.toml) 的最低 Blender 是 5.2.0，依赖 `nodebpy>=520.39.0`、`databpy>=0.12.0` 等。参考检出更新不改变 QC 的版本边界，不能直接打包上游节点资产或整套依赖。

### GXNU-MolStudio

四个提交中只有 [f22d8f6](https://cnb.cool/chem311/GXNU-MolStudio/-/commit/f22d8f6617c57b00ddae3c48a85d8791c6e219c3) 是产品功能批次；其余三个是介绍文章和派生图文更新。不能把提交数解释成四项独立新能力。

- [表面距离投影](../../submodules/GXNU-MolStudio/molstudio/core/surface_projection.py)驱动 Multiwfn `300 → 8`，读取 `distmap.txt` 并绘制投影。它表示沿指定扫描方向命中表面的距离，不等同于 QC 的空间场切片、ESP 值或通用三维投影。实现修正了 `(Nx, Ny)` 到绘图 `(Ny, Nx)` 的转置、半网格像素边界，并区分未命中表面的留白和有效距离。
- [AICD](../../submodules/GXNU-MolStudio/molstudio/core/aicd.py)读取 Gaussian 张量转储，计算指定磁场下的感应电流矢量及不同标量，再生成等值面和箭头；[π/σ 识别流程](../../submodules/GXNU-MolStudio/molstudio/core/multiwfn_pi.py)另调用 Multiwfn。输入构建、本地 Gaussian 运行和结果显示也随本批新增。
- 上游[投影测试](../../submodules/GXNU-MolStudio/tests/test_surface_projection.py)包含非方形网格绘图、留白和配色案例。这是本次已读的测试源码，不是本次运行结果，也不能证明真实 Multiwfn 数值或 AICD 科学接受已经通过。

### VTK

[逐键着色更新](https://github.com/Kitware/VTK/commit/7c014b6d5c9d62d6522a6cec4c8e85d369b788e9)在 `vtkMoleculeMapper` 中新增 `DiscreteByBond`：每条键可用 RGB/RGBA 或一分量标量经独立 lookup table 着色。QC 已能[读取选定原子对的 IRC Mayer 值](../../qcblender/blender/irc.py)，尚未将它映射到逐键颜色，因此值得评估数据驱动的键显示。

其余较大的增量集中于 WebGPU 透明层与 picking、ANARI 资源/颜色/时间步更新、HDF 缓存隔离、点定位器和窗口事件等。QC 使用 Blender 的渲染与交互系统，本轮不移植这些后端；HDF、WebGPU、ANARI 不是本批新增依赖。不得把上游缺陷模式或性能变化宣称为 QC 已复现缺陷或已获得的性能收益。

## 3. 采用顺序与后续验收建议

下表是研究建议，未实施，也不替代后续功能规格和授权。

| 优先级 | 候选与最小边界 | 收益、代价及限制 | 后续行为验收 |
| --- | --- | --- | --- |
| 优先 | 自动观察方向：在现有取景相机入口扩展显式选择；先评估 PCA，再评估减少遮挡 | 减少平面分子被侧着观察、重点结构被遮住的手动调整；成本中等。仅改变展示相机，不改源坐标；PCA 对近简并/对称结构可能方向不稳定，上游本身有此说明。不能照搬其世界尺度常数 | 复用 `test_science_framing.py` 与现有取景案例；覆盖平面、线性和对称结构、横竖画幅、多对象世界变换；核对原数组不变及实际图像 |
| 优先 | 显式应用出图预设：集中色彩管理、背景、透明输出；描边另作为可选项 | 减少重复设置，提高同批图片的一致性；成本低至中等。色彩变换会影响最终可见颜色，必须与图例一起核对；不在导入数据时自动覆盖用户场景设置 | 核对显式应用、取消、Undo/Redo；透明 PNG 的 alpha、图例与表面颜色、中文界面、工程保存重开；描边启用后单独比较图像 |
| 次优先 | 使用已导入 Mayer 数据做逐键标量着色，并跟随当前 IRC 步 | 将已有数值表转为可观察的反应过程；成本中等。沿用原子对身份、方法、单位和步号，明确缺失项；距离推断连线不等于计算键级 | 用真实 Mayer 输入逐对核对颜色、色标和步号；验证筛选后身份、缺失原子对、导出值及保存重开，不凭颜色像素代替数值校验 |
| 后续专题 | 表面距离投影图：先考虑外部 `distmap.txt` 及来源信息的导入显示 | 增加二维距离图；需要明确扫描方向、表面定义、距离单位和未命中标记，不能仅靠三列文件猜物理意义。计算流程保持外部，不增加必需 Multiwfn 依赖 | 非方网格、坐标轴/原子叠加、半网格边界、有效域和显示插值不改原值；配合真实外部输入单独确认科学语义 |
| 后续专题 | AICD：先制定外部结果导入与展示契约，再决定是否开发 | 新增张量/矢量场及磁响应语义，成本高。需明确磁场、坐标系、单位、π/σ/全电子范围及来源；Gaussian/Multiwfn 执行链不混入本轮维护 | 需要真实同源张量、日志与独立数值参照；核对 B 与 J 的方向、单位换算、原子关联、轨道范围，单独进行科研验收 |

所有候选继续服从[单扩展 ADR](../adr/0001-self-contained-extension.md)与[领域定义](../../CONTEXT.md)。若以后采用代码或资产，再按实际文件核对许可与更新 THIRD_PARTY；当前只是保留参考，不改变既有来源归属。

## 4. 不需要重复实施的内容

- QC 已有 Viridis/Cividis 冻结预设。本次对上游旧、新 `color_matplotlib.py` 的 AST literal 进行定向比较：两套各 13 个色阶及插值、颜色模式参数相同。原 [QC 预设](../../qcblender/color_presets.py)保留实际采用提交 `2eb0598`，不以本次参考 HEAD 改写历史归属。
- QC 已有刚体关联、取景相机及有效域处理。`test_science_profile.py` 已覆盖非立方/斜轴网格、有效域缺口及 CSV；本次只核对其存在与行为定义，没有重新运行未改动的产品测试。
- 以下 VTK 文件两端 Git blob 完全相同；这只是这四份源码的字节相等结论，不扩大为 VTK 全部接口和依赖不变。

| VTK 路径 | 两端共同 Git blob |
| --- | --- |
| `IO/Chemistry/vtkGaussianCubeReader.cxx` | `963d56a97d2e8ad25a8a5af00d080d537c8aad44` |
| `Common/DataModel/vtkImageData.cxx` | `7d56b4f0a78bfc140ac8c2b07dd5e7b6c7a3d769` |
| `Filters/Core/vtkProbeFilter.cxx` | `077caab77de689d2b99dcc028a1a625af39e9982` |
| `Filters/Core/vtkFlyingEdges3D.cxx` | `30dd07c5e24dec5c74cd451bdd3c581961368727` |

## 5. 本批执行与验证

获取和检出在各子模块目录内串行执行，均为退出码 0：

```text
MolecularNodes: git -c submodule.recurse=false -c fetch.recurseSubmodules=false fetch --no-tags --depth=1 origin 6cc280ff7002e46e6977cc2ab337cf9a34adac7a
GXNU-MolStudio: git -c submodule.recurse=false -c fetch.recurseSubmodules=false fetch --no-tags origin 427e6cca72fc43837949d0cee234bfc083279775
VTK: git -c submodule.recurse=false -c fetch.recurseSubmodules=false fetch --no-tags --depth=1 --filter=blob:none origin be385f1c26ca5699f5b17578c690a0d83eed9ec5
随后分别执行: git -c submodule.recurse=false switch --detach <对应目标SHA>
```

三个子模块维持 detached HEAD。fetch 按固定 SHA 获取，未调整远端跟踪分支或默认分支配置；最新主干身份来自实际 `ls-remote`，不是依赖可能滞后的 `origin/main` / `origin/master`。

| 项目 | 结果与证据 |
| --- | --- |
| Passed：目标与干净状态 | 三个 `rev-parse HEAD` 均匹配第 1 节目标；各自 `git status --porcelain` 均为空。主仓库 gitlink 差异为三个预期目标 |
| Passed：克隆与远端边界 | MolecularNodes、VTK 仍为 shallow；MolStudio 仍为完整历史；三个 origin URL 和 `.gitmodules` 未修改；VTK `blob:none`、`core.sparseCheckout=true` 保持 |
| Passed：标签与稀疏范围 | 标签数量前后为 0 / 1 / 2；完整标签名列表的 SHA-256 逐仓相同。VTK sparse-checkout 文件 SHA-256 前后均为 `cfe0c7cc418d11a873e0eea0b3708864f9928402db6e411731c2475949d701e6` |
| Passed：完整增量与重点源码 | 23 / 4 / 188 个唯一提交，来源、分页和浅历史边界见第 1 节；两套预设参数及四份 VTK 源文件比较结果见第 4 节 |
| Passed：最终文档与 diff 检查 | 四份本批/更新文档的相对链接、UTF-8 无 BOM、LF、尾部空白和完整清单检查通过；`git diff --check` 退出码 0；主仓库仅七个预期变更路径，无暂存改动，产品与依赖锁未变 |
| Not Run：上游程序及插件运行 | 没有运行上游测试、GUI、渲染、打包安装或独立科研验收；本批未变更这些对象 |

本地仅 main 分支与主工作树，没有本批或历史已完成的额外工作树需要归档。本批不生成新的安装包或清理产物，因此不调整当前安装、ARTIFACTS 或产品 CHANGELOG。

## 6. 关键来源原件

以下原件获取/核查日期均为 2026-10-23，版本为第 1 节对应仓库的目标提交。SHA-256 按 `git show <目标SHA>:<路径>` 的原始 blob 字节计算；MolStudio 的工作树可能由 Git 检出为 CRLF，不能混用工作树换行后的摘要。

所用章节为：`viewpoint.py` 的 PCA/评分/方向搜索，`scene/base.py` 的 Canvas 参数与 `look_at`，`outline.py` 的 alpha 组合，`pyproject.toml` 的兼容性与依赖；MolStudio 的距离图解析/绘制、AICD 张量与矢量转换、π/σ 工作流及投影测试；VTK 的 `UpdateBondGlyphPolyData`。VTK 的逐键源码位于既有稀疏检出范围外，已通过 Git blob 读取并保留于子模块对象库，未扩大 sparse-checkout。

| 仓库及原件路径 | 固定来源 | SHA-256（原始 blob） |
| --- | --- | --- |
| `submodules/MolecularNodes/molecularnodes/viewpoint.py` | [源码](https://github.com/BradyAJohnston/MolecularNodes/blob/6cc280ff7002e46e6977cc2ab337cf9a34adac7a/molecularnodes/viewpoint.py) | `f9726b3edcff69630d6ee5f0ea5083884faedf050f98d64c7a1f47a135ea0665` |
| `submodules/MolecularNodes/molecularnodes/scene/base.py` | [源码](https://github.com/BradyAJohnston/MolecularNodes/blob/6cc280ff7002e46e6977cc2ab337cf9a34adac7a/molecularnodes/scene/base.py) | `934cfa6ddc2917ab0261f05b84f0a5751ca4fac21ec8b7727fc9a6fc692a98c4` |
| `submodules/MolecularNodes/molecularnodes/nodes/compositor/outline.py` | [源码](https://github.com/BradyAJohnston/MolecularNodes/blob/6cc280ff7002e46e6977cc2ab337cf9a34adac7a/molecularnodes/nodes/compositor/outline.py) | `d5d0cb4811b7813df4cb51f027846f96e0bb6093f681bc07c72a0095553a0b59` |
| `submodules/MolecularNodes/pyproject.toml` | [源码](https://github.com/BradyAJohnston/MolecularNodes/blob/6cc280ff7002e46e6977cc2ab337cf9a34adac7a/pyproject.toml) | `1801537eb4e8227d49959160fbeea7aee4c1a52799815e7ef2b589d16ce8b357` |
| `submodules/GXNU-MolStudio/molstudio/core/surface_projection.py` | [源码](https://cnb.cool/chem311/GXNU-MolStudio/-/blob/427e6cca72fc43837949d0cee234bfc083279775/molstudio/core/surface_projection.py) | `d70853eb1a737dee83232108f57f8acd0208c135297dc92269588f33ae05e44c` |
| `submodules/GXNU-MolStudio/molstudio/core/aicd.py` | [源码](https://cnb.cool/chem311/GXNU-MolStudio/-/blob/427e6cca72fc43837949d0cee234bfc083279775/molstudio/core/aicd.py) | `1cb42f1be062c860280c748caa5b870a496a626337341b346fa673495fb97004` |
| `submodules/GXNU-MolStudio/molstudio/core/multiwfn_pi.py` | [源码](https://cnb.cool/chem311/GXNU-MolStudio/-/blob/427e6cca72fc43837949d0cee234bfc083279775/molstudio/core/multiwfn_pi.py) | `a7cc1209a4f098de205b56d4cb48525bbee29e63af361d0cb3e0904505c099d3` |
| `submodules/GXNU-MolStudio/tests/test_surface_projection.py` | [源码](https://cnb.cool/chem311/GXNU-MolStudio/-/blob/427e6cca72fc43837949d0cee234bfc083279775/tests/test_surface_projection.py) | `657cadf3cb0e69556b9b130eb25919b2dfd06a4c854116b10f00f3ab08336628` |
| `submodules/VTK/Domains/Chemistry/vtkMoleculeMapper.cxx` | [源码](https://gitlab.kitware.com/vtk/vtk/-/blob/be385f1c26ca5699f5b17578c690a0d83eed9ec5/Domains/Chemistry/vtkMoleculeMapper.cxx) | `33f3f1d880e096fb631c6e72c76be4666dea640bfb76f5f7bcf2d097c48190ec` |

## 附录：完整增量提交清单

保留 compare API 的提交顺序；MolStudio 使用本地完整历史的逆序输出。日期是提交记录，不用于截断比较范围；上游标题按原文保留。

### MolecularNodes：23 项

<details>
<summary>展开全部提交</summary>

| 序号 | 完整 SHA | Committer 时间 | 标题 |
| ---: | --- | --- | --- |
| 1 | `11639de25918ce8cb7ae4ee20a11bbcfd8d7b888` | 2026-10-12T15:16:14Z | tweak shader outline; update with focal length |
| 2 | `0ab75eecdc05ec58b8320a1dc91a2dfdc091d649` | 2026-10-12T15:23:00Z | Chore: Bump `nodebpy` and re-dump (#1275) |
| 3 | `9059f03ad30778be0abdfc5b1afa641f40d7ce52` | 2026-10-13T07:53:46Z | bump nodebpy |
| 4 | `441e66029888068cfcbd58f8c8b5d260ab2451b6` | 2026-10-14T13:50:02Z | Atoms / Representation result for Evaluate on Atoms (#1279) |
| 5 | `5f759d40587d4d421c229a6f69bd04723ad961bb` | 2026-10-14T17:10:07Z | Fix CellPack reusing an earlier import's instance collection (#1280) |
| 6 | `6ff30dec96f3b3014f6c3901bfad672a3559c080` | 2026-10-19T08:03:20Z | update with sticky transform |
| 7 | `91182b5bed207a82d7c8726cad1677d290bb8c2e` | 2026-10-19T09:59:26Z | update new orient nodes |
| 8 | `859ee336debde18453124c7acfaf4b9684f8e882` | 2026-10-21T11:25:14Z | simulate for stickiness>0 or smoothing |
| 9 | `c9a385d4c1b9e4eb8b1c7f1d84d94eac5032aaba` | 2026-10-21T11:57:26Z | Add hysteresis and camera transform to Orient to Best View |
| 10 | `5c9f00c96b5a5d8d0fd36c8ceecd4b41301258ca` | 2026-10-21T13:48:44Z | Update to databpy 0.12.0 for row-major FLOAT4X4 attributes (#1285) |
| 11 | `6115e2f0d9823c37f47a0330b79838c14bba34d1` | 2026-10-21T13:49:01Z | Merge branch 'main' into unobstructed-view |
| 12 | `a5c96d6e19a8dceeae913317b31c28c58091fe59` | 2026-10-21T14:03:27Z | ENH: Compositor nodes: Outline, Composite Illustrative, Goodsell Illustrate, AOV masks (#1240) |
| 13 | `7c2bb0f9447d57b4ea4bab6394e56f51f75b99f7` | 2026-10-21T14:09:51Z | Merge branch 'main' into unobstructed-view |
| 14 | `524854310a54d87b2fd30368b410ef671103cec5` | 2026-10-21T14:12:14Z | merge main |
| 15 | `c34fd070b489a5c0e4be647d81c40e27407308a5` | 2026-10-21T14:30:08Z | bump mda and nodebpy |
| 16 | `c5e8a21483dfb7be7c0724b70ff203a609facdfc` | 2026-10-21T14:44:23Z | fix quarto tabs |
| 17 | `e08c543f41701e56e8c582b421ebe0f74c18e790` | 2026-10-21T15:56:58Z | Fix canvas docs: hide trajectories instead of clearing them |
| 18 | `e5f7ab995402ebc9739abbcc6864664b7a40ffbf` | 2026-10-22T09:36:57Z | Split CI into per-workflow badges, test each Blender version, update README (#1293) |
| 19 | `27d108195b9ccfa680ac102f3256da5e33d089c3` | 2026-10-22T09:46:33Z | Refresh daily bpy from dailybpy on every test run |
| 20 | `cc47378d8732460277c81156b51388d9409b2ce8` | 2026-10-22T09:50:47Z | Fetch structures from PubChem (#1286) |
| 21 | `5672004505f94bba387a46a4ea08658f01699b2a` | 2026-10-22T11:05:35Z | Import CIF files with multiple data blocks and indented tags (#1294) |
| 22 | `d5b0a29309c8345c9e61031703f187dc75317aec` | 2026-10-22T11:05:35Z | Add Align Molecules operator (#1295) |
| 23 | `6cc280ff7002e46e6977cc2ab337cf9a34adac7a` | 2026-10-22T11:05:36Z | Canvas view_transform and background arguments (#1297) |

</details>

### GXNU-MolStudio：4 项

| 序号 | 完整 SHA | Committer 时间 | 标题 |
| ---: | --- | --- | --- |
| 1 | `f22d8f6617c57b00ddae3c48a85d8791c6e219c3` | 2026-10-18T09:31:21+08:00 | feat: AICD pi/sigma workflow and surface projection improvements |
| 2 | `d15cf8219dc77b11decad467e979ecf7535a7e8f` | 2026-10-18T09:33:42+08:00 | docs: add WeChat article with agent update guide |
| 3 | `9a98b5699afceb434eb7623d5c68975641c4cf2f` | 2026-10-18T09:36:11+08:00 | docs: correct product name in WeChat article |
| 4 | `427e6cca72fc43837949d0cee234bfc083279775` | 2026-10-18T09:38:20+08:00 | docs: neutralize WeChat article tone |

### VTK：188 项

<details>
<summary>展开全部提交</summary>

| 序号 | 完整 SHA | Committer 时间 | 标题 |
| ---: | --- | --- | --- |
| 1 | `bc99695f942d7e749d45b514358a16fb0f0d59f9` | 2026-09-08T14:42:58Z | Fix vortex core extraction on polyhedral meshes |
| 2 | `9f154f31dcd624a5f6e9d115be451410afa54bac` | 2026-10-02T11:08:11Z | vtkHDFReader imagedata: clear cache properly |
| 3 | `97ea3325abf037721c319673f1c8cf374d904177` | 2026-10-02T11:08:12Z | vtkHDFReader: Add temporal image cache test |
| 4 | `07a4e04983cdecdc5101c887057436c7021b4b53` | 2026-10-02T11:10:55Z | Add release note for ImageData vtkHDFReader fix |
| 5 | `10601e860db82b269fd3a4db3516546cdf618fcb` | 2026-10-05T07:08:09Z | Support explicit nodal VARLOCATION |
| 6 | `c5528ef593b52398564e437bbcdda7d5e4438af2` | 2026-10-06T07:42:41Z | Support VARSHARELIST in TecPlotReader |
| 7 | `ab2c67835edd46dda3c62c26449acbb65a723c70` | 2026-10-07T18:58:07Z | Add a test for switching anari libraries |
| 8 | `c845ae1cb07898bcc386be1ecacf6a130e7984c2` | 2026-10-07T18:58:08Z | Remove the renderer and actor observers when ANARI nodes are destroyed |
| 9 | `c7082fcfaff431baf788a3a59c927b4738a81fff` | 2026-10-07T18:58:08Z | Release the ANARI scene graph before its device in vtkAnariPass |
| 10 | `27b93b80c70cba89934407e47a4b8a87f4917536` | 2026-10-08T03:28:14Z | add WebGPU camera pass |
| 11 | `0dda6316823b3a77be16ead2654102970dad8ad1` | 2026-10-08T03:28:15Z | add WebGPU clear rgb pass |
| 12 | `7fcf37f5c1c13525dcbcd789e700aabcd06be981` | 2026-10-08T03:28:16Z | move vtkLightingMapPass to RenderingCore |
| 13 | `22fa14558a4584e4d5dc4a4ac627219d1c75a00b` | 2026-10-08T03:28:16Z | move vtkRenderStepsPass to RenderingCore |
| 14 | `c5018e105547bfe11888898c73774e5c251fce5d` | 2026-10-08T03:28:17Z | update render pass marshalling |
| 15 | `124094b6484767f2d45b139c8024f94b18431d77` | 2026-10-08T03:28:17Z | update changelog |
| 16 | `8b46c0344cf14c8c6a88dc1ce8bf8387dffe3a93` | 2026-10-08T13:37:17Z | EGL: fix undesired warnings |
| 17 | `938a12c6236ead7236ba692fd3c798f83a5d00ff` | 2026-10-08T13:44:23Z | EGL: fix undesired warnings |
| 18 | `5071a22ff816ab7107ef7db927a08b5c66a4a922` | 2026-10-08T15:27:56Z | Replace vtkObjectBase WeakBlockMutex with a spinlock (atomic boolean) |
| 19 | `a6e1d0905e7826172419822e2a70ffcc7cd14a15` | 2026-10-08T17:42:26Z | Declare missing vtkHDFWriter test data |
| 20 | `3eaae08c2b43eeb9653a80416e5585340d3483d9` | 2026-10-08T17:42:26Z | Restore selected arrays from the vtkHDFReader cache |
| 21 | `9cd7b224b90ba9dc7a5794f5444a667fe9045900` | 2026-10-08T17:42:26Z | Isolate vtkHDFReader structured caches by composite path |
| 22 | `2c60233e8ca604742aba65d19c86acb5466c8e17` | 2026-10-08T17:43:36Z | Add release note for vtkHDFReader cache fix |
| 23 | `a99e085d9a363d99056baeb0e4bf9f2599bd2002` | 2026-10-09T08:15:34Z | Improve TecplotReader memory management |
| 24 | `b8feba0ae1678b96a2481357e8f68081e22e5f1b` | 2026-10-09T08:15:34Z | Add tests TecplotReader |
| 25 | `eab735ad5440d5a9b213a85e924ed3e29aad805d` | 2026-10-09T08:15:34Z | Update release note |
| 26 | `9ad32c243384dbd5a497412ebd66fe799400444a` | 2026-10-09T13:58:20Z | TestAbortExecute: Avoid a failure case by thread racing |
| 27 | `2f8e9f24665994d5f6a30e6097f12507ed6cfe8f` | 2026-10-09T14:51:09Z | Remove duplicate 2DScalar.vti.sha512, it exists in Testing/Data |
| 28 | `6d6d904b34d6a2248eade1b0b1d880ab43026bd7` | 2026-10-09T14:51:09Z | Add a script to remove unused testing data content links |
| 29 | `d2fa5ac564518d6bd3bede9fe24d9ae9dc8ed7c5` | 2026-10-09T14:51:09Z | Delete unused content links for test data, and baseline images |
| 30 | `f522120c905fda607d44305475a4a5d90891f903` | 2026-10-10T02:57:01Z | Add a deep framebuffer to hold per-pixel transparent fragment lists |
| 31 | `b86da4ddd23be0eab38bfedf51a107edb22be01d` | 2026-10-10T02:57:02Z | Bind the deep framebuffer buffers as a renderer bind group |
| 32 | `00b0e19b33d2da86a4c5d2b8f0680f43631f0fbe` | 2026-10-10T02:57:02Z | Append translucent fragments to the deep framebuffer in WGSL |
| 33 | `c55bb904326d5d5c65ef8f0f838f01def1203f95` | 2026-10-10T02:57:02Z | Bind the deep framebuffer into translucent pipelines |
| 34 | `6bfbda817632f13fba3dd881246d4afe2b357ae9` | 2026-10-10T02:57:03Z | Resolve the deep framebuffer into the colour attachment |
| 35 | `9d6ff8a0b0d8a54b95f8c423825474cb736def8e` | 2026-10-10T02:57:03Z | Test that picking sees the nearest translucent layer |
| 36 | `3531188016a521e5d1cd5bb022f7147941b3fa56` | 2026-10-10T02:57:03Z | Test order independence past the per-pixel layer limit |
| 37 | `1449b78de25dd7183cb3d1375c23986bde397d9e` | 2026-10-10T02:57:03Z | Record deep framebuffer fragments only in the translucent pass |
| 38 | `e417bfcfee8402b53120cb6784f8f61aaa3939b5` | 2026-10-10T02:57:03Z | Test transparency through the glyph and composite mappers |
| 39 | `b925f7618870e58a2f86afe77bdb508223cab7b4` | 2026-10-10T03:44:56Z | Write point ids when a hardware selection asks for points |
| 40 | `f3fe51eba99258f667a330b1140ed8826940981e` | 2026-10-10T03:45:07Z | Skip props that are not pickable while a selection renders |
| 41 | `5911f54ee08b6c1efd6df3c22b23846975f40e3f` | 2026-10-10T03:45:07Z | Give overlay props an id so hardware selection can pick them |
| 42 | `d3c37749769dffd2adcb39bdc73e177dc1160223` | 2026-10-10T03:45:07Z | Carry every id channel through the fragment lists |
| 43 | `0bf7fd06ac35f20d4d9a2712184dd3fefba7249a` | 2026-10-10T03:45:07Z | Bypass the fragment lists while a selection renders |
| 44 | `2266effdfc5abca1fd390b734bb8c80e6fe1a1d2` | 2026-10-10T03:45:08Z | Test that selection is unchanged by the deep framebuffer |
| 45 | `ffef5b472bbd559f6b50b4fa688d4a3f3a54c9e6` | 2026-10-10T03:45:08Z | Report point ids from the glyph and composite mappers |
| 46 | `2ccd383005c452694747c1f596e84fa0011be66e` | 2026-10-10T03:45:08Z | Hide points behind the surface during a point selection |
| 47 | `aa1d24a361c4d95e92fb83545c29ee1e134ce2d0` | 2026-10-10T03:45:08Z | Add a release note for the deep framebuffer transparency |
| 48 | `67a76ae77ac14fc551be2855731bd06d62177d26` | 2026-10-10T03:45:08Z | Keep the wasm test exit code when output contains a semicolon |
| 49 | `7aacf46a720bce2c3c8d82b4ad3be33f44ce70d9` | 2026-10-10T03:45:09Z | Resolve deep framebuffer in a separate render pass |
| 50 | `eebf2afcb7228d59963cce86ffb716a42c2a99fc` | 2026-10-10T03:45:09Z | Avoid fragment shader discard in WebGPU deep framebuffer passes |
| 51 | `30eea124805c14b86b91e2569e5510079367400b` | 2026-10-10T03:45:09Z | Prevent D3D12 device hangs during WebGPU deep framebuffer resolve |
| 52 | `5effacf484837f3a5a3a2875d018c2f9cbf1a697` | 2026-10-10T03:45:09Z | Use vtkLog instead of iostream in WebGPU deep framebuffer tests |
| 53 | `17412865bd84caf84e66efa936f6146cca60db09` | 2026-10-10T03:45:09Z | Make A-buffer resolve order-independent for exact depth overlaps |
| 54 | `18a79148f56c8c2a614783b869cf01ff4c8578be` | 2026-10-10T03:45:10Z | Fix ghosting bug in deep framebuffer |
| 55 | `c6adad7cc8f3884f5ceb46b97a276d61e2848718` | 2026-10-10T03:45:10Z | Add interactive mode support to deep framebuffer tests |
| 56 | `086c77d8bc6f60c8e4264d69f34269524e0d61e5` | 2026-10-11T13:42:17Z | Scale ANARI directional lights to match the OpenGL backend's brightness |
| 57 | `94556f8489938d5cdd36cceb001ef9b308b02415` | 2026-10-11T14:10:54Z | Merge topic 'webgpu-transparency-abuffer' |
| 58 | `f417a3698995ff499788f64a30ad1eb5b21d6afc` | 2026-10-11T14:29:09Z | Correct the layer count for the deep framebuffer node pool in the release note |
| 59 | `c5f51ce0bae6577300338a518c6ca8e191397577` | 2026-10-12T04:01:02Z | VTK Nightly Date Stamp |
| 60 | `24625e37e87ef9ad7afa41bd6810a1d4fd2edb56` | 2026-10-12T06:49:54Z | Merge topic 'fix-warning-in-egl-master' |
| 61 | `ad67eaff685e595443881a21cfbf79027513a6f8` | 2026-10-12T07:30:30Z | Merge topic 'tecplot-reader-varsharelist-varlocation' |
| 62 | `00354ab8c86d9b26da9694dfdcc187d69b704e76` | 2026-10-12T07:36:21Z | Merge topic 'vtkhdf-image-cache-release' into release |
| 63 | `50af3508056de8947491052a3a445b091a753b1c` | 2026-10-12T07:36:21Z | Merge branch 'release' into master |
| 64 | `c5740cef0e6cd47f2a721ac76ca3783eee4ecf29` | 2026-10-12T09:23:00Z | Merge topic 'fix-warning-in-egl' into release |
| 65 | `4c5156b80acfb026c530d3b463668fd47c6e6009` | 2026-10-12T09:23:01Z | Merge branch 'release' into master |
| 66 | `d7f393e383f3abcf8b1fef3bfe2ca6ecb5bc9a68` | 2026-10-12T12:20:33Z | Merge topic 'fix_TestAbortExecute_race' |
| 67 | `91de455775b5bf0edc4aa2d546d393deb26a56ea` | 2026-10-12T12:38:45Z | Fix PBR LUT precision with GLES |
| 68 | `b0a99f2669c2a15935e0b6344915cb095caf1227` | 2026-10-12T15:15:59Z | Merge topic 'fix-anari-dangling-observers' |
| 69 | `68477f2ebefac1f973718dd43ec206fe84c08d84` | 2026-10-12T15:18:55Z | Keep DLPack export callbacks alive through interpreter shutdown |
| 70 | `219898cdfabe7d3fc0588c34b2e7b1843d236e1f` | 2026-10-12T15:18:55Z | Reject Metal tensors in dlpack_to_vtk |
| 71 | `168be562d9f574c2a612a2a6003b3d0d1830bb12` | 2026-10-12T15:35:00Z | Make vtkMemoryDescriptor addresses unsigned |
| 72 | `c17aeaa189a18260828c1bf9fcae824d997ed0bb` | 2026-10-12T15:35:00Z | Describe only memory a Viskores array already occupies |
| 73 | `2d176ab00e23024194eac4078e7bcde8b8f3430f` | 2026-10-12T15:35:00Z | Match a Kokkos build's memory space to its backend |
| 74 | `80d9ed77b2f8eb79d8077ace1bc045130bdfcd36` | 2026-10-12T15:35:00Z | Add DLPack and Viskores interop on Level Zero |
| 75 | `0003f2c53f081fdd493edf348c1c02df0fefa221` | 2026-10-12T21:32:31Z | Restore the comments stripped from the WebGPU mapper and renderer |
| 76 | `03e97ec4393aebb0982fc84c1e28da7a02f56cf4` | 2026-10-12T21:42:38Z | Fix component count when reading back ANARI window pixels |
| 77 | `071c6bc27a7e609b5fe4008c8a91b6b41a7b7055` | 2026-10-13T04:01:04Z | VTK Nightly Date Stamp |
| 78 | `41d28e01b5f2a3d2e88f07e9db08964a95470a8b` | 2026-10-13T08:48:52Z | Merge topic 'fix-lut-precision' |
| 79 | `42a0b8c21bfc50fdf7b03c51c043798c8cc5dab0` | 2026-10-13T12:14:51Z | CI: Exclude more macos tart timeouts |
| 80 | `9dbcc9c8bd567416bec77a320feed603a285f05e` | 2026-10-13T15:23:58Z | Add an issue template |
| 81 | `db753601f587d5f78c8892472eb53ecdf443182e` | 2026-10-13T15:48:04Z | Merge topic 'issue-template' |
| 82 | `81058ebcdfb790e1395463c71284cb21c1dfe2b9` | 2026-10-13T15:52:37Z | Merge topic 'webgpu-abuffer-release-note-layers' |
| 83 | `eb215a6f25b6ceb5fa3e61a66d87eb651e5b1027` | 2026-10-13T19:49:27Z | Merge topic 'webgpu-camera-pass' |
| 84 | `6af29fc9370fc1358555aff45372e4d098a15719` | 2026-10-14T03:23:39Z | Convert ANARI environment textures to linear radiance |
| 85 | `f8201404ec7262906037ba6b8eb3c1e80594ab35` | 2026-10-14T04:01:02Z | VTK Nightly Date Stamp |
| 86 | `f47296d4876cf2b54231c88c8dd41f8cef3b062e` | 2026-10-14T07:40:41Z | Merge topic 'fix_vtkhdf_caching_issues' |
| 87 | `7c014b6d5c9d62d6522a6cec4c8e85d369b788e9` | 2026-10-14T11:30:39Z | Chemistry: Add Individual Bond Coloring to vtkMoleculeMapper |
| 88 | `2d6f72eafbc2308c4ee8eb16745c9b4419cde55a` | 2026-10-14T12:18:07Z | Merge topic 'vtkobjectbase-size' |
| 89 | `22c7d1d005f48c30b6f7a58ca8adec2e7db476d6` | 2026-10-14T15:41:36Z | nanoflann: update to 2.0.1 |
| 90 | `b57ff495000b1a82ce4bcc69250c21173e96b3e2` | 2026-10-14T15:41:48Z | nanoflann 2026-10-12 (69d8bb49) |
| 91 | `9d0342c1d8945790e4e7d54e4ea076d43bbaeb92` | 2026-10-14T15:41:48Z | Merge branch 'upstream-nanoflann' into repurpose-vtkKDTreePointLocator |
| 92 | `e4072dec9a2ff2890d442dc73acca759ea00ae56` | 2026-10-14T18:08:52Z | Fix coincident topo offset units to resolve depth correctly |
| 93 | `b1c122f16f201f7e3b8753ebaed9b379baea61e2` | 2026-10-14T18:08:52Z | Fix 1 pixel lines for wireframe representation in the low-memory mapper |
| 94 | `b91196deb4f564b20f4941918292e6bee5a1fd54` | 2026-10-14T18:08:52Z | Fix thick lines in wireframe representation with low-mem mapper |
| 95 | `2b9b9f11eb5f05ee0b2f8aeac900d6490650c889` | 2026-10-14T19:31:49Z | ThirdParty/fides: Update to latest version |
| 96 | `d534caf2fd9b7ba010e1e19f462184aa40055cbf` | 2026-10-14T19:33:02Z | fides 2026-10-14 (80cb16c9) |
| 97 | `a2e07a6f92d26bd650884d3585ed6851e9f96f9c` | 2026-10-14T19:33:03Z | Merge branch 'upstream-fides' into update-fides-20261014 |
| 98 | `d95c9aa6cd9edfd54380a4ecd355bbf67efebc14` | 2026-10-15T02:51:07Z | vtkKdTreePointLocator: Replace vtkKdTree with nanoflann |
| 99 | `2d3f3b55debb796e666a4c7ba0dafaf8f12bce7a` | 2026-10-15T02:51:08Z | TestKdTreePointLocator2D: Test the queries of the 2D and 3D kd-trees |
| 100 | `e534d189f6cc80f53c61255919632ea70387c7d8` | 2026-10-15T02:51:08Z | vtkAbstractPointLocator: Add FindPointsInShell |
| 101 | `fb555ce2fd0920689c8460f09484f086c9158dff` | 2026-10-15T02:51:08Z | vtkAbstractPointLocator: Test FindPointsInShell |
| 102 | `1e31361b46651aab0824cf4b22efafc7779dc2d5` | 2026-10-15T02:51:08Z | TestPointLocators: Test the points at the radius |
| 103 | `c813ff0a681afb30dfe67b22136ad4d30c2e9ca3` | 2026-10-15T02:51:09Z | vtkAbstractPointLocator: Test the shells on the bucket boundaries |
| 104 | `bb1e7e774e33c8ccffff1f7737e1b81a02a5499a` | 2026-10-15T02:51:09Z | vtkAbstractPointLocator: Add FindNPointsInShell |
| 105 | `fb7b87fcc0eb2fd68e413d8a11035906859a51e7` | 2026-10-15T02:51:09Z | vtkAbstractPointLocator: Test FindNPointsInShell |
| 106 | `d7b69eea15dd4175a81f6f045ceeed0f3d1c278c` | 2026-10-15T02:51:09Z | vtkAbstractPointLocator: Test FindNPointsInShell for every locator |
| 107 | `c8989dfa5ddf22c1160f883a547b3bb6b86155e7` | 2026-10-15T02:51:10Z | Voronoi filters: Add SetPointLocator, using vtkKdTreePointLocator by default |
| 108 | `cee01034a12788b17f11f24657fb04936449fd56` | 2026-10-15T02:51:10Z | Voronoi filters: Update the tests for the default kd-tree |
| 109 | `f58d48cd410ddddebc144e3a9112aa5d043e80d8` | 2026-10-15T02:51:10Z | Add changelog |
| 110 | `23c6598c38cd3436b18249dc8c5f424eea278d83` | 2026-10-15T04:01:02Z | VTK Nightly Date Stamp |
| 111 | `e1c6621c08fb00e84854e7ce3da16aeec01c5965` | 2026-10-15T07:40:36Z | Merge topic 'macos_ci_exclusions' |
| 112 | `cd8578ad48ff5a07772478d1519dfd406eed4b2c` | 2026-10-15T12:35:10Z | Fix ANARI data array update when using poly data |
| 113 | `9947452a5b1c2d4f3a5205c4edb3c3d246cc0880` | 2026-10-15T14:52:38Z | Merge topic 'anari-brightness' |
| 114 | `3b372b4cba08c22afcf5a4655d18e1138c8002d8` | 2026-10-15T15:29:49Z | Merge topic 'repurpose-vtkKDTreePointLocator' |
| 115 | `cc3fe9a92710a7bda6ac3c7a40d462b8ac37303e` | 2026-10-15T17:21:39Z | Render ANARI skyboxes with their OpenGL shader |
| 116 | `b35205d51024244e3e063541d5df41eb77a4eeee` | 2026-10-15T17:21:39Z | Test ANARI skybox colors and foreground depth |
| 117 | `a6bfc8ee10faf3faa32fa3def6db76fd91a90191` | 2026-10-15T18:32:15Z | Fix Win32 interactor repeat count |
| 118 | `80ff80281a9a8e664d597d20338e1b531c98a579` | 2026-10-15T19:22:44Z | Document the ANARI skybox brightness fix |
| 119 | `83204cbf8965e31d778d1007e5d0f3f7a619cd01` | 2026-10-15T19:42:24Z | Keep the ANARI frame pointing at the current renderer |
| 120 | `e2121f23c760788c949f3461ac95bc2ac3b50563` | 2026-10-16T01:42:54Z | Do not skip the WebGPU surface when the view is externally owned |
| 121 | `12c851cc8c620f48a4f0eed8adce5cc2f9d82fc2` | 2026-10-16T04:01:02Z | VTK Nightly Date Stamp |
| 122 | `7ab7a113a05cff141b3d3ad8cbf5e3d2fa8d08f4` | 2026-10-16T06:05:20Z | Fix OpenGL shadow pass |
| 123 | `d01887086a87c463e2d21118a37f058b1c968109` | 2026-10-16T07:19:30Z | Merge topic 'fix-win32-repeat-count' |
| 124 | `fb2c316f7bf7e59a84eeea4156c80cda2a450d10` | 2026-10-16T08:38:21Z | Fix compilation on Windows |
| 125 | `473b7fa73cf6c16d415d07c6254148e9c9a862e4` | 2026-10-16T11:57:52Z | Merge topic 'fix-shadow-pass' |
| 126 | `dbb73e9cc80d20821ae63949c5f80e72fa5ea240` | 2026-10-16T14:59:25Z | Merge topic 'fix-windows-build' |
| 127 | `06c1dc3c9ae36267be8d7fa1332189d31a258d3d` | 2026-10-16T15:58:02Z | Merge topic 'webgpu-wasm-external-view' |
| 128 | `a26f0e4ec7982b1ab9d4000839dee58b0f0ecd30` | 2026-10-16T16:34:37Z | Apply the actor opacity once in the WebGPU fragment shader |
| 129 | `738f05c3f07debd02497600c10cc18cbf65697d1` | 2026-10-16T18:32:41Z | Merge topic 'coincident-depth-resolution' |
| 130 | `2bc1aa5033b3568bd200b20a77313de4d0898110` | 2026-10-16T19:32:01Z | Merge topic 'fix-vortexcore-polyhedral-meshes' |
| 131 | `edf29959b59c1c64bc324471ed93cf9eaa0e24c5` | 2026-10-16T22:48:52Z | Fix vtkWebAssemblyRenderWindowInteractor::SetCanvasSelector |
| 132 | `4287612ab3f85fc93224f0c6607f005b45de14cc` | 2026-10-16T22:48:52Z | wasm: Ignore mouse forward and back buttons |
| 133 | `a1dd3672b87e3f5f605ae1d1f619d8e4e51660da` | 2026-10-16T22:48:52Z | Fix undefined behaviour in EventDataWrapper::Data declaration |
| 134 | `4f19ea8b68de3f007933fbafe2791c72db515e04` | 2026-10-16T22:48:53Z | wasm: Fix logic error in resize callback removal |
| 135 | `c164bd1ce8fdb5fa184a9769ecf40dec6be4f8a7` | 2026-10-16T22:48:53Z | wasm: Fix leftover timers leaking the internals pointer. |
| 136 | `ee8733dfc0659c716bb37fe5a5d17d81213fc6fe` | 2026-10-16T22:48:53Z | wasm: Only destroy timer if it exists in the Timers map |
| 137 | `b6e04541a013e50aeb34fc383c71fe6e44e411c2` | 2026-10-16T22:48:54Z | wasm: Pop events from the queue before processing them |
| 138 | `9bcda67564618a678cb2b3b0ba6f5381eeaf7fec` | 2026-10-16T22:48:54Z | wasm: register the dbl-click, focusin, focusout callbacks |
| 139 | `5d3a65f1595ea6644f3b8fe717b20b335a0f6561` | 2026-10-17T01:24:27Z | Find a real interpreter for the DLPack shutdown test's child |
| 140 | `5197898a9725540acda3a7e0dab72727b09de40b` | 2026-10-17T04:01:03Z | VTK Nightly Date Stamp |
| 141 | `847d6b16d87a08e37f8c63fad40e39501553663e` | 2026-10-18T02:58:55Z | Merge topic 'remove-unused-content-links' |
| 142 | `f261aa08e9a19595937b9501dc98ca607526b753` | 2026-10-18T04:01:05Z | VTK Nightly Date Stamp |
| 143 | `89efb1a19581543bc35869d842f43b438cc0f60e` | 2026-10-19T03:51:14Z | Use volume matrices in the OpenGL fluid mapper |
| 144 | `c00223809d83b03e5359cff996002c2f99894cb5` | 2026-10-19T03:51:15Z | Exercise volume transforms in the fluid mapper test |
| 145 | `f072778c8be2cf16dad60c815d8af0521d5c22f9` | 2026-10-19T03:51:15Z | Match integer pointer deserialization with array deletion |
| 146 | `46f87ca2d440fdd2a137d301eec72837e8616437` | 2026-10-19T04:01:01Z | VTK Nightly Date Stamp |
| 147 | `4c6583b4f4c9fdb158b45d85e64cec1ecda78915` | 2026-10-19T08:06:49Z | Merge topic 'fix-anari-dataarray-update' |
| 148 | `6466418cbda095525a1b12a31f41ae8410752e83` | 2026-10-19T09:04:55Z | Merge topic 'individual_bond_coloring' |
| 149 | `767a1866e6f2e8573b6d1f8fa2fd441670336a3b` | 2026-10-19T13:08:23Z | vtkShrinkFilter: Use CheckAbortAndInvoke |
| 150 | `d704d848896466516057b2a2b24494c55f70a37e` | 2026-10-19T13:08:23Z | vtkContourGrid: Use CheckAbortAndInvoke |
| 151 | `a61ddb267cd5db8c5cb68f7965efa47709c43af3` | 2026-10-19T13:08:23Z | vtkClipDataSet: Use CheckAbortAndInvoke |
| 152 | `e80261a9a1562b813cd86b76748ba5f3a49f5eb8` | 2026-10-19T13:08:23Z | Doc: add release note |
| 153 | `5cf9751543ecd5370c65ffeab656ce09bb8a2c9d` | 2026-10-19T14:29:42Z | Merge topic 'wasm-fix-set-canvas-selector' |
| 154 | `fd9586b236e8e237c7e66f4cc54c7f9829c460c2` | 2026-10-19T21:02:59Z | Fix win32 interactor crash with hardware window vtable |
| 155 | `74aaf29242fb8a2f5dd1c96e99de3f8939a46555` | 2026-10-20T04:01:03Z | VTK Nightly Date Stamp |
| 156 | `623b47ae0ed5c5463ae1af40a89e2b3657605156` | 2026-10-20T09:25:52Z | ANARI: fix update for timestep |
| 157 | `c50c0c12fc66e6c90cb9fe5c7e799b183bc1f666` | 2026-10-20T09:29:50Z | ANARI: add test for temporal dataset |
| 158 | `0e89a0ed5ce3935e78e12edde4aca919e0fcdbe6` | 2026-10-20T11:32:25Z | Merge topic 'win32-iren-crash' |
| 159 | `ff43e9f4cd993c07c565f227e66783fad81c81cb` | 2026-10-20T12:19:09Z | ci: do not hold back weekly wheel uploads when tests fail |
| 160 | `1850e69f2b33f54af671eb2655ab6a8a6a8bb0ff` | 2026-10-20T12:32:10Z | Merge topic 'UseCheckAbortAndInvoke' |
| 161 | `97bf498dcb5670394716f6f8d4fd4fd53a2182c6` | 2026-10-20T13:39:50Z | Reviewers: sort list by domain |
| 162 | `4a6330a4cfd3e9b1e5fb27ec8b93deef3b744e2e` | 2026-10-20T13:39:50Z | develop.md: fix typo |
| 163 | `140abbc2ce6f8201e93995163c690ec60b51f9e1` | 2026-10-20T13:39:50Z | develop.md: add new reviewers for some domains |
| 164 | `6c1456b68c53e3b91274a87cbbd00739691b4734` | 2026-10-20T13:39:50Z | develop.md: add mathieu for cmake review |
| 165 | `eed5006b5840ab622341df15d18a1399b7828cb6` | 2026-10-20T14:14:55Z | Merge topic 'add-reviewers' |
| 166 | `64179faead458ee4e0fa446d3fce66c1f42309f2` | 2026-10-20T16:04:59Z | Merge topic 'dlpack-level-zero-linux' |
| 167 | `be02c243844da4f1b8122d4cbcbc914182a392cc` | 2026-10-20T16:05:28Z | Merge topic 'dlpack-shutdown-and-metal' |
| 168 | `3d3ae566fac4da33a777fc3186fa28672fbdb332` | 2026-10-20T16:46:05Z | Merge topic 'update-fides-20261014' |
| 169 | `b01129d7b5c6e7752e871f7689a2a321e7525872` | 2026-10-20T19:34:44Z | Merge topic 'anari-bg' |
| 170 | `95530399fe3871b821dc895c7020a0f9a7f779d2` | 2026-10-20T19:39:19Z | Merge topic 'anari-skybox-brightness' |
| 171 | `527c4d6247d8e093f941a157235e605c2285b828` | 2026-10-21T04:01:05Z | VTK Nightly Date Stamp |
| 172 | `45f4894a1cb2b22e1ecdc318fc0709e4eb833b35` | 2026-10-21T12:38:11Z | develop.md: add multiple reviewers |
| 173 | `12f73a6d5a06efdeb9c5c5fd8b0322a85b55756d` | 2026-10-21T12:39:44Z | develop.md: merge duplicate domain |
| 174 | `ebe1fa11c4d934d477124904ac3865b9ab3485d1` | 2026-10-21T14:43:36Z | Merge topic 'update-reviewer-lists' |
| 175 | `b71d3be24df23aebd093a18c74e5b68495280f05` | 2026-10-22T00:27:31Z | Merge topic 'wasm-pop-events-before-processing' |
| 176 | `1feb98772362e2528dd4d6e20e07c3792d659c70` | 2026-10-22T01:44:12Z | Merge topic 'wasm-ignore-mouse-forward-back' |
| 177 | `3321148ec66e680a3735b5ed2e2d403e0769074b` | 2026-10-22T04:01:02Z | VTK Nightly Date Stamp |
| 178 | `2a49f52e51bf535acb20bf4c16fd469bdcbf65a2` | 2026-10-22T11:35:40Z | Merge topic 'fix-update-timestep-anari' |
| 179 | `97db5fa15b9837f5a7cd7e291a906cbecbb8efc2` | 2026-10-22T14:05:49Z | Merge topic 'wasm-register-dblclick-focus-callbacks' |
| 180 | `0b6d83a1da979ae3fa02370ee329f5aa41d793ce` | 2026-10-22T14:10:04Z | Merge topic 'fix-eventdatawrapper-ub' |
| 181 | `d7e57e022b13fbd99af7ba73daa5061e98c05010` | 2026-10-22T14:20:38Z | Merge topic 'wasm-fix-resize-callback-removal' |
| 182 | `3e507935d20f912b5d7d509b66b8106b36a43490` | 2026-10-22T14:37:49Z | Merge topic 'wasm-fix-timer-internals-leak' |
| 183 | `7ad541f889bcbf13480d782985c59f1a26222176` | 2026-10-22T15:05:24Z | Merge topic 'ci-weekly-wheels' |
| 184 | `9f0588e2fe0d10573555834a66ac3dab95be4114` | 2026-10-22T15:12:57Z | Merge topic 'wasm-guard-destroy-timer' |
| 185 | `18501543f39c984aaf190e134ff3c8b9a6caaf9b` | 2026-10-22T16:20:38Z | Merge topic 'webgpu-fix-squared-opacity' |
| 186 | `fd4e4df88375e5f7f2b1c201c1f526f54ba49e1c` | 2026-10-22T16:21:21Z | Merge topic 'fix-fluid-mapper' into release |
| 187 | `abdc0e9ff7c52a877d80ddc9c5b8fd6be51dd1c6` | 2026-10-22T16:21:25Z | Merge topic 'fix-fluid-mapper' |
| 188 | `be385f1c26ca5699f5b17578c690a0d83eed9ec5` | 2026-10-22T16:21:25Z | Merge branch 'release' |

</details>
