# 分子显示与 XYZ

[返回教程目录](../SOP.md#topics) · [分子与标注](#atoms) · [显示层](#layers) · [关联与多帧](#frames)

路径相对材料根目录。已完成[插件安装](../SOP.md#install)；本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。

本页截图使用案例 `P06-` 前缀。

> XYZ 文件保存原子元素与坐标。本教程的坐标单位是 Å，1 Å = 0.1 nm；源原子编号从 1 开始。

<a id="atoms"></a>
## 分子与标注

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，选择 [shared/data/public/P06/water-dimer.xyz](../../shared/data/public/P06/water-dimer.xyz)。选中导入的原子对象，按 `F2` 命名为 **P06-single**。应出现两个水分子，共 **6 个原子，顺序 O/H/H/O/H/H**。切到 **Material Preview**。

> 球棍用球表示原子、棍表示键；空间填充按各元素的范德华半径（原子大小的参考值）画球；键线只显示键。Atom Radius 是球棍的原子球半径，Bond Radius 是键的粗细。显示键根据原子距离推断。

2. 在 **对象属性 → 几何表示 → 样式** 依次选择 **球棍、空间填充、键线**，应看到三种表示。回到球棍，将 **Atom Radius** 设为 **0.35 Å**、**Bond Radius** 设为 **0.12 Å**，球和键应变粗。

3. 在 **对象属性 → 局部选择与标注** 点击 **隐藏氢**，应只剩氧 1、4；点击 **保留指定氢**，输入 **2**，应显示 1、2、4；最后点击 **显示全部氢**，恢复六个原子。

> 局部选择使用原文件的原子编号。Mode=Replace 用本次结果替换原来的局部范围；输入的原子是种子，Include distance neighborhood 选入距任一种子不超过 Radius 的原子，Include seed atoms 决定是否保留种子本身。距离按源构型的 Å 坐标计算。

4. 点击 **设置局部选择**，**Source atom numbers (1-based)=1**、**Mode=Replace**，开启 **Include distance neighborhood**，填 **Radius=1.0 Å**，保持 **Include seed atoms** 开启。应只显示第一个水分子，即原子 1、2、3；点击 **清除局部限制** 恢复全部。

> Decimal places 设置标注保留的小数位数；Offset 设置文字相对标注位置的偏移，只移动标签，不改变原子位置和测量值。

> 二面角描述两组三原子平面的相对转角；按表中顺序输入四个源编号。

5. 保持 **P06-single** 活动，在 **N 侧栏 → 创建视图与检查工具** 依次创建下表四种标注，**Decimal places** 均设为 **3**。标注若重叠，在 **对象属性 → 局部选择与标注 → Source Atom Annotations** 点击对应设置图标修改 **Offset**。旋转视角，确认六原子球棍、读数与单位可见。截图保存为 `human/screenshots/P06-annotations.png`。

| 按钮 | Source atom numbers | 应看到的内容 |
| --- | --- | --- |
| 创建编号标注 | 1 | O1 |
| 创建距离标注 | 1,4 | 2.900 Å |
| 创建角度标注 | 2,1,3 | 112.770° |
| 创建二面角标注 | 2,1,4,5 | 0.000° |

![水二聚体的六原子球棍、源原子编号及距离、角度、二面角](../screenshots/P06-annotations.png)

<a id="layers"></a>
## 显示层

> Display Layers 是显示层列表；显示层是同一科学数据的一种展示。局部层用于突出选定原子；Duplicate 创建可单独调参的副本，便于比较不同显示效果。

6. 选 **P06-single**，点击 **N 侧栏 → 创建视图与检查工具 → 创建局部显示层**，输入 **1,4**。新层应只显示两个氧，原层保留六个原子。在 **Display Layers** 中关闭原层的眼睛图标，便于观察新层；看完后恢复原层、隐藏局部层。

7. 在 **Display Layers** 选回 **P06-single**，点击 **Duplicate**。选副本，将 **Atom Radius** 改为 **0.25 Å**；分别通过列表的眼睛图标显示原层和副本，应看到它们的半径分别为 **0.35/0.25 Å**。副本行的相机图标控制是否参与渲染，上下箭头调整列表顺序。截图保存为 `human/screenshots/P06-layers.png`。

![原层和副本的独立参数与显示层列表](../screenshots/P06-layers.png)

> 多选时最后选中的是活动对象；这里由活动对象提供要复制的参数。

8. 在 Outliner 先选副本，再按住 `Shift` 选 **P06-single**，使原层最后选中。打开 **3D Viewport → Object → QCBlender → 复制显示参数到选中视图**，只勾 **几何表示** 并确认。副本半径应变为 **0.35 Å**。仅选副本，在 **Display Layers → Remove** 删除它；原层应仍在。选原层再点击 **创建视图与检查工具 → 创建当前版本视图**，应能重新生成一层；观察后在列表隐藏新层。

<a id="frames"></a>
## 关联与多帧

> 数据源关联核对两份文件的原子顺序与构型。Maximum atom deviation 是对应原子允许的最大距离偏差；Align rigid rotation/translation 允许先整体旋转和平移再比较，不改变分子内部构型。每份文件仍保留自己的计算信息。

9. 通过 **导入 Gaussian / Cube / XYZ** 导入 [shared/data/public/P03/water-dimer.fchk](../../shared/data/public/P03/water-dimer.fchk)，将新原子对象命名为 **P03-atoms**。先选 **P06-single**，再 `Shift` 选 **P03-atoms**，点击 **对象属性 → 关联选中数据源**，保持 **Maximum atom deviation (angstrom)=0.001**、关闭 **Align rigid rotation/translation**。确认后应提示原子顺序和构型匹配。隐藏这两层及其副本，方便继续看多帧。

> XYZ 帧是同一原子顺序的一组坐标，Next/Previous 逐帧切换；Source lines 标示该帧在原文件中的行区间。帧序本身不提供物理时间。

10. 导入 [shared/data/public/P06/p04-three-frames.xyz](../../shared/data/public/P06/p04-three-frames.xyz)，选中新原子对象，命名为 **P06-frames**。在 **对象属性 → XYZ Frames** 点击 **Next → Next → Previous**，应按 **1→2→3→2** 切换；每帧都是 **O/O/H/H** 四个原子。展开原注释与 **Source lines** 可看到当前帧来源。

11. 保持 **P06-frames** 活动，点击 **创建视图与检查工具 → 创建二面角标注**，填 **3,1,2,4**，小数设 **3**。在 **XYZ Frames** 切换三帧，应依次看到约 **171.761°、−180.000°、−171.761°**，标签中的帧号同步改变；最后停在第 2 帧。截图保存为 `human/screenshots/P06-xyz-frames.png`。

![三帧 XYZ 的当前帧与随帧二面角](../screenshots/P06-xyz-frames.png)
