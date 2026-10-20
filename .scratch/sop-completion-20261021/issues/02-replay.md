Triage: ready-for-agent
Status: claimed
Blocked by: 01

# 02 按教程实操、截图与保存工程

主线与九专题按当前参数和输入执行，真实 MCP 与 CU 范围分别记录。27 张图片就地引用；保留每个独立案例最终工程和关键截图状态检查点。发现真实缺陷时修复并复验。

## Comments

2026-10-21：领取。主线步骤 1 复用已验证且当前成员一致的安装，CU 确认启用；步骤 2 已真实点击并核对 7 模块通过。实操发现侧栏只弹出短暂成功提示，详细结果位于插件偏好设置；已补充 SOP 的查看路径。首图 `P01-install.png` 取自本次真实 CU 图像，裁剪区域为原图的 `(170,250,930,566)`，无缩放、无内容补绘，目视确认模块名称和状态完整。

步骤 3 已通过原生 MCP 删除本批默认 Cube，保留 Camera/Light；材质预览、导入及后续步骤尚未执行。随后 CU 报窗口最小化；按提示重绑、激活时触发用户输入保护，捕获仍不可用。已异步请求用户恢复 Blender 到前台并保持展开，等待后继续，未使用过期坐标。

本次 SOP 新增说明后的检查：`outputs/runs/sop-20261021/docs-runtime/checks-tests.json`，10 项 Passed，0 失败、错误或跳过。当前执行与图片索引仍由主仓库 `validation/agent/reports/2026-10-21/sop-completion/step-image-index.json` 维护；前两步及首图已更新，其他项不借用旧图或旧工程充当本批通过。

2026-10-21 继续：材质预览已设置；真实 MCP 完成 P01 氧分子导入、命名 `P01-atoms`、核对两个氧原子与来源单位，并保存 `outputs/deliveries/sop-20261021/QCBlender-tutorial/work/human/P01/checkpoints/P01-import.blend` 及对应 `.qcdata/`。证据位于本批 `mcp/003-import-p01-start.json`、`004-p01-import-checkpoint.json`、`006-p01-source-binding.json`、`007-p01-source-details.json`。步骤 4 的侧栏截图与来源弹窗点击仍未完成；步骤 5 已发起真实科学来源资格检查，尚未生成轨道场。

检查点快照首次 Failed：新 `verify_sop_project.py` 对 268 字符 Windows 数组路径直接使用 `Path.resolve`，误报缺失。插件已有的 `filesystem_path` 可读取全部 23 个数组（16 个唯一文件），两个原子序数均为 8；产品保存未丢失数据。证据为 `projects/P01-import-baseline.json` 与 `mcp/005-p01-path-diagnosis.json`。离线子任务仅修复检查工具并补回归，实际 Blender 复验待整合后执行。

桌面当前阻塞已变化：可以捕获，但管理员 cmd 遮挡，重新绑定后激活 Blender 仍返回 `failed to activate captured window`。用户要求关闭 cmd 并多次要求重试激活；已核对前台 cmd PID 26956、启动时间 2026-10-21 04:29:09、标题及无命令子进程，针对该 PID 的关闭请求被 Windows 拒绝访问。没有关闭其他 cmd，也没有更改系统权限。用户再次授权后的激活及恢复重试仍失败；待前台状态恢复后继续真实点击和截图。

检查工具修复后实际快照 Passed。另按 Blender 5.1 RNA 使用 `Scene.compositing_node_group`；冷重开发现 Geometry Nodes 的 `*_use_attribute` ID 属性从布尔值读回为 0/1，只规范这类开关的等价表示，仍检查开关变化、非法值和实际插口数值。定向 10 项测试 Passed，旧实现的真实红测试保留。

本批旧进程 PID 24872 经只读确认 `is_dirty=False`，退出回调再次检查准确工程路径和干净状态后正常退出；进程查询确认无 Blender，再串行打开同一检查点，新 PID 96468。最初缺少退出保护的请求被自动审批拒绝，未执行；补充状态检查后的请求获准。冷重开比较 `projects/P01-import-cold-retry1.json` Passed、差异为空，覆盖科学数组、资源、节点、材质及持久显示设置。原失败报告保留；工具及红绿测试保存在稳定目录 `project-check-fixes/`。新窗口仍被管理员 cmd 遮挡且激活失败，未完成的 76 步、26 图及最终 ZIP 不标记通过。

2026-10-21 04:55：用户关闭管理员 cmd 后，检查确认 Blender/CU 同在会话 5，但该会话为 Disc、本地 console 为会话 6。用户明确要求生成并运行带 UAC 的 PS1；已执行 `outputs/runs/sop-20261021/session-handoff/Keep-Desktop-Interactive.ps1`，管理员子进程运行 `tscon.exe 5 /dest:console /v` 退出码 0，之后自动结束。实际复核会话 5 为 console/Active，无遗留 PowerShell 窗口；RDP 已断开时，CU 成功激活 Blender 并点击展开“数据与来源详情”，证据 `session-handoff/click-verification.json` 及同目录原始截图。桌面阻塞解除，可从 P01 导入后的侧栏截图与来源弹窗继续；这次恢复不把其余教程步骤提前计为通过。
