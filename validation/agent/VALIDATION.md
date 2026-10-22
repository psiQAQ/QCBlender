# 当前校验与历史整合检查

2026-10-23：当前完整候选源码为 `8d2f83f`，由 [current-install.json](current-install.json) 定位；[自动取景与出图验收](acceptance/auto-output.md)记录去重 61 项定向检查、四类真实渲染、GUI、完整构建/隔离安装与冷读 Passed。追加日常配置安装、128 个成员核对、原生自动取景/三档出图及新进程冷读 Passed；按用户要求未备份旧安装。随后日常 GUI 的两种自动取景、两次白底/透明渲染、恢复原设置及副本冷读 Passed，首轮观察脚本失败保留原记录。独立人工/科研、全量回归及远端 CI Not Run。以下记录属于各自历史候选。

2026-10-16：当时安装来自 `annotation-anchor-20261016-r1`，源码 `b02c9fa`，见[圆弧中点/创建朝向验收](acceptance/annotation-anchor.md)。266 标准库、96 公开科学、实际 GUI 创建、原生半角/朝向、渲染、冷读及日常安装/原保存工程恢复 Passed。独立人工/科研接受 Not Run；该批既有教程缺图状态未变。

2026-10-16：上一批安装来自 `sidebar-20261016-r2`，源码 `8e085f0`，见 [current-install.json](current-install.json) 与 [Sidebar/整数输入验收](acceptance/sidebar.md)。266 标准库、94 公开科学、无 IO 摘要、原生几何/上下文、实际 GUI 和安装/渲染/冷读、全局原工程恢复 Passed。非对象 pin 与多视图区原生比较 Not Run，边界单测通过；独立人工/科研接受 Not Run。十份教程已同步，27 处图片引用缺 23 张，完整图片门禁仍 Failed。

2026-10-16 上一批安装来自 `annotations-20261016-r2`，源码 `739c08b`，技术结果见[标注与面板验收](acceptance/annotations.md)。221 项标准库、92 项公开科学、标注几何与生命周期、XYZ/优化/IRC、工具提示语言组合、真实 GUI、安装/渲染/中文路径冷重开及全局原工程恢复 Passed。旧工程对象、科学数组、材质节点和偏好不变；独立人工与科研接受 Not Run。

2026-10-11 历史安装来自 `upstream-7dc0d11`，当批技术结果见[验收](acceptance/upstream-20261011.md)。181 项基础、130 项科学、安装、节点、色带/有效域、多 Cube、原地与移动冷重开及隔离/日常 GUI Passed。用户原有两张截图与 `.blend` 原样保留；人工 SOP 新增的两处截图空位由实际操作者补入，独立用户与科研接受 Not Run。

## 2026-10-06 校验目录整合

以下保留当批检查。该批安装包来自 `alpha-ci-0.1.0-190e11e`，产品树、依赖锁与整理前一致；当前安装已由上面的入口接替。

| 检查 | 状态 | 证据与范围 |
| --- | --- | --- |
| 数据准备 | Passed | [data-preparation.json](reports/2026-10-06/integration/data-preparation.json)：30 个公开输入、111 个本地 key、218 项映射复制 |
| 公开教程独立副本 | Passed | [workspace-after-review.json](reports/2026-10-06/integration/workspace-after-review.json)：13 份 Markdown、112 个链接，文件身份与 P04 相对引用；公开教程 73 步，29 个预定截图空位 |
| 基础测试 | Passed | [stdlib.json](reports/2026-10-06/integration/stdlib.json)：134 项，失败、错误、跳过均为 0 |
| 公开科学测试 | Passed | [public-core.json](reports/2026-10-06/integration/public-core.json)：67 项，失败、错误、跳过均为 0 |
| 完整本地科学测试 | Passed | [full.json](reports/2026-10-06/integration/full.json)：123 项，失败、错误、跳过均为 0 |
| 冻结样本与解析 | Passed | [frozen-samples.json](reports/2026-10-06/integration/frozen-samples.json)、[tutorial-samples.json](reports/2026-10-06/integration/tutorial-samples.json)；冻结包及清单字节保持原样 |
| 安装与工程移动 | Passed | [install.json](reports/2026-10-06/integration/install.json)、[cold-original.json](reports/2026-10-06/integration/cold-original.json)、[cold-moved.json](reports/2026-10-06/integration/cold-moved.json)；独立配置中的真实离线安装、生成、渲染及两个新进程读回 |
| 主流程 MO9、摘要与保存 | Passed | [alpha.json](reports/2026-10-06/integration/alpha.json)：生成、参数摘要、实际渲染、自包含工程及中文路径冷重开 |
| XYZ 与科学 CSV | Passed | [xyz-export-v2.json](reports/2026-10-06/integration/xyz-export-v2.json)：XYZ 帧和标注、各类 CSV、101 点剖面、取消清理及新进程数组读回 |
| 清理工具边界 | Passed | [cleanup-tests.log](reports/2026-10-06/integration/cleanup-tests.log)：4 项 |
| 旧输入及压缩包元数据保全 | Passed | [preservation.json](reports/2026-10-06/cleanup-prepared/preservation.json)：224 个旧输入与集中副本相符，保全 232 条 ZIP 成员记录 |
| 已确认的历史文件清理 | Passed | [receipt.json](reports/2026-10-06/cleanup-apply/receipt.json)：逐文件删除 257 项，合计 1,387,868,294 字节；集中输入、当前候选和保全元数据复核通过 |
| 清理后读取与测试 | Passed | [stdlib-after-cleanup.json](reports/2026-10-06/cleanup-apply/stdlib-after-cleanup.json)：134 项；[science-after-cleanup.json](reports/2026-10-06/cleanup-apply/science-after-cleanup.json)：123 项完整科学测试；失败、错误、跳过均为 0 |
| 历史教程去重与保护 | Passed | [verification.json](reports/2026-10-06/legacy-docs/verification.json)：三个重复转发页移除，423 个保护对象原字节不变，包括 419 张截图；合并前后用户原有修改相同 |
| 本轮 GUI 点击、维护者教程操作与截图 | Not Run | 29 个公开截图和 3 个本机截图由维护者按教程补充 |
| 原始 checkpoint 密度比较 | Not Run | 9 个原件已保留；未在本轮运行 PySCF 复算 |
| 独立科研判断与发布批准 | Not Run | 不由自动检查推导 |

Blender 后台进程逐个运行，启动前检查已有进程，命令收据记录 PID、配置目录、退出码及退出后的进程状态。主流程复用登记项 `alpha-preflight-summary-portable`；已核对完整产品树、依赖锁和记录中的实现摘要。渲染图片由 Agent 查看确认两种相位表面可见；没有替换人工截图。

完整命令与第一次执行记录见 [checks.json](reports/2026-10-06/integration/checks.json)，受影响工具的独立复跑见 [xyz-recheck.json](reports/2026-10-06/integration/xyz-recheck.json)。旧脚本缺少剖面场对象的失败报告仍为 `Failed`，修复记录见 [CHANGELOG](../../docs/CHANGELOG.md)，最终 XYZ 状态以 v2 报告为准。其他未涉及的专题没有在本轮重新执行 GUI。

本地提交、工作树保全与归档状态由 [ARTIFACTS](../../docs/ARTIFACTS.md) 统一路由。已确认清单的删除范围、保留对象与执行结果见 [CLEANUP](CLEANUP.md)。
