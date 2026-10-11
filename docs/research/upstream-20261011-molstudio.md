# GXNU-MolStudio 主干更新与适用性核查（2026-10-11）

本轮以已有能力改进为范围：更新参考源码身份，借鉴多 Cube 叠加流程补充公开教程；IRC 逐步电荷、DI/ASM/ESM 保留为后续候选。本报告依据固定 Git 对象和 QCBlender 当前代码，不把面板存在、README 声明或上游测试源码等同为运行、数值或独立科研验收。

## 1. 参考身份与方法

| 项目 | 固定身份与证据 |
|---|---|
| 官方来源 | <https://cnb.cool/chem311/GXNU-MolStudio>；与主仓 `.gitmodules` 一致 |
| 最近实际参考提交 | `6f3e859020e27d11511b512a7cc47564386b6216` |
| 最近实际参考记录 | [2026-10-03 综合审计](qcblender-completion-audit-2026-10-03.md) 的参考版本表、十维比较及已采用能力清单（第 102、117–139 行）；不是从当前 gitlink 反推 |
| 较早明确基准 | [MolStudio 对照](gxnu-molstudio-comparison.md) 第 6 行，以及 `.scratch/molstudio-adoption/spec.md` 第 11 行，均记录上述 SHA |
| 本轮目标提交 | `a030398b75e62bd10905c52d04c3f884e0b07fb6` |
| 在线复核 | 2026-10-11，`git ls-remote --symref origin HEAD refs/heads/main` 返回 `HEAD → refs/heads/main`，HEAD 与 main 均为上述目标 SHA |
| 完整比较范围 | `6f3e859020e27d11511b512a7cc47564386b6216..a030398b75e62bd10905c52d04c3f884e0b07fb6`，共 32 个提交，含两个合并提交 |
| QCBlender 任务起点 | `413168ea917fdbf98c27aa50787e296cae91effc`；实施范围以 `.scratch/upstream-20261011/spec.md` 为准 |

研究使用主检出中已存在的完整 Git 对象，通过 `git log`、`git diff`、`git show` 读取新旧树；在线操作仅查询远端身份。源码提交时间包含 2026-09-03 至 2026-10-01，部分早于历史审计日期；这些提交是否属于变化范围，以 Git 可达关系和树差异判断，不以时间过滤。

可复核命令（PowerShell；工作目录为已初始化的 `submodules/GXNU-MolStudio`）：

```powershell
git ls-remote --symref origin HEAD refs/heads/main
git rev-list --count 6f3e859020e27d11511b512a7cc47564386b6216..a030398b75e62bd10905c52d04c3f884e0b07fb6
git log --format="%H %cs %s" 6f3e859020e27d11511b512a7cc47564386b6216..a030398b75e62bd10905c52d04c3f884e0b07fb6
git diff --stat 6f3e859020e27d11511b512a7cc47564386b6216 a030398b75e62bd10905c52d04c3f884e0b07fb6
git show a030398b75e62bd10905c52d04c3f884e0b07fb6:molstudio/panels/irc_panel.py
```

## 2. 全部 32 个提交及分类

下表按本轮 `git log` 顺序列出全部提交。分类表示源码变化的审阅入口，不表示已运行或已采用。完整目标 SHA 已固定；表中缩写在本轮范围内唯一。

| 提交 | 分类 | 提交主题与核查要点 |
|---|---|---|
| `a030398` | 来源文档 | DOI 徽章改用 shields.io 托管 |
| `803d672` | 定位文档 | 定位措辞改为 integrated visualization and workflow platform |
| `92f0c8e` | 科学边界文档 | 澄清波函数分析由 Multiwfn 完成，软件整合可视化与工作流；具体能力仍须逐入口核对 |
| `6ee070c` | 展示文档 | README 标题居中 |
| `2765ad6` | 交互修复与测试 | 切语言不再误触发业务槽函数；新增相关语言回归覆盖 |
| `405815c` | 国际化与测试 | 17 个页签切英文后的中文残留修复；`tests/test_i18n.py` |
| `4c906ce` | 合并 | 合并 `github/main` 分支历史 |
| `0106c0c` | 合并 | 合并 `molstudio/main` 分支历史 |
| `9c235bf` | 路径与隐私维护 | 清除源码、文档中的本机绝对路径 |
| `7bce6d4` | 配置与结构维护 | 面板设置文件位置调整，开发残留收进 `_dev/` |
| `6530060` | 启动修复 | 按文件路径直接运行包内入口也可启动 |
| `abb6e51` | 包结构、功能与测试 | 源码收进 `molstudio`；同时包含新增 ASM IRC、IRC 拆分、多 Cube 叠加、晶体入口及测试，不只是路径移动 |
| `3536efe` | 来源文档 | ChemRxiv 引用信息与 cnb.cool 代码出处 |
| `798512b` | 来源文档 | ChemRxiv 引用信息与 cnb.cool 代码出处的另一分支提交 |
| `4579476` | 定位与归属文档 | README 描述调整，归属细节转入 THIRD-PARTY-NOTICES |
| `9a00a33` | 定位与归属文档 | README 描述与归属位置调整的另一分支提交 |
| `a58b72d` | 展示文档 | 截图章节改名 Gallery |
| `4a03ef1` | 展示文档 | 截图章节改名 Gallery 的另一分支提交 |
| `b333112` | 展示文档 | IGMH 截图与三列布局 |
| `4b5c42a` | 展示文档 | IGMH 截图与三列布局的另一分支提交 |
| `f9d0b93` | 展示文档 | 压缩 AIM/ESP 截图 |
| `f6fcc11` | 展示文档 | 增加 AIM/ESP 截图 |
| `a63cabe` | 展示文档 | 中文 README 增加 AIM/ESP 展示 |
| `1d6f9f5` | ESP 导入修复 | 修复 `esp_viewer` 引用旧 `IBOVIEW_DEFAULTS` 名称导致页签丢失 |
| `11800c4` | 渲染参数 | 独立调整渲染观感参数 |
| `44aea66` | 渲染结构维护 | 旧 OpenGL 预览链移至 `legacy/` |
| `2ca52e0` | 渲染重构 | 重写 GL 渲染内核的 IboView 移植表达层 |
| `917dac3` | 渲染来源归档 | 保留 `_glwidget_iboview.py` 原版快照 |
| `9f60880` | 许可与归属 | 新增 THIRD-PARTY-NOTICES，补移植文件版权头 |
| `ccb9ed6` | 文档 | 中英文 README |
| `0aba0c2` | 展示文档 | 增加并展示界面截图 |
| `a4ff665` | 新分析与交互 | 新增 DI/ESM，增强 IRC 逐步电荷、ESP、主题与画布 |

相似主题的提交是完整可达范围中的不同对象，不能按标题去重。`abb6e51ead17efa785742a0dc7083b8e6f9c4826` 的新增文件尤其需要逐文件核查。

## 3. 已具备能力与本轮采用范围

| 上游入口（目标提交内） | QCBlender 当前位置 | 本轮判断 |
|---|---|---|
| 多分析面板、IGMH/IRI、ESP、AIM、NBO、IRC Mayer、ETS-NOCV | `qcblender/external_fields.py`、`analysis_data.py`、`nbo.py`、`irc.py`、`nocv.py` 及对应 Blender 模块 | 既有外部结果导入路径。旧对照基准中“尚未验收”的描述不是当前新增需求；当前能力须结合相应验证记录核对 |
| `molstudio/panels/cub_stack_panel.py:374–401`：多 Cube 启用、颜色、相位颜色交换与加载 | `qcblender/blender/views.py:216` 的场视图、`blender/layers.py` 的图层、现有正负等值面和材质 | **采用操作组织，补公开教程**；复用既有显示能力，不增加科学类型或运行依赖 |
| ESP 表面与分区面积、极值 | `qcblender/analysis_data.py:50`、`external_results.py`、现有 ESP 字段映射和结果浏览 | 已有字段/外部表合同；不以最新 ESP 面板规模推定新增内核需求 |
| Qt/OpenGL、depth peeling、IboView 派生画布 | Blender 原生 Geometry Nodes、材质、OpenVDB | 架构不同，保持现有 Blender 路径 |
| `tests/test_imports.py`、`test_smoke_ui.py`、`test_i18n.py` | QCBlender 现有科学、节点和安装验证 | 更新“最新树有测试源码”的事实；上游测试本轮未运行 |

多 Cube 教程应使用同一静态构型的公开输入，分别设置每个场的阈值、正负颜色、显隐与图例，并按共享流程渲染、保存、重开。上游 `cub_stack_panel.py` 使用第一个启用 Cube 的结构，全局共用阈值与不透明度；QCBlender 继续使用实际原子身份、构型与场来源关联，以及各显示层自己的参数，不能把第一个文件的几何自动当作其余文件的科研参考。

教程通过本批实际验证后纳入 [Cube 专题](../../validation/human/topics/02-cube.md) 及相应轨道/色带操作入口。截图由本批操作者实际生成，研究报告不提供 GUI 通过结论。

## 4. IRC 逐步电荷：真实输入与延期理由

上游 `a4ff665eff58be8012ccbad56bf2ebc8da81faa0` 新增 IRC 电荷路径；目标树中的 `molstudio/panels/irc_panel.py:178,269,748,1140` 分别提供 Multiwfn 调用、worker、添加电荷和导出入口。QCBlender `qcblender/readers.py:48–51` 已保留 FCHK 原子电荷，`qcblender/irc.py:39–78` 目前只组装逐步坐标、能量和来源，没有保存各步电荷。

已逐一检索公开 P04 的全部 IOData 电荷字段，并计算 SHA-256：

| 文件 | 部分电荷方法 | SHA-256 |
|---|---|---|
| `validation/shared/data/public/P04/step-001.fchk` | 无 | `c801d883cea1804103adc3ca5cf217922c531d65f4a0002cb604492e8980cb2d` |
| `validation/shared/data/public/P04/step-002.fchk` | 无 | `9c8cdd3b495694dce0ca59da58d823df2fc892ce70831477f6d0fca24a492219` |
| `validation/shared/data/public/P04/step-003.fchk` | 无 | `d09831388dcae43afdddb490a2aa6a091622849c05491f68617750f457d37d20` |

六种检索字段是 `Mulliken Charges`、`ESP Charges`、`NPA Charges`、`MBS Charges`、`Type 6 Charges`、`Type 7 Charges`；文件仅有体系 `Charge` 与 `Nuclear charges`。当前使用的 IOData FCHK reader 只将实际打印字段映射为 `mulliken/esp/npa/mbs/hirshfeld/cm5`，不会由轨道或密度矩阵自动补算。来源可由本地运行环境 `outputs/science/iodata/formats/fchk.py:279–293` 复核；运行环境目录不是分发输入，重建方式遵循项目锁定科学环境。

[`tools/generate_tutorial_irc.py`](../../tools/generate_tutorial_irc.py) 的逐点生成流程写入轨道、SCF 密度与真实 Mayer 结果，未计算或写入部分电荷。[C10 验收记录](../../validation/agent/acceptance/tutorial-cu-validation.json) 中 `C10_IRC_annotations_and_cold_chain` 及对应输入身份绑定这批 P04 文件；迁移后的文件 SHA 与原记录相同。

共享输入中另有静态单文件电荷，例如 P01/P03/P05 的 Mulliken 和回归 CH₄ 的 Mulliken/ESP/NPA，但未找到可替代 P04 的真实同体系、同方法多步 IRC 电荷系列。本轮不拼接不同体系或方法，不修改冻结输入，不为正向验收构造科学数值。因此本轮**暂缓逐步电荷**，原 IRC/Mayer 功能保持现有合同。

取得合格实样本后的最小设计方向：

1. 沿用已有 `metadata.charges` 的 `method/array/unit`，每种完整方法可增加一个可选 `step_array`，指向 `(step_count, atom_count)` 数组；原 `array` 仍是与第一步 `positions` 对应的 `(atom_count,)`，避免破坏现有 Dataset 与 atom view。
2. 方法只在所有步都有同单位、同原子顺序且完整有限的数据时可用；部分缺失仅排除该方法并记录缺失步，不让原 IRC 导入失败。不补零、不沿用前步、不插值；损坏数据继续明确报错。
3. `blender/atomic_properties.py` 根据当前 `qc_irc_step` 取电荷；`blender/irc.py` 先准备并验证目标数据，再与坐标一起更新 `qc_charge`。保留共享 mesh 拒绝、Undo/Redo、标注及关联失效路径。
4. 在现有 `Data=IRC` 中按条件追加 `irc_charges.csv`，含步号、源原子编号、方法、charge[e]、源文件及 SHA；复用 `analysis.steps`，不增加分析 kind。旧工程和无电荷输入仍只导出原能量表。

当前构型身份沿用 `qcblender/geometry.py:scientific_geometry`、`blender/geometry.py:current_geometry` 和 `blender/association.py`。逐步电荷必须绑定同一步的来源记录；切步使已有构型关联失效的规则保持有效，IRC 当前步仍不构成独立静态科学参考。

现有 P04 可验证无电荷时导入、切步、能量/标注、Mayer、保存重开和原 CSV 兼容；逐步电荷变化、着色、完整/部分方法组合与电荷 CSV 的正向验收均缺真实输入，不能记录为通过。

## 5. DI、ASM 与 ESM 的科学边界

### DI 与 ASM

此处 **DI 是 Distortion–Interaction（畸变—相互作用），不是电子离域指数**。`a4ff665` 新 DI 面板使用五角色：优化片段 A/B、复合物构型下的片段 A/B，以及复合物。`abb6e51` 新 ASM 面板将同一分解逐点执行。

目标源码：`molstudio/panels/di_analysis_panel.py:1–17,71,91,547,567`，以及 `molstudio/panels/asm_irc_panel.py:280,298,1211`。实现的代数关系为：

```text
DeltaE_strain = (E_A_def - E_A_opt) + (E_B_def - E_B_opt)
DeltaE_int = E_complex - E_A_def - E_B_def
DeltaE_total = DeltaE_strain + DeltaE_int
```

本轮仅核对这些源码关系，未独立确认具体计算实例的片段、电子态、方法、基组及参考态定义，也未运行数值验收。不能因文件名含 TS 或界面写作活化能，就断言结果具备相应科研含义。

上游需要区别处理的细节：

- DI `parse_scf_energy` 读取最后匹配能量，包含泛化 fallback；不能据此确认属于用户选择的目标计算段、目标方法或电子态。
- DI `parse_thermal_correction` 实际读取 `Thermal correction to Energy=`，界面称为 ZPE；该字段与 `Zero-point correction` 不同。
- DI `_get_energy` 和 ASM `read_energy` 缺少所选修正时仍使用电子能；ASM `compute_asm_scan` 会跳过缺能量的点。用于 QCBlender 时必须明确所选能量身份与缺失状态，不能静默混合口径或改变路径点集合。

QCBlender `qcblender/gaussian_log.py:45,124–131` 已记录计算段、方法、角色、源行，并区分 ZPE、热能、焓和 Gibbs 修正/总量。后续若立项，优先使用用户明确选定的既有能量记录与片段角色，先限制为电子能；明确方法/基组、原子组成、片段电荷和自旋、构型关联、参考态及来源。单点 DI 与逐点 ASM 共用可审查代数核心，必须取得公开许可实样本及独立科学验证后再纳入人工教程。本轮不新增这类分析。

### ESM

目标 `molstudio/panels/energy_span_panel.py:59–105` 从用户输入的 Int/TS 能量序列取首末能量差为循环 DeltaG，跨循环分支加入该差值，寻找最大跨度，再用单指数表达计算 TOF。

本轮确认的是源码行为，尚未追溯原始理论的一手论文来独立确认循环闭合定义、符号、简化假设、温度/标准态与 TOF 适用条件，也未完成数值对照。ESM 作为后续研究候选，不能直接移植公式或把界面结果写成已验证催化动力学结论。

### 其他后续入口

`molstudio/panels/ircsplit_panel.py:375,449,580,712` 解析 Gaussian IRC 点并生成逐点/片段 GJF，包含固定路径标签和坐标块假设。计算准备与晶体生成超出本轮已有功能改进范围。后续研究需使用真实多种日志边界样本，保留物理步序、原子身份与明确失败语义。

## 6. 包结构、许可与归属

`abb6e51` 将源码迁入 `molstudio/core`、`panels`、`render`、`ui`，新增 `pyproject.toml`、包入口与测试。QCBlender 参考路径应写明目标树中的新位置；旧研究文件继续保留其固定提交和旧路径。最新树的测试包含导入、离屏界面、语言切换，不能据测试文件存在推定全部分析数值已有独立验证。

`9f60880` 新增根 `THIRD-PARTY-NOTICES.md`，记录 IboView 派生渲染、原子数据与面板语义，以及外部 Multiwfn/VMD/Tachyon 边界；根 LICENSE 与该声明指向 GPLv3-only。目标提交仍保留该归属文件；其中部分文件表路径沿用包迁移前名称，核查时应同时定位最新 `molstudio/render/ovcanvas/` 对应文件。

旧 [MolStudio 对照](gxnu-molstudio-comparison.md) 对其固定树所述“未见 DI/ESM 模块、THIRD-PARTY-NOTICES、自动化测试入口”保留为历史事实；本报告更新最新树的观察。本轮只借鉴工作流，未复制 MolStudio 实现或引入其运行依赖。若后续采用具体源码，需逐文件核对版权、衍生来源和组合分发要求，不能自动把上游 GPLv3-only 改写为 or-later。

安装与科学职责继续遵循 [单扩展 ADR](../adr/0001-self-contained-extension.md) 和 [领域定义](../../CONTEXT.md)：一个 Blender 扩展完成既有数据处理与显示；高级外部分析按明确来源与角色导入；本报告不修改该边界。

## 7. 验证状态与交付范围

| 状态 | 检查 | 证据或限制 |
|---|---|---|
| Passed | 最近实际参考身份查证 | 历史研究与任务规格共同指向 `6f3e859...` |
| Passed | 本轮在线主干身份复核 | `ls-remote` 的 HEAD/main 均为 `a030398...` |
| Passed | 完整提交范围与源码比较 | 32 提交完整列出；通过固定对象核查主要新增入口、包结构与归属 |
| Passed | P04 部分电荷字段与文件身份核查 | 六类字段均缺失；三份 SHA 已与验收材料核对 |
| Passed | QC 数据流与兼容边界阅读 | reader、IRC、当前构型、原子电荷显示、Dataset 和导出代码 |
| Not Run | MolStudio 程序、上游测试与 GUI | 本轮不安装或运行其环境 |
| Not Run | DI/ASM/ESM 及逐步电荷独立数值验收 | 不具备本轮验收材料或理论复核，保持候选状态 |
| Not Run | 本轮多 Cube 教程实际操作验收 | 由后续主 Agent 集成与 Blender 阶段产生新证据，本报告不代签 |
| Not Run | 独立人工/科研接受与发布 | 不属于本报告完成结论 |

本报告仅负责来源与适用性研究。子模块检出更新、教程实施、产品验证和最终证据索引由对应任务维护，不能把本报告的 Passed 扩展为插件新功能通过。
