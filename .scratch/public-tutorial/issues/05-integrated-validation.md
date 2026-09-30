# 05 综合验证

Triage: ready-for-agent
Status: resolved
Blocked by: 02, 04, 07

## 验收

同批 main 候选通过相关科学/节点/资格检查和可见 Blender MCP 操作、真实窗口截图及保存冷重开；MCP不记为鼠标点击，用户操作及独立签署仍单列。

## Comments

- 2026-09-30：按用户已批准实施计划建立任务；尚未领取或运行验收。
- 2026-09-30：主 Agent 领取；02/04/07 已 resolved。新候选绑定本次固定 main 提交，脚本核对与 Computer Use 实际点击分别记录。
- 2026-09-30：初轮原生检查发现剖面专项仍按旧曲线结构断言两条 spline，当前图表还包含轴及刻度；改为独立核对两段数据路径、无跨无效点连线及轴/刻度数量。教程同时补齐C07/C11/C13负向检查活动对象和前置条件，避免更早的guard掩盖目标断言。产品代码及公共接口未改；失败日志保留，更新固定提交后新批次复验。
- 2026-09-30：补齐剖面来源摘要拒绝的当前可见错误断言；原生剖面/相机/优化轨迹/结果浏览及各自双冷重开复验 Passed。清理计划发现新生成规范输入没有历史 original_path 时发生 KeyError，改为全部核对规范摘要、仅有历史来源时核对迁移原件；新增内容变更拒绝测试，9项清理边界测试 Passed。旧失败日志保留在 integration/r2；固定修正提交后另建 r3 候选批次，不继承探索报告。Computer Use 再连接仍返回 native pipe is unavailable，GUI Not Run。
- 2026-09-30：教程 Agent 只读集成复查确认C04旧映射入口必须用新的未映射密度层，0.4记录表案例必须改选关联可渲染视图取景；按现有operator行为修订步骤，主 Agent将用最终安装候选复核这些前置条件。
- 2026-10-01：r3绑定90ff9bf/4a0ac3e4候选：科学69、单测19、输入110、样本/checkpoint、安装/资产/图例/剖面/相机/优化/浏览及双冷重开Passed；C01–C13核心原生数据和选定operator复核Passed。工程42个科学对象绑定、785次数组摘要、12个VDB原地/中文移动/保全冷重开Passed。可见PID37508已打开；Computer Use仍缺native pipe，点击/截图/新候选MCP Not Run，保持claimed，不代签。索引docs/acceptance/tutorial-validation.json；证据outputs/evidence/2026-09-30/public-tutorial/integration/r3。

- 2026-10-01：按用户最新授权切换到 MCP 验收；连接先从有未保存修改的用户PID14284切换到新候选独立进程，原会话、工程及配置受保护。剩余C/N检查和证据完成后领取06。

## Answer

2026-10-01：按用户追加授权改用MCP完成技术验收。相同90ff9bf/4a0ac3e4候选的安装源码68项核对、C01–C13核心检查、N01–N18、连续Log Job2→新FCHK原生对话框、真实窗口截图、实际渲染、撤销/重做均Passed。新自包含工程55个科学对象，原路径/中文移动/归档解压分别在新可见进程核对1098次数组摘要和15个VDB，Passed。证据outputs/evidence/2026-10-01/public-tutorial-mcp/qualification-mcp.json；详细范围及摘要见验证索引。鼠标点击、用户本批复做、逐例完整成图和独立科研签署未继承通过，保持Not Run。未改产品/依赖/公共接口；原用户未保存会话及默认配置受保护。
