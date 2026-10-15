# 标注几何、材质与面板交互改进
Triage: ready-for-agent
Status: claimed

## 已批准目标与交付

完善四类源原子标注，修复“全部朝向相机”，为所有 QCBlender 面板/属性/列表/弹窗按钮补齐中英文悬停说明。保全用户工程，串行实际 Blender 验证，备份更新全局 Blender 5.1 插件和当前 ZIP，恢复原工程与语言；本地提交、ff-only 合并、注释标签归档，不 push。无需新增依赖。当前基线 9f67624。

## 标注契约

- 新建默认纯黑、Metallic=1；创建窗口可选颜色。后续编辑/更新不读取、限制或改写材质节点、material users；保留会更新的 FONT/CURVE/MESH 独立数据检查。
- 每条标注自己的 QC annotation material，内部 LABEL/LEADER/DASH/ARC 共享，不同条独立。DIHEDRAL PLANE_A/B 共享另一材质，初始颜色同选色、Alpha=.2、Metallic=0。后续用户在材质节点编辑。
- 当前视图显式统一材质操作 qcblender.unify_annotation_materials：预览数量，以当前文字材质为准建立每条独立副本并组内共享；保留旧材质及其节点、可随工程保存；Undo、幂等；不在打开旧工程时迁移。
- 默认前缀固定 Atom: 、Distance(1,2) = 、Angle(1,2,3) = 、Dihedral(1,2,3,4) = ，不随界面语言。prefix_mode DEFAULT/CUSTOM，自定义prefix原样（中文、空串、空格），尾部总追加真实符号+编号或数值+单位。来源构型仍存metadata不强塞入文字。距离默认4位、角度2位。
- 字体主Agent提供 blender.annotation_fonts.annotation_font()，使用现有Blender bundled Noto CJK并pack，不新下载依赖；创建及旧标注首次编辑需要字体时使用，不在每次构型更新写字体。

## 几何

- DISTANCE：真实两原子间圆截面虚线1:1、两端对称，均匀分配节距；默认独立直径.01（与leader分离）。零距离保留数值、隐藏虚线。
- ANGLE：圆心原子2，端点在2→1、2→3射线内角；radius=.5、独立直径.01，新增/编辑可改。0°隐藏零弧；180°使用确定辅助平面。
- DIHEDRAL：科学定义保留原B→C signed (-180,180]；圆心(2+3)/2，圆弧平面垂直2→3，首尾投影向量及方向与计算一致；两实体三角面123和234；radius/width同上。无定义构型显示undefined并隐藏无效几何，不留旧帧图形。
- show_leader/show_measurement/show_planes独立，整个visible关闭覆盖所有部件。所有部件局部坐标，随XYZ/优化/IRC更新，不改变科学数组。
- face_all仅当前原子视图所有LABEL，明确空annotation_id且不继承上次单条ID；仅转文字，保留其它部件；无相机清晰失败。
- copy复制所有部件、数据独立、组内材质共享组间独立；delete、visibility、Undo/Redo及save/reopen覆盖新增角色。旧LABEL/LEADER配对可读；首次edit补齐新测量部件，不暗中统一材质。

## 面板与提示

- 创建面板分组：显示视图、空间工具、场值采样、原子与几何标注（四按钮两列）、相机；隐藏不适用项目后不留空组。
- Workflow分导入/计算；Project分保存导出/恢复维护/诊断；External按科学类别。保留入口/顺序语义与能力判断。
- 所有插件owned按钮给出用途、对象、结果和必要前提；原生Blender按钮保留原生提示。静态bl_description，变体operator动态description按kind/action/id；遵守独立tooltip翻译开关。用户数据不翻译。
- 主Agent维护editor_ui.py、i18n.py、project.py及共享翻译入口/索引/证据。core Agent独占measurements/annotations/annotation_geometry/translations_annotations及核心测试。tooltip Agent独占其它模块的description及translations_tooltips/newtests。docs Agent仅human Markdown。

## 验收

先旧版实机复现单条后全部朝向、共享/自定义材质后编辑；保全之后再试，不动用户原件。纯数值+原生集成检查端点/比例/圆心/半径/正负/退化，材质与字体/前缀、迁移、copy/delete/Undo/Redo、XYZ/优化/IRC、全tooltip清单及语言开关；真实GUI四类创建编辑与hover，渲染、自包含中文路径冷读。主Agent综合stdlib/public-science、候选安装、全局冷启动；独立人工/科研签署Not Run。

## 任务
- 01-core：annotations-core；几何、文字、材质与生命周期。
- 02-tooltips：panel-tooltips；各operator描述与双语清单。
- 03-panels-fonts：main；面板、字体、共享入口与实际复现。
- 04-docs：annotations-docs；SOP与相关专题。
- 05-integration：main；构建、综合验收、全局安装与本地归档。
