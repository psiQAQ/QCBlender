# VTK 主干更新与既有功能回归依据

核查日期：2026-10-11。实施范围依据 [.scratch/upstream-20261011/spec.md](../../.scratch/upstream-20261011/spec.md)。本记录提供固定来源与适用性结论；本轮采用原子身份及有效域的回归方法，不引入 VTK 运行库，也不移植提面、采样或文件交换算法。

## 1. 来源、基线与目标

| 身份 | 固定值 | 依据 |
| --- | --- | --- |
| 最近实际参考 | `23f0a095621e91bbdbeace8451e22b950c8e5f46`，`v9.7.0` | [源码借鉴记录](source-adoption.md)、[2026-10-03 审计第 3 节](qcblender-completion-audit-2026-10-03.md#3-参考对象与比较基准)与本批开始时主仓 gitlink 一致 |
| 子模块固定历史 | 主仓 `2f98c397ad596260a9ed94c3cf115cf4051ae95e`，2026-09-27 | `git log -- submodules/VTK`；标题为“chore(references): 固定 VTK 与 MolecularNodes 参考源码” |
| 最近实际比较历史 | 主仓 `26fa9c99bc6011441e9c1981cefb4c79fa742223`，2026-10-03 | 上述审计明确记录 VTK 固定 SHA 与 sparse/partial 范围 |
| 本轮目标 | 默认分支 `master`，`4b0325a981d1f5cfad9d4da4909a8230881b2bf4` | 官方 GitLab 与 Kitware 镜像本轮 refs 查询一致；[固定提交](https://github.com/Kitware/VTK/commit/4b0325a981d1f5cfad9d4da4909a8230881b2bf4)，committer 时间 `2026-10-11T04:01:07Z`，标题 `VTK Nightly Date Stamp` |
| 官方原源 | `https://gitlab.kitware.com/vtk/vtk.git` | [.gitmodules](../../.gitmodules) |
| 官方镜像 | `https://github.com/Kitware/VTK.git` | [Kitware/VTK](https://github.com/Kitware/VTK)明确标识为 Visualization Toolkit repository 的镜像；本报告补丁、提交清单及文件内容读取均通过该镜像 GitHub API |

本轮固定主干身份与旧研究的采用依据分别记录。历史审计仍对应原 SHA，不把旧技术验收改写为新主干验收。VTK 的构建、运行及全部变化的行为验收不在本次来源调研内。

本轮早期访问 GitLab 网页/API 返回 403，两次 GitLab `ls-remote` 查询长时间无输出，随后通过本次终端执行会话 `97495`、`69957` 发送 Ctrl-C 停止，两会话均返回 `exit_code=1`。会话没有返回操作系统 PID，未按进程名终止其他进程。调研结束前以只读 `Get-CimInstance Win32_Process` 查询 `git.exe`、命令包含 `ls-remote` 与 `vtk` 的进程，成功退出且无匹配结果。

主 Agent 随后重新查询原源成功：`git ls-remote --symref origin HEAD refs/heads/master` 与同命令的官方 GitHub 镜像结果均为默认 `master`、完整目标 SHA `4b0325a...`，返回码 0。本轮查询记录保存在 `validation/agent/reports/2026-10-11/upstream/remote-refs.json`。早期访问失败与后续成功是两次不同访问的事实，不能据早期失败认定原源目前仍不可用。来源更新由主 Agent 维护，镜像读取没有修改 `.gitmodules`。

## 2. 完整提交范围及浅历史边界

完整范围为 `23f0a095621e91bbdbeace8451e22b950c8e5f46..4b0325a981d1f5cfad9d4da4909a8230881b2bf4`，含 **1775 个唯一提交**（包括合并提交及已进入主干的 release 回灌）。完整清单见 [upstream-20261011-vtk-commits.tsv](upstream-20261011-vtk-commits.tsv)。

清单来自[官方镜像 compare API](https://api.github.com/repos/Kitware/VTK/compare/23f0a095621e91bbdbeace8451e22b950c8e5f46...4b0325a981d1f5cfad9d4da4909a8230881b2bf4?per_page=100&page=1)，逐页读取 `per_page=100&page=1..18`；前 17 页各 100 项，第 18 页 75 项。每页返回 `ahead_by=1775`、`total_commits=1775`。清单含序号、完整 commit SHA、全部 parent SHA、committer UTC 时间和首行标题；末项等于目标 SHA，基线 SHA 不在清单中。顺序保留 API 返回顺序；标题中 tab 替换为空格。

TSV 的 Git blob 为 UTF-8 无 BOM、LF，含表头共 1776 行，SHA-256：
`2ad943d8ed1d94346fdbb2557d84a339adadd7f29f8b40d0ad4520fd483970e4`。

Windows 工作树可能按现有 Git 设置将 TSV 检出为 CRLF；上述摘要针对 Git 中的 LF 内容。核验工作树副本时先统一 CRLF 为 LF，或直接读取 Git blob，不把换行转换误判为提交清单内容变化。本研究不修改 Git 换行配置。

该数目直接由旧基线到新目标的完整 compare 分页核验，未以两个区段数目相加推定。主 Agent 用 `--shallow-since=2026-08-13` 获取的本地对象中，`git rev-list --count old..origin/master` 可见 1041 项，并报告基线祖先检查成功；1041 是该浅历史可见范围。完整清单第一项 `80ec566a572370568fee188949c9e691fde98d3d` 的 committer 时间为 2026-06-24：主干相对 release 基线的独有祖先可以早于基线发布日期，所以按日期截断不能取代完整祖先范围。范围成员身份以完整清单为准。

完整清单用于逐提交回查与主题筛选，不表示已经运行或逐行审计 1775 项实现。具体适用结论基于以下固定补丁、端点文件内容与 QC 现有源码/验证脚本；超出这些入口的变化没有被视为产品收益。GitHub compare 的文件列表存在返回数量上限，因此原有参考文件另行逐端点核对。

## 3. 原有十个参考文件的端点核对

通过官方镜像 `fetch_file` 分别读取基线与固定目标下的下列文件，比较 Git blob SHA；相同 blob 表示文件内容相同。不能用“日期之后没有 path log”替代这一核对，因为范围中存在早日期的主干祖先。

| 路径，相对 submodules/VTK | 基线 blob | 目标 blob | 结果 |
| --- | --- | --- | --- |
| `IO/Chemistry/vtkGaussianCubeReader.h` | `d88d8c43d7297b64ce792def8f2473befbf91477` | `d88d8c43d7297b64ce792def8f2473befbf91477` | 相同 |
| `IO/Chemistry/vtkGaussianCubeReader.cxx` | `963d56a97d2e8ad25a8a5af00d080d537c8aad44` | `963d56a97d2e8ad25a8a5af00d080d537c8aad44` | 相同 |
| `Common/DataModel/vtkImageData.h` | `bbc8acc1171160a6989fa0d885c9fc44fe75f18b` | `bbc8acc1171160a6989fa0d885c9fc44fe75f18b` | 相同 |
| `Common/DataModel/vtkImageData.cxx` | `7d56b4f0a78bfc140ac8c2b07dd5e7b6c7a3d769` | `7d56b4f0a78bfc140ac8c2b07dd5e7b6c7a3d769` | 相同 |
| `Filters/Core/vtkProbeFilter.h` | `7fed87e6eed0a302a55e143970552ef95ce21849` | `7fed87e6eed0a302a55e143970552ef95ce21849` | 相同 |
| `Filters/Core/vtkProbeFilter.cxx` | `077caab77de689d2b99dcc028a1a625af39e9982` | `077caab77de689d2b99dcc028a1a625af39e9982` | 相同 |
| `Filters/Core/vtkFlyingEdges3D.h` | `be899baaf40df111c1266956c7e804765dbf05ff` | `be899baaf40df111c1266956c7e804765dbf05ff` | 相同 |
| `Filters/Core/vtkFlyingEdges3D.cxx` | `860aabb43334641f96e126b4d0595b7c6f14cb79` | `30dd07c5e24dec5c74cd451bdd3c581961368727` | 不同，见下文 |
| `IO/XML/vtkXMLImageDataWriter.h` | `e88a996ee683de1a5c6b87a3aa40a1a9250eb082` | `4732a7edee3f255cdcd6d629a7f44be8deaf5b4c` | 不同，见下文 |
| `IO/XML/vtkXMLImageDataWriter.cxx` | `4e3b02a66663ec6c3070eb06dcf37252fd64c63b` | `4e3b02a66663ec6c3070eb06dcf37252fd64c63b` | 相同 |

两处变化的具体内容：

- [8d479138a8fcf2d8cda02e480cd3981a2dda96e1](https://github.com/Kitware/VTK/commit/8d479138a8fcf2d8cda02e480cd3981a2dda96e1)，`Filters/Core/vtkFlyingEdges3D.cxx`：移除设置后未使用的 `rowPtr`、`slicePtr` 及递增操作，保留原 `InterpolateCellData` 调用和遍历边界。该增量为编译警告清理，未形成 QC 提面算法替换的依据。
- [cb19899b3403b5593afae0b309652e490d82d96e](https://github.com/Kitware/VTK/commit/cb19899b3403b5593afae0b309652e490d82d96e)，`IO/XML/vtkXMLImageDataWriter.h`：引入 `vtkWrappingHints.h` 并为类增加 `VTK_MARSHALAUTO`，支持 VTK 序列化/反序列化包装；writer 实现文件未变。QC 当前没有 VTI 导出或 VTK 对象包装需求。

其余八个文件内容相同。既有 Cube reader 合同评估、Probe Input/Source 与有效点掩码、ImageData 仿射模型的观察仍适用于这些文件。此结论仅覆盖表中十个文件，不扩展到完整模块、依赖或测试。

## 4. 本轮采用的新增回归依据

### 4.1 过滤后的几何与属性逐点身份

主干新增修复 [46ad8a4a52d9142db3ff440bdb962ec81bca403b](https://github.com/Kitware/VTK/commit/46ad8a4a52d9142db3ff440bdb962ec81bca403b)，`Filters/Core/vtkMaskPoints.cxx`：均匀表面/体积随机采样的坐标来自 `randPtId`，属性原先却按循环的 `ptId` 复制；改为 `CopyData(pd, randPtId, id)`。错误会产生“位置正确、点属性来自另一源点”的结果。

配套新增测试 [2649dfa5d40b45adc87da656b8e1b1d18f388d92](https://github.com/Kitware/VTK/commit/2649dfa5d40b45adc87da656b8e1b1d18f388d92)，`Filters/Core/Testing/Cxx/TestMaskPoints.cxx`：给输入点添加源 PointId，每个输出点以该 ID 回查源位置并比较，覆盖所有随机模式。以上两 SHA 均在完整 1775 清单内。release cherry-pick `e6a30803e7589130050ccc9f82802d2a5a9b3c90` 与测试 `9a64d942c2ed52e4302102b9d6630e36fb76b386` 也在范围内，是同一修复/测试的回灌身份，不计为两种独立能力。

QC 已具备：

- [views.py](../../qcblender/blender/views.py)的 `atom_view` 创建 `qc_atom_id`、`qc_atomic_number` 及电荷属性；源身份不依赖 Blender 求值网格的顶点序号。
- [verify_node_helpers.py](../../tools/verify_node_helpers.py)已有实际 Geometry Nodes 筛选，验证数量、属性类型与 `qc_atom_id` 集合。
- [verify_audit_p1_association.py](../../tools/verify_audit_p1_association.py)已有损坏源 ID 的拒绝及无突变验证；[verify_display_precision.py](../../tools/verify_display_precision.py)已有原子 ID 与精度检查。

明确缺口：上述节点筛选检查把 ID 排序后比较集合，没有逐个输出点以 ID 回查对应源位置、元素和电荷。ID 集合正确仍不能单独排除属性与坐标错配。

本轮采用：在真实 Geometry Nodes 求值上，使用非对称坐标、不同元素和不同电荷，针对非连续/交叉筛选逐点核对 `qc_atom_id ↔ source position ↔ atomic_number ↔ charge`；同时保留空选择与属性缺失边界。区分源原子点与实现后的球/键表面：实现几何允许一原子对应多个顶点，不应要求其顶点位置等于核位置，也不能把求值顶点编号当源原子编号。先补回归，只有实际失败才修产品。

验收证据来自真实节点输出及保存工程的回读；合成测试输入只证明工程属性传播，不代替科学数值或独立人工接受。SOP 在现有源编号/选择操作附近解释源原子身份与求值几何，不要求用户填写技术摘要。

### 4.2 有效域、物理零与显示颜色

主干新增修复 [356bd2e11519d367553eff14bfc2185e99a5b3b6](https://github.com/Kitware/VTK/commit/356bd2e11519d367553eff14bfc2185e99a5b3b6)，`Common/Core/vtkLookupTable.cxx`：泛型标量快路径对非整数类型先检查 NaN，返回 NaN 色索引，避免 NaN 转整数。其 `Common/Core/Testing/Cxx/TestLookupTable.cxx` 同时覆盖 AOS double 与 SOA fallback 路径。原始主干 SHA 及 release cherry-pick `a44b758449d5682338d9090781df2632b0eed56c` 均在完整范围内。

这条修复提示“有效性在不同求值路径中保持一致”的验收方法。QC 科学数据合同拒绝非有限数组，通过布尔 mask 表示无效域，不以 NaN 色表替换合同。

| QC 已有入口 | 现有检查 | 本轮处理 |
| --- | --- | --- |
| [data.py](../../qcblender/data.py)、[field_ranges.py](../../qcblender/field_ranges.py)、[test_science_field_ranges.py](../../tests/test_science_field_ranges.py) | 数组有限性、有效范围、有效 NaN 拒绝 | 复用相关检查 |
| [verify_vmd_scalar_edges.py](../../tools/verify_vmd_scalar_edges.py) | 实际 GN 输出区分物理零、mask 无效、网格外；验证表面/切片三点映射、钳制和科学数组不变 | 保留原断言；按批准色带功能补对应显示路径 |
| [probe_scalar_views.py](../../tools/probe_scalar_views.py) | 斜轴线性场、物体变换后采样误差及完全域外切片 mask | 作为已有能力定位，需适用运行环境时复用 |
| [verify_charts.py](../../tools/verify_charts.py) | 等值线无效角点不参与、鞍点、常量场、取消 | 不重复实现同类算法 |
| [test_science_profile.py](../../tests/test_science_profile.py)、[verify_line_profile.py](../../tools/verify_line_profile.py)、[test_science_data_export.py](../../tests/test_science_data_export.py) | 斜轴剖面、内部无效间隔、域外、CSV 无效值留空、来源与保存重开 | 已有断言复跑；本轮需要时与新增显示路径串联 |
| [scalars.py](../../qcblender/blender/scalars.py)、[verify_mn_legend.py](../../tools/verify_mn_legend.py) | 材质缺失色分支；图例布局、数值范围与同材质渲染 | 增补缺失色与色带/反转、图例、导出之间的可观察一致性 |

必要补充收敛为：在同一明确合成场中，物理零、内部 mask 孔洞、网格外三种位置经过实际显示后保留区别；色带切换/反转后无效域仍按既有缺失语义显示，有效值与范围和图例对应，剖面/CSV 中无效值仍留空。现有脚本已测 GN 的值/mask 和 CSV，新增验证应补实际材质颜色及同轮操作联系，不把旧覆盖重新包装为新增功能。

验收需保存实际求值属性、颜色或渲染读数、图例对应及 CSV/metadata 证据，比较科学数组摘要保持不变。独立 GUI 操作、保存冷重开和最终结果由主 Agent 在集成候选上执行，本报告不把脚本存在记为本轮 Passed。

## 5. 其他增量的适用性与暂缓边界

| 类别与固定依据 | QC 适用性 | 本轮决定 |
| --- | --- | --- |
| [cadd777359f9b4bfb1924aa908bcd0ccd8f22b46](https://github.com/Kitware/VTK/commit/cadd777359f9b4bfb1924aa908bcd0ccd8f22b46)，负输入对数色表 NaN 传播；[c44c38a63b200ee9cc402c01a02b1664540afc91](https://github.com/Kitware/VTK/commit/c44c38a63b200ee9cc402c01a02b1664540afc91)，域外/NaN 对数映射测试 | QC 当前是有中心值的分段线性色映射，没有 log 模式 | 不新增对数映射；有限值与有效域回归沿用上节 |
| [6d020a2646280bf843a1ba445c403882d2f557eb](https://github.com/Kitware/VTK/commit/6d020a2646280bf843a1ba445c403882d2f557eb)，`IO/HDF/vtkHDFReader.cxx` 缓存更新前擦除同 key，避免 `emplace` 保留旧数组 | QC `science_identity.py` 缓存 key 已含数据、网格、参数、科学实现、Blender 身份；`worker.py` 校验数据/VDB并原子替换索引 | 未发现同型 QC 缺陷；不改缓存设计 |
| 五组旧参考文件，增量见第 3 节 | Cube reader 合同、Input/Source 与有效掩码已经审查/吸收；两处变更分别为警告清理和 VTK 包装声明 | 更新来源身份，保留 QC 自有 Cube、OpenVDB/GN 及源语义 |
| VTK 渲染窗口、WebGPU/OpenGL、MPI、DICOM、GLTF/OBJ、Python VTK 包装、第三方库等提交主题 | 不位于 QC 当前运行路径；该结论来自架构与依赖边界，不表示每项实现都已行为验收 | 记录完整范围，不转为 QC 产品任务或依赖更新 |
| 原 `vtkProbeFilter` 按批次准备采样状态的设计；QC `sampling.py` 当前逐点求逆，`profile.py/contours.py` 逐点采样 | 可作为未来测量后的性能候选；属于旧参考尚未采用的机会 | 本轮不实施批量采样，不把它算作新增上游更新 |
| FlyingEdges 后端替换、VTI/VTKHDF 导出 | 需要独立性能、坐标/顺序/单位/有效域合同与真实互操作需求 | 不进入本轮已有功能改进 |

既有 [ADR 0001](../adr/0001-self-contained-extension.md)保持有效。上述做法参考上游缺陷模式及测试方法，使用 QC 现有数据结构和 Blender 原生能力独立实现。若后续直接复制 VTK 源码，应逐文件核对版权与实际模块许可；Filters/Core 的 Sandia-USGov 附加声明仍按既有[源码借鉴记录](source-adoption.md)审查，本轮没有复制 VTK 产品代码。

## 6. 文件归属与后续实施验收

本研究仅拥有本 Markdown 与提交清单，不修改子模块、产品、SOP 或最终证据索引。主 Agent 维护子模块 gitlink、共享界面、许可证清单与证据归档。身份/有效域任务可复用上述验证脚本并按实际缺口增补；色带任务维护材质和图例变化，两任务交接现有材质属性、有效 mask、源原子身份断言，避免各自改写插值或源身份合同。

本记录是研究阶段结论。已批准的集成、GUI、安装、冷重开及人工教程变更由对应任务追加证据；此处未完成项不随子模块 SHA 更新自动转为通过。

| 检查 | 状态 | 证据与限制 |
| --- | --- | --- |
| 最近实际参考 SHA 与主仓历史 | Passed | 现存研究、主仓 gitlink 与日志精确核对 |
| 官方原源/镜像目标一致 | Passed | 主 Agent 本轮原源与镜像 `ls-remote` 返回码均为 0、完整 SHA 相同；本报告已读记录 |
| 完整提交范围 | Passed | compare 18 页，1775 唯一 SHA，末项等于目标，TSV 摘要如上 |
| 原参考十文件端点与两处补丁 | Passed | 基线/目标 blob 核对，固定范围内补丁检查 |
| 新增身份与有效域提交成员身份 | Passed | 原始主干与 release 回灌 SHA 均在清单中，具体补丁和测试已读 |
| QC 已有覆盖与必要缺口 | Passed | 上述源码/验证脚本静态核对；本轮未执行 Blender |
| 身份/有效域新增回归及产品修复 | Not Run | 属于后续实施与集成任务；当前未证实 QC 存在对应产品缺陷 |
| VTK 构建、运行及完整模块行为验收 | Not Run | 本轮源码参考，不安装或构建 VTK |
| GUI、安装包、保存冷重开及独立人工/科研接受 | Not Run | 由集成流程分别记录，不由来源调研代替 |
