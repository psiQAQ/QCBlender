# 0.0.1 支持范围与验证状态

更新：2026-09-30。清单声明 Windows x64，Blender 最低 5.1.1、最高边界 5.2.0；实际验证环境为 Windows x64、Blender 5.1.1、CPython 3.13.9、NumPy 2.3.4、OpenVDB 13。独立人工验收尚未签署，当前仅为本地开发候选。

## 当前候选与证据

当前本地候选的验证身份、产品源码树及 69 个文件摘要、ZIP 摘要、命令、报告摘要、截图和重建方法统一保存于受版本控制的[验证索引](acceptance/cleanup-validation.json)。资格绑定固定提交 `a7f9b43`；索引与任务收尾随后提交，不引用自身提交。大文件及受限样本仍在忽略目录，实际归档可用性以任务 06 的保全收据为准。

| 检查 | 状态 | 本次范围与证据 |
| --- | --- | --- |
| 科学回归 | Passed | 同批 qcf3：69/69，无失败、错误或跳过 |
| 非科学单测 | Passed | 11/11，显示复制、布局、输入与清理边界；同批单测日志 |
| 节点行为 | Passed | 七种选择实际原子编号、固定公共接口/标识、helper；资产和图例复用已有专项。上轮十组节点图对照另记历史 |
| 新 ZIP 离线安装与生命周期 | Passed | 新配置安装、科学运行库、worker 取消/缓存、注册/注销 |
| MO 成图及工程保存 | Passed | 实际求值、阈值/双相、渲染，原地及中文移动路径冷重开 |
| 数据恢复与节点资产 | Passed | 缺 VDB 恢复、来源重定位、电荷/偶极/振动；公共资产导出重载和已有分支保留 |
| 图例与双场 | Passed | 真实密度/ESP、横竖/旋转布局、替换及独立复制、旧图升级、signed MO/电荷；原地/中文移动冷重开与渲染 |
| 来源与包一致性 | Passed | 同批源码、ZIP、安装副本、wheel 摘要；Log 后新对话框导入 FCHK 回归，真正的源文件变化仍被拒绝 |
| 授权的指南界面操作 | Passed | Agent 使用 MCP + Computer Use 在可见新窗口实际点击：Log/FCHK 导入、能量、模式与播放、密度/剖面、保存、新进程重开及 CSV；具体准备与按钮范围见任务 04 |
| 全量历史 SOP、性能、完整网格收敛和外部视觉对照 | Not Run | 本批未重跑 C01–C13/N01–N18 全流程；专项不替代完整范围 |
| 独立人工签署、其他平台、公开发布 | Not Run | 不能由本次清理或技术通过推导完成 |

本次范围和处置见 [清理复查任务](../.scratch/cleanup-followup/spec.md)。基线清单已逐文件匹配 `47fd82c`；旧候选通过和导入失败分别保留于索引历史项，不继承为本批结果。Blender 图例重开仍有 VFont 转节点诊断；实际报告和画面通过不等于无日志警告。

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
| 未支持及受限范围 | B2PLYP 目标规则仍为候选；CASSCF、复合方法等不宣称完整解析。相关方法密度、WFN/WFX、ORCA、`.mwfn`、周期体系及新分析类型不属于当前支持范围；外部 IRC FCHK 路径已通过 C10 真实结果技术验收 |

GBasis 来源固定在 `science-sources.lock.json`，当前 wheel 为 `0.1.0+qcblender.071969c.pure1`，只打包 Python 数值路径。SciPy 等随包 wheels 固定 SHA-256，NumPy/OpenVDB 使用 Blender 自带版本；运行时不调用外部 Python/pip。

## 外部结果与轨迹

源码提供 IGMH/IRI 配对 Cube、ESP 极值/面积、NBO/E(2)、AIM、IRC FCHK/Mayer、ETS-NOCV 表与 NOCV pair Cube 的读取和显示；运行时不执行这些外部分析算法。输入角色、单位及关联限制见 [外部分析导入](EXTERNAL_ANALYSIS_IMPORT.md)。

真实结果的历史技术证据见 [SOP Agent 复跑](v1-acceptance/AGENT-REPLAY.md)、[来源清单](v1-acceptance/SOURCES.md) 和 [源码借鉴验收](acceptance/source-adoption.md)。本次科学回归覆盖相应解析/身份检查，未重跑每项外部结果的全部渲染及 GUI 工作流。Gaussian 优化日志仅支持已识别任务类型；扫描、重启、QST2/QST3 和复合路径不纳入逐步浏览。外部 IRC 使用显式有序 FCHK 清单，不代表任意 IRC 日志均可解析。

## 科学依据与复现

现有独立参考测试保留 CH4 UHF/cc-pVDZ 的 27 点 MO 与 18 点 Gaussian Cubegen 密度/ESP 对照；最大绝对误差约为 4.85e-9、8.44e-7 electron/bohr³、4.61e-6 hartree/e。AO 重叠与电子数测试覆盖开闭壳层、球谐/笛卡尔及矩形 MO；这些结果只证明所测样本。

网格收敛与远场专项历史证据：LiH+ 半宽 8 bohr、步长 0.1 bohr 得 2.99994998 个电子，200 bohr 的 rΦ=0.99993221；原报告 `outputs/scientific-convergence.json`。本次未单独重跑该完整实验。历史性能表保存在 Git 中的本文件基线版本；本次未执行性能基准，不作速度承诺。

当前构建、输入校验、安装和同批工程冷重开步骤见 [DEVELOPMENT](DEVELOPMENT.md)。`qualify_package.py` 只核对报告及文件身份，不代替实际运行。四组真实案例的计算参数与复建入口见 [复杂案例](COMPLEX_EXAMPLES.md)。

独立复做使用 [SOP](v1-acceptance/SOP.md)，记录 Blender 版本、输入方法/基组、源摘要和预期/实际结果。人工签署由使用者完成，不能用 Agent 测试结果填写。
