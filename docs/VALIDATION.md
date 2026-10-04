# 0.0.1 支持范围与验证状态

更新：2026-10-04。当前本地待验收候选使用Windows x64、Blender 5.1.1、CPython 3.13.9、NumPy 2.3.4、OpenVDB 13。独立使用者及科研签署尚未执行，未发布。

## 当前候选与证据

当前候选固定产品源码为`a4baaaf2cf163d93d8d7e25f3c9bd5e96ae01c3d`，详见[P1技术验证](acceptance/audit-p1-validation.md)及[机器索引](acceptance/audit-p1-validation.json)。97科学测试、当前构型关联/共享mesh原生与GUI、Undo/Redo、原地/中文移动及最终保全冷读Passed，六固定视觉场景比较Passed；独立使用者和科研签署Not Run。

## 历史展示、XYZ与CSV批次

以下表格保持2026-10-02批次范围。固定源码为`9d3ff61d2e32c47357fe624cf93052bfed6dd041`；产品树、文件/候选/输入摘要、实际命令、42份本批通过报告及GUI身份见[展示精度、XYZ与CSV验证索引](acceptance/display-xyz-export-validation.json)。后续文档和收尾提交不改变该候选身份。产物位置和重建入口见[ARTIFACTS](ARTIFACTS.md)。历史[公共教程资格](acceptance/tutorial-final-qualification.json)与[清理验证](acceptance/cleanup-validation.json)保留原批次身份。

| 检查 | 状态 | 本批实际范围 |
| --- | --- | --- |
| 科学回归及相关单测 | Passed | 82科学测试，无失败/错误/跳过；21项复制/布局/输入/清理单测；集中输入摘要与新XYZ严格边界 |
| 展示精度与公共资产 | Passed | 新原子外层Quality3、新切片201/轴；源坐标/编号不变，九公共资产实现、签名/接口和资产默认值保留；已有工程显示参数保留 |
| 标准XYZ | Passed | 单帧/同元素顺序三帧Å；离散切帧、逐帧身份/推断连接/距离与二面角/复制独立性；多帧不能借用第一帧关联科学记录 |
| 数据导出与二维清理 | Passed | IR、优化/收敛、IRC、Mayer、剖面、paired、ESP面积；真实worker完整/筛选、逐值、单位/掩码/来源、取消无遗留、唯一目录；539448有效体素完整导出 |
| 实际GUI操作 | Passed | XYZ导入/切帧、0.2Å密度、201切片、采样记录、值列/面积筛选、Mayer读取；目录修复后重新点击profile/IR/ESP筛选导出并MCP核对。e317→9d3ff61仅SKIP_SAVE一行，未变操作通过差异审阅复用，旧截图保留原候选 |
| 同候选安装与专项 | Passed | ZIP/安装副本/源码一致、11个锁定wheels；生命周期、原地/中文移动冷重开、缓存、公共资产、轮廓与图例专项 |
| 工程保全与旧谱图 | Passed | 可见工程12Dataset/249数组/1VDB，两新进程原地/中文移动冷读，帧2/Quality3/40401切片顶点与标注保留；旧谱图对象不删除且可导出三模式原数据 |
| 公开v2样本 | Passed | P06增加两份自有XYZ，科学文件/来源/许可与摘要核对；P03/P05原Cube字节不改，P02继续独立取得 |
| 用户复做、独立科研签署、发布 | Not Run | Agent不代签，不从技术通过推导科研接受；没有push或发布 |

截图紧接[SOP](v1-acceptance/SOP.md)步骤，用户占位由实际操作者填写。0.2Å网格和显示细分是展示设置，不是收敛证明；原始Cube保留其固定源网格。旧二维图仅在历史工程与证据中保留，新建结果使用CSV。归档与权限/占用对象的状态见ARTIFACTS收尾路由。

## 输入和科学边界

| 能力 | 当前实现与证据边界 |
| --- | --- |
| FCHK | IOData 适配；坐标/原子顺序、SP、球谐/笛卡尔、Alpha/Beta、占据、轨道能量、可用 SCF 密度和性质保留。FCHK 本身不证明计算收敛 |
| Log | cclib 性质 + 自有能量事件适配；G03/G09/G16 样本、Link1 job、正常/异常/截断状态分别处理。多构型 job 不自动把电荷/偶极/模式绑到最后构型 |
| XYZ | 标准有限三坐标Å；单帧或同元素顺序多帧离散查看；extxyz、PBC、额外列、dummy中心及截断显式拒绝 |
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
