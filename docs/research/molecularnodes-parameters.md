# MolecularNodes 参数交互借鉴

核查：2026-09-28。固定本地源码 `999b0b5e8f576c83b3dd854819303fe00c0507a0`，pyproject 版本 520.2.1，Blender >=5.2.0，GPL-3.0-or-later。QCBlender 独立实现，目标仍为 Blender 5.1.1；不移植节点资产或增加运行依赖。在线手册未绑定该提交，源码参数以固定 checkout 为准。

| 参考与实际查阅部分 | 对 QCBlender 的结论 |
| --- | --- |
| [Select](https://bradyajohnston.github.io/MolecularNodes/nodes/select.html)：Select Atomic Number、Select Proximity、And/Or/Inverted；本地 nodes/geometry/select_proximity.py | 按源原子身份建立显示集合，邻域距离 Å；不引入残基展开或动态 MD 选择。 |
| [Selection tutorial](https://bradyajohnston.github.io/MolecularNodes/tutorials/selections.html)：Different Styles Combined | 局部显示层复用现有复制、样式、半径和材质。 |
| [Style](https://bradyajohnston.github.io/MolecularNodes/nodes/style.html)：Spheres、Sticks、Ball and Stick、Surface | Sphere 的 Point/Instance/Mesh、Quality 和 VDW Scale 是显示参数。距离推断键不是计算键级，VDW 分子表面不是电子密度。性能模式另批测量。 |
| [Annotations](https://bradyajohnston.github.io/MolecularNodes/api/annotations.html)：AtomInfo、COMDistance、CanonicalDihedrals、Label2D/3D、Common Params；本地 annotations/base.py、props.py | 借鉴字号、颜色、偏移、显隐和引线；上游 Label3D 将锚点投影为屏幕文字，QC 本轮选择 FONT/CURVE 场景对象。其现成二面角标注面向残基，未提供任意三原子角标注。 |
| [Utilities](https://bradyajohnston.github.io/MolecularNodes/nodes/utilities.html)：Vector Angle、Dihedral Angle；本地 nodes/geometry/dihedral_angle.py | 独立 float64 几何测量，使用 atan2 并验证正负、180 度及退化，不直接移植节点配方。 |
| [Color](https://bradyajohnston.github.io/MolecularNodes/nodes/color.html)：Set Color、Color Attribute Map | 保持 QC 量名/单位/有效掩码和现有色带；Linear/OKLab 另立显示需求。本次检索未发现 MN 原生科学色标组件，图例排版是 QC 自身扩展。 |
| [Materials](https://bradyajohnston.github.io/MolecularNodes/api/materials.html)、[Canvas](https://bradyajohnston.github.io/MolecularNodes/api/canvas.html) | 独立材质、透明/轮廓、标准方向和渲染尺度可后续借鉴；本轮不增加场景模板或替换相机灯光。 |
| [Density](https://bradyajohnston.github.io/MolecularNodes/nodes/density.html)、[Animate](https://bradyajohnston.github.io/MolecularNodes/nodes/animate.html) | 切片/轮廓和动画控制后续评估；Hide Dust、插值构型不能默认为适合科学结果，当前不加入。 |
| [Attributes](https://bradyajohnston.github.io/MolecularNodes/attributes.html)：World Scale、charge | MN v520 的 1 Å=0.1 BU；QC 1 Å=1 BU。上游 charge 可有不同语义或缺失占位，不能借属性名推断科学量。 |

本地源码根目录为 `submodules/MolecularNodes/`，不更新 gitlink。额外网页原文在其单独忽略的 `reference-docs/`，索引记录 URL、版本、章节、获取时间及 SHA-256。源码许可见该 checkout 的 LICENSE 与 pyproject.toml；LICENSE.OLD 不是当前代码许可证。

## 已接受的首批范围

固定局部选择 → 源编号与随真实计算步更新的距离/角/二面角场景标注 → 现有图例布局。科学数组、坐标单位、来源身份和工程格式不变。实现和验收合同见 [规格](../../.scratch/molecularnodes-parameters/spec.md)。

源码与官方文档核对 Passed；新增功能、Blender 与 MolecularNodes 实际运行对照 Not Run。独立人工验收与外部视觉对照后置。
