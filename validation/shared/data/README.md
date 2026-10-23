# 校验输入

输入原件统一放在本目录。人工教程使用 `public/`；本机限定案例使用 `local/`；自动测试使用 `regression/`。保留的校验工程放 `validation/work/`，临时工作放 `.tmp/runs/`，正式导出放对应输出目录。

2026-10-22 整理保留的历史原件位于 `local/legacy-v1/`、`local/legacy-runs/`、`local/legacy-archives/`，均保持 Git 忽略及原始字节。来源旧路径、摘要和用途统一由 [ARTIFACTS](../../../docs/ARTIFACTS.md#output-layout-20261022) 指向的迁移映射定位，不授予额外再分发许可。

| 位置 | 内容 | 分发与 Git |
| --- | --- | --- |
| [public/gaussian-v1/](public/README.md) | 当前 P01–P06 的185个数据文件及版本清单，包含自有P02优化/频率/NBO日志 | 按逐文件许可清单随教程打包；科学输入从v3包恢复，当前版本清单显式跟踪 |
| `public/P01/`–`public/P06/`、根 `public/tutorial-samples.json` | legacy-v2历史输入与历史清单副本 | 保留原字节；历史身份由冻结清单与v2包核对，不作为当前教程入口 |
| `local/` | 历史受限Gaussian日志、本地科研输入和 `calculations/public-tutorial/` 历史计算原件 | Git 忽略；不进入公开教程包 |
| `regression/` | cclib、ChemTools、GBasis、IOData 小样本及 visual-baseline | 原字节与原来源文件跟踪；公开教程包排除 |
| [local-inputs.json](local-inputs.json) | 本地与共享输入的稳定 key、当前路径、用途、来源和身份 | 当前机器入口；`original_path` 保留原来源定位 |
| [migration-map.json](migration-map.json) | 旧路径到当前位置的逐文件映射 | 不表示任何旧文件已删除 |
| [complex-example-sources.json](complex-example-sources.json)、[local-log-downloads.json](local-log-downloads.json) | 外部输入的固定获取地址与身份 | 来源记录，不授予额外再分发许可 |

迁移表中 `bytes` 和 `sha256` 校验当前文件；样本包目录 README 的路径说明更新后，原来源身份保存在该条目的 `source_identity`。冻结 ZIP、清单及科学输入的字节身份保持不变。

## 准备公开材料

在仓库根目录使用已有 Python 3.13 执行：

```powershell
python -B tools/prepare_validation_data.py `
  --dataset current `
  --report validation/agent/reports/2026-10-24/gaussian-sop/public-inputs.json
```

`current` 是默认值，由 [活动交付记录](../../agent/acceptance/tutorial-sample-delivery.json) 选择当前数据集与包身份。目前为 `gaussian-v1` / `validation/agent/packages/qcblender-public-tutorial-samples-v3.zip`。命令按允许成员集合恢复185个数据文件至 `public/gaussian-v1/`，并恢复当前清单及根许可说明；核对逐文件身份、许可和P04两份CSV的全部相对引用与步号。已有文件必须匹配选定身份；不同内容直接失败，不覆盖用户文件。每次运行指定新的报告文件名。

v3包根 `tutorial-samples.json` 与仓库的 [当前清单](public/gaussian-v1/tutorial-samples.json) 保持原字节。当前清单的 `archive_path` 为 `gaussian-v1/Pxx/...`，相对于 `public/`；`path` 对应仓库内的版本化输入路径。当前 `P06/source.json` 指向新P03及新P04第1/35/69帧，并记录各源SHA-256。

显式选择 `--dataset legacy-v2` 才恢复历史v2包；[冻结清单](../../agent/v1-acceptance/tutorial-samples.json)与v2包的原字节身份保留在活动记录的 `legacy_dataset` 中，schema 1旧记录仍兼容。历史清单的 `archive_path` 用于定位 `public/` 下的旧输入，`path` 仅保留冻结时的来源位置。不要重跑旧finalize流程覆盖冻结原件，也不要用旧GUI或科学验证结论代替当前数据验收。

## 复制本地输入与计算原件

在新检出或工作树中，从已经整理好的参考检出复制。本机主检出已完成集中保存并清理旧副本，使用以下命令；`--reference-root` 为源检出的绝对路径：

```powershell
python -B tools/prepare_validation_data.py `
  --dataset legacy-v2 `
  --reference-root D:/workspace/QCBlender `
  --reference-layout current `
  --include-local `
  --include-calculations `
  --report validation/agent/reports/2026-10-24/gaussian-sop/legacy-inputs.json
```

此处 `--dataset legacy-v2` 保留既有本地迁移流程；当前数据模式不接受 `--include-local` 或 `--include-calculations`。`--reference-layout current` 读取参考检出的集中位置，与数据版本选择是两个不同参数。只有参考检出仍保有未迁移的旧布局时才选择 `--reference-layout legacy`，它只读取迁移清单列出的旧位置。命令不扫描删除、不回退寻找旧目录，也不修改参考检出。历史副本的实际清理结果见 [清理记录](../../agent/CLEANUP.md)。

legacy计算原件按 `local/calculations/public-tutorial/owned/` 与 `irc/` 保存；与历史公开输入字节相同的文件复用旧 `public/` 位置，对应原始位置由迁移映射定位。原始脚本、日志、PySCF checkpoint及计算条件保留，不改写日志中的历史执行路径。需要重跑某个原始计算时，先按映射在新的工作目录恢复它的输入层级；不要直接运行归档脚本覆盖原件。当前Gaussian-v1的私有计算证据另按本批记录保存，不由此历史迁移命令复制。工程内部 `.blend + .qcdata` 保持成套，不迁入此目录。

## 当前读取入口

- `tools.tutorial_dataset.load_dataset(root, dataset='current')` 选择并核对当前manifest与包身份；`dataset='legacy-v2'` 显式选择历史数据。默认教程、样本包校验与便携复制使用当前选择；读取输入时按所选清单的 `archive_path` 定位。
- `tools.local_inputs.input_path(key, root)` 继续按本地/历史索引核对单文件或目录key，必需文件缺失、变化或越界时直接失败。`public-tutorial/P03/igmh` 等旧稳定key保留其legacy-v2文件与旧SHA，不重定向为新Gaussian数据。
- `QCBLENDER_REFERENCE_ROOT` 可指向已经准备好资料的参考检出，供本地/历史索引解析使用；它不改变 `load_dataset` 的数据版本选择。
- 当前公开P02为 `public/gaussian-v1/P02/water_neutral_nbo_opt_freq.out`，属于本批自有计算日志，按当前逐文件许可清单纳入v3包。历史 `local/log-examples/water_neutral_nbo_opt_freq.out` 及其字节相同的 `.log` 别名仍为再分发许可未确认的原输入，保持本地限定，均不进入v3包。分发依据文件身份与许可判断，不能仅按P02案例编号一概允许或排除。
- `scientific-displays/ru-vdw-20261023` 指向真实 Multiwfn 距离投影的八文件参照包及三份适配器输入（`reference.xyz`、`scan.json`、`validity.csv`），共十一文件；含固定构型、扫描日志/设置、原始三列及独立球面求交点表。条件和误差界见[研究记录](../../../docs/research/scientific-display-reference-inventory-20261023.md#本次实际运行及数值验收)。原件及派生数据限本地使用，不进入公开教程包。
- 人工教程不要求读者执行身份核对、填写技术报告或记录实际结果；这些步骤属于 Agent 的准备与维护工作。
- `scientific-displays/aicd-benzene` 指向同源全电子/π 的八个 Gaussian 原件及两份 `source.json` 导入声明；各原件和声明由 `local-inputs.json` 核对。基准条件及原始点契约见[研究记录](../../../docs/research/scientific-display-reference-inventory-20261023.md#aicd-本次实际运行及数值契约)，操作见[AICD 专题](../../human/topics/11-aicd.md)。原件限本地使用，不进入公开教程包。
