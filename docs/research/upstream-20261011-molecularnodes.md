# MolecularNodes 主干更新与适用性研究

核查日期：2026-10-11。QCBlender 产品比较基线为 `413168ea917fdbf98c27aa50787e296cae91effc`；实施范围以[本批规格](../../.scratch/upstream-20261011/spec.md)为准。本报告保存来源比较和已批准的采用范围，不代表产品实现或 Blender 验收完成。

## 1. 最近实际参考版本与本批目标

最近有明确日期和源码身份的参考研究是[GitHub 发布流程研究](github-release-workflow.md)，核查日期为 **2026-10-05**，固定 MolecularNodes `999b0b5e8f576c83b3dd854819303fe00c0507a0`。该研究首次进入 QCBlender 的提交是 `5d899e508788ebf3b9b58a170a18a494133ebeb6`；2026-10-06 后续文档整理保留相同参考身份。此前[2026-09-28 参数研究](molecularnodes-parameters.md)和[2026-10-03 完成审计](qcblender-completion-audit-2026-10-03.md)也明确使用该提交。因此它是实际研究基线，不仅是本次观察到的 gitlink。

| 身份 | 固定值及依据 |
| --- | --- |
| 官方仓库 | [BradyAJohnston/MolecularNodes](https://github.com/BradyAJohnston/MolecularNodes)，由仓库 [.gitmodules](../../.gitmodules) 定位 |
| 最近实际研究基线 | `999b0b5e8f576c83b3dd854819303fe00c0507a0`，版本 520.2.1 |
| 本批默认主干目标 | `f88961b28828dfb32697748b575298dec20af3af`，版本 520.3.0 |
| 在线身份核对 | 2026-10-11 执行 `git -C submodules/MolecularNodes ls-remote --symref origin HEAD refs/heads/main`；HEAD 指向 `refs/heads/main`，两项均返回上述目标，且与本地已有 `origin/main` 一致 |
| 比较范围 | `999b0b5e8f576c83b3dd854819303fe00c0507a0..f88961b28828dfb32697748b575298dec20af3af`，`git rev-list --count` 返回 18 |
| 本报告查询时的 checkout | `999b0b5e8f576c83b3dd854819303fe00c0507a0`；主 Agent 独立负责后续 fetch、checkout 和主仓库 gitlink 更新 |
| 浅克隆约束 | 查询时 `--is-shallow-repository=true`，`remote.origin.tagOpt=--no-tags`；本报告未修改配置或 ref |

上游目标的 [pyproject.toml](https://github.com/BradyAJohnston/MolecularNodes/blob/f88961b28828dfb32697748b575298dec20af3af/pyproject.toml) 声明 Python `~=3.13.0`、Blender 最低 `5.2.0`、`nodebpy>=520.34.1` 等依赖。本项目继续遵守[单扩展 ADR](../adr/0001-self-contained-extension.md)，目标 Blender 5.1.1；参考更新不增加运行依赖，也不表示上游资产可直接安装到 QCBlender 支持环境。

## 2. 完整后续提交列表

以下按 `git log --reverse` 的拓扑顺序列出，日期为提交记录中的 author date。标题保留上游原文；分类和采用判断属于本报告分析。每个完整 SHA 均可在[官方仓库提交页](https://github.com/BradyAJohnston/MolecularNodes/commits/main/)以固定提交定位，本地精确对象可通过 `git -C submodules/MolecularNodes show <SHA>` 复核。

| 日期 | 完整提交 | 标题 | 分类与本批判断 |
| --- | --- | --- | --- |
| 2026-09-29 | `46bc57b8b45d9e8282e17b2b2ae2180b599430b6` | Bump nodebpy (#1251) | 上游工具链；不引入 |
| 2026-09-30 | `b575452248c4e138416cc3a97018f44602fbd3de` | Fix #1253: oxDNA unpickling on reloading a .blend (#1254) | oxDNA/pickle 会话修复；不替换 QC JSON/NPY 工程 |
| 2026-09-30 | `75355528927b1eb5eee2c42195bb95ec3cb2c1ea` | Support Fading Geometry (#1255) | 显示淡入淡出；已有 opacity 机制，本批不增加动画功能 |
| 2026-09-30 | `2eb05987d0fa60678ea2d793c95fe4bc886270af` | Add the Color matplotlib node (#1252) | 颜色；采用少量冻结色带数据与明确应用方式 |
| 2026-10-07 | `08cd56028c6b4e7f73458e30406bf77e6d972ec8` | Bump `nodebpy>= 520.34.0` and re-dump (#1261) | 上游工具链/节点重生成；不引入 |
| 2026-10-07 | `ba7783b59f0d3f9538e2f4f48045275a17e732ca` | ENH: Ease Value and Stagger Value nodes, easing and stagger in Animate Action (#1241) | 展示动画；不赋予真实计算步插值含义，本批不采用 |
| 2026-10-07 | `7e5fe2e369b716d22f96984c8a9caba58299ada1` | ENH: Symmetry builder nodes (Cyclic, Dihedral, Helical) (#1210) | 对称展示；当前量化结果范围外 |
| 2026-10-07 | `860ba0d86128d14b91e086d1fff27bb6cef0c205` | ENH: Symmetry Cubic node and axial symmetry for Symmetry Helical (#1263) | 对称展示；当前范围外 |
| 2026-10-07 | `6b6a3e21cfe913d9b2a68d11789d02aafb322c60` | bump nodebpy; menu switch default | 上游工具链/默认值；不引入 |
| 2026-10-08 | `0339f914c3fcd597527e61a351fa9f526c9bab9e` | FIX: Build biological assemblies from .pdb files (#1264) | 生物组装；当前科学数据范围外 |
| 2026-10-08 | `53e435410c748f8584ac6857ffa7524f05498fce` | Restrict `is_alpha_carbon` and `is_backbone` to polymer residues (#1265) | 生物结构语义；不新增残基模型 |
| 2026-10-08 | `8047387476d05e6fde5d305c4c15da62c86681c4` | Document attribute encoding, availability by format, and reading from Python (#1266) | 属性文档；补现有合同中的缺失属性和原始/求值边界 |
| 2026-10-08 | `68f0f8c3692b7ec47b77fd6d8a066eabe8951ef7` | initial codspeed benchmarks | 性能方法；扩展本地量测，不添加 CodSpeed 依赖 |
| 2026-10-08 | `ef62eaa61d453062143335fb5b9be7ab15812576` | Load test structures from tests/data; run network tests in one CI job (#1272) | 测试输入与网络隔离；复用 QC 已有本地输入与证据机制 |
| 2026-10-08 | `9b126475b8708d2cac4954293c412a68110798a7` | Speed up structure loading (#1267) | 加载/属性转换；采用分阶段量测思想，优化需有 QC 热点证据 |
| 2026-10-08 | `2297d06290b3af713ce098050a32d98714d12510` | Set atom types from elements instead of guessing from atom names (#1268) | 元素身份；QC 已由解析原子序数驱动，不据此宣称同类缺陷 |
| 2026-10-08 | `25ebcc82cf2c0eb00e623af57eaea2b6c0ac6397` | Link asset groups in one library read and ship nodes.blend uncompressed (#1271) | 资产加载；QC 主显示从源码构建且复用资产，不直接套用 |
| 2026-10-08 | `f88961b28828dfb32697748b575298dec20af3af` | Speed up Style Sticks, Ball and Stick and Surface (#1273) | 样式求值/SDF；热路径和科学网格边界不同，本批不直接移植 |

## 3. 采用：固定色带预设

直接来源为 [2eb0598 的 Color matplotlib 节点源码](https://github.com/BradyAJohnston/MolecularNodes/blob/2eb05987d0fa60678ea2d793c95fe4bc886270af/molecularnodes/nodes/geometry/color_matplotlib.py)、[生成程序](https://github.com/BradyAJohnston/MolecularNodes/blob/2eb05987d0fa60678ea2d793c95fe4bc886270af/docs/dev/colormap_node.py)和[数值测试](https://github.com/BradyAJohnston/MolecularNodes/blob/2eb05987d0fa60678ea2d793c95fe4bc886270af/tests/test_nodes.py)。生成程序说明 matplotlib 仅用于生成，运行时数据内联；本批采用数据，不引入其生成工具链。比较该文件的 `2eb0598..f88961b` 差异，仅生成说明和菜单默认值改变，Viridis/Cividis 数据及插值未变。

| 预设 | 固定内容 | 科学显示用途与边界 |
| --- | --- | --- |
| `QC_DEFAULT` | 现有三个 RGBA：`0 → (.8,.03,.02,1)`、`.5 → (.95,.95,.95,1)`、`1 → (.03,.18,.8,1)`；RGB/LINEAR | 保留当前红白蓝默认映射；量名、中心值和范围仍来自现有参数 |
| `VIRIDIS` | 上述上游文件全部 13 个 RGBA 色阶；RGB/B_SPLINE | 顺序色带选择，不自动改变物理范围、中心值或科学量 |
| `CIVIDIS` | 同源全部 13 个 RGBA 色阶；RGB/LINEAR | 顺序色带选择，不自动改变物理范围、中心值或科学量 |

Viridis 色阶位置为 `[0, .033127, .091617, .178541, .295513, .439554, .583146, .693999, .786693, .864936, .928568, .975252, 1]`；Cividis 为 `[0, .030621, .079477, .090894, .18086, .291146, .402322, .519735, .644381, .769231, .884914, .987296, 1]`。实现必须核对固定源码中的全部 RGBA 和插值，不能只取这些位置再重建颜色。两组均少于上游说明的 32 色阶限制。

上游注释称这些数据拟合 matplotlib 3.11.2，Viridis/Cividis 最大 sRGB 误差分别为 0.9/255、0.7/255。这是上游声明；本报告未运行其测试，也未独立复验该误差。QC 应核对冻结表、实际 Blender 5.1.1 ColorRamp 求值、反转和渲染一致性，不将设计参考写成独立色彩学验收。

许可依据是该目标的 [LICENSE](https://github.com/BradyAJohnston/MolecularNodes/blob/f88961b28828dfb32697748b575298dec20af3af/LICENSE) 与 [pyproject.toml](https://github.com/BradyAJohnston/MolecularNodes/blob/f88961b28828dfb32697748b575298dec20af3af/pyproject.toml)：GPL-3.0-or-later，LICENSE 为 GNU GPL v3 文本。两新预设属于固定上游数据复用，应在产品数据文件保留来源与许可说明，并由主 Agent 将确切提交、文件、采用数据及用途加入 [THIRD_PARTY](../../THIRD_PARTY.md)。QC 已有半径表归属仍保留其历史提交，不能用本批目标覆盖历史来源。数据可复用不代表需要打包 MolecularNodes、matplotlib 或 nodebpy。

### 与当前实现的接合点

- [scalars.py](../../qcblender/blender/scalars.py) 的 `scalar_material()` 已创建 `qc_role=color_ramp`、反转、有效掩码及图例共用材质；[ui.py](../../qcblender/blender/ui.py) 已提供 ColorRamp 原生编辑与反转。本批新增的是明确应用的预设。
- [auto_load.py](../../qcblender/auto_load.py) 位于 `qcblender/` 根目录，通过 `pkgutil.walk_packages` 扫描 `blender` 子树；[扩展入口](../../qcblender/__init__.py) 调用它。新增 `blender` 模块中的 Operator 可自动注册，无需添加独立注册钩子。
- [copy_display.py](../../qcblender/blender/copy_display.py) 的 `_state()`、`_material_role()` 已提供标准视图与 `scalar_map`/`charge_map` 材质定位。缺失、重复角色、错误节点类型或不可靠的目标需要明确拒绝。
- [view_summary.py](../../qcblender/blender/view_summary.py) 已保存 `color_mode`、`interpolation`、`hue_interpolation`、位置/RGBA、反转；外层还保存范围和科学身份。完整现有配置足够，不新增 Dataset schema 或持久化“最后选择预设”标签。仅色阶不足以重建插值；手改色阶后仍应导出实际值。
- [layers.py](../../qcblender/blender/layers.py) 的 `copy_layer()` 为 QC 复制层建立独立材质，并保持其表面与图例一致引用；`views.material()` 每次新建材质。原生共享材质时直接修改会同步影响所有引用。对话框明确应用到材质及共享语义，首批不增加自动分离逻辑。

### 最小操作与验收

在现有 Color map 附近提供“应用色带预设…”入口，打开三选项对话框；无预览更新回调，确认后才替换目标 ColorRamp，取消不修改。操作支持一次 Undo/Redo，保留范围/中心/反转/透明度/单位/源数组。自定义色带只在明确应用时被替换，安装、注册和打开工程不重写用户配置。Fog 的两点正负颜色与 opacity ramp 不纳入首批。

验收至少包含三预设完整数值与插值、取消、手工色阶及模式的 Undo/Redo 恢复、共享与 QC 复制层、表面/图例同步、反转、无效采样洋红色、冷重开与实际配置导出。对话框期间目标改变、只读材质或无效角色必须失败且无部分写入。[密度/ESP 教程](../../validation/human/topics/03-density-esp.md) 在现有第 5 步加入预设操作、可观察结果和相邻截图；恢复默认后继续现有电荷示例。

## 4. 采用：扩展原子样式分阶段量测

上游 [68f0f8c 的 benchmarks](https://github.com/BradyAJohnston/MolecularNodes/blob/68f0f8c3692b7ec47b77fd6d8a066eabe8951ef7/benchmarks/test_benchmarks.py) 将导入、样式、轨迹和颜色求值分组，使用新场景避免前轮数据块累积；[9b12647](https://github.com/BradyAJohnston/MolecularNodes/commit/9b126475b8708d2cac4954293c412a68110798a7) 后续修正未实际隔离对象创建的早期基准，拆分解析与转换。采用这种分阶段、真实执行边界的量测方法，不新增 CodSpeed/pytest-codspeed。

QC 已有 [benchmark_fields.py](../../tools/benchmark_fields.py)、[benchmark_display.py](../../tools/benchmark_display.py) 和[基准方法](../../validation/agent/acceptance/visual-performance-baselines.md)。现有显示基准在 CH4 上测 1/8/32 套原子和双相 MO 视图，不是单个大分子的原子/键规模曲线，也不测视口 FPS。[2026-10-04 技术记录](../../validation/agent/acceptance/audit-p2-baselines-validation.md) 中的历史数据不构成本批候选性能结果。

本批补原子数、键数、ball-stick/space-fill/bonds、Quality 的对象创建、节点求值、网格提取计时及进程峰值内存；记录环境、候选/源码/脚本/输入身份、冷热定义、重复原始数据和几何/科学身份校验。工程合成数据明确标为工程负载，不作为科研接受证据。速度仅报告，实际数据变化、错误和超时仍为失败。

`positions.tolist()`、逐原子颜色/半径映射和 RealizeInstances 是可测路径，当前没有本批数据证明它们构成主导瓶颈。因此首批交付量测和诊断报告，不预承诺矢量化、保留实例或后端替换。已有 [render_visual_baseline.py](../../tools/render_visual_baseline.py) 可以复验受影响画面，无需重建视觉回归系统。

## 5. 采用：补充属性与科学身份边界

上游 [8047387 的属性文档](https://github.com/BradyAJohnston/MolecularNodes/blob/8047387476d05e6fde5d305c4c15da62c86681c4/docs/attributes.qmd) 增加编码来源、按格式可用性、缺失 Named Attribute 静默给零及原始/求值几何的区别。QC 的[几何节点合同](../specs/geometry-nodes.md)第 2 节已有属性域、类型、含义表和“缺失不借数值零表示”的规定；本批仅补缺失属性的 Exists/有效位检查及原始载体与样式后 evaluated geometry 边界，不再维护第二份合同表。

[views.py](../../qcblender/blender/views.py) 的原始 POINT 载体有 `qc_atom_id` 零起始源索引、解析的 `qc_atomic_number` 及坐标；界面源编号从 1 开始。球棍/表面求值网格的顶点不能按位置顺序当作源原子。本批真实 Geometry Nodes 过滤后应逐点核对保留的原子身份、位置、元素与可用电荷；复用 [verify_node_helpers.py](../../tools/verify_node_helpers.py)、[verify_display_precision.py](../../tools/verify_display_precision.py) 等已有验证，只有发现真实缺陷才修产品。

## 6. 已具备及不直接采用的变化

| 上游变化 | QC 对照与本批处理 |
| --- | --- |
| `2297d06` 按解析元素设置 atom type，修复 Ca 名称被猜成 C | [readers.py](../../qcblender/readers.py) 读取 IOData atnums，[cube.py](../../qcblender/cube.py) 读取文件原子序数，[xyz.py](../../qcblender/xyz.py) 使用解析元素。保留此身份原则，不宣称 QC 有同一缺陷 |
| `25ebcc8` 批量读取资产库和未压缩 nodes.blend | [assets.py](../../qcblender/blender/assets.py) 按 qc_asset_id 复用并由源码建图；[asset_library.py](../../qcblender/blender/asset_library.py) 的旧资产预览已一次读库；[build_node_assets.py](../../tools/build_node_assets.py) 未请求压缩。无相同已证实热路径，不移植 nodebpy 资产加载体系 |
| `f88961b` 将 sticks 的 19 属性重复采样改为一次 face capture | QC 当前管状键与单材质路径不同，尚无同一 19 属性采样成本。先量测，不套用上游约 5x 声明 |
| `f88961b` 原子 VDW/SDF 正空间处理及实验粗 SDF/SES | 科学 Cube/MO/ESP 的源网格坐标和采样合同必须保留；原子 VDW 表面不是电子密度。不上线新表面，不将上游约 12% 声明当 QC 收益 |
| `25ebcc8` 约 40% 资产库读取改善 | 属上游提交信息中的自身结果；未对 QC 同机同数据测量，不迁移为产品性能结论 |
| `7535552` Fade Geometry | 上游处理 POINT/INSTANCE 的颜色 alpha 并在零淡出时返回空几何；QC 已有显示 opacity，首批不新增淡入动画或以删除几何代替科学缺失处理 |
| 上游 5.2 节点、nodebpy/MDAnalysis/biotite 依赖及生物组装 | 不进入自包含扩展的新运行依赖；不能把更新参考仓库等同于获得 Blender 5.1.1 兼容组件 |

Point/Instance/Mesh 球表示在旧基线 `999b0b5` 已存在，参数研究与完成审计已记录为性能候选；它是旧基线未采用内容，不是这 18 个提交新增功能。QC 当前实例后 Realize 的改变还涉及裁剪、着色采样、标注、提取与导出，需量测和行为证据才能另立实现任务。

## 7. 检查状态与来源复核

| 检查 | 结果 | 范围 |
| --- | --- | --- |
| 最近参考身份与日期追溯 | Passed | 研究文档和 QC Git 历史明确引用固定基线 |
| 默认主干在线身份 | Passed | ls-remote，目标 f88961b 与已有 origin/main 一致 |
| 18 提交范围与源码/文档差异 | Passed | 本地已有 Git 对象的 log/show/diff；未依赖可变网页正文 |
| 许可与固定色带来源核对 | Passed | 固定 LICENSE、pyproject、节点数据、生成说明、测试源码；不是独立法律签署 |
| 上游安装、运行与其性能/颜色测试 | Not Run | 未启动上游插件或运行其测试 |
| 本批 QC 功能实现、科学回归与性能量测 | Not Run | 由本批实施任务维护候选证据 |
| Blender 5.1.1 安装、GUI、Undo/Redo、渲染与冷重开 | Not Run | 由主 Agent 串行验收，不用源码比较代替 |
| 独立人工操作及科研接受 | Not Run | 不代签 |

本报告使用可复查的固定 Git 对象；在线 GitHub commit 页读取曾返回 Cache miss，不将其记为读取成功。未额外下载网页原件或附件，也未修改参考子模块、Blender 环境或用户工程。来源更新、最终候选身份和验收状态由[本批规格](../../.scratch/upstream-20261011/spec.md)及其任务证据衔接；本报告保留此研究快照身份。
