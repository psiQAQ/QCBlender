# 标注默认值与弹窗验收

2026-10-17，Windows x64 / Blender 5.1.1。产品源码 `2bb5f72f813a9f4424cdf5bb01be5ffae47fc7f7`，最终 ZIP 50,940,853 字节，SHA-256 `cd2f8d6c98c949468b74063f25670afb06975594bd385316da7a054c4976c224`。当前候选身份见 [current-install.json](../current-install.json)，汇总见 [acceptance.json](../reports/2026-10-17/annotation-ui/acceptance.json)。

四类新建标注默认字号 0.5，显式字号有效，编辑保留保存值。原子文字默认纯元素符号，自定义前缀后也只追加元素符号；旧文字在编辑确认或构型刷新时应用。两个弹窗的偏移 XYZ 一行等宽；每个来源编号同行显示元素和两位小数的 Blender 全局坐标，包含父级变换，使用当前源构型且不包含振动演示位移。批量滚动列表复用同一行绘制，保留编号范围、重复拒绝与交换规则。预览缓存只在操作阶段更新，draw 不读取 Dataset。

| 检查 | 结果及证据 |
| --- | --- |
| 定向检查 | Passed：[targeted.json](../reports/2026-10-17/annotation-ui/targeted.json)，65 项、无失败/错误/跳过；[文件身份](../reports/2026-10-17/annotation-ui/targeted-identity.json) |
| 标准库与公开科学 | Passed：[stdlib.json](../reports/2026-10-17/annotation-ui/stdlib.json) 266 项、[science.json](../reports/2026-10-17/annotation-ui/science.json) 100 项；相关源码和测试字节在提交前后未变，保留原报告提交及文件摘要 |
| 完整构建与隔离安装 | Passed：[candidate.json](../reports/2026-10-17/annotation-ui/candidate.json)、[isolated-install.json](../reports/2026-10-17/annotation-ui/isolated-install.json)；完整节点资产重建，复用 11 个锁定 wheel，安装文件与 ZIP 逐字节相同 |
| 原生行为和冷读 | Passed：[native.json](../reports/2026-10-17/annotation-ui/native.json)、[native-reopen.json](../reports/2026-10-17/annotation-ui/native-reopen.json)；真实 RNA、父级非均匀缩放/旋转/平移、换帧、四类默认值、元素/中文前缀、旧字号、科学坐标不变 |
| Computer Use | Passed：实际点击四类新建弹窗，原子新建/编辑、编号步进/直接输入/交换、八项列表及末尾滚动、编辑撤销与菜单重做；[原子新建](../reports/2026-10-17/annotation-ui/gui-new-atom.png)、[批量末尾](../reports/2026-10-17/annotation-ui/gui-batch-last.png)、[编辑实时预览](../reports/2026-10-17/annotation-ui/gui-edit-live.png)、[二面角直接输入](../reports/2026-10-17/annotation-ui/gui-dihedral-typed.png) |
| GUI 工程及冷读 | Passed：[gui-native.json](../reports/2026-10-17/annotation-ui/gui-native.json)、[gui-reopen.json](../reports/2026-10-17/annotation-ui/gui-reopen.json)；8 条实际 GUI 生成的文字均为 O/H，字号 0.5，编辑/菜单重做后编号与保存状态核对通过 |
| 当前教程材料 | Passed：公开样本、参数及文档链接；保留历史缺图占位，不代表完整截图或独立教程验收完成 |
| 日常安装、独立人工/科研接受 | Not Run：本批只更新候选 ZIP 并隔离安装，日常插件保持此前候选 |
| 本批全部测量编辑弹窗、测量 GUI 确认创建、渲染 | Not Run：测量新建窗口观察后取消；四类创建通过原生 CLI 验证，编辑公共布局通过原子窗口验证 |

## Standards

只读评审 `8fd2452...2bb5f72`，0 发现。

## Spec

按任务规格只读评审产品实现，0 发现；评审不替代上述实际验证。

## 保存、诊断和复现

本批开始及结束均无用户 Blender 会话，因此没有原用户工程需要恢复。GUI 与后台串行，最终候选使用隔离配置；MCP 集成未在隔离配置启用，本批原生调用记录为真实 CLI 或 Blender 控制台，不宣称 MCP 验收。

默认沙箱读取桌面 GUI 进程保存的 Dataset 目录被拒绝，失败记录保留为 [gui-reopen-sandbox-failed.json](../reports/2026-10-17/annotation-ui/gui-reopen-sandbox-failed.json)。在同一保存进程权限环境中冷读相同工程通过，未修改 ACL、取得所有权或强制删除。首次 GUI 脚本的属性页初始化错误、来源副本的读取失败及重试日志均保留于归档；这是本批验证环境诊断，不作为本次标注实现根因结论。

当前安装包在 `validation/shared/install/qcblender-0.1.0.zip`，稳定候选在 `outputs/candidates/current/annotation-ui-20261017/`；旧当前包保全为 `outputs/runs/annotation-ui-20261017/previous-current.zip`。任务工作树的输入、脚本、工程、配置、日志及旧诊断由该目录的保全清单和归档收据定位。重建使用 `python -m tools.dev_workflow build`，原生复验工具为 `tools/verify_annotation_dialog.py`；GUI 工程在归档中的 `outputs/runs/au/2/gui/g.blend` 及同名 `.qcdata/`。

本地 ff-only、注释标签和工作树收尾结果见[产物入口](../../../docs/ARTIFACTS.md#annotation-ui-20261017)，不 push。
