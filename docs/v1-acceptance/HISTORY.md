# SOP 历史证据与维护索引

本页保存从 SOP 移出的历史批次说明、技术检查与截图。整理基线为提交 `190e11e`，整理日期为 2026-10-06。下面的历史引文保留原文、候选身份和图注；其中的“本轮”“当前”及步骤位置指各自记录时的语境。当前人工操作以 [SOP](../../validation/human/SOP.md) 为准，材料和技术流程集中在 [validation](../../validation/README.md)。

## 维护与验收管理入口

| 内容 | 权威入口 |
| --- | --- |
| 安装包、工程、保全与重建 | [ARTIFACTS](../ARTIFACTS.md) |
| 独立人工验收状态 | [任务 02](../../.scratch/v1-acceptance/issues/02-human-acceptance.md) |
| 完整版本验收与外部对照范围 | [验收规格](../../.scratch/v1-acceptance/spec.md) |
| Alpha 技术验证和发布门禁 | [Alpha 验证](../acceptance/alpha-readiness-validation.md)、[发布流程](../research/github-release-workflow.md) |
| P1 关联与共享 mesh | [P1 验证](../acceptance/audit-p1-validation.md) |
| 拼接日志与重复 ETS-NOCV | [P2 验证](../acceptance/audit-p2-baselines-validation.md) |
| 静态参考、IGMH、取消及 VDB | [可靠性验证](../acceptance/reliability-validation.md) |
| 交互复用与产物维护 | [Blender 交互规则](../agents/blender-interaction.md)、[存储维护规则](../agents/storage-maintenance.md) |

用户操作、Agent Computer Use、MCP/原生数据检查和独立科研审阅分别记录；技术通过仅覆盖其绑定的候选与范围，不转写为用户签署。维护者在相应任务和验证索引维护状态，不在操作教程中追加执行日志。

## 准备、Alpha 与通用操作的历史记录

本教程保留 **C01–C13** 科学案例和 **N01–N18** 节点/交互检查编号。按钮位置与当前插件界面一致；对话框及部分控件仍使用英文。操作结果只记 **Passed / Failed / Not Run**。用户实际点击、Agent Computer Use 点击、MCP操作与数据核对、独立科研签署分别记录；Agent 不填写使用者签名。维护者按 [交互规则](../agents/blender-interaction.md) 和 [操作登记表](../acceptance/blender-operations.json) 复用已确认且功能未变的操作，MCP/命令行复验单独记录，完整案例结果仍逐项验收。

本文保留未变操作的历史Agent截图及所有用户截图占位；已有图的候选、输入和参数仅绑定[历史点击索引](../acceptance/tutorial-cu-validation.json)。旧二维图截图集中于文末历史证据定位，不能作为当前CSV导出或0.2 Å网格的验收。当前批次引用[展示精度、XYZ与数据导出验证索引](../acceptance/display-xyz-export-validation.json)；本轮新增入口已由Agent实际点击确认，MCP/原生检查与原地、中文移动冷重开通过；每张图保留其候选身份，e317→9d3ff61的单行目录修复按索引复核并重新点击验证。用户复做和独立科研签署仍为 **Not Run**。实际操作者在每步占位下追加独立文件名的截图，不覆盖历史证据。

2026-10-05静态参考、IGMH声明、取消和原生VDB检查见[可靠性验证](../acceptance/reliability-validation.md)。下列新增截图绑定a3ed826最终候选；MCP准备对象和参数，实际确认、Undo/Redo、Esc和保存由Agent Computer Use执行。用户复做与科研签署仍单独填写。

| 阶段 | 连续执行的操作 | 进入下一阶段前的检查 |
| --- | --- | --- |
| 1 材料与批次 | 按 0.1 建立本次目录，核对扩展 ZIP、样本包、输入及许可，填写批次身份 | 文件和摘要匹配；C02/C06 的 P02 必须另行取得并核对，缺少时对应案例记 Not Run |
| 2 干净配置安装 | 按 A00/A01 启动独立配置，安装扩展并检查科学运行库；按 0.2 定位编辑器和解除对象图钉 | 精确 Blender/扩展版本已记录，运行库检查成功，QCBlender 侧栏可见 |
| 3 首次出图 | 连续执行 A02–A09：导入 P01、自动预检、生成 Alpha 源 MO9、改等值、渲染、导出摘要、自包含保存、中文移动及新进程重开 | A01–A09 各有结果和证据；文件、科学身份及当前显示参数能够核对 |
| 4 科学案例 | 按下表执行 C01–C13 和 X01；每例先走 0.3 导入/来源核对，再执行该例全部编号步骤 | 科学记录、参数变化前后及错误/取消行为有实际记录；输入依赖未满足则停止该例 |
| 5 每例完成闭环 | 执行 0.5 所需 CSV 导出及当前视图摘要；再按 0.4 渲染、保存、原地冷重开、中文移动冷重开、归档及解包冷重开 | 图片、导出、工程和配套数据齐全；每次确认旧 PID 退出后才启动下一进程，摘要和源数值一致 |
| 6 节点与交互 | 在已保存工程的独立副本执行 N01–N18；先解除节点编辑器图钉，选择正确修改器，再改输入或接线 | 实际节点/接线、原值→新值和结果已记录；公共资产新增后打包关联库，再完成保存/冷重开 |
| 7 缺陷与复做 | Failed 时保留错误、工程与输入，登记缺陷；修复后以新候选重做相关操作、导出及工程闭环 | 未解决必需项仍为 Failed；缺输入或未执行仍为 Not Run，不能从历史通过记录继承 |
| 8 汇总与签署 | 按 3.1 填写工具、对象、参数及证据；按 3.2 逐行汇总；满足 3.3 条件后由独立使用者签署 | C/X、N、必要技术与许可材料全部符合完成条件，签名及科研适用性由实际独立验收者填写 |

本路线适用于 manifest **0.1.0** 的 GitHub Alpha 候选。每次记录扩展 ZIP、源码提交、样本 ZIP 和 P01 SHA-256；候选技术结果、Agent 点击、独立使用者试装与科研签署分别记录。首次 Alpha 的公开门禁见[发布研究与流程](../research/github-release-workflow.md)，正式 v1 仍按全部 C/N 案例验收。

先取得本批扩展 ZIP、v2 公开样本 ZIP、`release-manifest.json` 和 `SHA256SUMS.txt`。本地候选由[产物路由](../ARTIFACTS.md)定位；GitHub 附件仅在实际发布后下载。核对包大小、摘要及清单中的源码提交，不把本地 run ID 0 当作 GitHub CI 身份。将 v2 包解压到 `inputs/`，保持 P01 等目录结构。

科学 Dataset 的 **1 GiB** 上限包含保留源数组、新场值、有效域掩码及各 `.npy` 文件头。求值预算是另一个估算，计入全部驻留输入、输出与工作数组，不等于 Dataset 大小，也不是进程峰值保证。512³ 请求必须在大型数组分配和 VDB 写入前拒绝。

| 门禁 | 本次状态与证据 |
| --- | --- |
| 候选包技术检查 | Passed；127 标准库、67 公开科学、123 完整本地科学及安装/冷读，见[本批验证](../acceptance/alpha-readiness-validation.md) |
| Agent 界面确认 | Passed；本批实际生成、取消、Undo/Redo、等值、渲染、摘要、保存及中文移动重开；安装/原始导入使用 CLI，独立试装另记 |
| 组件许可复核 | Not Run；记录 IOData/GBasis 声明差异的处理依据 |
| 独立使用者短 SOP 试装 | Not Run；使用者填写候选摘要、步骤结果与签名 |
| 维护者公开批准 | Not Run；批准后在 GitHub UI 将草稿公开为 prerelease |
| 完整 v1 人工与科研验收 | Not Run；继续使用 C01–C13 / N01–N18 及独立签署 |

以下截图绑定 `19e4cf0` / `0c2d9add…73a03` 本地 Alpha 候选，由 Agent Computer Use 实际输入；公开复现工程和初始活动对象由 CLI 准备。完整步骤、失败修补及科学/人工边界见[本批验证](../acceptance/alpha-readiness-validation.md)。

填写批次身份，不沿用历史候选的通过状态：

两者摘要相同。历史原站取得与摘要核对Passed，仅证明提供者检查时可取得；每位使用者仍需核对实际下载。不把 P02 文件放进公开附件或归档分发。

   ![历史示例（原参数/原候选）：Agent操作示例：QCBlender N 侧栏与工作流入口](screenshot/00-qcblender-sidebar.jpg)

   历史剖面相机与渲染截图见文末历史证据定位，仅对应旧二维实现。当前剖面使用采样记录及0.5的数据导出；分子/场/切片渲染仍按本节执行。

   ![历史示例（原参数/原候选）：Agent原生菜单操作：文件、外部数据、打包关联库；随后MCP核对内嵌库摘要](screenshot/N18-pack-linked-libraries-menu-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：保存自包含工程的文件对话框](screenshot/00-04-portable-save.jpg)

   ![Agent点击偏好中的数据导出目录（e317候选）](screenshot/display-xyz-export/D01-export-preference-e317.jpg)

   ![偏好留空、未保存工程使用系统Documents（e317候选）](screenshot/display-xyz-export/D01-export-default-unsaved-e317.jpg)

   ![Agent点击导出；偏好留空、已保存工程使用blend父目录（9d3ff61）](screenshot/display-xyz-export/D01-export-default-saved-9d3ff61.jpg)

   ![Agent点击IR导出；三模式的频率和强度另经MCP逐值核对（9d3ff61）](screenshot/display-xyz-export/D01-IR-export-9d3ff61.jpg)

   ![Agent输入本次覆盖目录；偏好不改变（9d3ff61）](screenshot/display-xyz-export/D01-export-override-9d3ff61.jpg)

   ![Agent选择Current filter；四个原始bin和源百分比另经MCP核对（9d3ff61）](screenshot/display-xyz-export/D01-ESP-filtered-export-9d3ff61.jpg)

   计算取消可另行复做：选择可求值FCHK原子对象，经 **N侧栏 → QCBlender → 工作流 → 生成量子化学场** 启动计算，在运行中按 **Esc**，核对没有新增结果。a3ed826批次使用ESP、0.05 Å、margin 3 Å、1024 MiB；MCP确认worker正在运行，Agent按Esc后退出、任务登记清空且场景不变。下图为计算取消，CSV运行中GUI取消仍为Not Run；CSV worker取消由原生脚本覆盖。

   ![Agent Computer Use取消正在运行的ESP计算；MCP核对进程与场景不变（a3ed826）](screenshot/reliability/06-compute-cancelled.png)

   ![Agent再次打开对话框，恢复偏好目录；两次101行CSV逐值相同（9d3ff61）](screenshot/display-xyz-export/D01-export-reset-9d3ff61.jpg)

## C01–C05 历史记录与截图

### C01 FCHK、开壳层轨道与密度

   ![历史示例（原参数/原候选）：Agent Computer Use：FCHK 源记录与原子身份](screenshot/C01-01-source-fchk.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：逐字节 FCH 别名导入](screenshot/C01-01-fch-import.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Alpha 按源编号选择 MO9](screenshot/C01-02-alpha-mo9-settings.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Beta 按源编号选择 MO7](screenshot/C01-02-beta-mo7-settings.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：独立正负阈值](screenshot/C01-03-independent-thresholds.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：两相颜色与独立透明度](screenshot/C01-03-independent-opacity.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：总电子密度](screenshot/C01-04-total-result.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：自旋密度阈值 0.002](screenshot/C01-04-spin-002.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：体积雾的颜色及透明度控件](screenshot/C01-05-fog-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：盒裁剪开启；数组摘要另行核对](screenshot/C01-05-box-on-x0.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Opacity Scale 为 0 时体积雾消失](screenshot/C01-05-fixed-scale0.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Opacity Scale 恢复 40 后体积雾即时出现](screenshot/C01-05-fixed-scale40-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：不透明度渐变全黑时体积雾消失](screenshot/C01-05-fixed-ramp-black.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：恢复黑白渐变后体积雾即时出现](screenshot/C01-05-fixed-ramp-white.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：复制层为 0，原层保持 40 且仍可见](screenshot/C01-05-fixed-copy-independent.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复候选新建雾层及其材质](screenshot/C01-05-fixed-new-material.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：轨道渲染及图像另存](screenshot/C01-06-mo-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：总电子密度原生渲染及保存](screenshot/C01-06-total-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Alpha 密度原生渲染及保存](screenshot/C01-06-alpha-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Beta 密度原生渲染及保存](screenshot/C01-06-beta-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：自旋密度原生渲染及保存](screenshot/C01-06-spin-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：密度展示另存自包含工程](screenshot/C01-06-density-portable-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：自包含工程保存完成](screenshot/C01-06-portable-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：新进程通过文件菜单冷重开](screenshot/C01-06-cold-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：冷重开后重新渲染](screenshot/C01-06-cold-render.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：归档工程文件对话框](screenshot/C01-06-archive-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：工程归档完成](screenshot/C01-06-archive-saved.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：中文移动路径的文件打开对话框](screenshot/C01-06-moved-open-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：中文移动副本冷重开](screenshot/C01-06-moved-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：移动副本重新渲染](screenshot/C01-06-moved-render.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：归档解包后的新进程冷重开](screenshot/C01-06-unpacked-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：解包工程重新渲染](screenshot/C01-06-unpacked-render.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复复验另存自包含工程](screenshot/C01-06-fog-fixed-portable.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：新建雾层原生 F12 渲染](screenshot/C01-06-fog-fixed-render.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复工程原路径冷重开（92d498c候选）](screenshot/C01-06-fog-fixed-cold-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复工程原路径冷重开后渲染（92d498c候选）](screenshot/C01-06-fog-fixed-cold-render.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复工程中文移动副本冷重开（92d498c候选）](screenshot/C01-06-fog-fixed-moved-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复工程中文移动副本重新渲染（92d498c候选）](screenshot/C01-06-fog-fixed-moved-render.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复工程归档解包副本冷重开（92d498c候选）](screenshot/C01-06-fog-fixed-unpacked-restored.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复工程归档解包副本重新渲染（92d498c候选）](screenshot/C01-06-fog-fixed-unpacked-render.jpg)

   密度检查点复核：保存于步骤6的 `C01-density.blend + .qcdata` 已在2eddb6a候选的新原生后台进程冷重开，175配套文件、9 Dataset/221数组、17对象引用及7体积源一致；四密度重新渲染并检查，总密度=Alpha+Beta、自旋密度=Alpha−Beta关系通过。详见[点击补验索引](../acceptance/tutorial-cu-validation.json)的 `C01_density_checkpoint_cold`，原候选/保存身份与历史批次冷读身份分别记录。安装候选deb9416的后续原位置、中文移动及归档解包冷重开均通过；175配套文件、全部引用及四密度关系一致，12次重渲染像素与上述四张原图一致。此补验通过串行原生命令行执行，索引 `C01_density_checkpoint_current_three_paths` 记录报告、摘要、保留工程和重复图清理收据。最终统一候选资格另行维护，原 GUI 与雾工程证据保持原批次。

### C02 Log/Out 能量、振动与优化

   ![Agent点击导入真实Log Job2，能量与三模式保留；没有新谱图（e317候选）](screenshot/display-xyz-export/C02-job2-e317.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-01-log-alias-job2-preview](screenshot/C02-01-log-alias-job2-preview.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-01-log-source](screenshot/C02-01-log-source.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-01-calculation-source](screenshot/C02-01-calculation-source.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-01-zpe-record](screenshot/C02-01-zpe-record.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：选择真实 Log 文件](screenshot/C02-01-log-file.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：选择 Job 2 频率计算段](screenshot/C02-01-job2.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：能量记录与振动模式](screenshot/C02-01-energy-modes.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-mode3-playback](screenshot/C02-02-mode3-playback.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-mode3-phase-vectors](screenshot/C02-02-mode3-phase-vectors.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-mode1-playback](screenshot/C02-02-mode1-playback.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-mode2-playback](screenshot/C02-02-mode2-playback.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：模式3与振动显示参数](screenshot/C02-02-mode3-parameters.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：模式1播放画面](screenshot/C02-02-mode1-playing.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：模式2播放画面](screenshot/C02-02-mode2-playing.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-03-job1-preview](screenshot/C02-03-job1-preview.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-optimization-step1](screenshot/C02-04-optimization-step1.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-optimization-step2](screenshot/C02-04-optimization-step2.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-optimization-step3](screenshot/C02-04-optimization-step3.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-optimization-step4](screenshot/C02-04-optimization-step4.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-choose-step-dialog](screenshot/C02-04-choose-step-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-ballstick-converged](screenshot/C02-04-ballstick-converged.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-copy-step2](screenshot/C02-04-copy-step2.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-original-still-step1](screenshot/C02-04-original-still-step1.jpg)

   ![Agent在Log Job2之后打开新FCHK对话框，计算段重置（e317候选）](screenshot/display-xyz-export/C02-new-dialog-reset-e317.jpg)

   ![Agent确认P03 FCHK导入成功，六原子与源摘要另经MCP核对（e317候选）](screenshot/display-xyz-export/C02-fchk-success-e317.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-05-new-dialog-reset](screenshot/C02-05-new-dialog-reset.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-05-fchk-file-selected](screenshot/C02-05-fchk-file-selected.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-05-fchk-six-atoms](screenshot/C02-05-fchk-six-atoms.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：Log Job 2 后打开新的 FCHK 文件对话框](screenshot/C02-05-fchk-new-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：新 FCHK 导入结果](screenshot/C02-05-fchk-success.jpg)

6. 按0.4对实际振动/优化原子视图创建相机并渲染，用面板截图记录模式/频率/强度与能量；按0.5分别导出IR和optimization的CSV+metadata。对应N12/N15/N16保存工程，保留C02-energy、vibration、optimization、reimport截图与数据文件；历史IR图仅见旧索引。世界/文字颜色属于展示设置，不改变源值。

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-original-restored](screenshot/C02-06-cold-original-restored.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-original-render](screenshot/C02-06-cold-original-render.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-moved-restored](screenshot/C02-06-cold-moved-restored.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-moved-render](screenshot/C02-06-cold-moved-render.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-unpacked-restored](screenshot/C02-06-cold-unpacked-restored.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c，独立进程冷重开）：C02-06-cold-unpacked-render](screenshot/C02-06-cold-unpacked-render.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-camera](screenshot/C02-06-camera.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-white-background](screenshot/C02-06-white-background.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-black-label-material](screenshot/C02-06-black-label-material.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-render](screenshot/C02-06-render.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-png-save-dialog](screenshot/C02-06-png-save-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-portable-saved](screenshot/C02-06-portable-saved.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-06-archive-saved](screenshot/C02-06-archive-saved.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-04-portable-saved](screenshot/C02-04-portable-saved.jpg)

### C03 Cube/cub 物理量、网格与双符号

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-01-cube-selected](screenshot/C03-01-cube-selected.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-01-cube-imported](screenshot/C03-01-cube-imported.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-01-cub-selected](screenshot/C03-01-cub-selected.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-01-cub-imported](screenshot/C03-01-cub-imported.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-02-cub-declaration-parameters](screenshot/C03-02-cub-declaration-parameters.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-02-cub-declared](screenshot/C03-02-cub-declared.jpg)

   ![历史示例（原参数/原候选）：Agent MCP声明；Computer Use仅观察结果：C03-02-cube-declared-MCP](screenshot/C03-02-cube-declared-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-unlinked-003-001](screenshot/C03-03-unlinked-003-001.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-both-phases](screenshot/C03-03-both-phases.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-negative-only](screenshot/C03-03-negative-only.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-positive-only](screenshot/C03-03-positive-only.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-wire](screenshot/C03-03-wire.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-points](screenshot/C03-03-points.jpg)

   ![历史示例（原参数/原候选）：Agent 实际点击：C03-03-opacity-06-03](screenshot/C03-03-opacity-06-03.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP复验别名阈值/透明度；Computer Use观察](screenshot/C03-03-alias-controls-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP导入及声明真实几何场，GUI隐藏重复层](screenshot/C03-03-geometry-unmapped-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：GUI活动几何场与颜色映射入口](screenshot/C03-03-mapping-entry.jpg)

   ![历史示例（原参数/原候选）：Agent示例：GUI独立着色场来源与范围](screenshot/C03-03-mapping-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent示例：GUI关联着色结果；MCP取样核对](screenshot/C03-03-mapped-result.jpg)

   ![历史示例（原参数/原候选）：Agent示例：GUI替换为cub别名](screenshot/C03-03-replace-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent示例：GUI替换结果，范围和取样属性保留](screenshot/C03-03-replaced-result.jpg)

   ![历史示例（原参数/原候选）：Agent示例：GUI双符号阶段取景；Computer Use观察截图](screenshot/C03-05-phase-camera.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP双符号阶段渲染；Computer Use观察截图](screenshot/C03-05-phase-render-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP双符号阶段保存自包含工程；Computer Use观察截图](screenshot/C03-05-phase-portable-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP阶段工程冷重开数据核对；Computer Use观察截图](screenshot/C03-05-phase-cold-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP阶段工程冷重开渲染，像素一致；Computer Use观察截图](screenshot/C03-05-phase-cold-render-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP保存完整C03工程，3 Dataset/18数组/9引用；Computer Use观察截图](screenshot/C03-05-portable-mapping-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：MCP完整映射工程渲染；Computer Use观察截图](screenshot/C03-05-mapped-render-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：新可见进程原路径MCP冷重开及渲染；Computer Use观察截图](screenshot/C03-05-original-cold-render-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：新可见进程中文移动路径MCP冷重开及渲染；Computer Use观察截图](screenshot/C03-05-moved-cold-render-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent示例：新可见进程归档解包MCP冷重开及渲染；Computer Use观察截图](screenshot/C03-05-unpacked-cold-render-MCP.jpg)

### C04 ESP、电荷、偶极、切片、探针与剖面

1. 导入P03 FCHK，选原子对象分别 **N侧栏 → QCBlender → 工作流 → 生成量子化学场**，Quantity选Electron density/Electrostatic potential，两次 **Grid spacing=0.2 Å、Grid margin=3 Å、Memory budget=512 MiB**。记录当前实际网格与有效掩码，核对密度electron/bohr^3、ESP hartree/e；核附近无效点不算物理零。历史0.7 Å截图保留原身份，当前0.2 Å生成参数/结果须另截图，不继承历史插值值。

   ![Agent输入0.2Å、margin3Å、512MiB生成密度（e317候选）](screenshot/display-xyz-export/C04-density-fine-dialog-e317.jpg)

   ![新密度网格39×31×49；等值0.004electron/bohr³，MCP核对2188个求值顶点（e317候选）](screenshot/display-xyz-export/C04-density-fine-surface-e317.jpg)

   ![历史示例（原参数/原候选）：Agent点击：密度/ESP生成参数与密度结果；网格0.7 Å](screenshot/C04-01-density-generation-parameters.jpg)

   ![历史示例（原参数/原候选）：Agent点击：密度/ESP生成参数与密度结果；网格0.7 Å](screenshot/C04-01-density-generated.jpg)

   ![历史示例（原参数/原候选）：Agent点击：密度/ESP生成参数与密度结果；网格0.7 Å](screenshot/C04-01-ESP-generation-parameters.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：密度生成示例；ESP 须另行操作](screenshot/C04-01-density-dialog.jpg)

2. 选**密度表面**，打开 **对象属性 → 颜色映射 → 选择／替换着色场**，选择 ESP；核对候选源 SHA、job、量名/单位再确认。密度决定几何，ESP 决定颜色。隐藏独立 ESP 表面的显示和渲染，不删除其内部体场。

   ![历史示例（原参数/原候选）：MCP复用映射操作：密度0.004表面按ESP着色，21点数值核对](screenshot/C04-02-density-ESP-mapped-MCP.jpg)

3. 填 **Color Minimum=−0.05、Color Center=0、Color Maximum=+0.05**，须严格递增；在 **图例排版** 开 **显示图例**（Show Legend），改 长宽/字号/小数/方向/旋转/位置。点击 **零中心对称** 输入 **R=0.05**，再 **读取有效范围** 对照一次读取结果；记录并恢复成图色域。示例排版填长度 **2.6**、宽度 **0.25**、字号 **0.2**（均为本地布局单位），小数位数 **3**，开启竖向排列，旋转 **(0,0,0.3)**（rad），位置 **(3.5,0,0)**。在 **材质属性 → QCBlender · 节点材质** 修改 Color map 中间停靠点 **0.5→0.4**，将 **Reverse (0 or 1)** 从 **0→1**，确认表面和图例颜色方向同时反转；成图前恢复中点 **0.5** 与 Reverse **0**。原生撤销用 **编辑 → 撤销**，重做用 **编辑 → 重做**。范围外用端点颜色，无效采样为洋红；历史0.7 Å批次1800点均有效；当前批次核对实际掩码与无效域颜色。

   ![历史示例（原参数/原候选）：Agent点击：零中心对称与读取有效范围；图例排版和色带操作见下列补验图](screenshot/C04-03-zero-centered-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent点击：零中心对称与读取有效范围；图例排版和色带操作见下列补验图](screenshot/C04-03-valid-range.jpg)

   ![历史示例（原参数/原候选）：Agent点击：色域对称、读取范围和图例显隐；排版与色带见下列补验图](screenshot/C04-03-legend-visible-restored-range.jpg)

   ![历史示例（原参数/原候选）：Agent点击：图例默认排版](screenshot/C04-03-legend-default.jpg)

   ![历史示例（原参数/原候选）：Agent点击：长度2.6、宽度0.25、字号0.2、小数3](screenshot/C04-03-legend-dimensions.jpg)

   ![历史示例（原参数/原候选）：Agent点击：切换竖向排列](screenshot/C04-03-legend-vertical.jpg)

   ![历史示例（原参数/原候选）：Agent点击：图例Z旋转0.3 rad](screenshot/C04-03-legend-rotated.jpg)

   ![历史示例（原参数/原候选）：Agent点击：图例X位置3.5](screenshot/C04-03-legend-positioned.jpg)

   ![历史示例（原参数/原候选）：Agent点击：材质属性中的Color map与Reverse入口](screenshot/C04-03-material-before.jpg)

   ![历史示例（原参数/原候选）：Agent点击：Reverse=1，表面与图例方向同时反转](screenshot/C04-03-material-reversed.jpg)

   ![历史示例（原参数/原候选）：Agent点击：色带中间停靠点改为0.4](screenshot/C04-03-ramp-middle-changed.jpg)

   ![历史示例（原参数/原候选）：Agent点击：编辑菜单重做Reverse修改](screenshot/C04-03-material-menu-redo.jpg)

   ![历史示例（原参数/原候选）：Agent点击：恢复中点0.5与Reverse=0](screenshot/C04-03-material-restored.jpg)

   ![历史示例（原参数/原候选）：Agent观察：Object顶部QCBlender菜单中的旧映射入口](screenshot/C04-04-top-object-menu-entry.jpg)

   ![历史示例（原参数/原候选）：Agent点击新建视图，MCP核对无着色绑定并设置两对象选择](screenshot/C04-04-new-view-before-F3.jpg)

   ![历史示例（原参数/原候选）：Agent点击：默认配置F3检索旧映射操作](screenshot/C04-04-F3-fresh-map-entry.jpg)

   ![历史示例（原参数/原候选）：Agent点击：新未映射视图映射参数−0.05至+0.05](screenshot/C04-04-F3-fresh-map-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent GUI选择Mulliken电荷；此图为b709096批次](screenshot/C04-05-charge-mulliken-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent GUI将Charge Maximum设为0.5 e；保留原科学电荷](screenshot/C04-05-charge-range-half.jpg)

   ![历史示例（原参数/原候选）：Agent GUI创建偶极；默认0.5 Å/Debye](screenshot/C04-05-dipole-created-default.jpg)

   ![历史示例（原参数/原候选）：Agent GUI将偶极设为1.5 Å/Debye；方向及源向量不变](screenshot/C04-05-dipole-scale-1_5.jpg)

   ![Agent确认新切片201点/轴（e317候选）](screenshot/display-xyz-export/C04-slice201-dialog-e317.jpg)

   ![独立密度示例：201²显示点；MCP设色域0/0.0005/0.001electron/bohr³，ESP主案例按正文另操作（e317候选）](screenshot/display-xyz-export/C04-slice201-e317.jpg)

   ![历史示例（原参数/原候选）：Agent点击：创建新的ESP切片；候选e26d22a](screenshot/C04-06-fixed-new-slice-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent点击：Grid ij，101×101采样](screenshot/C04-06-fixed-grid-ij.jpg)

   ![历史示例（原参数/原候选）：Agent点击：Grid jk；混合绝对与相对绑定路径已通过复验](screenshot/C04-06-fixed-grid-jk.jpg)

   ![历史示例（原参数/原候选）：Agent点击：Grid ki](screenshot/C04-06-fixed-grid-ki.jpg)

   ![历史示例（原参数/原候选）：Agent点击：首次三原子平面1/2/3；教程2/1/4另经MCP复验](screenshot/C04-06-fixed-three-atoms-dialog.jpg)

   ![历史示例（原参数/原候选）：Agent点击：三原子平面；5072个域外采样点以洋红显示](screenshot/C04-06-fixed-three-atoms.jpg)

   ![历史示例（原参数/原候选）：Agent点击：自由平面Center/Rotation/Width/Height；6×6 Å](screenshot/C04-06-fixed-free-parameters.jpg)

   ![历史示例（原参数/原候选）：Agent拖动：QC Slice Gizmo平移](screenshot/C04-06-fixed-gizmo-move.jpg)

   ![历史示例（原参数/原候选）：Agent拖动：QC Slice Gizmo旋转](screenshot/C04-06-fixed-gizmo-rotation.jpg)

   ![历史示例（原参数/原候选）：Agent拖动：QC Slice Gizmo改变宽度](screenshot/C04-06-fixed-gizmo-width.jpg)

   ![历史示例（原参数/原候选）：Agent点击显式阈值与标签；MCP取景后观察，−0.02/0/0.02 hartree/e](screenshot/C04-06-fixed-explicit-contours-framed.jpg)

   历史内部无效域示例：真实水二聚体核附近5³ ESP，124点有效、1核点无效；21×21、0.18×0.18 Å切片有121点无效、渲染洋红；20/25/30 hartree/e阈值生成84段有效单元等值线。这是掩码传播诊断，不能推定当前0.2 Å全分子场命中同一核排除区。参数/工程仅绑定历史索引field_guards_and_recovery。

   ![历史示例（原参数/原候选）：MCP创建诊断切片，原生Blender渲染：内部核区无效采样为洋红；显示范围10至70 hartree/e](screenshot/C04-internal-mask-magenta.png)

   ![历史示例（原参数/原候选）：MCP原生异步等值线，20/25/30 hartree/e；84段线全部位于有效单元，核区无效范围不连线](screenshot/C04-internal-mask-contours.png)

   ![历史示例（原参数/原候选）：Agent点击：读取游标ESP，0.0085721002 hartree/e](screenshot/C04-07-esp-cursor-valid.jpg)

   ![历史示例（原参数/原候选）：Agent点击：ESP切片几何场取点预览，Enter保存](screenshot/C04-07-esp-geometry-probe-preview.jpg)

   ![历史示例（原参数/原候选）：Agent点击：第二取点预览后Escape恢复原记录](screenshot/C04-07-esp-geometry-probe-Escape-preview.jpg)

   ![历史示例（原参数/原候选）：Agent点击：密度表面绑定色场取点，实际采样ESP](screenshot/C04-07-bound-color-probe-preview.jpg)

   ![历史示例（原参数/原候选）：Agent点击Enter：保存0.072094069 hartree/e绑定色场读数](screenshot/C04-07-bound-color-probe-saved.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：独立密度几何场取点预览，单位 electron/bohr^3；该示例不是 ESP 取点](screenshot/C04-07-click-probe-preview.jpg)

   ![Agent点击采样线剖面数据；独立密度示例，MCP设起终点(-2,0,1.8)/(2,0,1.8)Å、101点（e317候选）](screenshot/display-xyz-export/C04-profile-dialog-e317.jpg)

   ![Agent确认采样记录，MCP核对101个源值；无新二维曲线（e317候选）](screenshot/display-xyz-export/C04-profile-record-e317.jpg)

   历史密度示例使用0.7 Å、margin3 Å，起终点(0,−2,1.45)/(0,+2,1.45)、Samples101；保留其源值身份。当前0.2 Å的ESP/密度采样各自执行并核对，不能继承历史插值值或有效点数。

   历史内部掩码补验：核点线段−0.1至+0.1 Å取9样本，valid为True/True/True/False/False/False/True/True/True，无效CSV值留空。(.075,.075,.075) Å独立插值一致；核点邻近拒绝无效角点，(.11,0,0) Å拒绝域外。该诊断仅绑定历史索引及旧源数组，当前导出需重新核对valid与空白值。

   ![历史示例（原参数/原候选）：MCP创建真实内部掩码剖面并导出CSV，Computer Use仅观察截图：核区三样本留空且曲线断开](screenshot/C04-internal-mask-profile-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP设置新源与活动参考；GUI关联按钮可用](screenshot/C04-09-source-selection.jpg)

   ![历史示例（原参数/原候选）：Agent首次GUI关联：刚体配准关闭，完整容差0.001 Å](screenshot/C04-09-association-tolerance.jpg)

   ![历史示例（原参数/原候选）：Agent GUI确认成功；MCP核对六原子映射和源数组不变](screenshot/C04-09-association-success.jpg)

   本例成图：密度/ESP表面与分子从正面观察，图例Legend Rotation设X=90°、Y=0°、Z≈17.19°（0.3 rad），使量/单位朝向相机。自由切片从顶面观察，更新当前等值线后取景；切片Margin可用0.15，其他空间视图0.05。历史二维剖面相机Margin0.20只绑定旧索引；当前剖面以采样记录和CSV+metadata核对。

   ![历史示例（原参数/原候选）：MCP导出并另存工程：7 Dataset、222数组、117配套文件；三路径冷重开报告见验证索引](screenshot/C04-10-association-exports-saved-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP在新可见进程核对中文移动工程、CSV和渲染；Computer Use观察截图](screenshot/C04-10-completion-cold-moved-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP在新可见进程核对ZIP解包工程、CSV和渲染；Computer Use观察截图](screenshot/C04-10-completion-cold-unpacked-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP另存检查点：6 Dataset、172数组；此图尚非最终C04成图](screenshot/C04-10-slice-fixed-checkpoint-saved-MCP.jpg)

   ![历史示例（原参数/原候选）：新进程MCP冷重开与CSV复导出；单独显示ESP剖面，完整C04成图待验收](screenshot/C04-10-slice-fixed-cold-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP保存阶段工程；完整C04渲染与冷重开待补验](screenshot/C04-10-mapping-checkpoint-saved-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP保存图例阶段工程；154数组保持原摘要，完整C04及本工程冷重开待补验](screenshot/C04-10-legend-checkpoint-saved.jpg)

   ![历史示例（原参数/原候选）：MCP保存F3映射阶段工程；3 Dataset和154数组核对，完整C04与冷重开待补验](screenshot/C04-10-F3-checkpoint-saved-MCP.jpg)

### C05 氢显隐、局部选择、标注与显示层

   ![历史示例（原参数/原候选）：Agent操作示例：水二聚体全部6个源原子](screenshot/C05-01-all-hydrogens.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：隐藏氢后保留氧，源编号1与4](screenshot/C05-01-hidden-hydrogens.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：保留指定氢，源编号2；氧仍保留](screenshot/C05-01-keep-hydrogen-2.jpg)

   ![历史示例（原参数/原候选）：Agent操作示例：撤销恢复6个原子，再用Edit菜单的Redo重做隐藏氢；返回氧1与4](screenshot/C05-01-redo-menu.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：并集后源编号1、2、4](screenshot/C05-02-union-result-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：源编号1及1.0 Å邻域参数](screenshot/C05-02-radius-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：邻域返回源编号1、2、3](screenshot/C05-02-radius-result-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：编号1、4的独立局部显示层](screenshot/C05-03-local-layer-result-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：按测量顺序输入距离编号1、4](screenshot/C05-04-distance-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use观察：N侧栏中文按钮与对象属性英文按钮入口](screenshot/C05-04-two-entry-paths-GUI.jpg)

   原生操作示例使用独立显示层 **C05 final annotations**，先恢复全部6个原子，仅选该层。角度输入 **2,1,3**、二面角输入 **2,1,4,5**，**Decimal places=3**；确认后分别为 **112.770°**、**0.000°**。历史示例中 Agent Computer Use 实际创建；独立 NumPy 参考和 MCP 同时核对源编号顺序、单位、锚点、引线及50个科学数组。

   ![历史示例（原参数/原候选）：Agent Computer Use：当前活动原子层与标注入口](screenshot/C05-final-entrances-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：角度编号2,1,3及三位小数](screenshot/C05-final-angle-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：二面角编号2,1,4,5；B→C约定](screenshot/C05-final-dihedral-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：距离文字大小调整为0.22](screenshot/C05-05-edit-size-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use观察：MCP调整颜色、偏移和小数后，科学距离仍为2.900 Å](screenshot/C05-05-edited-result-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：点击Face All to Camera；MCP核对实际旋转](screenshot/C05-final-face-camera-GUI.jpg)

   可复现排版：保持原子对象位置/旋转为0、缩放为1，球棍 **Atom Radius=0.35 Å、Bond Radius=0.12 Å、Quality=2**。四项文字设 **Size=0.16、Color RGB=(0.03,0.03,0.03)、Decimal places=3、Leader width=0.008、Show leader与可见勾选**；隐藏重复的旧标注及对应引线。分别设置下表 Offset，然后再点 **Face All to Camera**。这些设置只影响显示；历史示例另用MCP核对父对象缩放(2,0.5,1.5)后科学测量和源数组不变，再恢复缩放。

   图中排版使用Size=0.14，距离Offset=(0.3,−0.6,0.95)、角度Offset=(0.3,−0.6,−0.65)，从 **+X** 观察水的 **YZ** 源平面；文字朝向同方向相机。你可用右视图和视图缩放复现画幅。以下为MCP切步、调整排版后由Computer Use观察截图；本批逐步坐标与距离/角度经独立NumPy计算核对。

   ![历史示例（原参数/原候选）：MCP优化第1步；Computer Use观察：0.990 Å、106.000°及未完成收敛状态](screenshot/C05-followup-optimization-step1-framed-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP优化第4步；Computer Use观察：0.989 Å、100.037°及收敛状态](screenshot/C05-followup-optimization-step4-framed-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use移除前：独立临时显示层处于活动状态，移除按钮与对象同屏](screenshot/C05-Remove-confirmed-before.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use点击移除后：临时层及12个复制标注消失，下一层自动激活；MCP独立核对原对象及50数组，随后恢复先前显隐](screenshot/C05-Remove-confirmed-after.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：复制原子显示层；MCP核对Mesh、外层树和8个标注数据独立](screenshot/C05-display-layer-copy-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：上移副本；随后下移恢复原顺序，MCP核对次序](screenshot/C05-layer-order-up-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：对象顶部菜单 → QCBlender → 复制显示参数到选中视图；源最后选中并保持活动](screenshot/C05-copy-parameters-menu-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：确认几何表示、外观、数值设置三类别](screenshot/C05-copy-parameters-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use观察MCP选中的目标：球棍/0.35/0.12已复制，氧集合1、4和编号控件保留](screenshot/C05-copy-parameters-result-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：修复候选隐藏原子层，所属标注与引线同步隐藏](screenshot/C05-06-atom-layer-hidden-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：恢复原子层及所属标注](screenshot/C05-06-atom-layer-restored-GUI.jpg)

   当前版本视图示例：仅选上述 **P02第4步优化标注层**，点击 **创建当前版本视图**。新层应保留第4步和两项标注，Mesh、外层节点树、文字、曲线和材质独立；原层仍保留。历史批次真实点击后MCP核对通过，并在新层遍历四步，不改变原层；临时副本的单项标注和显示层移除另由MCP执行与核对，不记录为GUI删除点击。

   ![历史示例（原参数/原候选）：Agent Computer Use：创建当前版本优化视图；MCP核对第4步、独立图及标注](screenshot/C05-followup-current-view-after-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use观察：MCP另存自包含参数工程；原生新进程冷重开核对另记](screenshot/C05-controls-portable-saved-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP复用渲染操作：水二聚体全部6原子](screenshot/C05-final-render.png)

   ![历史示例（原参数/原候选）：MCP复用渲染操作：局部层只显示源氧1、4](screenshot/C05-selection-final-render.png)

   ![历史示例（原参数/原候选）：MCP实际渲染：O1、2.900 Å、112.770°、0.000°；四项标注与引线](screenshot/C05-annotations-final-render.png)

   历史批次另存 **C05-final.blend + .qcdata** 和同条目ZIP；关闭可见进程后，原路径、中文移动、解包分别在新原生后台进程冷重开，核对24文件、1 Dataset/50数组、6视图、52标注对象，并各重新渲染三图，像素一致。记录见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C05_native_annotations_and_renders`；历史失败报告保留，隐藏对象的保存变换通过完整父级链核对。退化、随优化/IRC步更新、移除与当前版本视图另行验收，不能据此将整个C05或全教程写为Passed。

![MCP选中真实优化Dataset；Computer Use展开外部结果面板，四个适用入口禁用（a3ed826）](screenshot/reliability/05-dynamic-reference-disabled.png)

## C06–C13 与 X01 的历史截图、执行记录和维护说明

以下为从原 SOP 移出的历史片段，保留原文与相对图片链接。批次身份、工具覆盖与当时验证结论以片段及所链接报告为准；当前操作流程见 SOP。

### C06 NBO 与 E(2)

   ![历史示例（原参数/原候选）：Agent Computer Use：仅选P02 Job2原子对象，在导入外部结果中点击NBO记录](screenshot/C06-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Gaussian Log/Out、Job2、block1原生导入对话框](screenshot/C06-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：第1条NBO与E(2)，7轨道、2相互作用及原文行](screenshot/C06-record1-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：分别选择第2条NBO与E(2)，核对源编号与数值](screenshot/C06-record2-GUI.jpg)

   本例在 **对象属性 → QCBlender · 对象与量子化学 → External Result Browser** 将 **Orbital type=BD、Orbital order=Occupancy, high to low、E(2) order=E(2), high to low**，点击 **应用筛选**；应显示2条轨道、2条E(2)。复原全部类型与默认范围后再点应用。Agent实际点击了上述组合；编号、范围、空结果和全部排序组合另由MCP用独立预期核对，不冒称逐项点击。

   ![历史示例（原参数/原候选）：Agent Computer Use：BD筛选和降序，应用后显示2轨道、2条E(2)](screenshot/C06-filter-BD-GUI.jpg)

   用相同字节的 `water_neutral_nbo_opt_freq.log` 再导入Job2/block1，新增记录对象而原记录保持。随后在3D视图执行 **Edit（编辑）→ 撤销**，确认别名对象消失；执行 **Edit（编辑）→ 重做**，确认别名对象及其原子父对象关联恢复。菜单复验Passed；历史批次快捷键尝试未恢复，失败截图单独留在证据目录，教程使用实际确认的菜单路径。

   ![历史示例（原参数/原候选）：Agent Computer Use：相同SHA的log别名，Job2/block1](screenshot/C06-cold-native-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：撤销后别名对象消失，原out记录保持](screenshot/C06-cold-native-undo-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Edit重做菜单恢复log对象；MCP核对完整分析和父对象](screenshot/C06-cold-native-menu-redo-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use观察：log别名、7条NBO/2条E(2)、单位、源行和关联水分子](screenshot/C06-cold-records-overview-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP复用相机构图及渲染：P02 Job2水分子，表格数据另见界面图](screenshot/C06-render.png)

   历史批次保存 **C06-final.blend + .qcdata** 与同条目ZIP；关闭GUI进程后，原地、中文移动、解包三个新原生后台进程分别读取38文件、3 Dataset/33数组、NBO关联和全部元数据，并重渲染核对像素一致。证据见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C06_NBO_records_browser_alias_and_cold_chain`。独立人工/科研签署仍为Not Run。

### C07 IGMH、IRI 成对场与数据导出

   ![历史示例（原参数/原候选）：Agent Computer Use：P03参考原子对象与成对场导入入口](screenshot/C07-entry-GUI.jpg)

   ![Agent Computer Use填写inter、片段与来源并确认；输入路径由MCP准备（a3ed826）](screenshot/reliability/01-igmh-declaration-dialog.png)

   ![MCP选择paired记录；Computer Use展开并核对IGMH来源声明（a3ed826）](screenshot/reliability/04-igmh-declaration-panel.png)

   本批来源填写`P03 GUI declaration`，表示本次用户声明文字；不是软件对片段物理意义的独立确认。

   ![历史示例（原参数/原候选）：Agent Computer Use输入并确认：IGMH两文件、单位和色域](screenshot/C07-IGMH-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use观察：IGMH导入结果；全部数组及关联另由MCP核对](screenshot/C07-IGMH-imported-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use选择IRI并确认：路径和数值由MCP准备，a为1.1](screenshot/C07-IRI-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP复用显示控件与相机构图，真实EEVEE渲染：IGMH 0.005，颜色取自独立sign(lambda2)rho场](screenshot/C07-igmh-v2.png)

   ![历史示例（原参数/原候选）：MCP复用显示控件与相机构图，真实EEVEE渲染：IRI 1.0、a=1.1](screenshot/C07-iri-v2.png)

4. 只选 **QC paired field data**，打开 **对象属性 → QCBlender → External Result Browser**，核对X为sign_lambda2_rho [electron/bohr^3]、Y为delta_g [electron/bohr^4]。启用四范围，填 **X from=−0.04、X to=0.04、Y from=0.001、Y to=0.02**，点 **Apply Filter**，再按0.5导出数据（Data）=paired、Rows=Current filter。历史36,391匹配数仅作本轮CSV行数待核实预期；结果及metadata记录实际筛选。

   勾 **Swap value columns**，保持四数值并重新应用/导出；范围作用于交换后的量列，历史28,630行待本轮CSV核实。保持同一物理筛选区须同步交换X/Y范围。IRI颜色−0.04..0.04、IRI0.1..2历史12,736行也待本轮CSV核实，同步交换范围时应保留同一体素集合。再导出Rows=All source records，核对539,448个有效体素及原索引，不使用50,000显示抽样。

   ![Agent交换值列并应用筛选；MCP准备真实配对Dataset与参考构型，没有新散点图（e317候选）](screenshot/display-xyz-export/C07-voxel-browser-e317.jpg)

   ![Agent Computer Use按Ctrl+Z撤销导入；MCP核对完整对象和绑定快照（a3ed826）](screenshot/reliability/02-igmh-undo.png)

   ![Agent Computer Use经Edit → Redo恢复；MCP核对完整快照与原科学数组（a3ed826）](screenshot/reliability/03-igmh-redo.png)

   ![历史示例（原参数/原候选）：MCP准备错误配对、Agent Computer Use确认：P03几何与P05颜色](screenshot/C07-wrong-pair-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use观察拒绝；MCP核对原有对象与绑定不变](screenshot/C07-wrong-pair-refused-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use执行Edit菜单撤销：新增配对对象移除](screenshot/C07-native-undo-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use执行Edit菜单重做：对象与同一科学记录恢复](screenshot/C07-native-redo-GUI.jpg)

   ![Agent Computer Use确认保存自包含工程；原地和中文移动新进程冷读另经脚本核对（a3ed826）](screenshot/reliability/08-portable-saved.png)

   ![历史示例（原参数/原候选）：Computer Use观察与截图：MCP保存后的IGMH总览；保存和控件设置由MCP执行](screenshot/C07-saved-overview-MCP.jpg)

   历史批次保全44文件、3 Dataset/66数组和4体积文件，关闭GUI后依次在三个新原生后台进程读取原路径、中文移动和ZIP解包工程；九次真实重渲染像素一致。报告、输入/候选摘要及工具身份见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C07_paired_fields_scatter_and_cold_chain`。该冷读为命令行技术证据，用户复做及独立科研签署仍为Not Run。

### C08 ESP 极值与面积分布

   ![历史示例（原参数/原候选）：Agent Computer Use：实际ESP场与ESP表面分析入口；密度阈值另由MCP准备](screenshot/C08-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP准备参数、Agent Computer Use确认：ESP极值与面积导入](screenshot/C08-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use观察：最大值记录1，36.69 kcal/mol](screenshot/C08-maximum-record1-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use选择：最大值记录2，57.80 kcal/mol及源坐标](screenshot/C08-maximum-record2-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use启用范围并应用：2条最大值；40/60由MCP准备](screenshot/C08-maximum-filter-GUI.jpg)

   ![Agent补充示例：中心范围-10至10kcal/mol；四bin、14.0429Å²、原百分比19.1886%；与正文0至20范围分别记录，MCP准备来源（e317候选）](screenshot/display-xyz-export/C09-esp-area-data-e317.jpg)

   点击 **3D视图 → N侧栏 → QCBlender → 工程与诊断 → 保存自包含工程**，保存 `.blend + .qcdata`；按0.4的归档工程步骤（N18）打包配套ZIP。完成后正常关闭，原路径、中文移动和ZIP解包路径分别在一个新Blender进程打开核对，每次关闭后再开下一处。本批文件名为 **C08-final.blend**，效果图带 `-v2` 后缀。

   ![历史示例（原参数/原候选）：MCP配置灯光、标签和相机，原生EEVEE渲染：ESP源极值；观察方向会产生投影重叠](screenshot/C08-extrema-v2.png)

   ![历史示例（原参数/原候选）：Computer Use观察与截图：MCP保存的最终工程、源标签和对象属性](screenshot/C08-saved-GUI.jpg)

   历史批次35组MCP筛选核对、5项错误输入检查及120文件/8Dataset/224数组/4体积/20引用保全Passed；三个串行原生后台进程冷读和6次重渲染像素一致Passed。报告、输入/候选摘要、失败诊断与工具身份见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C08_ESP_records_filters_and_cold_chain`。用户复做和独立科研签署仍为Not Run。

### C09 AIM 临界点、路径与属性

   ![历史示例（原参数/原候选）：Computer Use打开AIM拓扑入口；活动对象与参数条件由MCP准备](screenshot/C09-fixed-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP填写三个路径，Computer Use点击确定导入真实AIM数据](screenshot/C09-fixed-dialog-GUI.jpg)

   ![历史示例（原参数/原候选）：首次导入即显示CP类型、对应核、位置和真实电子密度](screenshot/C09-fixed-record1-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use切换记录2：对应核5H，源坐标与电子密度](screenshot/C09-fixed-record2-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use选择路径层：10组中的源组1，9点](screenshot/C09-path1-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use切换路径2：源组2，47点](screenshot/C09-path2-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP准备精确参数，Computer Use启用范围并应用：C源4/5保留](screenshot/C09-fixed-filter-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP配置相机和显示，原生EEVEE渲染：源核点与N9，C核点嵌在原子球内](screenshot/C09-points-v3.png)

   ![历史示例（原参数/原候选）：原生EEVEE渲染：完整源路径，O-H路径与参考键可能投影重叠](screenshot/C09-paths-v3.png)

   ![历史示例（原参数/原候选）：原生EEVEE渲染：参考分子、源C/N标记和路径总览](screenshot/C09-overview-v3.png)

   ![历史示例（原参数/原候选）：Computer Use观察截图：MCP保存的最终工程与属性范围](screenshot/C09-saved-GUI.jpg)

   历史批次28组MCP筛选和7项错误边界、120文件/8Dataset/224数组/4体积/20引用保全Passed；三处串行原生冷读与九次重新渲染像素一致Passed。首次原生导入、立即属性显示及路径选择证据和MCP准备分别记录。报告/输入/候选身份见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C09_AIM_properties_paths_filters_and_cold_chain`；历史清理证据仍引用[cleanup-validation.json](../acceptance/cleanup-validation.json)。用户复做及独立科研签署仍Not Run。

### C10 真实 IRC 步序、能量与随步标注

1. 新建独立工程，按清单保持 **P04/steps.csv** 和 **step-001/002/003.fchk** 的相对目录。CSV是UTF-8，首行为 `step,fchk`，步号从1连续。先在 **inputs/P04/** 复制CSV为 **checks-duplicate.csv**，将第二条数据的step改为1，保留FCHK相对路径。点击 **3D视图 → N侧栏 → QCBlender → 工作流 → 导入 IRC 路径**，在 **CSV manifest: step,fchk** 输入这个副本并点 **确定**。预期拒绝并报告 **Step numbers must be explicit, unique and contiguous from 1**，场景没有新IRC对象。记录副本摘要和错误，保留原件；本批该错误输入由MCP执行并核对未变，GUI错误对话框未执行。

   ![历史示例（原参数/原候选）：Computer Use打开导入IRC路径，唯一活动窗口与空白工程](screenshot/C10-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use填写P04清单并确认；MCP独立核对源坐标和能量](screenshot/C10-dialog-GUI.jpg)

   本示例三标签偏移分别为 **(1.7,−0.4,−0.9)、(1.7,−0.4,−0.2)、(1.7,−0.4,0.8)**，黄色 **(1,0.8,0.2,1)**，绕X轴 **90°**，正对后文Y方向相机。三种标注历史批次复用已确认GUI入口，通过MCP建立；用户可按C05的设置图标与 **Face All to Camera** 调整。

   ![历史示例（原参数/原候选）：Computer Use步1：源坐标、FCHK能量与三种随步标注](screenshot/C10-step1-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use点击Next至TS步2，能量峰值与标注同步](screenshot/C10-step2-GUI.jpg)

   ![历史示例（原参数/原候选）：Computer Use点击Next至步3；另已检查Previous返回步2](screenshot/C10-step3-GUI.jpg)

5. 在步3再次点 **Next**，或步1再点 **Previous**，预期报告 **IRC step is outside the imported path** 且步号、几何与标注不变。历史批次这两项端点检查通过MCP执行。

   ![历史示例（原参数/原候选）：Computer Use点击当前版本视图后的预期拒绝；MCP核对原步2和全部对象未变](screenshot/C10-current-view-rejection-GUI.jpg)

   标签使用上面的黄色发光材质，Strength **1**；世界Background灰色 **(0.12,0.12,0.12)**、Strength **0.8**、Standard视图变换；两Sun能量 **2/0.35**、角宽 **0.35 rad**，Euler XYZ旋转 **(0.7,−0.3,−0.4)/(−0.4,0.4,2.5) rad**。相机/照明与排版通过MCP复用，只影响显示。

   ![历史示例（原参数/原候选）：原生EEVEE渲染：四原子及步2的距离、角度、二面角](screenshot/C10-steps.png)

   ![历史示例（原参数/原候选）：Computer Use观察截图：MCP保存的工程路径、步2能量及对象](screenshot/C10-saved-GUI.jpg)

   历史批次真实导入与Previous/Next、当前版本拒绝原生操作Passed；独立坐标/能量/三种测量及错误输入由MCP核对Passed。8文件、1 Dataset/5数组/3对象引用保全，三处串行冷重开各重放1→2→3→2和三图，九次渲染像素一致Passed，全部进程退出。证据见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C10_IRC_annotations_and_cold_chain`；用户复做及独立科研签署仍Not Run。历史[cleanup-validation.json](../acceptance/cleanup-validation.json)按原批次维护。

### C11 IRC 逐步 Mayer 键级

1. 关闭其他Blender，打开已保存、**尚无Mayer表**的C10工程，保留原件，最后另存C11。保持CSV及三个 `step-001-mayer-pyscf.txt`, `step-002-mayer-pyscf.txt`, `step-003-mayer-pyscf.txt` 的相对位置。缺步检查先在 **inputs/P04/** 复制 `mayer-pyscf.csv` 为 **checks-missing-mayer.csv**，删除step3数据行并保存UTF-8。只选 **IRC path根原子**，打开 **Properties → 对象属性 → QCBlender · 对象与量子化学 → IRC Path → Import Mayer Results**，在 **CSV manifest: step,mayer_output** 指定副本并点 **确定**。预期 **Mayer step count differs from the IRC path**，没有新Mayer表/数组/曲线，原步号不变。已有表的重复导入拒绝不能代替缺步检查；本批缺步由MCP执行，错误对话框GUI未执行。

   ![Agent点击Read Pair 1,2；MCP准备真实Mayer源表并逐值核对，无新曲线（e317候选）](screenshot/display-xyz-export/C11-mayer-read-pair-e317.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：从IRC path根的对象属性打开Import Mayer Results](screenshot/C11-fixed-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：完整P04 Mayer CSV对话框并确认；源值由MCP独立核对](screenshot/C11-fixed-dialog-GUI.jpg)

   标注的 **Visible/show_leader** 控制在每次IRC切步时重新应用；只为某张图临时改变对象渲染开关时，切步后按该图重新核对可见对象。科学记录、标注值和当前步游标不因构图修改。下图排版及渲染通过MCP执行，原生图片已逐张检查。

   ![历史示例（原参数/原候选）：原生EEVEE：步2真实构型和沿用C10的距离、角度、二面角](screenshot/C11-geometry.png)

7. 在 **3D视图 → N侧栏 → QCBlender → 工程与诊断 → 保存自包含工程** 另存 **C11-final.blend + C11-final.qcdata**，按0.4的归档工程步骤（N18）打包配套ZIP。及时关闭并确认进程退出，再在新Blender依次打开原路径、中文移动副本和ZIP解包副本，每次完成后关闭再开下一处。检查两份Dataset/九数组、六对象引用、1,3逐步值和源构型，并重出三图。历史批次13文件全部摘要一致，三处冷读和九次像素一致渲染Passed；九份重复冷渲染已清理，三张原图与报告仍可取。

   历史批次Mayer首次导入和1,3切换由Agent Computer Use完成，源值/错误边界与重复步进由MCP核对，冷读由串行原生后台Blender完成。证据见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C11_Mayer_native_import_pairs_and_cold_chain`；本项Passed不代表完整教程或统一资格完成。用户复做与独立科研签署仍Not Run，历史[cleanup-validation.json](../acceptance/cleanup-validation.json)保持原身份。

### C12 ETS-NOCV 真实结果表

1. 关闭上一工程并确认其进程退出，新建Blender工程，在 **3D视图 → N侧栏 → QCBlender → 工作流 → 导入 Gaussian / Cube / XYZ** 导入 `inputs/P05/complex.fchk`；历史批次该入口复用已有成功GUI记录，通过MCP导入并核对58数组和六个源原子编号。保持 **根原子对象**为唯一活动对象，展开同侧栏 **导入外部结果 → ETS-NOCV 表**。在 **ETS-NOCV output text** 指定 `inputs/P05/nocv/ets-nocv.txt`，**Pair energy unit** 选文件声明的 **kcal/mol**，点 **确定**。预期新增 **QC ETS-NOCV pairs** 子表。导入后根仍活动，不能在根对象上寻找表的记录面板。

   ![历史示例（原参数/原候选）：Agent Computer Use：参考原子活动时的ETS-NOCV表导入入口](screenshot/C12-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：真实ETS-NOCV文本路径与kcal/mol单位](screenshot/C12-dialog-GUI.jpg)

2. 在 **N侧栏 → Display Layers** 点击 **QC ETS-NOCV pairs 行左侧的选择箭头**，或在Outliner选该子表；保持它唯一活动。打开 **Properties → 对象属性 → QCBlender · 对象与量子化学 → External Analysis Records**。**Record (1-based)=1** 查看pair1全部字段、原文行7，再改为 **2** 核对pair2/行8。来源摘要可在同对象面板 **来源详情** 查阅。关联标记 **user_assigned** 表示用户把表分配给参考构型，不表示插件重新进行了ETS-NOCV计算。本批原文逐行独立核对11行的全部字段和来源摘要。

   ![历史示例（原参数/原候选）：Agent Computer Use：pair1记录及原文行7；全部源字段由MCP独立核对](screenshot/C12-record1-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Record改2后显示pair2及原文行8](screenshot/C12-record2-GUI.jpg)

3. 保持表活动，打开同对象属性的 **External Result Browser**。**Pair number=1**、**Spin=总数**（英文Total）、范围勾选关闭，点 **应用筛选**，预期 **Matching records: 1** 和pair1/行7。Pair number的 **0** 表示全部。再设Pair=0、Spin=总数、**Eigenvalue=Negative orbital**，勾选本征值 **从/到** 并填 **−0.6/−0.5**，点 **应用筛选**，仍只匹配pair1。数值已有符号，本征值不取绝对值。本批范围数值由MCP准备，菜单、勾选与应用由Computer Use实际执行。

   ![历史示例（原参数/原候选）：Agent Computer Use：Pair1与Total筛选仅保留一条源记录](screenshot/C12-pair1-filter-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use启用负本征值范围并应用；MCP准备数值−0.6至−0.5](screenshot/C12-negative-filter-GUI.jpg)

4. 取消两本征值范围及两pair能量范围勾选，Pair=0、Spin=总数，选择 **排序 → Positive eigenvalue**，点 **应用筛选**。预期11条，首条 **pair11、positive_eigenvalue=0.00147、source_line=17**，完整顺序 **11,10,9,8,6,7,5,4,2,3,1**；相同值按pair顺序稳定排列。修改控件后必须应用。Pair energy范围使用面板标出的 **kcal/mol**，例如−60到−50只匹配pair1。不存在的pair999、Alpha/Beta筛选得到空结果；倒置范围及声明单位不符应拒绝，原记录保持不变。本批25组筛选/排序和3个错误输入由MCP验证，错误对话框未逐项点击。完成后恢复 **Pair1、Spin总数、范围关闭、排序Pair、Record1**。

   ![历史示例（原参数/原候选）：Agent Computer Use：正本征值排序后首条为pair11、源行17](screenshot/C12-sort-GUI.jpg)

5. 表对象只保存记录，没有可渲染网格。按0.4先选关联根分子出图，并用属性面板截图保存完整表记录。需要带说明文字的效果图时，可用Blender **Add → Text** 手动排版源字段；它是源记录说明，需同时保留单位、原文行号、打印范围和来源，不称为插件自动结果图。下图通过MCP设置原生Font对象并EEVEE渲染：1920×1080、Standard、正交相机 **(1.1,−20,0.1)**、绕X90°、Scale **12**；根显示位置X=−3、绕Z45°，仅改变显示变换，全部科学坐标/数组不变。文字位于Y=−1、朝向相机，默认Font，字号0.15–0.33。沿用C10两Sun照明，世界背景0.06灰/强度0.8；文字浅黄、Emission Strength=1。

   ![历史示例（原参数/原候选）：原生EEVEE：六原子参考构型与手动排版的pair1/2源记录说明](screenshot/C12-overview.png)

6. 在 **3D视图 → N侧栏 → QCBlender → 工程与诊断 → 保存自包含工程** 保存 **C12-final.blend + C12-final.qcdata**，按0.4的归档工程步骤（N18）打包ZIP；一个工程完成后及时关闭。确认退出后在新Blender依次打开原路径、中文移动副本、ZIP解包副本，每处核对11条源记录、2份Dataset、60数组、来源关联、筛选参数与渲染，关闭后再开下一处。历史批次40文件摘要和三处冷读/实际像素一致重渲染Passed；后台CLI在启用插件后显式执行已有 **刷新来源**，避免定时器尚未运行就调用依赖缓存的筛选按钮。首次后台时序Failed保留，不改写为通过。

   本批入口/源记录/筛选/排序首次确认由Agent Computer Use执行，数组和原文、错误输入、保存由MCP核对，冷读/重渲染由串行原生后台Blender完成。证据见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C12_ETS_NOCV_records_filters_and_cold_chain`；本项不代表完整教程或统一资格完成，用户复做及独立科研签署仍Not Run。历史[cleanup-validation.json](../acceptance/cleanup-validation.json)保持原身份。

### C13 NOCV pair Cube 与两符号密度

   ![历史示例（原参数/原候选）：Agent Computer Use：ETS表活动时打开NOCV pair Cube入口](screenshot/C13-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：真实pair Cube、Pair1、Total和明确密度单位](screenshot/C13-dialog-GUI.jpg)

2. 保持新场唯一活动，打开 **Properties → 对象属性 → QCBlender · 对象与量子化学** 核对网格和单位；点 **来源详情**，查看 **Geometry / data source** 的Cube摘要及 **Geometry field** 的量名、单位和Spin。Pair和表关联另选 **QC ETS-NOCV pairs**，在C12的 **External Analysis Records → Record (1-based)=1** 核对Pair1/Total与原文行7，再到 **External Result Browser** 设Pair1、Spin总数并点 **应用筛选**；预期定位已存在的唯一pair场。保存证据时分别记录Cube、ETS表及构型摘要，完整表manifest绑定由维护者报告核对。六原子编号对应 **[C,O,B,H,H,H]**；Cube采用bohr坐标，界面几何坐标采用Å。不要把普通MO Cube当成pair形变密度。本批全部Cube数值、表行、构型、科学数组及VDB由MCP独立核对，登记报告见当前验证索引。

3. 在同一对象属性的 **几何表示** 将 **正值阈值 [electron/bohr^3]=0.003**，勾选 **Link Thresholds**，分别勾选 **显示正值 / 显示负值**。实体模式下，默认蓝色表示正值、红色表示负值；两者都勾选时显示完整两符号密度，均关闭时只剩根分子。正值/负值单独显示分别导出 `C13-positive.png`、`C13-negative.png`；本批求值顶点分别2,052/2,718，合计4,770，数量仅适用于本批网格和显示参数。

   ![历史示例（原参数/原候选）：MCP设置阈值与两个显隐开关，Computer Use观察：两符号密度及实际控件](screenshot/C13-both-MCP.jpg)

   ![历史示例（原参数/原候选）：原生EEVEE：仅显示正值，阈值0.003 electron/bohr³](screenshot/C13-positive.png)

   ![历史示例（原参数/原候选）：原生EEVEE：仅显示负值，阈值0.003 electron/bohr³](screenshot/C13-negative.png)

   ![历史示例（原参数/原候选）：MCP设置独立正负阈值0.004与0.006，Computer Use观察实际界面](screenshot/C13-unlinked-MCP.jpg)

   ![历史示例（原参数/原候选）：MCP设置Positive Opacity0.35及Negative Opacity0.65，Computer Use展开实际材质面板](screenshot/C13-opacity-MCP.jpg)

   ![历史示例（原参数/原候选）：原生EEVEE：不同透明度下可见内部核构型，源密度数组不变](screenshot/C13-opacity.png)

5. 错误输入检查必须重新选择 **QC ETS-NOCV pairs 表对象**，在步骤1的对话框使用同一Cube但 **Pair number=999、Spin=总数**，确认；预期拒绝 **Selected pair and spin do not identify one ETS-NOCV table row**，不新增场、不改变现有科学数据。随后用 **Pair number=1、Spin=Alpha** 再次确认，预期同样拒绝。已有pair场不是导入参考对象。记录真实错误后取消对话框，恢复选择合法Pair1/Total场。本批两次错误导入由MCP调用真实异步Operator，Computer Use仅观察错误提示，不称为本批错误参数点击。

   ![历史示例（原参数/原候选）：MCP执行错误导入后的真实界面提示，Computer Use观察截图](screenshot/C13-guard-MCP.jpg)

6. 按 **N16** 检查撤销/重做：活动pair场，在 **N侧栏 → Display Layers → 复制** 创建副本，只把副本正值阈值改成0.009，原场应保持0.003。3D视口撤销/重做，核对副本存在状态、阈值、独立Mesh/节点树/材质和源绑定；移除本次临时副本时仅移除显示层。记录操作及科学数组保持不变。本批使用MCP的原生复制/撤销/重做和独立断言，未重复点击已登记操作。

   按0.4创建相机并F12渲染总览。本批保留C12显示变换：根X=−3、Z旋转45°；正交相机 **(−3,−20,0.65)**、X旋转90°、Scale **11**，1920×1080、Standard、EEVEE、C12两Sun与灰世界背景，隐藏C12手动说明文字。相机范围完整包围两符号密度；这些是展示参数，科学构型不变。

   ![历史示例（原参数/原候选）：原生EEVEE：Pair1/Total两符号形变密度总览](screenshot/C13-overview.png)

7. 在 **3D视图 → N侧栏 → QCBlender → 工程与诊断 → 保存自包含工程** 保存 **C13-final.blend + C13-final.qcdata**，按0.4的归档工程步骤（N18）打包ZIP，正常关闭并确认退出。依次在新进程打开原路径、中文移动副本、ZIP解包副本，每次核对Pair/Spin/表关联、相对VDB、控件和渲染后关闭再继续。历史批次48文件、3份Dataset、66数组、1VDB、4个科学引用及三处各四张像素一致重渲染Passed；重复冷渲染图核对后清理，四张原图和日志保留。

   ![历史示例（原参数/原候选）：MCP保存自包含工程后由Computer Use观察：C13标题无未保存标记，透明度已恢复](screenshot/C13-saved-MCP.jpg)

   首次合法导入由Agent Computer Use确认；参数/错误输入/复制/撤销重做/保存由MCP复用与核对，冷读及重渲染由串行原生CLI执行。证据见[历史验证索引](../acceptance/tutorial-cu-validation.json)的 `C13_pair_density_controls_and_cold_chain`。C12可见启动缓存恢复另有只读报告；不把后台定时器诊断改写为通过。本项不代表统一资格完成，用户复做和独立科研签署仍Not Run。历史[cleanup-validation.json](../acceptance/cleanup-validation.json)保持原身份。

### X01 标准XYZ与离散帧

   ![Agent首次点击标准XYZ文件导入（e317候选）](screenshot/display-xyz-export/X01-single-import-dialog.jpg)

   ![Agent导入单帧六原子XYZ，显示初值Quality3；源坐标/ID另经MCP核对（e317候选）](screenshot/display-xyz-export/X01-single-quality3.jpg)

   ![Agent导入三帧XYZ；Properties中的XYZ Frames入口（e317候选）](screenshot/display-xyz-export/X01-frame1.jpg)

   ![Agent点击Next至帧3；MCP建立距离/二面角标注并核对随帧值（e317候选）](screenshot/display-xyz-export/X01-frame3-annotations.jpg)

   ![Agent点击Previous返回帧2；1,2距离1.401928Å，二面角-180°（e317候选）](screenshot/display-xyz-export/X01-frame2-annotations.jpg)

   ![MCP复用保存自包含工程；Computer Use观察，保留12Dataset、249数组和VDB（9d3ff61）](screenshot/display-xyz-export/X01-portable-save-9d3ff61.jpg)

   ![新候选冷重开MCP核对帧2、源数组和标注；Computer Use观察（9d3ff61）](screenshot/display-xyz-export/X01-cold-9d3ff61.jpg)

X01技术证据进入[本批验证索引](../acceptance/display-xyz-export-validation.json)；用户复做与独立科研签署保持Not Run，待实际操作者填写。

## N01–N18 历史节点验证与截图

本节保留从 SOP 节点检查中移出的历史候选、维护者验证、截图和旧参数记录。以下原文只对应其注明的对象、参数及执行方式，不能作为本次用户复做结果。

### N01 QC Select Atoms

   ![历史示例（原参数/原候选）：Agent Computer Use（候选2eddb6a）：Element=8；MCP核对源编号1、4](screenshot/N01-element8-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：取消选中项，MCP核对零顶点；源标注仍可见](screenshot/N01-selection-off-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：Element=0、First=2、Last=3；MCP核对氢编号2、3](screenshot/N01-first2-last3-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：从添加菜单选择 QC Select Atoms](screenshot/N01-public-add-menu-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：在独立副本放置公共选择资产](screenshot/N01-public-added-GUI.jpg)

   N02 分支连好后，在新选择节点勾选 **选中项（Selection）**，设 **Element=8、First=1、Last=0**，只显示氧1、4。取消勾选应为空；恢复勾选并设 Element=0、First=2、Last=3，应显示氢2、3。再测 Element=8、First=1、Last=3，只保留氧1；First=2、Last=3时为空。核对实际源编号，不能只比较显示数量：两个氧和两个氢在本例都求值得到84顶点、160面。恢复全原子参数后继续 N02。

   ![历史示例（原参数/原候选）：Agent Computer Use：Selection 输出接入表示节点的 Selection](screenshot/N01-public-selection-wire-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生输入Element=8；MCP核对氧编号1、4，科学数组不变](screenshot/N01-public-oxygen-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生关闭Selection；MCP核对零顶点](screenshot/N01-public-selection-off-GUI.jpg)

### N02 QC Style Atoms and Bonds

   ![历史示例（原参数/原候选）：Agent Computer Use：局部氧1、4的空间填充](screenshot/N02-space-fill-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：相同局部氧集合的键线为空](screenshot/N02-bonds-empty-selection-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：清除局部限制后，六原子的O–H键线](screenshot/N02-bonds-all-atoms-cleared-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：键半径0.12 Å；源数组不变](screenshot/N02-bond-radius012-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：球棍原子半径0.35 Å；原层参数不变](screenshot/N02-atom-radius035-GUI.jpg)

   保持 N01 副本活动，在 **添加 → 表示 → 原子与键 → QC Style Atoms and Bonds** 放置资产。连接 **组输入 → 几何数据** 到新表示节点 **几何数据**，N01 节点 **Selection → Selection**；选择副本的元素材质，再将新表示节点 **几何数据** 接 **组输出 → 几何数据**，替换旧显示输出。本批示例为辅助组输入/输出创建、专用材质和布局由 MCP 准备，三条显示分支接线由 Computer Use 实际拖放；你可直接使用副本原有组输入和组输出。

   ![历史示例（原参数/原候选）：Agent Computer Use：原子与键目录中的公共表示资产](screenshot/N02-public-add-menu-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：新公共表示节点放置于独立副本](screenshot/N02-public-added-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent实际拖放选择及几何接线；辅助输入/输出、材质和布局由MCP准备](screenshot/N01-N02-public-route-GUI.jpg)

   全6原子选择时，将新节点 **Style (0 ball-stick, 1 space-fill, 2 bonds)** 依次设 **0、1、2**，球棍、空间填充和键线分别应为300/252/48顶点、512/480/32面；此计数适用于本批Quality=2、Atom Radius=0.25 Å、Bond Radius=0.07 Å、VDW Scale=1。核对4条O–H键及源编号1–6。改 Atom Radius 或 Bond Radius 时，只改变相应显示半径，不改变科学坐标；对象属性的两半径操作示例见上方。最后恢复Style=0，再按 N09 加裁剪。

   ![历史示例（原参数/原候选）：Agent原生Style=1；MCP核对六原子空间填充252顶点](screenshot/N02-public-spacefill-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生Style=2；MCP核对4条真实O–H推断键及全部源编号](screenshot/N02-public-bonds-GUI.jpg)

### N04 QC Style Isosurface / QC Surface Representation

   ![历史示例（原参数/原候选）：Agent实际添加菜单：表示/表面公共资产](screenshot/N04-01-catalog.jpg)

   ![历史示例（原参数/原候选）：Agent实际Volume与输出接线](screenshot/N04-02-iso-linked.jpg)

   ![历史示例（原参数/原候选）：Agent原生输入Isovalue=0.003](screenshot/N04-03-isovalue.jpg)

   ![历史示例（原参数/原候选）：Agent实际连接独立表面表示分支；MCP辅助对象和材质准备单列](screenshot/N05-01-surface-linked.jpg)

   ![历史示例（原参数/原候选）：Agent原生Style=1；独立边数断言Passed](screenshot/N05-02-wire.jpg)

   ![历史示例（原参数/原候选）：Agent原生Style=2；独立顶点数断言Passed](screenshot/N05-03-points.jpg)

   维护者渲染：以下仅显示独立公共分支，原层在诊断渲染期间临时隐藏，随后完全恢复。MCP原生求值得到实体4770顶点/4762面，线框152384顶点/76192面，点200340顶点/381600面；相关参数、接口和冷读报告见验证索引 `remaining_public_surface_assets`。

   ![历史示例（原参数/原候选）：MCP原生渲染：公共实体分支](screenshot/N04-style-0.png)

   ![历史示例（原参数/原候选）：MCP原生渲染：公共线框分支](screenshot/N04-style-1.png)

   ![历史示例（原参数/原候选）：MCP原生渲染：公共点分支](screenshot/N04-style-2.png)

### N06 QC Sample Scalar Field

   ![历史示例（原参数/原候选）：Agent原生显示层复制；此后节点调整仅作用于副本](screenshot/N15-field-copy-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生添加取样资产；后续Value/Valid接线由MCP完成](screenshot/N06-sample-asset-added-GUI.jpg)

   在副本测试取样位置输入 **(0,0,0)、(0,−2,0)、(0,−2,1.45) Å**，核对同一位置的表面颜色一致。历史0.7 Å网格三ESP值 **1.224086233、−0.044865982、−0.022647081 hartree/e** 仅绑定旧索引；当前0.2 Å网格须重新读取并记录实际值，不沿用此数值。域外/无效检查见N17。

   ![历史示例（原参数/原候选）：位置默认0/0/0；GUI体积接线、MCP数据核对；表面与图例分别计算](screenshot/N06-sample-origin-linked-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生把取样位置Y改为−2；162个真实表面顶点均与独立插值参考一致](screenshot/N06-sample-Y-negative-two-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生把取样位置Z改为1.45；科学值见同批报告](screenshot/N06-sample-Z-one-point-four-five-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生恢复Position接线；MCP核对副本求值摘要恢复且原视图不变](screenshot/N06-sample-Position-restored-GUI.jpg)

### N07 QC Map Scalar Colors v2

   ![历史示例（原参数/原候选）：Agent原生放置颜色资产；接线和副本专用材质由MCP设置](screenshot/N07-color-asset-added-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP连接新颜色节点；同色域下副本几何和颜色分量与原管线相同](screenshot/N07-color-asset-connected-MCP.jpg)

   ![历史示例（原参数/原候选）：Agent原生把色彩最大值改为0.1；MCP独立核对零中心分段映射，测试期间图例关闭](screenshot/N07-color-upper-bound-GUI.jpg)

   ![历史示例（原参数/原候选）：MCP调整副本图例；Computer Use观察截图，原显示层不变](screenshot/N07-field-copy-legend-independent-MCP.jpg)

### N08 QC Planar Slice

   ![历史示例（原参数/原候选）：Agent原生加入平面资产，MCP绑定中心/旋转并连接真实ESP切片](screenshot/N08-slice-asset-connected-MCP.jpg)

   把新节点 **分辨率 101→51**：切片网格顶点应由 **10,201→2,601**，范围仍为 X/Y **−3..3 Å**、Z **1.45 Å**，取样量和单位不变。本项测试新增节点的网格；等值线的重建沿用 C04 步骤，不根据原有曲线宣称已重建为51分辨率。最后将宽度/高度/分辨率接回组输入；新建外层若保持本轮201/轴，应恢复40,401点，已有工程仍按其保存的实际分辨率恢复。公共资产独立初值101不变，原层参数保留。

   ![历史示例（原参数/原候选）：Agent原生修改新平面节点分辨率；MCP核对2601顶点和21点独立插值参考](screenshot/N08-slice-resolution-51-GUI.jpg)

### N09 QC Clip Geometry

   ![历史示例（原参数/原候选）：Agent Computer Use：空间、裁剪目录中的 QC Clip Geometry](screenshot/N09-public-add-menu-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent Computer Use：放置公共裁剪资产](screenshot/N09-public-added-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent实际拖放表示到裁剪、裁剪到输出；边界向量由MCP准备](screenshot/N09-public-route-GUI.jpg)

   设置平面 **Origin=(0,0,1.45) Å、法线=(0,0,1)**，方框 **Minimum=(−0.5,−2,−2) Å、Maximum=(0.5,2,5) Å**。仅勾选平面Enabled时保留上方水分子源编号4、5、6；再同时勾选方框Enabled时保留编号4的部分几何；关闭平面、只保留方框时保留氧1、4及与其关联的部分键几何。每次比较裁剪前后位置和源编号，科学数组保持不变。本批依次核对150、50、100顶点与CPU半空间/闭区间盒参考完全一致；这是所记录质量、半径和边界的计数，不能代用于其他视图或场网格。最后关闭两项Enabled，恢复300顶点、512面。

   ![历史示例（原参数/原候选）：Agent原生开启平面裁剪；MCP逐顶点核对保留4、5、6](screenshot/N09-public-plane-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生同时开启平面和方框；MCP核对交集50顶点、编号4](screenshot/N09-public-intersection-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent原生仅保留方框裁剪；MCP核对100顶点及源编号1、4](screenshot/N09-public-box-GUI.jpg)

   按0.4先 **打包关联库**，再 **保存自包含工程** 和 **归档工程**；关闭本进程后，分别在新进程读取原工程、中文移动副本、ZIP解包副本。核对公共节点接口、所有输入、源编号和科学数组。Agent本批保存、归档及冷重开使用已登记操作的MCP/命令行复用；三个副本图、几何、50数组和48标注完全一致，移动/解包位置未取得外部节点库仍能求值。完整C05成图与其他案例验收分别记录。

   ![历史示例（原参数/原候选）：Computer Use观察已保存工程；裁剪恢复及MCP打包保存，完整成图另验收](screenshot/N09-public-restored-saved-MCP-observation.jpg)

### N10 QC Style Volume Fog

   ![历史示例（原参数/原候选）：Agent实际体积公共资产添加菜单](screenshot/N10-01-catalog.jpg)

   ![历史示例（原参数/原候选）：Agent实际两条Geometry接线；signed光学材质由MCP另行准备](screenshot/N10-02-fog-linked.jpg)

   维护者补验使用C13真实Pair1/Total带符号变形密度的独立Volume分支。Opacity Scale=0渲染全透明，40有非零alpha；本例Eevee光照下RGB偏暗，另用Cycles16 samples/640×360检查可见雾。下图是低采样诊断，参数和MCP渲染工具身份见索引，不作为C01用户点击或科研签名。48文件/3Dataset/66数组与两个内嵌节点库在新进程冷读通过，原工程和科学数组未变。

   ![历史示例（原参数/原候选）：MCP原生Cycles诊断：真实带符号变形密度雾，光学缩放40](screenshot/N10-fog-Cycles-40.png)

### N14 成对场全量/筛选CSV

   预期/需记录：两字段量/单位、全量有效体素539,448及原索引；筛选历史36,391/28,630/12,736只作本轮CSV行数待核实预期，交换列后筛选条件随角色保存。

### N16 撤销/重做

   历史维护者补验记录：候选deb9416中，C08 ESP源记录筛选、C09 AIM源记录筛选、C10真实IRC步进、C11 Mayer配对重绘、C12 ETS-NOCV Pair筛选均通过原生撤销、重做和再次恢复。重复操作按登记规则由MCP执行，显式保存操作前/后原生undo检查点；对象、节点、几何、标注、数据绑定及科学数组与完整场景快照严格一致。五个工程分别保存并正常关闭，再逐个新进程冷读通过，仅规范化portable路径。该记录不替代用户按上述菜单复做，也不填写独立科研签名；完整报告见验证索引 `C08_C12_native_undo_redo`。

### N18 保存/移动/冷重开与恢复

   若显示缓存确实丢失，先复制工程与完整配套数据作为恢复副本，只打开此副本。活动对象选需要恢复的**QC标量场视图**，在 **3D Viewport → N → QCBlender → 工程与诊断 → 重建显示缓存** 点击一次；等待真实作业完成，核对原数组、来源、单位、VDB绑定和显示几何。该操作从已保存科学数组生成缓存；缺科学数组应恢复原配套数据。示例为核附近诊断ESP，显示阈值30 hartree/e、56顶点/54面。

   ![历史示例（原参数/原候选）：Agent首次Computer Use点击重建显示缓存；MCP随后核对终态与全部科学数组、关联对象和几何](screenshot/N18-recovery-entry-GUI.jpg)

   ![历史示例（原参数/原候选）：Agent首次Computer Use在原生文件对话框选择同一Dataset的manifest.json并确认；MCP核对路径迁移与科学身份](screenshot/N18-relocate-dialog-GUI.jpg)

   ![Agent Computer Use确认同一manifest的损坏VDB测试副本；显示原生原因及路径，MCP核对原绑定不变（a3ed826）](screenshot/reliability/07-native-volume-error.png)

   恢复失败时记录原错误和日志，保留工程及输入。缺科学数组、不匹配manifest均须明确失败，不把它们当作物理零或新数据。历史维护者只在独立诊断副本暂存一份数组后执行拒绝检查，随后按SHA恢复；用户教程不要求删除配套数据。

   ![历史示例（原参数/原候选）：MCP缺科学数组请求留下的错误报告，Computer Use仅观察截图；数组随后按原SHA恢复，绑定未被替换](screenshot/N18-missing-array-MCP.jpg)

   恢复完成后仍在该唯一进程点 **工程与诊断 → 保存自包含工程** 另存；核对`.blend + .qcdata`后正常关闭。新进程冷重开，复核Dataset、数组、体积、节点和渲染。中文移动和归档解包继续按0.4逐个执行。此诊断工程55个配套文件、3个Dataset/108数组/1个VDB一致，冷读和重渲染像素一致；示例图仅为核区小网格片段。

   ![历史示例（原参数/原候选）：MCP保存恢复后的核区诊断ESP，原生Blender渲染；新进程冷读及像素一致，阈值30 hartree/e](screenshot/N18-recovered-diagnostic.png)

   历史N06–N08证据：加入公共资产后，先执行 0.4 的 **打包关联库**，再用 **保存自包含工程** 另存并归档。示例工程 `C04-public-nodes-packed.blend + .qcdata` 含两个内嵌节点库；三次冷重开分别使用新的唯一可见进程，MCP核对17个对象引用、7个Dataset、222数组、4个体积文件和117文件摘要。移动和解包时原相对路径的节点库不存在，内嵌资产仍求值正常。

   ![历史示例（原参数/原候选）：MCP另存并归档公共节点工程；Computer Use观察截图](screenshot/N18-public-nodes-packed-saved-MCP.jpg)

   ![历史示例（原参数/原候选）：中文移动副本冷重开，外部节点库不存在；MCP求值核对、Computer Use观察](screenshot/N18-public-nodes-cold-moved-MCP.jpg)

   ![历史示例（原参数/原候选）：ZIP解包副本冷重开，内嵌节点库和科学数组完整；MCP核对、Computer Use观察](screenshot/N18-public-nodes-cold-unpacked-MCP.jpg)

## 历史操作身份表

每个案例按下表逐步填写，可复制行；未实际执行保持 Not Run。所有路径相对本次批次，用户截图引用填写在相应操作步骤后。本文插图标为 Agent 操作示例，只证明图中所示动作与状态；未展示步骤继续保留待引用，不据此认定全教程 GUI Passed。

| 案例/步骤 | 活动对象/选择顺序 | 编辑器/面板/实际文字 | 参数原值→新值 | 预期→实际 | 结果 | 证据位置 | 执行者/方式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CXX/步骤号 | 待填写 | 待填写 | 待填写 | 待填写 | Not Run | 证据见各步骤 | 待填写 |

| 证据身份 | 可证明的范围 | 本次填写 |
| --- | --- | --- |
| User：用户实际操作 | 用户执行的明确点击与反馈；无反馈步骤不推定完成 | Not Run；截图/反馈待填写 |
| Agent Computer Use | 经授权在可见窗口实际点击；记录安装、进程、活动对象与截图 | Not Run；由根Agent记录 |
| MCP操作与数据核对 | 经授权调用真实 registered operators、原生文件对话框，核对数组/摘要/进程，记录真实窗口截图、渲染与新进程冷重开；写明实际调用及辅助范围 | Not Run；本轮结果见当前验证索引，历史技术范围见旧索引 |
| 原生脚本数据核对 | 维护者的自动化解析/数组/原生operator检查；独立绑定候选与命令 | Not Run；本表由当前批次执行者填写，维护者本轮结果见验证索引 |
| 独立科研复做与签署 | 独立使用者复做操作，并判断科学记录与成图适用性 | Not Run；姓名/日期留空 |

[当前批次验证索引](../acceptance/display-xyz-export-validation.json)记录显示精度、XYZ、显式CSV导出的实际候选、输入与工具身份；本轮新增入口的Agent点击、MCP/原生数据检查及工程冷读Passed；具体覆盖与旧截图复用范围见索引，独立使用者不从Agent记录继承签署。历史[cleanup-validation.json](../acceptance/cleanup-validation.json)、[tutorial-validation.json](../acceptance/tutorial-validation.json)、[tutorial-cu-validation.json](../acceptance/tutorial-cu-validation.json)保留原批次身份，仅对应原实现与原参数；历史Passed不继承到当前批次。用户截图占位由实际操作者补入。

## 历史二维图截图定位

以下图片仅绑定[历史点击索引](../acceptance/tutorial-cu-validation.json)及原候选/参数，保留旧工程追溯；不用于当前操作或0.2 Å结果验收。当前新建IR、剖面、paired、ESP面积、IRC/Mayer结果按0.5导出数据，已有工程图形不会自动删除，原Dataset仍可导出。

![历史示例（原参数/原候选）：Agent操作示例：选中密度线剖面创建正交相机，每侧留白5%](screenshot/00-04-camera.jpg)

![历史示例（原参数/原候选）：Agent操作示例：仅渲染密度剖面，EEVEE、1920×1080、100%、AgX；默认点光源与世界背景](screenshot/00-04-render.jpg)

![历史示例（原参数/原候选）：Agent操作示例：新进程冷重开密度剖面工程；4个Dataset、119个数组和1个体积文件另经MCP核对](screenshot/00-04-cold-final.jpg)

![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-ir-mode1](screenshot/C02-02-ir-mode1.jpg)

![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-ir-mode2-full](screenshot/C02-02-ir-mode2-full.jpg)

![历史示例（原参数/原候选）：Agent操作示例（候选92d498c）：C02-02-ir-mode3](screenshot/C02-02-ir-mode3.jpg)

![历史示例（原参数/原候选）：Agent点击：Sample field选颜色，采样101点；游标坐标由MCP设置](screenshot/C04-08-color-profile-dialog.jpg)

![历史示例（原参数/原候选）：Agent点击图幅宽度6与应用排版；MCP正面取景，CSV仍覆盖0–4 Å](screenshot/C04-08-color-profile-layout.jpg)

![历史示例（原参数/原候选）：Agent操作示例：独立密度剖面示例的游标起点，场单位 electron/bohr^3](screenshot/C04-08-cursor-start.jpg)

![历史示例（原参数/原候选）：Agent操作示例：独立密度剖面示例的创建参数，场单位 electron/bohr^3](screenshot/C04-08-profile-dialog.jpg)

![历史示例（原参数/原候选）：Agent操作示例：密度剖面结果，距离0–4 Å；隐藏其他图表文字以避免重叠](screenshot/C04-08-profile-final.jpg)

![历史示例（原参数/原候选）：Agent操作示例：导出剖面CSV，101个有效采样点；场单位electron/bohr^3](screenshot/C04-08-profile-csv.jpg)

![历史示例（原参数/原候选）：Agent操作示例：关闭IR谱显示层，谱线与所属文字同步隐藏；视口与渲染开关独立](screenshot/C05-06-ir-layer-hidden.jpg)

![历史示例（原参数/原候选）：Agent Computer Use启用范围并更新：36,391点；范围数值由MCP准备](screenshot/C07-IGMH-filter-GUI.jpg)

![历史示例（原参数/原候选）：Agent Computer Use交换轴并更新：相同数字应用于新轴后为28,630点](screenshot/C07-IGMH-swap-GUI.jpg)

![历史示例（原参数/原候选）：MCP恢复IGMH 36,391点范围并真实渲染；量名和单位另见上方面板截图](screenshot/C07-scatter-v2.png)

![历史示例（原参数/原候选）：Agent Computer Use应用中心范围：4bin、14.4784 Å²、19.7838%](screenshot/C08-area-center-GUI.jpg)

![历史示例（原参数/原候选）：Agent Computer Use切换并应用完整源区间：6bin、21.2676 Å²、29.0608%](screenshot/C08-area-source-interval-GUI.jpg)

![历史示例（原参数/原候选）：MCP配置相机，原生EEVEE渲染：40个源面积bin的原缩放柱形](screenshot/C08-area-v2.png)

![历史示例（原参数/原候选）：原生EEVEE渲染：三步归一化能量曲线及步2游标](screenshot/C10-curve.png)

![历史示例（原参数/原候选）：原生EEVEE渲染：曲线与源构型标注总览](screenshot/C10-overview.png)

![历史示例（原参数/原候选）：Agent Computer Use导入后自动生成1,2曲线；MCP核对当前第二步游标](screenshot/C11-fixed-pair12-GUI.jpg)

![历史示例（原参数/原候选）：Agent Computer Use将Atom B改为3并点击Plot Pair；MCP核对三点曲线和完整源值](screenshot/C11-fixed-pair13-GUI.jpg)

![历史示例（原参数/原候选）：原生EEVEE：源原子对1,3的三点归一化Mayer曲线，步2谷底游标](screenshot/C11-curve.png)

![历史示例（原参数/原候选）：原生EEVEE：左能量曲线、中央真实构型、右Mayer曲线；单位分别来自源记录](screenshot/C11-overview.png)

## 通用操作补充截图

![A03：Alpha 源 MO9 与资源预览](screenshot/alpha-readiness/ac6-MO9-parameters.png)

![A04–A05：等值 0.045 与完成的渲染](screenshot/alpha-readiness/ac6-render.png)

![A06：当前视图参数摘要导出](screenshot/alpha-readiness/ac6-summary-dialog.png)

![A09：中文路径新进程重开](screenshot/alpha-readiness/ac6-chinese-cold.png)
