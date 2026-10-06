# Cube 场

[返回教程目录](../SOP.md#topics)

路径相对材料根目录。本专题从 **File → New → General** 开始，在 Outliner 删除默认 Cube。

> Cube 保存规则网格上的场值。量名和单位须采用生成文件时的定义；声明操作不会换算数值。

1. 点击 **N 侧栏 → 工作流 → 导入 Gaussian / Cube / XYZ**，选择 [shared/data/public/P03/color.cube](../../shared/data/public/P03/color.cube)。选中导入的场表面，在 **对象属性 → 声明 Cube 物理量与单位** 中选择 **Other externally computed scalar field**，填 **Physical quantity=sign_lambda2_rho**、**Unit (use unknown if unavailable)=electron/bohr^3**，确认。应看到六原子水二聚体，对象属性应显示 **91×38×156 网格**与上述量、单位。

> `sign_lambda2_rho` 是外部分析生成的带符号电子密度，用于给相互作用区域着色。本例直接使用样本的原始数值。

2. 在 **对象属性 → 几何表示** 开启 **显示正值、显示负值**，取消 **Link Thresholds**，设 **正值阈值=0.03、负值阈值=0.01**。在 **Material Preview** 中应看到两种符号的表面；分别关开正值、负值开关，确认对应部分能够独立显隐。截图保存为 `human/screenshots/20-cube.png`。

![Cube 的正负表面、量名、单位及阈值](../screenshots/20-cube.png)

3. 将 **样式** 依次切换为 **实面、线框、点**，应看到表面表示改变，最后恢复实面。在 **Properties → Material → QCBlender · 节点材质** 设 **Positive Opacity=0.6、Negative Opacity=0.3**，两种表面应有不同透明度。

4. 再导入 [shared/data/public/P03/igmh/dg_inter.cub](../../shared/data/public/P03/igmh/dg_inter.cub)。对新场使用同一声明按钮，填 **delta_g_inter / electron/bohr^4**；设 **正值阈值=0.005**，只开启 **显示正值**。点击该场的 **对象属性 → 颜色映射 → 选择／替换着色场**，选择步骤 1 的 `shared/data/public/P03/color.cube` 场，填 **Color minimum=−0.05、Color maximum=0.05**。在 **Display Layers** 隐藏步骤 1 的独立表面，只保留新映射表面及一份原子层可见。应看到新表面按另一份 Cube 着色；开启 **图例排版 → 显示图例**，图例单位应为 **electron/bohr^3**。截图保存为 `human/screenshots/21-cube-mapping.png`。

![以 delta_g_inter 形成表面、以 sign_lambda2_rho 着色的结果](../screenshots/21-cube-mapping.png)

> 几何场决定表面在哪里，着色场决定表面上各点的颜色。图例采用着色场的单位。
