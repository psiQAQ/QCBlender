# 产物查找入口

更新：2026-10-02。任务状态见 `.scratch/`，原始报告负责验证结论；本页路由现存文件、候选、工程、重建方法和阻塞，不改变历史 Passed 或独立人工签署。

## 目录与生命周期

| 位置 | 用途 |
| --- | --- |
| `outputs/evidence/<日期>/<任务>/` | 报告、成功与失败日志、生成脚本、来源、摘要、清理收据及被索引引用的必要截图 |
| `outputs/projects/<工程标识>/` | 用户 `.blend` 与完整 `.qcdata`，不按任务结束删除 |
| `outputs/candidates/current/` | 最新待验收 ZIP；替换前记录身份、资格和旧候选可用性 |
| `outputs/runs/<短任务名>/<短批次>/` | 临时工程、隔离配置及缓存，收尾保全后清理 |
| 共用环境及资料的现有路径 | `outputs/build-site`、`outputs/science`、`outputs/wheels`、构建源码及必要许可证；参考原件留在原资料目录 |

真实输入的唯一清单为 `tests/data/local-inputs.json`，来源见 [SOURCES](v1-acceptance/SOURCES.md)。没有确认用途的原件保留原位，具体路径见本批 `routes.json` 的 `unknown_inputs`；不把它们称为已迁移或已删除。

## 当前任务与候选

当前公开教程样本包位于`outputs/evidence/2026-10-02/tutorial-cu/final-samples/qcblender-public-tutorial-samples-v1.zip`，身份、27份科学输入不变与轨道编号回归见[样本交付索引](acceptance/tutorial-sample-delivery.json)。历史旧包及报告保留原身份；正文SOP使用新包摘要，尚未发布。

归档前保全位于`outputs/evidence/2026-10-02/tutorial-cu/archive-preparation/`：`inventory.jsonl.gz`记录8个教程工作树37,121份忽略文件、2,226,468,017字节；`summary.json`和`working-source-map.json`记录222项文本证据及另一个工作树2份未提交源码的原字节/基线/补丁保全。此批未删除任何文件，未知二进制与独立环境仍保留；清理依赖GUI验收与主分支合并，不将保全盘点视为清理完成。

当前技术候选为`outputs/candidates/current/tutorial-a67d4b3/qcblender-0.0.1.zip`（a67d4b3，SHA-256见[最终技术资格索引](acceptance/tutorial-final-qualification.json)）。同批报告/日志/命令/脚本位于`outputs/evidence/2026-10-02/tutorial-cu/final-qualification/`；保全工程为`outputs/projects/tutorial-cu-full/qualification-a67d4b3/install/mo8.blend + .qcdata`和`legend/evidence.blend + .qcdata`，逐文件映射见`project-path-map.json`。新候选自动化技术资格Passed；完整GUI仅剩显示层首次移除确认，02claimed、03pending，未合并/归档。历史候选保留各自原身份及报告，待最终验收后按维护策略处理；重建顺序见DEVELOPMENT与索引。

2026-10-02 三个公共资产：qc.isosurface.v3、qc.surface_style.v1、qc.volume_fog.v1独立菜单添加和六条核心接线GUI Passed；固定Socket接口、正负相、三样式独立边/顶点数、独立阈值与opacity属性MCP Passed，原对象/节点布局/绑定/66数组未变。48文件/3Dataset/两个内嵌库保全，PID14372新进程冷读全快照/点求值Passed，全部进程退出。12图紧接N04/N10步骤，登记67项；Eevee雾alpha通过但本例RGB偏暗，Cycles可见诊断分别记录，辅助准备不冒称GUI。02仍claimed、03pending，统一资格及合并归档待完成。

公共表面/雾证据：`outputs/evidence/2026-10-02/tutorial-cu/full/remaining-boundaries/public-surfaces/`；保全工程：`outputs/projects/tutorial-cu-full/cases/public-surfaces/N04-N10-public-surfaces.blend + .qcdata`。逐文件摘要与旧新映射见`preservation.json`/`project-path-map.json`；原始C13保留，实际菜单/连接图在SOP对应步骤。

2026-10-02 C08–C12：在deb9416/c736bb9五个串行唯一可见进程中，原生过滤/IRC步进/Mayer配对及撤销、重做、恢复MCP Passed；对象/节点/坐标/曲线/标注/绑定/全部数组与完整快照一致，原工程和原输入未变。保存副本迁入cases/undo/C08–C12并逐文件核对，五个新后台进程冷读完整快照与科学文件Passed，全部进程退出。64项GUI历史登记保持原身份，复用影响审阅单列Passed。02仍claimed，03pending；其余三个公共资产、统一资格和合并归档待完成。证据full/remaining-boundaries/undo/completion.json。

撤销重做批次：`outputs/evidence/2026-10-02/tutorial-cu/full/remaining-boundaries/undo/`；各案例保存工程位于`outputs/projects/tutorial-cu-full/cases/undo/C08–C12/`，逐文件旧新路径见每例`project-path-map.json`。保留成功日志、原生前后快照、命令和复用差异审阅；用户/独立科研签署Not Run。

2026-10-02：真实内部核区无效掩码的探针拒绝/9点剖面断线与CSV留空、洋红实渲染、84段等值线独立单元守卫Passed；配对Cube网格origin诊断偏移明确拒绝且不重采样。N18首次CU重建缓存/重新定位同Dataset Passed，缺科学数组与错误manifest经MCP拒绝且绑定不变；52源数组及56顶点/54面恢复一致。两个独立工程各55配套文件/3Dataset/108数组/1VDB保全并在新进程冷读与渲染像素一致；原历史证据和失败验证器诊断保留。7图紧接SOP步骤，操作登记64项，源deb9416/候选c736bb9完整身份见索引。全部Blender退出，重复冷图核对后清理。02仍claimed、03pending；其余三个公共资产、C08–C12撤销重做、统一资格与合并归档待完成。

内部掩码/配对网格/缓存与重新定位证据：`outputs/evidence/2026-10-02/tutorial-cu/full/remaining-boundaries/field-guards/`，内部洋红与等值线子批为`internal-display/`。必要工程分别保存在`outputs/projects/tutorial-cu-full/cases/field-guards/`和`cases/internal-mask-display/`；各自`project-path-map.json`逐文件核对旧新路径，`render-prune.json`定位保留图与已清理重复冷图。失败作业的原request/result/log、验证器失败诊断与原图均保留；小网格仅用于边界诊断。

2026-10-02 C01密度检查点：安装候选deb9416/c736bb9在原位置、中文移动和新归档解包副本串行冷读Passed；176文件/9Dataset/221数组/17引用/7体积源与源摘要一致，四密度关系与12次重渲染像素一致Passed。三个进程已退出，12份重复PNG核对后清理，四张已检查原图保留。证据full/remaining-boundaries/C01-density/cold-chain.json；原2eddb6a报告保持原身份。02仍claimed、03pending，内部无效mask/网格不匹配/其余资产与撤销恢复/统一资格和合并归档待完成。

密度证据与重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/remaining-boundaries/C01-density/`；移动工程位于`outputs/projects/tutorial-cu-full/中文移动/C01-density-checkpoint/`，解包工程位于`outputs/projects/tutorial-cu-full/unpacked/C01-density-checkpoint/`。原四张PNG位于`full/C01-density-cold/`，新批重复图已删除，清单见`render-prune.json`。

C13真实Pair1/Total导入GUI Passed；独立133950个Cube值/六原子/表绑定、10显示组合、两个真实异步错误拒绝及独立复制/原生撤销重做MCP Passed。48文件/3Dataset/66数组/1VDB/4引用保全，三处串行冷读和12次像素一致渲染Passed，全进程退出。11图紧接步骤，登记62项；BOHR常数/接口缩写/空材质测试诊断保留。C12可见启动自动缓存Passed另列；完整教程剩余边界、统一资格和合并归档待完成。

C13证据：`outputs/evidence/2026-10-02/tutorial-cu/full/C13/`；保全副本：`outputs/projects/tutorial-cu-full/`的C13目录；四张原渲染保留，12张重复冷渲染核对后清理。候选deb9416/c736bb9。

C12真实ETS-NOCV首次导入、记录1/2、Pair/Total/负本征值范围与正本征值排序GUI Passed；11打印行与全部字段、25筛选排序和3错误边界MCP Passed。40文件/2Dataset/60数组/2引用保全，三处串行后台冷读和3次像素一致渲染Passed，全部进程退出。表无渲染网格，效果图手动排版源说明明确标注；8图紧接步骤，登记61项。原测试断言和后台启动缓存时序Failed保留；完整教程、统一资格和合并归档仍待完成。

C12报告、脚本和原工程：`outputs/evidence/2026-10-02/tutorial-cu/full/C12/`；移动/解包：`outputs/projects/tutorial-cu-full/`对应C12目录。当前候选沿用源码deb9416，摘要c736bb9，逐批验证身份不继承。

C11原生Mayer导入自动曲线与1,3 Plot Pair通过；6对×3步18源值、两对8次步进/标注同步与非法/重复/缺步输入MCP Passed。deb9416以两行对象上下文override修复Properties嵌套poll缺陷，新候选c736bb9；13文件/2Dataset/9数组/6引用保全，三处串行冷读和9次像素一致渲染Passed，全进程退出。原导入Failed及临时渲染开关断言诊断保留；7图紧接步骤，登记57项。完整教程、统一资格与合并归档仍待完成。

当前C11证据、原工程和重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C11/fixed/`；修复前失败证据在其上一级。新候选：`outputs/candidates/current/tutorial-irc-mayer-context-deb9416/qcblender-0.0.1.zip`，构建/安装/专项证据：`outputs/evidence/2026-10-02/tutorial-irc-mayer-context/`。移动/解包工程在`outputs/projects/tutorial-cu-full/`对应C11目录；旧候选通过不继承给本候选。

C10真实三步H2O2导入、Next/Previous和IRC当前版本视图预期拒绝GUI Passed；四原子身份/坐标/FCHK能量、三种源编号测量/文字/锚点/引线及重复步号/端点不变MCP Passed。8文件/1Dataset/5数组/3引用、三处串行冷重开逐步重放与九次像素一致实渲染Passed，全进程退出；10图紧接教程步骤，登记55项。原子编号/快照类型断言诊断保留，重复冷渲染核对后清理。产品未改，完整教程/统一资格及合并归档仍待完成。

证据及重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C10/`；保留`C10-final.blend + .qcdata`和ZIP，作为无Mayer导入的C11检查点。移动/解包副本在`outputs/projects/tutorial-cu-full/`对应C10目录；沿用13401c6/cc4e7ac候选身份。

C09首次AIM导入、立即属性记录1/2、路径组1/2和数值范围GUI Passed；独立原文11CP/10路径408点/550属性、28筛选及7错误边界Passed。120文件/8Dataset/224数组/4体积/20引用保全与三处串行冷重开、九次像素一致实渲染Passed，全部进程退出。8界面截图和3效果图紧接步骤，登记52项。首次属性面板int/string键缺陷以13401c6最小修复，新候选cc4e7ac完整摘要见索引；原Failed与排版/脚本诊断保留，九份重复冷渲染核对后清理。完整教程/统一资格及合并归档仍待完成。

证据及重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C09/fixed/`，原失败及修复前工程在上一级C09；修复构建/安装/10项科学检查与大样本59CP/58路径专项在`outputs/evidence/2026-10-02/tutorial-aim-records/`。保留fixed中的`C09-final.blend + .qcdata`和ZIP，移动/解包副本在`outputs/projects/tutorial-cu-full/`对应C09目录；最新候选`outputs/candidates/current/tutorial-aim-records-13401c6/`。

C08 ESP：原生入口/确认、记录2、极值范围和两面积模式，以及35组MCP筛选/5错误输入核对Passed。证据、原始诊断、输入/候选摘要与重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C08/`；最终工程`C08-final.blend + .qcdata`及ZIP保留120文件、8Dataset/224数组/4体积/20引用。中文移动和解包工程在`outputs/projects/tutorial-cu-full/`对应C08目录。三个串行新进程和6次重渲染像素一致Passed，全部退出；8界面图和2效果图紧接步骤，登记48项。6份重复冷渲染删除7,746,576字节，原图/日志/摘要收据保留；初始构图和保存设置诊断保留，完整教程/统一资格待完成。

C07成对场：IGMH/IRI导入、散点范围/交换、错误原子配对拒绝和Edit菜单撤销重做GUI及独立MCP核对Passed；参数准备范围单列。证据、原始成功/失败日志与重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C07/`。保留`C07.blend + .qcdata`和ZIP（44文件、3Dataset/66数组、4体积），中文移动与解包副本在`outputs/projects/tutorial-cu-full/`对应C07目录；三个新串行进程与九次真实重渲染像素一致Passed，全部进程退出。11截图、3效果图紧接步骤，44操作登记；9份已核对重复冷渲染删除，原图和摘要收据保留。原失败构图和两项断言诊断原样保留；完整C/N与统一资格待验收。

C06 NBO/E(2)：Job2/block1原生out/log导入、行1/2与BD降序筛选、撤销及Edit菜单重做Passed；27筛选/排序组合由MCP独立核对。证据、成功/失败日志与重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C06/`；保留`C06-final.blend + .qcdata`及ZIP（38文件、3 Dataset/33数组），中文移动和解包副本位于`outputs/projects/tutorial-cu-full/`对应C06-final目录。三个新串行原生进程冷读及真实重渲染像素一致Passed，所有进程退出。9截图和1渲染紧接SOP步骤；快捷键重做失败观察单列、菜单复验Passed，未修改产品。完整C/N与统一资格待验收。

C01独立密度检查点：2eddb6a候选新原生进程冷读、175科学文件/9Dataset/221数组/17引用/7体积源、四密度关系及四图重渲染Passed，PID3392已退出。证据、PNG与重建脚本`outputs/evidence/2026-10-02/tutorial-cu/full/C01-density-cold/`；保留原`outputs/projects/tutorial-cu-full/unpacked/C01/C01-density.blend + .qcdata`，摘要未变。原保存批次92d498c与本批资格分开；该检查点移动/解包和最终统一资格仍Not Run。

C05/P02优化标注与当前版本：实际GUI创建新层、MCP独立四步测量/标注同步及临时副本移除Passed；合成退化边界单列。证据与重建脚本`outputs/evidence/2026-10-02/tutorial-cu/full/C05-followup/`，保留`C05-optimization-annotations.blend + .qcdata`和同条目ZIP（12文件、2Dataset/8数组、5视图/8标注）。原路径、中文移动和解包分别新进程冷读并重放四步Passed，原C02工程不变，全部进程退出。3张图紧接C05步骤，37操作登记；IRC、GUI移除点击、完整案例与统一资格仍分开待验收。

C05角度/二面角创建与朝向原生GUIPassed，独立参考112.770°/0.000°；三张1920×1080实渲染已按步骤展示。证据与重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C05-final/`；保留`C05-final.blend + .qcdata`及ZIP（24文件、1Dataset/50数组、6视图/52标注）。原路径、中文移动和解包三个新进程及9次像素一致重渲染Passed，完整变换链核对；失败诊断原样保留，全部进程退出。操作登记36项；剩余C05边界/随步、后续案例、统一资格与合并归档仍待完成。

C05公共原子选择、表示和裁剪资产已实际GUI添加并接线，身份/固定接口、三样式及平面/盒/交集独立参考Passed。17张原始截图紧接N01/N02/N09；辅助输入输出、材质和边界向量的MCP准备单独标注。证据与重建脚本：`outputs/evidence/2026-10-02/tutorial-cu/full/C05-public-atoms/`；保全`C05-public-atoms.blend + .qcdata`及同条目ZIP，24文件、1Dataset/50数组、6视图/48标注、2内嵌库。原路径/中文移动/解包三个新原生进程读回图/几何/数组完全一致，后两者外部节点库路径不存在；检查脚本长路径失败和修正版分别保留。全部进程退出，登记34项，完整C05成图、后续案例、统一资格与合并归档仍待完成。

C05对象属性选择/样式/半径、显示层复制与排序、相容原子显示参数传递补验Passed，使用同一2eddb6a候选。原生操作与MCP准备/数据核对分列，14张截图紧接SOP步骤；操作登记31项。报告和重建脚本位于 `outputs/evidence/2026-10-02/tutorial-cu/full/C05-completion/`，新工程 `C05-display-controls.blend + .qcdata` 共3文件、1 Dataset/50数组、5原子视图/40标注；原路径新原生进程读回控件、数组、标注和求值几何一致Passed，工程摘要未变。首个边界点击和保存后同一事件周期的dirty断言失败仅作为检查脚本诊断保留。PID41240与51472正常退出；完整C05成图/移动解包、公有节点添加、后续案例、统一资格和main合并归档仍Not Run。

C05原子层标注显隐修复候选为 `outputs/candidates/current/tutorial-atom-layer-2eddb6a/qcblender-0.0.1.zip`，固定源码 `2eddb6a`；构建安装、GUI视口/渲染切换、三个真实视图专项断言及新工程冷重开Passed。证据与重建脚本在 `outputs/evidence/2026-10-02/tutorial-cu/atom-layer/`，工程 `C05-layer-fixed.blend + .qcdata` 保全24文件、50科学数组及24标注。旧候选失败及旧工程/ZIP摘要保存在 `outputs/evidence/2026-10-01/tutorial-cu/full/C05/`，不覆盖历史结论。10张截图按C05对应步骤引用，操作登记27项；全部Blender进程已退出。完整C05/C-N、统一资格、main合并及归档仍Not Run，配置保留待继续验证。

C04公共节点N06/N07/N08新增资产、接线/参数调整及恢复Passed，同候选e26d22a；GUI操作与MCP接线/独立参考分列。工程 `outputs/projects/tutorial-cu-full/cases/C04/C04-public-nodes-packed.blend + .qcdata` 和同名ZIP保全117文件、7 Dataset/222数组、17引用及4体积；两份关联节点库已原生打包。原路径、中文移动和解包冷重开Passed，后两者外部节点库不存在仍能求值一致。证据/重建脚本和截图摘要见 `outputs/evidence/2026-10-01/tutorial-cu/full/C04/public-nodes/preservation.json`；移动映射在cold-moved/unpacked的process.json；16张图紧接SOP对应步骤，登记26项。四进程均正常退出。完整C04/C-N、统一资格和main合并/归档仍Not Run，未清理活跃候选配置。

C04源关联/导出补验使用同一e26d22a候选：GUI关联按钮及0.001 Å容差确认Passed，源选择和独立数据核对由MCP完成；六类PNG、三个CSV、7 Dataset/222数组/15引用/4体积与117配套文件保全，原检查点摘要不变。证据/重建脚本见 `outputs/evidence/2026-10-01/tutorial-cu/full/C04/completion/preservation.json`；新工程为 `outputs/projects/tutorial-cu-full/cases/C04/C04-association-exports.blend + .qcdata`，同名ZIP117条目逐字节核对。原路径、中文移动及ZIP解包副本分别在唯一新可见进程完成MCP冷重开、三份CSV复导出及像素一致的渲染核对Passed；117文件、7 Dataset/222数组、15引用及4体积摘要一致，三个进程均正常退出。冷重开报告与重建脚本见同批 `preservation-cold-chain.json`；两张Computer Use观察截图紧接C04-10，操作工具标为MCP。长路径验证脚本原失败与修正版分别保留，插件数据读取通过。完整C04/C-N与统一资格仍Not Run；电荷/偶极图保留b709096历史身份，操作登记22项。

C04切片绑定路径修复候选为 `outputs/candidates/current/tutorial-slice-e26d22a/qcblender-0.0.1.zip`，源码 `e26d22a`；原生四平面及身份拒绝守卫、GUI定平面/Gizmo/等值线/探针和ESP剖面补验Passed，证据与重建脚本见 `outputs/evidence/2026-10-01/tutorial-cu/full/C04/slice-retest/preservation.json`，原生报告见 `outputs/evidence/2026-10-01/tutorial-cu/slice-plane/`。保全工程 `outputs/projects/tutorial-cu-full/cases/C04/C04-slice-fixed-checkpoint.blend + .qcdata` 共95文件、6 Dataset/172数组；原路径新进程冷读和三份CSV复导出Passed。此95文件阶段工程的完整成图及移动/解包链条未复验；后续117文件工程的成图和三路径冷重开见上方completion批次。完整C-N及统一资格仍Not Run；阶段进程已退出，隔离配置保留待后续验证。

C04旧多选映射补验候选为 `outputs/candidates/current/tutorial-mapping-b709096/qcblender-0.0.1.zip`，源码 `b709096`，菜单修复分支任务记录提交 `6310d6e`；安装及默认F3执行Passed，完整资格Not Run。历史失败、原始动作/截图与摘要映射见 `outputs/evidence/2026-10-01/tutorial-cu/mapping-top-menu/preservation.json` 及 [补验索引](acceptance/tutorial-cu-validation.json)。保全工程 `outputs/projects/tutorial-cu-full/cases/C04/C04-F3-checkpoint.blend` 与 `.qcdata`；三份新阶段工程冷重开、剩余C04/完整C-N仍Not Run。按该批scripts与build.json重建；main未合并，分支/工作树和本批隔离配置保留。

| 任务 / 日期 | 提交或标签 | 证据与主要报告 | 工程、候选与阻塞 | 重建入口 |
| --- | --- | --- | --- | --- |
| 教程点击补验与逐步骤截图 / 2026-10-01 | 基础已验候选92d498c；最新菜单补验候选b709096见上文；历史1554ee2与90ff9bf身份分列 | outputs/evidence/2026-10-01/tutorial-cu/；[补验索引](acceptance/tutorial-cu-validation.json)，full/fog/、full/C02/、full/C03/ 与 full/C04/ 分别保存缺陷、原生动作、截图、数组和冷重开报告；截图逐步骤置于 docs/v1-acceptance/screenshot/ | 基础已验候选 outputs/candidates/current/tutorial-fog-92d498c/qcblender-0.0.1.zip；新工程 outputs/projects/tutorial-cu-full/cases/C02/C02.blend + .qcdata、C02.png 与 C02.zip，中文移动/解包副本见 full/C02/relocation.json。C02/C03三路径冷重开Passed；C04阶段工程 outputs/projects/tutorial-cu-full/cases/C04/C04-mapping-checkpoint.blend + .qcdata，74文件摘要见 full/C04/portable-checkpoint-MCP.json，图例补验和原阶段冷读见 full/C04/legend/；新增 C04-legend-checkpoint.blend + .qcdata 的74文件摘要见 portable-legend-checkpoint.json，保全见 preservation.json；完整C04及新图例工程冷重开仍Not Run；C03完整工程在 outputs/projects/tutorial-cu-full/cases/C03/C03.blend + .qcdata，PNG/ZIP及26文件清单见 full/C03/portable-archive-MCP.json，移动映射见 full/C03/relocation.json，保全收据见 full/C03/preservation-complete.json；C03进程均正常退出，outputs/runs/cu/4/p 保留待后续验收；完整02 claimed、03 pending，main未合并、工作树与分支保留；独立签署Not Run。历史配置清理及提前合并拒绝见 closing.json；本轮活跃配置保留 | [SOP](v1-acceptance/SOP.md)、本批脚本与索引；各历史报告保持原始字节 |
| 公共教程与节点可读性 / 2026-10-01 | 验证`90ff9bf`，已合入main；05/06 resolved；四个注释标签前缀`archive/2026-10-01/`，完整分支名与提交见验证索引 | `outputs/evidence/2026-10-01/public-tutorial-mcp/`：`qualification-mcp.json`、`cases.json`、`nodes-report.json`、`cold-{original,moved,unpacked}.json`、真实`screenshots/`及渲染；此前原生证据在`outputs/evidence/2026-09-30/public-tutorial/`；[索引](acceptance/tutorial-validation.json) | 最新候选`outputs/candidates/current/public-tutorial-90ff9bf/qcblender-0.0.1.zip`；新工程`outputs/projects/public-tutorial-mcp-20261001/tutorial.blend`及qcdata，归档ZIP在本批证据目录；`closing.json`与`cleanup-prep/{storage-result,preservation-mapping-final}.json`记录清理/旧路径映射，四新工作树/分支已正常移除。MCP技术验收Passed，用户复做/鼠标点击/独立签署Not Run；最终可见MCP进程PID21116使用独立`outputs/runs/pm/final-view/p`；旧活跃配置与历史权限阻塞保留 | [SOP](v1-acceptance/SOP.md)、manifest、[开发说明](DEVELOPMENT.md)及本批脚本；新批次不得覆盖历史证据 |
| 工作树与 outputs 维护 / 2026-09-30 | 验证 `aaf20f8`；已合并 `8188a41`，归档 `archive/2026-09-30/chore/output-maintenance` | `outputs/evidence/2026-09-30/output-maintenance/`：`result.json`、`cleanup-safe/{summary,applied}.json`、`before/after.jsonl.gz`、`path-map.jsonl.gz`、`routes.json`、`protection-checks.json`、`closing.json`、`worktree-preservation.json` | 本轮工作树及已合并分支已正常移除；旧权限/占用及未知对象保留，任务 02/03 保持 claimed | 本批命令 JSON（历史参数）；新批次按开发说明；[维护规则](agents/storage-maintenance.md) |
| 清理复查补丁 qcf3 / 2026-09-30 | 源码 `a7f9b43`；已合并 `20bfdcd` | `outputs/evidence/2026-09-30/cleanup-followup/qcf3/`：`qualification.json`、`evidence-index.json`、`gui/`；[验证索引](acceptance/cleanup-validation.json) | 历史 ZIP 暂保留于 `outputs/candidates/current/qcblender-0.0.1.zip`；签署 Not Run，待本轮验收后解除基线引用再清理 | [开发说明](DEVELOPMENT.md)；资格与 GUI 覆盖见验证索引 |
| 仓库清理 / 2026-09-30 | `47fd82c` | `outputs/evidence/2026-09-30/cleanup-followup/f458/`，按旧相对路径查报告；保全收据 `outputs/evidence/2026-09-30/cleanup-followup/preservation.json` | f458 的 11 个目录、3 个 ZIP 访问拒绝，旧工作树及分支保留；旧 ZIP 不作为可用候选 | 原任务 `.scratch/repository-cleanup/`；原始输入与共用环境 |
| 输入集中与产物维护 / 2026-09-29 | `archive/2026-09-29/chore/storage-cleanup` | `outputs/evidence/2026-09-30/history/storage-cleanup/`：`applied.json`、`branch-archive.json`、冷重开日志 | 用户保全工程见下表；旧验证不继承为本轮通过 | [历史记录](acceptance/storage-cleanup.md)及当前开发说明 |

本批IR显隐修复候选50,633,643字节，SHA-256 `694e27cbc328a64b9fe6bb07d6236273474de26de13af8d6f8e2c9cdbc98c4cd`；初批MCP教程基线候选仍保留，大小50,633,596字节，SHA-256：`4a0ac3e46c163dd32a53057ddb2f4e414901d7c56b95d59aa6d17a8df3b739ca`。公开样本包为`outputs/evidence/2026-09-30/public-tutorial/samples/qcblender-public-tutorial-samples-v1.zip`，SHA-256 `a4ccfc3ef91921817d17284196ba23ccfb7cce7b1643cdfa41af8e8a6103f85b`。本批新旧必要证据保全映射见`outputs/evidence/2026-10-01/public-tutorial-mcp/cleanup-prep/preservation-mapping-final.json`；历史路径按映射定位，不将已删除路径称为仍可直接取得。上轮qcf3候选暂保留，身份分别维护。上轮维护批次的重建探针通过安装、生命周期及双冷重开，随后清理其 ZIP、场景和隔离配置；保留命令、摘要和报告，不替换待验收候选，也不宣称 ZIP 字节复现。

本轮正式清理两次apply删除24,750个文件/1,845,200,762字节，执行失败0；清理后复验110项输入、69项科学回归及锁定环境重建Passed。盘点4,199,701,889→2,625,815,407字节，净减少1,573,886,482字节，包含新证据和独立最终可见配置；权限不可读目录内容不计入两端。保全映射1516项，旧报告字节保持；旧路径不再承诺直接可取，按映射查副本，已删除候选/缓存从保留输入和环境重建。`runs/pt/3/p`与`runs/pm/final-view/p`分别由活跃窗口使用，结束并保全后才清；未知输入/恢复文件与158项扫描阻塞原位保留。旧f458十四对象拒绝和b48c空根占用仍未解除，相关历史任务未resolved。

## 保全工程与共用环境

| 位置 | 当前核对与用途 |
| --- | --- |
| `outputs/projects/public-tutorial-mcp-20261001/tutorial.blend` + `tutorial.qcdata/` | MCP本批保全；55个科学对象绑定、1098次数组摘要、15个VDB，在原路径、中文移动和归档解包三个新可见进程Passed；截图/渲染/CSV/工程ZIP见本批证据和验证索引 |
| `outputs/projects/public-tutorial-90ff9bf/tutorial.blend` + `tutorial.qcdata/` | 本轮保全，256项副本摘要含候选/样本；42个科学对象绑定、785次数组摘要、12个VDB冷重开Passed；可见PID37508及独立`outputs/runs/pt/3/p`保持活跃保护 |
| `outputs/projects/user-session-20260930/current.blend` + `current.qcdata/` | 当前可见 Blender 工程；新进程 Dataset/11 项数组核对 Passed，见维护批次 `user-cold.json` |
| `outputs/projects/cleanup-followup-original/未命名.blend` + 同名 `.qcdata/` | 原任务保全快照，原字节与验证索引摘要一致 |
| `outputs/projects/recovery/pid3144-preserved/evidence.blend` + `evidence.qcdata/` | 历史用户工程；本轮新进程 4 个 Dataset、数组及 3 个 VDB 摘要和加载 Passed，见 `recovery-cold.json` |
| `outputs/recovery/`、`outputs/projects/recovery/另一个目录/` | 原始恢复资料及可读副本；部分对象访问拒绝，尚不能确认完整保全，原目录保留 |
| `outputs/build-site/`、`outputs/science/` | 共用构建工具和科学环境；现有锁定版本及清理后 69 项科学回归 Passed |
| `outputs/wheels/qualified/` | 显式核对的 11 个锁定 wheels 和 `backend-wheel.json`；版本/锁文件不变，见 `qualified-wheels.json`、`environment.json` |
| `outputs/backend-wheel.json` 与 `outputs/wheels/` 的旧后端 wheel | 默认记录对应的旧 wheel 不可读，原位保留；默认后端路径检查 Failed，不能当作已修复 |
| `outputs/cleanup-followup-20260930/b48c/outputs/qcf3/profile/` | 可见 Blender PID 14284 仍使用的安装配置；保留至会话正常退出后重新核对，不随旧任务删除 |
| `outputs/runs/pt/1`、`pt/2`、`outputs/runs/public-tutorial/` | 探索批次和子任务材料共约1.29GB；最终清理未执行，日志/原件归属及保全后按策略处理。`pt/3`为当前验收批次，活跃配置保留 |
| `outputs/blender-dev/`、`outputs/blender-runtime.json` | 运行时记录引用的现有配置，保留；其引用解除前不清理 |
| `outputs/build-python/`、`build-sources/`、`gbasis-build/`、`native-backend-licenses/`、`reference-tools/`、`m0-research/`、`visualization-adoption/`、`repaired-wheels/`、`unrepaired-wheels/` | 构建来源、许可证、参考资料或尚待用途确认的环境；保留原路径，不自动归为重复环境 |

当前可复用的后端是 `wheels/qualified/backend-wheel.json` 与同目录 wheels 的配对，不是根目录旧记录。新工作树先核对锁定摘要，再把这份记录显式复制到该工作树忽略的 `outputs/backend-wheel.json`；打包传入 `--wheels-dir <主检出>/outputs/wheels/qualified`，科学检查传入 `--site <主检出>/outputs/science`。本轮脚本 `rebuild.py`、`short-rebuild.py`、`after-validation.py` 和 `qualification.py` 保存实际参数；原工作树已移除，复验先创建干净工作树、显式复制并核对必要输入，然后改用新批次和报告位置，不能直接覆盖历史证据。新批次换成未使用的短目录，复用 [开发说明](DEVELOPMENT.md) 的退出码记录流程。

## 历史任务路由

以下为 2026-09-30 的迁移日期；各任务的原执行日期、源码身份和 Passed/Failed 保持在原报告与 [CHANGELOG](CHANGELOG.md) 中。历史相对层级和字节不变。旧候选、可重建测试工程及孤立配置不再承诺可用；权限拒绝对象可能仍原位存在，不作为已保留的可用交付。需要复跑时，从对应任务工具、保留输入及当前锁定环境重建并重新资格检查。

| 历史任务 | 保留证据目录（相对 outputs） | 查找入口 |
| --- | --- | --- |
| acceptance | `evidence/2026-09-30/history/acceptance/` | `density-esp-cold-view.json`、`extension.json` |
| analysis-gui | `evidence/2026-09-30/history/analysis-gui/` | `esp.json`、`irc.json` |
| animation-acceptance | `evidence/2026-09-30/history/animation-acceptance/` | `result.json` |
| animation-acceptance-v2 | `evidence/2026-09-30/history/animation-acceptance-v2/` | `result.json` |
| atom-visibility | `evidence/2026-09-30/history/atom-visibility/` | `gui.json`、`reopened.json` |
| blender-acceptance | `evidence/2026-09-30/history/blender-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| blender-analysis-gui | `evidence/2026-09-30/history/blender-analysis-gui/` | 批次内原相对层级；完整路径见 routes.json |
| blender-external-worker | `evidence/2026-09-30/history/blender-external-worker/` | 批次内原相对层级；完整路径见 routes.json |
| blender-final-acceptance | `evidence/2026-09-30/history/blender-final-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| blender-localized-install | `evidence/2026-09-30/history/blender-localized-install/` | 批次内原相对层级；完整路径见 routes.json |
| blender-m7 | `evidence/2026-09-30/history/blender-m7/` | 批次内原相对层级；完整路径见 routes.json |
| blender-m8 | `evidence/2026-09-30/history/blender-m8/` | 批次内原相对层级；完整路径见 routes.json |
| blender-pure-acceptance | `evidence/2026-09-30/history/blender-pure-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| branch-archive | `evidence/2026-09-30/history/branch-archive/` | 批次内原相对层级；完整路径见 routes.json |
| committed-build-d1abfe8 | `evidence/2026-09-30/history/committed-build-d1abfe8/` | `result.json` |
| complex-examples | `evidence/2026-09-30/history/complex-examples/` | `source-inspection.json`、`summary.json` |
| composable | `evidence/2026-09-30/history/composable/` | `report.json` |
| diagnostics | `evidence/2026-09-30/history/diagnostics/` | 批次内原相对层级；完整路径见 routes.json |
| extension-cleanup | `evidence/2026-09-30/history/extension-cleanup/` | `applied.json`、`cold-reopen.json` |
| external-results | `evidence/2026-09-30/history/external-results/` | `gui.json` |
| external-worker | `evidence/2026-09-30/history/external-worker/` | 批次内原相对层级；完整路径见 routes.json |
| fog-acceptance | `evidence/2026-09-30/history/fog-acceptance/` | `report.json` |
| handoffs | `evidence/2026-09-30/history/handoffs/` | 批次内原相对层级；完整路径见 routes.json |
| irc-acceptance | `evidence/2026-09-30/history/irc-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| layer-acceptance | `evidence/2026-09-30/history/layer-acceptance/` | `report.json` |
| log-fixtures | `evidence/2026-09-30/history/log-fixtures/` | `cclib-data-tree.json`、`cclib-tree.json` |
| molecularnodes-parameters | `evidence/2026-09-30/history/molecularnodes-parameters/` | `a-precheck-science.json` |
| multiwfn-parameters | `evidence/2026-09-30/history/multiwfn-parameters/` | `worktree-retirement.json` |
| nbo-acceptance | `evidence/2026-09-30/history/nbo-acceptance/` | `gui-undo.json` |
| nocv-acceptance | `evidence/2026-09-30/history/nocv-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| node-assets | `evidence/2026-09-30/history/node-assets/` | `report.json` |
| optimization-trajectory | `evidence/2026-09-30/history/optimization-trajectory/` | `candidate.json`、`document-checks.json` |
| repository-cleanup-merge | `evidence/2026-09-30/history/repository-cleanup-merge/` | `merge-receipt.json` |
| result-browser | `evidence/2026-09-30/history/result-browser/` | `final-receipt.json`、`gui-checks.json` |
| scalar-probe | `evidence/2026-09-30/history/scalar-probe/` | `manifest.json`、`result.json` |
| source-adoption | `evidence/2026-09-30/history/source-adoption/` | `final-audit.json`、`wheel-recovery.json` |
| storage-cleanup | `evidence/2026-09-30/history/storage-cleanup/` | `applied.json`、`branch-archive.json` |
| v1-acceptance | `evidence/2026-09-30/history/v1-acceptance/` | 批次内原相对层级；完整路径见 routes.json |
| vesta-comparison | `evidence/2026-09-30/history/vesta-comparison/` | `input.json` |
| visual-acceptance | `evidence/2026-09-30/history/visual-acceptance/` | `result.json` |
| visual-acceptance-v2 | `evidence/2026-09-30/history/visual-acceptance-v2/` | `result.json` |
| vmd-parameters | `evidence/2026-09-30/history/vmd-parameters/` | 批次内原相对层级；完整路径见 routes.json |
| volume-probe | `evidence/2026-09-30/history/volume-probe/` | `result.json` |
| workflow-migration | `evidence/2026-09-30/history/workflow-migration/` | 批次内原相对层级；完整路径见 routes.json |

根目录零散历史报告、脚本和日志集中在 `outputs/evidence/2026-09-30/history/root/`。全部任务原路径到现位置的 SHA-256 映射见维护批次 `path-map.jsonl.gz`；主检出源码引用同时记录固定 source_commit/source_path，main 后续改动时按该 Git 身份取回并核对摘要。本轮已改动文件的少量字节副本位于 `fixed-source-reference/`，修正收据为 `source-reference-fix.json`；`routes.json` 按原任务名称定位。原报告中的旧路径是历史信息，不能直接视为仍存在；未迁移且保留的科学原件另列 unknown_inputs。

## 本轮清理结果与后续维护

正式摘要盘点的可读普通文件从 86,043 个 / 4,423,648,046 字节变为 29,291 个 / 1,453,516,003 字节，净减少 2,970,132,043 字节（约 2.97 GB）。同口径排除不可读对象，包含新增的必要证据、工程和 qualified wheels；此为收据时间点大小，后续日志增加会改变现值。按清单成功删除 67,453 个文件 / 3,279,888,606 字节，另合并 37 个已核对报告副本并移除 15,031 个空目录。

- Passed：11,063 项迁移目标摘要，33 份报告、8 张截图与 CSV，104 个输入摘要，8 项清理边界测试，科学 69/69，保留候选资格核对、重建/安装/生命周期和原地/中文移动冷重开，用户工程 Dataset/数组/VDB，既有标签和源码子模块。
- Failed：168 个访问拒绝盘点项、两份活跃进程日志无法删除；f458 14 项拒绝与 b48c 空根占用，旧工作树/分支保留；旧默认后端 wheel 不可读。本轮首次长批次安装在中文解压路径超过 Windows 长度限制，日志保留；短批次复验 Passed。
- Not Run：独立人工科研签署；未扩展到全量历史 SOP、ACL 修改、远端发布或 push。

后续任务从本页添加一行日期、提交/归档标签、证据、工程、候选可用性、重建步骤和阻塞；收尾更新清理收据及 CHANGELOG。任务 policy 和详细清单放本批 evidence。未知内容默认保留，不按扩展名或“测试目录”名字删除；权限、占用及保全失败项保持 claimed。具体实施规则见[存储维护](agents/storage-maintenance.md)。
