# QCBlender 完成情况、缺陷与参考实现比较

调研日期：2026-10-03。固定产品基线：`96f9c7ea0c41c63f8b689a766ffafeb14aa3bb48`，版本`0.0.1`，Windows x64 / Blender 5.1.1 / CPython 3.13.9 / NumPy 2.3.4。

**插件已形成覆盖主要量子化学可视化工作流的本地技术候选，但还不能称为完成发布。** 本轮82项科学测试通过，相关单测与候选安装、XYZ/CSV、工程冷重开等专项通过；另外复现了四类产品缺陷，其中动态构型关联与共享mesh切步会造成画面构型和科学身份不一致，应优先修复。独立使用者验收、科研签署和跨软件实际运行对照仍为Not Run。

现有Dataset、独立科学计算、Geometry Nodes/OpenVDB与自包含工程的制作思路有明确依据。参考项目带来的主要增量是固定视觉回归、显示性能测量、批量出图、多来源比较和体场交换；多数基础交互与外部结果导入能力已经具备，不应重新作为待开发功能。

本报告仅调研、复现和提出修复/功能方向，没有实施产品修复、修改依赖或发布。仓库相对路径均从固定基线的仓库根解析；`submodules/...`一律指主检出`D:/workspace/QCBlender/submodules/...`的下述固定版本，不指未检出子模块的研究工作树。验证制品的最终入口为主仓`outputs/evidence/2026-10-03/plugin-audit/`；原始命令收据保留执行时`outputs/runs/plugin-audit/1/`路径，不改写原报告身份。

## 1. 完成情况与本轮验证

### 1.1 能力矩阵

“已实现”表示当前代码有可达路径；“本轮Passed”只覆盖表列实际检查。历史C01–C13/N01–N18完整Agent技术验收保留原候选身份，不视作本轮重新点击全部教程。独立人工认可与发布是另外的验收门槛，不按`.scratch`中resolved比例计算产品完成率。

| 能力 | 当前实现 | 本轮及历史验证 | 主要边界 |
| --- | --- | --- | --- |
| 输入 | IOData适配FCHK；cclib和自有事件适配Gaussian Log；多数据/斜轴Cube；标准单帧及同原子顺序多帧XYZ | 本轮科学回归、实际worker导入、XYZ严格边界及来源浏览Passed；Gaussian首段SCF前失败再拼接任务的边界另复现缺陷 | 后缀不证明量名、单位或收敛；支持范围见[VALIDATION第27–35行](../VALIDATION.md) |
| 求值 | 范围内实值、非周期、全电子HF/DFT的MO、总/Alpha/Beta/自旋密度、完整ESP | 本轮82科学测试Passed，0失败/错误/跳过；MO、密度、ESP与独立参考误差保持约4.85e-9、8.44e-7 electron/bohr³、4.61e-6 hartree/e | 参考只证明所测样本；完整网格收敛、远场及性能实验本轮Not Run；[VALIDATION:31–49](../VALIDATION.md) |
| 外部分析 | IGMH/IRI配对场、ESP极值/面积、NBO/E(2)、AIM、Mayer、ETS-NOCV表及pair Cube读取、来源与筛选 | 本轮相应解析/身份、七类导出和C04/C07–C13来源重建检查Passed；历史完整案例/渲染保留；NOCV冲突字段遗漏另复现缺陷 | 运行时不执行这些外部分析算法；新二维结果使用记录与CSV；[VALIDATION:41–43](../VALIDATION.md) |
| 轨迹 | Gaussian优化逐步构型/能量/收敛/原文；有序IRC FCHK、逐步Mayer；XYZ离散切帧 | 本轮XYZ逐帧身份/连接/测量/复制、IRC/Mayer导出Passed；动态关联及共享mesh切步另复现缺陷 | XYZ帧序不代表物理时间或IRC；不宣称任意IRC日志和扫描/QST路径解析；[优化边界:9–16](../OPTIMIZATION_TRAJECTORY.md) |
| 显示 | 原子/键、双相场、双场着色、切片/轮廓、雾、振动、局部选择/测量标注、显示层和九公共资产 | 本轮安装检查的实际场求值/阈值/相位/渲染及XYZ显示Passed；Quality3、201切片和0.2Å入口的历史当前候选证据已核摘要 | 本轮未重跑全部显示入口；显示细分不代表科学收敛；[VALIDATION:12–17](../VALIDATION.md) |
| 导出 | IR、optimization、IRC、Mayer、profile、paired、ESP_AREA的CSV与metadata | 本轮真实worker七类全量/筛选、539448有效paired体素、无效剖面留空、取消无遗留和记录对象检查Passed | 新建二维图已移除；旧图对象保留；[导出任务:13–15](../../.scratch/display-xyz-export/issues/03-data-export.md) |
| 保存与恢复 | 自包含`.blend + .qcdata`、原地/移动冷重开、缓存及重定位 | 本轮安装归档与新XYZ/导出综合工程原地、中文移动后新进程冷重开Passed；快照、metadata和CSV摘要一致 | 此专项不等于所有历史工程重新验收；旧权限/占用对象仍保留；[ARTIFACTS:41–47](../ARTIFACTS.md) |
| 交付 | 本地候选ZIP、11锁定wheels、离线运行、SOP和公开v2样本 | 候选及历史42报告、附加样本资料的摘要核验Passed；本轮安装副本71个Python文件与固定源码一致 | 独立用户/科研签署与发布未完成；P02单独取得；[交付入口:9–18](../ARTIFACTS.md) |

### 1.2 身份与执行证据

当前候选源码为`9d3ff61d2e32c47357fe624cf93052bfed6dd041`；它与调研基线的`qcblender`产品树同为`58108f2c64d358ada1d5800be7e24f5cc45b7a10`。ZIP为50,635,717字节，SHA-256为`362b87d3d1f41ec949da8597a47b248e7ef74ca574d96454d1dda31100556ce9`。候选、qualification、evidence-index与42份原报告共45文件，以及样本清单/公开包/文档检查报告3文件均匹配索引；HEAD的71个源码Git blob也全部匹配。[逐项核验](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json)

| 本轮检查 | 状态 | 实际执行范围与证据 |
| --- | --- | --- |
| 科学回归 | Passed | 82项，0失败/错误/跳过；[science.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/science.json)、[命令收据](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/science.json) |
| 相关单测 | Passed | 共31项：30通过，1项POSIX大小写专用在Windows跳过；copy 9、binding-paths 5、fog 5、legend 2、local-inputs 1、cleanup 9。原日志和收据位于[logs](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/) |
| 同候选安装与运行 | Passed | 离线安装、worker导入/求值、取消、生命周期、重复场缓存、阈值/正负相、实际渲染及归档；[extension.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/install/extension.json)、[命令](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/install.json) |
| XYZ及CSV综合检查 | Passed | 加载同批安装生成的`mo8.blend`后，帧身份/测量/复制、逐帧推断连接、七类导出/取消检查全部通过；[xyz-seeded-report.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/xyz-seeded-report.json)、[命令](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/xyz-seeded.json) |
| 原地与中文移动冷重开 | Passed | 两个新后台Blender进程，工程快照与导出文件摘要保持；[原地](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/xyz-inplace-reopen.json)、[中文移动](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/xyz-moved-reopen.json)及相应logs命令收据 |
| 来源浏览与连续导入状态 | Passed | 新预览重置、选定job、源文件变化拒绝、同名不同来源、损坏绑定、metadata-only及C04/C07–C13来源重建；[browser/checks.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/browser/checks.json)、[命令](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/browser.json) |
| 空factory场景直接运行XYZ专项 | Failed | 缺已有field，脚本175行StopIteration；失败保留，随后按历史正式命令补齐同批fixture才通过；这是验证入口前置问题，见第2.5节 |
| 独立缺陷复现 | 复现Passed，产品行为Failed | 逻辑层8案例含5对照和3缺陷；安装候选实际operator确认IRC/优化关联及共享mesh两类缺陷，XYZ共享mesh拒绝对照通过。见[logic/results.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logic/results.json)、[boundary-report.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json) |
| 全教程本轮重做、性能和跨软件运行 | Not Run | 本轮为科学回归与关键边界专项；没有重新执行每一项C/N渲染/GUI，也未实测参考软件速度、数值或视觉表现 |
| 独立使用者/科研签署、发布 | Not Run | [人工验收任务（第10行）](../../.scratch/v1-acceptance/issues/02-human-acceptance.md)、[发布机制任务（第4行）](../../.scratch/v1-acceptance/issues/03-release-mechanism.md)保持独立门槛 |

来源浏览的`new_dialog_resets_previous_preview`通过`ImportHelper.invoke`边界mock验证状态复位；metadata-only检查对`np.load`注入失败以确认不读取科学数组。这些是限定边界测试，不是实际文件对话框点击，也不是用替身替代科学解析。[工具边界:100、139、197](../../tools/verify_result_browser.py)

**GUI专项已完成：两项缺陷通过实际点击复现。** 在本批隔离 Blender 5.1.1（PID 60604）中，实际点击“关联选中数据源”和确认：IRC第3步仍被报告为与第1步匹配，显示偏差0而真实最大偏差为0.07072670385241508 Å。随后通过原生Alt+D创建共享mesh副本，取消位移并点击IRC Path的Next；副本显示Step 2，原对象仍显示Step 1，但原对象坐标改变0.03541665638593227 Å。场景准备及数值观察使用Python，以上按钮和快捷键由Agent Computer Use实际执行；不记作用户操作或独立人工验收。见[GUI数值与截图索引](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/gui/verification.json)。

本批工程已正常保存并退出；新后台进程PID 63368冷读确认所有GUI对象的坐标、mesh共享关系、步骤、关联记录和Dataset数组可恢复。保存回调后dirty标志为true，实际保存完整性以此次[冷读报告](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/gui/cold-reopen.json)核验，未把该标志自行改写。该工程有意保留缺陷状态，不能当作科学正确性通过的示例。

GUI前置环境的失败记录另行保留：首次沙箱GUI未暴露可操作窗口；首次桌面GUI因本任务临时数据目录的创建账户权限而拒绝读取。随后将本任务39个文件复制到新目录，逐文件SHA-256相同，原ACL和所有权均未改变，才完成上述实际点击。它们属于测试环境记录，不混入产品缺陷计数。

## 2. 四类产品缺陷及维护缺口

优先级按影响建议：P1为可能使科学身份与显示内容静默不一致，P2为特定输入边界下的解析或说明错误。以下缺陷均对应审计固定源码96f9c7e；后续AUDIT-02/03与AUDIT-01/04均已修复并验证，分别见[P2验证](../acceptance/audit-p2-baselines-validation.md)及[P1当前验证](../acceptance/audit-p1-validation.md)。复现报告中的`execution_status`或`verification_status=Passed`表示测试达成了预期复现，不能解释为缺陷产品行为通过。

### 2.1 AUDIT-01 / P1：动态构型关联使用基础Dataset，忽略当前步骤

- **触发与对照：** 将IRC或优化视图与其起始构型关联，起始步对照成功；把动态视图切到其他步，再执行“关联选中数据源”。使用真实P04 IRC和P02优化输入。
- **实测：** IRC切至第3步、优化切至第4步后，当前构型最大偏差分别约`0.070726704 Å`、`0.045609836 Å`，明显超过`0.001 Å`容差，operator仍返回FINISHED并记录`max_error_angstrom=0`、`geometry_matched`。IRC原关联在不重新关联而只切步时也仍保留。
- **原因与影响：** [blender/association.py:19–32](../../qcblender/blender/association.py)接受两个原子视图，加载基础Dataset调用`compare_sources`，没有读取对象当前构型。不同构型被标为匹配，会误导跨来源字段/属性与当前画面的关系；关联摘要无法表达后来改变的步骤。
- **修复方向与回归：** 关联应使用明确的当前科学构型身份；切步后使旧关联失效或验证其仍匹配。无法建立稳定身份时先拒绝动态视图关联。覆盖IRC/优化作为reference和moving两种角色、切步前后、关联后再切步及静态/刚体对照。
- **证据：** [逻辑对照与原始输入](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logic/README.md)、[安装候选原生operator的dynamic_association_irc/optimization](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json)。逻辑层IRC偏差`0.07072670392160446 Å`，原生mesh读回略有浮点差异，不混同为不同缺陷。

### 2.2 AUDIT-02 / P2：Gaussian首任务SCF前失败时遗漏拼接边界

- **触发与对照：** 同一文本拼接两个Gaussian运行，第一段在出现`SCF Done:`前失败，第二段正常结束；正常任务后拼正常任务可正确识别两段。
- **实测：** 缺陷输入仅得到一个failed job，沿用第一段HF route，同时把后段RB3LYP能量吞入这一job；第二段无法作为独立正常任务选择。输入为保留原文的最小合成解析边界，不声称完整计算日志的全量性质导入通过。
- **原因与影响：** [gaussian_log.py:25–32](../../qcblender/gaussian_log.py)仅在此前已有`SCF Done:`时把`Entering Gaussian System, Link 0=`认作新拼接任务；成功SCF不是运行边界成立的必要条件。导入预览使用同一`inspect_log`路径，用户可能丢失后段可用任务及正确方法上下文。
- **修复方向与回归：** 按明确运行开始/结束身份独立分段，保留失败/截断段和后续正常段各自route、状态与源行范围；覆盖第一段SCF前失败/截断、正常拼接、Link1以及开头banner处理。
- **证据：** [logic/results.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logic/results.json)中的`gaussian_normal_concatenation`、`gaussian_failed_before_scf`；[最小失败文本](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logic/failed-then-normal.log)。本项为真实解析器调用复现，没有使用文件/解析器mock。

### 2.3 AUDIT-03 / P2：ETS-NOCV重复记录冲突检查遗漏本征值和单轨道能量

- **触发与对照：** 同一spin/pair、pair energy与正负轨道编号相同，但第二行的正负eigenvalue或正负轨道能量改变。完全相同重复可合并；pair energy变化已正确拒绝。
- **实测：** 第二行从本征值`±0.12`改成`±0.45`，单轨道能量从`-3.1/0.6`改成`-3.2/0.7`时，解析器仍只保留第一行，没有报告冲突。
- **原因与影响：** [external_results.py:212–219](../../qcblender/external_results.py)去重只比较pair energy与两个轨道编号；遗漏的科学字段会影响记录浏览、筛选及对结果的解读。该表可经现有ETS-NOCV导入入口到达，后续没有另一层冲突检查。
- **修复方向与回归：** 对同一spin/pair比较完整规范化科学字段及单位/缺失状态，保留原文定位；相同记录仍可合并，任何有意义冲突都给出明确错误。分别改变正/负eigenvalue和正/负轨道能量，避免一个组合案例掩盖漏项。
- **证据：** [logic/results.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logic/results.json)中的三个nocv案例。输入为最小合成边界，复现范围是科学解析与真实可达调用链，不冒称实际点击该错误对话框。

### 2.4 AUDIT-04 / P1：共享mesh的IRC/优化副本切步会改变原对象几何

- **触发与对照：** 用Blender原生`bpy.ops.object.duplicate(linked=True)`建立共享mesh副本，只在副本切IRC/优化步骤。XYZ同类操作已有独立mesh守卫，正确拒绝并保持两对象不变。
- **实测：** IRC原对象仍报第1步，副本为第2步，但原对象坐标漂移约`0.035416656 Å`；科学构型与mesh的偏差约`0.035363352 Å`。优化原对象仍第1步，副本第4步，原对象坐标漂移约`0.045609836 Å`。
- **原因与影响：** [irc.py:64–82](../../qcblender/blender/irc.py)和[optimization.py:17–44](../../qcblender/blender/optimization.py)直接写共享mesh，只更新当前对象的步骤/缓存。Blender共享几何是预期机制，但插件各对象的科学步骤、标注和构型说明因此不再一致；P1依据是原视图在无提示情况下显示另一构型而继续保留旧科学身份，未发现源Dataset数组被改写。
- **修复方向与回归：** 在任何写入前检查`obj.data.users`，沿用[XYZ守卫:31–32](../../qcblender/blender/trajectory.py)拒绝共享mesh切步并给出解除链接方法；如选择复制mesh再操作，需要同时验证显示层、标注和绑定独立。覆盖IRC/优化、根对象及子对象入口、取消/Undo和保存冷读，保证拒绝时对象、mesh和缓存均不变。
- **证据：** [blender/boundary-report.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/blender/boundary-report.json)中的`shared_mesh_irc`、`shared_mesh_optimization`与`shared_mesh_xyz_control`；[实际脚本](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/blender_audit.py)、[执行收据](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/bugs.json)。

### 2.5 文档、测试入口和任务状态

- **现行导入文档过时：** [EXTERNAL_ANALYSIS_IMPORT.md:12–17](../EXTERNAL_ANALYSIS_IMPORT.md)仍承诺paired散点、ESP面积图、IRC能量曲线和Mayer曲线。当前[导出设计:13–15](../../.scratch/display-xyz-export/issues/03-data-export.md)与代码已使用记录对象和CSV，新建二维图被移除。该页是README指向的现行说明，应更新结果预期；无需为旧文案恢复已取消功能。
- **XYZ测试fixture前置缺说明：** 空factory场景直接运行脚本在[verify_xyz_export_blender.py:175](../../tools/verify_xyz_export_blender.py)找不到field而StopIteration，本轮[失败收据](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/logs/xyz.json)保留。历史正式命令与实际日志明确加载`install/mo8.blend`；该field由`verify_extension.py:93–107,159`生成保存。按此前置运行的本轮xyz-seeded及双冷读均Passed。[DEVELOPMENT:200](../DEVELOPMENT.md)只说明图例专项需要mo8，没有列XYZ专项入口；建议补命令和清晰前置错误。此失败不列产品Bug，详见[核验附录](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json)的`xyz_fixture_followup`。
- **子任务状态未同步：** 雾材质任务[仍claimed且GUI Not Run（第31行）](../../.scratch/tutorial-fog-materials/issues/01-material-slots.md)，主任务[已记录同修复候选GUI及三处冷读Passed（第31行）](../../.scratch/tutorial-cu/issues/02-gui.md)；MN参数spec[仍claimed（第4行）](../../.scratch/molecularnodes-parameters/spec.md)，四个issue均resolved且[技术完成已记录（第11行）](../../.scratch/molecularnodes-parameters/issues/04-integration.md)。应补当前Answer和证据指针，不删除历史状态。
- **真实未完成项：** 独立人工/科研签署、发布机制、参考软件实际对照，以及[旧f458/b48c权限与占用清理（第41行）](../ARTIFACTS.md)保持独立。旧任务关于“尚未配置remote”的日期性记录不能当作当前事实；本地现有origin，本轮没有push或发布。

## 3. 参考对象与比较基准

| 对象 | 本轮确认的版本 | 比较范围与限制 |
| --- | --- | --- |
| QCBlender | `96f9c7ea0c41c63f8b689a766ffafeb14aa3bb48`；manifest 版本 `0.0.1` | Windows x64；manifest 声明 `blender_version_min = 5.1.1`、`blender_version_max = 5.2.0`。本轮核对固定 main 代码、既有证据并运行第1节所列专项；源码及运行依赖的范围以 `qcblender/blender_manifest.toml:1–16`、`docs/adr/0001-self-contained-extension.md:1–9` 为准。 |
| MolecularNodes（MN） | `999b0b5e8f576c83b3dd854819303fe00c0507a0`；520.2.1 | `submodules/MolecularNodes/pyproject.toml:3–19,63–65` 要求 Python 3.13、Blender ≥5.2.0，并依赖 nodebpy 等库。节点设计可以参考，当前节点源码或资产不能视为 QC 的 Blender 5.1.1 可直接运行组件。 |
| GXNU-MolStudio（GXNU） | `6f3e859020e27d11511b512a7cc47564386b6216` | 阅读 Qt/OpenGL、worker、Cube 和批处理源码；未安装或运行。README 的功能表只用于定位，功能结论以固定树中的代码为依据。 |
| VTK | `23f0a095621e91bbdbeace8451e22b950c8e5f46`；v9.7.0 | 已确认 shallow 为 true、partial clone filter 为 `blob:none`。本地 sparse 仅包含 Cube reader、ImageData、ProbeFilter、FlyingEdges3D、XMLImageDataWriter 相关 `.h/.cxx`、四个模块声明、CMakeLists 与许可文件。未补取对象、编译、安装或运行；其余过滤器、writer 基类、测试和完整构建依赖不在本次可审查范围。 |
| Multiwfn | 用户已有 2026.9.1 手册、2026.9.20 Win64 源码与二进制包许可 | 核对输出格式和物理语义；不是 QC 的运行依赖。本轮实际读取 NOCV 能量状态、ESP PDB 单位切换、IGM/IGMH 设置等源码片段，未重新运行分析。 |
| VMD | 本地官方用户手册 1.9.3；开发版手册 1.9.4a48 单列 | 参数描述以对应手册版本为准；既有下载页快照不能证明 1.9.3 参数与其他发行版完全相同。本轮实际读取等值面参数及许可原文，未运行 VMD。 |
| GaussView | 本地官方 GaussView 6 手册 `submodules/GaussianView/gv6.pdf` | 本轮读取 PDF 物理页 79–86，涉及计算摘要、原文入口、多分子表和优化图；印刷页码比物理页序少 4。未运行 GUI，未据此推断实际性能。 |

当前参考 MN 与 QC 的版本差异是实质约束。例如 MN `submodules/MolecularNodes/molecularnodes/nodes/geometry/style_spheres.py:180–205` 使用 `ClosureZone` 和 `realize_to_point_domain`，且通过 nodebpy 构造节点；不能只替换几行 API 名称就宣称已兼容 5.1.1。后续实现应在 QC 支持的 Blender 中独立构造、检查并运行节点图。

## 4. 十个维度的横向比较

下表的“已实现”表示固定代码有对应路径；QCBlender实际运行与缺陷结果见第1、2节。参考项目只读取固定源码和一手资料，未安装或运行，不据设计结构推断实测性能、正确性或体验排名。

| 维度 | QCBlender 当前实现 | 固定参考实现或一手资料 | 取舍与剩余空间 |
| --- | --- | --- | --- |
| 1. 数据模型与科学身份 | `Dataset` 分离 metadata 与数组，校验原子、场形状、有效掩码，并以内容摘要保存和读取；场有量名、单位、来源、计算段和自旋身份。见 `qcblender/data.py:95–199`、`qcblender/evaluate.py:144–158`。 | MN 的 Molecule 以 MDAnalysis Universe/AtomGroup 和轨迹为中心，位置经 world scale 转换，见 `submodules/MolecularNodes/molecularnodes/entities/molecule/base.py:148–285`。VTK ImageData 保存 origin、spacing、direction 和索引到物理空间矩阵，见 `submodules/VTK/Common/DataModel/vtkImageData.h:289–344`。 | QC 的量化结果身份适合当前目标；MN 的残基/轨迹模型与 VTK 的几何/数组模型不自动包含这些科学语义。保留 QC 模型，按需增补互操作映射。 |
| 2. 科学计算与界面职责 | 科学求值不依赖 bpy；后台任务使用同一 Blender 的无界面进程，带任务身份、日志和取消。见 `qcblender/evaluate.py:35–158`、`qcblender/blender/jobs.py:13–63`。 | GXNU 的 `CubeWorker` 使用 QThread 调用 Multiwfn，再可调用 VMD/Tachyon 渲染，见 `submodules/GXNU-MolStudio/workers.py:15–136`；NOCV 使用持久外部会话，见 `submodules/GXNU-MolStudio/etsnocv/runner.py:245–282,285–410`。 | 可以借鉴队列和单项结果组织；不把外部分析面板数量当作 QC 应内置算法的数量。当前单扩展、自带必要 wheels 的边界仍成立。 |
| 3. 格点、Cube 与数值精度 | Cube 入口有多 dataset/源轨道编号、完整步向量、内存预算、float64 与数据数量检查。见 `qcblender/cube.py:11–83`。科学数组与 float32 VDB 显示缓存分开，见 `qcblender/worker.py:237–251`。 | GXNU `submodules/GXNU-MolStudio/marching_cubes.py:41–92` 的读取路径将格点装入 float32，按 `nx*ny*nz` 检查数量；VTK `submodules/VTK/IO/Chemistry/vtkGaussianCubeReader.cxx:175–233` 跳过轨道编号、分配单个 float32 标量，grid origin/spacing 为 0/1，另持有 Transform。 | 不建议替换当前 Cube reader。完整仿射坐标、多场源编号、科学单位及有效域是兼容性要求，不由后缀或“支持 Cube”四字证明。 |
| 4. 渲染与几何节点构造 | QC 用原生 Geometry Nodes、OpenVDB 和 Blender 材质；GridToMesh 有正负分支、有效性采样和 Adaptivity；原子球实例随后实现为网格。见 `qcblender/blender/views.py:284–364`、`qcblender/blender/assets.py:124–156`。 | MN `submodules/MolecularNodes/molecularnodes/nodes/geometry/style_spheres.py:145–205` 实现 Point/Instance/Mesh 分流；GXNU `submodules/GXNU-MolStudio/ovcanvas/_glwidget.py:1293,1669,5401` 使用自己的 QOpenGLWidget 与 depth peeling；VTK 提供算法组件而非此类完整科研侧栏。 | QC 继续使用 Blender 渲染和节点编辑。可评估保留实例/点表示，但是否提升速度需实测，且要核查裁剪、材料和采样对已实现网格的依赖。 |
| 5. 参数交互与更新边界 | QC 的 N-Panel、Object/Material Properties 已分工；视图控件读取节点唯一值，来源浏览使用缓存 metadata。见 `qcblender/blender/editor_ui.py:66–319`、`qcblender/blender/ui.py:403–438`、`qcblender/blender/source_browser.py:15–78`。 | VMD 1.9.3 在 rep 内区分 dataset、isovalue、绘制模式和 Step；拖阈值时可临时降低提面分辨率，见本地 `submodules/VMD/isosurface.html:73–105`。MN sphere 菜单与 Quality 分开。 | 参数面板和科学场/显示控制分离已吸收。QC 已有 Quality/Adaptivity，下一步应量测交互延迟，再决定是否新增明确的预览模式；不能把源场网格 spacing 当显示滑块。 |
| 6. 多视图、选择、测量和结果浏览 | QC 已有局部选择、氢显示、真实步测量标注、字段来源、结果过滤与优化步查看。见 `qcblender/blender/atom_selection.py:141–240`、`qcblender/blender/layers.py:60–117`、`qcblender/blender/annotations.py:108–146,232–362`、`qcblender/blender/result_browser.py:230–349`、`qcblender/blender/optimization.py:17–48`。 | MN 提供 selection/annotation 节点与实体属性；GaussView 6 的 Molecule Group Table 支持多分子排序、查找、来源列和复制，见 PDF 物理页 83–84/印刷页 79–80。GXNU 主窗口集成各分析面板，见 `submodules/GXNU-MolStudio/main_window.py:641`。 | 单来源详情和单视图参数不是缺口。多来源只读比较表与连续出图工作流仍可补，需避免跨方法/状态的自动科学合并。 |
| 7. 场采样、双场着色与外部语义 | QC 用 `qc_value/qc_valid` 采样，已有线剖面、切片、等值线及几何场/色场显式关联。见 `qcblender/blender/assets.py:55–69`、`qcblender/profile.py:27–88`、`qcblender/contours.py:12–69`、`qcblender/external_fields.py:12`。 | VTK `submodules/VTK/Filters/Core/vtkProbeFilter.h:8–22,80–95,138` 分离 Input 几何与 Source 场并输出有效掩码。Multiwfn `submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/ETS_NOCV.f90:812–873` 区分未计算能量与 Alpha/Beta；`submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/surfana.f90:1339–1343` 根据数值范围切换 ESP PDB 单位。 | Probe 角色和外部语义已经吸收。有效域不能当零值、NOCV 零能量不能自行判成未计算、ESP 单位不能从文件后缀推断；新增分析必须沿用这些边界。 |
| 8. 缓存、持久化和迁移 | QC 以 manifest/数组摘要校验内容，求值缓存键包含科学身份；提供 `.blend + .qcdata`、缓存重建、同一 Dataset 定位和归档。见 `qcblender/data.py:136–199`、`qcblender/worker.py:138–200`、`qcblender/project.py:12–48`、`qcblender/blender/project.py:38–100`。 | MN `submodules/MolecularNodes/molecularnodes/session.py:151–197,229` 使用 `.MNSession` pickle、实体注册和路径重映射；GXNU 工作路径会保存 Cube/渲染结果，现读入口不足以证明存在与 QC 等价的内容寻址科学工程。 | QC 的科学内容与显示缓存分离已有清晰收益；无需改成 Python 对象 pickle。不能把 MN 会话重载或 GXNU 输出文件等同为相同迁移合同。 |
| 9. 性能设计与已测边界 | QC 分块求值并缓存重复场；现有 `tools/benchmark_fields.py:24–66` 测 worker 时间、峰值内存和缓存命中，未测本次节点拖动/多视图交互。 | VTK `submodules/VTK/Filters/Core/vtkFlyingEdges3D.h:8–48` 描述四遍、预分配和 SMP，`submodules/VTK/Filters/Core/vtkFlyingEdges3D.cxx:1385–1392,1479–1480` 实际使用 `vtkSMPTools::For`；MN 以点/实例表示减少某些几何工作。 | 这里只能确认算法和结构。没有同机同数据基准，不能声称 VTK 或 MN 更快，也不应先替换当前提面后端；先分开测求值、加载、提面、着色、视口和最终渲染。 |
| 10. 测试与交付 | QC 有科学测试、安装/工程专项脚本、渲染像素断言和同轮冷重开一致性。见 `tools/verify_composable_render.py:18–44`、`tools/verify_fog.py:38–44`。 | MN `submodules/MolecularNodes/tests/test_render_images.py:31–44,54–108` 使用固定 CPU 渲染与提交的参考 PNG；`submodules/MolecularNodes/tests/test_session.py:131–207,270–292` 有会话恢复测试。GXNU 固定树的文件名搜索未找到测试入口；VTK 测试目录不在本地 sparse。 | QC 可补跨改动视觉基线，而不是从零增加视觉测试。GXNU/VTK 未运行及材料缺口不构成其没有测试或质量差的结论。独立人工验收也不能由这张代码比较表代替。 |

## 5. 已采用项与真正新增的边界

以下项目在当前源码已有入口，且仓库保存了对应阶段技术记录。本轮已重跑的范围仅按第1节声明，其余历史Passed仍保留原候选和执行批次。

| 参考来源 | 已采用的能力 | 当前代码与记录 |
| --- | --- | --- |
| GXNU | 隐藏/保留氢；IGMH/IRI 双场；ESP 极值/面积；NBO/E(2)；AIM；显式 IRC 步序与 Mayer；ETS-NOCV/NOCV 关联。 | `qcblender/blender/layers.py:76`、`qcblender/external_fields.py:12`、`qcblender/analysis_data.py:50,101,164`、`qcblender/nbo.py:25,87`、`qcblender/irc.py:39,81`、`qcblender/nocv.py:8`；汇总 `docs/research/visualization-adoption-plan.md:17–27`。这些是外部已有结果导入，不是新增 SCF 或 Multiwfn 内核。 |
| MN | 固定局部选择、源原子编号、随真实步更新的测量标注、图例排版和自动取景。 | `qcblender/blender/atom_selection.py:197,240`、`qcblender/blender/annotations.py:232,304,362`、`qcblender/blender/camera.py:60`；`docs/research/molecularnodes-parameters.md:19–23`、`docs/research/source-adoption.md:9`。 |
| VMD | 参数分组、显式着色场、有效格点范围、兼容视图复制参数。 | `qcblender/blender/editor_ui.py:243–319`、`qcblender/blender/scalars.py:309`、`qcblender/blender/color_ranges.py:89`、`qcblender/blender/copy_display.py:17–39`；`docs/research/vmd-parameters.md:23–32,48–51`。 |
| Multiwfn | 原生界面分工、点击探针/切片、等值线/剖面和外部记录过滤定位；CP 身份、ESP 单位、NOCV 未计算状态等语义。 | `qcblender/blender/interaction.py:241,298,418`、`qcblender/blender/result_browser.py:230–349`、`qcblender/external_results.py:51,129,171`；`docs/research/multiwfn-parameters.md:27–41`。 |
| VTK / GaussView | 几何与采样场分离、有效掩码、线剖面；计算摘要、来源原文和构型/结果联动。 | `qcblender/profile.py:34`、`qcblender/blender/source_browser.py:271`、`qcblender/blender/optimization.py:17`；`docs/research/source-adoption.md:10–11`。 |

旧 `docs/research/gxnu-molstudio-comparison.md:5` 明确采用 QC `1007375` 基准。该表中的旧“尚未验收”描述不能作为 `96f9c7e` 新需求。MN 的半径表还有一项真实数据复用：`qcblender/radii.py:1–3` 与 `THIRD_PARTY.md:28` 记录来源为历史 MN `5ad56c9cf33c4f82ceb3ca507d26d0cab6f7203c`，与本轮参考 checkout `999b0b5` 区别保存。

## 6. 五项有价值的改进候选

优先级是本轮建议，不是已获实施批准的任务。P1 表示在继续扩充功能前优先完善；P2 表示按常用工作流安排；P3 表示有明确交换需求再实施。成本为相对工程规模，不是工期估算。每项需要独立需求和验收，不自动新增依赖。

### F1. 固定视觉回归基线 — P1，工程质量能力

- **用户场景与收益**：更新插件后，原有 MO 相位、双场色图、图例或标注位置发生变化，即使“有可见红蓝像素”仍可能通过。固定场景和预期图可以发现跨改动的形状、配色、透明及排版退化。
- **已有与新增**：复用现有 signed-MO、双场、fog 和移动工程测试；新增小规模版本化参考 PNG、差异图和受控更新流程。`tools/verify_fog.py:38–44` 的保存前后比较不能替代固定预期图；MN 的参考是 `submodules/MolecularNodes/tests/test_render_images.py:31–44,54–108`。
- **成本与依赖**：中；需要稳定场景、CPU 渲染设置、图像差异报告及版本/字体/色彩管理记录。优先复用已随验证环境存在的图像读取能力，不把 MN 测试库加入插件运行依赖。
- **风险**：不同 Blender、采样器、字体或降噪器会造成漂移；容差过宽掩盖退化，自动重写预期图又会让失败失效。科学数值测试仍保留。
- **验收**：同一已知场景稳定重跑通过；刻意隐藏一侧相位、改变图例单位/位置或移除有效域遮罩时失败；失败保留差异图和候选身份；只有人工查看并认可的视觉变更可更新参考图。独立科研签署单列。

### F2. 显示性能基准与明确的预览质量 — P1，先测量再决定产品实现

- **用户场景与收益**：若高分辨率体场或多个视图下拖动阈值、切换局部选择出现明显延迟，目标是定位瓶颈，并在保留最终质量的前提下改善交互；当前没有本轮实测数据证明延迟幅度。
- **已有与新增**：已有 Quality、Adaptivity、worker 分块和缓存。新增视口操作基准；只有测量证明收益时，才在 Blender 5.1.1 中独立实现低成本预览或保留实例路径。参考 MN `submodules/MolecularNodes/molecularnodes/nodes/geometry/style_spheres.py:145–205` 与 VMD `submodules/VMD/isosurface.html:79–105`；VTK FlyingEdges 仅作为算法对照候选。
- **成本与依赖**：测量中、节点行为改造中至大；需要真实多原子/多体场样本、固定硬件/候选和时间/内存采集。保留当前 OpenVDB/GN；不以增加 VTK 或 MN 为默认前置。
- **风险**：去掉 RealizeInstances 可能影响按面材质、裁剪或后续节点；预览结果若被当作最终图会误导；改变源网格 spacing 将改变科学采样，不能混入显示质量设置。
- **验收**：分别记录冷/热加载、阈值拖动、选择更新、提面和最终渲染的耗时与峰值内存；数组与来源摘要不变；退出预览、取消、Undo 和冷重开均恢复设定的最终质量；原子编号、双相、双场、斜轴和有效域测试通过。先报告数据，再设定有依据的速度门槛。

### F3. 带来源记录的批量出图队列 — P2，产品工作流能力

- **用户场景与收益**：对一组明确的分子/轨道生成统一画幅和配色的论文插图，减少逐项求值、复制显示参数、取景、命名和渲染的重复操作。
- **已有与新增**：组合已有 worker、显示参数复制、自动取景和 Blender 渲染；新增用户可审查的队列与逐图结果记录。GXNU `submodules/GXNU-MolStudio/workers.py:64–136` 和 `submodules/GXNU-MolStudio/main.py:20–70` 提供工作流参照，不移植其外部程序调用。
- **成本与依赖**：大；需要任务生命周期、保存/恢复场景状态、碰撞安全的输出路径、逐项取消/重试和渲染配置验证。沿用单扩展，不增加 Multiwfn/VMD/Tachyon 运行依赖。
- **风险**：轨道、自旋、网格或场身份混用；预设覆盖用户灯光/相机；多任务竞争 Blender 场景；同名结果覆盖。未知量名/单位的数值参数不能跨视图自动套用。
- **验收**：至少覆盖闭壳层与开壳层、两种来源、多个轨道、成功/失败混合和中途取消；逐图记录 source SHA、轨道/自旋、阈值/单位、场网格和渲染配置；重复执行不静默覆盖；失败只影响对应任务；用户原场景可恢复。尚未测量前不声称比手动流程快多少。

### F4. 多来源只读结果比较表 — P2，产品浏览能力

- **用户场景与收益**：并排核对多个计算文件的方法、基组、状态、能量和来源，选择需要展示的结果，减少在来源详情窗口之间反复切换。
- **已有与新增**：复用已有计算段与来源 metadata；新增用户明确加入的比较行、按列排序/查找及复制/导出。GaussView 6 PDF 物理页 83–84/印刷页 79–80 是交互依据；当前 QC `qcblender/blender/source_browser.py:271` 仍是单绑定详情。
- **成本与依赖**：中；需要统一显示字段和缺失状态、稳定行身份、轻量缓存及既有导出流程接入。首版只读科学记录，面板重绘不重新解析原始文件或载入大数组。
- **风险**：把不同方法、计算段、电子态或能量定义直接相减；把缺失值显示为零；自动按文件名合并不同来源。
- **验收**：同一多段 Log 的两段和两个不同文件可同时显示，排序不改变来源身份；失败/未收敛/缺失结果原样表达；每行能定位原文行号和文件 SHA；导出与界面一致。首版不自动生成反应能、相对稳定性或跨方法排名。

### F5. 可回读的体场交换导出 — P3，按目标软件需求启动

- **用户场景与收益**：将插件内生成或导入后明确解释的场交给已有外部分析/绘图流程，减少手工解包 `.qcdata` 和猜测坐标、数组顺序或单位。
- **已有与新增**：当前 `qcblender/data_export.py:57–75` 列出 IR、优化、IRC、Mayer、剖面、成对场和 ESP 面积表导出；通用三维体场交换仍是独立能力。参考 VTK `submodules/VTK/Common/DataModel/vtkImageData.h:289–344` 与 `submodules/VTK/IO/XML/vtkXMLImageDataWriter.h:4–11`。
- **成本与依赖**：大；先由实际接收软件确定一种格式及版本，再复用可靠 writer。Cube 与 VTI 的取舍尚不是已决实现方案；任何新 writer 依赖需要另行授权。当前 sparse 缺少 writer 基类及完整往返测试，不能据单个头文件承诺互操作。
- **风险**：目标格式/读者不支持斜轴、多数组、有效域或元数据；Cube 无通用有效掩码表达，不能把无效点写零而不说明；点/单元数据顺序和单位缩放错误会形成貌似合理的图。
- **验收**：固定目标读者回读非立方斜轴、多字段、已知/未知量名及含无效域样本；逐点比较数值和物理坐标，保留单位、来源与有效性；格式不能表达的内容明确拒绝或通过已约定的伴随元数据保存，不静默丢弃；报告所支持的确切组合，不笼统宣称支持 VTK/Cube 全格式。

ORCA、Molden、`.mwfn`、周期体系、Hide Dust、DI/ESM 及新科学分析算法不因参考项目提供而自动进入这五项。它们需要真实输入、明确科学定义和单独需求；尤其 Hide Dust 可能隐藏真实的小连通区域，不能设为未经解释的科研图默认行为。

## 7. 许可证与复用方式

下表记录实际许可材料及工程处理边界，不以许可证名称代替逐文件审查。

| 来源 | 固定材料与事实 | 本轮采用及后续代码复用要求 |
| --- | --- | --- |
| QC / MN | QC manifest `qcblender/blender_manifest.toml:10`、MN `submodules/MolecularNodes/pyproject.toml:6` 均声明 GPL-3.0-or-later。QC `qcblender/radii.py:1–3` 已记录 MN 历史提交的数据表改编，`THIRD_PARTY.md:28` 已列归属。 | 当前节点、相机、选择和图像测试建议均为设计参考、独立实现。若复制其他 MN 源码或资产，逐文件核对版权、依赖、节点资产生成及再分发材料；既有半径表不能写成“从未复用 MN 内容”。本轮未拉取历史 `5ad56c9` 对象复验原表。 |
| GXNU | 根 `submodules/GXNU-MolStudio/LICENSE:1` 为 GPLv3 文本；`submodules/GXNU-MolStudio/README_zh.md:245–252` 声明 GPLv3-only 并引用 THIRD-PARTY-NOTICES；本轮 `git ls-files '*THIRD*'` 未列出该材料。 | 借鉴交互和批处理组织，不复制实现。若后续采用代码，需要先明确逐文件和第三方材料，评估组合后的分发许可及声明；不能直接沿用 QC 的 or-later 标记覆盖来源差异。 |
| VTK | 所读 reader/filter 文件头为 BSD-3-Clause；`submodules/VTK/Copyright.txt:9–21` 有保留版权/条款要求；`submodules/VTK/Filters/Core/vtk.module:12–21` 另声明 `LicenseRef-BSD-3-Clause-Sandia-USGov`，其 `submodules/VTK/Filters/Core/LICENSE:25–30` 有相应声明。 | 本轮仅参考数据流和算法设计。若引入代码或 wheel，需要审查完整实际依赖模块及其许可材料，保留归属并复验打包；不能以单文件 SPDX 推导整个 VTK 模块的分发清单。 |
| Multiwfn | `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/LICENSE.txt:1–7` 为作者自定义条款，涉及使用/分发、修改版出售和原始论文引用；不能简写成标准 GPL/BSD。 | 只核对输出语义。复制源代码、打包或自动调用应分别评估实际用法与许可，不能从“源码可读”推断任意复用条件。 |
| VMD | 本地 `submodules/VMD/LICENSE.html:329–378` 区分主程序和插件；`submodules/VMD/plugin-license.html:330–355` 表示多数插件用 UIUC Open Source License，同时保留具体插件/文件例外。 | 本轮使用手册中的参数行为。若采用 Molfile 或主程序源码，必须先定位实际文件适用条款；不把插件许可证推广到 VMD 主程序。 |
| GaussView | 本轮材料是官方用户手册，没有查得可复用程序源码许可证。 | 只将表格和结果浏览行为作产品参考，不复制程序、截图资产或手册正文进入产品。 |

## 8. 官方资料与摘要索引

本轮复算下面的本地 SHA-256。MN 与 VMD 两个 `sources.json` 内分别 11 项和 26 项文件全部逐项匹配。索引保存 URL、章节、获取时间和逐文件摘要；这证明本地材料身份，不证明其仍是在线最新版本。

| 本地资料 | 版本、来源与使用位置 | SHA-256 |
| --- | --- | --- |
| `submodules/MolecularNodes/reference-docs/sources.json` | 2026-09-28 保存的 [MN 官方文档](https://bradyajohnston.github.io/MolecularNodes/) 11 项；标记参考源码 999b0b5/520.2.1，但网页本身未绑定同一提交。实现判断以源码为准。 | `b9566796d518be3c01358f3ccd8ca7c893793401578b79afe81a51a65acd5b44` |
| `submodules/VMD/sources.json` | 2026-09-27 起保存的 [VMD 官方手册及源码页](https://www.ks.uiuc.edu/Research/vmd/current/ug/) 26 项；区分 1.9.3、1.9.4a48 和历史源码修订。 | `e809f09311e3c1bb90dbe3cb3d95238d991f2b60827fa7671c57708f76af17b9` |
| `submodules/Multiwfn/Multiwfn_manual_2026.9.1.pdf` | 用户已有手册；此前逐章索引见 `docs/research/multiwfn-parameters.md:3–23`；本轮未全文重读。作者入口为 [Multiwfn 官网](http://sobereva.com/multiwfn/)，本轮未重新下载或验证在线更新日期。 | `418871dc13a9c0860f4f5417935ca2848cb2251f42bce9b26e90a15717c6c9fb` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64.7z` | 固定源码包；本轮读解压目录 `submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/ETS_NOCV.f90:812–873`、`submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/surfana.f90:1339–1343`、`submodules/Multiwfn/Multiwfn_2026.9.20_src_Win64/visweak.f90:468–491`。 | `6cb3cd981f56178302bbcfb6936c577d5b56e338df690924d881835298e94eb` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64.7z` | 固定二进制包，仅核材料身份，未运行。 | `940b849d2be7baecf78dfeeecda2cef8ec86f38fae0f874f88144fc8ff5fae0a` |
| `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/LICENSE.txt` | 本轮实际读取作者条款。 | `0846f4144fd66d07a5b17e340863147a6797bbec871114d804ae620ffd7e8360` |
| `submodules/GaussianView/gv6.pdf` | [GaussView 6 官方手册](https://gaussian.com/wp-content/uploads/dl/gv6.pdf) 本地副本；本轮读取物理页 79–86，表格行为依据物理页 83–84/印刷页 79–80。 | `66ea3d5143de282a231e2b87473b71a6d0d63c3447e9a7c10b4497e9f954c847` |

三个 Git 子模块的官方来源分别由 `.gitmodules:1–11` 固定为 [MolecularNodes](https://github.com/BradyAJohnston/MolecularNodes)、[GXNU-MolStudio](https://cnb.cool/chem311/GXNU-MolStudio) 和 [VTK](https://gitlab.kitware.com/vtk/vtk.git)。本轮实际 HEAD 与第 3 节一致，三个子模块在本次只读核查时的 `git status --short` 均为空。Git 源码以 commit 定位；不把下载资料的日期或哈希与源码版本混用。


## 9. 科学范围、样本许可与后续顺序

### 9.1 当前不支持范围

以下是明确的范围边界，不因参考项目提供相应功能就直接认定为Bug：XYZ的extxyz/PBC/额外列/dummy中心；内置求值的h及以上、ECP、幽灵中心、广义/复轨道；相关方法密度、WFN/WFX、ORCA、`.mwfn`和周期体系；尚未完整解析的CASSCF/复合方法及仍为候选的B2PLYP目标规则；优化扫描、重启、QST2/QST3等。扩展这些范围需要真实输入、科学定义和单独需求。[当前边界（第29行）](../VALIDATION.md)

### 9.2 真实样本与再分发

| 样本 | 当前科学来源与用途 | 交付及许可边界 |
| --- | --- | --- |
| P01 | 自定义O₂，PySCF 2.13.1 UHF/STO-3G，中性三重态、16电子；MO与自旋/电子密度 | 包内FCHK/FCH；CC BY 4.0，署名QCBlender contributors |
| P02 | Gaussian16 A.03/NBO3.1真实水多计算段，RHF/STO-3G；优化4步，job2有3模式及NBO/E(2) | 包外单独取得；数据再分发许可未确认，不能套用cclib程序许可证；C02/C06前置 |
| P03 | 自定义水二聚体，PySCF RHF/6-31G(d)；Multiwfn真实IGMH/IRI、ESP及AIM结果 | 包内；CC BY 4.0；按manifest声明量名、单位和片段，不声称网格收敛 |
| P04 | 自定义H₂O₂，PySCF RHF/STO-3G加geomeTRIC原生TS/双向IRC；61接受帧中跨TS连续三点，真实SCF及同密度/重叠矩阵Mayer | 包内；CC BY 4.0；当前为真实IRC，不以旧构型或三点扫描替代 |
| P05 | 自定义CO/BH₃与整体几何，真实SCF及Multiwfn ETS-NOCV | 包内；CC BY 4.0；能量为整体KS矩阵重构的Multiwfn近似，不称F_TS方法 |
| P06 | 从P03/P04源FCHK提取的标准XYZ，Å、固定原子顺序 | 包内；CC BY 4.0；不携带FCHK能量、波函数或IRC语义 |

条件、来源和预期值见[SOURCES第159–183行](../v1-acceptance/SOURCES.md)。P01/P03/P05是自行定义的示意构型，没有声称优化结构；较早S01–S35输入仍各自遵守其来源和许可边界。P02下载失败、摘要不符或不具备使用权时，相应案例必须保持Not Run；原站定位与本地读取说明不授予再分发权限。

公开v2包为12,175,753字节，SHA-256 `b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`；本轮复核匹配。包只含P01/P03/P04/P05/P06及清单、LICENSE、NOTICE，不包含P02或程序。[样本交付索引](../acceptance/tutorial-sample-delivery.json)、[本轮核验](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/completion-evidence.json)

### 9.3 建议顺序与验收门槛

先修复AUDIT-01与AUDIT-04的科学构型/共享mesh边界，随后修复两个解析缺陷，并同步现行二维结果说明及测试入口前置。每项使用本轮正常对照和失败输入形成回归，验证拒绝时场景不变、Undo及冷重开后科学身份一致；修复候选需要重新记录包摘要，不能继承本轮旧包身份。

再建立F1视觉基线与F2性能基准，以观测结果决定是否修改节点表示或提面策略。F3批量出图和F4多来源比较按用户实际工作流选择；F5先明确接收软件与目标格式。新科学格式/算法及运行依赖不自动纳入本次建议。

独立使用者按确切新候选完成SOP与科研签署后，才进入已规定的发布机制任务。技术回归、原生operator调用、Agent实际GUI操作、跨软件运行对照与独立科研认可分别记录；本报告不替代任何一项缺失门槛。

## 10. 证据保全与交付状态

证据已迁入主仓[本批目录](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/README.md)，工程迁入`outputs/projects/plugin-audit/`。所有迁移保留原字节和内部相对层级，旧路径通过[preservation-map.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/preservation-map.json)解析。`xyz-seeded/integration.blend`及`gui/linked-observed.blend`在最终保留位置分别经新进程冷重开，Dataset、数组、体积文件和GUI缺陷状态核对[Passed](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/retained-project-checks.json)。

本次独立安装环境和已保全的原副本共6,036文件、500,234,681字节已删除；这是删除文件大小之和，不是全仓净节省。十个权限目录内74文件、207,636字节已由创建用户读取复制并核对摘要，原件继续保留，未修改ACL或所有权；因此[清理状态为Partial](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/cleanup-receipt.json)。所有本批Blender进程已正常退出。

产物统一由[ARTIFACTS](../ARTIFACTS.md)定位。研究报告已提交为`26fa9c9`并合入main。后续两项P2与基准实现、归档身份和当前候选由[ARTIFACTS](../ARTIFACTS.md)及[修复验证](../acceptance/audit-p2-baselines-validation.md)定位；原始审计证据保持原身份。最终摘要与链接检查见[final-verification.json](D:/workspace/QCBlender/outputs/evidence/2026-10-03/plugin-audit/final-verification.json)。
