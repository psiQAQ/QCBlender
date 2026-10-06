# 03 数据迁移

Triage: ready-for-agent
Status: resolved
Blocked by: 01
Owner: data agent

## Scope

负责 `validation/shared/data/`、`validation/agent/packages/`、数据当前索引、必要 tools/tests 路径适配、`.gitignore` 及迁移报告/工具。冻结 `docs/v1-acceptance/tutorial-samples.json` 内容不变；历史报告原字节不变。未跟踪数据先复制保全，不删除旧原件。安装包 shared/install 由主 Agent 集中。

## Acceptance

公开 30 输入和许可证齐全、CSV 同组相对引用有效；本地稳定 key 可用且无公开重复原件；单文件/目录 key、REFERENCE_ROOT 和边界拒绝通过；相关回归与冻结公开包检查通过，未执行检查明确列出。迁移映射可供 main 重放，旧原件删除待任务 06 确认。

## Answer

当前原件位于 `validation/shared/data/public/`、`local/`、`regression/`，入口为该目录 `README.md`。公开 30 个输入按冻结 `archive_path` 汇集，P04 相对路径保持。6 个大 Cube 和公开清单副本从跟踪的 `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip` 恢复；其他小型输入和回归样本在 Git 中迁移。`.gitattributes` 保留源文件原字节。

`tools/prepare_validation_data.py` 只创建或验证明确列出的文件；`--reference-layout legacy/current` 显式选择参考检出布局，缺文件、内容变化和越界直接失败，不覆盖、不自动回退、不删除。`migration-map.json` 保存 292 条原路径映射；111 个稳定 key 包括 P02 的字节相同 `.log` 别名，6 个既有 `public-tutorial` key 复用公开原件。必要计算原件按映射保存，9 个 `.chk` 身份保留；历史日志与脚本不改写。

公开 NOTICE 使用冻结 v2 包的原始 859 字节，含 P06 声明；原 658 字节说明保存在 `regression/provenance/tutorial-v1-NOTICE.md`。冻结 `docs/v1-acceptance/tutorial-samples.json` 保留原路径，清单和 v2 ZIP 均保持原字节。

| 检查 | 状态与证据 |
| --- | --- |
| 首次复制与当前布局重放 | Passed；`outputs/runs/validation-layout/data-preparation.json`、`data-preparation-current.json`，30 个公开输入、111 个本地 key、218 条复制/复用映射 |
| 标准库套件 | Passed；134 tests，0 failures/errors/skips；`outputs/runs/validation-layout/stdlib.json` |
| Public-core 数值套件 | Passed；67 tests，0 failures/errors/skips；`outputs/runs/validation-layout/public-core.json` |
| 完整科学套件 | Passed；123 tests，0 failures/errors/skips；`outputs/runs/validation-layout/science-full.json` |
| 冻结教程样本与科学接口 | Passed；31 个输入、30 个 included；`outputs/runs/validation-layout/tutorial-samples.json` |
| Git 暂存字节与源文件保全 | Passed；72 个已跟踪数据文件的工作区字节与 Git blob 一致，67 个迁移原件保持原 blob；冻结包 33 个成员逐字节相同；`outputs/runs/validation-layout/staged-data-bytes.json` |
| 最终路径边界复验 | Passed；6 个 local_inputs/validation_data 测试及实际 31 个目录 key；缺失、变更、路径越界、共享 key、显式布局和不覆盖行为有效 |
| PySCF checkpoint 密度比较 | Not Run；选用的现有 Blender Python/science 环境没有 PySCF，未安装依赖 |
| Blender 界面与独立人工验证 | Not Run；任务 05 和维护者分别处理 |

上述报告对应本分支开发检出；main 与实际安装环境由任务 05 重新核对。旧忽略输入和 outputs 原计算文件均保留，删除仍待任务 06。主检出合并后执行同一准备命令补齐忽略资源：

```powershell
python -B tools/prepare_validation_data.py `
  --reference-root D:/workspace/QCBlender `
  --reference-layout legacy `
  --include-local `
  --include-calculations `
  --report outputs/runs/validation-layout/data-preparation.json
```

已有该报告时指定新的文件名；从完成整理的检出复制时使用 `--reference-layout current`。

## Comments

2026-10-06：数据 Agent 已领取。公开输入按冻结清单装配；本地资料只复制并核对，旧的忽略目录及 outputs 原件保留，后续删除由任务 06 确认。
