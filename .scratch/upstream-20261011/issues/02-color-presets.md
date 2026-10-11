Triage: ready-for-agent
Status: resolved
Blocked by: 01

# 色带预设

按spec实现纯数据、Blender操作器和专项检查；共享UI由主Agent接入，保存旧色带和明确目标验证。产品实现与脚本检查完成后交主Agent实际GUI验收。

## Comments

- 2026-10-11 产品实现 Agent 领取；01 已 resolved。负责冻结数据、独立 Operator、纯数据测试和 Blender 验证脚本；UI 接合及真实 Blender 验收由主 Agent 串行负责。

## Answer

- 已增加 `qcblender/color_presets.py`：QC_DEFAULT 保留当前三点；Viridis/Cividis 完整采用固定上游 13 点及 RGB/B_SPLINE、RGB/LINEAR，记录来源与 GPL-3.0-or-later，不增加依赖。
- 已增加 `qcblender/blender/color_presets.py`：`qcblender.apply_color_preset`，属性 `material_role` 为 `scalar_map` / `charge_map`，`preset` 为 `QC_DEFAULT` / `VIRIDIS` / `CIVIDIS`。按现有自动扫描注册；共享 UI 由主 Agent 接入。
- invoke 只校验并锁定目标，确认 execute 才替换既有 ColorRamp；直接 EXEC_DEFAULT 使用当前对象。校验标准视图、唯一角色、节点类型、编辑权限以及对话框期间对象/材质/节点身份；不修改图链接、范围、反转、透明度、数据或摘要 schema。共享材质沿用原生语义。失败后恢复完整色阶与三种模式并保留错误信息；REGISTER/UNDO 由 Blender 承担。
- `tools/verify_color_presets.py` 接受 `--module`、`--field-dataset` 绝对路径及 `--output` 绝对 JSON 路径。准备真实字段视图和明确标为工程测试的电荷样本，覆盖全部预设、真实 ColorRamp 求值、控制和科学数组不变、故障注入回滚、非法目标、原生共享、QC 复制和新视图独立、实际摘要。输出自包含 `<report-stem>-scene.blend`，供主 Agent GUI 验收；另一个 Blender 进程用 `--reopen-check --output <new-report.json>` 核对保存的色带、显示控制、链接、材质归属和科学数组。

### 验证

- Passed：Blender 5.1 自带 Python 以 `-B -m unittest discover -s tests -p test_color_presets.py -v` 运行 5 项测试；同命令分别运行 `test_copy_display.py` 9 项、`test_view_summary.py` 7 项。
- Passed：对固定 `2eb05987d0fa60678ea2d793c95fe4bc886270af` 与 `f88961b28828dfb32697748b575298dec20af3af` 的 `git show` 源码进行 AST literal 比较，全部位置、RGBA 和插值与产品冻结表一致。
- Passed：四个新增 Python 文件 AST 语法检查与 `git diff --check`。
- Not Run：本 Agent 未启动或连接 Blender；专项脚本、实际 GUI 应用/取消/反转/Undo/Redo、渲染、保存和冷重开由 05/06 任务串行验收。脚本的 headless preflight 不代替实际取消操作；故障注入仅证明运行时回滚边界，独立人工和科研接受仍需分别记录。
