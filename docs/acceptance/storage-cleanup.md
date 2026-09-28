# 输入集中与阶段产物清理记录

2026-09-29，Windows / Blender 5.1.1。按用户批准的范围维护仓库，不修改插件产品源码，不安装、卸载或更新依赖，不推送或发布。本轮只复验受迁移影响的检查；历史完整技术 SOP 不作为本次重新执行的结果。

## 用户工程

PID 3144 的当前状态已使用 **Save Portable QC Project** 另存到 `outputs/recovery/pid3144-preserved/evidence.blend`，同目录 `evidence.qcdata/` 配套保留。首次独立冷重开核对 4 个 Dataset、3 个体积文件和 19 个对象通过，随后保存最后界面状态并正常关闭原进程。该目录不进入清理范围；保存摘要和数组记录在 `preserved.json`。

## 输入与受影响检查

104 个原始输入及来源记录集中到 `tests/data/local/`；S01–S35 字节摘要不变，两个 IRC/Mayer CSV 的相对路径无需改写。受跟踪索引为 `tests/data/local-inputs.json`，人工目录为 [SOURCES.md](../v1-acceptance/SOURCES.md)。输入迁移与重建工具提交为 `d2d5fc7`。

| 检查 | 状态 | 证据（相对 `outputs/storage-cleanup/`） |
| --- | --- | --- |
| 保存前后 Dataset/数组/体文件关联，首次冷重开及原 PID 退出 | Passed | `preserved-before-cleanup.json`、保全目录 `preserved.json` |
| 104 个输入复制摘要、CSV 成套引用 | Passed | `input-migration.json`、`csv-validation.json` |
| 69 项科学回归，0 skipped | Passed | `science.json` |
| C07/C08/C09/C12/NBO 结果浏览、保存及移动冷重开 | Passed | 各案例 `checks.json` 及 `*-cold.log`、`*-moved.log` |
| 切片交互、等值线和线剖面，保存/移动冷重开 | Passed | `interaction/checks.json`、`charts/checks.json` |
| 从输入重建 C04、C07–C13 并核对来源详情 | Passed | `source-browser/checks.json` |
| 真实 IGMH/IRI 双场与有效域、原生面板/资产能力矩阵 | Passed | `scalar-edges/edges.json`、`foundation-core/core.json`、`foundation-nbo/nbo.json` |
| 必需输入缺失/变更拒绝，清理保护边界 | Passed | `tests/test_local_inputs.py`、`tests/test_storage_cleanup.py` |
| 本次重新执行完整技术 SOP、Computer Use 界面复验 | Not Run | 本次未改产品界面，只运行受影响的重建与数据检查 |
| 独立人工验收、外部视觉对照 | Not Run | 继续后置，不代签 |

密度/ESP 重建使用原始 S03 波函数和 0.7 Å 的显示测试网格；数值求值通过已安装扩展完成，没有复用历史场缓存作为输入。原始 Multiwfn 输出条件仍按 SOURCES 记录。字体依赖关系及外部内置笔刷相对路径警告保留在 Blender 日志中，不属于本次新发生的科学数组损坏。

## 清理与空间

| 项目 | 结果 |
| --- | --- |
| 清理前可读文件逻辑大小 | 22.85 GB（21.28 GiB） |
| 清理后可读文件逻辑大小 | 13.43 GB（12.51 GiB）；之后再移除 1.46 MB 源码字节码 |
| 清单实际删除 | 75,755 文件 / 9,390,323,949 字节 |
| 源码目录字节码清理 | 110 文件 / 1,463,630 字节 |
| 受保护文件 SHA-256 核对 | 229,800 项 Passed |
| 保全工程清理后冷重开 | Passed：4 Dataset / 3 体文件 / 19 对象 |
| 清理后科学回归和输入摘要 | Passed：69 tests / 0 skipped，104 个输入 |
| 既有标签、源码子模块及 Git 连通性 | Passed：35 个既有标签、3 个子模块，fsck 退出码 0 |

同权限、同扫描方式的实测文件大小减少约 9.42 GB。扫描无法读取的目录不计入大小，不能把此数值当作整个磁盘的物理分配量；空间差还包含 Blender 原生延迟清理和本次新增报告。完整字节数见 `space-report.json`、`size-before-full.json`、`size-after-full.json`。

现用软件环境和配置约 12.4 GB（含构建/测试环境及共享依赖），这是剩余容量的主体。另保留参考资料、集中输入、日志、保全工程及 Git 历史。清单中 74 个恢复文件（约 23.37 MB）归属未独立确认，继续保留；188 个扫描受限路径和 8 个拒绝删除的 `portable.zip` 未强制处理，未修改权限。未知用途输出也未删除。

清理校验发现 34 个旧安装暂存项在 Blender 启动后消失：`stale-pending`、`.~stale~` 标记及 31 个旧二进制副本。Blender 5.1.1 本地 `scripts/modules/addon_utils.py` 的 `_stale_pending_check_and_remove_once()` 在启动时执行该延迟清理；31 个二进制均有摘要相同的现用库副本，复核 Passed。它们属于原生安装缓存，不是本次卸载或更新依赖。原始例外仍保留在 `applied.json`，分类核查在 `exception-audit.json`；没有未解释的现用软件文件变化。

保全工程在普通 Agent 沙箱下读取部分目录会报权限错误；使用原 Blender 的宿主权限冷重开 Passed。对应失败和成功日志分别保留，不将权限失败解释成 Dataset 损坏。

逐项清单位于 `inventory.jsonl.gz`（每行包含绝对路径、用途/理由、大小、动作及修改时间；受保护环境另有 SHA-256）。`summary.json` 是分类汇总；`applied.json` 是实际删除和未处理项记录。未知归属、恢复文件和权限受限项按清单保留，不修改 ACL。

## 保留政策

已验收的候选 ZIP、历史生成工程及图像由本次授权清理，原始日志、摘要和历史 Passed 留存。历史记录中的二进制路径只是当时证据索引，不再声称可直接打开。需要新候选时从当前源码重建，记录新摘要并重新做安装资格检查；新包不是已删除固定候选的逐字节复现。

后续遵循 [存储维护规则](../agents/storage-maintenance.md)。保留安装环境、配置、构建/测试解释器、共享 wheels、集中输入、参考资料、源码子模块、Git 历史及既有技术/归档标签。本地提交合回 `main`，归档为 `archive/2026-09-29/chore/storage-cleanup`；不保留开发分支引用。
