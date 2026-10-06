# 03 环境与重建入口

Triage: ready-for-agent
Status: resolved
Blocked by: 01
Owner: runtime agent

## Scope

当前工具改为明确候选参数及集中输入，在新目录重建所需 fixture；统一根 wheels 入口。给出最小构建环境、当前科学环境、唯一原始来源和完整许可的保留集合，及可退役旧环境/原生链清单。产品源码和依赖锁不变。

## Acceptance

检查脚本不依赖已结束任务的生成物；相关测试及参数检查通过。环境与来源文件逐项交接主 Agent，禁止自行删主检出文件或启动 Blender。本地提交后等待串行合并。

## Answer

当前工具使用明确候选参数与集中输入，在新批次目录重建 MO Cube、Gaussian NBO 参考及数值 ETS/NOCV fixture。首次与增量构建统一根 wheels；回归 fixture 可从集中输入或唯一 IOData/GBasis 原始 ZIP 恢复，已有不同内容直接失败。环境建议由 `tools/runtime_cleanup_plan.py` 输出，先核对全部根 wheel 的实际摘要与锁定记录，缺失或差异直接失败；通过后保留五个锁定包的 RECORD 文件及完整 science，历史原生构建环境单列退役。

- Passed：复制主检出 429 个保留构建文件到本工作树后，使用 Blender Python 从固定 GBasis ZIP 离线构建 pure1 wheel；未安装或更新依赖，主环境未改。
- Passed：5 个标准库安全/归档恢复、根 wheel 身份及候选节点资产测试、1 个真实 CH4 MO/Cube/NOCV 数值检查，以及工具参数入口。
- Passed：主 Agent 完成同版本合格 wheel 迁移后，普通读取环境核对根目录 11 份 wheel 均与锁及 backend record 匹配；当前建议保存期望和实际摘要。迁移收据为主检出 `validation/agent/reports/2026-10-06/outputs-prune/wheel-normalization.json`。
- Passed：源码编码和换行约定保持，`git diff --check`。
- Not Run：Blender 场景运行、当前候选安装与冷重开，由主 Agent 合并后串行执行；数值 NOCV fixture 不代表真实 NOCV 科研验收。
- NOCV 检查的生成和冷重开均要求明确 `--candidate`，从该 ZIP 提取节点资产后注册源码；本批已有提取字节必须与候选一致。当前教程候选的真实资产提取及重复读取 Passed，577,053 字节，SHA-256 `529c1702554cad748b23f112265a2e89689dd71332f9cff6ad8c384a4e1af96f`；Blender 两阶段复验由主 Agent 串行完成。

逐文件环境建议及完整原件位置见本任务工作树 `validation/agent/reports/2026-10-06/outputs-prune/runtime/final-v2/runtime-plan.json`；原构建及科学验证收据为上级目录 `checks.json`。`build_keep_files`/`build_retire_files` 相对 `outputs/build-site`；`protected_paths` 相对仓库根；`retired_task_roots` 相对 outputs。主 Agent 保全本批报告后维护最终路由，本任务未删除主检出文件。
