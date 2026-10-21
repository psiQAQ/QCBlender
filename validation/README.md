# QCBlender 校验与教程

人工操作从 [SOP](human/SOP.md) 开始，按目录选择需要学习的专题。完整材料包含安装包和案例输入，适用 Windows x64、Blender 5.1.1、QCBlender 0.1.0。

完整实操材料已统一到本目录：按[工程索引](工程索引.md)查找 79 个步骤、27 张截图及 36 个最终工程/检查点，工程位于 `work/human/`。2026-10-22 从最新版交付材料迁入，验证及旧副本清理状态见[迁移记录](agent/acceptance/delivery-consolidation.md)；检查点的生成与保存前验证见[补验记录](agent/acceptance/checkpoint-rebuild.md)。独立人工和科研验收尚未执行。

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
| 使用本机 P02 检查优化、振动与 NBO | [本地限定案例](agent/LOCAL-CASES.md) |
| 审阅历史文件的保留与清理 | [清理清单](agent/CLEANUP.md) |

教程里的 `shared/`、`human/`、`work/` 均相对于本文件所在的材料根目录。仓库中的根目录是 `validation/`；复制到其他电脑后，相对位置保持相同。

## 目录用途

| 目录 | 用途 |
| --- | --- |
| `human/SOP.md`、`human/topics/` | 人工教程和按需专题，作为仓库及文档网站的教程源文件 |
| `human/screenshots/`、`human/renders/` | 教程引用的界面截图和渲染图，与文档一起纳入 Git |
| `shared/data/public/` | P01/P03/P04/P05/P06 公开案例、许可与来源说明 |
| `shared/data/local/` | 本机科学输入及原始计算材料，公开教程包排除 |
| `shared/data/regression/` | 自动回归使用的小样本 |
| `shared/install/` | 当前安装包 |
| `agent/` | 技术流程、检查覆盖、冻结材料及技术报告 |
| `work/human/` | 按教程生成的工程、配套科学数据、导出文件和移动副本，Git 忽略 |
| `work/agent/<批次>/` | 新 Agent 验证批次的工作文件，Git 忽略 |

截图前缀沿用所在章节的案例编号：P01 轨道入门与自旋密度，P03 水二聚体场和分析，P04 IRC，P05 ETS-NOCV，P06 XYZ 与公共节点；后缀说明图片内容。截图用于展示独有的操作入口、控件或视觉结果，同一结果的重复确认保留文字说明。

教程中的图片只引用 `human/` 内的图片文件。`.blend`、`.qcdata/`、CSV 导出和工程 ZIP 放在 `work/human/`；保留需要继续使用的工程及配套数据。既有 Agent 工作目录和 `outputs/runs/` 批次原位保留，由 [ARTIFACTS](../docs/ARTIFACTS.md) 定位。

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

公开样本附带的 `LICENSE`、`NOTICE.md` 和来源说明一起保留。公开入门包不包含 `local/`、`regression/`、`agent/` 和 `work/`。P02 的再分发许可未确认，仅本地案例页使用它。

需要连同已保存工程交给本地使用者检查时，在上述材料之外复制 `工程索引.md`，以及索引列出的 `work/human/` 工程、同名 `.qcdata/`、导出文件和工程归档；保持相对位置，排除 `.blend1` 等自动备份。不要直接打包整个 `validation/`，其中另有本地限定输入、回归数据和技术报告。分发包的 README 说明从 `human/SOP.md` 和 `工程索引.md` 开始即可；主仓库保留本页导航。

## 开发维护

当前整理规格与执行状态见[教程截图任务](../.scratch/tutorial-screenshots-20261011/spec.md)。新检出准备数据的方法见[数据目录](shared/data/README.md)；技术核对和清理收据与人工教程分开维护。发布前通过 [Agent 文档检查](agent/README.md#教程材料与完整图片检查)确认图片已补齐。全仓工程及历史证据仍由 [ARTIFACTS](../docs/ARTIFACTS.md) 路由。
