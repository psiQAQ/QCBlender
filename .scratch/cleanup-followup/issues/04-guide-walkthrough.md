# 仅依据指南点击界面

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: 03

## 验收步骤

使用 03 的同批安装候选，在独立 Blender 配置下，仅阅读 [用户指南](../../../docs/USER_GUIDE.md) 查找并点击入口，不用脚本调用 Operator 代替。

1. 导入已核对摘要的 water_neutral_nbo_opt_freq.out，选择含频率的计算段；选中原子对象，在对象属性的科学记录与振动模式中查看能量，记录值、方法与角色。
2. 在同一面板选择一个振动模式，到高级参数调整 Animate，并在时间轴播放，确认模式、频率和原子显示位移对应；记录界面路径及实际按钮或属性文字。
3. 导入随仓库的 ch4_uhf_ccpvdz.fchk 并生成场；选中场视图，移动游标后点击记录剖面起点、创建线剖面，确认曲线、单位及有效点数。
4. 从工程与诊断点击保存自包含工程，另存新 .blend 与 .qcdata；新进程重开，确认科学对象和剖面仍可读。

逐项记录活动对象、实际路径、预期/实际结果和截图路径；检查者自行反馈。未执行保持 Not Run。本任务是操作指南检查，不改变独立科研验收签署。

## Comments

- 2026-09-30：用户追加授权修复导入参数复用缺陷，并由 Agent 通过 MCP + Computer Use 在独立可见 Blender 窗口完成剩余实际点击、保存和重开检查及截图。已发现并连接本地 Computer Use 组件；保留用户原有未保存窗口。新候选复验及实际点击尚未完成，状态保持 claimed；旧候选失败与用户已完成的两项仍单独保存。

- 当前宿主没有桌面点击工具；Blender 脚本和截图工具不作为实际点击证据。

- 2026-09-30：03 已 resolved，可以由检查者领取并复做。仅依据指南查找入口；活动对象、路径、按钮文字、预期和实际结果由检查者填写。候选已完成技术资格，尚未收到人工反馈。

- 2026-09-30：用户已实际执行前两项并开始第三项，领取状态更新为 claimed。能量及三个振动模式的播放 Passed；Log 后导入 FCHK 被来源摘要保护检查拒绝，第三项 Failed，保存/重开 Not Run。保留现有 Blender 会话（现场 PID 24852），未覆盖安装或操作工程。
- 文件及失败任务输入副本的 SHA-256 均为 3f93c52df5ef5adda00eff89bc5c9bb0bc10182722193d87e72f3b710d7c2c40，匹配清单；失败请求却带有先前水 Log 的摘要 9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519 和 job_index=1。已确认新文件对话框沿用先前的 source_sha256/job_number。实际安装 ui.py 与同批 ZIP 及仓库一致。
- 两行产品修复草案保存在 outputs/cleanup-followup/import-preview-state.patch，尚未应用。独立后台 Blender 使用模型化的操作参数及隔离的文件对话框边界，执行真实已安装 worker：旧状态复现 Failed、内存草案下 FCHK 导入 succeeded、显式摘要对应的源文件变化仍被拒绝。该复现不作为实际点击证据。报告为 outputs/qcf2/human/evidence/import-state-probe.json；产品冻结边界是否允许本次最小缺陷修复，等待用户决定。

## 本次材料

- 同批候选：outputs/qcf2/dist/qcblender-0.0.1.zip；SHA-256：48ca845e1d0f7be7bdc1300d962f733c89958fb89add2ff763aee24ebee5c760。
- 输入：tests/data/local/log-examples/water_neutral_nbo_opt_freq.out（S08，仅本地检查）和 tests/data/chemtools/ch4_uhf_ccpvdz.fchk；本轮已核对原始字节。
- 在独立进程/配置安装或启用上述 ZIP；新工程和截图保存到 outputs/qcf2/human，不覆盖技术检查工程或已打开的用户工程。

## 操作记录

实际操作者：用户；检查日期：2026-09-30。以下依据用户反馈及其截图记录，未反馈的路径或动作不推定为完成。受限原件和截图不进入 Git。

| 操作 | 活动对象与选择顺序 | 实际编辑器/面板/按钮 | 预期与实际结果 | 截图路径 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 能量记录 | water_neutral_nbo_opt_freq.out / Job 2 原子对象 | Properties → Object → QCBlender · 对象与量子化学 → 科学记录与振动模式；截图已核对 | 预期显示计算段能量；实际选中 RHF / electronic_total / target，-74.9659011806 Eh，用户报告约 -74.9659 Eh | outputs/qcf2/human/evidence/energy-modes.png | Passed |
| 模式选择与播放 | 同一 Job 2 原子对象 | 科学记录与振动模式列表已见；播放由用户报告，高级参数控件未另截图 | 列表频率 2169.7613、4141.3837、4392.5759 cm⁻¹；用户确认三个模式均能随帧播放 | 同上 | Passed |
| 线剖面 | 甲烷原子/场视图尚未创建 | 工作流导入 FCHK；失败请求的文件路径正确 | 预期导入并生成剖面；实际 Source changed after preview，曲线与采样检查尚未运行 | 错误由用户文字及原始 worker 报告核对 | Failed |
| 保存与新进程重开 | 待填写 | 待填写 | 待填写 | 待填写 | Not Run |

原始截图位置：C:/Users/ustcw/Pictures/Screenshots/屏幕截图 2026-09-30 155143.png；保留副本字节一致，SHA-256 为 2fbbb5a1bbceef170074b728c575cc4cc1de9f2e6b72f6615a867baef04b5940。失败请求、result.json、worker.log 和诊断摘要保留在 outputs/qcf2/human/evidence/。本记录属于操作指南检查；独立科研验收签署仍 Not Run。
