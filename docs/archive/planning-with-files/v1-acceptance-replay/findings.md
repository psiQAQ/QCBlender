# 复跑发现

- 2026-09-26：候选包和 S01–S11 摘要匹配。C07–C13 缺完整真实分析输出；后台仅检索和下载数据，不安装软件。
- Computer Use `@oai/sky` 初始化和应用枚举成功。初始无 Blender 进程。
- `blender-mcp --help` 沙箱内失败、沙箱外 Passed；无需修复或重新安装启动器。
- GUI 安装与科学运行时检查 Passed，证据 `outputs/v1-acceptance/replay/installation.json`、`runtime.json`。独立配置确认 Blender 5.1.1 / zh_HANS。
- SOP-01：运行时按钮在 Preferences → Add-ons → QCBlender，不在 3D 侧栏；已以实际 GUI 操作核对并修正 SOP。
- 沙箱启动 Blender 有窗口但不在 Computer Use 可见桌面；已关闭本轮沙箱 PID 15048，改用已批准的桌面启动，PID 28364。
- UI-01 初始复现：默认约 270px 宽侧栏裁掉名称/显隐等按钮；拉宽后完整显示。已移除固定 ui_units_x，并用新进程默认窄侧栏确认修复。
- C01：GUI 导入 S01、生成 Alpha HOMO35 / Beta HOMO34 与总/Alpha/Beta/自旋密度；网格统一为 0.2 Å、边距 3 Å。Alpha MO 阈值已由 0.05 调至 0.045。
- C10/C11：三个真实相邻 IRC 构型经现有 PySCF RHF/STO-3G 生成 FCHK/Mayer；六栏 MCP 技术检查通过，首次 GUI 待补；研究报告为 docs/research/sop-real-sources-c10-c13.md。
- UI-02：add_legend 材质输出变量遮蔽几何输出，导致 Geometry KeyError；共享函数修复后 GUI Map Colors、MCP Charge/Slice、中文回归通过。
- PORT-01：VDB 绝对路径不能随工程迁移；修为相对路径并刷新缓存，首次保存、Save As、失败回滚及新进程移动重开通过。
- ESP-01：真实 Multiwfn surfanalysis.pdb 的最大值/最小值分别从1编号；原读取器全局serial查重错误。现按(kind,serial)查重，同类重复仍拒绝；真实19点导入与GUI重试通过。
- 用户提供的 Multiwfn 2026.9.20 Windows 可直接运行，无需安装依赖。C07 IGMH/IRI、C08 ESP、C09 AIM、C12/C13 ETS-NOCV均生成真实输出，完整来源、参数、日志和摘要已加入 S25–S35。
- Computer Use 捕获已恢复，C04–C13 首次适用入口已确认。Mayer 重复导入已有结果会明确拒绝；新IRC路径的首次GUI导入正常。两者分别保留证据。
- 当前固定候选为03311fdeb0c83a38a546ebddedee1fe05e8dcb7260b53c889dd9fee3fa7ee231，50,440,466字节；最终包科学20/20、新配置离线安装及移动重开、源码/ZIP/安装一致性Passed。
