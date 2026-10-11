Triage: ready-for-agent
Status: resolved
Blocked by: 01

# 原子样式性能测量

单原子对象规模、三样式和Quality分阶段测量；固定工程输入和冷热条件，记录耗时、内存、源码与环境身份。只交基准和诊断，不预承诺优化。Blender运行由主Agent串行执行。

## Comments

- 2026-10-11 性能工具子 Agent 领取。前置 01 已 resolved；独占 tools/benchmark_atom_styles.py、tests/test_atom_benchmark.py 与本任务，原生 Blender 运行由主 Agent 在 05/06 串行执行。

## Answer

实现交付完成：`tools/benchmark_atom_styles.py` 复用现有隔离安装、Python 文件一致性、环境身份、报告及比较能力；不修改产品，不新增依赖。源码 commit、产品 tree、安装模块和 manifest、候选 ZIP、工具、CPU/Blender/依赖版本及源 CH4 FCHK SHA-256 均写入报告。

默认矩阵为单载体 32/128/512 原子、ball-stick/space-fill/bonds、Quality 1/3；预热 1、正式 3，每种条件分别测量创建、显式 depsgraph 完成及 evaluated_get、to_mesh 提取。冷条件重建本批节点资产，热条件创建新载体并复用冷轮节点资产；两者均不清理 OS cache、均重新读取 Dataset。内存同时记录阶段边界当前 WorkingSetSize 和进程生命周期 PeakWorkingSetSize，后者不归属于单个阶段。Quality 对当前固定 8 段键管没有独立分辨率作用，报告明确保留此语义。

种子在当前 Blender 进程解析；工具不启动 Blender worker，不连接 MCP，不终止外部进程。工程负载按源原子顺序重复 CH4 至精确目标数，末尾构型允许截断，只保留端点有效的构型内键；记录生成参数和每个文件摘要，标明不是新的计算科学体系。每轮检查原始输入、种子和生成 Dataset 文件不变，载体原子 ID/元素/位置/键、实际单对象数量、节点/材质数、求值网格数量和重复计数。新输出目录拒绝覆盖；矩阵、重复数、Quality 和预估几何有显式预算。

- Passed：`python -S -m unittest discover -s tests -p test_atom_benchmark.py -v`，9 项。
- Passed：`python -S -m py_compile tools/benchmark_atom_styles.py tests/test_atom_benchmark.py`、`python -S tools/benchmark_atom_styles.py --help`、`git diff --check`。
- Not Run：原生 Blender 烟测及完整性能矩阵，由主 Agent 在合并后的 main、当前完整候选上串行执行，归入 05/06 证据。本任务 resolved 表示实现与纯 Python 边界验证完成，不代表原生运行或独立科研接受完成。

### 主 Agent 原生运行命令

以下 PowerShell 在最终 main 根目录执行，先完成当前候选构建并确认没有其他 Blender 进程。首次设置二进制和该 main 构建的候选；每次运行使用一个全新目录。`--timeout` 是原生阻塞调用返回后的超时检查；若需要硬期限，由主 Agent 启动器控制且只管理其持有的进程。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$candidate = Join-Path $PWD 'outputs/dist/qcblender-0.1.0.zip'
$benchmarkRoot = Join-Path $PWD 'outputs/runs/upstream-20261011-atoms-smoke'
if (Test-Path $benchmarkRoot) { throw 'Use a new benchmark root' }
New-Item -ItemType Directory -Path "$benchmarkRoot/config", "$benchmarkRoot/extensions", "$benchmarkRoot/datafiles", "$benchmarkRoot/cache", "$benchmarkRoot/temp"
$env:BLENDER_USER_RESOURCES = $benchmarkRoot
$env:BLENDER_USER_CONFIG = "$benchmarkRoot/config"
$env:BLENDER_USER_EXTENSIONS = "$benchmarkRoot/extensions"
$env:BLENDER_USER_DATAFILES = "$benchmarkRoot/datafiles"
$env:BLENDER_USER_CACHE = "$benchmarkRoot/cache"
$env:TEMP = "$benchmarkRoot/temp"
$env:TMP = "$benchmarkRoot/temp"
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/benchmark_atom_styles.py -- --profile-root $benchmarkRoot --candidate $candidate --output "$benchmarkRoot/report" --atoms 5 --qualities 1 --styles ball-stick,space-fill,bonds --warmups 0 --repeats 1 --timeout 120
if ($LASTEXITCODE -ne 0) { throw 'Atom benchmark smoke failed' }
```

完整矩阵在烟测进程正常退出后执行；仍使用最终 main 和相同候选。

```powershell
$benchmarkRoot = Join-Path $PWD 'outputs/runs/upstream-20261011-atoms-matrix'
if (Test-Path $benchmarkRoot) { throw 'Use a new benchmark root' }
New-Item -ItemType Directory -Path "$benchmarkRoot/config", "$benchmarkRoot/extensions", "$benchmarkRoot/datafiles", "$benchmarkRoot/cache", "$benchmarkRoot/temp"
$env:BLENDER_USER_RESOURCES = $benchmarkRoot
$env:BLENDER_USER_CONFIG = "$benchmarkRoot/config"
$env:BLENDER_USER_EXTENSIONS = "$benchmarkRoot/extensions"
$env:BLENDER_USER_DATAFILES = "$benchmarkRoot/datafiles"
$env:BLENDER_USER_CACHE = "$benchmarkRoot/cache"
$env:TEMP = "$benchmarkRoot/temp"
$env:TMP = "$benchmarkRoot/temp"
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/benchmark_atom_styles.py -- --profile-root $benchmarkRoot --candidate $candidate --output "$benchmarkRoot/report" --atoms 32,128,512 --qualities 1,3 --styles ball-stick,space-fill,bonds --warmups 1 --repeats 3 --timeout 900
if ($LASTEXITCODE -ne 0) { throw 'Atom benchmark matrix failed' }
```
