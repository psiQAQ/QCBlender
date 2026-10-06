# QCBlender 校验与教程

人工操作从 [SOP](human/SOP.md) 开始，按目录选择需要学习的专题。完整材料包含安装包和案例输入，适用 Windows x64、Blender 5.1.1、QCBlender 0.1.0。

## 入口

| 要做的事 | 位置 |
| --- | --- |
| 安装、生成第一张轨道图、导出和保存重开 | [人工 SOP](human/SOP.md) |
| 分子显示、XYZ、ESP、分析结果等专题 | [专题目录](human/SOP.md#topics) |
| 保存自己的截图 | `human/screenshots/`，文件名写在对应步骤下 |
| 查找案例输入与来源 | [数据目录](shared/data/README.md) |
| 查看当前安装文件 | [安装材料](shared/install/README.md) |
| 运行技术校验 | [Agent 流程](agent/README.md)、[检查覆盖](agent/COVERAGE.md) |
| 使用本机 P02 检查优化、振动与 NBO | [本地限定案例](agent/LOCAL-CASES.md) |
| 审阅历史文件的保留与清理 | [清理清单](agent/CLEANUP.md) |

教程里的 `shared/`、`human/`、`work/` 均相对于本文件所在的材料根目录。仓库中的根目录是 `validation/`；复制到其他电脑后，相对位置保持相同。

## 目录用途

| 目录 | 用途 |
| --- | --- |
| `human/` | 人工教程、按需专题及使用者补充的截图 |
| `shared/data/public/` | P01/P03/P04/P05/P06 公开案例、许可与来源说明 |
| `shared/data/local/` | 本机科学输入及原始计算材料，公开教程包排除 |
| `shared/data/regression/` | 自动回归使用的小样本 |
| `shared/install/` | 当前安装包 |
| `agent/` | 技术流程、检查覆盖、冻结材料及技术报告 |
| `work/human/` | 按教程生成的工程、导出文件和渲染 |
| `work/agent/` | Agent 本次运行的工作文件 |

## 人工完成后的打包

1. 将截图保存在 `human/screenshots/`，名称与步骤下的图片引用一致。只完成部分专题时，可在发给用户的说明中写明范围。
2. 新建一个用于分发的空文件夹，例如 `QCBlender-tutorial/`。按下表复制内容，保留目录层级。

   | 从本目录复制 | 分发文件夹中的位置 |
   | --- | --- |
   | `human/` | `QCBlender-tutorial/human/` |
   | `shared/data/public/` | `QCBlender-tutorial/shared/data/public/` |
   | `shared/install/` | `QCBlender-tutorial/shared/install/` |

3. 用文件管理器将 `QCBlender-tutorial/` 压缩为 ZIP。用户解压后打开 `human/SOP.md`；图片、输入和安装包保持相对位置即可。P04 的整个目录随包复制，其 CSV 会读取同目录的 FCHK 和分析表。

公开样本附带的 `LICENSE`、`NOTICE.md` 和来源说明一起保留。`local/`、`regression/`、`agent/` 和 `work/` 不进入教程压缩包。P02 的再分发许可未确认，仅本地案例页使用它。

## 开发维护

计划与执行状态在 [本地计划书](../.scratch/validation-layout/spec.md)。新检出准备数据的方法见[数据目录](shared/data/README.md)；技术核对和清理收据与人工教程分开维护。全仓工程及历史证据仍由 [ARTIFACTS](../docs/ARTIFACTS.md) 路由。
