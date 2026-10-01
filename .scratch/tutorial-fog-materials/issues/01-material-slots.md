# [P1] 绑定体积雾材质槽并同步参数复制

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: none

## 目标

按 [规格](../spec.md) 实现体积雾材质槽绑定、显示参数复制同步与回滚，并扩充相关测试。

## Comments

- 2026-10-01：主 Agent 已通过原生 Material dropdown 实测，增加同材质槽后 Opacity Scale 及 opacity ramp 编辑即时更新 MATERIAL 视口；原始截图与工程由主 Agent 保全。
- 2026-10-01：领取独立 fix/tutorial-fog-materials 工作树。验证与本地提交已授权；共享 GUI/MCP 与安装候选由主 Agent 串行处理。

- 2026-10-01：旧工程迁移范围已获主 Agent 确认。仅 load_post 与启用时一次处理；本地 editable fog Mesh、唯一明确 QC fog group、实际连接到 Material interface 的输入及 qc_fog 材质才补槽。保留已有槽，无重复；linked/read-only、非 fog、歧义或断开/改接图跳过。

## Answer

源码实施及本地验证已完成。新 fog carrier mesh 与 GN Material 引用同一材质；复制显示参数记录并同步匹配槽，失败时还原槽与 GN 引用。旧工程按上述加载边界修复，无槽对象仍可复制参数。GN 接口、材质传递函数、依赖与科学数组保持。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 非科学 Python 测试 | Passed | 显式 Blender 5.1 Python：copy 9、migration 5、legend 2、local inputs 1、cleanup 9，共 26 项；outputs/runs/fog-materials/report.json 与各 test_*.log |
| 源码语法与 diff 检查 | Passed | 同一 report.json；git diff --check 退出 0 |
| 原生 Blender RNA/GN 材质引用 | Passed | Blender 5.1.1 独立 factory/background 配置；native-report.json、native-command.json、native.log |
| 新建与复制层 | Passed | 新建 slot/socket 同指针，复制层拥有独立材质且同指针 |
| 参数复制与旧无槽兼容 | Passed | 参数复制槽/socket 同步，保留无关槽及目标 Plane；无槽旧对象可复制；失败回滚由 Python 边界测试覆盖 |
| 保存/加载/linked/注销边界 | Passed | 真实保存不迁移；open_mainfile 后 load_post 补槽；重复调用幂等；真实 linked 无槽对象不改；unregister 移除 hook/timer |
| 安装候选、MATERIAL 即时刷新及真实 C01 冷重开/渲染/数组 | Not Run | 主 Agent 串行可见验收，诊断 A/B 不作为此源码候选资格 |

运行入口为 outputs/runs/fog-materials/run_checks.py 与 verify_native_materials.py；命令、退出码、源码及日志摘要见上述报告。原生检查采用真实 Blender 材质、节点和对象，空 Volume 仅用于引用结构验证，未加载科学数组。factory startup 保存出现系统 brush asset 相对路径警告，测试断言及退出码通过。

Status 保持 claimed，等待主 Agent 安装候选与真实 C01 验收后闭合。原始缺陷工程、诊断截图与主任务索引由主 Agent 维护。
