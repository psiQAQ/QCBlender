# 复杂量子化学案例集

四例使用真实 Gaussian 结果，保留可编辑几何节点和科学数据。均为 STO-3G 小基组计算，适合演示及软件回归，不作为高精度科研计算结论。外部 RDG 预处理仅存在于案例准备脚本，不属于插件内置求值功能。

## 打开与展示

安装 `outputs/dist/qcblender-0.0.1.zip` 后打开以下场景。移动场景时必须同时复制同名 `.qcdata` 目录。PNG 和 MP4 可直接查看。

| 案例 | 场景与成片 | 物理量与参数 |
| --- | --- | --- |
| DVB 自由基阳离子，20 原子，+1 / 双重态 | [场景](../outputs/complex-examples/orbitals/orbitals.blend)、[轨道与自旋](../outputs/complex-examples/orbitals/orbitals-spin.png)、[线框](../outputs/complex-examples/orbitals/orbital-wire.png)、[点](../outputs/complex-examples/orbitals/orbital-points.png)、[体积雾](../outputs/complex-examples/orbitals/spin-fog.png) | UB3LYP；Alpha SOMO 35，等值 ±0.045 bohr^-3/2；自旋密度 α−β，等值 ±0.002 electron/bohr³；另存 Beta HOMO 34、总/Alpha/Beta 密度视图 |
| 中性 DVB，20 原子，单重态 | [场景](../outputs/complex-examples/vibration/vibration.blend)、[振动与 IR](../outputs/complex-examples/vibration/vibration-ir.png)、[两秒动画](../outputs/complex-examples/vibration/vibration-ir.mp4) | B3LYP；54 个模式；默认最强 IR 模式 45，3396.4292 cm⁻¹；显示振幅 0.35 Å，播放 1 Hz，非物理时间 |
| 色氨酸，27 原子，中性单重态 | [场景](../outputs/complex-examples/polar/polar.blend)、[ESP / 电荷 / 偶极](../outputs/complex-examples/polar/density-esp-charges.png)、[ESP 切片](../outputs/complex-examples/polar/esp-slice.png) | RHF；密度等值 0.004 electron/bohr³；ESP 色域 ±0.05 hartree/e；Mulliken 电荷色域 ±0.6 e；偶极显示缩放 1.5 Å/D |
| 水二聚体，6 原子，中性单重态 | [场景](../outputs/complex-examples/interaction/interaction.blend)、[氢键区域](../outputs/complex-examples/interaction/hydrogen-bond-rdg.png) | PBE；外部 RDG=0.5，以 sign(λ₂)ρ 着色，−0.035 / 0 / +0.02 electron/bohr³ 对应蓝 / 绿 / 红 |

中性 DVB 与阳离子属于不同计算，分开保存。色氨酸 FCHK 与 Log 原子顺序一致，最大坐标差约 4.99e-7 Å；偶极以 e·bohr 与 Debye 换算后核对。

## 操作与能力覆盖

1. 在轨道场景的 QCBlender 显示层选择左侧轨道，调整 `Isovalue`、`Link Thresholds`、正负相位、材质及透明度。切换 solid / wire / points。正负表示轨道相位；其他已生成物理量默认隐藏，可分别启用。
2. 复制显示层，改变阈值或材质，再排序或删除复制层。复制层的外层节点图独立；进入 Geometry Nodes 可查看公共等值面、样式、采样和颜色映射节点的连接。
3. 色氨酸场景中，密度决定表面位置，ESP 决定颜色。切片与原子 ESP 映射作为隐藏替代视图保留。右侧电荷空间填充模型可切换球棍或只显示键；偶极保持物理方向及源坐标原点。
4. 轨道视图已有裁剪节点，可启用平面或包围盒。选择场视图，将 3D Cursor 放入网格，使用 `Read Field at 3D Cursor` 读取数值及单位。无效/网格外采样不作为物理零值。
5. 振动场景中选择分子，切换模式并播放时间轴，IR 选中峰随之变化。图注描述默认模式，手动换模式后应同步修改图注再出图；展示振幅及播放速度不是实际振动振幅和频率。
6. 相互作用场景分别绑定 RDG 几何来源与带符号密度颜色来源。RDG 等值、颜色范围和颜色中心独立可调；中心明确为零。

| 能力 | 本案例证据 |
| --- | --- |
| Log/FCHK/Cube 导入、状态与单位 | 四例真实导入；来源清单、`source-inspection.json` |
| MO / 总 / Alpha / Beta / 自旋密度 | 轨道案例；总密度=Alpha+Beta、自旋=Alpha−Beta、69电子占据断言 |
| ESP、原子电荷、偶极 | 色氨酸场景及匹配文件坐标、偶极核对 |
| 节点组合、正负相位、阈值、表面/线框/点 | 轨道实际网格、三种渲染及独立阈值检查 |
| 雾、切片、独立场着色 | 自旋雾、ESP 切片、RDG 表面着色 |
| 图层复制/排序/删除、裁剪、游标 | 轨道操作断言；原视图阈值独立、科学缓存不变 |
| 振动、IR、原生动画导出 | 54 模式、48 帧 PNG、24 fps MP4；冷重开后解码帧数 |
| 工程可迁移 | 复制到 `portable/<case>` 后，新进程打开、核对网格和摘要、重新渲染 |

撤销重做、异常输入、解析场精度等细节继续由现有 M6/M7 验收覆盖，见 [验证说明](VALIDATION.md)。案例集不替代全部回归测试。

## 来源与外部预处理

[来源清单](../tests/data/complex-example-sources.json) 固定上游提交、URL、SHA-256 和仓库许可证。原始文件及许可证留在忽略的 `outputs/complex-examples/sources`。

- [cclib 测试数据](https://github.com/cclib/cclib/tree/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data)：DVB、色氨酸，BSD-3-Clause 仓库。
- [ChemTools 数据](https://github.com/theochem/chemtools/tree/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data)：水二聚体及 NCIPLOT/ELF Cube，GPL-3.0-or-later 仓库。ELF 只登记为可选素材，不宣称新增其内置计算。

准备脚本复用随包 GBasis，在单独后台进程求密度梯度和 Hessian。RDG 为 `|∇ρ| / [2(3π²)^(1/3)ρ^(4/3)]`；λ₂ 是密度 Hessian 按升序排列的第二个特征值。保存未过滤 RDG、未放大的带符号密度、显示专用的过滤 RDG。

网格 38×56×39，间距 0.12 Å。密度不在 `[1e-6, 0.05] electron/bohr³` 时，显示 RDG 置为 10，以排除核心和极低密度区域；原始未过滤场另存。

上游 NCIPLOT `dens.cube` 为 **100×sign(λ₂)ρ**，参考 RDG 中 457 点为过滤哨兵。去除倍率并仅对照未过滤 RDG 点，最大绝对差分别约 4.71e-6 electron/bohr³、5.02e-5。导数另与中心差分交叉检查；生成 Cube 经写入重读核对。

## 复建

在仓库根目录 PowerShell 执行。首次下载需要网络，其余步骤使用隔离配置和离线模式；本地安装包须已存在。准备脚本仅在隔离配置缺少插件时通过原生扩展流程安装。

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
$blenderPython = 'C:\Program Files\Blender Foundation\Blender 5.1\5.1\python\bin\python.exe'
$env:BLENDER_USER_RESOURCES = "$PWD/outputs/blender-m8"
& $blenderPython tools/fetch_complex_examples.py
if ($LASTEXITCODE -ne 0) { throw 'Source verification failed' }
& $blender --background --factory-startup --offline-mode --python-exit-code 1 --python tools/prepare_complex_examples.py
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed' }
```

```powershell
foreach ($case in @('orbitals', 'polar', 'interaction')) {
    & $blender --background --factory-startup --offline-mode --python-exit-code 1 --python tools/build_complex_examples.py -- $case
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $case" }
}
& $blender --background --factory-startup --offline-mode --python-exit-code 1 --python tools/build_complex_examples.py -- vibration --animation
if ($LASTEXITCODE -ne 0) { throw 'Animation failed' }
foreach ($case in @('orbitals', 'polar', 'interaction', 'vibration')) {
    & $blender --background --factory-startup --offline-mode --python-exit-code 1 --python tools/verify_complex_examples.py -- $case
    if ($LASTEXITCODE -ne 0) { throw "Cold-open verification failed: $case" }
}
```

`source-inspection.json` 记录科学核对；各例 `report.json` 保存网格、参数、耗时、缓存命中和图层，`reopen.json` 保存可迁移性检查。色氨酸网格 47×33×46，间距 0.28 Å，首次 ESP 本机实测约八分钟，后续命中缓存；该观察值不是性能保证。512 MiB 是求值预算，不是实测进程峰值，且不包含 Blender 和渲染开销。

独立人工验收及发布仍为 **Not Run**。技术检查和 Agent 画面检查不替代用户对操作体验及科研适用性的确认。
