# [P1] 删除已证实的死代码与冗余实现，保持接口和工程兼容

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 01

## 目标

只处理任务 01 清单中已经证明不再需要的实现。候选清单不是删除授权的自动展开；证据不完整的项保留并解释。遵守 [总规格](../spec.md)。

## 重点核查范围

`qcblender/` 与 `qcblender/blender/` 中的未使用导入、私有函数、不可达分支、被替代的构造流程和常量；`tools/` 中真正过时的脚本/重复验证入口；与被删代码仅有机械关联的测试和文档引用。

`verify_*`、`probe_*`、`build_*`、`prepare_*` 可能是有意保留的 CLI、独立验证或重建路径，不能因不被插件 import 就删除。空包入口、旧工程兼容路径、显式拒绝不支持输入的分支同样不是天然死代码。

## 必须检查的动态和兼容入口

- [qcblender/auto_load.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/auto_load.py)：动态模块导入、Blender 类发现、RNA 依赖顺序。
- [qcblender/__init__.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/__init__.py)：注册/注销、hooks、timer、菜单和对象属性。
- 节点组/资产的持久标识、socket identifier、Operator ID、worker 动作字符串，以及旧 `.blend/.qcdata` 中仍可能存在的引用。
- `views.atom_selection()` 在 [qcblender/blender/assets.py](https://github.com/psiQAQ/QCBlender/blob/1b87751616ecb03d89f6a8c0e96cac99544b420a/qcblender/blender/assets.py) 中仍有调用，不能根据单个文件内没有调用就删除。

## 执行清单

- [x] 对每个拟删除符号复核全仓引用及动态/外部入口；记录“确定不存在”与“当前未发现”的区别。
- [x] 先补必要的行为保护测试，再按小批次删除确认无用的导入、实现、分支或工具。
- [x] 删除过时工具前确认其用途已有等价验证覆盖，或其验证对象确实已不存在；同步重建步骤和调用入口。
- [x] 同步更新残留 import、字符串引用、文档和构建清单，不留下只用于被删实现的孤立封装。
- [x] 对必须保留的诊断、安全或兼容代码在清单中写理由；不要到源码里批量添加“这段不能删”的噪声注释。
- [x] 准确报告文件/行数变化，仅作审计数据，不作为成功目标。

## 不做

不删除产品能力来让代码变短；不改变数据格式或标识；不顺便改目录架构；不清理用户资产、科学样本、源码子模块或共享环境；不删掉失败测试或增加 skip 来制造通过。新发现的行为缺陷另记任务，不混入本 PR。

## 验收

- [x] 每个实际删除项都能回链任务 01 的证据与验证。
- [x] 保留入口和公共契约的签名/标识未变化，原有功能和错误行为未改变。
- [x] 相关科学及非科学测试无新增回归。
- [x] 涉及 Blender 入口时，通过干净安装、注册/注销、相关 UI/操作、保存/冷重开检查。
- [x] 无验证环境时记录 Not Run 并保留阻塞；不关闭需要该验证的删除项。
- [x] 清单同步更新为已删除或保留，并附提交及验证结果。

## Comments

尚未执行；本任务不预先宣称仓库中某个具体函数已经被证实为死代码。

- 2026-09-30：01 已 resolved，领取本任务，仅删除清单 D01–D05 的未使用导入。所有工具、注册类、诊断/兼容分支保留。

- 2026-09-30：D01–D05 完成，5 个文件 `+2/-5`，净减 3 行。首次验证归档解压受路径长度限制；同一候选改用 `outputs/rc02/` 后安装、保存及冷重开通过。临时快照比较器首次把 tuple 与 JSON list 比较造成误报，改为两份 JSON 对照后内容相同；失败日志均保留。未修复范围外的历史工具行为。03 可领取。

## Answer

[清理清单](inventory.md) D01–D05 均已删除；其余候选保留。五份文件的非导入 AST、原编码/BOM/换行不变（`phase02/import-edits.json`）。公共函数、Operator ID、资产与字段没有修改。工具中的三项仅删除无副作用的 stdlib 导入，完整 GUI/标量专项未重跑，不能从编译结果推导其 GUI Passed。

验证证据均以 `outputs/repository-cleanup/phase02/` 为前缀：

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 科学 / 非科学 | Passed，69/69、11/11，0 skipped | `science.json`、`unit.json`，数值指标与 baseline 一致 |
| 十组节点快照 / 实际选择 | Passed，与 baseline 完全相同 | `nodes.json`、`snapshot-r2.log` |
| 新包构建 / 离线安装 / 注册注销 / 求值取消缓存 | Passed | `build.log`、`install-short.log`、`extension.json` |
| 保存、原地与中文目录冷重开 | Passed | `cold-original.log`、`cold-moved.log`；工程 `outputs/rc02/` |
| 缓存恢复 / 电荷偶极 / 振动 | Passed | `recovery.json`、`recovery.log` |
| 源码、安装副本、ZIP / wheel 摘要 | Passed | `qualification.json`、`evidence-index.json`、`source-hashes.json` |
| 独立人工验收 / 完整历史 GUI 专项 | Not Run | 此次技术检查不代替人工或全部历史矩阵 |

候选 SHA-256：`530e2770760292cb9981464908d65cbb8961dace7ab5eea66a75d52cf95cf50a`。源码清单摘要：`a611e634801109cfb8b181d435bef9943f51bf5e82c52281bb7553e7b031be5a`。基于 `1b877516` 未提交工作树；未获提交授权。日志、新候选和测试工程保留，无用户资产清理。
