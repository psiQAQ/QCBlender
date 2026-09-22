# 开发任务已迁移

2026-09-23：M7 裁剪、体积曲线和游标采样已实现并通过解析场与实际体积渲染检查；20 项科学回归通过。完整打包/GUI/振动回归仍进行中，见 M7 任务。

2026-09-23：M7 公共节点与常用样式首批真实 Blender 检查通过；阶段证据见 M7 任务。开发问题记录入口为 `docs/DEVELOPMENT_PITFALLS.md`，后续持续追加已复现问题与复验状态。

2026-09-23：已批准 M7 可组合科学场显示，开始节点接口解耦；实施及验收状态统一记录在 `.scratch/qcblender-v1/issues/08-m7-composable-views.md`。

2026-09-23：用户确认的 M6 追加范围技术验收完成：公共等值面/体积雾、显示层管理、独立样式与振动/IR 复制、真实渲染和 GUI 撤销/重做。状态与证据以 `.scratch/qcblender-v1/issues/07-m6-display-layers.md` 为准；独立用户与发布验收归 M5。

复建验收发现并修复 Blender 宿主的 Windows 长路径缓存读取；原失败配置复验和 20 项科学回归通过，最新包摘要与边界见 M5 任务记录。

已有开发已分五批本地提交；17 个已提交样本的 SHA-256 与来源记录一致，当前安装包资格检查 Passed。提交与验收证据见 `.scratch/qcblender-v1/issues/06-m5-release.md`。

最新实施证据写入 `.scratch/qcblender-v1/issues/`：M0–M4 在声明范围内完成，M5 已有技术候选，保留独立用户与发布验收。源码/包摘要和报告汇总见 outputs/qualification.json。后续仍以该处为唯一任务状态。

用户已授权持续进行本地提交，已有开发按逻辑单元分批保存；当前授权见 `.scratch/qcblender-v1/spec.md`。不推送。

当前实施以 [.scratch/qcblender-v1/spec.md](../../.scratch/qcblender-v1/spec.md) 及独立任务为准，本文件不维护第二份任务状态。

用户已授权按设计实施、启动/安装 Blender、下载公开计算样例及随包所需依赖。设计期历史保存在 design-archive/；其中旧阶段限制不适用于已授权实施。
