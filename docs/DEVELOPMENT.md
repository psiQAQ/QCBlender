# Windows 构建与验收

以下步骤在仓库根目录 PowerShell 执行，目标 Windows x64、Blender 5.1.1 / CPython 3.13.9。每条命令成功后再继续；当前实际结果见 [VALIDATION](VALIDATION.md)。最终用户只安装合格扩展 ZIP，以下环境是开发验证所需。

## 输入与已有环境

按本机安装设置路径。使用独立、路径较短的新验收目录，避免覆盖已有工程；原生 ZIP 解压仍可能受 Windows 路径长度限制。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$blenderPython = 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe'
$batch = "$PWD/outputs/qc01"
$qa = "$batch/qa"
$scienceSite = "$PWD/outputs/science"
$wheels = "$PWD/outputs/wheels"
$env:BLENDER_USER_RESOURCES = "$batch/profile"
$env:TEMP = "$batch/process-temp"
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force $env:TEMP
```

`qc01` 是本批示例名称；下一批换用另一个未使用的短目录名，安装工程和报告随 `$batch` 一起隔离。

必要输入由 [SOURCES](v1-acceptance/SOURCES.md) 和 `tests/data/local-inputs.json` 固定来源及 SHA-256。已有集中输入可以用 `QCBLENDER_REFERENCE_ROOT` 指向包含相同清单的仓库；部分日志单测仍直接使用当前仓库 `tests/data/local/log-examples/`，需按清单复制相同字节。校验后才运行：

```powershell
& $blenderPython -I tools/local_inputs.py
```

缺少输入时按来源清单取得原件，保留许可证；不使用历史生成工程代替原始输入。复用已有锁定 wheels、`outputs/backend-wheel.json` 和 science 测试目录，不必重复安装环境。

## 构建新候选

```powershell
& $blenderPython -I tools/build_extension.py --blender $blender --wheels-dir $wheels --output-dir "$batch/dist"
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
$candidate = "$batch/dist/qcblender-0.0.1.zip"
Get-FileHash -Algorithm SHA256 $candidate
```

`dependencies.lock.json` 固定 wheel URL/SHA-256，`science-sources.lock.json` 固定科学源码。构建核对锁定输入并生成节点资产；ZIP 含科学 wheels 与许可文本，NumPy/OpenVDB 来自 Blender。ZIP 时间戳可能不同，不能宣称逐字节复现；每个新包记录摘要并重新验收。

仅在首次建立开发环境、且依赖下载/安装已获授权时，按顺序运行下列命令；已有环境跳过。工具版本由 `tools/build-requirements.txt` 固定，不向 Blender Python 安装构建工具。

```powershell
$uv = (Get-Command uv).Source
$env:UV_CACHE_DIR = "$PWD/outputs/uv-cache"
& $blenderPython -I tools/prepare_build.py --uv $uv
& $blenderPython -I tools/fetch_dependencies.py
& $blenderPython -I tools/build_science_backend.py
```

科学测试环境使用随包 wheels 和宿主 NumPy；依赖安装也是首次环境准备步骤：

```powershell
$locked = Get-Content dependencies.lock.json -Raw | ConvertFrom-Json
$backend = Get-Content outputs/backend-wheel.json -Raw | ConvertFrom-Json
$scienceWheels = @($locked.packages.filename) + @($backend.filename)
$scienceWheels = $scienceWheels | ForEach-Object { Join-Path $wheels $_ }
& $uv pip install --python $blenderPython --target $scienceSite --no-deps $scienceWheels
```

## 数值与非科学单测

```powershell
& $blenderPython -I tools/run_science_tests.py --site $scienceSite --output "$batch/science.json"
foreach ($test in @('test_copy_display.py', 'test_legend_layout.py', 'test_local_inputs.py', 'test_storage_cleanup.py')) {
    & $blenderPython -B -m unittest discover -s tests -p $test
    if ($LASTEXITCODE -ne 0) { throw "Unit tests failed: $test" }
}
```

科学报告记录 tests/failures/errors/skipped 和参考误差；只看退出码不能代替确认真实样本及测试数量。完整网格收敛专项另由 `tools/qualify_scientific_fields.py` 执行；没有运行时记 Not Run。

## 安装、显示与同批工程冷重开

继续使用上述隔离配置。以下命令均在新进程运行，安装测试生成本批 `mo8.blend`、同名 `.qcdata/`、渲染、归档和中文移动副本。

```powershell
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_extension.py --python tools/verify_node_assets.py -- --candidate $candidate --output-dir $qa
& $blender --background --offline-mode --disable-autoexec "$qa/mo8.blend" --python-exit-code 1 --python tools/verify_extension.py -- --reopen --output-dir $qa
& $blender --background --offline-mode --disable-autoexec "$qa/moved 中文 path/mo8.blend" --python-exit-code 1 --python tools/verify_extension.py -- --reopen --output-dir $qa
& $blender --background --offline-mode --disable-autoexec "$qa/moved 中文 path/mo8.blend" --python-exit-code 1 --python tools/verify_project_recovery.py
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_node_helpers.py
```

`verify_extension.py` 核对运行库来源、实际求值、取消、缓存和注册/注销。`verify_node_assets.py` 在安装测试创建场后执行，检查公共等值面、分支保留和资产导出重载，输出 `outputs/node-assets/report.json`。恢复检查固定写入 `outputs/acceptance/recovery.json`，运行前须确认该目录可写，并把本次报告副本与日志纳入批次。冷重开日志应分别保存，脚本复用报告字段时不能仅保留最后一次 stdout。

图例专项在已安装扩展的同一隔离配置下从集中输入创建真实密度/ESP 场。`--out` 必须传绝对路径，并让隔离配置位于其父目录内；否则 Blender 渲染路径可能落在仓库之外。

```powershell
$legend = "$batch/legend"
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_mn_legend.py -- --check legend --out $legend
```

随后分别打开 `$legend/evidence.blend` 与 `$legend/moved 中文 path/evidence.blend`，执行同一脚本 `--check reopen --out $legend`。只重开本次生成工程，记录两份日志并检查渲染。

更广行为按改动范围选择专项工具与 [SOP](v1-acceptance/SOP.md)。`verify_results_blender.py --case C07 --check prepare --out <本批目录>`、`verify_multiwfn_interaction.py --mode prepare`、`verify_multiwfn_charts.py --mode prepare` 可从集中输入复建；具体必需参数见各工具。GUI、完整 SOP、性能与其他平台未运行时明确 Not Run。已有工具不代表每项命令对当前候选均已复验；已知问题见 [开发问题记录](DEVELOPMENT_PITFALLS.md) 和对应本地任务。

## 汇总资格与保留证据

保存源码提交/工作区摘要、构建命令、ZIP 摘要和实际安装目录。批次索引 JSON 使用 `candidate_sha256` 和 `checks`；每个检查包含批次内报告相对 `path`、报告 `sha256` 与相同 `candidate_sha256`，报告状态须为 Passed。

```powershell
& $blenderPython -I tools/qualify_package.py --candidate $candidate --installed-dir '<本批实际安装目录>' --evidence-index "$batch/evidence-index.json" --output "$batch/qualification.json"
```

将占位安装目录替换为本批实际路径，并先生成索引。资格工具只校验源码、ZIP、wheel、安装副本和报告身份，不执行 Blender 验收或判断覆盖是否充分。修改产品源码后必须重建并复验。

文件系统受限时，原生安装器重命名或新数据读取可能需要宿主权限；保留真实错误，不能吞错或修改科学行为规避。技术检查与独立人工签署分别维护。阶段结束按 [存储维护规则](agents/storage-maintenance.md) 保留工程、必要输入和日志；本页命令不提供额外删除授权。
