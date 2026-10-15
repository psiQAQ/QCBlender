# 技术验收索引

当前安装候选由 [current-install.json](../current-install.json) 定位，执行步骤见 [Agent 校验](../README.md)，支持范围见 [VALIDATION](../../../docs/VALIDATION.md)。本目录记录具名候选的结果；各报告的 Passed / Failed / Not Run 只属于其源码、安装包和输入。

## 持续使用的方法与登记

当前专题：[Sidebar 摘要与整数标注输入](sidebar.md)（2026-10-16）；上一批见[标注几何、材质与面板提示验收](annotations.md)，历史双语实现见 [i18n](i18n.md)。

| 内容 | 入口 |
| --- | --- |
| 已确认 GUI 操作及复用条件 | [操作登记表](blender-operations.json)、[交互规则](../../../docs/agents/blender-interaction.md) |
| 固定视觉与性能基准方法 | [基准说明](visual-performance-baselines.md) |
| 历史生成物清理边界 | [清理记录](storage-cleanup.md)；现存位置见 [ARTIFACTS](../../../docs/ARTIFACTS.md) |

## 历史路径与当前位置

历史机器记录和冻结清单保留原始字节、候选身份及当时的路径。读取其中的材料时，先按下表换算仓库相对路径，再核对原记录的 SHA-256；操作登记表中的截图同样适用。路径迁移不改变原有 Passed / Failed / Not Run。

| 记录中的路径前缀 | 当前路径前缀 |
| --- | --- |
| `docs/acceptance/` | `validation/agent/acceptance/` |
| `docs/v1-acceptance/` | `validation/agent/v1-acceptance/` |

上述映射只改变位置。其他历史 `outputs/` 产物的保留或退役状态由 [ARTIFACTS](../../../docs/ARTIFACTS.md) 定位。当前工具直接读取新路径；发布验证器也能读取迁移前标签内的旧布局。

## 候选和专题记录

当前候选：[主干维护、色带与构型身份](upstream-20261011.md)、[机器索引](upstream-20261011.json)。上一批：[空场景按钮与编号范围](ui-bounds.md)、[空场景属性入口](empty-properties.md)。

| 批次或主题 | 说明与机器记录 |
| --- | --- |
| 教程截图与案例命名 | [当前截图要求、命名与保全](tutorial-screenshots-20261011.md) |
| 教程素材与工作目录 | [文件布局、图片门禁及保全](tutorial-assets-20261011.md) |
| Alpha 科学预检、摘要与保存 | [验证说明](alpha-readiness-validation.md)、[索引](alpha-readiness-validation.json)、[交付](alpha-readiness-delivery.json) |
| GitHub Actions 下载与资格 | [下载修复](actions-download-fix.md) |
| 当前构型关联与共享 mesh | [P1 验证](audit-p1-validation.md)、[索引](audit-p1-validation.json)、[交付](audit-p1-delivery.json) |
| Gaussian 拼接任务、重复 ETS-NOCV 与基准 | [P2 验证](audit-p2-baselines-validation.md)、[索引](audit-p2-baselines-validation.json)、[交付](audit-p2-delivery.json) |
| 静态参考、IGMH、取消与原生 VDB | [可靠性验证](reliability-validation.md)、[索引](reliability-validation.json)、[交付](reliability-delivery.json) |
| 展示精度、XYZ 与 CSV | [验证索引](display-xyz-export-validation.json)、[清理收据](display-xyz-export-cleanup.json) |
| 公开教程和样本身份 | [教程验证](tutorial-validation.json)、[GUI 记录](tutorial-cu-validation.json)、[样本交付](tutorial-sample-delivery.json)、[最终资格](tutorial-final-qualification.json) |
| 早期源码借鉴与 VMD 参数 | [源码借鉴](source-adoption.md)、[VMD 参数](vmd-parameters.md) |
| 早期清理验证 | [机器记录](cleanup-validation.json) |

## 早期专项验收全文

以下四份报告从 docs 根目录归入 `history/`，文件名保持不变。旧任务记录中的根目录路径对应下列位置；原日期、参数、候选摘要和验收结论保留。

| 原 docs 根目录文件 | 当前位置 |
| --- | --- |
| `RESULT_BROWSER.md` | [结果浏览](history/RESULT_BROWSER.md) |
| `OPTIMIZATION_TRAJECTORY.md` | [Gaussian 优化轨迹](history/OPTIMIZATION_TRAJECTORY.md) |
| `MOLECULARNODES_PARAMETERS.md` | [MolecularNodes 参数交互](history/MOLECULARNODES_PARAMETERS.md) |
| `MULTIWFN_PARAMETERS.md` | [Multiwfn 参数与界面](history/MULTIWFN_PARAMETERS.md) |

原始报告或工程退役后的可用性从 [ARTIFACTS](../../../docs/ARTIFACTS.md) 查找，历史批次摘要见 [outputs 索引](../../../docs/archive/outputs-history/README.md)。技术验证不替代独立人工或科研签署。
