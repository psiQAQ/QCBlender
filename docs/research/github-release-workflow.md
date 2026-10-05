# QCBlender GitHub 发布流程

核查日期：2026-10-05。本文记录一手源码与官方文档的事实，以及已确定的 Alpha 发布设计；远端运行状态由对应任务和候选发布记录维护。

## 采用的发布方式

QCBlender 使用单个自包含 Blender 扩展，首发 Windows x64 / Blender 5.1.1，必要科学 wheels 随包，NumPy/OpenVDB 使用 Blender 自带版本。该边界来自 [ADR 0001](../adr/0001-self-contained-extension.md)，不能用参考项目的运行时架构替代。

首个 Alpha 的 manifest 为 `0.1.0`，注释标签为 `v0.1.0`，GitHub Release 标记 `prerelease=true`。版本、tag 与预览 channel 分别校验；预览不设为 latest。GitHub 的 `prerelease` 是独立布尔字段，草稿和预览不能成为 latest；Blender 扩展 manifest 要求语义化版本。依据：[GitHub Release API](https://docs.github.com/en/rest/releases/releases#create-a-release)、[Blender 5.1 扩展 manifest](https://docs.blender.org/manual/en/5.1/advanced/extensions/getting_started.html)。

候选流程：最终版本源码进入 main → 核心 CI 与干净 Windows 候选构建 → 按 run ID 下载确切 artifact → 本地技术资格与人工短 SOP → 注释标签绑定该 run 的提交 → 推广同一附件字节为 GitHub 草稿 → 实际操作者明确批准 → 维护者在 GitHub UI 公开预览。发布作业只验证和上传，不重新构建或压缩附件。

## 参考项目与源码身份

| 来源 | 本次核对身份 | 核对位置与事实 | 采用部分 |
| --- | --- | --- | --- |
| MolecularNodes | 子模块 commit `999b0b5e8f576c83b3dd854819303fe00c0507a0` | `.github/workflows/release.yml` 第 4–41 行：`v*` 标签、macOS/Blender 5.2 构建、draft Release；`upload.yml` 第 4–38 行：`published` 后下载 ZIP 并上传扩展平台 | 草稿与公开分阶段，同一已发布 ZIP 进入后续平台流程 |
| ChemBlender | 本地 HEAD `2e94f90419aab186f522fb3b701746839ee8c5c4`，`.github` 工作区无修改 | `extension-package.yml` 第 16–210 行：核心 stdlib 测试、Windows 干净构建、隔离安装与冷读、artifact；`extension-release.yml` 第 4–171 行：手动 verify，精确注释 tag/run/artifact；第 173 行起：写权限分离、原产物推广与附件摘要核验 | 精确候选身份、校验与写权限分离、发布阶段不重建 |
| BlenderKit 官方发布 action | 2026-10-05 读取公开 `main` 的 `action.yml`，未作为本项目依赖 | `release_stage` 支持 alpha/beta/rc/gold；下载 build artifact 后重新 ZIP，创建 draft，并设置 prerelease | 候选与发布阶段分离、预览状态显式记录 |
| Sverchok | 2026-10-05 读取官方 README 与 Releases；未读取到发布 workflow | README 明确 Blender 兼容版本和 legacy 安装方式，说明版本 ZIP 与旧工程的用途 | 在下载说明中明确兼容环境、安装包身份和旧工程边界 |

固定源码链接：

- [MolecularNodes release.yml](https://github.com/BradyAJohnston/MolecularNodes/blob/999b0b5e8f576c83b3dd854819303fe00c0507a0/.github/workflows/release.yml)、[upload.yml](https://github.com/BradyAJohnston/MolecularNodes/blob/999b0b5e8f576c83b3dd854819303fe00c0507a0/.github/workflows/upload.yml)。本地资料为主检出的 `submodules/MolecularNodes/.github/workflows/`。
- [ChemBlender extension-package.yml](https://github.com/psiQAQ/ChemBlender_2_x/blob/2e94f90419aab186f522fb3b701746839ee8c5c4/.github/workflows/extension-package.yml)、[extension-release.yml](https://github.com/psiQAQ/ChemBlender_2_x/blob/2e94f90419aab186f522fb3b701746839ee8c5c4/.github/workflows/extension-release.yml)。本地资料为 `D:/workspace/ChemBlender_2_x/.github/workflows/`；两份文件 SHA-256 分别为 `45772ca9b888a4230e4ecc464d3575aa8e6bd2ab51df97813fad3c0f2f380690`、`55966c51f82d40b56b5dd66e4362e99d803f2b687eb3a9eb74dc8a0e8b3af0f5`。
- [BlenderKit build action](https://github.com/BlenderKit/blender-addon-build/blob/main/action.yml)、[release action](https://github.com/BlenderKit/blender-addon-release/blob/main/action.yml)。链接使用上游分支，本次观察不保证后续内容不变。
- [Sverchok README](https://github.com/nortikin/sverchok/blob/master/README.md)、[Releases](https://github.com/nortikin/sverchok/releases)。本次只依据实际读取的安装与兼容说明，不推断其 workflow 行为。

参考流程的适用限制：MolecularNodes 的 Blender 5.2、macOS、浮动 actions、未显式 tag 的 Release 下载和自动扩展平台上传不属于本轮设计；QCBlender 下载须固定 tag/asset 并复核摘要。ChemBlender 当前为 wheel-free Viewer，不能套用其空 wheel 清单及体积预算。BlenderKit release action 会重新 ZIP，且使用浮动旧版 actions；本项目继续使用自身构建工具及完整 commit SHA 固定的 GitHub 官方 actions。Sverchok 的 legacy/source ZIP 安装方式不能代替自包含扩展安装包。

## 候选构建与草稿推广契约

`extension-package.yml` 产生候选 artifact `qcblender-candidate-{version}-{source_commit}`。候选附件包含扩展 ZIP、许可合格 v2 样本 ZIP、精简公开复现材料 ZIP、`release-manifest.json` 与 `SHA256SUMS.txt`；完整技术报告在同 artifact 的 `reports/` 中。manifest 保存 version/channel/source_commit/candidate_run_id/product_tree、支持环境、附件大小与 SHA、报告状态与 SHA。artifact ID 由上传响应和发布记录绑定，不放进自包含 artifact 形成循环身份。

`extension-release.yml` 仅从默认分支手动调度，接口为 `tag`、`candidate_run_id`、`dry_run`；默认 `dry_run=true`。候选版本在构建前固定；注释 tag 指向同一 run 的 `head_sha`。先验证 annotated tag、main 可达性、manifest/tag 版本、workflow/run 提交与成功状态、唯一未过期 artifact、源码身份、附件/报告摘要及发布清单。缺失、过期、摘要变化或来源错误直接失败，不根据 latest 运行选择产物。

验证 job 保持 `contents: read`，仅访问 artifact 时增加 `actions: read`。草稿写 job 独立授予 `contents: write`，使用 `GITHUB_TOKEN`，按 tag 串行且 `cancel-in-progress=false`。写 job 声明受保护的发布 environment；仓库管理员需要真实配置规则，YAML 中声明 environment 不证明 reviewer 已配置。依据：[GitHub deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)。

发布报告保存明确的 run ID、artifact ID、tag 提交、每份附件摘要和校验状态。所有可推广附件只复制原始字节；Release notes 取当前版本的已审阅文档，不根据提交列表推导科研功能或支持范围。

由 `GITHUB_TOKEN` 产生的普通事件不会启动新的 workflow，`workflow_dispatch`、`repository_dispatch` 等有指定例外。因此维护者在 GitHub UI 公开草稿，既落实人工批准，也保留未来正式版的 `release.published` 扩展平台链路。依据：[GitHub workflow 触发规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。

## 公开门禁与 SOP

Alpha 技术门禁包括核心测试、固定科学环境与真实必要样本、本次科学回归、Blender 原生 validate/build、离线隔离安装、注册/注销和冷重开、源码/ZIP/wheel 摘要一致。公共 CI 显式选择可公开回归集合；完整本地资格单独记录，必要样本缺失或 required skip 不能报告 Passed。Alpha 不替代完整独立科研接受。

所有随包组件都需要可审查的许可材料。当前 [THIRD_PARTY](../../THIRD_PARTY.md) 记录 IOData/GBasis 包元数据与根 LICENSE 的声明差异，以及 SciPy/OpenBLAS/GCC runtime 随包材料；保留真实差异并完成复核，未完成时保持本地候选。Alpha 不提供许可豁免。

公开样本依据 [SOURCES](../v1-acceptance/SOURCES.md) 第 157–183 行与 [样本机器清单](../v1-acceptance/tutorial-samples.json)。仅推广许可合格的 v2 样本及由公开输入生成的复现材料。P02/S08 及未知许可原件和相关 `.blend/.qcdata` 不加入公开附件；SOP 保留原站获取、SHA 核验及剩余限制。

人工 Alpha 短 SOP 由实际操作者执行：记录 ZIP/样本 SHA → Windows x64 / Blender 5.1.1 新清洁配置离线安装确切 ZIP → 导入 P01、创建固定 Alpha MO9 并核对原子/轨道/量名 → 调整等值面、保存 PNG 和自包含 `.blend + .qcdata` → 正常关闭 → 中文路径移动工程 → 新进程冷重开并核对科学记录/节点/视图/来源 → 填写结果和针对该 ZIP 的公开批准。修复后重新构建候选，重做受影响步骤。

本轮 Alpha 准备使用 `.scratch/alpha-readiness/`。正式 [v1 发布机制](../../.scratch/v1-acceptance/issues/03-release-mechanism.md) 仍依赖独立人工任务 02；完整签署标准见 [SOP 3.3](../v1-acceptance/SOP.md#33-最终签署)。正式 v1 全部人工必需项通过后再领取，不将 Alpha 准备任务作为其完成证据。

首次 Blender Extensions 上架与后续自动上传属于正式发布后续，不在本轮配置 token 或上传。官方要求先安装测试，再由 Blender ID 上传并等待审核；更新 API 使用上传 ZIP 和认证 token。依据：[Blender 5.1 上架说明](https://docs.blender.org/manual/en/5.1/advanced/extensions/getting_started.html)、[Blender CI/CD](https://developer.blender.org/docs/features/extensions/ci_cd/)。上传成功、等待审核和已经上架分别记录。

## 失败恢复与验证状态

- tag 移动、run 不成功、artifact 过期、版本/源码不符、报告缺失或 SHA 不符：停止，不取其他候选、不自动重建。
- 草稿创建或上传中断：保留真实错误和 draft；重试校验同一身份，只补缺失附件，现有附件必须摘要一致。禁止 `--clobber`。
- 已公开且身份完全相同：记录已完成；内容不同：失败并创建新 PATCH 候选，不移动旧 tag 或替换公开 ZIP。
- 测试覆盖错误 run/tag/版本、过期 artifact、改变的 wheel、陈旧证据、缺许可、重复/额外 ZIP 成员和草稿附件摘要错误。
- 本次参考代码与官方文档核查：Passed。实际远端 CI、草稿创建、人工试装、公开批准、公开下载摘要复核与 Blender Extensions：Not Run；由各实施任务记录实际证据。
