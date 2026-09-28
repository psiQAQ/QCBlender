# Multiwfn 参数与界面技术验收

本轮按 [规格](../.scratch/multiwfn-parameters/spec.md) 顺序集成。独立人工验收和外部视觉对照单独维护。

## 界面分工

| 位置 | 职责 |
| --- | --- |
| N 侧栏 | 导入导出、创建对象、数值摘要、全局显示层 |
| 对象属性 | 科学属性、几何表示、颜色范围、空间参数、局部选择与标注 |
| 材质属性与着色编辑器 | 默认独立材质、颜色、透明度、粗糙度及原生材质节点 |
| Render / Output / Color Management | Blender 原生渲染设置 |
| Geometry Nodes 与资产浏览器 | 显示流程、按用途分组的输入、九个分类通用节点 |

## 当前候选

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
| 等值线与剖面集成 | Passed | 第三批候选，见下表 |
| 外部浏览集成 | Failed | 第四批已集成；专项运行通过，追加审查缺陷待修复和重新资格验证 |
| 最终 C01–C13 六栏及 N01–N18 | Not Run | 在最终候选执行 |

运行故障与复验方法见 [开发注意事项](DEVELOPMENT_PITFALLS.md)。本记录不替代 SOP 独立人工签署。

第一批本地技术标签为 `qa/multiwfn-parameters-2026-09-28-01`。其范围限于上述已执行检查；最终全量 SOP 继续在后续候选上执行。

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

旧候选保留了标签更新显隐、全局子对象联动与失效提示恢复的复现证据。完整最终 SOP、独立人工验收及外部视觉对照仍为 Not Run。
