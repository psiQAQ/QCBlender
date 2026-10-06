# 校验输入

输入原件统一放在本目录。人工教程使用 `public/`；本机限定案例使用 `local/`；自动测试使用 `regression/`。生成的工程、导出表和临时文件放到 `validation/work/` 或已有的 `outputs/runs/` 批次目录。

| 位置 | 内容 | 分发与 Git |
| --- | --- | --- |
| [public/](public/README.md) | P01/P03/P04/P05/P06 的 30 个公开输入，LICENSE、NOTICE 和来源清单 | 可以随人工教程打包；6 个大 Cube 和清单副本由冻结包恢复，其余小文件跟踪 |
| `local/` | Gaussian 日志、历史科研输入和 `calculations/public-tutorial/` 计算原件 | Git 忽略；不进入公开教程包 |
| `regression/` | cclib、ChemTools、GBasis、IOData 小样本及 visual-baseline | 原字节与原来源文件跟踪；公开教程包排除 |
| [local-inputs.json](local-inputs.json) | 本地与共享输入的稳定 key、当前路径、用途、来源和身份 | 当前机器入口；`original_path` 保留原来源定位 |
| [migration-map.json](migration-map.json) | 旧路径到当前位置的逐文件映射 | 不表示任何旧文件已删除 |
| [complex-example-sources.json](complex-example-sources.json)、[local-log-downloads.json](local-log-downloads.json) | 外部输入的固定获取地址与身份 | 来源记录，不授予额外再分发许可 |

## 准备公开材料

在仓库根目录使用已有 Python 3.13 执行：

```powershell
python -B tools/prepare_validation_data.py --report outputs/runs/validation-layout/public-inputs.json
```

命令从 `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip` 按允许成员集合恢复文件，验证 30 个输入、许可证与 P04 CSV 相对引用。已有文件必须匹配来源身份；不同内容直接失败，不覆盖用户文件。每次运行指定新的报告文件名。

公开包内的 `tutorial-samples.json` 与仓库的 [冻结清单](../../../docs/v1-acceptance/tutorial-samples.json) 保持原字节。清单的 `archive_path` 是 `public/` 内的当前路径；`path` 是冻结时的来源位置，不能作为当前读取入口。`P06/source.json` 同样保留生成时的来源定位。CI 校验冻结 ZIP、成员集合、逐文件身份及许可声明。

## 复制本地输入与计算原件

在新检出或工作树中，从已经整理好的参考检出复制。本机主检出已完成集中保存并清理旧副本，使用以下命令；`--reference-root` 为源检出的绝对路径：

```powershell
python -B tools/prepare_validation_data.py `
  --reference-root D:/workspace/QCBlender `
  --reference-layout current `
  --include-local `
  --include-calculations `
  --report outputs/runs/validation-layout/local-inputs.json
```

`current` 显式读取参考检出的集中位置。只有参考检出仍保有未迁移的旧布局时才选择 `--reference-layout legacy`，它只读取迁移清单列出的旧位置。命令不扫描删除、不回退寻找旧目录，也不修改参考检出。历史副本的实际清理结果见 [清理记录](../../agent/CLEANUP.md)。

计算原件按 `local/calculations/public-tutorial/owned/` 与 `irc/` 保存；与公开输入字节相同的文件复用 `public/`，对应原始位置由迁移映射定位。原始脚本、日志、PySCF checkpoint 及计算条件保留，不改写日志中的历史执行路径。需要重跑某个原始计算时，先按映射在新的工作目录恢复它的输入层级；不要直接运行归档脚本覆盖原件。工程内部 `.blend + .qcdata` 保持成套，不迁入此目录。

## 当前读取入口

- `tools.local_inputs.input_path(key, root)` 按当前索引核对单文件或目录 key，必需文件缺失、变化或越界时直接失败。
- `public-tutorial/P03/igmh` 等旧稳定 key 指向 `public/` 的同一份数据，不在 `local/` 重复保存公开原件。
- `QCBLENDER_REFERENCE_ROOT` 可指向已经准备好资料的参考检出；公开解析使用冻结清单中的 `archive_path`。
- P02 为 `local/log-examples/water_neutral_nbo_opt_freq.out` 和字节相同的 `.log` 别名。原数据再分发许可未确认，两者均不进入公开教程包。
- 人工教程不要求读者执行身份核对、填写技术报告或记录实际结果；这些步骤属于 Agent 的准备与维护工作。
