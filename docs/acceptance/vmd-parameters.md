# VMD 参数交互技术验收

本轮基线为 `main` 的 `2fa8096`，开发分支为 `feat/vmd-parameters`。四包按顺序集成；独立人工验收与外部视觉对照继续后置。规格见 [任务目录](../../.scratch/vmd-parameters/spec.md)。

| 批次 | 代码 | 科学回归 | 独立安装 | MCP 操作与渲染 | 保存、原地与移动冷重开 | Computer Use | 整批 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 分组面板 | Passed | Passed，45 项 | Passed | Passed | Passed | Not Run | Not Run |
| 02 显式着色场 | 开发分支已提交，尚未集成 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |
| 03 一次性色标范围 | 开发分支已提交，尚未集成 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |
| 04 复制显示参数 | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run | Not Run |

第一包证据目录为 `outputs/vmd-parameters/01-panel/`：`science.json`、`offline/extension.json`、`features/checks.json`、`gui-checks.json`。`features/evidence.blend` 与同目录 `.qcdata` 为可移动工程，`features/moved 中文 path/` 为移动副本；三种表面样式 PNG 与冷重开 PNG 分别保留。`candidate.json` 记录源码提交、逐文件摘要与 ZIP SHA-256。旧 SOP、结果浏览、优化轨迹及源码参考候选未覆盖。

2026-09-28 第一包原子三种样式的顶点数为 274 / 210 / 64，轨道实面、线框、点的顶点数为 2068 / 65920 / 86856。三种表面样式的渲染覆盖像素不同。撤销与重做正确，两个新进程重开后源身份、数组摘要和网格计数一致。实际面板由 Blender 原生截图 `panel-mcp.png` 记录；这份截图不代表 Computer Use 点击验收。

Computer Use 未完成的原因是当前桌面访问失败：`GetCursorPos: Access denied (0x80070005)`；恢复后截取仍返回 `IGraphicsCaptureItemInterop.CreateForMonitor: Could not capture the given monitor (0x80070057)`。MCP 连接正常。第一包保留待验状态，尚未创建整批通过标签。

独立人工复做与签署：**Not Run**。VMD 实际运行及外部视觉对照：**Not Run**。
