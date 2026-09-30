# Windows 构建与验收

在仓库根目录 PowerShell 执行，目标 Windows x64、Blender 5.1.1 / CPython 3.13.9。首次检出先走“首次环境准备”，已有环境走“增量构建准备”，随后进入共同验收流程。当前结果见 [VALIDATION](VALIDATION.md)。最终用户只安装合格扩展 ZIP。

## 工作树与产物收尾

在主仓库 `.worktrees/<任务名>/` 使用独立分支开发，复验后 ff-only 合并本地 main；为任务最终提交创建带注释的 `archive/YYYY-MM-DD/<完整分支名>` 标签，核对保留产物及提交可达性后移除工作树，再删除已合并分支。main 推进时先更新分支并复验。该流程不包含 push。

[产物路由](ARTIFACTS.md) 是现存证据、用户工程、候选及重建方法的唯一查找入口。任务结束后保留最新待验收候选、共用环境及锁定 wheels，迁移必要日志和数据后清理独立测试配置及旧候选，执行边界见[维护规则](agents/storage-maintenance.md)。

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

[来源清单](v1-acceptance/SOURCES.md) 和 tests/data/local-inputs.json 固定来源、许可及 SHA-256。没有必要样本时在本阶段停止，不用旧工程或跳过代替。

可以从已有本地检出复制清单所列原件。设置 sourceRoot 为实际来源；复制前后核对字节，不覆盖不同内容，也不复制旧候选、工程或报告。清单中仅供本地验收或发布许可待核的样本继续放在忽略目录，不随 ZIP 或 Git 分发。

~~~powershell
$copyInputs = @'
import hashlib, json, shutil, sys
from pathlib import Path
source_root, root = map(lambda value: Path(value).resolve(), sys.argv[1:])
catalog = json.loads((root / 'tests/data/local-inputs.json').read_text(encoding='utf-8'))
for entry in catalog['files'].values():
    relative = Path(entry['path'])
    source, target = source_root / relative, root / relative
    assert source.resolve().is_relative_to(source_root / 'tests/data/local'), source
    assert target.resolve().is_relative_to(root / 'tests/data/local'), target
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256'], source
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(source, target)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == entry['sha256'], target
print('INPUT_COPY_PASSED:', len(catalog['files']))
'@
$sourceRoot = '<已有原件的仓库绝对路径>'
Invoke-QCCheck 'copy-inputs' $blenderPython @('-I', '-c', $copyInputs, $sourceRoot, $repo)
Invoke-QCCheck 'inputs' $blenderPython @('-I', 'tools/local_inputs.py')
~~~

已在当前检出准备原件时，只执行 inputs 检查。QCBLENDER_REFERENCE_ROOT 可显式指向相同清单的输入仓库，但部分日志回归和恢复工具直接读取当前 tests/data/local/log-examples；以上复制方式无需该变量。必要输入不存在、摘要不同或超出清单规定用途时，应记录阻塞。

## 首次环境准备

仅在依赖下载和隔离安装已获授权后执行。新工作树初始不应存在 backend-wheel.json 或依赖上一检出的 science 目录。可显式复制依赖缓存：锁定 wheels 按 dependencies.lock.json 校验，GBasis 原始 ZIP 按 science-sources.lock.json 校验；后端 wheel 和资格报告由本次生成。

~~~powershell
Invoke-QCCheck 'prepare' $blenderPython @('-I', 'tools/prepare_build.py', '--uv', $uv)
Invoke-QCCheck 'dependencies' $blenderPython @('-I', 'tools/fetch_dependencies.py')
$sourceLockBytes = [System.IO.File]::ReadAllBytes("$repo/science-sources.lock.json")
Invoke-QCCheck 'backend' $blenderPython @('-I', 'tools/build_science_backend.py')
$sourceLockText = [System.IO.File]::ReadAllText("$repo/science-sources.lock.json").Replace("`r`n", "`n")
if ($sourceLockText -ne $utf8.GetString($sourceLockBytes).Replace("`r`n", "`n")) { throw 'Science source lock changed' }
[System.IO.File]::WriteAllBytes("$repo/science-sources.lock.json", $sourceLockBytes)
$locked = Get-Content dependencies.lock.json -Raw | ConvertFrom-Json
$backend = Get-Content outputs/backend-wheel.json -Raw | ConvertFrom-Json
$scienceWheels = @($locked.packages.filename) + @($backend.filename)
$scienceWheels = @($scienceWheels | ForEach-Object { Join-Path $wheels $_ })
Invoke-QCCheck 'science-install' $uv (@('pip', 'install', '--python', $blenderPython, '--target', $scienceSite, '--no-deps') + $scienceWheels)
~~~

prepare_build 固定工具版本，fetch_dependencies 核对每个 wheel，build_science_backend 从固定 GBasis 源码生成纯 Python wheel 和 outputs/backend-wheel.json。科学源码锁由工具重写时，仅在文本完全一致后恢复其原字节，保留原有换行；内容变化直接失败。完成后检查两个锁文件没有改动。首次路径接着执行下方共同流程，不提前调用 build_extension。

## 增量构建准备

已有环境先运行输入检查，再核对已有工具、科学依赖和 wheels；缺少准备产物时回到首次路径，不隐式使用其他检出的 backend-wheel.json。

~~~powershell
$checkEnvironment = @'
from importlib.metadata import distributions
import hashlib, json
from pathlib import Path
root = Path.cwd()
expected = dict(line.split('==') for line in (root / 'tools/build-requirements.txt').read_text().splitlines() if line)
actual = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in distributions(path=[str(root / 'outputs/build-site')])}
assert all(actual.get(name.lower().replace('_', '-')) == version for name, version in expected.items())
backend = json.loads((root / 'outputs/backend-wheel.json').read_text())
packages = json.loads((root / 'dependencies.lock.json').read_text())['packages'] + [backend]
science = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in distributions(path=[str(root / 'outputs/science')])}
for package in packages:
    wheel = root / 'outputs/wheels' / package['filename']
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == package['sha256'], wheel
    assert science.get(package['name'].lower().replace('_', '-')) == package['version'], package['name']
print('BUILD_ENVIRONMENT_PASSED')
'@
Invoke-QCCheck 'environment' $blenderPython @('-I', '-c', $checkEnvironment)
~~~

环境核对通过后，增量与首次路径均执行以下流程。产品源码变化必须构建新候选并复验；已有环境不意味着旧测试报告可沿用。

## 科学与非科学检查

~~~powershell
Invoke-QCCheck 'science' $blenderPython @('-I', 'tools/run_science_tests.py', '--site', $scienceSite, '--output', "$batch/science.json")
foreach ($test in @('test_copy_display.py', 'test_legend_layout.py', 'test_local_inputs.py', 'test_storage_cleanup.py')) {
    Invoke-QCCheck ($test.Replace('.py', '')) $blenderPython @('-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', $test)
}
Invoke-QCCheck 'helpers' $blender @('--background', '--factory-startup', '--offline-mode', '--disable-autoexec', '--python-exit-code', '1', '--python', 'tools/verify_node_helpers.py')
~~~

科学报告记录 tests/failures/errors/skipped 和参考误差；核对实际样本与数量，必要样本不能 skipped。节点辅助测试比较实际源原子编号及固定公共接口，范围与上轮十组完整节点图对照分别记录。完整网格收敛实验另由 qualify_scientific_fields.py 执行；未执行记 Not Run。

公共教程批次先从[ARTIFACTS](ARTIFACTS.md)核对公开样本包与输入摘要，再执行解析检查。sourceRoot沿用输入检查中已核对的主检出；包不存在时停止，不从旧报告继承通过。

~~~powershell
$tutorialPackage = Join-Path $sourceRoot 'outputs/evidence/2026-09-30/public-tutorial/samples/qcblender-public-tutorial-samples-v1.zip'
Invoke-QCCheck 'tutorial-samples' $blenderPython @('-I', 'tools/verify_tutorial_samples.py', '--reference-root', $sourceRoot, '--package', $tutorialPackage, '--report', "$batch/tutorial-samples.json")
~~~

`--checkpoints`仅由已有PySCF计算环境执行，解释器/版本单列，不作为插件依赖。完整命令见本轮验证索引；缺必要checkpoint时在该检查停止，新批次不覆盖旧报告。

## 打包与离线安装

~~~powershell
Invoke-QCCheck 'build' $blenderPython @('-I', 'tools/build_extension.py', '--blender', $blender, '--wheels-dir', $wheels, '--output-dir', "$batch/dist")
$candidate = "$batch/dist/qcblender-0.0.1.zip"
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

检查实际渲染。图例初建和第一次重开的报告 status 为 Not Run，表示完整双冷重开链尚未完成；保留这些阶段快照，用第二次重开后的完整 Passed 报告参加资格汇总。更广范围按改动选择 [SOP](v1-acceptance/SOP.md) 和专项工具；已有工具不等于每项命令对当前候选均通过。GUI 实际点击、完整 SOP、性能、独立人工签署及其他平台分别记录，不由包资格推导。

## 生成索引与汇总资格

以下可执行示例将本批实际报告及命令收据绑定到同一 ZIP。命令收据仅说明相应命令成功；覆盖范围仍按工具的实际断言声明。只收录已执行且 Passed 的检查；Failed / Not Run 写入任务或受版本控制的验证索引。

~~~powershell
$makeIndex = @'
import hashlib, json, sys
from pathlib import Path
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
    json.dumps({'candidate_sha256': digest, 'checks': checks}, indent=2) + '\n', encoding='utf-8')
print('EVIDENCE_INDEX_PASSED:', len(checks), digest)
'@
Invoke-QCCheck 'index' $blenderPython @('-I', '-c', $makeIndex, $batch, $candidate)
$installed = "$env:BLENDER_USER_RESOURCES/extensions/user_default/qcblender"
if (-not (Test-Path -LiteralPath "$installed/__init__.py")) { throw 'Installed extension source directory missing; inspect the installation log' }
Invoke-QCCheck 'qualification' $blenderPython @('-I', 'tools/qualify_package.py', '--candidate', $candidate, '--installed-dir', $installed, '--evidence-index', "$batch/evidence-index.json", '--output', "$batch/qualification.json")
~~~

安装目录须是本批实际扩展源码目录，可从安装日志核对。资格工具比较源码、ZIP、wheel、安装副本与报告身份，不执行 Blender 检查，也不判断覆盖是否充分。检查 qualification 的 source_commit 与本批提交一致，并保存源码文件清单、工具版本和报告摘要。修改被验证源码后必须重新构建复验。

文件系统受限时保留真实错误，必要时按既有授权在宿主执行；不能吞错、改 ACL 或修改科学行为规避。阶段结束按 [存储维护规则](agents/storage-maintenance.md) 保留工程、必要输入、环境及日志。技术资格与独立人工验收分别维护。
