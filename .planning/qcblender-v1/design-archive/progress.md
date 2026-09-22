# Progress

## 2026-09-22

- 用户选择先做首版范围、架构与路线设计，再实施。
- 已检查 Git 状态、MolecularNodes README/pyproject/LICENSE，保留既有索引状态。
- 已尝试打开引用对话；工具不支持该 URI，正文尚缺。
- 已启动 research 技能要求的 Gaussian 官方资料研究；主任务继续节点架构与现有代码研究。
- 当前目标分类：progress，已获得改变设计约束的实际源码证据。
- 已实测 Blender 5.1.1 节点类型与 OpenVDB 模块存在；已核对 ChemBlender 当前 HEAD 与能力矩阵。
- 已阅读 VMD Orbital、VESTA 功能文档，正在收敛基于具体科研工作流的首版范围。
- 已完成 README、首版设计与 Gaussian 输入研究，进入文档一致性和路径检查。
- 已编写并实际运行 tools/probe_volume_nodes.py；最终运行 Passed、exit 0，无 OpenVDB 引用泄漏诊断。测试 VDB 已清理，结果 JSON 留在被忽略的 outputs/volume-probe/。
- 已新增 .gitignore，仅忽略本任务输出目录与 Python 字节码。
- 检查时 .gitignore 已另有 .agents/skills/ 规则，保留该规则并补齐末尾换行。
- 设计最终采用既有 cbq_core 科学模型和 CBQ 持久化，以普通适配接入 QCBlender 的节点与结果工作流。
- 文档与脚本 UTF-8/末尾换行/空白检查 Passed，12 个本地 Markdown 链接存在；子模块工作树无修改，既有暂存项保持不变。
- 设计阶段已交付，完整目标仍 active：引用对话正文未核对，插件实施和全部产品验收仍待完成。
- 插件实现、安装验证、真实数据验收：Not Run。

## 2026-09-22 单插件设计细化

- 用户明确修正架构：单 Blender 扩展，内置通用 QC 数据转换；cbq_core 仅参考；必需依赖以 wheels 打包。
- 已读取 setup-matt-pocock-skills：仓库无 remote，无根 AGENTS.md/CLAUDE.md，triage 已安装，按 single-context 配置；任务跟踪偏好已发问。
- 已定位用户提供的四份 GPT 对话文稿与 sobereva 文章，均在既有忽略目录；不修改这些来源。
- 已读能量文章，启动 research 技能要求的两个独立研究：方法特定能量语义、Blender 扩展 wheels/内置执行环境。
- 已完整读取四份对话资料；已询问内置波函数求值是否属于首版，以及是否采用较集中的物理量展示范围。架构按单插件约束先行细化，其它未决项保持显式待确认。
- 用户已确认首版内置波函数求值；覆盖 MO、电子/自旋密度、ESP、原子电荷、偶极、振动/IR。优化/IRC、差分、WFN/WFX 和高级分析后续。
- 用户已确认非周期实值 HF/DFT（含开壳层/常见基组），更广方法能量保留并区分；首发 Windows x64 + Blender 5.1.1。
- 两份 research 结果已完成并审阅：方法特定能量语义、随扩展 wheels 打包。GBasis 0.1.0 Windows 的 NumPy<2 与宿主 NumPy2.3.4 冲突，M0 须资格验证兼容固定源码构建。
- 已扩展并运行体数据实验：第二斜轴场的三线性采样 Passed，最大绝对误差 1.79e-6；真实科学输入及完整安装仍 Not Run。
- 用户已审阅并批准 outputs/agent-setup-draft.md，选择 AGENTS.md。已写入根入口与 docs/agents/ 三份配置，采用本地 Markdown、默认五标签、single-context；已建立领域词汇表与单插件 ADR。
- 详细设计一致性检查完成：18 个文档/脚本的编码、末尾换行、空白及语法检查 Passed，39 个本地链接存在，4 份技能配置逐字匹配批准草案，5 份来源 SHA-256 未改变。
- git diff --check 与 git diff --cached --check 均 exit 0；MolecularNodes 保持浅克隆且工作树无修改；索引仍只有既有 .gitmodules 和 gitlink，没有提交或推送。
- 本次未安装依赖。已确认的 GBasis 发布版依赖组合 Failed；兼容源码构建、真实 QC 输入/求值、扩展安装及产品 UI/渲染均 Not Run。M0–M5 是实施路线，不计作已完成功能。
