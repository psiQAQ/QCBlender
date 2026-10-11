# Agent 校验入口

这里维护可重复执行的技术检查、文件身份和清理清单。[本轮整合检查](VALIDATION.md)记录主分支上的实际结果。人工学习从 [人工 SOP](../human/SOP.md) 开始；本地限定的优化、频率和 NBO 案例见 [LOCAL-CASES](LOCAL-CASES.md)。[COVERAGE](COVERAGE.md) 保留旧 A/C/N/X/P1 编号与当前入口的对应关系。

当前安装包定位在 [current-install.json](current-install.json)，实际安装文件为 `validation/shared/install/qcblender-0.1.0.zip`。公开输入在 `validation/shared/data/public/`，本机资料在 `validation/shared/data/local/`，回归输入在 `validation/shared/data/regression/`。冻结样本 ZIP 位于 `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip`；其原始清单仍为 `validation/agent/v1-acceptance/tutorial-samples.json`。

> 冻结样本包：已经固定内容和文件身份的样本 ZIP，整理目录时保留原始字节。

## 选择检查范围

候选验收、GUI 操作登记和固定基准见[技术验收索引](acceptance/README.md)；冻结样本清单、来源和历史截图见[v1 材料](v1-acceptance/README.md)。两组材料由 `docs/` 迁入，历史机器记录的原路径按[迁移对应关系](acceptance/README.md#历史路径与当前位置)定位。

| 变化范围 | 执行入口 | 能证明的范围 |
| --- | --- | --- |
| 文档、相对路径、公开打包 | [verify_workspace.py](tools/verify_workspace.py) | 路径、链接、公开资源集合和教程文件边界；准备阶段允许图片空位，`--require-images` 要求全部图片存在 |
| 本地输入迁移 | `tools/local_inputs.py`、`tests/test_local_inputs.py` | 索引解析、必要文件与内容身份；缺少必要输入应失败 |
| 冻结样本 ZIP | `tools/candidate_artifacts.py check-samples` | 原始 ZIP 身份、30 个公开输入、来源清单和 P02 排除 |
| 公开科学能力 | `tools/run_science_tests.py --suite public-core` | `tools/test_profiles.py` 中明确列出的科学测试 |
| 完整本地科学能力 | `tools/run_science_tests.py --suite full`、`tools/verify_tutorial_samples.py` | 现有本地样本对应的科学读取与数值断言，包括 P02；原始 checkpoint 另选 `--checkpoints` |
| 安装与可迁移工程 | `tools/verify_extension.py`、`tools/verify_alpha_workflow.py` | 当前候选的真实安装、生成、导出及新进程读回 |
| XYZ 与科学 CSV | `tools/verify_xyz_export_blender.py` | 离散帧、显式数据导出与对应输入/单位 |
| 构型关联与共享对象 | `tools/verify_audit_p1_association.py`、`tools/verify_audit_p1_shared_mesh.py` | 有效/失效关联、共享 mesh 拒绝与独立对象恢复；需要 P02 本地输入 |
| 视觉回归 | `tools/render_visual_baseline.py` | 已有六种视觉场景的自动比较；不能代替人眼验收 |
| 历史压缩包盘点 | [inventory_cleanup.py](tools/inventory_cleanup.py)、[CLEANUP](CLEANUP.md) | 逐文件用途、身份、建议和未检查范围；没有删除入口 |

> public-core：仅依赖可公开样本的指定科学测试集合，不包含全部本地科研案例。

只有本批实际执行并满足断言的检查才记 `Passed`；执行失败记 `Failed`，未运行或缺少必要条件记 `Not Run`。历史报告的通过状态不自动属于新安装包。自动测试、真实 GUI 操作、维护者反馈与独立科研判断分别记录。

## 复用已有环境

以下命令在仓库根目录的 PowerShell 中运行。使用已安装的 Blender 5.1.1 和项目现有 `outputs/science/`；环境不齐时按 [开发说明](../../docs/DEVELOPMENT.md) 查明缺项，再按授权补充依赖。这里的示例不安装依赖。

批次名 `a1` 必须尚未使用。原始工程写到 `validation/work/agent/a1/`，命令日志和技术报告写到 `validation/agent/reports/a1/`；两者都不进入公开教程包。既有批次及 `outputs/runs/` 内容保持原位，按 [ARTIFACTS](../../docs/ARTIFACTS.md) 查找。

```powershell
$repo = (Get-Location).Path
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$python = 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe'
$batch = Join-Path $repo 'validation/work/agent/a1'
$reports = Join-Path $repo 'validation/agent/reports/a1'
$candidate = Join-Path $repo 'validation/shared/install/qcblender-0.1.0.zip'
$samples = Join-Path $repo 'validation/agent/packages/qcblender-public-tutorial-samples-v2.zip'
foreach ($path in @($python, $blender, $candidate, $samples, "$repo/outputs/science")) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required path is missing: $path" }
}
if ((Test-Path -LiteralPath $batch) -or (Test-Path -LiteralPath $reports)) {
    throw 'Choose an unused batch name'
}
New-Item -ItemType Directory -Path $batch,$reports -ErrorAction Stop | Out-Null
$env:QCBLENDER_REFERENCE_ROOT = $repo
$utf8 = [System.Text.UTF8Encoding]::new($false)
function Invoke-Validation([string]$name, [string]$executable, [string[]]$arguments) {
    $lines = & $executable @arguments 2>&1
    $code = $LASTEXITCODE
    $text = (($lines | ForEach-Object { $_.ToString() }) -join "`n") + "`n"
    [System.IO.File]::WriteAllText("$reports/$name.log", $text, $utf8)
    $receipt = [ordered]@{ command = @($executable) + $arguments; exit_code = $code }
    [System.IO.File]::WriteAllText("$reports/$name-command.json", ($receipt | ConvertTo-Json -Depth 5) + "`n", $utf8)
    $lines | ForEach-Object { Write-Output $_ }
    if ($code -ne 0) { throw "Check failed: $name ($code)" }
}
```

命令收据只记录退出码。各工具报告中的覆盖范围、跳过项和冷重开状态仍需检查。

## 教程材料与完整图片检查

在仓库根目录的 PowerShell 中，使用上文定义的 `$python`；每次换用尚不存在的报告路径和副本目录：

```powershell
& $python -B -I validation/agent/tools/verify_workspace.py --report validation/agent/reports/tutorial-next/prepare.json --portable-dir validation/work/agent/tutorial-next/public-copy
if ($LASTEXITCODE -ne 0) { throw 'Tutorial material validation failed' }
```

此检查允许尚待操作者补入的截图和渲染图，报告会列出各图片是否存在；独立副本只包含教程文档、引用的图片、公开输入和安装材料。教程目录中出现工程、科学数据或未知文件时检查失败，应先按保全流程整理对应文件。

图片补齐后，发布前运行完整图片检查：

```powershell
& $python -B -I validation/agent/tools/verify_workspace.py --require-images --report validation/agent/reports/tutorial-next/images.json
if ($LASTEXITCODE -ne 0) { throw 'Tutorial images are incomplete' }
```

`--require-images` 只确认引用的图片文件齐全；Git 跟踪、网站构建和实际部署须分别核对。

## 输入与科学检查

按改动范围选择执行；无需每次重复运行全部检查。

```powershell
Invoke-Validation 'inputs' $python @('-I', 'tools/local_inputs.py')
Invoke-Validation 'stdlib' $python @('-I', 'tools/run_stdlib_tests.py', '--output', "$reports/stdlib.json")
Invoke-Validation 'frozen-samples' $python @('-I', 'tools/candidate_artifacts.py', 'check-samples', '--package', $samples, '--output', "$reports/frozen-samples.json")
Invoke-Validation 'public-science' $python @('-I', 'tools/run_science_tests.py', '--site', "$repo/outputs/science", '--suite', 'public-core', '--output', "$reports/public-science.json")
```

本地资料齐全时补充完整检查：

```powershell
Invoke-Validation 'local-science' $python @('-I', 'tools/run_science_tests.py', '--site', "$repo/outputs/science", '--suite', 'full', '--output', "$reports/local-science.json")
Invoke-Validation 'tutorial-samples' $python @('-I', 'tools/verify_tutorial_samples.py', '--reference-root', $repo, '--package', $samples, '--report', "$reports/tutorial-samples.json")
```

`--checkpoints` 需要原始计算文件与既有 PySCF 环境。未执行时保留报告中的 `original_checkpoint_density: Not Run`，不把常规样本通过视为原始计算复算通过。

## 安装、导出与冷重开

先遵守 [Blender 操作规则](../../docs/agents/blender-interaction.md)，核对当前连接 PID、工程保存状态与 [操作登记表](acceptance/blender-operations.json)。同一时刻只运行一个 Blender 进程。以下命令按顺序串行执行，使用本批独立配置，不连接现有用户会话。

> 冷重开：前一个 Blender 进程退出后，启动一个新进程读取已保存工程。

```powershell
$env:BLENDER_USER_RESOURCES = "$batch/profile"
$env:BLENDER_USER_CONFIG = "$batch/profile/config"
$env:BLENDER_USER_EXTENSIONS = "$batch/profile/extensions"
$env:BLENDER_USER_DATAFILES = "$batch/profile/datafiles"
$env:BLENDER_USER_CACHE = "$batch/cache"
$env:TEMP = "$batch/process-temp"
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Path $env:BLENDER_USER_CONFIG,$env:BLENDER_USER_EXTENSIONS,$env:BLENDER_USER_DATAFILES,$env:BLENDER_USER_CACHE,$env:TEMP -ErrorAction Stop | Out-Null
$qa = "$batch/install"
Invoke-Validation 'install' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_extension.py', '--', '--candidate', $candidate, '--output-dir', $qa)
Copy-Item -LiteralPath "$qa/extension.json" -Destination "$reports/install.json"
Invoke-Validation 'cold-original' $blender @('--background', '--offline-mode', '--disable-autoexec', "$qa/mo8.blend", '--python-exit-code', '1', '--python', 'tools/verify_extension.py', '--', '--reopen', '--output-dir', $qa)
Copy-Item -LiteralPath "$qa/extension.json" -Destination "$reports/cold-original.json"
Invoke-Validation 'cold-moved' $blender @('--background', '--offline-mode', '--disable-autoexec', "$qa/moved 中文 path/mo8.blend", '--python-exit-code', '1', '--python', 'tools/verify_extension.py', '--', '--reopen', '--output-dir', $qa)
Copy-Item -LiteralPath "$qa/extension.json" -Destination "$reports/cold-moved.json"
```

`verify_extension.py` 使用固定 `extension.json`，上面的命令已把安装与两次冷重开报告分阶段保存。安装和移动工程必须来自本批 `$qa`，不借用历史 `.blend`。

专项工具同样从当前候选和集中输入开始，在新目录重建 fixture：

```powershell
Invoke-Validation 'external-worker' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_external_worker.py', '--', '--candidate', $candidate, '--reference-root', $repo, '--output-dir', "$batch/external-worker")
Invoke-Validation 'numeric-nocv' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_nocv.py', '--', '--candidate', $candidate, '--reference-root', $repo, '--output-dir', "$batch/numeric-nocv")
Invoke-Validation 'numeric-nocv-cold' $blender @('--background', '--offline-mode', '--disable-autoexec', "$batch/numeric-nocv/nocv.blend", '--python-exit-code', '1', '--python', 'tools/verify_nocv.py', '--', '--reopen', '--candidate', $candidate, '--reference-root', $repo, '--output-dir', "$batch/numeric-nocv")
```

worker 检查读取集中保存的 C07 IGMH 和 Gaussian NBO 原件，另从 CH4 波函数重建数值 Cube 与测试 ETS 表；数值 NOCV 关联检查不代表真实 NOCV 科研验收。`prepare_vesta_comparison.py` 使用 `--reference-root` 和必需的 `--output-dir` 重建同一 MO Cube；`prepare_complex_examples.py` 需要明确 `--candidate`、`--reference-root` 和新的 `--output-dir`。`verify_node_layout.py` 的 baseline/check/reopen 三阶段共享本批 `--out`，每阶段明确 `--candidate` 和 `--reference-root`，资产直接从指定 ZIP 提取。

NOCV 生成与冷重开都要求同一份 `--candidate`；节点资产从该 ZIP 提取到本批 `library/` 后再注册源码。冷重开核对提取文件仍与候选一致，缺少资产、重复资产成员或字节不同直接失败。

构建和科学环境只维护 `outputs/build-site/`、`outputs/science/` 及根 `outputs/wheels/`；重建方式见[开发说明](../../docs/DEVELOPMENT.md#增量构建准备)。环境精简清单可用 `tools/runtime_cleanup_plan.py --root <参考检出> --report-dir <新目录>` 生成，工具只输出建议，不删除文件。生成前按依赖锁及 backend record 核对每份根 wheel 的实际 SHA-256，缺失或不匹配直接失败；成功报告的 `canonical_wheels` 保存期望摘要、实际摘要与 Passed。只有根 wheel 全部通过，来源副本才能进入退役建议。五个构建包文件按 distribution RECORD 归属保留，完整科学环境及原始源码/许可另列保护路径。

Alpha 主流程和 XYZ/CSV 的明确入口如下。它们使用上一步的本批安装配置；运行前保证前一个 Blender 已退出。

```powershell
Invoke-Validation 'alpha' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_alpha_workflow.py', '--', '--candidate', $candidate, '--output-dir', "$batch/alpha", '--report', "$reports/alpha.json")
Copy-Item -LiteralPath "$reports/alpha.json" -Destination "$reports/alpha-before-reopen.json"
Invoke-Validation 'alpha-cold' $blender @('--background', '--offline-mode', '--disable-autoexec', "$batch/alpha/中文路径移动/example.blend", '--python-exit-code', '1', '--python', 'tools/verify_alpha_workflow.py', '--', '--reopen', '--candidate', $candidate, '--output-dir', "$batch/alpha", '--report', "$reports/alpha.json")
Invoke-Validation 'xyz-export' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_xyz_export_blender.py', '--', '--reference-root', $repo, '--output-dir', "$batch/xyz", '--report', "$reports/xyz-export.json")
Copy-Item -LiteralPath "$reports/xyz-export.json" -Destination "$reports/xyz-before-reopen.json"
Invoke-Validation 'xyz-cold' $blender @('--background', '--offline-mode', '--disable-autoexec', "$batch/xyz/integration.blend", '--python-exit-code', '1', '--python', 'tools/verify_xyz_export_blender.py', '--', '--reference-root', $repo, '--output-dir', "$batch/xyz", '--report', "$reports/xyz-export.json", '--reopen')
```

P1 关联与共享对象检查需要 P04 和 P02 本地资料：

```powershell
Invoke-Validation 'association' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_audit_p1_association.py', '--', '--output-dir', "$batch/association")
Invoke-Validation 'association-cold' $blender @('--background', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_audit_p1_association.py', '--', '--output-dir', "$batch/association", '--reopen', "$batch/association/p1-association.blend")
Invoke-Validation 'shared-mesh' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_audit_p1_shared_mesh.py', '--', '--output-dir', "$batch/shared")
Invoke-Validation 'shared-mesh-cold' $blender @('--background', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_audit_p1_shared_mesh.py', '--', '--output-dir', "$batch/shared", '--reopen', "$batch/shared/shared-mesh.blend")
```

以上脚本报告保存在各自输出目录。归档时把报告、命令日志与必要工程位置纳入同批索引；不要改写历史报告以绑定新候选。原生脚本不能证明完整 GUI 点击或撤销矩阵；需要实际 GUI 操作的检查见 [COVERAGE](COVERAGE.md)。

## 清理盘点与收尾

先看 [CLEANUP](CLEANUP.md)。仅重新生成只读清单时，在主检出执行：

```powershell
& $python -I validation/agent/tools/inventory_cleanup.py --root $repo --latest-candidate outputs/candidates/current/alpha-ci-0.1.0-190e11e --report-dir validation/agent/reports/cleanup-next
if ($LASTEXITCODE -ne 0) { throw 'Cleanup inventory failed' }
```

新的报告目录必须不存在。工具检查被保留候选的现有文件与报告，再盘点其他压缩包和有明确映射的旧安装对象；只为拟清理文件计算身份，不遍历所有科学数组。输出 `inventory.json` 和 `inventory.md`，保留读取失败及排除范围。

本批结束后，按 [存储维护规则](../../docs/agents/storage-maintenance.md) 维护 [ARTIFACTS](../../docs/ARTIFACTS.md)、任务状态与实际检查结果。清单生成不等于用户批准删除；用户工程、依赖、未知归属、链接和权限拒绝对象保留。SHA-256、技术收据及结果状态只属于 Agent 流程，不添加到人工 SOP。
