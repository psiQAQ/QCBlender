# Sidebar 职责收敛与 QC 对象信息摘要
Triage: ready-for-agent
Status: resolved

## 已批准目标

用户批准实现：Sidebar 仅保留导入导出、当前 QC 对象只读摘要、折叠数据/来源详情、折叠对象导航、工程维护；内部计算/创建/测量/编辑移到对象属性栏。保持功能、Operator API、科学数据定义和工程兼容，不新增依赖。全局插件更新、当前工程保全恢复、本地提交/ff-only/注释标签归档已授权，不 push。

## 界面契约

- Sidebar 顺序：Import and Export（导入与导出）、Current QC Object（当前 QC 对象）、Data and Source Details（数据与来源详情）、QC Object Navigation（QC 对象导航）、Project and Maintenance（工程与维护）。后三区默认折叠；摘要展开。
- 导入导出保留基础文件、外部分析、已有数据/参数导出，目标相关操作明确标出目标；能力判断不放宽。
- 属性栏承接 Compute、Display Views、Spatial Tools、Field Sampling、Camera；原子标注只在 Local Selection and Annotations；显示层当前对象显隐/复制/删除/排序放属性栏 Display Layer Management。保留 Outliner 和已有右键入口。
- 来源查看/刷新/关联仅属性栏，Sidebar 一处 Open Object Properties，沿用固定目标但明确对象；摘要读取3D活动对象，不读Properties pin。
- 导航按来源分组，仅SELECT，无修改操作，默认折叠。

## 摘要契约

短摘要：对象名、视图类型、来源原子总数、源文件、计算段、当前XYZ/优化/IRC步；来源总数不得由隐藏后mesh计数冒充。详情：method/basis/status/parser/source，按类别汇总场/轨道/振动/轨迹/外部分析的数量单位及维度。只读manifest metadata/array descriptors缓存，不读数组或运行计算。绘制无磁盘IO；刷新在import/generate/associate/refresh/load生命周期。缺失明确，不沿用旧对象数据。子对象按source_object归属并明确owner；普通对象/空选择无QC摘要。长列表按类别归并、有界输出，不列数值大表。英中文翻译及独立tooltip开关。

## 用户追加：标注编号输入

用户明确要求直接关闭当前工程；2026-10-16 已正常关闭 PID 59380，不覆盖磁盘原件。四类标注改用可直接输入及左右步进的整数编号控件；范围1..当前来源原子总数，越界钳制到边界，钳制结果若与同组其它编号重复则保留该控件原值，不自动跳过占用编号。创建和编辑均覆盖；距离/键角/二面角固定2/3/4个独立编号，原子标注保留批量能力（数量加独立编号，单条编辑一个）。旧atoms字符串程序调用兼容，工程记录仍source_atom_numbers数组。原子不足时明确拒绝相应测量创建，不用重复默认编号。实际GUI验证直接输入、左右步进、上下界、重复拒绝及Undo/Redo。

## 分工与验证明细

- 01-summary: feat/sidebar-summary，独占source_browser.py、新纯摘要模块和对应tests；提供无IO摘要接口及生命周期缓存建议，不动UI/翻译入口。
- 02-ui: feat/sidebar-main，主Agent独占editor_ui.py/layers.py/注册/翻译入口/共享测试及验证工具，接入摘要并处理生命周期调用点。
- 03-docs: docs/sidebar-sop，独占validation/human Markdown；主Agent维护其余共享证据索引。
- 04-delivery: 主Agent串行Blender。空/普通/atoms/field/slice/fog/annotation/multisource/local/missing案例，维度/来源/构型/无IO/有界摘要；真实GUI迁移入口和双语窄栏。候选安装及冷读、全局更新、原工程保全、stdlib/public science/工作区必需检查。独立人工科研Not Run。

## Answer

2026-10-16：实施及技术验收完成。候选源码 `8e085f0`；266 标准库、94 公开科学、真实 GUI、原生几何/缓存/上下文、安装/渲染/冷读和全局原工程恢复通过。证据：`validation/agent/acceptance/sidebar.md`；独立人工/科研签署及两个原生上下文边界保持 Not Run，教程缺图仍 Failed。本地整合与归档收据由 `docs/ARTIFACTS.md` 路由。
