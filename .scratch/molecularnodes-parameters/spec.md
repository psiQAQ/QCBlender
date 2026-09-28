# MolecularNodes 参数交互首批

Triage: ready-for-agent
Status: claimed

## 基线和范围

VMD 已验收提交 d662247 已普通合并至 main，本轮分支 feat/mn-parameters。固定参考 MolecularNodes 999b0b5 / 520.2.1，只读源码及文档，独立实现，不新增运行依赖。Windows x64 / Blender 5.1.1 / zh_HANS，版本保持 0.0.1。

用户确认三个工作包：A 固定局部选择和独立显示层；B 源编号及距离、角度、二面角场景标注；C 现有图例排版。邻域固定源原子集合，测量跟随真实优化/IRC 步；振动展示位移和对象变换不影响科学值。不做屏幕覆盖层、自动避让、体场处理或新分析。

## 公共接口与所有权

- `qcblender.geometry.scientific_geometry(data, kind='source', step=None)` 返回只读 float64 源 Å 坐标及来源记录，kind 为 source/optimization/irc。
- `qcblender.blender.geometry.current_geometry(obj, data=None)` 在显式操作中验证绑定摘要、原子编号/元素、步号，再返回 `(positions, record)`；传入 data 必须属于同一绑定。面板 draw 禁止调用。
- B 标注作为所属 atom view 的直接子对象，用 `qc_annotation` 标记自己的记录/角色；不得仅按名字识别对象。B 导出 `update_annotations(owner, positions, record)`、`copy_annotations(source, target, collection)`、`remove_annotations(owner)` 供主代理集成生命周期；异常不吞掉。
- A 的布尔掩码独立于 qc_atom_visible，不写 Dataset；导出 `copy_selection(source,target)` 用于旧视图升级（普通图层复制天然复制独立 mesh/属性）。未知自定义节点图必须预检，拒绝时原图不变。
- 主代理独占 ui.py、layers.py、copy_display.py、parameters.py、source_browser.py、optimization.py、irc.py 和总文档集成。子代理如需这些文件提供补丁建议，不直接编辑。

## A 行为

源编号支持 1,3,7-10，重复编号去重；距离邻域默认 5 Å，min distance <= R，默认包含种子。替换/并集/交集/差集/反选/清除局部限制；空结果拒绝且无变化。记录种子、半径、固定编号、来源与步号，重新计算只在用户点击时发生。与旧元素/区间/H gate 求交。复用 copy_layer 创建局部层，IRC 仅原位操作且禁止整路径复制。选择不改变 IGMH 科学片段。

## B 行为

测量原子有序输入；DISTANCE Å、ANGLE 0..180 degree、DIHEDRAL (-180,180] degree。二面角以 B→C 为轴、BA/CD 的垂直投影，用 atan2((v×w)·axis,v·w)；-180 归为 180。拒绝重复编号、零长度角臂及退化二面角；0/180 夹角有效。创建时非法不新增对象；换步后退化显示未定义和原因，不显示陈旧值。

FONT/CURVE 原生对象，字号/颜色/偏移/小数位/引线粗细/显隐/一次性朝向相机。默认编号为元素+源编号，距离 4 位、角度 2 位；锚定真实构型，振动展示不移动锚点。每次操作/成功换步更新，draw 不读数组。不改变旧 measure_distance 的源构型语义。

## C 行为

图例新增 Length=2、Width=.18、Text Size=.16、Decimals=5、Orientation=horizontal、Rotation=(0,0,0)，使用布局单位。保持旧默认视觉；横竖都用现有同一色带、三点范围及标题。中心位于色带中点。参数复制不覆盖目标选择/标签/图例布局。旧图例用显式升级且自定义图预检，不自动覆盖用户节点。

## 验收与交付

A→B→C 普通合并。每包独立 ZIP、锁定 wheel SHA、源码与安装副本核对、科学回归、干净配置、GUI/MCP、受影响 SOP、保存及移动冷重开；通过后本地附注 qa/mn-parameters-<日期>-01..03。C 最终候选完整 C01–C13 六栏、N01–N18。技术状态 Passed/Failed/Not Run。独立人工与外部视觉对照后置，不推送发布。

证据位于 outputs/molecularnodes-parameters/。参考原文限定 submodules/MolecularNodes/reference-docs/ 并局部忽略，索引记录 URL/版本/章节/日期/SHA。保留此前所有候选。

## Comments

- 2026-09-28: 实施启动；基线合并完成；独立 MCP Windows Blender 5.1.1 查询通过。公共接口科学检查待执行，A/B/C Blender 检查 Not Run。
