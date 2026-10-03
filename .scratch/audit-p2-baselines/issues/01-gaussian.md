# Gaussian 独立计算段

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

按上级spec修复AUDIT-02；文件归属qcblender/gaussian_log.py、tests/test_science_log.py及本任务记录。保留真实输入来源，不更新其他共享文档。修复前后断言证据与完整导入记录于Answer。

## Comments

- 2026-10-03：原缺陷在main复现：failed-then-normal仅一个failed job。
- 2026-10-03：补充缺失首段banner与连续纯banner对照：初版边界算法在3 tests中出现6 failures，记录于工作树 `outputs/boundary-red.log/json`；最终算法使用实际计算内容判断边界，全部通过。

## Answer

- 实施：`split_jobs` 依据 `Entering Gaussian System, Link 0=` 和既有 Link1 标记划分计算段。此前已有route、SCF、termination或orientation时，运行起始标记创建新段；首个或连续纯banner与前言留在首段。分段不再取决于 SCF 成功，扫描保持线性。公开数据结构未变。
- Failed（修复前预期红灯）：先新增三个回归测试再运行，3 tests、4 failures、0 errors；失败/截断段吞并后续真实正常日志，连续失败案例得到2段而非5段。使用 `26fa9c9` 原始模块和相同回归再次确认，记录于本工作树 `outputs/red.log`、`outputs/red.json`。
- Passed：`test_science_log` 共10 tests、0 failures、0 errors，包括原有真实 Link1、双杂化、MP2、CCSD(T)、TD、IR模式和数据往返检查。新增覆盖失败、截断、连续失败、正常拼接、首个banner/前言、连续纯banner、缺失首段banner、Link1及各段 route/status/energy/源行身份。更新到已整合NOCV的任务分支后再次通过。
- Passed：失败/截断/连续失败/正常段后拼接受既有 `tests/data/cclib/sources.json` 摘要约束的真实 `water_mp2.log`，`inspect_log` 与 `read_log` 选中末段一致；原子编号、构型、全部能量数量和值与单独导入完全相同，来源行号按拼接偏移准确保存。前后无显式构型的失败段单独读取仍明确拒绝，不从相邻段继承构型。
- Passed：原审计 `outputs/evidence/2026-10-03/plugin-audit/logic/failed-then-normal.log` 正确为 `failed`（1–4行）与 `normal`（5–9行）；正常拼接对照保持两个正常段。当前记录在本工作树 `outputs/green.log`、`outputs/green.json`。
- Passed：`git diff --check`。
- 环境：Blender 5.1 自带 Python，复用主检出的 `outputs/science`；本文件的两个 local input 调用尊重 `QCBLENDER_REFERENCE_ROOT`，保持主检出默认行为。
- 重跑（PowerShell，工作目录 `.worktrees/gaussian-segments`）：`& 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe' -B outputs/validate_gaussian.py --baseline` 重现预期红灯（退出码1）；同命令去掉 `--baseline` 验证当前修复（退出码0）。脚本与日志保留为本批技术证据，主Agent在归档工作树前保全。
- Not Run：Blender界面入口、实际工程保存/冷重开、整体科学回归和独立人工验收由主Agent后续综合验收维护；本任务仅完成解析及真实选段导入技术验证。
