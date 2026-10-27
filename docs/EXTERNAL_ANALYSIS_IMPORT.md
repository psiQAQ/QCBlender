# 外部分析结果导入指南 (External Analysis Import)

QCBlender 提供了一组用于加载和呈现第三方专业量化软件（如 Multiwfn、NBO、AIMAll 等）分析成果的标准化入口。

> [!NOTE]
> QCBlender 只负责读取、校验并以原生几何节点渲染已有的分析成果文件，不会在后台启动外部软件进程，亦不执行自洽场（SCF）能量迭代。

---

## 导入规范与通用约束

1. **构型静态绑定**：
   导入 IGMH/IRI、AIM、NBO、ESP 极值与 ETS-NOCV 数据前，必须先在 Blender 场景中导入对应的静态分子构型。参考 Dataset 或其绑定祖先含可用优化轨迹、IRC 或多帧 XYZ 时，即使停在初始步也会拒绝绑定；将所需步骤保存成独立结构或波函数文件后重新导入。
2. **网格与空间对齐**：
   导入 Cube 网格时，插件会自动校验源文件的原子序号、元素类型、空间坐标与网格原点/步长。对齐失败将弹出错误提示。
3. **物理量与单位声明**：
   外部分析表格或点/路径数据（PDB、TXT、CSV）不一定包含自解释量纲。用户须依据原始计算在导入弹窗中声明所需单位并选中对应参考对象；声明不隐式换算数值，插件不会根据文件名猜测。点与表格缺少完整原子身份时，软件只能核对可用的编号、坐标范围和来源，不能替操作者证明同源。

---

## 支持的外部分析类型与对应入口

分量、片段、计算段与源编号的完整约束见[附录](#appendix)。

| 功能类型 | 侧边栏入口 | 所需外部输入文件 | 生成的 Blender 场景元素与效果 |
| --- | --- | --- | --- |
| **弱相互作用分析**<br>(IGMH / IRI) | `Import IGMH / IRI` | • 空间几何场 Cube (δg / IRI)<br>• 色彩映射 Cube (sign(λ₂)ρ) | 按电子密度带符号特征值着色的空间等值面，记录 inter/intra/total/unknown 分量及可选片段成员声明，不从一个 Cube 自动分解分量 |
| **静电势表面分析**<br>(ESP Extrema / Areas) | `ESP Surface` | • 活动静态 ESP 场（导入或内置生成）<br>• 极值点 PDB (CPs)<br>• 面积分布统计 TXT | 密度曲面上的极大/极小值点标注，按数值区间着色，导出不同 ESP 区间的表面积统计 |
| **自然键轨道分析**<br>(NBO) | `Import NBO Records` | • 包含 NBO 输出的 Gaussian Log/Out | 在侧栏浏览各键轨道占据数、轨道能、原子贡献比及 E(2) 二级微扰稳定化能 |
| **分子拓扑分析**<br>(AIM / QTAIM) | `AIM` | • 临界点 PDB (CPs.pdb)<br>• 键径路径 PDB (paths.pdb)<br>• 属性文件 (CPprop.txt) | 空间显示核/键/环/笼临界点与拓扑路径，在记录浏览器中选择并高亮点、查询属性 |
| **反应历程键级演化**<br>(IRC + Mayer) | `IRC FCHK Path`<br>`Import Mayer Results` | • IRC 步序 FCHK 映射 CSV<br>• 对应步数的 Mayer 键级文本 CSV | 沿反应坐标逐帧浏览分子几何变化、能量演化剖面，以及关键原子对的 Mayer 键级演化折线 |
| **能量分解与电荷转移**<br>(ETS-NOCV) | `ETS-NOCV Table`<br>`NOCV Pair Cube` | • NOCV 汇总分析文本<br>• 目标轨道对的形变密度 Cube | 浏览各 NOCV 轨道对与相互作用能贡献表，生成对应通道正负相位的电荷转移形变密度等值面 |

---

## 常用清单文件格式示例

### 1. IRC 步序与 FCHK 映射清单 (`irc_steps.csv`)
采用 UTF-8 编码，包含 `step` 和 `fchk` 两列，步号必须从 1 开始连续且不重复，文件也不得重复。路径相对清单所在目录，或使用绝对路径：

```csv
step,fchk
1,step_001.fchk
2,step_002.fchk
3,step_003.fchk
```

### 2. Mayer 键级数据映射清单 (`mayer_steps.csv`)
步数、行顺序必须与已导入 IRC 一一对应，各步 Mayer 原子对集合须一致：

```csv
step,mayer_output
1,mayer_001.txt
2,mayer_002.txt
3,mayer_003.txt
```

---

## 工程保存与数据溯源

- 使用 **工程与维护 → 保存与归档 → 保存自包含工程** 时，系统会将解析后的结构化数据和网格二进制存入配套的 `.qcdata/` 目录。
- 原始外部文件不随工程打包，但其文件名、文件 SHA-256 校验和以及导入时指定的单位均会完整记录在元数据清单中。


<a id="appendix"></a>
## 附录：来源声明与验证边界

### IGMH 分量与片段

IGMH 的分量与片段均为用户声明（`user_assigned`），不会根据文件名推断。Fragment atoms 使用 JSON 二维列表，例如 `[[1,2,3],[4,5,6]]`，编号按源 Cube 原子顺序从 1 开始；允许只声明部分原子，片段内重复、非整数和越界编号会拒绝，片段之间交叠会保留并提示。未声明分量或旧工程缺少信息时显示 unknown/unverified。选中几何场或 paired 数据记录，在 **对象属性 → QCBlender · 对象与量子化学 → IGMH 来源声明** 核对记录；保存工程和 CSV 的 `scientific_metadata` 均保留该声明。

### 输入身份与记录选择

异步导入期间若参考对象、绑定或计算内容改变，结果会被拒绝接入。IGMH/IRI 两份 Cube 必须有相同原子顺序、构型和网格。NBO 导入需选择从 1 开始的 Gaussian 计算段及该段内 NBO 块号；多构型计算段不会自动匹配最终几何，也不能把 NBO 编号当作 canonical MO 编号。NOCV Pair Cube 需选择已导入的 ETS-NOCV 表、源 Pair 编号和自旋，构型须与表关联的静态参考一致。

原始输出不随自包含工程打包，需要重新核对时另行保留。各类结果的可用范围、历史技术复验及独立验收状态见 [VALIDATION](VALIDATION.md)；技术通过不等于独立科研接受。
