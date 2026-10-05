# 外部分析结果导入

本页描述已有外部分析结果的导入入口。运行时只读取已有结果文件；不会启动 Multiwfn、VMD 或 Tachyon。每个文件的角色由对话框或显式 CSV 步序给出，来源文件名和 SHA-256、用户指定单位及关联信息写入 `.qcdata`。界面不根据文件名推断物理量，也不隐式换算数值。科学样本验收状态见 [验证记录](VALIDATION.md)。

## 在侧栏操作

先导入对应计算并选中静态参考视图，再在 QCBlender 侧栏选择入口。IGMH/IRI、AIM、NBO、ESP 分析与 ETS-NOCV 相关入口要求参考 Dataset 及其绑定祖先为静态构型。含可用优化轨迹、IRC 或多帧 XYZ 的对象即使显示初始步也会拒绝；请将所需步骤保存为独立结构或波函数文件后重新导入。异步导入期间若参考对象、绑定或计算内容改变，本次结果也会拒绝接入。场导入会检查 Cube 的原子编号顺序、坐标和网格；点/表格文件通常没有完整原子身份，因此与活动视图的关联由用户指定，并只做可用的坐标范围、编号和来源检查。

| 入口 | 用户指定的文件和关联 | 结果 |
| --- | --- | --- |
| Display Layers → Hide H / Keep H / Show all | 原子源编号从 1 开始；Keep H 可写 `2,4-6` | 仅改变该原子视图的显示，源数组不变 |
| Import IGMH / IRI | 活动静态参考视图、几何场 Cube、sign(λ₂)ρ 着色 Cube、两种场值单位、颜色范围；IGMH 另选 inter/intra/total/unknown、可选片段成员及声明来源 | 着色等值面及 δg–sign(λ₂)ρ 散点；两 Cube 必须有相同原子顺序、构型和网格 |
| ESP Surface | 活动 ESP 场、极值点 PDB、面积分布文本、表面定义及数值/面积单位 | 极大/极小点、逐点数值查询及面积图；结果需处于参考构型附近 |
| Import NBO Records | 活动参考视图、Gaussian Log/Out、从 1 开始的 job 和该 job 内的 NBO 块号 | NBO 占据、能量、原子和 E(2)；多构型 job 拒绝自动归到最终几何，不把 NBO 对应到 canonical MO |
| AIM | 活动参考视图、CPs.pdb、paths.pdb、可选 CPprop.txt | C/N/O/F 临界点、按 residue 编组的路径及属性查询 |
| IRC FCHK Path | `step,fchk` CSV 清单，行顺序即步序 | 逐步构型和 Hartree 能量曲线；当前用原子球显示路径，不沿用首步键连线 |
| Import Mayer Results | 已导入的 IRC 原子视图、`step,mayer_output` CSV 清单 | 对指定原子对的逐步 Mayer 键级曲线；步数与原子对集合须一致 |
| ETS-NOCV Table | 活动参考视图、外部表格文本、成对能量单位 | pair、自旋、轨道编号、能量及原文行号 |
| NOCV Pair Cube | 已导入 ETS-NOCV 表、pair 编号、自旋、带正负值的 Cube 和单位 | 该 pair 的原生双相等值面；Cube 构型须与表格关联的参考构型一致 |

IGMH 的分量与片段均为用户声明（`user_assigned`），不会根据文件名推断。Fragment atoms 使用 JSON 二维列表，例如 `[[1,2,3],[4,5,6]]`，编号按源 Cube 原子顺序从 1 开始；允许只声明部分原子，片段内重复、非整数和越界编号会拒绝，片段之间交叠会保留并提示。未声明分量或旧工程缺少信息时显示 unknown/unverified。选中几何场或 paired 数据记录，在 **对象属性 → QCBlender · 对象与量子化学 → IGMH 来源声明** 核对记录；保存工程和 CSV 的 `scientific_metadata` 均保留该声明。

IRC 清单采用 UTF-8 CSV。路径可相对清单所在目录，也可用绝对路径；编号必须从 1 连续且文件不重复。例如：

```csv
step,fchk
1,step_001.fchk
2,step_002.fchk
3,step_003.fchk
```

对应的 Mayer 清单：

```csv
step,mayer_output
1,mayer_001.txt
2,mayer_002.txt
3,mayer_003.txt
```

导入后使用 **Save Portable QC Project** 保存 `.blend` 和同名 `.qcdata/`。原始外部文件不会打包进工程；manifest 保存其名称、SHA-256 与解析记录。若要重新核对原始输出，请单独保留计算输出文件。

## 验证边界

真实样本的历史技术验收覆盖 NBO、IGMH/IRI、ESP、AIM、IRC/Mayer、ETS-NOCV 和 NOCV 场，来源与范围见 [SOP 来源清单](v1-acceptance/SOURCES.md) 和 [Agent 复跑记录](v1-acceptance/AGENT-REPLAY.md)。当前候选实际复验与未执行项目以 [VALIDATION](VALIDATION.md) 为准；独立用户验收尚未签署。
