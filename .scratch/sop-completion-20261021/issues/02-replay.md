Triage: ready-for-agent
Status: resolved
Blocked by: 01

# 02 按教程实操、截图与保存工程

主线与九专题按当前参数和输入执行，真实 MCP 与 CU 范围分别记录。27 张图片就地引用；保留每个独立案例最终工程和关键截图状态检查点。发现真实缺陷时修复并复验。

## Comments

2026-10-21 最终：79 个编号步骤及章节内演示、27 张教程图已完成；36 个最终工程和检查点原位及中文路径解包新进程比较 Passed。最终教程 ZIP 含 1,755 个文件，296,605,483 字节，SHA-256 `a567d578cf0bfb4940bc2a02b140e8d4af61016440571a84e7b81cbdfa414a9c`。P01 已恢复，原生基线比较 Passed、差异为空，CU 观察相位与相机取景正常。 详见 `validation/agent/acceptance/sop-completion.md`。


2026-10-21 06:10：P06 已补原层与副本交替独显并恢复，11 步均完成。修复候选 `06b46875482a4ee377180717551457f9b74019f01c6c3f3221754119f75ff052` 完整构建、隔离安装、日常安装及原场景冷读 Passed，旧安装和偏好保留备份。Cube 专题 7 步、2 图也完成；四次串行冷读覆盖单场检查点、叠加、映射及中文路径副本，严格比较零差异。当前 69/79 步、24/27 图；密度/ESP 正在执行，尚未计入完成。报告分别在 `projects/P06-fixed-final-cold.json`、`P06-layers-cold.json`、`P06-annotations-cold-repeat.json`、`P06-annotations-case-check.json`、`P03-*-cold.json` 及 `mcp/035`–`047`。P06 标注初始完整快照失败的范围保留，不将两次冷读比较冒充有效的初始快照比较。

本地提交被自动审批两次拒绝，理由为未识别到用户授权；已另行询问并等待。该步骤暂停，其余已授权操作继续，不执行 push。

2026-10-21 05:45：P06 专题的导入、样式、氢显隐、七种局部选择操作、四类标注与编辑、朝向、材质保留、显示层复制、来源关联及多帧测量已执行；三张教程图已目视核对。步骤 7 尚补原层独显与副本独显的往返证据，其他 10 步完成，当前共 25/79 步、8/27 图。旧标注统一材质没有旧输入，本批不适用；纯行为说明不冒充实际演示结果。

P06 最终工程冷读 Failed：科学数组及节点内容保持，但三个生成节点树重新编号。确认 `node_identity._managed` 未保存碰撞后缀，已以 `1f7d537` 修复并保留用户改名保护；15 项定向测试 Passed。新候选构建、隔离/日常安装与原场景冷读尚待执行。检查工具另以 `e7a4744` 仅规范 Blender RNA 自动产生的正负 Infinity 标记；12 项测试 Passed，科学数组仍拒绝非有限值，原失败记录保留。证据位于主仓库稳定批次的 `projects/`、`mcp/016`–`031`、`cu/022`–`032`、`offline-stage2/`。

2026-10-21 05:07：P01 主线 15 步、5 图完成。CU 实际完成来源弹窗、HOMO/LUMO 8/10 预览、源编号 9 输入与生成确认、负相位显隐、F12 渲染、摘要目录输入及导出；MCP 调整阈值 0.045、正相位不透明度 0.4→1、创建取景相机并保存/归档，CU 分别观察实际效果。渲染 PNG 为 1280×720，摘要中的来源、单位、MO9、网格和阈值核对通过；摘要明确保留材料 Alpha 链路未求值的范围，不冒充完整渲染评价。

最终工程及 `.qcdata/` 保存后正常退出 PID 96468。`Wait-Process` 本身权限不足，随后独立进程查询确认 Blender 已退出，才启动 PID 37748。实际 `projects/P01-final-cold.json` Passed、差异为空，CU 重开画面与相机取景通过；归档包含 1 个 blend、38 个数据成员，CRC 校验通过。真实截图 `cu/010`–`021`、MCP 收据 `010`–`015` 和更新后的 `step-image-index.json` 位于主仓库本批稳定报告目录。当前总计 15/79 步、5/27 图，剩余专题及阶段 03 的中文路径/检查点专项冷读仍待完成。

2026-10-21：领取。主线步骤 1 复用已验证且当前成员一致的安装，CU 确认启用；步骤 2 已真实点击并核对 7 模块通过。实操发现侧栏只弹出短暂成功提示，详细结果位于插件偏好设置；已补充 SOP 的查看路径。首图 `P01-install.png` 取自本次真实 CU 图像，裁剪区域为原图的 `(170,250,930,566)`，无缩放、无内容补绘，目视确认模块名称和状态完整。

步骤 3 已通过原生 MCP 删除本批默认 Cube，保留 Camera/Light；材质预览、导入及后续步骤尚未执行。随后 CU 报窗口最小化；按提示重绑、激活时触发用户输入保护，捕获仍不可用。已异步请求用户恢复 Blender 到前台并保持展开，等待后继续，未使用过期坐标。

本次 SOP 新增说明后的检查：`outputs/runs/sop-20261021/docs-runtime/checks-tests.json`，10 项 Passed，0 失败、错误或跳过。当前执行与图片索引仍由主仓库 `validation/agent/reports/2026-10-21/sop-completion/step-image-index.json` 维护；前两步及首图已更新，其他项不借用旧图或旧工程充当本批通过。

2026-10-21 继续：材质预览已设置；真实 MCP 完成 P01 氧分子导入、命名 `P01-atoms`、核对两个氧原子与来源单位，并保存 `outputs/deliveries/sop-20261021/QCBlender-tutorial/work/human/P01/checkpoints/P01-import.blend` 及对应 `.qcdata/`。证据位于本批 `mcp/003-import-p01-start.json`、`004-p01-import-checkpoint.json`、`006-p01-source-binding.json`、`007-p01-source-details.json`。步骤 4 的侧栏截图与来源弹窗点击仍未完成；步骤 5 已发起真实科学来源资格检查，尚未生成轨道场。

检查点快照首次 Failed：新 `verify_sop_project.py` 对 268 字符 Windows 数组路径直接使用 `Path.resolve`，误报缺失。插件已有的 `filesystem_path` 可读取全部 23 个数组（16 个唯一文件），两个原子序数均为 8；产品保存未丢失数据。证据为 `projects/P01-import-baseline.json` 与 `mcp/005-p01-path-diagnosis.json`。离线子任务仅修复检查工具并补回归，实际 Blender 复验待整合后执行。

桌面当前阻塞已变化：可以捕获，但管理员 cmd 遮挡，重新绑定后激活 Blender 仍返回 `failed to activate captured window`。用户要求关闭 cmd 并多次要求重试激活；已核对前台 cmd PID 26956、启动时间 2026-10-21 04:29:09、标题及无命令子进程，针对该 PID 的关闭请求被 Windows 拒绝访问。没有关闭其他 cmd，也没有更改系统权限。用户再次授权后的激活及恢复重试仍失败；待前台状态恢复后继续真实点击和截图。

检查工具修复后实际快照 Passed。另按 Blender 5.1 RNA 使用 `Scene.compositing_node_group`；冷重开发现 Geometry Nodes 的 `*_use_attribute` ID 属性从布尔值读回为 0/1，只规范这类开关的等价表示，仍检查开关变化、非法值和实际插口数值。定向 10 项测试 Passed，旧实现的真实红测试保留。

本批旧进程 PID 24872 经只读确认 `is_dirty=False`，退出回调再次检查准确工程路径和干净状态后正常退出；进程查询确认无 Blender，再串行打开同一检查点，新 PID 96468。最初缺少退出保护的请求被自动审批拒绝，未执行；补充状态检查后的请求获准。冷重开比较 `projects/P01-import-cold-retry1.json` Passed、差异为空，覆盖科学数组、资源、节点、材质及持久显示设置。原失败报告保留；工具及红绿测试保存在稳定目录 `project-check-fixes/`。新窗口仍被管理员 cmd 遮挡且激活失败，未完成的 76 步、26 图及最终 ZIP 不标记通过。

2026-10-21 04:55：用户关闭管理员 cmd 后，检查确认 Blender/CU 同在会话 5，但该会话为 Disc、本地 console 为会话 6。用户明确要求生成并运行带 UAC 的 PS1；已执行 `outputs/runs/sop-20261021/session-handoff/Keep-Desktop-Interactive.ps1`，管理员子进程运行 `tscon.exe 5 /dest:console /v` 退出码 0，之后自动结束。实际复核会话 5 为 console/Active，无遗留 PowerShell 窗口；RDP 已断开时，CU 成功激活 Blender 并点击展开“数据与来源详情”，证据 `session-handoff/click-verification.json` 及同目录原始截图。桌面阻塞解除，可从 P01 导入后的侧栏截图与来源弹窗继续；这次恢复不把其余教程步骤提前计为通过。
