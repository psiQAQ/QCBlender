# 核心优化、SOP 与 GitHub Alpha 发布

Triage: ready-for-agent
Status: claimed

## 目标与授权

用户于2026-10-05批准实施，以main@9bfa682为基线。保持单扩展、Windows x64、Blender 5.1.1及现有依赖版本/锁文件内容。授权本地commit、ff-only合入main、注释archive标签及保全后正常移除本批工作树。远端步骤须有对应具体授权；公开Alpha须经真实人工试装及明确批准。独立科研签署不能由Agent代签，正式v1发布任务继续受既有人工验收前置约束。

## 实现契约

1. 科学Dataset序列化数组总量上限1 GiB，包含保留源数组、替换后的float64场值/bool有效域及.npy header；按manifest记录计数。加载先检查全部路径/总大小再加载；保存/求值/VDB/缓存复制/归档一致。求值工作内存估算计入全部驻留输入数组，不宣称是全进程严格内存限制；不扩大mmap/物化重构。
2. 科学指纹包含evaluate/readers/data源码及GBasis/IOData/NumPy/SciPy身份，外层继续绑定manifest/grid/参数/Blender版本。旧缓存自然失效，不使用仓库HEAD，不因文档或显示层变化失效。
3. 生成入口自动使用独立异步资格检查，再打开参数对话框。检查无网格分配，使用现有prepare判定方法/ECP/基组/占据/密度矩阵；报告已知不支持与环境/完整性失败有区别。资格缓存绑定manifest和科学指纹，清理于冷重开/注销；对象或绑定变化不自动打开对话框。draw只消费轻量预览，显示网格/点数/结果大小/预算/拒绝原因，后台在cachehit与计算前复检。
4. 现有导出新增SUMMARY，生成view-summary.md与metadata.json。科学来源/方法/基组/构型/物理量/单位/轨道/自旋/网格/有效域与实时modifier/socket/material色带输入分开。自定义图或缺字段标partial/unverified并列原因，不填默认值，不宣称完整渲染等效。目录/暂存/取消/SHA流程复用，旧CSV和科学schema保持。
5. 公开核心CI显式stdlib/public-science集合，无tests/data/local依赖；真实IOData/GBasis和独立cubegen/Fortran参考必须执行，必要缺失及skip失败；完整本地suite默认行为不变。Windows-2022和官方Blender5.1.1；现有锁下载、隔离安装、节点/安装/冷读报告。构建只核验源码锁，不重写。版本来自manifest；Alpha0.1.0/tagv0.1.0，预览channel与prerelease独立。
6. GitHub候选构建与发布推广分离。候选metadata保存version/channel/source_commit/run_id/文件SHA/报告，artifact_id由上传元数据和发布记录绑定，不在自包含artifact内循环引用自身ID。发布接口tag/candidate_run_id/dry_run(default true)，仅默认分支调度；核对注释tag/main可达性/版本/run.head_sha/成功workflow/唯一未过期artifact及确切包身份。只推广原ZIP，草稿写权限独立，串行不取消；人工在UI公开prerelease，不上Blender Extensions。附件重试仅补缺失，摘要冲突失败，禁止clobber或移动旧tag。
7. 组件许可复核及人工短SOP是公开门禁。仅发布可分发v2样本和由公开输入生成的工程，P02等未知许可输入/相关工程排除。当前未知许可差异须保留真实状态，不以Alpha豁免。

## 候选与CI交接

候选workflow名extension-package.yml，artifact名qcblender-candidate-{version}-{source_commit}。候选ZIP、v2样本ZIP、精简复现材料ZIP、release-manifest.json与SHA256SUMS.txt构成发布附件；本次完整技术报告在同artifact reports/中。manifest明确当前candidate_run_id、source_commit、product_tree、平台、版本、文件大小/SHA与报告状态/摘要。发布workflow名extension-release.yml，从确切run的artifact读取，不取latest、不重新压缩附件。

## 验收

小预算边界与512³无大型分配拒绝、fingerprint失效、方法/ECP/基组/占据/DM资格、取消与对象变更、实时摘要及partial、自包含保存/中文移动冷读、六固定视觉和相关原生GUI/Undo/Redo，分别记录Passed/Failed/Not Run。Standards/Spec分轴复审。公开CI运行、草稿创建、人工试装、公开批准及下载摘要复核独立记录；工作流存在不代表远端已执行。

## 顺序与归属

01核心科学串行；02摘要与03CI独立并行；04发布研究；05发布工作流在03/04完成后领取；06文档/SOP在01/02/03/05完成后；07主Agent串行综合资格；08本地归档；09远端候选CI；10人工试装/Alpha公开。01产品科学和generate UI归主Agent，02仅导出/摘要/editor导出入口，03构建工具/manifest/package workflow，05发布验证器/release workflow。共享Blender及最终证据索引由主Agent维护。

## Comments

当前主仓库工作区干净。既有reliability任务resolved；本批不改其历史身份，不重复实施流式摘要实验或扩大性能重构。
