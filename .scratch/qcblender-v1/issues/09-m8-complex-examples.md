# M8 复杂案例集与首版可视化验收

Status: ready-for-human
Execution: complete

## 目标

交付 DVB 阳离子、中性 DVB 振动、非对称极性有机分子、氢键复合物四个真实案例。复用现有插件，提供来源清单、复建脚本、可迁移的 blend/qcdata、渲染图、振动短动画和覆盖报告。

## 边界

- Windows x64 / Blender 5.1.1；允许外部预处理生成 Cube，但不增加插件运行依赖或内置分析量。
- 不新增 Gaussian 计算；不拼接不同计算状态的文件。
- 大型素材与生成物留在 outputs；本地分批提交，不推送。
- 科学数据与展示参数分离；独立人工验收不由 Agent 签署。

## Comments

2026-09-23：用户批准完整案例验收与演示交付，并允许必要的外部 Cube 预处理。前两个候选文件已阅读；四例真实导入和场景验证待执行。

2026-09-23：技术交付完成。第一批来源及预处理提交为 `df016e7`；极性案例选用27原子的色氨酸，氢键案例选用具有独立 NCIPLOT 参考的水二聚体。交付4组 blend/qcdata、8张代表图、48帧 PNG 和2秒 MP4；入口 `docs/COMPLEX_EXAMPLES.md`。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 固定来源、许可、摘要 | Passed | 10个下载文件；`tests/data/complex-example-sources.json` |
| 色氨酸 FCHK/Log 匹配 | Passed | 最大坐标差4.99e-7 Å，偶极单位换算核对；`outputs/complex-examples/source-inspection.json` |
| 外部 RDG/带符号密度 | Passed | 梯度/Hessian差分、Cube往返、NCIPLOT独立参考；不增加插件内置分析菜单 |
| 真实场景与渲染 | Passed | 各例 `report.json`；人工查看 Agent 可见 PNG，修正图注、照明和切片位置 |
| 冷重开及可迁移数据 | Passed | 四例 `reopen.json`；复制到 portable 后真实渲染，几何计数和缓存摘要一致 |
| 动画编码/解码 | Passed | 原生 H264 MP4，24 fps、48帧；新进程重读验证帧数 |
| 既有科学回归 | Passed | 20/20，`outputs/science-reference.json` |
| 汇总 | Passed | `outputs/complex-examples/summary.json` 含成片和场景摘要 |
| 独立用户验收/发布 | Not Run | 保留 M5 人工边界，不由 Agent 签署 |

当前限制：STO-3G 示例不代表高精度科研结论；体积网格用于展示；首次色氨酸ESP本机耗时约八分钟，缓存复建显著更快。Blender既有 VFont 依赖关系警告仍可见，但本轮网格计数、图注和冷重开渲染通过；不声称已修复警告根因。视频接口、NCI倍率及照明问题已写入开发问题记录。
