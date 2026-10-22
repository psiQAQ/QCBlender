# outputs 分类整理（2026-10-22）

用户批准按用途整理 outputs，历史 QCBlender 安装包仅保留当前已验证版本；当前身份仍由 [current-install.json](../current-install.json) 指定。构建输入进入 `modules/`，有用缓存与临时工作进入 `.tmp/`，本机配置进入 `.local/`；科学输入、工程和长期证据沿用集中目录。

## 权威证据

本批唯一详细记录目录：`validation/agent/reports/2026-10-22/output-layout/`。

- `migration.jsonl.gz`：逐文件原路径、新路径、SHA-256、用途及保留/迁移/退役决定。
- `archive-members.jsonl.gz`：混合 ZIP 的成员摘要、保留位置及退役理由。
- `plan.json`：清单身份和扫描范围；`blocked.json`、`unreadable-files.json`：链接、目录或文件读取受限项。
- `copy-all.json`、`removed.jsonl.gz`、`cleanup.json`：复制核验与实际删除结果。
- `protected-project-groups.json`：9 组工程的原位保护覆盖；已复制部分不作为完整迁移结果。
- `imports.json`、`science/`、`offline-package.json`、`representative-after-cleanup.json`、`original-restoration.json`：实际运行范围和结果。
- `integrated-paths/`、`integrated-stdlib/`、`execution/`：最终主检出检查和本批真实执行原始记录；`path-tests/` 保留子任务早期记录；`residuals.json`、`inspect-retained.ps1` 保存未完成项及只读核验入口。

旧报告不改写 Passed、提交、候选或执行时绝对路径。文件当前位置使用映射定位；旧安装包退役后，历史 Passed 不再表示二进制可取得。

## 验证状态

| 范围 | 状态与实际结果 |
| --- | --- |
| 文件迁移 | Passed：10,130 个原文件核验后移除旧位置；混合归档独有成员先保全 |
| 清理 | Passed：58,121 个退役文件，5,961,811,713 逻辑字节；无删除失败。连同迁移旧位置，共删除 68,251 文件 |
| 保护对象和当前包 | Passed：619 个原位保留文件摘要一致；当前候选及教程安装入口身份不变，11 个锁定 wheel 一致 |
| 代码及数值验证 | Passed：最终主检出的 272 项标准库、98 项路径相关检查；新环境导入和 5 项科学/项目回归 |
| 实际构建与迁移工程 | Passed：一次离线构建、100 个源码文件和 11 个 wheel 核验；代表工程删源后独立冷读零差异，3 个 Dataset 均位于新侧车目录 |
| 原 P01 恢复 | Passed：恢复到原路径、dirty=false，科学数组、对象、节点、材质和编辑器类型一致；GUI 区域像素尺寸不同 |
| 严格完整 GUI 快照 | Failed：首次断言记录 groups/materials/screens 差异；后续只读快照与基线仅剩 8 处 GUI 区域尺寸差异，原失败记录未覆盖 |
| 初轮受限对象处置 | Not Run（当时）：35 个受限目录、6 个受限文件和 1 个 junction 保留；续办结果见下节。未知 `outputs/1.blend` 继续保护 |
| 独立人工/科研验收、远端 CI | Not Run：本地目录和工具迁移不代替这些验收 |

磁盘可用空间变化和最终分支归档见同批 `closing.json`；逻辑退役字节与磁盘可用空间分别统计，不用读取失败对象推算空间。构建前首次源码身份检查因新许可尚未提交而 Failed，提交许可后重试 Passed，见 `build-preflight.json`。依赖版本、锁文件和产品源码未变，未下载、安装或升级依赖。

## 受限残留继续核对（2026-10-22）

用户授权继续处理原 42 个对象；重试均可读取，未修改 ACL、取得所有权或强制删除。详细结果、准确路径和可选只读核验命令在同批 `retained-followup/README.md`，逐项结论以 `result.json` 为准，原受限记录不覆盖。

| 范围 | 状态与实际结果 |
| --- | --- |
| 30 个目录与 6 个文件 | Passed：20 个工程 Dataset 目录随 9 组工程补齐到 validation，10 个有用 worker 缓存目录迁入 `.tmp/cache/blender-jobs/`；5 个 portable 工程归档保留，1 个 wheel 与 modules 锁定副本相同后去重 |
| 5 个恢复目录 | Passed：155 个文件完整可读并核对摘要，继续原位保护；没有按缓存删除 |
| 文件与科学完整性 | Passed：842 文件迁移、1 文件去重，843 个旧位置移除；35 个 Dataset、1,591 个数组及 VDB 摘要、5 个归档 CRC 和 9 组相对绑定静态检查通过。映射 `mapping.json`，删除收据 `removed.jsonl.gz` |
| junction 与空目录 | Passed：核对目标及相关进程后只解除确切 junction，再逐个正常移除空目录；总计 278 个空目录，零数据文件删除、零错误 |
| 原工程与未完成项 | Passed：未知 `outputs/1.blend` 摘要不变，当前 P01 进程未被关闭、重启或修改；无权限或迁移阻塞，无需手动处理命令 |
| 本轮 Blender 冷读/构建/全量回归/人工验收 | Not Run：原字节、相对绑定及环境未变，复用初轮代表性迁移冷读证据；本轮补充实际科学加载及全量文件比对，不扩大产品验收结论 |

移除旧位置字节 51,628,981，包含迁移原件，不能作为净空间收益；真正去重 wheel 为 107,320 字节。磁盘可用空间采样及非隔离观测限制见 `result.json`。本轮仅更新本地文件与现有路由；按用户追加授权提交本地 Git，不推送，教程优化另行提交。
