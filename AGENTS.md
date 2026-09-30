## Agent skills

### Issue tracker

本仓库的需求、规格和任务采用本地 Markdown；操作任务前读取 [任务跟踪规则](docs/agents/issue-tracker.md)。理由：`.scratch/` 保存依赖、领取状态和验证证据，避免跳过前置任务或维护两套状态。

### Triage labels

分派任务使用默认五种 triage 标签，执行进度另记 `Status`；映射见 [标签规则](docs/agents/triage-labels.md)。理由：需要人工处理的任务仍可能未开始，分派对象与完成状态不能混用。

### Domain docs

采用 single-context；讨论领域术语或架构决策前按 [领域文档规则](docs/agents/domain.md) 读取相关内容。理由：物理量定义和单扩展决策分别由 `CONTEXT.md`、ADR 统一维护。

## 参考资料

- 调研需要保存原始网页、软件手册及附件时，放入 `submodules/<软件名>/`，沿用已有软件目录名称，并将资料目录加入 `.gitignore`。理由：原件体积和再分发许可不同于可审阅的研究文字。
- 保存资料时记录来源 URL、软件版本、获取日期、所用章节或页码及文件 SHA-256。理由：同名手册或网页可能更新，结论需要能定位到确切来源。
- 研究结论和来源索引保存到 `docs/research/`，引用对应的本地资料路径。理由：Git 中保留可审阅的结论和来源定位，原件按本节目录与忽略规则存放。
- 已有 Git 源码子模块继续保持跟踪；其中新增的下载资料仅忽略具体资料路径，不整体忽略 `submodules/` 或已有源码子模块。理由：`.gitmodules` 和 gitlink 固定参考源码版本，不能被资料忽略规则掩盖。

## 阶段产物维护

阶段结束时按 [存储维护规则](docs/agents/storage-maintenance.md) 核对产物保留、清理授权和 CHANGELOG；具体保护、删除及验证要求以该文件为准。理由：用户工程、必要输入和新候选证据有不同生命周期，集中规则可避免按文件名误删。
