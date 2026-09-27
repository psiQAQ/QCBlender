# 源码借鉴与逐批技术验收

Status: resolved

用户于 2026-09-27 确认四项范围，集成分支为 `main`；先将当前功能分支合回主分支，再建立工作树。基础功能提交 `685a0b3`，包含已技术验证的 Gaussian 优化轨迹；三个既有候选保持原摘要和证据。

## 目标与分工

1. [A AIM 关联校验](issues/01-aim.md)。
2. [B ETS-NOCV 能量状态](issues/02-nocv.md)。
3. [C 正交取景相机](issues/03-camera.md)。
4. [D 场值线剖面与 CSV](issues/04-profile.md)。

第一波三个 GPT-6 sol / high 代理分别使用 `.worktrees/adopt-aim`、`adopt-nocv`、`adopt-camera`，分支为 `feat/adopt-aim`、`feat/adopt-nocv`、`feat/adopt-camera`。A 集成通过后在 `.worktrees/adopt-profile`、`feat/adopt-profile` 启动 D。主代理依次按 A、B、C、D 合并；公共 UI、总文档、候选和验收由主代理负责。

子代理仅在各自工作树开发和提交；参考源码、现有样本和科学库从主目录只读访问。子代理不启动 Blender、不导入 bpy、不调用 MCP，只运行 Python 数学/解析测试和静态检查。临时文件放各自忽略的 outputs。Blender 行为在主代理执行前保持 Not Run。

## 验收循环

主代理审查分支并普通合并，每批执行科学回归、独立 ZIP 构建和干净配置安装、相关 GUI/MCP 与 SOP、渲染、保存和移动冷重开。错误先修复和复验，通过前不合并下一批。每批证据绑定源码提交、ZIP SHA-256 和安装副本，输出在 `outputs/source-adoption/<批次>/`。

通过后提交技术记录并创建本地附注标签 `qa/source-adoption-20260927-01` 至 `04`。D 的标签还要求最终候选 C01–C13 六栏、N01–N18 全部技术 Passed。旧证据不转记为新候选通过；任何未执行项标 Not Run。

开发版本保持 0.0.1；不新增依赖、不推送、不发布。完成后保全工作树证据并归档工作树，保留分支与标签。人工验收和外部视觉对照后置，不代签。

## 范围与变更

本轮仅新增正交取景和既有场的离散线采样。ORCA、.mwfn、周期体系、新分析算法、透视取景、表面碎片过滤不纳入。普通缺陷自主修复；新增依赖、科学语义歧义、许可影响、范围变化或用户现有工程风险先反馈具体证据和选项，仅暂停受影响工作。

源码参考及许可见 [研究记录](../../docs/research/source-adoption.md)，执行状态见 [进度](progress.md)。
