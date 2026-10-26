# 14 Windows 0.1.0 预览发布

Triage: ready-for-agent
Status: claimed

## 目标与授权

2026-10-26 用户批准本任务计划：在独立发布分支实施，提交并通过 CI 发布 `v0.1.0` Windows x64 / Blender 5.1.1 Alpha Preview；不设为 latest。更新中英文 README、Release、Pages 和远程安装索引。公开附件为扩展 ZIP、完整 SOP/公开素材 ZIP（不含安装包）、index.json、发布清单、SHA256SUMS.txt。内部样本包、复现工程和报告保留在确切 CI artifact。

本次预览安装门槛改为 Agent 实际安装、MCP 与 Computer Use 验收；独立人工和科研签署仍为 Not Run，正式 v1 门槛不变。按当前交互规则先只读盘点进程，有用户会话时才请求保存关闭并记录恢复目标，随后串行验证。

专题 10/11 优先核实许可并复用现有 Ru/苯案例，保留原件。无法证实可公开时不发布、不删减专题、不改用新计算、不联系作者，列出具体缺件交用户决定；继续完成不受影响的工程工作。

## 实施与验收

1. 修复历史材料准备错误：当前 packages/README.md 不属于冻结科学输入，旧迁移摘要不应阻止恢复旧样本。保留冻结 ZIP、清单、回归及科学输入校验。
2. 核实素材/组件许可；构建完整教程附件和原生 Blender 索引，记录精确成员、大小与 SHA-256。
3. 候选 CI 完整通过后下载确切 run/artifact；实际 ZIP/远程安装、MCP、GUI、公开素材导入及保存冷重开通过。
4. CI 推广同一字节并公开 prerelease，显式调度 Pages；正式索引 `https://notes.psiqaq.cn/QCBlender/index.json` 指向固定 Release 附件。
5. 从公开地址核对附件摘要、正式索引安装、双语网站与恢复结果；如实记录 Passed / Failed / Not Run。

## Comments

- 初始源码 `d0a504496638cb95516b00be39ad797953f88dd7`，分支 `release/windows-preview-0.1.0`。当前没有 Release。候选 run 40319030172 在 stdlib 两项数据准备测试失败；Website run 40319030532 已成功。
- 本地通过 `python -m tools.dev_workflow --run-dir .tmp/runs/windows-preview-0.1.0/ci-baseline check --module test_validation_data` 复现同两项错误；报告 `.tmp/runs/windows-preview-0.1.0/ci-baseline/checks.json`。迁移记录保存 README 826 字节，当前说明为 1139 字节；其他 package/catalog/regression 记录字节摘要匹配。
- 定向回归先失败后通过：`.tmp/runs/windows-preview-0.1.0/ci-regression-red/checks.json` 与 `ci-fixed/checks.json`。新增检查覆盖包导航变化可恢复旧样本、冻结回归输入篡改仍拒绝；原两项测试均通过。远端完整候选 CI 尚未重跑。
- 许可核查见[本次来源核对](../../../docs/research/windows-preview-license-review-20261026.md)。已读原作者页面及原始附件，无明确覆盖现有 Ru/苯素材的公开教程分发依据；用户随后批准改用自建公开案例，见下条。
- 2026-10-26 用户明确答复“我没有额外授权，改用自建公开案例”。据此改用自有 P03 水二聚体构型的距离投影，以及解析正六边形初始构型生成的苯 CSGT all/π；不公开原 Ru/苯来源素材，保留历史输入与验收。
- 新投影实际 Multiwfn 运行及独立离散球面求交核对完成：61×41，849 个采样命中、1652 个未命中。旧 Ru 专用脚本“连续相交与采样命中数相等”假设在新数据有 1 个薄弦反例；保留该现象，按独立离散采样定义验证全部深度，不宣称连续表面精确性。脚本、实际日志和对照位于 `.tmp/runs/windows-preview-0.1.0/examples/`，待最终证据保全。
- 新苯 all/π 实际计算已正常结束，固定解析构型，轨道 17、20、21，经 Multiwfn 核实；两套各 240,630 点。参考张量和单位磁场响应一致，Aniso 误差不超过 2.23e-16。两组新公开案例的 MCP 导入、Computer Use 观察及便携工程冷读 Passed；最终 CI 候选安装尚待执行。
- 发布工具定向测试（`test_candidate_artifacts`、`test_release_candidate`、`test_preview_release`）Passed；报告 `.tmp/runs/windows-preview-0.1.0/preview-boundaries/checks.json`。网站公开 Release 元数据边界测试 4 项 Passed。完整候选 CI、真实安装、GUI 与最终发布均 Not Run。
- 用户已回复 Blender 关闭，并要求将“先调查进程，再在确有用户会话时请求关闭”写入规则偏好。本次 `session list` 实际返回空进程列表；规则入口和交互文档已同步。用户未指定原工程，不从最近文件猜选恢复目标。

- 教程 80 张图全部视觉复查：裁剪区域解码像素一致；5 张局部选择图重新构图、8 张科学显示图改为新案例。总计 49,091,794 → 20,945,908 字节。旧图和完整原图保全，逐图身份见产物入口。发布工具 7 项扩展边界测试 Passed，最终远端候选和发布仍待执行。
- 候选 run `40338016490`（源码 `cf2a27a`，扩展 SHA-256 `478c9d9a1959018ea24904868cbc5c2f0bc17afd126eb8df48b799c95b654eaf`）完整 CI Passed；实际 ZIP 安装、P01/投影/AICD 与冷重开 Passed。通过 UI 添加临时远程仓库并下载相同字节后，科学运行时检查 Failed：worker 的 `--factory-startup` 丢失新增仓库命名空间，报 `extension repository "repository" doesn't exist`。因此该候选不发布。
- 修复 worker：从自身安装文件定位本地仓库，仅在出厂配置缺少对应仓库时补入，不加载其他用户插件或远程地址。保留启用后的扩展来源一致性检查。失败安装的隔离开发副本经真实后台 Blender 诊断和 P01 导入 Passed（`.tmp/runs/windows-preview-0.1.0/worker-fix/`）；新增候选 CI 的自定义仓库 worker 验收，最终新包仍待 CI 及安装复验。
- 最终候选 run `40341330234`、artifact `12659470998`、源码 `bec0877d025d95a291e99efdbc09fdad9c423be6` 完整 CI Passed，含新增远程仓库 worker 检查。扩展 SHA-256 `020efb1652c7f1ed9309d032bfd454898db95a61ec099c5109f43ad037006642`。最终包实际 ZIP/暂存远程安装、137 文件字节比对、科学运行环境、P01/投影/AICD、14 数据对象冷重开与中文路径教程检查 Passed。绑定身份的公开门禁见 `validation/agent/acceptance/releases/v0.1.0/gates.json`；正式发布、Pages 与正式索引安装尚待执行，独立人工及科研验收 Not Run。
