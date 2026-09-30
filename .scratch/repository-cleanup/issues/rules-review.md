# 项目规则逐条核验

2026-09-30；范围只含根 AGENTS 和四份 `docs/agents/`。继承的用户全局规则不在修改范围。下列“保留”条款均在正文旁附具体理由；表中依据为当前代码、目录、任务或实际风险。没有根据 Python 调用次数删掉规范。

## 根 AGENTS

| 位置 / 要求 | 当前依据与适用条件 | 处置 / 理由 |
| --- | --- | --- |
| Issue tracker：读本地任务规则 | `.scratch/` 54 份既有记录，本轮任务存在真实 Blocked by | 保留；执行状态只有一个来源 |
| Triage：五标签 | `triage-labels.md`、人工任务仍 pending | 澄清只用于分派；Status 表示执行进度 |
| Domain：先读词汇和 ADR | CONTEXT 与 accepted ADR 0001 已存在 | 保留；物理量与架构有已确认约束 |
| 参考原件目录与忽略 | `.gitignore` 对 Multiwfn 等原件目录单独忽略 | 保留；原件许可/体积与文字结论不同 |
| 来源 URL/版本/日期/章节/摘要 | `docs/research/sop-real-sources-*.md` 和样本来源索引 | 保留；固定结论对应版本 |
| 结论与索引放 research | 已有 15 份研究文档 | 保留；目录提供稳定证据入口，去除重复忽略要求 |
| 保留 gitlink，仅忽略附件 | `.gitmodules` 和三个索引 mode 160000 条目 | 保留；忽略下载不等于移除参考源码版本 |
| 阶段产物 | storage-maintenance、CHANGELOG、prune_outputs | 合并为权威规则链接；具体清理条件不在根重复维护 |

## 任务跟踪

| 位置 / 要求 | 当前依据与适用条件 | 处置 / 理由 |
| --- | --- | --- |
| 开头：本地任务 / 不远端发布 | issue-tracker 与本轮未发布任务稿 | 合并重复“技能发布到本地”句；技能不提供外部写入授权 |
| 主题目录、spec、issues 编号 | 现有 `.scratch/*/issues/` | 合并相邻两条；保留定位约定 |
| Triage 字段 | 现有 ready-for-agent / ready-for-human | 保留；角色与进度分开 |
| Status 三态、Execution 映射 | 本轮按 claimed → resolved 推进 | 保留；下游只认已验收前置 |
| Comments 追加讨论证据 | 既有技术复验与人工未签署记录 | 保留；不覆写决策依据 |
| 读取路径 / 目录内编号 | 多主题都含 01 | 保留；编号不是全仓唯一 |
| wayfinder 地图 / Type / Blocked by | 主仓库有 wayfinder 技能；有疑问时适用 | 保留；地图只做索引 |
| 前置 resolved、领取 claimed、Answer | 任务 01→06 明确依赖 | 保留；地图仅在已有时更新，不凭流程另建 |
| spec 验收条件 / to-tickets | 主仓库技能存在，任务规格已拆分 | 保留；明确规格先于实施 |
| 有疑问才 research/grilling/prototype | 锁文件和主仓库对应技能目录可读 | 保留条件；明确任务不用额外计划 |
| research / domain / defects 分别存放 | research、CONTEXT、ADR、DEVELOPMENT_PITFALLS 和任务目录 | 保留；不同资料有各自权威位置 |
| code-review / Passed Failed Not Run | 主仓库 code-review SKILL 可读；本轮真实报告 | 保留；补充宿主可用性说明，锁文件不保证安装 |
| 技术结果 / 人工签署 / 发布前置 | `.scratch/v1-acceptance/issues/02-human-acceptance.md` 和 03 | 保留；Agent 不代签 |
| handoff 到 outputs，仅放指针 | 主仓库 handoff 技能与既有 outputs/handoffs | 保留；临时交接不复制长期状态 |
| implement-spec 授权 | 主仓库技能可读；本轮未要求提交 | 保留；技能不授权 commit / PR |
| 不创建 .planning / 历史非现行授权 | archive README + `.scratch` 当前任务 | 保留；避免过期状态恢复 |

## Triage 与领域

| 位置 / 要求 | 当前依据与适用条件 | 处置 / 理由 |
| --- | --- | --- |
| needs-triage | 范围尚未评估时 | 保留；维护者先确定任务边界 |
| needs-info | 缺少会影响结果的输入时 | 保留；标明等待资料 |
| ready-for-agent | 明确规格的实施任务 | 保留；已有可执行边界 |
| ready-for-human | 独立人工验收任务 | 保留；自动化不能代办 |
| wontfix | 有明确不实施决定时 | 保留；防止重复领取 |
| canonical role 同名 / Status 分离 | 任务顶部字段 | 保留；名称映射不混入进度 |
| 不创建远端标签 | 无标签发布授权 | 保留；本地分类不产生外部写入 |
| Domain：读取 CONTEXT / ADR | 现有词汇表和 ADR 0001 | 保留；先理解定义与单扩展约束 |
| 文件不存在时继续 / 初始化 | CONTEXT 和 ADR 自设计阶段已建立 | 删除启动期分支，改为维护既有位置；domain-modeling 保留用于新定义 |
| 定义与实施细节分离 | CONTEXT 与 specs / QCBLENDER_V1_DESIGN | 保留；词义不随代码结构改变 |
| 使用词汇、说明歧义 | 轨道相位、电荷、电子密度等定义 | 保留；避免科学量混淆 |
| 冲突引用 ADR、先取得决定 | accepted ADR 0001 | 保留；局部清理不能推翻产品交付边界 |

## 存储维护

| 位置 / 要求 | 当前依据与适用条件 | 处置 / 理由 |
| --- | --- | --- |
| 保存→输入→日志→删除 | `blender/project.py` 与已完成 storage-cleanup 任务 | 保留；解除引用后才删除 |
| 只覆盖批准类别 / 新类别另确认 | 用户工程、依赖及未知项是独立授权对象 | 保留；移除政策生效日期叙事，CHANGELOG 已记录历史 |
| 顺序1：状态/PID/独立便携保存 | `save_project`；仅存在需保全会话时 | 收敛条件；无会话不凭空创建保全工程 |
| 顺序2：冷重开/失败保留/关闭准确 PID | 保存可能遗漏外部数据，进程不能按名字混同 | 保留；失败时不销毁恢复机会 |
| 顺序3：小样本/大型输入/摘要/索引/CSV | `local_inputs.py`、104 项索引、SOURCES | 保留；路径迁移与科学字节身份分离 |
| 顺序4：更新入口/缺输入失败/重建/相关检查 | prepare_sop_fixture、科学测试与 Blender 验证 | 保留；缺 fixture 不转换为跳过 |
| 顺序5：逐文件计划/无引用/链接未知项跳过 | `prune_outputs.py` 的扫描、分类及路径检查 | 保留；路径名不证明用途或边界 |
| 顺序6：按计划删/保留日志/保护复验/空间口径 | prune apply、受保护摘要和历史清理报告 | 保留；证明没有扩大删除范围 |
| 类别：用户工程 / 可重建展示 | 存储保护前缀 recovery | 保留；用户指定资产不属于历史副本 |
| 类别：运行环境 / 重复候选 wheel | shared extension wheels、dependencies lock | 保留；字节重复与共享环境必须区分 |
| 类别：原始输入 / 已迁移副本 | local-inputs、CSV 成套关联 | 保留；只能删除核对后的旧副本 |
| 类别：来源 Git / 无引用缓存 | 三个 gitlink、Git 标签、worker jobs | 保留；不可重建的追溯信息与缓存不同 |
| 类别：日志 / 已结束会话临时文件 | 验收/删除报告与恢复文件的用途 | 保留；未知恢复文件不自动删 |
| 不按扩展名删除 | Gaussian .log、节点库/偏好 .blend | 保留；后缀无法判定数据用途 |
| 环境只清缓存、不改依赖 | Blender 多扩展共享依赖 | 保留；不破坏安装环境 |
| 日志原位 / 路径映射 | 文档与任务对产物位置的引用 | 保留；迁移后仍能定位 |
| 不改 ACL/所有权/全库回收 | 权限与历史对象是独立边界 | 保留；本轮失败也按此处理 |
| plan/apply 前置验证与审查 | CLI `--help` 实测与代码审查 | 保留；分类工具不能代替保全和授权 |
| 新 report-dir 保留旧收据 | 当前 CLI 支持 `--report-dir` | 补出真实参数；不能覆盖删除证据 |
| 历史 Passed / 二进制可用性 | storage-cleanup 已清历史制品 | 保留；不把旧结果转为新验证 |
| 重建记录提交、ZIP 摘要、新检查 | build_extension / qualify_package 当前实跑 | 保留；新包独立绑定证据 |
| CHANGELOG 记录阶段与保留 | 现有 CHANGELOG | 保留；历史集中、当前手册不写流水账 |
| 人工验收 / 外部视觉对照独立 | 人工任务 pending，签名空白 | 保留；Agent 技术结论不提供人类认可 |

## 验证

- **Passed**：5 份规则、11 个本地 Markdown 链接，0 错误；`outputs/repository-cleanup/rules-links.json`。
- **Passed**：`python tools/prune_outputs.py --help`，确认 `--plan / --apply / --report-dir`；本轮未执行 plan/apply。
- **Passed**：普通 diff 复核；保留条款逐条附理由，原件/许可、科学校验、用户工程、人工签署和外部授权没有放宽。
- **Passed**：当前宿主可读主仓库的被引用技能目录；锁文件未改，未安装技能。
- **Not Run**：磁盘清理 apply、远端标签/Issue 发布、独立人工验收；均不属于本轮规则清理操作。
