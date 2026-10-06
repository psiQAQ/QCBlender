# 历史文件清理待确认清单

更新：2026-10-06。**尚未删除任何历史文件。** 本页供维护者确认保留和清理范围；实际逐文件身份见 [JSON 清单](reports/2026-10-06/cleanup/inventory.json)，便于阅读的完整表见 [Markdown 清单](reports/2026-10-06/cleanup/inventory.md)。报告位于主检出，技术报告目录不进入 Git 或公开教程包。

本次快照针对主仓库 `outputs/` 中的既有资源。复制到 `validation/` 的新资源及旧输入迁移副本需要在整合后追加旧新路径核对；本页不授权删除这些额外路径。下文路径均相对仓库根目录，大小为文件逻辑字节数，不是磁盘净释放量。

## 保留对象

| 对象 | 保留位置与理由 |
| --- | --- |
| 最新完整候选 | `outputs/candidates/current/alpha-ci-0.1.0-190e11e/` 整套保留。安装包 `qcblender-0.1.0.zip` 为 50,656,021 字节；样本包 12,175,753 字节；复现包 943,116 字节；同目录清单和 10 份报告保留 |
| 最新 CI 原始容器 | `outputs/evidence/2026-10-06/actions-fix/run-37415371574/candidate-artifact.zip`，63,810,939 字节，保存最新下载的原始容器 |
| 教程安装入口 | `validation/shared/install/qcblender-0.1.0.zip` 是上述候选的原字节副本，定位见 [current-install.json](current-install.json) |
| 公开输入及冻结包 | `validation/shared/data/public/` 与 `validation/agent/packages/qcblender-public-tutorial-samples-v2.zip`；来源、许可和原始冻结清单保留 |
| 本地科学输入 | `validation/shared/data/local/`、`validation/shared/data/regression/`、原始计算日志/checkpoint 及生成脚本。迁移后核对索引与必要输入，不删除工程内部的 `.qcdata` |
| 用户与恢复工程 | `outputs/projects/`、`outputs/recovery/`、其他归属未明确的 `.blend/.qcdata` 与工程 ZIP，全部保留 |
| 环境、依赖与资料 | 共用 `outputs/build-python/`、`outputs/build-site/`、`outputs/science/`、`outputs/wheels/`、许可证、构建源码、科研参考原件及活跃配置保留 |
| 其他插件 | `outputs/mcp-1.0.0.zip`，16,842 字节，属于 Blender Lab MCP 插件，保留 |
| 报告和历史身份 | 原始报告、失败日志、来源记录、保全映射、Git 提交及归档标签保留。需要清理二进制时新增其可用性记录，不把原报告改成新候选结果 |

最新候选来自 CI run `37415371574`，本地记录显示北京时间 2026-10-06 12:49:48 成功完成。此次工具已实际核对三个 ZIP 的内容身份、CRC 及十份原报告的文件身份与 `Passed` 字段；当前 Blender 复跑和独立人工验收均为 `Not Run`。这项文件检查不产生新的产品测试通过结论。

## 待确认清理的分组

| 分组 | 文件数 | 字节 | 删除前条件 |
| --- | ---: | ---: | --- |
| 有名旧插件安装 ZIP | 15 | 759,647,855 | 最新候选与教程安装副本可用，现有文档路由更新，旧报告仍可定位 |
| 按摘要命名的旧安装对象 | 6 | 303,932,832 | 核对保全映射，只选择下列六个对象，不删除整个 `objects/` |
| 旧版或重复公开样本 ZIP | 7 | 85,225,361 | 最新冻结包和公开原件可用；历史 NOTICE 与清单差异已保存 |
| 旧自动复现 ZIP | 3 | 2,829,077 | 最新复现包可用，原批报告和身份保留；不扩大到用户工程 ZIP |
| 旧 CI 外层压缩包 | 1 | 63,810,897 | 旧 CI 日志、下载收据、清单及报告已在容器外保留 |
| 不完整 VESTA 下载 | 1 | 1,029,378 | 确认该残缺下载无需继续保留；不删除其他第三方工具 |
| **合计** | **33** | **1,216,475,400** | **按逐文件清单确认后另行执行** |

其中旧安装包合计 **21 个文件、1,063,580,687 字节**。它们的分类是“已被最新候选替代”；本清单没有断言每一个旧包都损坏。

### 15 个有名旧安装 ZIP

| 路径 | 字节 |
| --- | ---: |
| `outputs/candidates/baseline/reliability-prehash-982e339/qcblender-0.0.1.zip` | 50,644,984 |
| `outputs/candidates/baseline/reliability-posthash-94b99f5/qcblender-0.0.1.zip` | 50,645,010 |
| `outputs/candidates/current/alpha-0.1.0-19e4cf0/qcblender-0.1.0.zip` | 50,656,085 |
| `outputs/candidates/current/alpha-ci-0.1.0-f8b1115/qcblender-0.1.0.zip` | 50,656,040 |
| `outputs/candidates/current/audit-p1-a4baaaf/qcblender-0.0.1.zip` | 50,638,451 |
| `outputs/candidates/current/audit-p2-49872b0/qcblender-0.0.1.zip` | 50,635,805 |
| `outputs/candidates/current/display-xyz-export-9d3ff61/qcblender-0.0.1.zip` | 50,635,717 |
| `outputs/candidates/current/reliability-final-a3ed826/qcblender-0.0.1.zip` | 50,645,094 |
| `outputs/evidence/2026-10-04/audit-p1/candidate-v1/qcblender-0.0.1.zip` | 50,638,205 |
| `outputs/evidence/2026-10-04/audit-p1/candidate-v2/qcblender-0.0.1.zip` | 50,638,451 |
| `outputs/evidence/2026-10-04/audit-p2/candidate/qcblender-0.0.1.zip` | 50,635,805 |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/preserved/outputs/repository-cleanup/final/dist/qcblender-0.0.1.zip` | 50,632,940 |
| `outputs/evidence/2026-10-04/legacy-worktree-retry/preserved/outputs/repository-cleanup/phase02/dist/qcblender-0.0.1.zip` | 50,633,098 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/qcblender-0.1.0.zip` | 50,656,085 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/dist/qcblender-0.1.0.zip` | 50,656,085 |

### 6 个无后缀安装对象

下面六个文件都在 **`outputs/evidence/2026-10-05/alpha-readiness/objects/`** 中；表中完整文件名追加到该父目录即为准确路径。原路径与当前对象的一一对应见 `outputs/evidence/2026-10-05/alpha-readiness/preservation-map.jsonl.gz`。本次已核对 ZIP 内扩展 ID 为 `qcblender`，文件摘要与保全映射相符。

| 完整文件名 | 原批次 | 字节 |
| --- | --- | ---: |
| `64e3709d75e10a070854eaf712f0fac230435bd87c5c55b1a35e4aaac16703a3` | ac1 | 50,654,719 |
| `135f11b260b0ac3a353e50d7308189bd959f062bc2df295d3bb22fe286d3ad70` | ac2 | 50,654,971 |
| `74a13eecf3728bd8c2ed8569323b539775969b115d5e6860b991209d99e785b8` | ac3 | 50,655,046 |
| `3e2fef693fd117d3f1d5c539c734c60aa235e6ee21ed4fa476af33437e52c07e` | ac4 | 50,655,964 |
| `67a48d6ff601cef0ce807d33675f64f38f53acd23fbad9e73ebd9119c0ecb5f3` | ac5 | 50,656,047 |
| `0c2d9add59b6332f243c5cd87b852a38b94090286f1b7671d7666694a4b73a03` | ac6 | 50,656,085 |

### 其他 12 个候选

| 路径 | 字节 | 分类 |
| --- | ---: | --- |
| `outputs/candidates/current/alpha-0.1.0-19e4cf0/qcblender-public-tutorial-samples-v2.zip` | 12,175,753 | 样本副本 |
| `outputs/candidates/current/alpha-ci-0.1.0-f8b1115/qcblender-public-tutorial-samples-v2.zip` | 12,175,753 | 样本副本 |
| `outputs/evidence/2026-09-30/public-tutorial/samples/qcblender-public-tutorial-samples-v1.zip` | 12,173,296 | 旧样本 |
| `outputs/evidence/2026-10-02/display-xyz-export/final/samples/qcblender-public-tutorial-samples-v2.zip` | 12,175,753 | 样本副本 |
| `outputs/evidence/2026-10-02/display-xyz-export/samples/qcblender-public-tutorial-samples-v2.zip` | 12,175,902 | 早期 v2 清单不同 |
| `outputs/evidence/2026-10-02/tutorial-cu/final-samples/qcblender-public-tutorial-samples-v1.zip` | 12,173,151 | 旧样本 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/qcblender-public-tutorial-samples-v2.zip` | 12,175,753 | 样本副本 |
| `outputs/candidates/current/alpha-0.1.0-19e4cf0/qcblender-reproduction-0.1.0.zip` | 943,011 | 旧复现包 |
| `outputs/candidates/current/alpha-ci-0.1.0-f8b1115/qcblender-reproduction-0.1.0.zip` | 943,055 | 旧复现包 |
| `outputs/evidence/2026-10-05/alpha-readiness/ac6/artifact/qcblender-reproduction-0.1.0.zip` | 943,011 | 旧复现包 |
| `outputs/evidence/2026-10-06/actions-fix/run-37414740265/candidate-artifact.zip` | 63,810,897 | 旧 CI 容器 |
| `outputs/reference-tools/VESTA-3.5.8-win64.zip` | 1,029,378 | 缺少可读取的 ZIP 中央目录 |

旧 v1 包没有 P06，其 `NOTICE.md` 与 `tutorial-samples.json` 和当前版本不同；早期 v2 也有清单差异。清理时先保存这些独有的小文件及原包身份，不能仅因数据主体重复而丢失历史署名与来源。

## 扫描边界与执行前复核

本次工具明确排除 **434 个目录或链接入口**，包括共用环境、用户/恢复工程、`.qcdata`、未指定的内容对象库和扩展安装目录；这些目录的全部内部文件没有被此次扫描验证。另有 **19 个 ZIP 读取失败**，准确路径与原始错误全部在 JSON/Markdown 报告中，保持原位。它们主要位于历史 `tutorial-cu/full/`、`public-tutorial-mcp/` 和两个 `outputs/runs/cu/4/.../portable.zip`。

`outputs/evidence/2026-10-05/reliability/gui/dataset-fixture.zip` 用途暂不归入安装残包，保留。源码 ZIP、IGMH/IRI 原始教程资料和 Multiwfn 工具包保留。本轮没有检查活动进程引用、用户现用安装或每份工程的冷重开；不能据此清理环境或工程。

执行顺序由主 Agent 维护：先完成新资源复制、必要原件与来源保全及当前文档引用更新，再请维护者确认本页准确文件清单；获批后按 [存储维护规则](../../docs/agents/storage-maintenance.md) 复核每个目标的绝对路径、大小、修改时间和摘要，再执行独立清理步骤并保存收据。文件变化、链接、权限拒绝或用途未明确的项均保留。

[inventory_cleanup.py](tools/inventory_cleanup.py) 仅有扫描与报告输出参数，**没有 `apply` 或删除功能**。重新扫描必须选择新的报告目录；完整命令见 [Agent README](README.md#清理盘点与收尾)。
