# 开发流程与 MCP 复用验收

2026-10-16，技术验收 `Passed`。统一入口为 `python -m tools.dev_workflow`，步骤见 [开发流程](../../../docs/agents/development-workflow.md)，四批观察见 [复盘](../../../docs/agents/development-retrospective.md)。

## 验证对象与结果

- `Passed`：6 项定向测试，0 failures/errors/skips；错误 PID 拒绝写入，失败命令或报告不会记成功，失败不自动重试，相同身份直接复用。最新执行源码 `06a8859`，收据 `outputs/runs/dev-workflow-20261016/checks-adapters/checks.json`。后加启动辅助脚本单独经真实 MCP 验证，不扩大重跑既有检查。
- `Passed`：完整重建产品及双语节点资产、隔离安装逐成员比对、11 次固定原生操作、保存冷读、全局安装逐成员比对。产品源码 `6700920`，后续只改开发工具和记录；新 ZIP 为 50,940,475 字节，SHA-256 `ca3a92f5caf9a35d4bc70c80c81fa3eebeb9b7d4bbf0e0eaf0e75960bf063aeb`。
- `Passed`：现有 SDK 通过真实 Streamable HTTP MCP 的 `execute_blender_code` 执行身份、导入、键角/二面角创建与编辑、三帧 XYZ 切换、独立半角与相机朝向断言、渲染、自包含保存和正常退出；随后新进程冷读快照一致。未用 `execute_blender_code_for_cli` 冒充交互 MCP，也不宣称宿主原生工具列表已重载。
- `Passed`：原保存工程 `outputs/projects/sidebar-preserved-20261016/user-session.blend` 已打开，当前 PID 66808；原 `.blend` 和五个配套文件摘要不变，持久场景、科学数组、节点、材质、偏好与布局基线一致。开始时按用户本次明确授权直接关闭 PID 71804，未保存其未保存改动。
- `Passed`：全局规则追加通用复用原则及本仓库入口。HTTP 401 经内存比较确认为旧令牌；获用户明确授权后仅替换 Blender MCP 的 Authorization，备份在 `%USERPROFILE%/.codex/config.before-blender-token-20261016.toml`，令牌未进入 Git 或报告。
- `Not Run`：独立人工、独立科研验收和远端 CI。本批没有产品界面变更，历史产品 GUI 证据保留原身份；Computer Use 只用于恢复窗口的观察与现有 MCP 服务启动。

完整证据与摘要见 `validation/agent/reports/2026-10-16/dev-workflow/acceptance.json`。当前安装身份见 [current-install.json](../current-install.json)，本地提交、保全及归档由同目录 `delivery.json` 和 `outputs/runs/dev-workflow-20261016/archive/` 收据记录。不 push。

## 实际故障及复验

会话启动后重复填入 `status` 导致包装器报错，实际子进程已执行，未重复启动。冷读差异来自无引用、无 fake user 的启动材质，快照改为持久材质范围；原快照与失败结果保留，科学数据及实际使用材质仍完整比较。主检出锁文件换行差异曾阻止复用，依赖锁改为解析内容比较，候选及显式输入仍按原字节核对。

恢复窗口的现有 MCP 集成保持 `Stopped`，实际点击“偏好设置 → 插件 → Blender MCP Integrated → Start MCP”后，MCP 身份和原工程基线再次通过。已记录稳定操作 ID `blender-mcp-start-existing-service-20261016`。通用 `mcp_start.py` 的已运行服务复用分支通过真实 MCP；新会话的启动仍须以工具发现结果判断就绪。

## 计量与保留

本批成功执行 16 次实际 MCP 工具调用：14 次固定操作、1 次案例场景设置、1 次启动辅助脚本复用。结果收据共 121,040 字节；核心 MCP 案例耗时 24.498 秒，其 CLI 摘要输出 1,776 字节。这不是整项开发耗时或网络字节数。Computer Use 共 14 次截图调用、返回 18 帧，保存 2 帧；没有重复点击产品标注入口。另有两张实际渲染。无可靠 token 对比数据，不报告节省比例。

旧安装、偏好、旧当前 ZIP、原保存工程备份、运行脚本、失败及成功结果均保留于 `outputs/runs/dev-workflow-20261016/`；新候选保留于 `outputs/candidates/current/dev-workflow-20261016-r1/`。任务工作树的忽略文件逐项保全后正常归档，历史材料不清理。

归档时另有 2 次维护用 MCP 调用：读取并移出 Blender 的工作目录，同时再次断言原工程基线；随后 1 次调用按精确服务 PID 正常重启其子进程以释放继承目录，结束时再只读核对一次身份。原工作树仅剩的空目录因此正常移除，未改 ACL 或强制删除。启动器补充显式工作目录，恢复时使用原工程目录，防止再次继承任务工作树；本批当前进程迁移与基线断言已执行，该收尾参数修正未额外重启已恢复窗口。核心验收的 16 次调用计量与 4 次归档维护调用分别记录。
