# VMD 体场参数对 QCBlender 的借鉴

核查日期：2026-09-28。VMD 官方[下载页](https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=VMD)列出 **2.0.0 正式版**（2026-03-25，所列包为 Linux RHEL 8+）和 **2.0.1 alpha**（2026-04-21）。下述可逐项核查的 `current/ug/` [用户手册封面](https://www.ks.uiuc.edu/Research/vmd/current/ug/)标为 **1.9.3**，因此参数描述限定于 1.9.3；[1.9.4a48 开发版手册](https://www.ks.uiuc.edu/Research/vmd/vmd-1.9.4/ug/ug.html)的能力单独注明。尚未找到能据以断言这些具体参数在 2.0.0 完全相同的正式版手册，也未运行 VMD 2.0.0。

## 已核实的参数与作用域

VMD 1.9.3 的 Graphics Window 先选 molecule，再选 representation（rep）；每个 rep 有选择、绘制方法、着色方法与材质，修改选中 rep 即影响其显示。[Graphics Window §5](https://www.ks.uiuc.edu/Research/vmd/current/ug/node45.html) QCBlender 借鉴“一个科学来源可以有多个独立视图”的交互，不照搬 VMD 的 molecule/rep 内部结构。

| VMD 1.9.3 参数 | 含义与作用域 | QCBlender 取舍及科学边界 | 官方章节 |
| --- | --- | --- | --- |
| `Isosurface: Data Set`, `Isovalue` | 在一个 molecule 的多个体数据集中为当前 rep 选场；阈值是该场的数值，沿等值面提取。单位随输入场，手册未给通用单位。 | 视图保存源字段身份和带单位的阈值；MO 正负相位、密度和 ESP 使用各自量纲。改阈值只改变提取的面，不重算科学场。 | [Isosurface §6.1](https://www.ks.uiuc.edu/Research/vmd/current/ug/node77.html) |
| `Isosurface: Draw`, `Boundary`, `Step`, `Size` | Draw 为 Points/Shaded Points/Wireframe/Solid Surface；Boundary=Box 显示体数据边框与轴；Step 跳过体素以降低**提取面**分辨率；Size 是点/线粗细。拖动阈值时可暂用低分辨率。均为 rep 显示参数。 | 样式/边框可作视图设置；Step 与源网格 spacing、物理精度分开标识。低质量交互只可用于预览。 | [Isosurface §6.1](https://www.ks.uiuc.edu/Research/vmd/current/ug/node77.html) |
| `VolumeSlice: Data Set`, `Slice Axis`, `Slice Offset`, `Render Quality` | rep 选场；沿数据坐标 X/Y/Z 轴定位，offset 为 0–1；Low 取最近样点的颜色，Medium 使用双线性插值。 | 后续空间观察可借鉴轴、归一化位置和采样模式；插值是显示处理，不表示源格点重新计算。斜轴网格须按自身坐标变换解释。 | [VolumeSlice §6.1](https://www.ks.uiuc.edu/Research/vmd/current/ug/node76.html) |
| `Orbital` 波函数类型、自旋、激发、轨道 ID、isovalue、grid spacing | 轨道 rep 选择量子态及轨道；isovalue 是波函数**振幅**阈值，grid spacing 决定生成轨道场的采样网格间距。 | QCBlender 区分“重新求值格点”与“从现存数组提面”；不可把现有 Cube 的格点间距当作单纯显示质量滑块。 | [Orbital §6.1](https://www.ks.uiuc.edu/Research/vmd/current/ug/node79.html)、[官方 Orbital 绘制源码 rev 1.53](https://www.ks.uiuc.edu/Research/vmd/doxygen/DrawMolItemOrbital_8C-source.html) |
| `Coloring Method: Volume`、`Color Scale Data Range` | Volume 从关联的体数据集给表面着色；范围可对选中 rep 手动设定，默认按数据最小/最大自动缩放，超界值映到端色。 | 显式绑定几何场与色场，候选显示来源、计算段、字段及单位；范围是**色映射**数值域，不是阈值，也不修改数组。 | [Coloring Methods §6.2](https://www.ks.uiuc.edu/Research/vmd/current/ug/node85.html)、[Graphics Window: Color Scale Data Range](https://www.ks.uiuc.edu/Research/vmd/current/ug/node45.html)、[电势着色官方教程](https://www.ks.uiuc.edu/Research/vmd/minitutorials/colorbypot/) |
| `Color Scale` 类型、`midpoint`、`min`、`max` | 1.9.3 使用全局当前色阶；RWB 等为色阶形状，文档的 midpoint/min/max 调整归一化调色函数，并非有单位的物理范围。 | QCBlender 的数值 `minimum/center/maximum` 仍为视图色带的**字段单位**值；不把 VMD 调色函数参数误作物理值。不同视图色带材质保持独立。 | [Color scale §6.2](https://www.ks.uiuc.edu/Research/vmd/current/ug/node87.html) |
| atom selection、clip plane、display clipping | atom selection 过滤原子；`mol clipplane` 按 rep 设置裁剪平面；显示窗口还有前后裁剪。 | 裁剪仅影响可见几何，不能被描述为对体场做掩码或更改有效域。本轮复制参数保留目标裁剪。 | [Atom selections §6.3](https://www.ks.uiuc.edu/Research/vmd/current/ug/node97.html)、[mol 命令 §9](https://www.ks.uiuc.edu/Research/vmd/current/ug/node140.html)、[Display Settings §5](https://www.ks.uiuc.edu/Research/vmd/current/ug/node44.html) |

源码快照的 `DrawMolItemOrbital.C` 在轨道身份或 grid spacing 变化时重建轨道网格；仅 isovalue 或 step size 变化时重新提取表面。这是 **rev 1.53（2021-10-28）源码观察**，不能代替 2.0.0 运行结论。[官方源码](https://www.ks.uiuc.edu/Research/vmd/doxygen/DrawMolItemOrbital_8C-source.html) 对两场着色，官方电势教程先把势网格载入同一 molecule 再选择 Volume 着色；QCBlender 应据自身关联校验确认几何/色场坐标与来源，不能凭相同文件名匹配。[官方教程](https://www.ks.uiuc.edu/Research/vmd/minitutorials/colorbypot/)

VMD 1.9.3 的 [`volmap`](https://www.ks.uiuc.edu/Research/vmd/current/ug/node156.html)可从原子选择生成新体图，`-res`/`-minmax` 属于生成网格的设置；其中 Coulomb 图使用原子电荷及其文档单位，不等同量子电子结构计算输出的 ESP。[1.9.4a48 开发版 `voltool`](https://www.ks.uiuc.edu/Research/vmd/vmd-1.9.4/ug/node158.html)另提供 crop、trim、mask、clamp、smooth、downsample、supersample 等**改变体素数组**的操作，双图操作涉及重采样/插值。这些属于后续独立科学数据操作，不能混入本轮仅改变显示的裁剪、色标或复制。

## 本轮四项实施合同

本轮规格见本地 `.scratch/vmd-parameters/spec.md`。以下是 QCBlender 的独立设计，不声称 VMD 提供同名批量操作；沿用现有 Dataset、视图、worker 与材质，不加入 VMD 运行依赖。

1. **分组参数面板**：按数据来源、几何表示、颜色映射、材质、空间观察、高级参数展示现有唯一值；阈值显示字段单位，MO 正负标为“相位”，其他带符号场标为正负值。借鉴 rep 内设置分层。[VMD Graphics Window](https://www.ks.uiuc.edu/Research/vmd/current/ug/node45.html)
2. **显式着色场绑定**：用户选择几何场与色场，候选显示来源摘要、计算段、字段和轨道；执行现有关联检查，未知自定义映射拒绝。VMD 的 Volume 着色与同一 molecule 多数据集提供交互参照，QCBlender 的跨场坐标校验由自身合同决定。[VMD Volume 着色](https://www.ks.uiuc.edu/Research/vmd/current/ug/node85.html)、[电势着色教程](https://www.ks.uiuc.edu/Research/vmd/minitutorials/colorbypot/)
3. **一次性有效格点范围**：worker 对指定原始场及有效掩码计算 `minimum < center < maximum`、有效点数、量名和单位；严格跨零时中心为 0，否则取中点。常量、无有效点、非有限值报错；核对 Dataset manifest SHA-256；允许取消。不创建 Dataset 或体缓存，不在面板绘制时读取数组。可手动或设 `-R/0/+R`；保持端色饱和与无效采样颜色。VMD 的每 rep 色阶范围仅是交互依据，自动计算规则为 QCBlender 独立定义。[VMD Data Range](https://www.ks.uiuc.edu/Research/vmd/current/ug/node45.html)、[mol scaleminmax](https://www.ks.uiuc.edu/Research/vmd/current/ug/node140.html)
4. **复制显示参数**：活动视图向兼容选中视图复制几何表示、外观、数值设置三组；先验证所有目标，量名/单位未知或不一致时拒绝数值组。来源、轨道、选择、布局、裁剪和图例位置保持各视图独立，材质色带也保持独立。来源概念是 VMD 的 per-rep 属性，本操作是 QCBlender 新行为。[VMD Graphics Window](https://www.ks.uiuc.edu/Research/vmd/current/ug/node45.html)

MO 振幅的正负是波函数相位；密度差、NOCV 形变密度等有符号场的正负表示各自定义下的增减，不能标成 MO 相位；总电子密度没有对应的负相位。[VMD 轨道阈值说明](https://www.ks.uiuc.edu/Research/vmd/current/ug/node79.html)、[QCBlender 领域模型](../../CONTEXT.md) ESP 数值与色标必须沿用具体来源记录的单位，不把 VMD 教程的示例上下限当作通用默认值。[官方电势着色教程](https://www.ks.uiuc.edu/Research/vmd/minitutorials/colorbypot/) 阈值、色标、材质、裁剪都只改变显示；若将来提供场乘法、平滑或重采样，需生成有来源和参数的新科学数据，并单独验收。[VMD 开发版 voltool](https://www.ks.uiuc.edu/Research/vmd/vmd-1.9.4/ug/node158.html)

## 后续候选与许可边界

后续候选按独立需求评估：体场切片轴/位置及插值、边框与格网对齐检查、可复现图例、局部结构裁剪及测量、交互预览质量与最终质量分离。已有[VolumeSlice](https://www.ks.uiuc.edu/Research/vmd/current/ug/node76.html)、[Isosurface](https://www.ks.uiuc.edu/Research/vmd/current/ug/node77.html)、[Color Scale Bar 脚本](https://www.ks.uiuc.edu/Research/vmd/script_library/scripts/colorscalebar/)可作交互参考；不据此承诺本轮实现。体素裁剪/平滑或 VMD 原生算法移植另需科学与许可评估。[1.9.4a48 voltool](https://www.ks.uiuc.edu/Research/vmd/vmd-1.9.4/ug/node158.html)

[VMD 主程序许可](https://www.ks.uiuc.edu/Research/vmd/current/LICENSE.html)与[插件许可](https://www.ks.uiuc.edu/Research/vmd/plugins/pluginlicense.html)不同：主程序/源码受其专有许可条款约束；插件目录一般采用 UIUC Open Source License，但文件或插件可能另有标注。这里仅依据公开手册和源码理解交互/边界，独立实现 QCBlender 功能；不复制 VMD 代码、插件代码、图像资产，不打包 VMD，也不把其源码许可推定为全部插件许可。QCBlender 继续遵守[单扩展架构决定](../adr/0001-self-contained-extension.md)。

## 原文与验证状态

官方网页、源码页及 2016-10-07 量子可视化教程 PDF 的本地原文在忽略目录 `submodules/VMD/`；逐项 URL、版本、使用章节、UTC 获取时间、大小和 SHA-256 见同目录 `sources.json`。本地索引 SHA-256：`e94980c1efc40af2aaef28090442424d863ae5931185984c7f981c67097c2b1c`；21 份原文逐项哈希匹配。关键文件为 `download.html`、`guide-index.html`、`representations.html`、`isosurface.html`、`orbital.html`、`slice.html`、`coloring.html`、`color-scale.html`、`orbital-source.html`、`LICENSE.html`、`plugin-license.html`；完整索引保留于本地，不提交下载原文。该索引是截至上述获取时间的快照，在线发布状态可能变化。

| 检查 | 状态 | 范围 |
| --- | --- | --- |
| 官方资料核对与本地原文 SHA-256 | Passed | 21 项与 `sources.json` 匹配；本文的版本及参数结论按对应官方章节限定。 |
| 纯 Python 范围单元检查 | Passed | `tests/test_science_field_ranges.py` 在范围工作包中通过；这不代表四项集成已通过。 |
| QCBlender 四项完整 UI/worker 集成、真实文件与冷重开 | Not Run | 由主集成完成后按规格逐项验证。 |
| VMD 2.0.0 和 Blender 实际界面/渲染对照 | Not Run | 本文是官方资料研究，无 VMD/Blender 运行证据。 |
| 独立人工复做与签署 | Not Run | 技术检查不能代替人工验收。 |
