# 开发入口与 Windows 完整构建

日常修改先读 [开发流程](agents/development-workflow.md)，通过 `python -m tools.dev_workflow` 查询操作、选择定向测试和一个实际相关案例，再构建最终候选并执行安装冒烟。参数以 `python -m tools.dev_workflow --help` 为准；流程取舍见 [近期复盘](agents/development-retrospective.md)。

本页保留环境准备、完整构建及发布级验收命令，供首次准备、发布资格或改动需要扩大覆盖时查阅。命令在仓库根目录 PowerShell 执行，目标 Windows x64、Blender 5.1.1 / CPython 3.13.9。首次检出先走“首次环境准备”，已有环境走“增量构建准备”，再按任务范围选择后续检查；发布使用文末候选 CI 门禁。当前结果见 [VALIDATION](VALIDATION.md)。最终用户只安装合格扩展 ZIP。

## 工作树与产物收尾

在主仓库 `.worktrees/<任务名>/` 使用独立分支开发，复验后 ff-only 合并本地 main；为任务最终提交创建带注释的 `archive/YYYY-MM-DD/<完整分支名>` 标签，核对保留产物及提交可达性后移除工作树，再删除已合并分支。源码、测试/输入、环境和候选身份相同时引用原结果；main 推进带入相关改动时才复验受影响内容。该流程不包含 push。

[产物路由](ARTIFACTS.md) 是现存证据、用户工程、候选及重建方法的唯一查找入口。任务结束后保留最新待验收候选、共用环境及锁定 wheels，迁移必要日志和数据后清理独立测试配置及旧候选，执行边界见[维护规则](agents/storage-maintenance.md)。

## Blender 操作复用

维护者遵守 [单进程与操作复用规则](agents/blender-interaction.md)。先请用户保存关闭 Blender，确认退出后开始，结束打开原保存工程。用 `python -m tools.dev_workflow query "<关键词>"` 定位登记表的操作 ID 与证据；已确认入口优先真实 MCP、其次已有 CLI，Computer Use 按首次入口及 UI 输入/弹窗/布局/交互变化复验。纯内部实现通过定向检查和实际相关案例核验。切换工程或重连时重新核对 PID，每批结果与历史 GUI 证据分别记录。

## 本批目录与命令记录

先提交待验证的文档、测试及产品源码，记录实际提交。使用新的短任务和批次名称（示例 qc/1）；中文移动测试的完整数组路径应短于 260 字符，批次过长时先缩短路径；批次目录存在时停止，不能覆盖旧证据。以下函数保存每条命令、输出摘要与退出码，成功后才继续；命令成功不自动证明未运行的其他范围。

~~~powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$blenderPython = 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe'
$repo = (Get-Location).Path
$batch = "$repo/outputs/runs/qc/1"
$qa = "$batch/qa"
$scienceSite = "$repo/outputs/science"
$wheels = "$repo/outputs/wheels"
$uv = (Get-Command uv -ErrorAction Stop).Source
if (Test-Path -LiteralPath $batch) { throw 'Choose an unused batch directory' }
$sourceCommit = git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot identify source commit' }
$utf8 = [System.Text.UTF8Encoding]::new($false)
$env:BLENDER_USER_RESOURCES = "$batch/profile"
$env:BLENDER_USER_CONFIG = "$env:BLENDER_USER_RESOURCES/config"
$env:BLENDER_USER_EXTENSIONS = "$env:BLENDER_USER_RESOURCES/extensions"
$env:BLENDER_USER_DATAFILES = "$env:BLENDER_USER_RESOURCES/datafiles"
$env:BLENDER_USER_CACHE = "$batch/cache"
$env:TEMP = "$batch/process-temp"
$env:TMP = $env:TEMP
$env:UV_CACHE_DIR = "$repo/outputs/uv-cache"
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_CONFIG,$env:BLENDER_USER_EXTENSIONS,$env:BLENDER_USER_DATAFILES,$env:TEMP,"$batch/logs" | Out-Null

function Invoke-QCCheck([string]$name, [string]$executable, [string[]]$arguments) {
    Write-Output ("Running: " + $name)
    $lines = & $executable @arguments 2>&1
    $code = $LASTEXITCODE
    $log = "$batch/logs/$name.log"
    [System.IO.File]::WriteAllText($log, (($lines | ForEach-Object { $_.ToString() }) -join "`n") + "`n", $utf8)
    $record = [ordered]@{
        status = $(if ($code -eq 0) { 'Passed' } else { 'Failed' })
        source_commit = $sourceCommit
        command = @($executable) + $arguments
        exit_code = $code
        log = "logs/$name.log"
        log_sha256 = (Get-FileHash -LiteralPath $log -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    [System.IO.File]::WriteAllText("$batch/$name-command.json", ($record | ConvertTo-Json -Depth 8) + "`n", $utf8)
    $lines | ForEach-Object { Write-Output $_ }
    if ($code -ne 0) { throw "Check failed: $name ($code)" }
}
~~~

Blender 路径按本机安装修改。 CONFIG、EXTENSIONS 和 DATAFILES 必须显式指定并在 Blender 启动前创建；仅设置资源根目录时，缺少子目录可能回退到用户默认配置。安装脚本先核对本批实际目录，校验通过后才安装。构建工具写入仓库的 outputs/build-site；科学测试依赖写入 outputs/science，不向 Blender Python 的安装目录写入包。部分旧工具固定写入 outputs/node-assets、outputs/acceptance 或 outputs/recovery，须在新工作树执行，或先确保没有上一批同名产物。

## 必要输入与前置检查

[集中数据目录](../validation/shared/data/README.md) 和 `validation/shared/data/local-inputs.json` 固定来源、许可及身份。没有必要样本时在本阶段停止，不用旧工程或跳过代替。人工教程已备好资源时可直接从安装开始，以下命令用于开发检出的技术准备。

公开资源从仓库内的冻结 v2 包恢复；本地原件可从已完成整理的参考检出复制。准备工具只处理清单内的路径，已有不同内容直接失败，不覆盖用户文件；受限输入保持在忽略目录，公开教程包排除。

~~~powershell
$sourceRoot = '<已有原件的仓库绝对路径>'
Invoke-QCCheck 'copy-inputs' $blenderPython @('-I', 'tools/prepare_validation_data.py',
    '--reference-root', $sourceRoot, '--reference-layout', 'current',
    '--include-local', '--include-calculations', '--report', "$batch/input-preparation.json")
Invoke-QCCheck 'inputs' $blenderPython @('-I', 'tools/local_inputs.py')
~~~

只需要公开回归时，省略 `--reference-root`、`--reference-layout`、`--include-local`、`--include-calculations`。首次从旧 `tests/data/` 布局迁入时，显式选择 `--reference-layout legacy`，工具不会自动回退查找旧路径。已备齐本地原件时只执行 inputs 检查。`QCBLENDER_REFERENCE_ROOT` 可显式指向已整理的参考检出；部分完整科学测试直接使用当前检出的 `validation/shared/data/local/`，运行前按上面命令准备。每次指定新报告路径。

## 首次环境准备

仅在依赖下载和隔离安装已获授权后执行。新工作树初始不应存在 backend-wheel.json 或依赖上一检出的 science 目录。可显式复制依赖缓存：锁定 wheels 按 dependencies.lock.json 校验，GBasis 原始 ZIP 按 science-sources.lock.json 校验；后端 wheel 和资格报告由本次生成。

~~~powershell
Invoke-QCCheck 'prepare' $blenderPython @('-I', 'tools/prepare_build.py', '--uv', $uv)
Invoke-QCCheck 'dependencies' $blenderPython @('-I', 'tools/fetch_dependencies.py')
$sourceLockBytes = [System.IO.File]::ReadAllBytes("$repo/science-sources.lock.json")
Invoke-QCCheck 'backend' $blenderPython @('-I', 'tools/build_science_backend.py')
$sourceLockText = [System.IO.File]::ReadAllText("$repo/science-sources.lock.json").Replace("`r`n", "`n")
if ($sourceLockText -ne $utf8.GetString($sourceLockBytes).Replace("`r`n", "`n")) { throw 'Science source lock changed' }
$locked = Get-Content dependencies.lock.json -Raw | ConvertFrom-Json
$backend = Get-Content outputs/backend-wheel.json -Raw | ConvertFrom-Json
$scienceWheels = @($locked.packages.filename) + @($backend.filename)
$scienceWheels = @($scienceWheels | ForEach-Object { Join-Path $wheels $_ })
Invoke-QCCheck 'science-install' $uv (@('pip', 'install', '--python', $blenderPython, '--target', $scienceSite, '--no-deps') + $scienceWheels)
~~~

prepare_build 固定工具版本，fetch_dependencies 核对每个 wheel，build_science_backend 从固定 GBasis 源码生成纯 Python wheel 和 outputs/backend-wheel.json。后端构建只核验科学源码锁，不改写锁文件；内容变化直接失败。完成后检查两个锁文件没有改动。首次路径接着执行下方共同流程，不提前调用 build_extension。

## 增量构建准备

已有环境先运行输入检查，再核对已有工具、科学依赖和 wheels；缺少准备产物时回到首次路径，不隐式使用其他检出的 backend-wheel.json。首次与增量构建统一使用 `outputs/wheels/`，随后逐文件校验后端记录与 wheel。不要以文件名相同替代摘要核对。

整理已有缓存时，先按依赖锁及 backend record 核对全部根 wheel。缺失或摘要不同则停止缓存退役；只有同版本的合格内容完成迁移、根目录重新核对通过后，才能删除来源副本。保留路径的登记不代表该路径当前内容已合格。

~~~powershell
$wheels = "$repo/outputs/wheels"
$env:QCBLENDER_WHEELS_DIR = $wheels
~~~

~~~powershell
$checkEnvironment = @'
from importlib.metadata import distributions
import hashlib, json, os
from pathlib import Path
root = Path.cwd()
expected = dict(line.split('==') for line in (root / 'tools/build-requirements.txt').read_text().splitlines() if line)
actual = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in distributions(path=[str(root / 'outputs/build-site')])}
assert all(actual.get(name.lower().replace('_', '-')) == version for name, version in expected.items())
backend = json.loads((root / 'outputs/backend-wheel.json').read_text())
packages = json.loads((root / 'dependencies.lock.json').read_text())['packages'] + [backend]
science = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in distributions(path=[str(root / 'outputs/science')])}
for package in packages:
    wheel = Path(os.environ['QCBLENDER_WHEELS_DIR']) / package['filename']
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == package['sha256'], wheel
    assert science.get(package['name'].lower().replace('_', '-')) == package['version'], package['name']
print('BUILD_ENVIRONMENT_PASSED')
'@
Invoke-QCCheck 'environment' $blenderPython @('-I', '-c', $checkEnvironment)
~~~

环境核对通过后，增量与首次路径均可执行以下流程。产品源码变化后完整构建最终候选，并重验受影响行为及最终安装冒烟；相同身份的检查按开发流程引用原报告。已有环境本身不证明旧报告适用于新候选。

共用构建环境按 `tools/build-requirements.txt` 保留五个锁定包及其 RECORD 文件；科学环境保留完整的 `outputs/science/`。本地解释器使用已安装的 Blender Python。GBasis 固定原始 ZIP 保留在 `outputs/build-sources/`，后端构建不需要历史 qcint 编译环境。保留当前构建工具、锁定运行 wheels 和 GBasis 原始 ZIP 后，可以离线构建；从空环境重新安装构建工具还需要相应的离线 wheel 或已获授权的下载。

回归输入的当前入口为 `validation/shared/data/regression/`。`tools/collect_m0_fixtures.py --reference-root <参考检出> --output-root <目标检出>` 优先核对或复制集中输入；缺少 IOData/GBasis fixture 时，从参考检出的唯一原始 ZIP 恢复，不依赖历史展开源树。ChemTools 输入缺失时直接给出缺失路径与固定来源 URL，不隐式下载。

## 科学与非科学检查

~~~powershell
Invoke-QCCheck 'science' $blenderPython @('-I', 'tools/run_science_tests.py', '--site', $scienceSite, '--output', "$batch/science.json")
foreach ($test in @('test_copy_display.py', 'test_legend_layout.py', 'test_local_inputs.py', 'test_storage_cleanup.py')) {
    Invoke-QCCheck ($test.Replace('.py', '')) $blenderPython @('-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', $test)
}
Invoke-QCCheck 'helpers' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_node_helpers.py')
~~~

科学报告记录 tests/failures/errors/skipped 和参考误差；核对实际样本与数量，必要样本不能 skipped。节点辅助测试比较实际源原子编号及固定公共接口，范围与上轮十组完整节点图对照分别记录。完整网格收敛实验另由 qualify_scientific_fields.py 执行；未执行记 Not Run。

公共教程批次先完成上面的数据准备，再执行解析检查。使用本检出的冻结 v2 包和当前输入；包不存在时停止，不从旧报告继承通过。

~~~powershell
$tutorialPackage = Join-Path $repo 'validation/agent/packages/qcblender-public-tutorial-samples-v2.zip'
Invoke-QCCheck 'tutorial-samples' $blenderPython @('-I', 'tools/verify_tutorial_samples.py', '--reference-root', $repo, '--site', $scienceSite, '--package', $tutorialPackage, '--report', "$batch/tutorial-samples.json")
~~~

`--checkpoints`仅由已有PySCF计算环境执行，解释器/版本单列，不作为插件依赖。完整命令见本轮验证索引；缺必要checkpoint时在该检查停止，新批次不覆盖旧报告。

## 打包与离线安装

~~~powershell
Invoke-QCCheck 'build' $blenderPython @('-I', 'tools/build_extension.py', '--blender', $blender, '--wheels-dir', $wheels, '--output-dir', "$batch/dist")
$extensionVersion = (Select-String -Path qcblender/blender_manifest.toml -Pattern '^version = "([^"]+)"').Matches.Groups[1].Value
$candidate = "$batch/dist/qcblender-$extensionVersion.zip"
Get-FileHash -LiteralPath $candidate -Algorithm SHA256
Invoke-QCCheck 'install' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_extension.py', '--python', 'tools/verify_node_assets.py', '--', '--candidate', $candidate, '--output-dir', $qa)
Copy-Item -LiteralPath "$qa/extension.json" -Destination "$batch/extension-install.json"
Copy-Item -LiteralPath 'outputs/node-assets/report.json' -Destination "$batch/node-assets.json"
~~~

ZIP 核对锁定 wheels 并生成节点资产；依赖及许可随包，NumPy/OpenVDB 使用 Blender 自带版本。时间戳可能使 ZIP 摘要改变，不宣称逐字节复现。verify_extension 核对科学运行库、求值、取消、缓存及注册/注销；verify_node_assets 检查公共等值面、分支保留和资产导出重载。

## 同批工程冷重开与恢复

只打开本批安装检查生成的工程。每次重开后立即保存报告副本，避免原地和移动结果被最后一次覆盖。

~~~powershell
Invoke-QCCheck 'cold-original' $blender @('--background', '--offline-mode', '--disable-autoexec', "$qa/mo8.blend", '--python-exit-code', '1', '--python', 'tools/verify_extension.py', '--', '--reopen', '--output-dir', $qa)
Copy-Item -LiteralPath "$qa/extension.json" -Destination "$batch/extension-cold-original.json"
Invoke-QCCheck 'cold-moved' $blender @('--background', '--offline-mode', '--disable-autoexec', "$qa/moved 中文 path/mo8.blend", '--python-exit-code', '1', '--python', 'tools/verify_extension.py', '--', '--reopen', '--output-dir', $qa)
Copy-Item -LiteralPath "$qa/extension.json" -Destination "$batch/extension-cold-moved.json"
New-Item -ItemType Directory -Force -Path 'outputs/acceptance' | Out-Null
Invoke-QCCheck 'recovery' $blender @('--background', '--offline-mode', '--disable-autoexec', "$qa/moved 中文 path/mo8.blend", '--python-exit-code', '1', '--python', 'tools/verify_project_recovery.py')
Copy-Item -LiteralPath 'outputs/acceptance/recovery.json' -Destination "$batch/recovery.json"
~~~

恢复检查使用原始输入重建缺失 VDB，并核对来源重定位、电荷、偶极和振动。新工程、配套数据及日志保留在本批目录和上述固定工具目录。

## 图例专项

out 必须为绝对路径；继续使用本批已安装扩展配置，配置位于图例目录的父目录内。先打开安装检查生成的 mo8.blend：图例专项从该工程取得 MO 视图，再创建密度/ESP 场；空场景不满足前置条件。

~~~powershell
$legend = "$batch/legend"
Invoke-QCCheck 'legend' $blender @('--background', '--offline-mode', '--disable-autoexec', "$qa/mo8.blend", '--python-exit-code', '1', '--python', 'tools/verify_mn_legend.py', '--', '--check', 'legend', '--out', $legend)
Copy-Item -LiteralPath "$legend/checks.json" -Destination "$batch/legend.json"
Invoke-QCCheck 'legend-cold-original' $blender @('--background', '--offline-mode', '--disable-autoexec', "$legend/evidence.blend", '--python-exit-code', '1', '--python', 'tools/verify_mn_legend.py', '--', '--check', 'reopen', '--out', $legend)
Copy-Item -LiteralPath "$legend/checks.json" -Destination "$batch/legend-cold-original.json"
Invoke-QCCheck 'legend-cold-moved' $blender @('--background', '--offline-mode', '--disable-autoexec', "$legend/moved 中文 path/evidence.blend", '--python-exit-code', '1', '--python', 'tools/verify_mn_legend.py', '--', '--check', 'reopen', '--out', $legend)
Copy-Item -LiteralPath "$legend/checks.json" -Destination "$batch/legend-cold-moved.json"
~~~

检查实际渲染。图例初建和第一次重开的报告 status 为 Not Run，表示完整双冷重开链尚未完成；保留这些阶段快照，用第二次重开后的完整 Passed 报告参加资格汇总。更广范围按改动选择 [Agent 检查覆盖](../validation/agent/COVERAGE.md) 和专项工具；已有工具不等于每项命令对当前候选均通过。GUI 实际点击、人工教程、性能、独立科研接受及其他平台分别记录，不由包资格推导。

## 生成索引与汇总资格

以下可执行示例将本批实际报告及命令收据绑定到同一 ZIP。命令收据仅说明相应命令成功；覆盖范围仍按工具的实际断言声明。只收录已执行且 Passed 的检查；Failed / Not Run 写入任务或受版本控制的验证索引。

~~~powershell
$makeIndex = @'
import hashlib, json, subprocess, sys
from pathlib import Path
source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
batch, candidate = map(lambda value: Path(value).resolve(), sys.argv[1:])
digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
reports = ['science.json', 'node-assets.json', 'extension-install.json',
           'extension-cold-original.json', 'extension-cold-moved.json', 'recovery.json',
           'legend-cold-moved.json']
reports += [f'{name}-command.json' for name in
            ['test_copy_display', 'test_legend_layout', 'test_local_inputs', 'test_storage_cleanup',
             'helpers', 'install', 'cold-original', 'cold-moved', 'recovery',
             'legend', 'legend-cold-original', 'legend-cold-moved']]
checks = {}
for name in reports:
    path = batch / name
    raw = path.read_bytes()
    report = json.loads(raw)
    assert report['status'] == 'Passed', (name, report)
    if 'log' in report:
        assert hashlib.sha256((batch / report['log']).read_bytes()).hexdigest() == report['log_sha256'], name
    checks[name] = {'path': name, 'sha256': hashlib.sha256(raw).hexdigest(),
                    'candidate_sha256': digest}
(batch / 'evidence-index.json').write_text(
    json.dumps({'candidate_sha256': digest, 'source_commit': source_commit, 'checks': checks}, indent=2) + '\n', encoding='utf-8')
print('EVIDENCE_INDEX_PASSED:', len(checks), digest)
'@
Invoke-QCCheck 'index' $blenderPython @('-I', '-c', $makeIndex, $batch, $candidate)
$installed = "$env:BLENDER_USER_RESOURCES/extensions/user_default/qcblender"
if (-not (Test-Path -LiteralPath "$installed/__init__.py")) { throw 'Installed extension source directory missing; inspect the installation log' }
Invoke-QCCheck 'qualification' $blenderPython @('-I', 'tools/qualify_package.py', '--candidate', $candidate, '--installed-dir', $installed, '--evidence-index', "$batch/evidence-index.json", '--output', "$batch/qualification.json")
~~~

安装目录须是本批实际扩展源码目录，可从安装日志核对。资格工具比较源码、ZIP、wheel、安装副本与报告身份，不执行 Blender 检查，也不判断覆盖是否充分。检查 qualification 的 source_commit 与本批提交一致，并保存源码文件清单、工具版本和报告摘要。修改被验证源码后必须重新构建复验。

文件系统受限时保留真实错误，必要时按既有授权在宿主执行；不能吞错、改 ACL 或修改科学行为规避。阶段结束按 [存储维护规则](agents/storage-maintenance.md) 保留工程、必要输入、环境及日志。技术资格与独立人工验收分别维护。

## 公开核心候选与 GitHub Alpha

准备锁定 wheels、本次 backend-wheel.json 和科学测试依赖，确保 Git 检出干净。在 Windows x64 的 Blender 5.1.1 Python 下运行：

```powershell
& $blenderPython -I -B tools/run_candidate_ci.py --blender $blender --site $scienceSite --output-dir outputs/runs/alpha-1 --run-id 0 --channel alpha
```

目标目录必须不存在。该入口运行显式标准库集合与公开科学集合、构建、隔离离线安装、注册/注销、原地及中文移动冷重开、P01/MO9 摘要及首次渲染。公开科学集合必须调用真实 IOData/GBasis 并通过独立 cubegen/Fortran 对照；缺必要输入或跳过即失败。完整受限样本集合继续用 `run_science_tests.py` 默认 full 入口。

候选 artifact 包含原扩展 ZIP、冻结 v2 样本 ZIP、精简复现 ZIP、报告、release-manifest.json 和 SHA256SUMS.txt。manifest 保存源码提交、运行 ID、依赖和包/样本摘要；上传返回的 artifact ID 单独用于发布身份核验。资格工具要求本次 evidence-index 和隔离安装路径，没有历史报告兜底。

候选 CI 在 `.github/workflows/extension-package.yml`；发布入口在 `extension-release.yml`，默认分支手动输入 tag、candidate_run_id、dry_run（默认 true）。发布只核验并上传原文件，不重新打包；先核对注释标签、main 可达性、manifest 版本、精确运行提交、artifact 与报告。组件许可通过后可创建草稿，独立试装和公开批准另记绑定候选的 release-gates 记录；维护者最后在 GitHub UI 公开为 prerelease。首次 Alpha 只发 GitHub。详见[发布研究](research/github-release-workflow.md)。
