# QCBlender 校验与教程

人工操作从 [SOP](human/SOP.md) 开始，按目录选择需要学习的专题。完整材料包含安装包和案例输入，适用 Windows x64、Blender 5.1.1、QCBlender 0.1.0。

当前教程包含主线及 12 个专题，共 **98 个编号步骤、79 个展示图片引用**。按[工程索引](工程索引.md)查找步骤、图片与工程；当前 Gaussian 工程位于 `work/human/gaussian-v1/`，科学输入位于 `shared/data/public/gaussian-v2/`。21 份新工程均已保存并冷读通过，0 差异。首轮新增 44 张截图，原目标复查另补 4 张，并重拍 IRC 总览；当前共 48 张新增图及 27 张重拍图，均已转为 PNG。材料和独立公开副本检查通过，独立人工和科研验收 Not Run。详见[本批验收](agent/reports/2026-10-24/gaussian-sop/acceptance.md)。

旧 `work/human/P01/` 等目录及其 36 份工程保留历史身份。2026-10-22 的迁移与旧副本清理见[迁移记录](agent/acceptance/delivery-consolidation.md)，当时检查点的生成与保存前验证见[补验记录](agent/acceptance/checkpoint-rebuild.md)；这些旧记录不代表当前 Gaussian 案例已完成验证。

## 入口

| 要做的事 | 位置 |
| --- | --- |
| 安装、生成第一张轨道图、导出和保存重开 | [人工 SOP](human/SOP.md) |
| 按步骤或截图打开已保存工程 | [工程索引](工程索引.md)；编辑前另存自己的副本 |
| 分子显示、XYZ、ESP、分析结果等专题 | [专题目录](human/SOP.md#topics) |
| 保存自己的截图 | `human/screenshots/`，以 `Pxx-内容.png` 命名，具体路径写在对应步骤下 |
| 保存教程渲染图 | `human/renders/`，教程直接引用渲染成品 |
| 查找案例输入与来源 | [数据目录](shared/data/README.md) |
| 查看当前安装文件 | [安装材料](shared/install/README.md) |
| 运行技术校验 | [Agent 流程](agent/README.md)、[检查覆盖](agent/COVERAGE.md) |
| 使用公开 P02 学习优化、振动与 NBO | [Gaussian 日志专题](human/topics/12-gaussian-log.md) |
| 查找旧的本机限定日志案例 | [历史本地案例](agent/LOCAL-CASES.md) |
| 审阅历史文件的保留与清理 | [清理清单](agent/CLEANUP.md) |

教程里的 `shared/`、`human/`、`work/` 均相对于本文件所在的材料根目录。仓库中的根目录是 `validation/`；复制到其他电脑后，相对位置保持相同。

## 目录用途

| 目录 | 用途 |
| --- | --- |
| `human/SOP.md`、`human/topics/` | 人工教程和按需专题，作为仓库及文档网站的教程源文件 |
| `human/screenshots/`、`human/renders/` | 教程引用的界面截图和渲染图，与文档一起纳入 Git |
| `shared/data/public/` | 当前 `gaussian-v1/` 的 P01–P06 公开案例、许可与来源说明；根目录旧输入保留历史身份 |
| `shared/data/local/` | 本机科学输入及原始计算材料，公开教程包排除 |
| `shared/data/regression/` | 自动回归使用的小样本 |
| `shared/install/` | 当前安装包 |
| `agent/` | 技术流程、检查覆盖、冻结材料及技术报告 |
| `work/human/gaussian-v2/` | 当前原生53帧 P04 与 P06 新工程、侧车、导出和归档，Git 忽略 |
| `work/human/gaussian-v1/` | 未变化工程继续复用；旧69帧 P04/P06 保留历史身份 |
| `work/human/` 其余历史案例目录 | 旧教程工程、配套数据与移动副本，保留原批次身份，Git 忽略 |
| `work/agent/<批次>/` | 新 Agent 验证批次的工作文件，Git 忽略 |

截图前缀沿用所在章节的案例编号：P01 轨道入门与自旋密度，P02 Gaussian 日志，P03 水二聚体场和分析，P04 IRC，P05 ETS-NOCV，P06 XYZ 与公共节点，SD01 表面距离投影，AICD01 电流响应；后缀说明图片内容。截图用于展示独有的操作入口、控件或视觉结果，同一结果的重复确认保留文字说明。

教程中的图片只引用 `human/` 内的图片文件。当前新 P04/P06 的 `.blend`、`.qcdata/`、CSV 导出和工程 ZIP 放在 `work/human/gaussian-v2/`，其他未变化工程沿用 `work/human/gaussian-v1/`；保留需要继续使用的工程及配套数据。Agent 临时工作放 `.tmp/runs/`，长期报告放 `validation/agent/reports/<date>/<task>/`；既有批次当前位置由 [ARTIFACTS](../docs/ARTIFACTS.md) 定位。

## 人工完成后的打包

1. 按教程步骤保存截图和渲染图，路径与步骤下的图片引用一致。只完成部分专题时，可在发给用户的说明中写明范围。
2. 新建一个用于分发的空文件夹，例如 `QCBlender-tutorial/`。按下表复制内容，保留目录层级。

   | 从本目录复制 | 分发文件夹中的位置 |
   | --- | --- |
   | `human/SOP.md` | `QCBlender-tutorial/human/SOP.md` |
   | `human/topics/` | `QCBlender-tutorial/human/topics/` |
   | `human/screenshots/` | `QCBlender-tutorial/human/screenshots/` |
   | `human/renders/` | `QCBlender-tutorial/human/renders/` |
   | `shared/data/public/` | `QCBlender-tutorial/shared/data/public/` |
   | `shared/install/` | `QCBlender-tutorial/shared/install/` |

3. 用文件管理器将 `QCBlender-tutorial/` 压缩为 ZIP。用户解压后打开 `human/SOP.md`；图片、输入和安装包保持相对位置即可。P04 的整个目录随包复制，其 CSV 会读取同目录的 FCHK 和分析表。

公开样本附带的 `LICENSE`、`NOTICE.md` 和来源说明一起保留。公开入门包不包含 `local/`、`regression/`、`agent/` 和 `work/`。当前公开 P02 使用自有 Gaussian 日志，许可随公开材料保留；历史本机 P02 日志与专题 10/11 的本机限定材料不进入公开教程包。

需要连同已保存工程交给本地使用者检查时，在上述材料之外复制 `工程索引.md`，以及索引列出的当前 `work/human/gaussian-v2/` 及继续复用的 `work/human/gaussian-v1/` 工程、同名 `.qcdata/`、导出文件和工程归档；需要历史或本机限定专题时，再按各自范围与来源条件附上对应工程，保持相对位置，排除 `.blend1` 等自动备份。不要直接打包整个 `validation/`，其中另有本地限定输入、回归数据和技术报告。分发包的 README 说明从 `human/SOP.md` 和 `工程索引.md` 开始即可；主仓库保留本页导航。

## 开发维护

当前整理规格与执行状态见[Gaussian 教程任务](../.scratch/sop-gaussian-20261024/spec.md)及[原目标复查](../.scratch/sop-gaussian-20261024/issues/05-original-goal-audit.md)。新检出准备数据的方法见[数据目录](shared/data/README.md)；技术核对和清理收据与人工教程分开维护。发布前通过 [Agent 文档检查](agent/README.md#教程材料与完整图片检查)确认图片已补齐。全仓工程及历史证据仍由 [ARTIFACTS](../docs/ARTIFACTS.md) 路由。
