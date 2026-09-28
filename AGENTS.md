## Agent skills

### Issue tracker

本仓库的需求、规格和任务采用本地 Markdown；操作任务前读取 [任务跟踪规则](docs/agents/issue-tracker.md)。

### Triage labels

分派或更新任务状态时使用默认五种 triage 标签；映射见 [标签规则](docs/agents/triage-labels.md)。

### Domain docs

采用 single-context；讨论领域术语或架构决策前按 [领域文档规则](docs/agents/domain.md) 读取相关内容。

## 参考资料

- 调研需要保存原始网页、软件手册及附件时，放入 `submodules/<软件名>/`，沿用已有软件目录名称，并将资料目录加入 `.gitignore`。
- 保存资料时记录来源 URL、软件版本、获取日期、所用章节或页码及文件 SHA-256，便于追溯。
- 研究结论和来源索引保存到 `docs/research/`，引用对应的本地资料路径；原始下载资料保持在 Git 忽略范围内。
- 已有 Git 源码子模块继续保持跟踪；其中新增的下载资料仅忽略具体资料路径，不整体忽略 `submodules/` 或已有源码子模块。

## 阶段产物维护

阶段完成后按 [存储维护规则](docs/agents/storage-maintenance.md) 先保全用户工程、集中必要输入、保留日志，再清理用户已批准类别的生成物与缓存。新增类别、依赖环境变更、未知归属及用户工程需单独确认。维护现有 `docs/CHANGELOG.md`，记录阶段验证及产物保留状态；历史 Passed 不代替新候选验证。
