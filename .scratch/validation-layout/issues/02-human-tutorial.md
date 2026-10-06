# 02 人工教程

Triage: ready-for-agent
Status: resolved
Blocked by: 01
Owner: tutorial agent

## Scope

负责 `validation/human/` 与 `validation/agent/LOCAL-CASES.md`。按计划主流程和专题重写；读取实际 UI 和输入核对参数。无需人工结果模板、SHA 操作或旧截图；截图引用留给维护者填写。不得修改产品代码、数据、根索引或其他任务文件。

## Acceptance

主流程从安装开始，全部独有公开能力有入口；路径以 validation 为材料根；参数摘要与科学 CSV 都有练习；专用名词独立引用解释，截图就地命名，P02 本地页不成为公开前置条件。完成自查、提交并等候串行合并轮次。

## Comments

2026-10-06：已将计划提交 `788f548` 快进同步到独立工作树。按独占范围编写公开主线、按需专题及 P02 本地页；此任务不启动 Blender，界面操作由主 Agent 综合复核及维护者操作确认。

2026-10-06：按 `qcblender/blender/result_browser.py` 的实际 `draw()` 核对，ESP/AIM 的源编号、数值属性与点值范围控件，以及 ETS 的 Pair number 控件目前没有绘制。公开教程采用可用的 Record/Match 浏览、ESP 面积筛选与 ETS 能量范围筛选；不把旧 SOP 对这些控件的描述继承为已完成的 GUI 验证。FCHK 来源窗口也不显示基组和电荷数组，教程改为核对文件名、坐标单位、科学记录与实际着色。未修改产品代码。

2026-10-06：数据分支进入 `main@6e03549` 后，忽略的 Cube、P02 日志和安装包仍需在主检出准备；初次实际路径检查发现这些文件尚未复制。主 Agent 已接手串行准备，教程保持既定路径，完整主检出的资源存在性由任务 05 复验。

## Answer

- 已新增 `validation/human/SOP.md`：15 个主流程操作，含安装、轨道、渲染、参数摘要、一次保存重开和归档；安装前无需文件摘要操作。
- 九个 `human/topics/` 专题保留分子/XYZ、Cube、密度/ESP、空间观察与 CSV、IGMH/IRI、ESP/AIM、IRC/Mayer、ETS-NOCV 和公共节点。公开部分合计 73 个编号操作，P02 本机页另有 8 个操作。
- 公开教程仅依赖 `human/`、`shared/data/public/` 和 `shared/install/`；P02 位于 `agent/LOCAL-CASES.md`，明确排除在公开包之外。29 个公开截图与 3 个本机截图均给出就地保存名和图片引用，未提供伪造截图。
- `Passed`：公开文档链接、显式锚点、连续步骤编号、截图路径及唯一文件名；所需资源的原件映射；未引入本机绝对路径、SHA 操作、实际结果填写或签署要求；UTF-8 无 BOM；按钮与参数经当前源码核对。
- `Passed`：`git diff --check`；提交前另以 `git diff --cached --check` 核对新增文档。
- `Not Run`：本子任务未启动 Blender，未执行实际 GUI 操作、渲染或保存重开；维护者截图和独立人工操作仍待完成。完整主检出及独立打包的复核由任务 05 负责。
