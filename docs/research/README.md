# 研究资料索引

本目录保存来源核对、格式语义、设计取舍和固定日期的审查。每篇结论以文内日期、软件版本和样本为边界；当前实现与限制见 [VALIDATION](../VALIDATION.md)，候选实际验证见[验收索引](../../validation/agent/acceptance/README.md)。参考原件沿用文内 `submodules/<软件名>/` 等来源路径及摘要。

## 输入与科学语义

- [Gaussian 输入与数值边界](gaussian-inputs.md)：2026-09-22 设计研究，保留当时的分期建议。
- [Gaussian 方法特定能量](gaussian-energy-semantics.md)：原始输出标签、能量类别与来源约束。
- [Gaussian 日志实现依据](gaussian-log-implementation.md)：计算段、性质和结构的关联方式。

## 数值后端、打包与发布

- [M0 后端可行性](m0-backend-feasibility.md)：固定环境下的后端调查与实验。
- [Blender 扩展打包研究](blender-extension-packaging.md)：2026-09-22 的依赖候选与运行边界；现行步骤见[开发说明](../DEVELOPMENT.md)。
- [随包许可证审查](bundled-license-audit.md)：组件、来源和许可范围。
- [GitHub 发布流程](github-release-workflow.md)：CI、候选资格与发布门禁。

## 参考软件与设计取舍

- [用户资料与设计依据](source-review.md)：2026-09-22 的材料阅读和需求快照；其中“剩余工作”属于当时阶段。
- [源码采用依据](source-adoption.md)、[可视化采用路线](visualization-adoption-plan.md)：参考实现和具体取舍。
- [MolStudio 对照](gxnu-molstudio-comparison.md)：功能与工作流比较。
- [VMD 参数](vmd-parameters.md)、[MolecularNodes 参数](molecularnodes-parameters.md)、[Multiwfn 参数](multiwfn-parameters.md)：原软件依据和 QCBlender 的适用边界，技术执行结果在[验收索引](../../validation/agent/acceptance/README.md)。

## 真实样本与固定日期审查

- [C07–C09 样本来源](sop-real-sources-c07-c09.md)、[C10–C13 样本来源](sop-real-sources-c10-c13.md)：真实输入、计算条件和来源限制。
- [2026-10-03 完成度审查](qcblender-completion-audit-2026-10-03.md)：该源码基线下的覆盖与缺陷；后续修复按[验收索引](../../validation/agent/acceptance/README.md)追踪。

`docs/GPT-Web-Chat/` 与 `docs/sobereva/` 是本机既有忽略资料，当前不作为可分发文档入口；所采用的内容、原路径和摘要由[资料阅读记录](source-review.md)说明。
