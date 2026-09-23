# 0.0.1 候选的支持范围与验证

日期：2026-09-23。平台：Windows 11 x64，Blender 5.1.1，CPython 3.13.9，NumPy 2.3.4，OpenVDB 13。当前是本地开发验收候选，尚未对外发布；独立用户验收未签署。

## 输入和科学边界

| 能力 | 当前实现与证据边界 |
| --- | --- |
| FCHK | IOData 适配；坐标/原子顺序、SP、球谐/笛卡尔、Alpha/Beta、占据、轨道能量、可用 SCF 密度和性质保留。FCHK 本身不证明计算收敛 |
| Log | cclib 性质 + 自有能量事件适配；G03/G09/G16 样本、Link1 job、正常/异常/截断状态分别处理。多构型 job 不自动把电荷/偶极/模式绑到最后构型 |
| Cube | 单/多 MO、交错、非立方斜轴、坐标单位、损坏数据检查；普通标量保持未知，可显式声明内置量或外部物理量名称/单位，不做猜测或隐式换算 |
| 内置场 | 实值、非周期、全电子 HF/DFT；RHF/UHF/ROHF、UB3LYP 实例。MO、总/Alpha/Beta/自旋密度、核与电子密度 ESP |
| 基组 | SP、球谐/笛卡尔 d/f 和实际 nMO<nAO 回归；g 的 Python 基组不变量另行检查。h 及以上、ECP、幽灵中心、广义/复轨道显式拒绝 |
| 理论层次 | 已确认 SCF 轨道和密度一致才求值。方法白名单见 `evaluate.prepare`；白名单是入口边界，不代表每个泛函/版本组合都有独立参考 |
| 能量 | HF/DFT、MP2、CCSD(T)、DSDPBEP86、明确标记选态的 TD，保留参考/目标/校正/热力学和源位置；多步或冲突不自动取最后值 |
| 后续范围 | B2PLYP 目标规则仍为候选；CASSCF、复合方法等不宣称完整解析。相关方法密度、WFN/WFX、轨迹/IRC、ORCA、周期系统后续交付 |

GBasis 来源固定在 `science-sources.lock.json`，当前 wheel 为 `0.1.0+qcblender.071969c.pure1`，只打包 Python 数值路径。SciPy 等随包 wheels 固定 SHA-256，NumPy/OpenVDB 使用 Blender 自带版本；运行时不调用外部 Python/pip。

## 技术验收

| 项目 | 状态 | 证据 |
| --- | --- | --- |
| 复杂案例集 | Passed | DVB阳离子/振动、色氨酸、水二聚体，4组可迁移工程、8张代表图、48帧MP4；[操作及复建](COMPLEX_EXAMPLES.md)，独立人工验收仍未完成 |
| 解析/归一化/科学回归 | Passed | 20 项测试，`outputs/science-reference.json`；含路径逃逸/损坏摘要拒绝、并发不可变数据复制 |
| MO 独立参考 | Passed | CH4 UHF/cc-pVDZ，27 点 Fortran 参考，Alpha/Beta MO 8/9 最大绝对误差约 4.85e-9 |
| 密度/ESP 独立参考 | Passed | 同一 CH4 的 Gaussian Cubegen 18 点：密度最大误差 8.44e-7 electron/bohr^3，ESP 4.61e-6 hartree/e；只证明对应样本 |
| AO/电子数 | Passed | 开闭壳层、纯/笛卡尔、矩形 MO 的 CᵀSC 与 Tr(PS)；CH4 电子数 9.9999999974 |
| 网格与远场 | Passed | `outputs/scientific-convergence.json`：LiH+ 密度/自旋步长与范围分开变化，半宽 8 bohr、步长 0.1 bohr 得 2.99994998 个电子；200 bohr 的 rΦ=0.99993221，趋向 +1 |
| 全新配置离线安装 | Passed | `outputs/acceptance/extension.json`；后台库来源、GUI 不导入求值依赖、取消、注册/注销、缓存复用 |
| 双相面与显示阈值 | Passed | 阈值改变表面网格，正/负面独立，VDB 哈希不变；`outputs/acceptance/mo8.png` 已作视觉检查 |
| 公共等值面资产 | Passed | `outputs/node-assets/report.json`：无对象/材质绑定的共享资产，独立阈值与源平移、保留原分支、资产库导出和重载 |
| 可组合节点与常用样式 | Passed | `outputs/composable/report.json`：三种原子/表面样式、修改器重排、保留分支/旧图、映射后独立相位透明度、平面/盒裁剪、斜轴与无效域游标采样；真实 Gaussian 三种表面渲染已检查 |
| 体积雾 | Passed | `outputs/fog-acceptance/report.json`：真实 Cycles 渲染的正负颜色、零/连续不透明度、缓存摘要不变及冷重开渲染一致；图片已检查 |
| 显示层管理 | Passed | `outputs/layer-acceptance/report.json`：增删、复制、排序/可见性、独立材质及模式/IR，保存重开和 GUI 撤销/重做；面板截图已检查 |
| 双场与切片 | Passed | `outputs/scalar-probe/result.json`：斜轴线性场采样最大误差约 1.08e-6，对象变换后约 2.27e-6；域外 289 个切片点全为无效 |
| 原子、图例和关联 | Passed | `outputs/visual-acceptance-v2/result.json`：元素/编号选择、真实密度/ESP、与范围联动的图例、刚体配准、平衡距离、Cube 显式单位及外部场声明；渲染已检查 |
| 电荷/偶极/振动/IR | Passed | `outputs/acceptance/recovery.json`、`outputs/vibration-probe.json`：Mulliken、偶极方向/比例/零向量、3 个水分子模式、真实位移方程、位移箭头、IR 高亮 |
| 动画导出 | Passed | `outputs/animation-acceptance-v2/result.json`；原生 Blender 渲染 4 张 PNG，图注保留频率及非物理播放速度，源科学数组完全不变；已检查代表帧 |
| 保存、中文路径、迁移恢复 | Passed | 配套 `.blend + .qcdata`、ZIP、移动后冷启动、缺 VDB 重建、按 manifest 摘要重定位；数组和表面保持一致 |
| 保存失败的回滚 | Passed | `outputs/acceptance/failed-save.json`：真实 Blender 保存失败后，先前场景索引与内存中的对象/体文件引用保留 |
| Windows 长路径数组 | Passed | `outputs/acceptance/storage-paths.json`：Blender 宿主内超过 260 字符的数组路径可读取、复制复用和归档；深层隔离配置中的实际重复场缓存命中 |
| 模式和色标的冷重开 | Passed | `outputs/acceptance/*-cold-view.json`：模式选择、IR 引用、能量记录、时间驱动位移及扩展开关；双场绑定/色标/文字图例保持，冷启动渲染已检查 |
| 交互界面 | Passed（局部） | `outputs/acceptance/interactive.json`：开发实例实际异步 Log/FCHK 导入、模式/能量接入、HOMO 生成（Alpha MO 5，占据 1，-0.543101269 Eh）；不是独立用户复做证据 |
| 人工使用与外部视觉对照 | Not Run | 用户独立复做及 VMD/VESTA 同输入同阈值的视觉比较尚未执行 |
| 对外发布 | Not Run | 其他平台、任意第三方扩展组合、所有科学方法不在本轮验收范围；许可材料尚待发布复核 |

复现命令见 [DEVELOPMENT.md](DEVELOPMENT.md)。`tools/qualify_package.py` 核对 ZIP 中 Python 与工作区源码一致、wheel 摘要、排除原生 GBasis，并汇总报告及精确 ZIP 摘要到 `outputs/qualification.json`。它核对证据，不自动运行 Blender 检查；修改代码后必须重建并执行相关检查。

## 性能观测

当前候选在 Intel64 Family 6 Model 183 Stepping 1 上测 CH4、34 AO、Alpha MO 8；完整工作进程包含启动、场数组、VDB 和结果落盘。内存为 Windows 峰值工作集，不等同于用户设定的数组预算。

| 网格 | 首次任务 | 重复缓存 | 首次峰值工作集 |
| --- | --- | --- | --- |
| 64³ | 2.51 s | 1.61 s | 251 MiB |
| 128³ | 6.56 s | 1.71 s | 315 MiB |
| 256³ | 76.65 s | 3.22 s | 827 MiB |

证据：`outputs/field-performance.json`。测量期间同机还运行了渲染验收，属于有竞争负载的观测，不是隔离硬件基准或性能承诺。ESP 计算复杂度高于单个 MO，不能用此表推算 ESP 耗时。

## 独立复做入口

安装 ZIP 后按 [用户指南](USER_GUIDE.md) 导入自己的 FCHK，选择一个 MO，生成密度/ESP 并设置明确色标；用频率 Log 选择模式并导出动画；保存配套工程，移动目录并重开。记录 Blender 版本、输入方法/基组、源文件摘要、预期与实际结果。用户验收签署目前为空，不由 Agent 的测试结果填写。
