# 正式版发布流程与同步修改清单

本页用于准备正式版、调整发布通道，以及核对 Release、网站和 Blender 安装入口是否一致。流程核对基线为 2026-10-27、提交 `1f618d9`；执行时先对照当前代码。本文记录后续工作，不表示正式版门禁已通过，也不授予提交、推送、公开发布或平台上传权限。

当前 `v0.1.0` 是已公开的 Alpha Preview。推荐为正式版使用新的版本和注释标签，保留旧预览版及其附件、证据。现有 [v1 验收规格](../../.scratch/v1-acceptance/spec.md)以 `v1.0.0` 为目标；实际版本由当次发布任务确定。

## 1. 确认发布条件和目标

先读取 [独立人工验收任务 02](../../.scratch/v1-acceptance/issues/02-human-acceptance.md)和 [发布机制任务 03](../../.scratch/v1-acceptance/issues/03-release-mechanism.md)，按前置关系推进。正式 v1 所需人工、科研、许可及包资格检查全部通过后，才推进正式发布；预览版曾获准使用的 Agent 安装替代门禁仅适用于该次预览。Agent 可整理实际反馈和证据，不能代填独立人工或科研通过。

在当次任务中确定版本、支持平台和 Blender 范围、公开附件、实际操作者，以及已获授权的外部动作。现有已验证范围为 Windows x64 / Blender 5.1.1；改为正式版不会自动扩大兼容范围。新版本继续复用 [开发流程](development-workflow.md)、[完整构建与资格](../DEVELOPMENT.md)和 [Blender 交互规则](blender-interaction.md)。

正式版的发布目标为：

| 对象 | 正式版目标 | 核对方式 |
| --- | --- | --- |
| manifest 与 tag | manifest 为当次版本，注释 tag 为 `v<版本>`，指向确切候选源码提交 | 本地及远端 tag、候选清单与 ZIP 内 manifest 一致 |
| 候选通道 | 新增明确的正式通道，例如 `stable`；该值目前尚不受支持 | 构建、清单、推广和网站使用同一通道契约 |
| GitHub Release | 公开后 `draft=false`、`prerelease=false`，明确设为 Latest | Release API 与 `/releases/latest` 均指向当次版本 |
| 网站和索引 | 中英文内容显示正式版，附件 URL 固定到该版本 | 网站构建、在线内容和下载字节一致 |
| 验收结果 | 每项结果对应确切候选和实际执行者 | `Passed / Failed / Not Run` 分开记录 |

GitHub 的预发布标记与版本字符串相互独立；草稿和预发布不能设为 Latest。正式版公开时需明确设置 Latest，而不是仅修改标题中的“Alpha”。规则来源：[GitHub Release API](https://docs.github.com/en/rest/releases/releases#create-a-release)（核对日期：2026-10-27）。

完成标志：发布任务列明版本、范围、前置证据和授权；缺失门禁有明确责任人，未执行项保持 `Not Run`。

## 2. 先补齐正式版支持

**当前自动公开入口只支持 `v0.1.0` 预发布，不能直接用于正式版。** 按下表改造后再生成正式候选；不要通过把 `publish_preview` 改为 true 或手动翻转旧 Release 标记来绕过改造。

表中路径均相对仓库根目录；“同步修改”指后续正式发布实施时需要检查和调整的对象，本次文档不修改这些实现。

| 对象与当前入口 | 正式版需要同步的内容 |
| --- | --- |
| `qcblender/blender_manifest.toml` | 更新版本；保持已验证的 `platforms`、`blender_version_min/max`，扩大范围时补相应验证。由 manifest 派生包名，检查 `tools/package_identity.py` 等读取方，避免另写版本常量。 |
| `.github/workflows/extension-package.yml`、`tools/run_candidate_ci.py`、`tools/candidate_artifacts.py` | 当前只接受 `alpha/preview`。增加正式通道并贯通候选与公开清单；继续使用锁定依赖、干净 Windows 构建、完整节点资产和原始报告。依赖变更另按授权处理，不为改通道重写依赖锁。 |
| `tools/release_candidate.py`、`tools/verify_release_gates.py` | 当前公开条件限制版本为 `0.1.0`，写入时固定 `prerelease=true`、`make_latest=false`。增加正式候选、草稿及公开状态的校验，要求正式人工/科研、许可及公开批准门禁；保留旧预览规则和历史证据。`draft_readiness` 当前只检查许可，不等于正式版可公开。 |
| 候选与门禁 schema | 当前 v2 候选被代码当作 preview，含 `agent_preview_installation`；`independent_alpha_installation` 也不表达完整 v1 验收。明确正式字段或新 schema 及兼容规则，不把旧 Alpha 试装直接解释为正式门禁。构建时尚未完成的人工结果保留原值，后续以绑定同一候选的独立证据记录补充，不修改已生成附件。 |
| `.github/workflows/extension-release.yml` | 参数化写死的 `docs/releases/v0.1.0.md`，区分预览与正式草稿路径，维持默认 dry-run、写权限隔离、受保护的 `release` environment 和按 tag 串行执行。若新增 CI 正式公开动作，应与预览动作分开，公开前重新核对全部正式门禁；同步任务 03 中的公开方式。 |
| `tools/tutorial_bundle.py`、`tools/repository_index.py` | 保留完整教程、不重复包含安装包、公开输入许可和组内相对引用校验。索引仍由 Blender 官方工具生成，下载地址固定到新 tag 的附件；同步候选端与发布端的文件名、清单及摘要断言。 |
| `website/scripts/published-release.mjs`、`.github/workflows/pages.yml` | 当前固定 `releaseTag='v0.1.0'` 且拒绝 `prerelease=false`，`QCB_RELEASE_TAG` 不能单独覆盖此限制。增加明确的正式版本/通道选择和校验，保持附件集合、摘要及已部署索引保护；保留从发布后显式调度 Pages 的路径。 |
| `website/scripts/prepare-docs.mjs`、`website/src/data/copy.ts`、`website/src/components/DownloadsPage.astro` | 生成数据当前从 `current-install.json` 读取 channel；双语文案和下载徽标还含硬编码 Alpha。让版本、通道、状态和固定下载地址保持一致，覆盖首页、兼容说明、页脚与下载页。生成的 JSON/HTML 通过脚本重建，不直接编辑。 |
| `tests/test_candidate_artifacts.py`、`tests/test_release_candidate.py`、`tests/test_preview_release.py`、`website/scripts/published-release.test.mjs` | 保留预览路径测试，增加正式候选成功路径、缺人工/科研或批准的拒绝路径、版本/通道/附件摘要不一致、草稿与正式公开状态、正式网站解析及默认发布目标切换。仅把旧断言的 true 改成 false 不足以验证通道隔离。 |

网站切换应分两步：先让实现能识别旧预览和新正式版，仍默认服务已公开预览；正式版公开并可验证后，再激活新版本。这样，准备工作合入 main 时的自动 Pages 构建不会去下载尚未公开的附件，也不会擦除既有安装入口。

完成标志：正式通道的定向检查通过，旧预览路径保持可核验；任何尚未实现的正式参数均明确记录，不能当成已有命令使用。

## 3. 同步用户说明和交付入口

| 入口 | 同步内容与时机 |
| --- | --- |
| `README.md`、`README_zh.md` | 正式版本、支持范围、固定 Release 链接、安装包和教程包名称；保留 ZIP 安装与远程仓库安装两条完整路径。公开前用准备状态，公开后核对实际可下载。 |
| `docs/releases/<tag>.md` | 为新版本新增发布说明，写明相对上一版的变化、兼容范围、安装/升级、已知限制、验证范围和附件用途；保留旧版发布说明。 |
| `validation/human/SOP.md`、受影响专题、`validation/README.md`、`validation/shared/install/README.md` | 更新当前安装包和教程分发说明；UI 或操作变化时同步步骤与真实截图。保留科学量中的 alpha/beta、自旋术语及历史版本叙述，避免全库替换“Alpha”。 |
| `validation/agent/current-install.json`、`validation/shared/install/` | 最终确切包通过验证后更新版本、channel、源码、大小、SHA 和证据入口。当前可下载包与日常 Blender 已安装版本分开记录；仅更新包入口不代表已执行日常安装。 |
| `validation/agent/acceptance/releases/<tag>/` | 新建当次候选、门禁、实际安装和发布后核验记录，绑定 run ID、artifact ID、source commit、扩展 SHA 及证据文件摘要。保留 `v0.1.0` 的原始记录。 |
| `docs/ARTIFACTS.md`、`docs/CHANGELOG.md`、当次 `.scratch/` 任务 | 分别更新产物位置、用户可见变化、实际完成状态；通过链接复用证据，不复制第二套状态。 |
| `docs/DEVELOPMENT.md` | 正式流程实现后补充当前接口及资格要求，保留明确标注的 0.1.0 历史流程；`docs/research/github-release-workflow.md` 作为带日期的研究依据，不把旧观察改写成新结果。 |

原则上沿用五个公开附件：`qcblender-<版本>.zip`、`qcblender-tutorial-<版本>.zip`、`index.json`、`release-manifest.json`、`SHA256SUMS.txt`。公开集合变更必须同时调整打包、推广、网站校验及文档；内部报告、受限输入和复现工程继续按既有边界保存。

完成标志：中英文当前入口使用同一版本和支持范围；历史材料保留原身份，所有新链接有明确目标。

## 4. 构建并验收确切候选

1. 将正式版实现、版本、教程和发布前说明收敛到候选源码。按已批准流程提交并合入 main，在干净 Windows CI 中生成正式通道候选。保留本次所需的技术资格和公开科学检查；完整本地及独立验收按 v1 规格执行，不用公共 CI 代替。
2. 记录成功 workflow 的 `head_sha`、run ID 和唯一未过期 artifact ID，下载确切 artifact，核对候选清单、扩展/教程 ZIP、索引、报告及依赖摘要。按 run ID 选择，不能选择“最近一次”碰巧成功的运行。
3. 用这份 ZIP 实际完成所需安装、运行环境、关键案例、MCP/GUI、保存与新进程冷重开；按照 v1 规格取得独立用户反馈、科研接受和所需外部视觉对照。正式索引尚未公开时保留预发布测试身份，公开后再补正式地址验证。
4. 在新版本证据目录记录实际结果。Agent 整理操作者反馈，不要求用户重复填写技术摘要表。修复导致源码、输入或包变化时生成新候选，重新绑定门禁；同身份且未受影响的有效结果按开发流程复用。
5. 获准创建和推送发布标签后，将新的注释 tag 指向该候选的确切源码提交。门禁记录、发布说明可以另在默认分支维护；标签身份以候选源码为准，不能误指向后续记录提交。

完成标志：tag、run、artifact、ZIP 和证据身份可逐项对应；任一必需项 `Failed / Not Run` 时，正式公开仍受阻。技术 dry-run 通过不等于所有正式发布门禁通过。

## 5. 创建草稿，批准后公开并部署

默认沿用现有正式任务设计：**CI 核验并创建草稿，实际操作者复核该包并明确批准后，维护者公开正式版。** 若当次改为 CI 公开，先实现受保护的正式动作并同步任务 03，不能复用预览特例。

1. 正式通道改造合入默认分支后，先运行发布 dry-run；核对注释标签、源码可达性、候选身份、所有报告和正式门禁。`gates_record` 指向默认分支内本版本记录，证据按其相对路径和摘要核对。
2. 按已批准流程创建该版本草稿并上传原始五附件，逐项下载复核 SHA。发布阶段只复制确切 CI 字节，不重建、不重压缩；同名不同摘要直接失败。
3. 实际操作者复核草稿所含确切 ZIP，维护者确认公开批准后发布：取消 **This is a pre-release**，选择 **Set as latest release**。若使用已实现的 CI 正式动作，对应目标为 `draft=false`、`prerelease=false`、`make_latest='true'`。
4. 核对公开 Release 后，激活网站的正式版本目标，并显式调度 Pages，携带相同 `release_tag`。`GITHUB_TOKEN` 产生的普通事件通常不会启动新 workflow；不能仅等待 `release.published` 自动接续，`workflow_dispatch` 是官方允许的例外。[GitHub workflow 触发规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)（核对日期：2026-10-27）。

以下为改造完成后的核对和 Pages 调度示例。使用 PowerShell，工作目录为仓库根目录，已安装并登录 `gh`；先把版本替换为当次已批准版本。最后一条是外部动作，仅在已获部署授权、网站选择器支持该 tag 且 Release 已公开时执行。

```powershell
$repo = 'psiQAQ/QCBlender'
$version = '<当次版本>'
$tag = "v$version"
gh release view $tag --repo $repo --json tagName,isDraft,isPrerelease,assets,url
gh api "repos/$repo/releases/latest" --jq '.tag_name'
```

预期：目标 Release 已公开且不是预发布，五附件完整，Latest 返回 `$tag`。任一不符时先修复对应步骤。

```powershell
gh workflow run pages.yml --repo $repo --ref main -f "release_tag=$tag"
```

完成标志：正式 Release 和对应 Pages 运行都成功，记录实际提交及 run ID；只有草稿创建成功或命令调度成功时，不能标记发布完成。

## 6. 从用户入口验收并收尾

- 从正式 Release 下载五个附件，与原 CI 候选逐字节或 SHA 核对；访问 `/releases/latest` 确认正式版本，检查仓库首页 Releases 区域的可见入口。
- 检查中英文首页、下载页、语言切换和安装说明，确认版本、通道、兼容范围及两种下载目标一致。站点成功部署不代替实际浏览器验收。
- 核对 `https://notes.psiqaq.cn/QCBlender/index.json` 与该 Release 的原始索引相同，索引中的包版本、平台、兼容范围、大小、SHA 与固定附件 URL 均匹配。
- 在隔离 Blender 配置中从正式 ZIP 和正式远程仓库完成安装/同步，检查科学运行环境及必要关键案例。验证已有预览用户的升级路径和工程兼容性；具体覆盖按实际改动确定。日常安装只有在另有授权且真实执行后才能记录 Passed。
- 更新第 3 节的当前入口，按 [存储维护规则](storage-maintenance.md)保全原始材料、工程和证据；提交、快进合并、本地归档及推送按当次授权收尾。

完成标志：发布、部署、公开字节、浏览器及两种安装路径均有当次结果，未完成项有明确记录，正式 v1 的必需门禁没有被预览版证据替代。

## 7. 失败处理与扩展平台边界

草稿上传中断时，核对同一候选后继续补齐缺失附件；已有附件摘要不同则停止，保留错误和草稿。已公开包需要内容修复时发布新修订版本，保持旧 tag 和附件身份。Pages 失败时保留已公开包和最后有效网站/索引，修复部署后再做公开入口验收；Release 元数据拉取失败时不清空既有安装入口。

Blender Extensions 上架是独立阶段，沿用任务 03：首次由 Blender ID 上传并等待审核，后续自动上传另行配置授权与密钥。必须上传同一已核验 ZIP，并分别记录上传成功、等待审核和已上架；GitHub 正式版发布成功不代表平台已经收录。
