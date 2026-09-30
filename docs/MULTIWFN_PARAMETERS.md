# Multiwfn 参数与界面技术验收

> 产物状态更新（2026-09-29）：本页是历史技术验收记录。候选 ZIP、生成工程及图像已纳入用户批准的清理范围；日志、摘要和历史 Passed 保留，二进制可用性以 [清理记录](acceptance/storage-cleanup.md) 为准。本文中“可重开”“保留候选”等描述只代表验收当时状态。当前可用的用户工程单独保存，后续演示从集中输入重建。

本轮按 [规格](../.scratch/multiwfn-parameters/spec.md) 顺序集成。独立人工验收和外部视觉对照单独维护。

当前操作见 [用户指南](USER_GUIDE.md)，新候选构建和复验流程见 [DEVELOPMENT](DEVELOPMENT.md)。本页只保留对应历史批次的结果与范围。

## 第一批：界面与资产

第一批候选位于 `outputs/multiwfn-parameters/01-foundation-r5/`，源码提交 `65e4e9b`，ZIP SHA-256 为 `01a8e7af1cb935c4b7872ce87a63e5289d51ede849ed854f6cad6a521e74a976`。旧候选及失败证据保留。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 科学回归 61 项 | Passed | `science.json` |
| 干净配置安装与离线移动冷重开 | Passed | `offline/extension.json` |
| 能力判断、缺失绑定、socket 身份、旧资产清理 | Passed | `foundation/core/core.json` |
| 真实面板重绘不读取科学数组、Properties 固定对象 | Passed | `foundation/gui/gui.json` |
| 样式切换、GUI 撤销和原生菜单重做 | Passed | `gui-evidence/objects-redo.png` |
| 九个分类资产、未分配为空、材质属性入口 | Passed | `gui-evidence/assets-nine.png`、`assets-unassigned-empty.png` |
| 参数复制及计算段工程保存、原目录和移动冷重开 | Passed | `regression-copy/checks.json`、`regression-jobs/checks.json` |
| C07 真实 IGMH / IRI 源值、参数变化及移动冷重开 | Passed | `final-sop/cases/C07/source-node-check.json`、`candidate-run.json` |
| C08 / C09 真实记录、撤销重做、保存和移动冷重开 | Passed | `final-sop/cases/C08/`、`C09/` 的 `analysis-check.json` 和 `candidate-run.json` |
| ESP 单位冲突拒绝且场景完整、声明位置和五列面积区间 | Passed | `final-sop/cases/C08/metadata-check.json` |
| 第一批最终资格 | Passed | `qualification.json`、`evidence-index.json`；源码、安装副本、ZIP 和 wheel 摘要一致 |

运行故障与复验方法见 [开发注意事项](DEVELOPMENT_PITFALLS.md)。本记录不替代 SOP 独立人工签署。

第一批本地技术标签为 `qa/multiwfn-parameters-2026-09-28-01`。其范围限于上述检查；最终全量 SOP 已在第四批 `04-results-r2` 候选上完成。

## 第二批：探针与切片

候选位于 `outputs/multiwfn-parameters/02-interaction-r4/`，源码 `acc36f6`，ZIP SHA-256 为 `f302e5e662fccc6a945863b61b78322213e806fe22557ea9f461007e66333761`。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 科学回归 64 项、独立安装、离线冷重开 | Passed | `science.json`、`offline/extension.json` |
| 仿射 ij/jk/ki、三原子定平面、构型冲突拒绝 | Passed | `features/checks.json` |
| 源坐标采样、局部对象变换、复制与科学数组不变 | Passed | `features/checks.json` |
| 几何场和着色场点击、真实 Cube 插值与字段来源 | Passed | `gui-evidence/checks.json`、`probe-geometry.png`、`probe-color-saved.png` |
| 无命中、域外、取消、撤销和重做、只读摘要同步 | Passed | `gui-evidence/checks.json`、`probe-nohit.png`、`probe-outside.png` |
| 切片 Gizmo 与自由平面状态、对象空间属性入口 | Passed | `gui-evidence/gizmo-move.png`；旋转和尺寸入口另见保留的 `02-interaction-r3/gui-evidence/` |
| 两类工程保存、原目录和移动冷重开、重新渲染 | Passed | `features/checks.json`、`gui-evidence/checks.json` |
| 参数复制和 Gaussian 计算段回归 | Passed | `regression-copy/checks.json`、`regression-jobs/checks.json` |
| 源码、安装副本、ZIP、wheel 摘要一致 | Passed | `qualification.json`、`evidence-index.json` |

本批标签为 `qa/multiwfn-parameters-2026-09-28-02`。点击探针记录真实字段来源；运行期间绑定或计算身份变化会拒绝保存。切片位置、方向和尺寸进入对象属性的“空间观察”，显示采样数仍在“几何表示”。

继承的 C07 工程会输出 Blender 内置字体 `VFont -> Node` 关系警告；本批可见渲染和两次冷重开均通过。原始日志保留，不将该诊断当作新增功能失败或静默删除。

## 第三批：等值线、色谱与剖面

候选位于 `outputs/multiwfn-parameters/03-charts-r5/`，源码 `50ac4d8`，ZIP SHA-256 为 `ed29271c7a258cdf02cbced537b4a544c80d710d6edec63ae6557bbada09a01e`。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 科学回归 64 项、独立安装与离线冷重开 | Passed | `science.json`、`offline/extension.json` |
| 真实 C07 等值线、自动九级范围、源摘要拒绝和任务取消 | Passed | `features/checks.json` |
| 101 点剖面、排版前后 CSV 与科学数组不变 | Passed | `features/checks.json`、`features/profile-before.csv` |
| 色谱材质独立、曲线和标签复制、删除清理 | Passed | `features/checks.json` |
| GUI 开关、异步旧结果丢弃、绑定失效及恢复 | Passed | `gui.json`、`gui-evidence/checks.json` |
| 全局视口与渲染显隐、子对象用户状态保持 | Passed | `gui-evidence/checks.json` |
| 两类工程保存、原目录及移动冷重开、重新渲染 | Passed | `features/checks.json`、`gui-evidence/checks.json` |
| 参数复制、计算段回归、源码与 ZIP/安装副本一致 | Passed | `regression-copy/checks.json`、`regression-jobs/checks.json`、`qualification.json` |

本批标签为 `qa/multiwfn-parameters-2026-09-28-03`。等值线和剖面排版在对象属性，四种色谱预设在材质属性；全局显示层仍在 N 侧栏。数值标签是可编辑的原生文字，不自动避让。默认九级阈值取当前显示范围的内部等间距值；显式阈值允许包含零。无效单元不生成跨越空洞的线段。

旧候选保留了标签更新显隐、全局子对象联动与失效提示恢复的复现证据。完整最终 SOP 见第四批；独立人工验收及外部视觉对照仍为 Not Run。

## 第四批：外部结果与最终资格

最终候选位于 `outputs/multiwfn-parameters/04-results-r2/`，构建源码 `f2cf3da`，验证提交 `580fbbe`，ZIP SHA-256 为 `d2a016d481249dba46df8501a2d961fb355a0caef9b60c3c5af8edbeeceb5872`。本批本地技术标签为 `qa/multiwfn-parameters-2026-09-28-04`。

| 检查 | 状态 | 证据（相对于最终候选目录） |
| --- | --- | --- |
| 69 项科学回归、独立配置安装、离线移动冷重开 | Passed | `science.json`、`offline/extension.json` |
| IGMH/IRI 全部有效点筛选后确定性抽样、数量和轴单位 | Passed | `result-C07/checks.json`、`gui.json` |
| ESP 原始区间与百分比、AIM 源编号、NBO/E(2)、NOCV 身份与定位 | Passed | `result-C08/`、`result-C09/`、`result-NBO/`、`result-C12/` 的 `checks.json` |
| 自定义高亮节点图修改前拒绝、源摘要变化和错误输入不破坏场景 | Passed | 五类结果的 `checks.json`、`final-sop/cases/` 错误输入记录 |
| 外部视图复制、删除、撤销、保存及各自双冷重开 | Passed | 五类结果和 `gui-evidence/checks.json` |
| 参数复制、计算段、探针/切片、等值线/剖面回归 | Passed | `regression-copy/`、`regression-jobs/`、`regression-interaction/`、`regression-charts/` 的 `checks.json` |
| GUI 散点更新、记录面板、IRC 切步、NOCV 导入与错误提示 | Passed | `gui.json`、`final-sop/cases/C10/steps-gui.json` |
| C01–C13 六栏全部完成，N01–N18 全部完成 | Passed | `final-sop/final-sop-summary.json`、`final-sop-summary.md` |
| 13 个工程分别在原目录与移动目录用新进程重开、重渲染 | Passed | 各例 `candidate-run.json`、`reopen-check.json`、`moved-check.json`；26 次独立进程 |
| 源码、已安装副本、ZIP 和 wheel 一致 | Passed | `qualification.json`、`evidence-index.json` |
| 独立人工验收、外部软件视觉对照 | Not Run | 继续后置，不代签，不发布 |

Computer Use 负责确认可读界面与实际按钮操作；重复导入、参数变更、数值与数组摘要核对采用 MCP 和独立 Blender 进程。SOP 记录型截图使用当前候选的对象属性面板，固定文件名与额外渲染分别保留；收集对应关系及 SHA-256 见 `final-sop/image-collection.json`。所有工程使用插件的便携保存，附带 `.qcdata`；本轮未改科学数组或归档格式。

NOCV 定位约束为同一关联构型、同一结果表 Dataset、pair、spin 及已有绑定；旧记录缺少表身份时明确要求重新导入。散点更换轴后立即展示所选量与单位，点击更新后才重新筛选。CP/ESP 筛选限定活动图层本身的分析类型，切换类型通过对应图层进行；不把伪元素解释为真实原子。

### 复验记录

`04-results-r1` 保留首次资格失败证据；上述 NOCV 身份、散点轴标签和自定义高亮图预检缺陷在 r2 修复并完整复验。最终 SOP 回放补齐 C03 显式映射步骤，IRI 指数按 Blender 浮点精度使用 `1e-6` 容差；C04 长时 ESP 任务超过 MCP 传输等待后，从已完成 worker 核对结果，没有重复计算或跳过源值检查。各次日志保留在候选目录。
