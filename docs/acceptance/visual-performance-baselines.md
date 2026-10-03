# 固定视觉与性能基准

视觉参考位于 `tests/data/visual-baseline/`。六个场景使用真实 CH4 FCHK，分别覆盖原子/键、双相 MO8、密度/ESP 有效域、切片/轮廓、雾、图例/源原子距离标注。PNG 和 JSON 一起版本化；JSON 保存输入和科学数组摘要、环境、场景参数及检查区域。初始图由 Agent 逐图检查，独立人工认可为 **Not Run**。

视觉配置为 Blender 5.1.1、Cycles CPU、32 samples、seed 17、640×448、4线程、Standard/sRGB、关闭自适应采样和降噪。字体使用该 Blender 构建内置 Bfont。每张全图及各固定区域均须满足 RGB MAE ≤ 0.003，任一通道差值大于 8/255 的像素比例 ≤ 0.01。环境或科学身份不符、缺图、尺寸不符直接失败。差异图放大8倍便于定位，不参与阈值计算。

以下为 PowerShell 命令，在仓库根目录运行。先按 [DEVELOPMENT](../DEVELOPMENT.md) 构建并安装当前候选到本任务隔离 Blender 配置，再设置 `BLENDER_USER_CONFIG`、`BLENDER_USER_EXTENSIONS`、`BLENDER_USER_DATAFILES`、`TEMP`、`TMP`；所有目录放在新的 `outputs/runs/<任务>/` 下。目标目录必须尚不存在，避免覆盖旧证据。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/render_visual_baseline.py -- --case signed-mo --output outputs/runs/visual-check-1
```

`--case` 可选 `atoms`、`signed-mo`、`density-esp`、`slice-contours`、`fog`、`legend-annotations`。默认 `compare` 只读取参考图；每次保存候选图、差异图、报告和自包含工程。保存后使用同一安装环境的新进程运行 `--reopen <工程.blend>`，比较相同参考并核对全部科学数组。

新参考候选使用 `--mode record --output <新待审目录>`，逐图检查后单独审查 PNG/JSON 变更。不要把失败的比较结果自动接受为参考图。`--mutation` 支持 `hide-negative`（signed-mo）、`legend-unit`、`legend-position`（legend-annotations）、`disable-valid-mask`（density-esp）；资格验证要求它们产生实际像素比较 **Failed**，环境或加载异常不能作为成功检出。

性能运行使用两个不同的新配置目录。以下示例测量场求值；显示基准将脚本换为 `tools/benchmark_display.py`，并使用另一个新 `profile-root` 和 `output`。

```powershell
$benchmarkRoot = Join-Path $PWD 'outputs/runs/performance-fields-1'
New-Item -ItemType Directory -Path "$benchmarkRoot/config", "$benchmarkRoot/extensions", "$benchmarkRoot/temp"
$env:BLENDER_USER_CONFIG = "$benchmarkRoot/config"
$env:BLENDER_USER_EXTENSIONS = "$benchmarkRoot/extensions"
$env:TEMP = "$benchmarkRoot/temp"
$env:TMP = "$benchmarkRoot/temp"
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/benchmark_fields.py -- --profile-root $benchmarkRoot --candidate outputs/dist/qcblender-0.0.1.zip --output outputs/runs/performance-fields-report-1
```

两工具默认预热1次、正式5次。场基准测量64³/128³/256³冷/热求值及导入；热缓存采用同一输入Dataset、独立worker，冷缓存只删除本任务已核对摘要的索引，不清空操作系统缓存。显示基准测量1/8/32套原子和双相MO视图，计时阈值更新、原子筛选至依赖图完成、提面和最终CPU渲染。它不测量视口FPS。

`report.json` 保存原始耗时、median/min/max、对应worker或Blender进程的生命周期峰值内存、硬件、候选、输入和脚本摘要。显示组共享同一Blender进程，因此后续组的进程峰值可能包含前组高水位。`--baseline <旧report.json>` 只比较环境及参数兼容的报告；速度变化仅记录，无阻断阈值。错误缓存命中、科学数组变化、异常及超时仍为 **Failed**。worker有执行期限；阻塞的Blender主线程调用还需启动器设置外层进程期限。

本批结果及保全位置统一通过 [ARTIFACTS](../ARTIFACTS.md) 查找。技术验证不替代独立科研签署。
