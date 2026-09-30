# 02 节点布局

Triage: ready-for-agent
Status: resolved
Blocked by: 无

## 验收

新外层 Frames 与限定集合布局；公共组/接口不变，真实 Blender 专项和兼容检查通过。

## Comments

- 2026-09-30：按用户已批准实施计划建立任务；尚未领取或运行验收。
- 2026-09-30 21:34 前：节点布局子 Agent（GPT-6.1 SOL / medium）已领取任务，baseline.stdout.log 于 21:34 写出；准确领取分钟没有单独记录。原代理因模型容量错误中断，继任节点子 Agent 接续既有工作树与检查记录，并完成真实 MO8 图例回归和两次冷重开。

## Answer

- Passed：Blender 5.1.1 新建原子、场、切片与新增着色、电荷、振动分支生成 7 个单层 Frame；已有用户节点的坐标、parent、标签、宽度及自定义连接保持不变。
- Passed：布局前后外层接口、求值网格、数据文件摘要一致；9 个公共资产签署摘要一致，公共资产无新增 Frame。保存后独立冷重开保持相同节点布局与求值结果。证据：D:/workspace/QCBlender/outputs/runs/public-tutorial/nodes/ 下 baseline.json、check.json、reopen.json 及对应 stdout 日志。
- Passed：隔离安装版的 verify_vmd_parameters.check_copy、verify_vmd_scalar_edges.check_edges；verify_mn_legend.check_legend 使用主检出真实 ch4_uhf_ccpvdz.fchk 导入并计算 alpha MO8 后完整通过，普通及中文移动路径冷重开均 Passed。证据：同目录 copy-result.json、edges-result.json、legend-r2-result.json、regression-legend-r2/checks.json。安装版五个修改模块与本工作树 SHA-256 相同。
- Failed（已排除）：首次 legend 检查场景缺少 orbital_amplitude 视图而 StopIteration；补足真实 MO8 输入后复跑通过。原始 legend.stderr.log 保留。
- Not Run：主 Agent 负责同一候选的综合科学验证、GUI 操作及独立人工签署。
