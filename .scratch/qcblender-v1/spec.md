# QCBlender 首版实施

以 [主设计](../../docs/QCBLENDER_V1_DESIGN.md) 及其数据/节点契约为规格；任务状态只在下列文件维护。Status 为 triage 标签，Execution 为 pending/in_progress/complete，技术完成不代替独立用户认可。

- [M0 科学后端与安装资格验证](issues/01-m0-runtime.md)
- [M1 数据导入与已有场](issues/02-m1-data.md)
- [M2 内置波函数求值](issues/03-m2-evaluation.md)
- [M3 几何节点配方](issues/04-m3-nodes.md)
- [M4 振动、IR 与方法特定能量](issues/05-m4-vibration-energy.md)
- [M5 发布与工程验收](issues/06-m5-release.md)

主 Agent 汇总任务与验收，子 Agent 仅修改各自分配文件。必要依赖在仓库内构建/收集并随扩展分发，用户无外部 Python 环境要求。开发输出放 outputs/，原始用户资料保持忽略。

当前 M0–M4 在声明范围内完成；M5 技术候选已产生，独立复做和发布验收继续保留。产物、支持矩阵和复做入口见 [验收记录](../../docs/VALIDATION.md)。

当前 Git 授权（2026-09-22）：用户要求将已有开发分批提交，后续持续按可验证的逻辑单元创建本地 commit；不执行 push 或远端发布。此授权取代本任务早期的“暂不提交”约束。
