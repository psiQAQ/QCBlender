# Windows 构建与验收

目标为 Windows x64、Blender 5.1.1、宿主 CPython 3.13.9 / NumPy 2.3.4 / OpenVDB 13。以下命令在仓库根目录的 PowerShell 执行。构建者需要 Blender 和已有 uv；验收机器只需要 Blender 与扩展 ZIP。

## 构建

设置本机路径。当前验证使用 uv 0.11.19；构建工具版本固定在 `tools/build-requirements.txt`。全部下载和中间文件进入忽略的 `outputs/`，不向 Blender Python 安装构建工具。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$blenderPython = 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe'
$uv = 'C:/Users/ustcw/.local/bin/uv.exe'
& $blenderPython -I tools/prepare_build.py --uv $uv
& $blenderPython -I tools/fetch_dependencies.py
& $blenderPython -I tools/build_science_backend.py
& $blenderPython -I tools/build_extension.py --blender $blender
```

每条命令成功后再执行下一条。依赖下载严格遵循 `dependencies.lock.json` 的 URL/SHA-256；源码固定在 `science-sources.lock.json`。GBasis 只打包未修改的 Python 数值实现，使用 setuptools 生成标准 wheel，排除可选原生积分接口；`outputs/backend-wheel.json` 保存产物摘要。ZIP 时间戳可能产生不同哈希，需重新验收，不能声称逐字节可重现。

产物为 `outputs/dist/qcblender-0.0.1.zip`。ZIP 含所需 wheels 与许可文本，运行时不调用 pip/uv、不下载包；NumPy/OpenVDB 使用宿主版本。`THIRD_PARTY.md` 记录源码许可事实和发行材料要求。

## 科学验收

将随包 wheels 安装到仓库专用测试目录，保留宿主 NumPy。这里是开发验证命令，不是最终用户安装步骤。

```powershell
$env:UV_CACHE_DIR = "$PWD/outputs/uv-cache"
$env:TEMP = "$PWD/outputs/process-temp"
$env:TMP = $env:TEMP
$locked = Get-Content dependencies.lock.json -Raw | ConvertFrom-Json
$backend = Get-Content outputs/backend-wheel.json -Raw | ConvertFrom-Json
$scienceWheels = @($locked.packages.filename) + @($backend.filename)
$scienceWheels = $scienceWheels | ForEach-Object { Join-Path "$PWD/outputs/wheels" $_ }
& $uv pip install --python $blenderPython --target outputs/science --no-deps $scienceWheels
& $blenderPython -I tools/fetch_log_examples.py
& $blenderPython -I tools/run_science_tests.py
& $blenderPython -I tools/qualify_scientific_fields.py
```

来源、版本、SHA-256 和许可证随 `tests/data/` 样本保存。许可边界不清晰的公开 Log 只下载到 `outputs/log-examples`，不作为扩展内容分发：

```powershell
& $blenderPython -I tools/fetch_log_examples.py
```

快速回归输出 `outputs/science-reference.json`；网格积分与带电远场检查输出 `outputs/scientific-convergence.json`。独立 Cubegen/Fortran 参考、代数不变量、网格收敛是不同证据，不能互相替代。

## Blender 原生验收

使用隔离配置、关闭自动脚本和网络。测试自己创建的场景及进程，不写入日常 Blender 配置。

```powershell
$env:BLENDER_USER_RESOURCES = "$PWD/outputs/blender-acceptance"
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_extension.py --python tools/verify_node_assets.py
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_storage_paths.py
& $blender --background --offline-mode --disable-autoexec 'outputs/acceptance/moved 中文 path/mo8.blend' --python-exit-code 1 --python tools/verify_extension.py -- --reopen
& $blender --background --offline-mode --disable-autoexec 'outputs/acceptance/moved 中文 path/mo8.blend' --python-exit-code 1 --python tools/verify_project_recovery.py
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_visual_features.py
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_animation.py
& $blender --background --offline-mode --disable-autoexec 'outputs/animation-acceptance/water-mode.blend' --python-exit-code 1 --python tools/verify_saved_views.py
& $blender --background --offline-mode --disable-autoexec 'outputs/visual-acceptance/density-esp.blend' --python-exit-code 1 --python tools/verify_saved_views.py
& $blender --background --offline-mode --disable-autoexec 'outputs/acceptance/moved 中文 path/mo8.blend' --python-exit-code 1 --python tools/verify_failed_save.py
& $blender --background --offline-mode --disable-autoexec 'outputs/acceptance/moved 中文 path/mo8.blend' --python-exit-code 1 --python tools/probe_scalar_views.py
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/benchmark_fields.py
```

`verify_extension.py` 安装当前 ZIP，验证运行库来源、后台计算/取消、重复场缓存、双相和阈值，生成渲染并保存可迁移工程；带 `--reopen` 在新目录冷启动并核对数组身份及网格数量。`verify_storage_paths.py` 必须在 Blender 宿主中运行，验证超过 260 字符的数组路径；独立 Python 的 Windows 长路径行为不能代替这项检查。`verify_project_recovery.py` 验证缺失缓存恢复、重定位、电荷/偶极及振动/IR。报告位于 `outputs/acceptance/`。

在限制文件系统的 Agent 沙箱内，Blender 原生安装器可能无法将扩展暂存目录重命名；该测试需要宿主批准相应的本地安装操作。这不属于最终用户的插件依赖。

当前技术状态以 `.scratch/qcblender-v1/issues/` 和实际报告为准。独立用户验收不得由 Agent 代签。

`verify_node_assets.py` 在原生安装测试创建场之后执行，检查公共等值面节点的参数/源对象隔离、已有分支连接保留及无对象/材质绑定的 `.blend` 资产导出和重新加载；报告为 `outputs/node-assets/report.json`。

体积雾检查复用原生安装测试生成的轨道工程：

```powershell
& $blender --background --offline-mode --disable-autoexec 'outputs/acceptance/moved 中文 path/mo8.blend' --python-exit-code 1 --python tools/verify_fog.py
& $blender --background --offline-mode --disable-autoexec 'outputs/fog-acceptance/fog.blend' --python-exit-code 1 --python tools/verify_fog.py -- --reopen-fog
```

`outputs/fog-acceptance/report.json` 记录正负颜色、零不透明度、连续透明度、缓存不变和保存后渲染一致性。

显示层检查分为数据/节点操作、冷重开和实际 GUI 撤销：

```powershell
& $blender --background --offline-mode --disable-autoexec 'outputs/acceptance/moved 中文 path/mo8.blend' --python-exit-code 1 --python tools/verify_layers.py
& $blender --background --offline-mode --disable-autoexec 'outputs/layer-acceptance/layers.blend' --python-exit-code 1 --python tools/verify_layers.py -- --reopen-layers
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_layers.py -- --vibration-layers
& $blender --offline-mode --disable-autoexec 'outputs/layer-acceptance/layers.blend' --python-exit-code 1 --python tools/verify_layers_gui.py
```

最后一条需 GUI，脚本自动检查撤销/重做、截取显示层面板并退出本次 Blender；继续使用上述隔离配置。`outputs/layer-acceptance/report.json` 汇总结果。振动复制检查重新导入真实 Gaussian 样本，不依赖其他会话生成的旧缓存权限。

完成相应检查后运行 `& $blenderPython -I tools/qualify_package.py`，核对最终 ZIP 与当前源码、随包 wheel 哈希，并汇总已有报告。它不代替上述 Blender 验收命令。
## 开发问题记录

实际故障、处理和复验状态见 [开发问题与复验记录](DEVELOPMENT_PITFALLS.md)。新增记录须区分已复现故障、静态发现和待验证推断。
