# QCBlender 首版实施

以 [主设计](../../docs/QCBLENDER_V1_DESIGN.md) 及其数据/节点契约为规格；任务状态只在下列文件维护。Status 为 triage 标签，Execution 为 pending/in_progress/complete，技术完成不代替独立用户认可。

- [M0 科学后端与安装资格验证](issues/01-m0-runtime.md)
- [M1 数据导入与已有场](issues/02-m1-data.md)
- [M2 内置波函数求值](issues/03-m2-evaluation.md)
- [M3 几何节点配方](issues/04-m3-nodes.md)
- [M4 振动、IR 与方法特定能量](issues/05-m4-vibration-energy.md)
- [M5 发布与工程验收](issues/06-m5-release.md)
- [M6 可组合节点与显示层](issues/07-m6-display-layers.md)
- [M7 可组合科学场显示](issues/08-m7-composable-views.md)

主 Agent 汇总任务与验收，子 Agent 仅修改各自分配文件。必要依赖在仓库内构建/收集并随扩展分发，用户无外部 Python 环境要求。开发输出放 outputs/，原始用户资料保持忽略。

当前 M0–M4、M6 及 M7 在声明范围内技术完成；M5 技术候选已产生，独立复做和发布验收继续保留。产物、支持矩阵和复做入口见 [验收记录](../../docs/VALIDATION.md)。

当前 Git 授权（2026-09-22）：用户要求将已有开发分批提交，后续持续按可验证的逻辑单元创建本地 commit；不执行 push 或远端发布。此授权取代本任务早期的“暂不提交”约束。

2026-09-23 首版范围确认：支持 MO、电子/自旋密度、ESP、原子电荷、偶极、振动位移及其他外部 Cube 标量场；ELF、LOL、RDG/NCI 等新分析量的内置计算后置。首版包含完整显示层管理（增删、复制、排序和多层样式），公共几何节点可自由组合，提供适配物理量的等值面、体积雾和颜色映射。相机与图像/动画导出沿用 Blender 原生流程，自动构图、灯光预设和科研图排版后置。M6 是现有 M3 的追加交付，完成后更新 M5 包与工程验收；此前的技术候选不代表新增范围已完成。后续实质范围分歧须向用户确认。
