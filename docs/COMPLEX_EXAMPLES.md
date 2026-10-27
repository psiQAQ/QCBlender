# 复杂量化案例集 (Complex Examples)

本文档记录四个真实 Gaussian 历史验证案例及其重建参数。历史场景和成片已纳入[产物清理](../validation/agent/acceptance/storage-cleanup.md)，下表路径用于定位历史记录，当前不提供这些现成工程。需要使用时按[附录重建流程](#rebuild)从集中输入生成新的 `.blend` 与配套 `.qcdata/`，并验证新候选。

> [!NOTE]
> 本文案例采用 STO-3G 小基组计算，主要用于检验插件在多类型数据组合下的可视化能力、节点兼容性及渲染表现，不作为高精度科研物理结论。RDG 等预处理计算由离线脚本准备，非插件内置 SCF 计算功能。

---

## 案例一览与典型参数

移动或复制工程场景时，**必须将同名的 `.qcdata/` 目录与 `.blend` 一同存放**。

| 案例名称与体系特征 | 场景工程与渲染成果 | 涉及物理量与典型显示参数 |
| --- | --- | --- |
| **DVB 自由基阳离子**<br>(20 原子，+1 价，双重态) | • 场景：`outputs/complex-examples/orbitals/orbitals.blend`<br>• 轨道与自旋密度：`orbitals-spin.png`<br>• 体积雾：`spin-fog.png` | • 方法：UB3LYP<br>• Alpha SOMO (轨道 35)，等值面 ±0.045 bohr^-3/2<br>• 自旋密度 (α−β)，等值面 ±0.002 e/bohr³<br>• 包含 Beta HOMO (34) 及全密度分量视图 |
| **中性 DVB 分子**<br>(20 原子，中性单重态) | • 场景：`outputs/complex-examples/vibration/vibration.blend`<br>• 简正振动与 IR 谱：`vibration-ir.png`<br>• 振动动画：`vibration-ir.mp4` (24 fps) | • 方法：B3LYP<br>• 54 个简正振动模式<br>• 默认最强红外模式 45 (3396.43 cm⁻¹)<br>• 振幅缩放 0.35 Å，动画播放频率 1 Hz（展示用标度） |
| **色氨酸分子**<br>(27 原子，中性单重态) | • 场景：`outputs/complex-examples/polar/polar.blend`<br>• ESP / 电荷 / 偶极：`density-esp-charges.png`<br>• ESP 空间截面切片：`esp-slice.png` | • 方法：RHF<br>• 电子密度等值面：0.004 e/bohr³<br>• ESP 表面着色色域：±0.05 hartree/e<br>• Mulliken 电荷着色范围：±0.6 e；偶极矢量比例：1.5 Å/Debye |
| **水二聚体弱相互作用**<br>(6 原子，中性单重态) | • 场景：`outputs/complex-examples/interaction/interaction.blend`<br>• 氢键 RDG 区域：`hydrogen-bond-rdg.png` | • 方法：PBE<br>• RDG 等值面：0.5，以 sign(λ₂)ρ 映射着色<br>• 映射范围：−0.035 / 0 / +0.02 e/bohr³ (蓝/绿/红) |

---

## 核心操作与交互要点

1. **多层轨道与自旋显示**：
   在轨道场景中，通过显示层分别控制正负相位、材质着色、实体/线框/点云（Solid / Wire / Points）显示。调整等值阈值时，正负相位可保持对称联动，也可解除联动独立调节。
2. **图层复制与节点隔离**：
   复制显示层后，新图层将获得独立的外层几何节点修改器参数。可分别指定不同的截断阈值或材质样式，底层计算网格与科学缓存保持只读共享。
3. **静电势表面着色与空间探针**：
   在色氨酸案例中，以电子密度曲面作为空间几何载体，将静电势场数值直接映射到曲面材质。场景内保留了 2D 剖面切片与原子电荷模型，并可通过 3D 游标探针读取网格点的具体数值。
4. **振动模式与红外光谱联动**：
   在振动工程中切换振动模式序号并播放时间轴，分子将沿简正坐标运动，同时视口中的 IR 光谱峰标会自动定位到对应吸收频率。
5. **弱相互作用分析 (RDG / NCI)**：
   利用几何节点将 RDG 空间场作为等值面生成源，同时绑定带符号密度 `sign(λ₂)ρ`（ρ 乘密度 Hessian 第二特征值的符号） 作为色彩源，实现经典 NCI 绿/蓝区域映射。

---

## 数据来源与依赖规范

各案例的上游来源与校验记录详见 [案例来源配置](../validation/shared/data/complex-example-sources.json)：

- **cclib 测试数据集** (BSD-3-Clause)：DVB 阳离子与色氨酸算例原始输出。
- **ChemTools 测试数据** (GPL-3.0+)：水二聚体与弱相互作用原始结构。

离线预处理脚本使用 GBasis 计算空间网格中的密度一阶梯度与 Hessian 矩阵，生成的 RDG 与密度特征值网格遵循标准量化定义。

---

<a id="appendix"></a>
## 附录：来源处理与复建

- [来源、缩放及历史数值核对](#source-processing)
- [从集中输入重建案例](#rebuild)

<a id="source-processing"></a>
### 来源、缩放及历史数值核对

[来源清单](../validation/shared/data/complex-example-sources.json) 固定上游提交、URL、SHA-256 和仓库许可证。原始文件及许可证留在忽略的 `validation/shared/data/local/complex-examples/`，统一索引见 [数据目录](../validation/shared/data/README.md)。

- [cclib 测试数据](https://github.com/cclib/cclib/tree/f90be37ffa1ab4cfec97495bdd01d670ca329f17/data)：DVB、色氨酸，BSD-3-Clause 仓库。
- [ChemTools 数据](https://github.com/theochem/chemtools/tree/47c9fe255848b8dbc6f589beb738421f76401885/chemtools/data)：水二聚体及 NCIPLOT/ELF Cube，GPL-3.0-or-later 仓库。ELF 只登记为可选素材，不宣称新增其内置计算。

准备脚本复用随包 GBasis，在单独后台进程求密度梯度和 Hessian。RDG 为 `|∇ρ| / [2(3π²)^(1/3)ρ^(4/3)]`；λ₂ 是密度 Hessian 按升序排列的第二个特征值。保存未过滤 RDG、未放大的带符号密度、显示专用的过滤 RDG。

网格 38×56×39，间距 0.12 Å。密度不在 `[1e-6, 0.05] electron/bohr³` 时，显示 RDG 置为 10，以排除核心和极低密度区域；原始未过滤场另存。

上游 NCIPLOT `dens.cube` 为 **100×sign(λ₂)ρ**，参考 RDG 中 457 点为过滤哨兵。去除倍率并仅对照未过滤 RDG 点，最大绝对差分别约 4.71e-6 electron/bohr³、5.02e-5。导数另与中心差分交叉检查；生成 Cube 经写入重读核对。


<a id="rebuild"></a>
### 从集中输入重建案例

在仓库根目录 PowerShell 执行。先按 [DEVELOPMENT](DEVELOPMENT.md) 从当前源码构建并安装新候选，沿用该隔离配置及 `$blender` / `$blenderPython`。已有输入先运行 `tools/local_inputs.py`；仅缺输入且下载已获授权时运行 `tools/fetch_complex_examples.py`。以下脚本固定写入 `outputs/complex-examples/`，先确认该目录没有需保护的旧工程。

```powershell
& $blenderPython -I tools/local_inputs.py
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

上述数值和运行耗时为历史记录，本次文档修订未重跑四例流程。当前候选与独立验收状态以 [VALIDATION](VALIDATION.md) 为准；历史技术检查和 Agent 画面检查不替代独立用户或科研验收。
