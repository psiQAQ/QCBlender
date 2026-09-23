# 03 v1.0.0 发布机制

Status: ready-for-agent
Type: task
Execution: pending
Blocked by: 02

## 工作

人工验收全部通过后，以 `git@github.com:psiQAQ/QCBlender.git` 为目标建立发布机制。仅声明 Windows x64 / Blender 5.1.1；比较 MolecularNodes 的标签构建、GitHub Release、扩展平台上传顺序与 `D:/workspace/ChemBlender_2_x/.github` 的标签/摘要门禁。

1. 在干净 Windows runner 按锁文件取依赖和复建 ZIP。现有 `tools/build_science_backend.py` 不得改写受跟踪的 `science-sources.lock.json`；`tools/qualify_package.py` 从 manifest 读版本，只用本次 CI 的证据。
2. 校验 `v1.0.0` 标签与 manifest、源码锁、wheel 摘要、离线安装、许可材料、科学回归和包摘要；任一失败停止。
3. 标签工作流只创建附 ZIP 和 SHA-256 的 **草稿** GitHub Release。使用者安装这份确切 ZIP、复核关键案例并明确批准后，才公开 Release。
4. 首次 Blender Extensions 上架由 Blender ID 人工上传并等待审核。已有条目后，仅在 GitHub Release `published` 事件中经受保护环境和密钥上传同一份已核验 ZIP；区分上传失败、等待审核与已上架。

## 验收

本地工作流、构建脚本和门禁经干净环境验证；无用户公开发布批准时不推送标签、不公开 Release、不上传平台。接口依据：[Blender 扩展安装与上传](https://docs.blender.org/manual/en/5.1/advanced/extensions/getting_started.html)、[Blender CI/CD](https://developer.blender.org/docs/features/extensions/ci_cd/)、[GitHub deployment environments](https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments)。

## Comments

2026-09-23：前置 02 为 `Not Run`，本任务未领取；当前仓库尚无 `.github` 发布工作流，也未配置 remote。
