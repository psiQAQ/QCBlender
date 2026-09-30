# 0.0.1 支持范围与验证状态

更新：2026-10-01。清单声明 Windows x64，Blender 最低 5.1.1、最高边界 5.2.0；实际验证环境为 Windows x64、Blender 5.1.1、CPython 3.13.9、NumPy 2.3.4、OpenVDB 13。独立人工验收尚未签署，当前仅为本地开发候选。

## 当前候选与证据

本轮候选资格绑定固定提交 `90ff9bf`；源码、69个产品文件摘要、候选、输入、命令、报告和保全位置见[公共教程验证索引](acceptance/tutorial-validation.json)，索引随后提交，不引用自身提交。完整产物及重建入口见[ARTIFACTS](ARTIFACTS.md)。[cleanup-validation.json](acceptance/cleanup-validation.json)为历史批次，不继承其界面Passed。

| 检查 | 状态 | 本轮实际范围 |
| --- | --- | --- |
| 科学、单测及输入摘要 | Passed | 科学69/69；复制/布局/输入/清理单测19；110项集中输入摘要 |
| 教程样本与公开包 | Passed | 28项输入、27项自有CC BY 4.0分发文件；P02原站单独获取，分发许可未确认，不加入包；原始checkpoint另用现有计算环境核对 |
| 节点、安装及包资格 | Passed | 固定helper接口和原子编号、公共资产、离线安装/生命周期；68个Python文件在源码/ZIP/安装副本中逐字节一致；生成manifest补入11个锁定wheels，其他字段与源模板相同，安装副本匹配 |
| 图例、剖面、相机、优化与浏览 | Passed | 同批专项及原地/移动冷重开；图例链阶段Not Run及完整链Passed分别保留 |
| 教程核心原生检查 | Passed | C01–C13真实输入的worker、部分同步operator和数组；新未映射层旧入口、关联可渲染视图取景及负向前置复核 |
| 教程工程保全冷重开 | Passed | 42个科学对象绑定、785次数组摘要、12个VDB；原地/中文移动/规范保全分别新进程核对 |
| 可见新候选窗口 | Passed | 独立配置PID37508；原用户PID14284受保护；只启动与原生初始化，不算点击验收 |
| 实际点击、截图、新候选MCP、撤销重做 | Not Run | Computer Use宿主native pipe不可用；完整C01–C13/N01–N18尚未完成。Log Job2→新FCHK重置只有原生状态回归Passed |
| 科研签署、性能/完整收敛、其他平台、发布 | Not Run | 本轮未执行，Agent不代签 |
| 最终归档及工作树/分支/缓存清理 | Not Run | 05 claimed、06 pending，前置点击验收未满足；保全及待清理收据已保存 |

外层节点布局的前后代码对照另见任务02，不把旧分支报告当成本候选报告。早期节点安装曾写入默认userpref.blend，没有前次快照可供恢复；记录在任务07。新增实际配置路径guard后，本批命令核对默认文件SHA未再改变。图例冷重开仍有VFont诊断，报告通过不表示无日志警告。

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
