# QCBlender 首版设计与交付计划

## Goal

开发以几何节点为主要控制方式的 Blender 量子化学/计算化学可视化插件。首版面向 Gaussian 各类输出，后续支持 ORCA；以可验证的具体工作流评估替代 VMD/VESTA 的效果。用户于 2026-09-22 选择先完成首版范围、架构和开发路线设计，再据此实施。

## Phases

1. 核对仓库、参考项目、格式与工具的一手证据；明确引用对话的访问缺口。**Status:** complete
2. 编写首版范围、数据与节点架构、输入支持矩阵及验收标准。**Status:** complete
3. 制定依赖决策、开发顺序、风险验证与可执行交付路线。**Status:** complete
4. 检查设计一致性、来源与路径，交付可审阅设计。**Status:** complete
5. 按单 Blender 插件约束，读取用户补充资料、细化科学/节点/打包设计并确认边界。**Status:** complete
6. 配置 setup-matt-pocock-skills 的任务跟踪、标签及领域文档规则。**Status:** complete
7. 依据确认后的设计实施插件，完成真实文件、Blender 行为、安装与视觉验收。**Status:** pending

## Constraints

- 本阶段先完成设计；不安装依赖、不修改参考子模块、不提交或推送。
- 用户新要求：单个 Blender 插件内完成通用量子化学数据转换；cbq_core 仅代码/思想参考，无外部 Python 包或环境安装要求；必需依赖优先以 wheels 随扩展打包。
- 当前仓库无首个 commit；已有暂存的 .gitmodules 与 MolecularNodes gitlink，以及未跟踪的 .agents/ 和 skills-lock.json，予以保留。
- 不把解析支持、数值正确性、Blender 可用性和人工认可合并为一个完成标志。
- 现有 docs/GPT-Web-Chat/20260922-{1,2,3,4}.md 和 docs/sobereva/ 能量文章作为用户提供材料；这些目录已被忽略，保持原样。

## Next Step

详细设计与技能配置已交付。实施从 M0 开始：固定真实样例和依赖闭包，验证兼容后端构建、Blender 自带运行时与离线安装，再进入数据/节点开发。

## Errors Encountered

| 情况 | 处理 |
| --- | --- |
| git log 提示 main 尚无 commit | 使用工作树和索引作为当前事实来源 |
| web 无法打开 chatgpt-conversation:// URI，当前无会话读取工具 | 记录信息缺口，依据用户当前明确目标继续共同前置研究 |
| density/io.py 不存在 | 已用 rg --files 确认实际实现为 density/grids.py |
| Blender 官方手册部分页面 open 返回 402 | 使用官方搜索结果与本地 5.1.1 Python 类型核对，进一步行为仍需实验 |
| 体数据实验初次退出报告 OpenVDB Transform 引用泄漏 | 各网格独立构建 transform 并在脚本结束释放网格；重跑退出码 0，无泄漏诊断 |
| 内联文档检查被 PowerShell 引号解析拒绝 | 改为 outputs/ 下可审阅脚本执行 |
| 文档检查发现 .gitignore 无末尾换行 | 保留当前所有规则，仅补末尾换行后重新检查 |
| apply_patch 同一请求删除/新增同一路径、以及上下文未含完整行时失败 | 分开删除/新增；按原文完整行重建精确补丁，失败批次核查后再应用 |
| GBasis 自动文档页面不可访问，搜索未返回项目文档 | 改查固定提交的作者源码；不把无关搜索结果作为依据 |
