# 产物查找入口

任务的状态保存在 `.scratch/`，验证结论由对应报告负责；本页只路由现存证据、候选、工程、重建方法和清理阻塞。更新本页不改变历史报告或独立人工签署。

## 目录与生命周期

- `outputs/evidence/<日期>/<任务>/`：必要日志、报告、生成脚本、来源、摘要、清理收据及被索引引用的必要截图。
- `outputs/projects/<工程标识>/`：用户工程及完整配套 `.qcdata`，不按任务完成状态删除。
- `outputs/candidates/current/`：最新待验收 ZIP；替换前记录源码、摘要、资格及旧候选可用性。
- `outputs/runs/<任务>/<批次>/`：任务期间临时工程、隔离环境和缓存；任务结束并保全后清理。
- 共用 `outputs/build-site`、`outputs/science`、`outputs/wheels` 及必要源码/许可证维持工具现有路径。真实输入使用 `tests/data/local-inputs.json` 和 `docs/v1-acceptance/SOURCES.md`；参考原件保留原资料目录。

## 本地证据

本轮迁移和核对完成后填写任务路由；迁移原始报告不改字节，通过旧路径映射查找。
