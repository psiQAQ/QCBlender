# 标注工作树权限与清理验收

2026-10-17，Windows / Blender 5.1.1。原工作树 `.worktrees/annotation-ui` 和 `feat/annotation-ui` 分支已正常移除；原注释标签 `archive/2026-10-17/feat/annotation-ui` 的对象及提交 `74ca98d5abe24025e3e77c4824830dadf84f255f` 均保持不变，提交仍可从 main 到达。没有修改 ACL、取得所有权或强制删除。

完整保全与删除收据在 `outputs/runs/annotation-ui-cleanup-20261017/`；[机器结果](../reports/2026-10-17/annotation-ui-cleanup/acceptance.json)保存候选、保护对象、实际进程和空间口径。[产物入口](../../../docs/ARTIFACTS.md#annotation-ui-20261017)集中定位原任务及日常插件更新。

| 验收 | 状态及范围 |
| --- | --- |
| 权限原因 | Passed：同一四路径在原创建账户下全部可读，日常用户下全部 WinError 5；`acl-owner.json` 只读核对受保护 DACL，允许 Owner Rights、SYSTEM、Administrators。`diagnosis-*.json` 记录实际账户差异 |
| 路径及清理边界 | Passed：逐层枚举，拒绝链接及 reparse point；清单只覆盖指定工作树及本批记录工作树，其他历史残留未处理 |
| 受限文件保全 | Passed：18 文件 / 14,908 字节，`sandbox-datasets.zip` SHA-256 `5d29e6e4cbf2d17f587834615fdce1b1cc2e3c0c16ca6b1b588469207e213dca`；原创建账户归档、日常用户核对 ZIP 成员，`sandbox-retention.json` 记录原路径、大小、mtime 和摘要 |
| 其余忽略文件保全 | Passed：8,851 文件 / 671,465,592 字节；统一 `finish` 完整核对后生成 `finish/annotation-ui-ignored.zip`，405,576,547 字节，SHA-256 `03ed4fddfc5176fb75e9148591d30843b91bd7b6753583152252a8543597f1b7`；对应 retention、archive 和计划复核 JSON 保留 |
| 工程副本与冷读 | Passed：37 文件逐字节相同；`projects/source-native/annotation-ui.blend`、`projects/native/annotation-ui.blend`、`projects/gui/g.blend` 及各自 `.qcdata` 在日常配置新进程冷重开，逐值核对科学坐标、构型记录、文字、字号和位置；`cold-acceptance.json` 与 `cold/` 保存原生报告和 PID/退出码 |
| 正常移除 | Passed：原拥有者正常删除四个已核验目录；日常用户执行 `git worktree remove` 和 `git branch -d`，统一工具收据 `finish/annotation-ui-archive.json`；没有失败残留 |
| 保护对象 | Passed：当前 ZIP、稳定候选、旧当前 ZIP、旧日常插件 ZIP、旧偏好备份及 `current-install.json` 的 SHA-256 与清理前相同，清单见机器结果 |
| 会话 | Passed：用户明确已保存关闭且无需恢复；三次后台 CLI 串行，PID 85000 / 49524 / 87280 均退出 0，结束无 Blender 进程 |
| 产品测试复跑、GUI、独立人工/科研接受 | Not Run：产品源码、候选和依赖没有变化；原任务测试和 GUI 报告保持原身份，本批只验收保全与清理，不代签独立接受 |

## 原因与复现

已有账户权限的差异已通过同一路径的直接读取确认。`qcblender/project.py::copy_dataset` 在私有临时目录下创建候选后发布到最终位置，与本轮观察到的创建账户 DACL 一致。此前日常用户执行的归档不能读取该目录，Git 的警告又混入忽略文件列表，报出“linked files”；本轮实际逐层检查未发现链接或 junction。

本次按现有权限分账户操作，没有更改访问控制，也没有修改产品代码。先保全原数据和工程副本，冷读通过后才删除原目录；其余文件仍使用统一归档工具。原任务的失败报告和早期 `delivery.json` 原样保留，不能据后续成功改写当时状态。

## 恢复与空间口径

日常打开使用 `projects/` 内三套已冷读副本。需要还原原忽略文件时，将两份 ZIP 按其工作树相对成员路径解压到同一新目录；`sandbox-datasets.zip` 补齐四个原先权限受限的 Dataset 目录。跟踪源码从原归档标签恢复，不需要恢复旧 ACL。

原工作树共正常移除 10,109 个文件 / 802,001,128 个逻辑字节，包含可从 Git 重建的跟踪文件及 `.git` 指针；其中 8,869 个忽略文件 / 671,480,500 字节已保全。删除阶段前后卷可用空间由 183,748,497,408 变为 184,159,952,896 字节，观察增加 411,455,488 字节；该差值包含新归档占用与同期文件系统活动，不等同于删除逻辑字节。本批记录工作树的后续移除不计入上述原工作树数字。

清理记录分支按本地 ff-only 流程整合，以 `archive/2026-10-17/chore/annotation-ui-cleanup` 注释标签归档；该工作树保全与正常移除的收据位于同批 `records/`。不 push、不更新远端标签或发布版本。
